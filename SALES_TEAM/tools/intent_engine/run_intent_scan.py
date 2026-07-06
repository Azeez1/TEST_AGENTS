"""Intent Signal Engine orchestrator CLI.

Flow: start_run -> load enabled collectors -> collect (errors contained) ->
resolve -> score per avenue/metro -> export_csv -> export_sheet -> finish_run
-> SUMMARY block.

Usage:
    python run_intent_scan.py [--avenues trucking pe_distress] [--metros houston]
                              [--since-days 7] [--backfill-days 90]
                              [--no-sheet] [--dry-run] [--scheduled]

--dry-run uses an in-memory store seeded with the fixtures synthetic signals,
never touches the real DB or the Google Sheet, and writes CSVs to
OUTPUT_DIR/dry_run/ so real exports are never overwritten.
"""
import argparse
import importlib.util
import sys
import threading
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
import resolve as resolve_mod  # noqa: E402
from collectors import CollectorResult, load_collectors  # noqa: E402
from common.score import (MAX_AGE_DAYS, PAY_MAX_AGE_DAYS,  # noqa: E402
                          TIMING_MAX_AGE_DAYS, score_entity_v2)
from common.store import Store  # noqa: E402
from export_csv import export_csv  # noqa: E402

CONTACT_FIELDS = ("phone", "email", "street", "zip")

# --- per-collector timeout watchdog -----------------------------------------
# A single stalled collector (slow HTTP, first-run HCAD reparse) must never
# freeze the whole scan. Each collector runs under a wall-clock timeout; on
# expiry it is abandoned (SKIPPED) and the run continues. Defaults are in
# seconds and overridable via the registry's optional "collector_timeouts"
# section; heavy first-run collectors get more headroom.
DEFAULT_COLLECTOR_TIMEOUT = 300
_CODE_COLLECTOR_TIMEOUTS = {
    "pay_hcad": 900,        # first run streams + parses an 872 MB HCAD member
    "osha_dol": 600,        # downloads + scans a large OSHA inspection CSV
    "sba_loans": 600,       # downloads + scans the SBA FOIA CSV
    "pay_sba": 600,         # joins every avenue's entities against the SBA index
    "trucking_fmcsa": 900,  # pulls 5k+ inspection/crash signals — slow but reliable, must finish
                            # not abandoned (an abandoned mid-write worker keeps the DB lock and stalls the run)
}


def _collector_timeout(source_id, registry):
    """Watchdog timeout (seconds) for one collector. Registry
    'collector_timeouts' overrides the in-code defaults; unknown -> DEFAULT."""
    reg = registry.get("collector_timeouts") or {}
    val = reg.get(source_id)
    if val is None:
        val = _CODE_COLLECTOR_TIMEOUTS.get(source_id, DEFAULT_COLLECTOR_TIMEOUT)
    try:
        return max(1, int(val))
    except (TypeError, ValueError):
        return DEFAULT_COLLECTOR_TIMEOUT


def _call_collect(collector, since, store, registry):
    """Invoke one collector, containing ALL errors into a CollectorResult
    (the collector contract says never raise, but contain anyway)."""
    try:
        r = collector.collect(since, store, registry)
        if not isinstance(r, CollectorResult):
            r = CollectorResult(collector.source_id, 0, 0, "ERROR",
                                "collector returned non-CollectorResult")
    except Exception as exc:  # noqa: BLE001 - defensive containment
        r = CollectorResult(collector.source_id, 0, 0, "ERROR",
                            f"{type(exc).__name__}: {exc}")
    return r


