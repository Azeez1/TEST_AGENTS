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
    """Load enabled collectors and run each, containing ALL errors."""
    results = []
    collectors, missing, disabled = load_collectors(registry)
    for c in collectors:
        if c.avenue not in avenues:
            results.append(CollectorResult(c.source_id, 0, 0, "SKIPPED",
                                           f"avenue {c.avenue} not selected"))
            continue
        if not set(m.lower() for m in c.metros) & set(metros):
            results.append(CollectorResult(c.source_id, 0, 0, "SKIPPED",
                                           "no selected metro"))
            continue
        try:
            r = c.collect(since, store, registry)
            if not isinstance(r, CollectorResult):
                r = CollectorResult(c.source_id, 0, 0, "ERROR",
                                    "collector returned non-CollectorResult")
        except Exception as exc:  # contract says never raise, but contain anyway
            r = CollectorResult(c.source_id, 0, 0, "ERROR",
                                f"{type(exc).__name__}: {exc}")
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
    parser.add_argument("--dry-run", action="store_true",
                        help="in-memory store + synthetic fixture signals; "
                             "no real DB, no sheet; CSVs -> OUTPUT_DIR/dry_run/")
    parser.add_argument("--scheduled", action="store_true",
                        help="mark this run as scheduled (logged in runs table)")
    args = parser.parse_args(argv)

    config.ensure_dirs()
    registry = config.load_registry()
    avenues = _parse_list(args.avenues, list(registry["avenues"].keys()), "avenue")
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
                              "dry_run": args.dry_run})

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
