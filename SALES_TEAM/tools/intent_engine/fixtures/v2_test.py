"""v2 scoring unit tests — solvency, timing, per-type cap, expected value.

Proves the four Phase 0 guarantees:
  (a) a solvent-wounded profile outranks BOTH a dying one and a calm-solvent
      one (EV level), and at equal pain + equal pay data the distress-density
      guardrail alone separates solvent from dying (ability level)
  (b) every factor is bounded: pain_norm/ability/deal_size in 0..1,
      timing in 1..2, expected_value in 0..2 — fuzzed over hostile inputs
  (c) missing pay data => ability exactly 0.5 + pay_data='unknown', and the
      row still flows through build_rows (never dropped)
  (d) the per-type cap stops 20 identical liens from dominating: the pile
      converges (20 ~= 8 identical) and a 3-signal diverse profile outranks it

Usage: python fixtures/v2_test.py          (exit 0 = PASS)
"""
import sys
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import Signal  # noqa: E402
from common.score import (expected_value, pain_normalize, score_entity,  # noqa: E402
                          score_entity_v2)
from common.solvency import sba_credit_bucket, score_ability_to_pay  # noqa: E402
from common.timing import timing_boost, timing_detail  # noqa: E402
from common.store import Store  # noqa: E402

TODAY = date.today()
FAILURES = []


def check(cond, label):
    status = "ok " if cond else "FAIL"
    print(f"  [{status}] {label}")
    if not cond:
        FAILURES.append(label)


def _d(days_ago):
    return (TODAY - timedelta(days=days_ago)).isoformat()


def sig(stype, days_ago, mag, attrs=None):
    return {"signal_type": stype, "signal_date": _d(days_ago),
            "magnitude": mag, "attrs": attrs or {}}


def registry():
    return config.load_registry()


# ---------------------------------------------------------------------------
# (a) solvent-wounded outranks dying and calm-solvent
# ---------------------------------------------------------------------------

def test_ranking():
    print("(a) solvent-wounded outranks dying + calm-solvent")
    reg = registry()
    cfg = reg["avenues"]["pe_distress"]
    tdefs = reg["timing_signals"]

    wounds = [sig("lien_filed", 2, 1.0), sig("judgment_filed", 5, 0.8),
              sig("sba_maturity_window", 10, 0.6)]
    solvent_pay = [sig("size_parcels", 30, 0.75),
                   sig("credit_sba_loan", 60, sba_credit_bucket(600_000))]

    # A: solvent + wounded (3 wounds, real size + credit)
    a = score_entity_v2(wounds, solvent_pay, [], {}, cfg, as_of=TODAY,
                        timing_defs=tdefs)
    # B: dying (same 3 wounds PLUS 11 more liens; tiny size, no credit)
    dying_pain = wounds + [sig("lien_filed", 3 + i, 1.0,
                               {"ref": f"L{i}"}) for i in range(11)]
    b = score_entity_v2(dying_pain, [sig("size_parcels", 30, 0.10)], [], {},
                        cfg, as_of=TODAY, timing_defs=tdefs)
    # C: calm + solvent (one small old wound, same strong pay data as A)
    c = score_entity_v2([sig("lien_filed", 60, 0.4)], solvent_pay, [], {},
                        cfg, as_of=TODAY, timing_defs=tdefs)

    print(f"      A solvent-wounded EV={a['expected_value']:.3f} "
          f"(pain={a['pain']:.1f} pay={a['ability_to_pay']:.2f} ds={a['deal_size']:.2f})")
    print(f"      B dying           EV={b['expected_value']:.3f} "
          f"(pain={b['pain']:.1f} pay={b['ability_to_pay']:.2f} ds={b['deal_size']:.2f})")
    print(f"      C calm-solvent    EV={c['expected_value']:.3f} "
          f"(pain={c['pain']:.1f} pay={c['ability_to_pay']:.2f} ds={c['deal_size']:.2f})")
    check(a["expected_value"] > b["expected_value"],
          "solvent-wounded EV > dying EV (even though dying has MORE pain)")
    check(a["expected_value"] > c["expected_value"],
          "solvent-wounded EV > calm-solvent EV")
    check(b["ability_to_pay"] < 0.3, "dying ability_to_pay collapses (<0.3)")
    check(a["ability_to_pay"] > 0.6, "solvent-wounded ability_to_pay > 0.6")

    # equal pain + equal pay data: density guardrail alone separates them
    few, _, _ = score_ability_to_pay({}, solvent_pay, wounds, as_of=TODAY)
    many, _, _ = score_ability_to_pay({}, solvent_pay, dying_pain, as_of=TODAY)
    check(few > many,
          f"equal pay data: ability(3 wounds)={few:.2f} > ability(14 wounds)={many:.2f}")


