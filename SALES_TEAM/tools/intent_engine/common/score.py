"""Scoring: time-decayed weighted sum with a stacking bonus (v1 pain) plus the
v2 EXPECTED_VALUE layer (timing x ability-to-pay x deal-size).

FROZEN INTERFACE (v1, unchanged signature — now with a per-type cap):
    score_entity(signals, avenue_cfg, as_of=None) -> (score, sorted_types)

    per-signal contribution = weight * magnitude * 0.5 ** (age_days / half_life_days)
    PER-TYPE CAP (v2 addition, kills bulk-filing dominance): within one
    signal_type, contributions are sorted descending; the first
    `per_type_cap` (default 3) count fully, each one after that is
    multiplied by per_type_diminish ** (i - cap + 1) (default 0.5) —
    so 20 identical liens converge to ~cap+1 units instead of 20.
    then, when >= 2 distinct signal types contribute:
        score *= min(stacking_bonus ** (distinct_types - 1), 3.0)

FROZEN INTERFACE (v2):
    pain_normalize(pain, avenue_cfg) -> float 0..1
        = pain / (pain + hot_threshold)     (saturating; 0.5 exactly at hot)
    expected_value(pain_norm, timing, ability, deal_size, deal_size_weight=1.0)
        -> float 0..2
        = pain_norm * timing * ability * (1 - 0.5*w*(1 - deal_size))
        (w=1 -> the balanced (0.5 + 0.5*deal_size) factor; w=0 ignores size)
    score_entity_v2(pain_signals, pay_signals, timing_signals, entity,
                    avenue_cfg, as_of=None, timing_defs=None) -> dict with keys:
        expected_value, pain, pain_norm, timing, timing_window, ability_to_pay,
        pay_sources, pay_data, deal_size, deal_size_known, top_signals, hot

Factor bounds: pain_norm 0..1, timing 1..2, ability_to_pay 0..1, deal_size 0..1,
deal-size factor 0.5..1 (at w=1) => expected_value 0..2.

Signal-window constants (used by the orchestrator to partition signals):
    MAX_AGE_DAYS (180)         pain signals
    PAY_MAX_AGE_DAYS (1095)    solvency signals (staleness-decayed in solvency.py)
    TIMING_MAX_AGE_DAYS (540)  timing signals (windows derive from old anchors)
"""
from datetime import date

from common.solvency import (PAY_MAX_AGE_DAYS, deal_size_proxy,  # noqa: F401
                             score_ability_to_pay)
from common.timing import TIMING_MAX_AGE_DAYS, timing_detail  # noqa: F401

MAX_AGE_DAYS = 180
STACK_CAP = 3.0
DEFAULT_PER_TYPE_CAP = 3
DEFAULT_PER_TYPE_DIMINISH = 0.5


def score_entity(signals, avenue_cfg, as_of=None):
    """signals: list of dicts with signal_type, signal_date (ISO), magnitude.
    avenue_cfg: the avenue's slice of signal_registry.json
    (has 'signals' {type: {weight, half_life_days}}, 'stacking_bonus', and
    optionally 'per_type_cap' / 'per_type_diminish').

    Returns (score: float, sorted_types: list[str]) — types sorted by their
    decayed contribution, highest first.
    """
    if as_of is None:
        as_of = date.today()
    sig_defs = avenue_cfg.get("signals", {})
    per_type = {}  # signal_type -> list of individual decayed contributions
    for s in signals:
        stype = s["signal_type"]
        sdef = sig_defs.get(stype)
        if sdef is None:
            continue  # unknown type for this avenue — skip
        try:
            sdate = date.fromisoformat(str(s["signal_date"])[:10])
        except ValueError:
            continue
        age_days = (as_of - sdate).days
        if age_days < 0:
            age_days = 0
        if age_days > MAX_AGE_DAYS:
            continue
        half_life = float(sdef.get("half_life_days", 90)) or 90.0
        weight = float(sdef.get("weight", 1.0))
        magnitude = max(0.0, min(1.0, float(s.get("magnitude", 0.0))))
        decayed = weight * magnitude * (0.5 ** (age_days / half_life))
        per_type.setdefault(stype, []).append(decayed)

    # per-type cap: full credit for the strongest `cap` signals of a type,
    # geometric diminishing for the rest (bulk-filing dampener)
    cap = max(1, int(avenue_cfg.get("per_type_cap", DEFAULT_PER_TYPE_CAP)))
    dim = float(avenue_cfg.get("per_type_diminish", DEFAULT_PER_TYPE_DIMINISH))
    dim = max(0.0, min(0.9, dim))
    contrib = {}
    for stype, vals in per_type.items():
        vals.sort(reverse=True)
        total = 0.0
        for i, v in enumerate(vals):
            factor = 1.0 if i < cap else dim ** (i - cap + 1)
            total += v * factor
        contrib[stype] = total

    base = sum(contrib.values())
    distinct = len([t for t, v in contrib.items() if v > 0])
    score = base
    if distinct >= 2:
        bonus = float(avenue_cfg.get("stacking_bonus", 1.5))
        score = base * min(bonus ** (distinct - 1), STACK_CAP)

    sorted_types = sorted(contrib, key=lambda t: contrib[t], reverse=True)
    return score, sorted_types


