"""Predictive-timing boost — Intent Engine v2.

FROZEN INTERFACE:
    timing_boost(entity, timing_signals, today=None, timing_defs=None)
        -> float in [1.0, 2.0]
    timing_detail(entity, timing_signals, today=None, timing_defs=None)
        -> {"boost": float, "window": str, "active": list[str]}

Model:
    Each timing signal type has a def {offset_days, window_days, ramp_days, boost}
    (from signal_registry.json top-level "timing_signals", falling back to
    DEFAULT_TIMING_DEFS below). The receptiveness window for one signal is:
        window_start = signal_date + offset_days
        window_end   = window_start + window_days
    A signal's attrs may override with explicit ISO "window_start"/"window_end"
    and a numeric "boost".
    boost(today) = 1.0                          before window_start - ramp_days
                 = linear 1.0 -> type boost     over the ramp
                 = type boost                   inside [window_start, window_end]
                 = 1.0                          after window_end
    Entity boost = max over its timing signals, clamped to [1.0, MAX_BOOST=2.0].
    No timing signals (or none in window) => 1.0 exactly.

Per-avenue windows this encodes (see registry defs):
    trucking       insurance_renewal      policy effective + 12mo (±30d)
    mechanical     permit_growth_window   surge starts at trajectory signal
    property_mgmt  eviction_spike_window  spike month + ~60d
    dead_listings  stale_crossing_180     DOM crossed 180 (seller despair window)
    manufacturing  abatement_deadline     OSHA abatement date - 30d .. +15d
    pe_distress    distress_acceleration  accumulation-rate spike + 90d

COLLECTOR ATTACHMENT CONTRACT (Phase 1):
    Timing signals are ordinary v1 Signal objects. signal_type MUST be
    registered under top-level "timing_signals" in signal_registry.json.
    signal_date = the anchor date the window derives from (e.g. the policy
    EFFECTIVE date for insurance_renewal, the ABATEMENT date for
    abatement_deadline with its negative offset). Prefer attrs
    window_start/window_end when the source gives explicit dates.
    Timing signals are accepted up to TIMING_MAX_AGE_DAYS (540) old.
"""
import json
from datetime import date, timedelta

MAX_BOOST = 2.0
TIMING_MAX_AGE_DAYS = 540   # old enough to keep effective+12mo windows alive

DEFAULT_TIMING_DEFS = {
    "insurance_renewal":     {"offset_days": 335, "window_days": 60, "ramp_days": 30, "boost": 1.8},
    "permit_growth_window":  {"offset_days": 0,   "window_days": 90, "ramp_days": 14, "boost": 1.4},
    "eviction_spike_window": {"offset_days": 0,   "window_days": 60, "ramp_days": 14, "boost": 1.5},
    "stale_crossing_180":    {"offset_days": 0,   "window_days": 60, "ramp_days": 0,  "boost": 1.6},
    "abatement_deadline":    {"offset_days": -30, "window_days": 45, "ramp_days": 0,  "boost": 1.5},
    "distress_acceleration": {"offset_days": 0,   "window_days": 90, "ramp_days": 0,  "boost": 1.6},
}


def _parse_attrs(obj):
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, str) and obj.strip():
        try:
            parsed = json.loads(obj)
            return parsed if isinstance(parsed, dict) else {}
        except (ValueError, TypeError):
            return {}
    return {}


def _parse_date(value):
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def _clamp_boost(b):
    try:
        return max(1.0, min(MAX_BOOST, float(b)))
    except (TypeError, ValueError):
        return 1.0


def _signal_window(signal, defs):
    """Resolve one timing signal to (window_start, window_end, ramp_days, boost)
    or None when it cannot be resolved."""
    stype = str(signal.get("signal_type", ""))
    d = dict(defs.get(stype) or {})
    if not d:
        return None
    attrs = _parse_attrs(signal.get("attrs"))
    ws = _parse_date(attrs.get("window_start"))
    we = _parse_date(attrs.get("window_end"))
    if ws is None:
        anchor = _parse_date(signal.get("signal_date"))
        if anchor is None:
            return None
        ws = anchor + timedelta(days=int(d.get("offset_days", 0)))
    if we is None:
        we = ws + timedelta(days=int(d.get("window_days", 30)))
    if we < ws:
        ws, we = we, ws
    boost = _clamp_boost(attrs.get("boost", d.get("boost", 1.5)))
    ramp = max(0, int(d.get("ramp_days", 0)))
    return ws, we, ramp, boost


def timing_detail(entity, timing_signals, today=None, timing_defs=None):
    """Full transparency version: boost + the window label that produced it.

    Returns {"boost": float in [1,2], "window": "type YYYY-MM-DD..YYYY-MM-DD" or "",
             "active": [labels of every in-window/ramping signal]}.
    """
    if today is None:
        today = date.today()
    defs = dict(DEFAULT_TIMING_DEFS)
    if timing_defs:
        for k, v in timing_defs.items():
            if isinstance(v, dict):
                defs[k] = {**defs.get(k, {}), **v}
    best, best_label, active = 1.0, "", []
    for s in timing_signals or []:
        resolved = _signal_window(s, defs)
        if resolved is None:
            continue
        ws, we, ramp, full = resolved
        label = f"{s.get('signal_type')} {ws.isoformat()}..{we.isoformat()}"
        if ws <= today <= we:
            b = full
        elif ramp and (ws - timedelta(days=ramp)) <= today < ws:
            frac = 1.0 - (ws - today).days / float(ramp)
            b = 1.0 + (full - 1.0) * max(0.0, min(1.0, frac))
        else:
            continue
        active.append(label)
        if b > best:
            best, best_label = b, label
    return {"boost": _clamp_boost(best), "window": best_label, "active": active}


def timing_boost(entity, timing_signals, today=None, timing_defs=None):
    """FROZEN: receptiveness-window multiplier, bounded [1.0, 2.0]."""
    return timing_detail(entity, timing_signals, today=today,
                         timing_defs=timing_defs)["boost"]


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        today = date.today()
        # policy effective ~350d ago -> inside effective+335..+395 window
        in_window = [{"signal_type": "insurance_renewal",
                      "signal_date": (today - timedelta(days=350)).isoformat(),
                      "attrs": {}}]
        b = timing_boost({}, in_window, today)
        assert abs(b - 1.8) < 1e-9, b
        # effective 100d ago -> window opens in ~235d -> no boost
        far = [{"signal_type": "insurance_renewal",
                "signal_date": (today - timedelta(days=100)).isoformat(), "attrs": {}}]
        assert timing_boost({}, far, today) == 1.0
        # explicit attrs window + absurd boost stays clamped at 2.0
        explicit = [{"signal_type": "eviction_spike_window",
                     "signal_date": today.isoformat(),
                     "attrs": {"window_start": (today - timedelta(days=5)).isoformat(),
                               "window_end": (today + timedelta(days=5)).isoformat(),
                               "boost": 9.9}}]
        assert timing_boost({}, explicit, today) == 2.0
        # no timing signals -> exactly 1.0
        assert timing_boost({}, [], today) == 1.0
        d = timing_detail({}, in_window, today)
        assert d["window"].startswith("insurance_renewal ")
        print(f"timing self-test PASS (renewal boost={b}, window={d['window']})")