# ---------------------------------------------------------------------------
# (b) all factors bounded, fuzzed over hostile inputs
# ---------------------------------------------------------------------------

def test_bounds():
    print("(b) factor bounds under fuzzing")
    import random
    random.seed(42)
    reg = registry()
    tdefs = reg["timing_signals"]
    types_pain = ["lien_filed", "judgment_filed", "sba_maturity_window"]
    types_pay = ["size_fleet", "size_parcels", "credit_sba_loan",
                 "credit_ucc_filing"]
    types_timing = ["insurance_renewal", "eviction_spike_window",
                    "stale_crossing_180", "abatement_deadline"]
    cfg = reg["avenues"]["pe_distress"]
    ok = True
    for trial in range(300):
        pain = [sig(random.choice(types_pain), random.randint(-30, 400),
                    random.uniform(-2, 5)) for _ in range(random.randint(0, 25))]
        pay = [sig(random.choice(types_pay), random.randint(-10, 2000),
                   random.uniform(-2, 5)) for _ in range(random.randint(0, 6))]
        tim = [sig(random.choice(types_timing), random.randint(-400, 500),
                   random.uniform(0, 1),
                   {"boost": random.uniform(-3, 9)} if random.random() < 0.3
                   else {}) for _ in range(random.randint(0, 4))]
        ent = {"attrs": {"power_units": random.choice([None, -5, 0, 3, 120, 9e9])}}
        v2 = score_entity_v2(pain, pay, tim, ent, cfg, as_of=TODAY,
                             timing_defs=tdefs)
        bounds = (0.0 <= v2["pain_norm"] <= 1.0
                  and 1.0 <= v2["timing"] <= 2.0
                  and 0.0 <= v2["ability_to_pay"] <= 1.0
                  and 0.0 <= v2["deal_size"] <= 1.0
                  and 0.0 <= v2["expected_value"] <= 2.0)
        if not bounds:
            ok = False
            print(f"      trial {trial} out of bounds: {v2}")
            break
    check(ok, "300 fuzz trials: pain_norm/ability/deal_size in 0..1, "
              "timing in 1..2, EV in 0..2")
    check(pain_normalize(0.0, cfg) == 0.0, "pain_norm(0) == 0")
    check(pain_normalize(1e9, cfg) < 1.0, "pain_norm(huge) < 1.0 (saturates)")
    check(abs(pain_normalize(float(cfg["hot_threshold"]), cfg) - 0.5) < 1e-9,
          "pain_norm(hot_threshold) == 0.5 exactly")
    check(expected_value(1.0, 2.0, 1.0, 1.0) == 2.0, "EV ceiling == 2.0")
    check(expected_value(1.0, 1.0, 1.0, 0.0) == 0.5,
          "EV deal-size floor factor == 0.5 (balanced, cannot dominate)")
    check(timing_boost({}, [], TODAY) == 1.0, "timing floor == 1.0 (no signals)")


# ---------------------------------------------------------------------------
# (c) missing pay data => 0.5 neutral + unknown, row never dropped
# ---------------------------------------------------------------------------