# ---------------------------------------------------------------------------
# v2: EXPECTED_VALUE = pain_norm x timing x ability_to_pay x deal-size factor
# ---------------------------------------------------------------------------

def pain_normalize(pain, avenue_cfg):
    """Saturating 0..1 normalization: pain/(pain + hot_threshold).
    Exactly 0.5 at the avenue's hot threshold; asymptotically -> 1.0."""
    midpoint = float(avenue_cfg.get("hot_threshold", 5.0)) or 5.0
    p = max(0.0, float(pain))
    return p / (p + midpoint)


def expected_value(pain_norm, timing, ability, deal_size, deal_size_weight=1.0):
    """BALANCED master score, bounded 0..2. Deal size is present but cannot
    dominate: its factor spans only [1 - 0.5*w, 1.0]."""
    p = max(0.0, min(1.0, float(pain_norm)))
    t = max(1.0, min(2.0, float(timing)))
    a = max(0.0, min(1.0, float(ability)))
    d = max(0.0, min(1.0, float(deal_size)))
    w = max(0.0, min(1.0, float(deal_size_weight)))
    ds_factor = 1.0 - 0.5 * w * (1.0 - d)
    return p * t * a * ds_factor


def score_entity_v2(pain_signals, pay_signals, timing_signals, entity,
                    avenue_cfg, as_of=None, timing_defs=None):
    """Full v2 breakdown for one entity in one avenue. All sub-scores returned
    for transparency; missing pay data => ability 0.5 + pay_data='unknown'
    (the row is scored, never dropped)."""
    if as_of is None:
        as_of = date.today()
    pain, top_types = score_entity(pain_signals, avenue_cfg, as_of=as_of)
    pain_norm = pain_normalize(pain, avenue_cfg)
    tdetail = timing_detail(entity, timing_signals, today=as_of,
                            timing_defs=timing_defs)
    ability, pay_sources, pay_data = score_ability_to_pay(
        entity, pay_signals, distress_signals=pain_signals, as_of=as_of)
    deal_size, ds_known, ds_sources = deal_size_proxy(entity, pay_signals,
                                                      as_of=as_of)
    w = float(avenue_cfg.get("deal_size_weight", 1.0))
    ev = expected_value(pain_norm, tdetail["boost"], ability, deal_size, w)
    hot = pain >= float(avenue_cfg.get("hot_threshold", 999))
    return {
        "expected_value": ev,
        "pain": pain,
        "pain_norm": pain_norm,
        "timing": tdetail["boost"],
        "timing_window": tdetail["window"],
        "ability_to_pay": ability,
        "pay_sources": pay_sources,
        "pay_data": pay_data,
        "deal_size": deal_size,
        "deal_size_known": ds_known,
        "top_signals": top_types,
        "hot": hot,
    }
