"""Ability-to-pay (solvency) scoring — Intent Engine v2.

FROZEN INTERFACE:
    score_ability_to_pay(entity, pay_signals, distress_signals=None, as_of=None)
        -> (ability: float 0..1, sources_used: list[str], pay_data: "ok"|"partial"|"unknown")
    deal_size_proxy(entity, pay_signals, as_of=None)
        -> (deal_size: float 0..1, known: bool, sources: list[str])

Model (all factors explicit and bounded 0..1):
    SIZE   = max over size_* pay signals (staleness-blended) and entity-attr
             fallbacks (SIZE_ATTR_NORMALIZERS below). None when no size data.
    CREDIT = max over credit_* pay signals (staleness-blended). None when absent.
    base   = both present:  0.5 + (0.5*SIZE + 0.5*CREDIT - 0.5) * 0.9   -> pay_data="ok"
             one present:   0.5 + (component - 0.5) * 0.6               -> pay_data="partial"
             none:          0.5                                         -> pay_data="unknown"
    DISTRESS-DENSITY GUARDRAIL (uses the entity's pain/distress signals):
        n_eff = sum(0.5 + 0.5*magnitude) over distress signals <= 180 days old
        penalty = 1.0                         if n_eff <= 3   (few wounds = still solvent)
                = linear 1.0 -> 0.35          for 3 < n_eff < 8
                = 0.35                        if n_eff >= 8   (stacked severe = dying)
        A sizable company is shielded: if SIZE known and >= 0.4,
            penalty = penalty + (1 - penalty) * 0.5 * SIZE
    ability = clamp01(base * penalty)

    MISSING pay data => ability stays 0.5 (neutral) with pay_data="unknown"
    (guardrail may still lower it when the entity is drowning in distress —
    that IS data we have). Rows are NEVER dropped for missing pay data.

Staleness: a pay signal's value is blended toward neutral 0.5 with confidence
    conf = 0.5 ** (age_days / 730)      (2-year half-life)
Pay signals older than PAY_MAX_AGE_DAYS (1095) are ignored upstream.

COLLECTOR ATTACHMENT CONTRACT (Phase 1):
  - Pay signals are ordinary v1 Signal objects emitted via store.add_signal().
    signal_type MUST start with "size_" or "credit_" and be registered under
    top-level "solvency_signals" in signal_registry.json.
    magnitude MUST already be normalized 0..1 using the formulas below
    (SIZE_ATTR_NORMALIZERS for size sources, sba_credit_bucket for SBA,
    UCC_PRESENCE_CREDIT for a GA UCC-1 hit).
  - Collectors SHOULD also stamp raw size attrs on the entity via
    store.upsert_entity(..., attrs={...}) using keys in SIZE_ATTR_NORMALIZERS
    (power_units, mcs150_mileage, parcel_count, permit_count_12m, employees,
    asking_price) so size is derivable even without a dedicated pay signal.
"""
import json
import math
from datetime import date

NEUTRAL = 0.5
PAY_MAX_AGE_DAYS = 4380            # ~12y: solvency is a slow-changing trait, not a fresh wound;
                                  # a business that borrowed years ago is still a real bankable operation
STALENESS_HALF_LIFE_DAYS = 1825.0  # ~5y half-life: solvency decays far slower than pain

# guardrail
HEALTHY_DISTRESS_N = 3.0
DYING_DISTRESS_N = 8.0
DYING_FLOOR = 0.35
DISTRESS_MAX_AGE_DAYS = 180
SIZE_SHIELD_MIN = 0.4

UCC_PRESENCE_CREDIT = 0.6          # GA UCC-1 on file = a lender underwrote them