def _run_with_watchdog(collector, since, db_path, registry, timeout_s):
    """Run a collector on its OWN Store connection inside a DAEMON worker
    thread, bounded by `timeout_s`. On timeout the worker is abandoned (a
    leaked thread is acceptable) and a SKIPPED result is returned so the
    orchestrator moves on.

    A DAEMON thread is essential: a stalled collector's thread may still be
    blocked in a slow HTTP call at interpreter shutdown. Non-daemon workers
    (e.g. ThreadPoolExecutor's) are joined by an atexit handler, which would
    hang the whole process at exit and swallow the SUMMARY. Daemon threads are
    abandoned cleanly on exit, so the run always finishes and flushes."""
    from common.store import Store  # local import: only needed for real runs

    box = {}

    def _target():
        # Connection is created AND used entirely within this worker thread,
        # so SQLite's same-thread check is satisfied without global flags.
        cs = Store(db_path)
        try:
            box["result"] = _call_collect(collector, since, cs, registry)
        except BaseException as exc:  # noqa: BLE001 - never let a worker die silently
            box["result"] = CollectorResult(collector.source_id, 0, 0, "ERROR",
                                            f"{type(exc).__name__}: {exc}")
        finally:
            try:
                cs.close()
            except Exception:
                pass

    t = threading.Thread(target=_target,
                         name=f"collector-{collector.source_id}", daemon=True)
    t.start()
    t.join(timeout_s)
    if t.is_alive():
        # Still blocked (likely a stalled HTTP call). Abandon it and continue;
        # the daemon thread dies when the process exits at end of run.
        print(f"[watchdog] {collector.source_id} exceeded {timeout_s}s — "
              f"abandoning it (SKIPPED) and continuing the scan.", flush=True)
        return CollectorResult(collector.source_id, 0, 0, "SKIPPED",
                               f"timeout after {timeout_s}s")
    return box.get("result") or CollectorResult(
        collector.source_id, 0, 0, "ERROR", "watchdog: no result produced")


def _registry_types(registry, section):
    """Signal types under a top-level registry section, minus _doc keys."""
    return {k for k in (registry.get(section) or {}) if not k.startswith("_")}


def _merged_attrs(store, ent, contributing):
    """Entity attrs (JSON) merged with first non-null attrs off its signals so
    solvency sees size attrs (power_units etc.) collectors stamp on Signals."""
    import json as _json
    merged = {}
    raw = (ent or {}).get("attrs")
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = _json.loads(raw)
            if isinstance(parsed, dict):
                merged.update(parsed)
        except ValueError:
            pass
    elif isinstance(raw, dict):
        merged.update(raw)
    for s, _conf in contributing:
        a = s.get("attrs")
        if isinstance(a, str) and a.strip():
            try:
                a = _json.loads(a)
            except ValueError:
                continue
        if not isinstance(a, dict):
            continue
        for k, v in a.items():
            if v not in (None, "", "None") and merged.get(k) in (None, "", "None"):
                merged[k] = v
    return merged


def _parse_list(values, valid, label):
    if not values:
        return list(valid)
    out = []
    for v in values:
        for part in str(v).split(","):
            part = part.strip().lower()
            if not part:
                continue
            if part not in valid:
                raise SystemExit(f"Unknown {label}: {part!r} (valid: {', '.join(valid)})")
            out.append(part)
    return out


