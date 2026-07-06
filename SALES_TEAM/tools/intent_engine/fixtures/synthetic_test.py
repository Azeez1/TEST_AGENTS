"""Synthetic end-to-end test for the intent engine core (no collectors needed).

Injects ~15 synthetic Signals across all 6 avenues into a temp (in-memory)
store, runs resolve + score + export_csv into a temp dir, asserts CSVs are
written and hot rows appear, prints PASS/FAIL plus the summary.

Also exercises the match ladder:
    - exact key           (1.0)  IRONHAUL two signals on one dot key
    - name_norm + zip     (0.9)  LONE STAR HAULERS: dot: key <-> biz: key, cross-avenue
    - name_norm + metro   (0.6)  STONEBRIDGE at two different zips, flagged weak

Usage: python fixtures/synthetic_test.py
"""
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import Signal  # noqa: E402
from common.store import Store  # noqa: E402


def _d(days_ago):
    return (date.today() - timedelta(days=days_ago)).isoformat()


def make_synthetic_signals():
    """~15 signals across all 6 avenues; several stack, several stay cold."""
    return [
        # --- trucking (houston): IRONHAUL stacks hot; LONE STAR stays cold ---
        Signal("dot:2422093", "IRONHAUL EXPRESS LLC", "houston", "trucking",
               "insurance_cancellation", _d(3), 1.0, "synthetic",
               "https://li-public.fmcsa.dot.gov/2422093", {"rec": 1},
               {"zip": "77040", "phone": "713-555-0101", "street": "8800 Fairbanks N Houston Rd"}),
        Signal("dot:2422093", "IRONHAUL EXPRESS LLC", "houston", "trucking",
               "recent_crash", _d(10), 0.8, "synthetic",
               "https://ai.fmcsa.dot.gov/crash/2422093", {"rec": 2}, {"zip": "77040"}),
        Signal("dot:9999999", "LONE STAR HAULERS INC", "houston", "trucking",
               "oos_rate_high", _d(40), 0.5, "synthetic",
               "https://ai.fmcsa.dot.gov/sms/9999999", {"rec": 3}, {"zip": "77038"}),
        # --- pe_distress: LONE STAR lien merges 0.9 with the dot: entity above ---
        Signal("biz:lone star haulers|77038", "LONE STAR HAULERS LLC", "houston",
               "pe_distress", "lien_filed", _d(9), 1.0, "synthetic",
               "https://www.cclerk.hctx.net/liens/LN-2026-4410", {"rec": 4},
               {"zip": "77038"}),
        # --- property_mgmt (houston): STONEBRIDGE hot; second zip weak-links 0.6 ---
        Signal("biz:stonebridge properties|77002", "STONEBRIDGE PROPERTIES LLC",
               "houston", "property_mgmt", "eviction_spike", _d(5), 0.9, "synthetic",
               "https://jp.hctx.net/evictions/2026-88121", {"rec": 5},
               {"zip": "77002", "phone": "713-555-0177"}),
        Signal("biz:stonebridge properties|77002", "STONEBRIDGE PROPERTIES LLC",
               "houston", "property_mgmt", "violation_cluster", _d(12), 0.7,
               "synthetic", "https://data.houstontx.gov/violations/V-33019",
               {"rec": 6}, {"zip": "77002"}),
        Signal("biz:stonebridge properties|77009", "STONEBRIDGE PROPERTIES",
               "houston", "property_mgmt", "eviction_spike", _d(8), 0.4, "synthetic",
               "https://jp.hctx.net/evictions/2026-88355", {"rec": 7},
               {"zip": "77009"}),
        # --- mechanical (atlanta): single moderate signal, stays below threshold ---
        Signal("biz:meridian mechanical|30303", "MERIDIAN MECHANICAL CONTRACTORS",
               "atlanta", "mechanical", "permit_volume_growth", _d(20), 1.0,
               "synthetic", "https://permits.atlantaga.gov/BP-2026-5521", {"rec": 8},
               {"zip": "30303", "email": "office@meridianmech.example"}),
        # --- manufacturing (houston): ACME stacks hot; GULF COAST stays cold ---
        Signal("biz:acme fabrication|77041", "ACME FABRICATION LLC", "houston",
               "manufacturing", "osha_citation", _d(7), 0.9, "synthetic",
               "https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1771001",
               {"rec": 9}, {"zip": "77041", "street": "5501 Brittmoore Rd"}),
        Signal("biz:acme fabrication|77041", "ACME FABRICATION LLC", "houston",
               "manufacturing", "warn_notice", _d(15), 0.8, "synthetic",
               "https://www.twc.texas.gov/warn/2026-0455", {"rec": 10},
               {"zip": "77041"}),
        Signal("biz:gulf coast plastics|77015", "GULF COAST PLASTICS CO", "houston",
               "manufacturing", "epa_violation", _d(30), 0.6, "synthetic",
               "https://echo.epa.gov/detailed-facility-report?fid=110001234567",
               {"rec": 11}, {"zip": "77015"}),
        # --- pe_distress (houston): ACME lien + judgment stack hot (bonus 2.0) ---
        Signal("biz:acme fabrication|77041", "ACME FABRICATION LLC", "houston",
               "pe_distress", "lien_filed", _d(9), 1.0, "synthetic",
               "https://www.cclerk.hctx.net/liens/LN-2026-5102", {"rec": 12},
               {"zip": "77041"}),
        Signal("biz:acme fabrication|77041", "ACME FABRICATION LLC", "houston",
               "pe_distress", "judgment_filed", _d(14), 0.75, "synthetic",
               "https://www.cclerk.hctx.net/judgments/JG-2026-0918", {"rec": 13},
               {"zip": "77041"}),
        # --- dead_listings (houston): stale + price cut stacks hot ---
        Signal("bbs:HOU-4471", "MACHINE SHOP GULF COAST", "houston", "dead_listings",
               "stale_180d", _d(0), 1.0, "synthetic",
               "https://www.bizbuysell.com/Business-Opportunity/HOU-4471", {"rec": 14},
               {"zip": "77029"}),
        Signal("bbs:HOU-4471", "MACHINE SHOP GULF COAST", "houston", "dead_listings",
               "price_cut", _d(20), 0.66, "synthetic",
               "https://www.bizbuysell.com/Business-Opportunity/HOU-4471#price",
               {"rec": 15}, {"zip": "77029"}),
    ]