def test_missing_pay():
    print("(c) missing pay data => 0.5 neutral + pay_data=unknown, row kept")
    reg = registry()
    cfg = reg["avenues"]["property_mgmt"]
    v2 = score_entity_v2([sig("eviction_spike", 4, 0.9)], [], [], {}, cfg,
                         as_of=TODAY, timing_defs=reg["timing_signals"])
    check(v2["ability_to_pay"] == 0.5,
          f"ability == 0.5 exactly (got {v2['ability_to_pay']})")
    check(v2["pay_data"] == "unknown", "pay_data == 'unknown'")
    check(v2["expected_value"] > 0.0, "EV still > 0 (row scoreable)")

    # end-to-end: a pain-only entity must SURVIVE build_rows
    import run_intent_scan as ris
    store = Store(":memory:")
    store.add_signal(Signal(
        "biz:no pay data props|77002", "NO PAY DATA PROPS LLC", "houston",
        "property_mgmt", "eviction_spike", _d(4), 0.9, "synthetic",
        "https://example.test/ev-1", {}, {"zip": "77002"}))
    rows = ris.build_rows(store, reg, ["property_mgmt"], ["houston"])
    store.close()
    kept = [r for r in rows if "NO PAY DATA" in r["entity_name"]]
    check(len(kept) == 1, "pain-only row present in build_rows output")
    if kept:
        check(kept[0]["pay_data"] == "unknown" and
              kept[0]["ability_to_pay"] == 0.5,
              "row flagged unknown at 0.5, not dropped")
        check(kept[0]["funnel"] == "customers",
              "property_mgmt row routed to CUSTOMERS funnel")


# ---------------------------------------------------------------------------
# (d) per-type cap kills the 20-identical-liens dominance (SADE case)
# ---------------------------------------------------------------------------

def test_per_type_cap():
    print("(d) per-type cap: 20 identical liens cannot dominate")
    cfg = registry()["avenues"]["pe_distress"]

    def liens(n):
        return [sig("lien_filed", 1, 1.0, {"ref": i}) for i in range(n)]

    s8, _ = score_entity(liens(8), cfg, as_of=TODAY)
    s20, _ = score_entity(liens(20), cfg, as_of=TODAY)
    s20_uncapped = 20 * 4.0  # weight 4, mag 1, fresh, no stacking (1 type)
    print(f"      8 identical={s8:.2f}  20 identical={s20:.2f}  "
          f"uncapped-20 would be {s20_uncapped:.0f}")
    check(s20 < 0.30 * s20_uncapped, "20-lien pile scores <30% of uncapped sum")
    check(s20 <= s8 * 1.05, "pile converges: score(20) ~= score(8)")
    check(s20 >= s8, "more signals never LOWERS the score (monotone)")

    diverse, _ = score_entity(
        [sig("lien_filed", 1, 1.0), sig("judgment_filed", 2, 1.0),
         sig("sba_maturity_window", 3, 1.0)], cfg, as_of=TODAY)
    print(f"      3-signal diverse profile={diverse:.2f}")
    check(diverse > s20,
          "3 diverse signals outrank 20 identical liens (diversity > bulk)")


# ---------------------------------------------------------------------------
# timing window sanity (supports the frozen attachment contract)
# ---------------------------------------------------------------------------

def test_timing_windows():
    print("(+) timing windows: renewal fires ~12mo after policy effective")
    tdefs = registry()["timing_signals"]
    in_window = [sig("insurance_renewal", 350, 1.0)]
    d = timing_detail({}, in_window, TODAY, timing_defs=tdefs)
    check(abs(d["boost"] - 1.8) < 1e-9,
          f"effective 350d ago -> boost 1.8 (window {d['window']})")
    check(timing_boost({}, [sig("insurance_renewal", 100, 1.0)], TODAY,
                       timing_defs=tdefs) == 1.0,
          "effective 100d ago -> no boost yet (window opens ~day 335)")
    clamped = timing_boost({}, [sig("eviction_spike_window", 1, 1.0,
                                    {"boost": 99})], TODAY, timing_defs=tdefs)
    check(clamped == 2.0, "absurd per-signal boost clamps at 2.0")


def test_funnel_tags():
    print("(+) funnel routing tags in registry")
    reg = registry()
    expect = {"trucking": "customers", "property_mgmt": "customers",
              "mechanical": "customers", "manufacturing": "customers",
              "dead_listings": "acquisitions", "pe_distress": "acquisitions"}
    got = {a: reg["avenues"][a].get("funnel") for a in expect}
    check(got == expect, f"funnel tags correct: {got}")


def main():
    print("=" * 64)
    print("V2 SCORING TESTS - solvency x timing x pain x deal-size")
    print("=" * 64)
    test_ranking()
    test_bounds()
    test_missing_pay()
    test_per_type_cap()
    test_timing_windows()
    test_funnel_tags()
    print("-" * 64)
    if FAILURES:
        print(f"FAIL ({len(FAILURES)} failed)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("PASS (all v2 scoring guarantees hold)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