def build_rows(store, registry, avenues, metros, run_id=None):
    """Resolve entities, score each cluster per avenue/metro (v2: pain x timing
    x ability-to-pay x deal-size), return export rows ranked by expected_value."""
    clusters, _ = resolve_mod.resolve(store)
    rows = []
    today = date.today()
    pay_types = _registry_types(registry, "solvency_signals")
    timing_types = _registry_types(registry, "timing_signals")
    timing_defs = registry.get("timing_signals") or {}
    for avenue in avenues:
        cfg = registry["avenues"][avenue]
        known_types = set(cfg.get("signals", {}).keys())
        funnel = cfg.get("funnel", "customers")
        top_n = int(cfg.get("top_n", 25))
        for metro in metros:
            scored_rows = []
            for canonical, members in clusters.items():
                pairs = resolve_mod.signals_for_cluster(store, members, avenue, metro)
                contributing, pay_contrib, timing_contrib = [], [], []
                for s, conf in pairs:
                    stype = s["signal_type"]
                    try:
                        sdate = date.fromisoformat(str(s["signal_date"])[:10])
                    except ValueError:
                        continue
                    age = (today - sdate).days
                    if stype in known_types and 0 <= age <= MAX_AGE_DAYS:
                        contributing.append((s, conf))
                    elif stype in pay_types and age <= PAY_MAX_AGE_DAYS:
                        pay_contrib.append((s, conf))   # future pay dates = fresh
                    elif (stype in timing_types
                          and -400 <= age <= TIMING_MAX_AGE_DAYS):
                        timing_contrib.append((s, conf))  # future anchors OK
                if not contributing:
                    continue  # pain is the entry ticket; pay/timing only enrich
                sigs = [s for s, _ in contributing]
                ent = store.get_entity(canonical) or {}
                ent = dict(ent)
                ent["attrs"] = _merged_attrs(store, ent,
                                             contributing + pay_contrib)
                v2 = score_entity_v2(sigs, [s for s, _ in pay_contrib],
                                     [s for s, _ in timing_contrib], ent, cfg,
                                     as_of=today, timing_defs=timing_defs)
                score, top_types = v2["pain"], v2["top_signals"]
                if score <= 0:
                    continue
                hot = v2["hot"]
                contact = {f: (ent.get(f) or "") for f in CONTACT_FIELDS}
                for info in members:
                    if all(contact.values()):
                        break
                    e2 = store.get_entity(info["entity_key"]) or {}
                    for f in CONTACT_FIELDS:
                        if not contact[f] and e2.get(f):
                            contact[f] = e2[f]
                evidence = []
                for s, _ in sorted(contributing, key=lambda p: p[0]["signal_date"],
                                   reverse=True):
                    ref = s.get("source_ref") or ""
                    if ref and ref not in evidence:
                        evidence.append(ref)
                    if len(evidence) >= 3:
                        break
                all_contrib = contributing + pay_contrib + timing_contrib
                row = {
                    "entity_key": canonical,
                    "score": score,
                    "hot": hot,
                    "entity_name": ent.get("name") or sigs[0]["entity_name"],
                    "metro": metro,
                    "avenue": avenue,
                    "funnel": funnel,
                    "expected_value": v2["expected_value"],
                    "pain": v2["pain"],
                    "pain_norm": v2["pain_norm"],
                    "timing": v2["timing"],
                    "timing_window": v2["timing_window"],
                    "ability_to_pay": v2["ability_to_pay"],
                    "pay_data": v2["pay_data"],
                    "pay_sources": ";".join(v2["pay_sources"]),
                    "deal_size": v2["deal_size"],
                    "top_signals": ";".join(top_types),
                    "signal_count": len(contributing),
                    "latest_signal_date": max(s["signal_date"] for s in sigs),
                    "evidence_urls": " | ".join(evidence),
                    "phone": contact["phone"],
                    "email": contact["email"],
                    "street": contact["street"],
                    "zip": contact["zip"],
                    "first_seen": ent.get("first_seen", ""),
                    "match_conf": min(c for _, c in all_contrib),
                }
                scored_rows.append(row)
                if run_id is not None:
                    store.save_score(run_id, canonical, avenue, metro, score, hot,
                                     top_types)
            scored_rows.sort(key=lambda r: -r["expected_value"])
            rows.extend(scored_rows[:top_n])
    return rows


def run_collectors(store, registry, avenues, metros, since):
    """Load enabled collectors and run each under a per-collector timeout
    watchdog so a single stalled collector can never freeze the whole scan.

    Real (file-backed) runs isolate each collector on its own Store connection
    inside a worker thread bounded by `_collector_timeout`; a timeout is
    recorded as SKIPPED and the scan continues. Dry-run uses an in-memory DB
    (which cannot be shared across connections), so those collectors run inline
    with errors contained — no watchdog, since dry-run is a manual dev tool.
    """
    results = []
    collectors, missing, disabled = load_collectors(registry)
    in_memory = str(getattr(store, "db_path", "")) == ":memory:"
    for c in collectors:
        if c.avenue not in avenues:
            results.append(CollectorResult(c.source_id, 0, 0, "SKIPPED",
                                           f"avenue {c.avenue} not selected"))
            continue
        if not set(m.lower() for m in c.metros) & set(metros):
            results.append(CollectorResult(c.source_id, 0, 0, "SKIPPED",
                                           "no selected metro"))
            continue
        if in_memory:
            r = _call_collect(c, since, store, registry)
        else:
            timeout_s = _collector_timeout(c.source_id, registry)
            r = _run_with_watchdog(c, since, store.db_path, registry, timeout_s)
        results.append(r)
    for m in missing:
        results.append(CollectorResult(m, 0, 0, "SKIPPED",
                                       "module not implemented yet (Phase 1)"))
    for d in disabled:
        results.append(CollectorResult(d, 0, 0, "SKIPPED", "disabled in registry"))
    return results


