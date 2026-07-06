"""Shared plumbing for the v2 ability-to-pay collectors
(pay_sba, pay_hcad, pay_census_size, pay_ga_ucc).

Internal helper — underscore prefix, NOT a collector, never listed in
collectors_enabled and never imported by load_collectors().

Pay collectors differ from pain collectors in one structural way: they do not
discover NEW entities, they ATTACH solvency signals to entities that pain
collectors already put in the store. Two consequences:

1.  EMISSION — every Signal is emitted with the MATCHED entity's own
    entity_key / name / avenue / metro. store.add_signal() upserts the entity
    row from the signal's identity fields, so emitting under any other
    avenue/metro/name would silently rewrite the entity. Attaching on the
    exact entity_key means the signal lands at resolve conf 1.0; the match
    heuristics below are therefore the collector's identity claim and are
    deliberately conservative (see name_quality_ok / zip-conflict veto in
    each collector).

2.  SELF-TEST — an empty throwaway store has nothing to join against, so the
    harness first copies entities READ-ONLY out of the real DB at
    config.DB_PATH into the in-memory store, then runs collect(). Nothing is
    ever written back to the real DB or the sheet.

Pay signals use the PAY_MAX_AGE_DAYS (1095d) window from common/solvency.py,
not the orchestrator's `since` — a 2-year-old SBA loan is still credit data
(staleness decay handles the aging), so collect(since, ...) intentionally
ignores `since` for the join window.
"""
import json
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors._federal import write_fixture  # noqa: E402


def name_quality_ok(name_norm):
    """Guard against junk name joins: a normalized name is distinctive enough
    to assert identity only when it has >= 2 tokens or >= 8 characters
    (spike matches were multi-token: DOGS N SUDS, WEED PRO LAWN CARE, ...)."""
    nn = (name_norm or "").strip()
    if not nn:
        return False
    return len(nn.split()) >= 2 or len(nn) >= 8


def entity_name_index(store, avenues, metros=None):
    """Index the store's existing entities by lower-cased name_norm.

    Returns {name_norm_lower: [entity dict, ...]} for the given avenues
    (and metros, when provided), skipping entities whose normalized name
    fails name_quality_ok. Entities are the join targets — pay collectors
    never create entities of their own.
    """
    index = {}
    for avenue in avenues:
        for e in store.iter_entities(avenue=avenue):
            if metros and e.get("metro") not in metros:
                continue
            nn = (e.get("name_norm") or "").strip().lower()
            if not nn or not name_quality_ok(nn):
                continue
            index.setdefault(nn, []).append(e)
    return index


def seed_entities_from_real_db(mem_store, avenues=None, cap_per_avenue=None):
    """Copy entities READ-ONLY from the real DB into an in-memory store so a
    pay collector's --self-test has something to join against.

    Opens config.DB_PATH with sqlite URI mode=ro (cannot write). Returns the
    number of entities seeded; 0 when the real DB does not exist yet.
    """
    db = Path(config.DB_PATH)
    if not db.exists():
        return 0
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    seeded = 0
    try:
        q = "SELECT * FROM entities"
        args = []
        if avenues:
            q += f" WHERE avenue IN ({','.join('?' * len(avenues))})"
            args = list(avenues)
        per_avenue = {}
        for r in conn.execute(q, args):
            e = dict(r)
            av = e["avenue"]
            if cap_per_avenue is not None:
                if per_avenue.get(av, 0) >= cap_per_avenue:
                    continue
                per_avenue[av] = per_avenue.get(av, 0) + 1
            try:
                attrs = json.loads(e.get("attrs") or "{}")
                if not isinstance(attrs, dict):
                    attrs = {}
            except ValueError:
                attrs = {}
            mem_store.upsert_entity(
                e["entity_key"], av, e["metro"], e["name"],
                zip=e.get("zip"), phone=e.get("phone"), email=e.get("email"),
                street=e.get("street"), attrs=attrs)
            seeded += 1
    finally:
        conn.close()
    return seeded


def pay_self_test(collector, seed_avenues, cap_per_avenue=None, days=30):
    """Shared --self-test harness for pay collectors.

    Seeds an in-memory store with real-DB entities (read-only), runs
    collect(), prints status + per-type counts, saves
    fixtures/<source_id>_sample.json. Writes NOTHING to the real DB or sheet.
    Returns a process exit code.
    """
    from common.store import Store

    registry = config.load_registry()
    store = Store(db_path=":memory:")
    seeded = seed_entities_from_real_db(store, avenues=seed_avenues,
                                        cap_per_avenue=cap_per_avenue)
    since = date.today() - timedelta(days=days)
    print(f"[self-test] {collector.source_id}: seeded {seeded} entities "
          f"(avenues={list(seed_avenues)}"
          f"{'' if cap_per_avenue is None else f', cap={cap_per_avenue}/avenue'}) "
          f"from real DB (read-only); collecting into in-memory store ...")
    if seeded == 0:
        print("[self-test] WARNING: real DB has no entities to join against — "
              "run the pain collectors (run_intent_scan.py) first for a "
              "meaningful test.")
    result = collector.collect(since, store, registry)

    print(f"[self-test] status          = {result.status}")
    print(f"[self-test] signals_added   = {result.signals_added}")
    print(f"[self-test] entities_seen   = {result.entities_seen}")
    if result.error:
        print(f"[self-test] notes           = {result.error}")

    by_type = {}
    for s in store.get_signals():
        if s["source_id"] != collector.source_id:
            continue
        by_type[s["signal_type"]] = by_type.get(s["signal_type"], 0) + 1
    for t, n in sorted(by_type.items()):
        print(f"    {t}: {n}")
    for s in [s for s in store.get_signals()
              if s["source_id"] == collector.source_id][:5]:
        print(f"    {s['signal_date']}  {s['signal_type']:<18} "
              f"mag={s['magnitude']:.2f} {s['metro']:<8} {s['entity_name'][:48]}")

    path = write_fixture(collector.source_id,
                         getattr(collector, "sample_payload", None), result)
    print(f"[self-test] fixture -> {path}")
    store.close()
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


def pay_selftest_main(collector_factory, seed_avenues, description,
                      default_cap=None):
    """argparse wrapper every pay collector's __main__ delegates to."""
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--self-test", action="store_true",
                        help="join against real-DB entities (read-only) in a "
                             "throwaway in-memory store; prints counts, saves "
                             "a fixture; no sheet, no real-DB writes")
    parser.add_argument("--cap", type=int, default=default_cap,
                        help="self-test: max entities seeded per avenue "
                             f"(default {default_cap or 'unlimited'})")
    args = parser.parse_args()
    if args.self_test:
        return pay_self_test(collector_factory(), seed_avenues,
                             cap_per_avenue=args.cap)
    parser.print_help()
    print("\nThis module is normally run by run_intent_scan.py; "
          "standalone use supports --self-test only.")
    return 2