def _clamp01(x):
    try:
        return max(0.0, min(1.0, float(x)))
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# explicit 0..1 size normalizations (per avenue's raw size attribute)
# ---------------------------------------------------------------------------
SIZE_ATTR_NORMALIZERS = {
    # trucking: 500 power units -> 1.0 (log scale)
    "power_units": lambda v: _clamp01(math.log10(max(float(v), 0.0) + 1.0) / math.log10(501.0)),
    # trucking: 10M annual miles -> 1.0 (log scale; best revenue proxy)
    "mcs150_mileage": lambda v: _clamp01(math.log10(max(float(v), 0.0) + 1.0) / 7.0),
    # property: 200 parcels owned -> 1.0 (log scale, HCAD real_acct owner index)
    "parcel_count": lambda v: _clamp01(math.log10(max(float(v), 0.0) + 1.0) / math.log10(201.0)),
    # contractors: 50 permits in trailing 12mo -> 1.0 (linear)
    "permit_count_12m": lambda v: _clamp01(float(v) / 50.0),
    # manufacturing: 500 employees -> 1.0 (log scale, OSHA Nr Employees)
    "employees": lambda v: _clamp01(math.log10(max(float(v), 0.0) + 1.0) / math.log10(501.0)),
    # dead_listings: $100K -> 0.0, $10M -> 1.0 (log scale on asking price)
    "asking_price": lambda v: _clamp01((math.log10(max(float(v), 1.0)) - 5.0) / 2.0),
}


def sba_credit_bucket(gross_approval):
    """SBA GrossApproval -> 0..1 credit bucket (bigger loan = more underwriting)."""
    try:
        g = float(gross_approval)
    except (TypeError, ValueError):
        return 0.0
    if g < 50_000:
        return 0.3
    if g < 250_000:
        return 0.5
    if g < 1_000_000:
        return 0.7
    if g < 5_000_000:
        return 0.9
    return 1.0


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _parse_attrs(obj):
    """entity/signal 'attrs' may be a dict or a JSON string from SQLite."""
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, str) and obj.strip():
        try:
            parsed = json.loads(obj)
            return parsed if isinstance(parsed, dict) else {}
        except (ValueError, TypeError):
            return {}
    return {}


def _age_days(signal, as_of):
    try:
        sdate = date.fromisoformat(str(signal.get("signal_date", ""))[:10])
    except (ValueError, TypeError):
        return None
    return max(0, (as_of - sdate).days)


def _staleness_conf(age_days):
    if age_days is None:
        return 1.0
    return 0.5 ** (age_days / STALENESS_HALF_LIFE_DAYS)


def _component(pay_signals, prefix, as_of):
    """Max staleness-blended magnitude over pay signals of one kind.
    Returns (value 0..1 or None, sources list)."""
    best, sources = None, []
    for s in pay_signals or []:
        stype = str(s.get("signal_type", ""))
        if not stype.startswith(prefix):
            continue
        age = _age_days(s, as_of)
        if age is not None and age > PAY_MAX_AGE_DAYS:
            continue
        mag = _clamp01(s.get("magnitude", 0.0))
        conf = _staleness_conf(age)
        eff = NEUTRAL + (mag - NEUTRAL) * conf   # blend toward neutral with age
        sources.append(stype)
        if best is None or eff > best:
            best = eff
    return best, sorted(set(sources))


def _size_from_attrs(entity):
    """Fallback: derive size from raw entity attrs. Returns (0..1 or None, sources)."""
    attrs = _parse_attrs((entity or {}).get("attrs"))
    best, sources = None, []
    for key, norm in SIZE_ATTR_NORMALIZERS.items():
        val = attrs.get(key)
        if val in (None, "", "None"):
            continue
        try:
            v = norm(val)
        except (TypeError, ValueError):
            continue
        sources.append(f"attr:{key}")
        if best is None or v > best:
            best = v
    return best, sources


def _size_component(entity, pay_signals, as_of):
    sig_size, sig_sources = _component(pay_signals, "size_", as_of)
    attr_size, attr_sources = _size_from_attrs(entity)
    if sig_size is None and attr_size is None:
        return None, []
    if sig_size is None:
        return attr_size, attr_sources
    if attr_size is None:
        return sig_size, sig_sources
    return max(sig_size, attr_size), sorted(set(sig_sources + attr_sources))