def build_summary_lines(registry, avenues, metros, rows, collector_results):
    """One line per avenue/metro: entity counts, or explicit SOURCE EMPTY/ERROR."""
    by_group = {}
    for r in rows:
        by_group.setdefault((r["avenue"], r["metro"]), []).append(r)
    status_by_collector = {c.source_id: c for c in collector_results}
    lines = []
    for avenue in avenues:
        cfg = registry["avenues"][avenue]
        for metro in metros:
            grp = by_group.get((avenue, metro), [])
            if grp:
                hot = [r for r in grp if r["hot"]]
                top = max(grp, key=lambda r: r["score"])
                lines.append(
                    f"{avenue} / {metro:<10} {len(grp):>3} entities | {len(hot):>2} hot"
                    f" | top: {top['entity_name']} ({top['score']:.2f})")
            else:
                errs = [status_by_collector[cid].error
                        for cid in cfg.get("collectors", [])
                        if cid in status_by_collector
                        and status_by_collector[cid].status == "ERROR"]
                if errs:
                    lines.append(f"{avenue} / {metro:<10} SOURCE ERROR: {errs[0]}")
                else:
                    lines.append(f"{avenue} / {metro:<10} SOURCE EMPTY")
    return lines


def print_summary(run_date, since, collector_results, summary_lines, csv_paths,
                  sheet_status):
    print()
    print("=" * 60)
    print(f"INTENT SCAN SUMMARY  ({run_date})   window since {since}")
    print("=" * 60)
    print(f"Collectors ({len(collector_results)}):")
    for r in sorted(collector_results, key=lambda x: x.source_id):
        detail = f"  {r.error}" if r.error else ""
        counts = (f"  +{r.signals_added} signals / {r.entities_seen} entities"
                  if r.status == "OK" else "")
        print(f"  {r.source_id:<22} {r.status:<8}{counts}{detail}")
    timed_out = sorted(r.source_id for r in collector_results
                       if r.status == "SKIPPED"
                       and "timeout" in (r.error or "").lower())
    if timed_out:
        print(f"Timed out (abandoned by watchdog, scan continued): "
              f"{', '.join(timed_out)}")
    print("Avenues:")
    for line in summary_lines:
        print(f"  {line}")
    print("CSVs written:")
    for p in csv_paths:
        print(f"  {p}")
    print(f"Sheet: {sheet_status}")
    print("=" * 60)