def inject(store):
    """Add all synthetic signals to a store. Returns count inserted."""
    return sum(1 for sig in make_synthetic_signals() if store.add_signal(sig))


def run_test():
    import resolve as resolve_mod
    import run_intent_scan as ris
    from export_csv import export_csv

    registry = config.load_registry()
    avenues = list(registry["avenues"].keys())
    metros = list(registry["metros"].keys())

    store = Store(":memory:")
    injected = inject(store)
    # re-inject to prove dedup idempotency
    dupes = inject(store)

    failures = []
    if injected < 12:
        failures.append(f"expected >=12 synthetic signals injected, got {injected}")
    if dupes != 0:
        failures.append(f"dedup failed: {dupes} duplicates inserted on re-inject")

    # match ladder assertions
    _, key_map = resolve_mod.resolve(store)
    if (key_map["dot:9999999"]["canonical"]
            != key_map["biz:lone star haulers|77038"]["canonical"]):
        failures.append("name+zip (0.9) merge failed: LONE STAR dot:/biz: not clustered")
    sb_a = key_map["biz:stonebridge properties|77002"]
    sb_b = key_map["biz:stonebridge properties|77009"]
    if sb_a["canonical"] != sb_b["canonical"]:
        failures.append("name+metro (0.6) merge failed: STONEBRIDGE zips not clustered")
    elif not (sb_a["weak"] or sb_b["weak"]):
        failures.append("weak flag missing on the 0.6 STONEBRIDGE match")

    rows = ris.build_rows(store, registry, avenues, metros)
    out_dir = Path(tempfile.mkdtemp(prefix="intent_synth_"))
    paths = export_csv(rows, output_dir=out_dir)

    if not paths:
        failures.append("no CSVs written")
    for p in paths:
        if not p.exists():
            failures.append(f"missing CSV: {p}")

    avenues_with_rows = {r["avenue"] for r in rows}
    if avenues_with_rows != set(avenues):
        failures.append(f"expected rows in all 6 avenues, got {sorted(avenues_with_rows)}")

    hot_rows = [r for r in rows if r["hot"]]
    if not hot_rows:
        failures.append("no hot rows produced")
    expected_hot_avenues = {"trucking", "property_mgmt", "manufacturing",
                            "pe_distress", "dead_listings"}
    got_hot_avenues = {r["avenue"] for r in hot_rows}
    if got_hot_avenues != expected_hot_avenues:
        failures.append(f"hot avenues mismatch: expected {sorted(expected_hot_avenues)}, "
                        f"got {sorted(got_hot_avenues)}")

    hotlist = [p for p in paths if "hotlist" in p.name]
    if not hotlist:
        failures.append("hotlist CSV missing")
    else:
        with open(hotlist[0], encoding="utf-8") as f:
            n_lines = sum(1 for _ in f)
        if n_lines < 2:
            failures.append("hotlist CSV has no data rows")

    # weak match_conf surfaces on the stonebridge row
    sb_rows = [r for r in rows if r["avenue"] == "property_mgmt"
               and "STONEBRIDGE" in r["entity_name"].upper()]
    if sb_rows and abs(sb_rows[0]["match_conf"] - 0.6) > 1e-9:
        failures.append(f"expected STONEBRIDGE match_conf 0.6 (weak member contributed), "
                        f"got {sb_rows[0]['match_conf']}")

    # ---- summary ----
    print("=" * 60)
    print("SYNTHETIC FIXTURES TEST - intent engine core")
    print("=" * 60)
    print(f"signals injected: {injected} (re-inject dupes: {dupes})")
    print(f"rows scored: {len(rows)}  |  hot: {len(hot_rows)}")
    for r in sorted(rows, key=lambda r: (-r['hot'], -r['score'])):
        flag = "HOT " if r["hot"] else "    "
        print(f"  {flag}{r['avenue']:<14} {r['metro']:<8} {r['entity_name']:<32}"
              f" score={r['score']:>6.2f} conf={r['match_conf']:.2f}"
              f" [{r['top_signals']}]")
    print("CSVs written:")
    for p in paths:
        print(f"  {p}")

    if failures:
        print("\nFAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(run_test())