def _distress_density_penalty(distress_signals, as_of):
    """1.0 (healthy) down to 0.35 (dying) from stacked recent distress."""
    n_eff = 0.0
    for s in distress_signals or []:
        age = _age_days(s, as_of)
        if age is None or age > DISTRESS_MAX_AGE_DAYS:
            continue
        n_eff += 0.5 + 0.5 * _clamp01(s.get("magnitude", 0.0))
    if n_eff <= HEALTHY_DISTRESS_N:
        return 1.0
    if n_eff >= DYING_DISTRESS_N:
        return DYING_FLOOR
    frac = (n_eff - HEALTHY_DISTRESS_N) / (DYING_DISTRESS_N - HEALTHY_DISTRESS_N)
    return 1.0 - frac * (1.0 - DYING_FLOOR)


# ---------------------------------------------------------------------------
# frozen API
# ---------------------------------------------------------------------------

def score_ability_to_pay(entity, pay_signals, distress_signals=None, as_of=None):
    """Combine SIZE + CREDIT + distress-density guardrail into ability-to-pay.

    entity: entity dict (from store.get_entity; 'attrs' may be JSON string).
    pay_signals: signal dicts whose signal_type starts with size_/credit_.
    distress_signals: the entity's pain signals (for the density guardrail).

    Returns (ability 0..1, sources_used list[str], pay_data "ok"|"partial"|"unknown").
    MISSING pay data => (0.5, [...], "unknown") — never drop the row upstream.
    """
    if as_of is None:
        as_of = date.today()
    size, size_sources = _size_component(entity, pay_signals, as_of)
    credit, credit_sources = _component(pay_signals, "credit_", as_of)
    sources = list(size_sources) + list(credit_sources)

    if size is None and credit is None:
        base, pay_data = NEUTRAL, "unknown"
    elif size is not None and credit is not None:
        raw = 0.5 * size + 0.5 * credit
        base = NEUTRAL + (raw - NEUTRAL) * 0.9
        pay_data = "ok"
    else:
        raw = size if size is not None else credit
        base = NEUTRAL + (raw - NEUTRAL) * 0.6
        pay_data = "partial"

    penalty = _distress_density_penalty(distress_signals, as_of)
    if penalty < 1.0:
        if size is not None and size >= SIZE_SHIELD_MIN:
            penalty = penalty + (1.0 - penalty) * 0.5 * size
        sources.append("distress_density")

    return _clamp01(base * penalty), sources, pay_data


def deal_size_proxy(entity, pay_signals, as_of=None):
    """DEAL_SIZE 0..1 from the SIZE component only (bigger operator = bigger deal).

    Returns (deal_size, known, sources). Unknown size => (0.5, False, []) so the
    EV deal-size factor stays neutral-midpoint instead of punishing missing data.
    """
    if as_of is None:
        as_of = date.today()
    size, sources = _size_component(entity, pay_signals, as_of)
    if size is None:
        return NEUTRAL, False, []
    return size, True, sources


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        today = date.today()
        big = {"attrs": {"power_units": 120, "mcs150_mileage": 4_000_000}}
        # missing everything -> exactly neutral
        a, src, flag = score_ability_to_pay({}, [], [])
        assert (a, flag) == (0.5, "unknown"), (a, flag)
        # sizable + credit + few wounds -> well above neutral
        pay = [{"signal_type": "credit_sba_loan", "magnitude": sba_credit_bucket(600_000),
                "signal_date": today.isoformat()}]
        pain = [{"signal_type": "lien_filed", "magnitude": 1.0,
                 "signal_date": today.isoformat()}]
        b, src, flag = score_ability_to_pay(big, pay, pain)
        assert b > 0.6 and flag == "ok", (b, flag)
        # drowning tiny company -> low
        many = pain * 12
        c, src, flag = score_ability_to_pay(
            {}, [{"signal_type": "size_fleet", "magnitude": 0.1,
                  "signal_date": today.isoformat()}], many)
        assert c < 0.2 and flag == "partial", (c, flag)
        ds, known, _ = deal_size_proxy(big, [])
        assert known and 0.0 <= ds <= 1.0
        print("solvency self-test PASS "
              f"(neutral={a:.2f} solvent={b:.2f} dying={c:.2f} deal_size={ds:.2f})")