def _load_synthetic_module():
    path = ENGINE_ROOT / "fixtures" / "synthetic_test.py"
    spec = importlib.util.spec_from_file_location("intent_synthetic_fixtures", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None):
    parser = argparse.ArgumentParser(description="Dux Machina Intent Signal Engine")
    parser.add_argument("--avenues", nargs="*", default=None,
                        help="avenues to scan (default: all)")
    parser.add_argument("--metros", nargs="*", default=None,
                        help="metros to scan (default: all)")
    parser.add_argument("--since-days", type=int, default=7,
                        help="lookback window in days (default 7)")
    parser.add_argument("--backfill-days", type=int, default=None,
                        help="override lookback for a deep backfill run")
    parser.add_argument("--no-sheet", action="store_true",
                        help="skip Google Sheet export")
    parser.add_argument("--export-only", action="store_true",
                        help="skip ALL collection; re-score the already-persisted "
                             "signals in the real DB across ALL avenues+metros and "
                             "run the combined export (customers/acquisitions CSVs "
                             "+ CUSTOMERS/ACQUISITIONS/PIPELINE sheet tabs). Use as "
                             "the assembly step after per-avenue collection runs. "
                             "Writes the sheet unless --no-sheet; degrades to "
                             "CSV-only if creds/spreadsheet id are absent.")
    parser.add_argument("--dry-run", action="store_true",
                        help="in-memory store + synthetic fixture signals; "
                             "no real DB, no sheet; CSVs -> OUTPUT_DIR/dry_run/")
    parser.add_argument("--scheduled", action="store_true",
                        help="mark this run as scheduled (logged in runs table)")
    args = parser.parse_args(argv)

    config.ensure_dirs()
    registry = config.load_registry()
    # --export-only is an assembly step: it must ALWAYS span every avenue+metro
    # so the combined customers/acquisitions lists are complete regardless of
    # which per-avenue collection runs preceded it. It also forces the real DB
    # (dry-run's in-memory store holds nothing to export).
    if args.export_only:
        args.dry_run = False
        avenues = list(registry["avenues"].keys())
        metros = list(registry["metros"].keys())
    else:
        avenues = _parse_list(args.avenues, list(registry["avenues"].keys()),
                              "avenue")
        metros = _parse_list(args.metros, list(registry["metros"].keys()), "metro")
    lookback = args.backfill_days if args.backfill_days else args.since_days
    since = date.today() - timedelta(days=lookback)
    run_date = date.today().isoformat()

    if args.dry_run:
        print("[dry-run] in-memory store seeded with fixtures synthetic signals; "
              "real DB and Google Sheet untouched.")
        store = Store(":memory:")
        synth = _load_synthetic_module()
        injected = synth.inject(store)
        print(f"[dry-run] injected {injected} synthetic signals.")
        output_dir = config.OUTPUT_DIR / "dry_run"
    else:
        store = Store()
        output_dir = config.OUTPUT_DIR

    run_id = store.start_run({"argv": vars(args), "scheduled": args.scheduled,
                              "dry_run": args.dry_run,
                              "export_only": args.export_only})

    if args.export_only:
        print("[export-only] skipping all collection; re-scoring the persisted "
              f"DB across {len(avenues)} avenues x {len(metros)} metros and "
              "assembling the combined lists.", flush=True)
        collector_results = []
    else:
        collector_results = run_collectors(store, registry, avenues, metros, since)
    rows = build_rows(store, registry, avenues, metros, run_id=run_id)
    csv_paths = export_csv(rows, run_date=run_date, output_dir=output_dir)

    sheet_status = "skipped"
    if args.dry_run:
        sheet_status = "skipped (--dry-run)"
    elif args.no_sheet:
        sheet_status = "skipped (--no-sheet)"
    else:
        from export_sheet import export_sheet  # lazy: google libs only when needed
        summary_rows = [[line] for line in
                        build_summary_lines(registry, avenues, metros, rows,
                                            collector_results)]
        try:
            ok = export_sheet(rows, summary_rows=summary_rows)
            sheet_status = "updated" if ok else "skipped (no spreadsheet id or creds)"
            if ok:
                # Durable PIPELINE tracker tab — guarded so a failure here can
                # never crash the scan (the tab is a convenience, not the scan).
                try:
                    from pipeline_tab import sync_pipeline
                    presult = sync_pipeline()
                    if presult.get("ok"):
                        print(f"[pipeline] PIPELINE tab refreshed: "
                              f"{presult['rows']} companies, "
                              f"{presult['preserved']} statuses preserved.")
                except Exception as pexc:
                    print(f"[pipeline] WARNING: PIPELINE tab refresh failed "
                          f"({type(pexc).__name__}: {pexc}) - scan unaffected.")
        except Exception as exc:
            sheet_status = f"ERROR: {type(exc).__name__}: {exc}"

    summary_lines = build_summary_lines(registry, avenues, metros, rows,
                                        collector_results)
    summary_payload = {
        "collectors": [vars(r) for r in collector_results],
        "avenues": summary_lines,
        "csv_paths": [str(p) for p in csv_paths],
        "sheet": sheet_status,
    }
    any_error = any(r.status == "ERROR" for r in collector_results)
    store.finish_run(run_id, status="PARTIAL" if any_error else "OK",
                     summary=summary_payload)

    print_summary(run_date, since.isoformat(), collector_results, summary_lines,
                  csv_paths, sheet_status)
    store.close()
    sys.stdout.flush()
    sys.stderr.flush()
    return 0


if __name__ == "__main__":
    code = main()
    # Flush before exit: any daemon watchdog worker still stuck in a stalled
    # HTTP call is abandoned here (daemon threads do not block interpreter
    # shutdown), so the SUMMARY above is always written.
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(code)
