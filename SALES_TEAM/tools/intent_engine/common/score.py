"""Scoring: time-decayed weighted sum with a stacking bonus.

FROZEN INTERFACE:
    score_entity(signals, avenue_cfg, as_of=None) -> (score, sorted_types)

    score = sum over signals <= 180 days old of:
                weight * magnitude * 0.5 ** (age_days / half_life_days)
    then, when >= 2 distinct signal types contribute:
                score *= min(stacking_bonus ** (distinct_types - 1), 3.0)
"""
from datetime import date

MAX_AGE_DAYS = 180
STACK_CAP = 3.0


def score_entity(signals, avenue_cfg, as_of=None):
    """signals: list of dicts with signal_type, signal_date (ISO), magnitude.
    avenue_cfg: the avenue's slice of signal_registry.json
    (has 'signals' {type: {weight, half_life_days}} and 'stacking_bonus').

    Returns (score: float, sorted_types: list[str]) — types sorted by their
    decayed contribution, highest first.
    """
    if as_of is None:
        as_of = date.today()
    sig_defs = avenue_cfg.get("signals", {})
    contrib = {}  # signal_type -> summed decayed contribution
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
        contrib[stype] = contrib.get(stype, 0.0) + decayed

    base = sum(contrib.values())
    distinct = len([t for t, v in contrib.items() if v > 0])
    score = base
    if distinct >= 2:
        bonus = float(avenue_cfg.get("stacking_bonus", 1.5))
        score = base * min(bonus ** (distinct - 1), STACK_CAP)

    sorted_types = sorted(contrib, key=lambda t: contrib[t], reverse=True)
    return score, sorted_types
