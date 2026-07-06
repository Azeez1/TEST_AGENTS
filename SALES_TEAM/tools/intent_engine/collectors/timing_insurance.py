"""timing_insurance — trucking insurance-renewal receptiveness windows (v2 TIMING).

Avenue:    trucking   | Metros: houston, atlanta
Source id: timing_insurance
Emits:     insurance_renewal   (registered under registry "timing_signals")

SPIKE RESULT (2026-07-06, 12 real hot Houston/Atlanta DOTs + 150 random census DOTs):
  * LIVIEW scrape (li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist)
    is BLOCKED for programmatic use: the carrier-search form is reCAPTCHA-gated
    (hidden input g_recaptcha_response). GET and POST without a captcha token
    both re-render the empty search form (~17.5 KB, zero result links), and
    Bright Data Web Unlocker returned empty bodies for this Oracle PL/SQL app.
    Detail pages need a pv_apcant_id that only the captcha'd search reveals.
    DO NOT scrape LIVIEW.
  * The SAME L&I insurance data is SoQL-queryable on data.transportation.gov
    dataset qh9u-swkp ("ActPendInsur — All With History"): columns
    effective_date, cancl_effective_date, policy_no, name_company,
    ins_form_code, mod_col_1. Measured coverage: 12/12 hot DOTs had an
    effective_date; 81/150 random census carriers (~54%) have an ACTIVE filing
    (no cancellation date) with an effective_date; median active-filing age
    308 days (annual refresh is the norm, validating the anniversary proxy).
    One batched in-list query covers 100 DOTs in ~1s.
  => This collector uses the SoQL path: free, no captcha, no paywall, batched.
     Carriers not present in qh9u-swkp simply get no timing signal (timing
     stays exactly 1.0 for them — the frozen timing.py default).

Renewal model (the plan's "insurance renewal ~= policy effective + 12mo"):
  Federal L&I filings persist for years (a filing effective 01/01/2008 can
  still be active), but commercial auto/BIPD policies renew at the ANNIVERSARY
  of the effective date. Anchor = the latest ACTIVE filing's effective date,
  projected to its most recent calendar anniversary (<= today).
  Receptiveness window (from registry timing_signals.insurance_renewal:
  offset_days=335, window_days=60) = [anniversary - 30d, anniversary + 30d].
  A signal is emitted only when that window is open now or opens within
  EMIT_HORIZON_DAYS (60) — i.e. "their renewal falls in the next ~60 days".

Signal mechanics (frozen v2 collector-attachment contract):
  entity_key   dot:{dot} (same key trucking_fmcsa uses -> exact 1.0 resolve)
  signal_date  most recent calendar anniversary of the effective date
               (always 0..365 days old -> passes the orchestrator's
               -400..TIMING_MAX_AGE_DAYS window filter)
  attrs        explicit window_start / window_end ISO dates (timing.py
               prefers these over the offset math), plus contact fields and
               the SIZE-ATTR fallbacks power_units / mcs150_mileage from the
               census row (feeds common/solvency.py deal-size/ability).
  source_ref   the carrier's live qh9u-swkp API URL (clickable evidence that
               returns the policy rows incl. the effective date).
  dedup        signal_date changes once per policy-year and source_ref is
               stable per DOT, so re-runs are naturally idempotent.

`since` is ignored (renewal windows are forward-looking, derived from the
current active filing, not from recent events).

Runtime note: full production run re-pulls the metro census (2-3 pages/metro,
reusing collectors/trucking_fmcsa.py's pinned query) then ~1 L&I query per 100
DOTs — roughly 35 throttled requests / ~2 minutes for both metros.

Self-test (in-memory store, live queries, NOTHING written to sheet/real DB):
    python -m collectors.timing_insurance --self-test [--cap N] [--metro M]
saves fixtures/timing_insurance_sample.json.
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

_ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors.trucking_fmcsa import Collector as _CensusFetcher  # noqa: E402
from collectors.trucking_fmcsa import _num  # noqa: E402
from common.http import soda  # noqa: E402
from common.normalize import clean_zip  # noqa: E402
from common.timing import DEFAULT_TIMING_DEFS  # noqa: E402

DS_ACTPEND = "qh9u-swkp"          # L&I "ActPendInsur - All With History" (SoQL)
DOT_BATCH = 100                   # DOTs per in-list query (matches trucking_fmcsa)
EMIT_HORIZON_DAYS = 60            # emit when the window opens within this many days

ACTPEND_SELECT = ("dot_number, docket_number, ins_form_code, mod_col_1, "
                  "name_company, policy_no, effective_date, "
                  "cancl_effective_date, max_cov_amount")


def evidence_url(padded_dot):
    """Live L&I API URL for one carrier — returns its policy rows as JSON."""
    return (f"https://data.transportation.gov/resource/{DS_ACTPEND}.json"
            f"?dot_number={padded_dot}")


def _parse_li_date(s):
    """L&I dates are MM/DD/YYYY. Returns date or None."""
    try:
        return datetime.strptime(str(s).strip(), "%m/%d/%Y").date()
    except (TypeError, ValueError):
        return None


def _clamped_date(year, month, day):
    """date(year, month, day) with day clamped for short months / Feb 29."""
    while day > 28:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1
    return date(year, month, day)


def _anniversaries(effective, today):
    """(last_anniversary <= today, next_anniversary > today) of an effective
    date, on the real calendar. Returns None for future effective dates
    (policy not yet in force; its first renewal is ~a year out, never inside
    the emit horizon)."""
    if effective > today:
        return None
    cand = _clamped_date(today.year, effective.month, effective.day)
    if cand > today:
        return (_clamped_date(today.year - 1, effective.month, effective.day),
                cand)
    return (cand,
            _clamped_date(today.year + 1, effective.month, effective.day))


def renewal_window(effective, today, timing_def):
    """Resolve one active filing to its emit-worthy receptiveness window.

    Returns (anchor_anniversary, window_start, window_end) or None when the
    carrier's renewal window is neither open nor opening within
    EMIT_HORIZON_DAYS.
    """
    lead = 365 - int(timing_def.get("offset_days", 335))     # days before anniv
    span = int(timing_def.get("window_days", 60))
    annivs = _anniversaries(effective, today)
    if annivs is None:
        return None
    last_anniv, next_anniv = annivs
    for anniv in (last_anniv, next_anniv):
        ws = anniv - timedelta(days=lead)
        we = ws + timedelta(days=span)
        if we < today:                       # window already closed
            continue
        if ws > today + timedelta(days=EMIT_HORIZON_DAYS):   # too far out
            continue
        return last_anniv, ws, we
    return None


class Collector(BaseCollector):
    avenue = "trucking"
    source_id = "timing_insurance"
    metros = ("houston", "atlanta")

    def __init__(self, carrier_cap=None):
        # carrier_cap limits census carriers per metro (used by --self-test)
        self.carrier_cap = carrier_cap
        self._fixture = {}

    # ------------------------------------------------------------------ #
    #  fetch                                                             #
    # ------------------------------------------------------------------ #

    def _fetch_active_filings(self, dots):
        """Latest ACTIVE (no cancellation date) filing effective date per DOT.

        L&I zero-pads dot_number to 8 digits; census does not. Returns
        {unpadded_dot: {"effective": date, "row": raw_row}}.
        """
        padded = {str(d).zfill(8): str(d) for d in dots}
        best = {}
        keys = sorted(padded)
        for i in range(0, len(keys), DOT_BATCH):
            batch = keys[i:i + DOT_BATCH]
            inlist = ",".join(f"'{p}'" for p in batch)
            rows = soda(DS_ACTPEND, {
                "$select": ACTPEND_SELECT,
                "$where": f"dot_number in ({inlist}) "
                          "AND cancl_effective_date IS NULL "
                          "AND effective_date IS NOT NULL",
                "$limit": str(DOT_BATCH * 50),
            })
            if rows and "actpend_active" not in self._fixture:
                self._fixture["actpend_active"] = rows[0]
            for r in rows:
                dot = padded.get(r.get("dot_number", ""))
                eff = _parse_li_date(r.get("effective_date"))
                if dot is None or eff is None:
                    continue
                cur = best.get(dot)
                if cur is None or eff > cur["effective"]:
                    best[dot] = {"effective": eff, "row": r}
        return best

    # ------------------------------------------------------------------ #
    #  collect                                                           #
    # ------------------------------------------------------------------ #

    def collect(self, since, store, registry):
        today = date.today()
        timing_def = dict(DEFAULT_TIMING_DEFS.get("insurance_renewal", {}))
        timing_def.update(
            (registry.get("timing_signals") or {}).get("insurance_renewal")
            or {})
        signals_added = 0
        entities_seen = 0
        warnings = []
        try:
            census = _CensusFetcher(carrier_cap=self.carrier_cap)
            metros_cfg = registry.get("metros", {})
            for metro in self.metros:
                metro_cfg = metros_cfg.get(metro)
                if not metro_cfg:
                    warnings.append(f"{metro}: missing from registry metros")
                    continue
                try:
                    carriers = census._fetch_census(metro, metro_cfg)
                except Exception as exc:
                    warnings.append(f"{metro}: census fetch failed: {exc!r:.300}")
                    continue
                entities_seen += len(carriers)
                by_dot = {}
                for c in carriers:
                    raw_dot = str(c.get("dot_number", "")).strip()
                    if raw_dot.isdigit():
                        by_dot[str(int(raw_dot))] = c
                if not by_dot:
                    continue
                try:
                    filings = self._fetch_active_filings(list(by_dot))
                except Exception as exc:
                    warnings.append(f"{metro}: L&I query failed: {exc!r:.300}")
                    continue
                for dot, info in filings.items():
                    resolved = renewal_window(info["effective"], today,
                                              timing_def)
                    if resolved is None:
                        continue
                    anchor, ws, we = resolved
                    signals_added += self._emit(store, metro, dot,
                                                by_dot[dot], info, anchor,
                                                ws, we, today)
        except Exception as exc:  # contract: never raise
            return CollectorResult(self.source_id, signals_added,
                                   entities_seen, "ERROR",
                                   error=f"{type(exc).__name__}: {exc}")
        error = "; ".join(warnings)
        if entities_seen == 0 and warnings:
            status = "ERROR"
        elif signals_added == 0:
            status = "EMPTY"
        else:
            status = "OK"
        return CollectorResult(self.source_id, signals_added, entities_seen,
                               status, error=error)

    def _emit(self, store, metro, dot, carrier, filing, anchor, ws, we, today):
        row = filing["row"]
        padded = str(dot).zfill(8)
        name = (carrier.get("legal_name") or carrier.get("dba_name")
                or f"DOT {dot}")
        attrs = {
            "window_start": ws.isoformat(),
            "window_end": we.isoformat(),
            "phone": carrier.get("phone") or None,
            "email": carrier.get("email_address") or None,
            "street": carrier.get("phy_street") or None,
            "zip": clean_zip(carrier.get("phy_zip")) or None,
            "power_units": _num(carrier.get("power_units")),
            "mcs150_mileage": _num(carrier.get("mcs150_mileage")),
        }
        sig = Signal(
            entity_key=f"dot:{dot}",
            entity_name=name,
            metro=metro,
            avenue=self.avenue,
            signal_type="insurance_renewal",
            signal_date=anchor.isoformat(),
            magnitude=1.0,
            source_id=self.source_id,
            source_ref=evidence_url(padded),
            raw={
                "policy_effective_date": filing["effective"].isoformat(),
                "renewal_anniversary_anchor": anchor.isoformat(),
                "window": [ws.isoformat(), we.isoformat()],
                "days_until_window": max(0, (ws - today).days),
                "insurer": row.get("name_company"),
                "policy_no": row.get("policy_no"),
                "form": row.get("ins_form_code"),
                "coverage_type": row.get("mod_col_1"),
                "docket": row.get("docket_number"),
                "note": "renewal proxy = anniversary of the active L&I filing "
                        "effective date (LIVIEW scrape is reCAPTCHA-blocked; "
                        "data via SoQL qh9u-swkp)",
            },
            attrs=attrs,
        )
        return 1 if store.add_signal(sig) else 0


COLLECTOR = Collector()


# ---------------------------------------------------------------------- #
#  self-test                                                             #
# ---------------------------------------------------------------------- #

def _self_test(cap, metro):
    import config
    from common.store import Store

    registry = config.load_registry()
    store = Store(db_path=":memory:")
    col = Collector(carrier_cap=cap)
    if metro:
        col.metros = (metro,)
    since = date.today() - timedelta(days=30)

    # pure-logic assertions first (no network)
    tdef = DEFAULT_TIMING_DEFS["insurance_renewal"]
    today = date(2026, 7, 6)
    r = renewal_window(date(2024, 8, 1), today, tdef)     # anniv 2026-08-01
    assert r is not None and r[1] == date(2026, 7, 2), r  # window open soon
    assert renewal_window(date(2024, 1, 15), today, tdef) is None  # far out
    r = renewal_window(date(2025, 6, 20), today, tdef)    # anniv 16d ago
    assert r is not None and r[2] >= today, r             # window still open
    assert renewal_window(date(2026, 9, 1), today, tdef) is None  # future eff
    assert _clamped_date(2026, 2, 29) == date(2026, 2, 28)
    print("[self-test] renewal_window logic assertions PASS")

    print(f"[self-test] timing_insurance  since={since} metros={col.metros} "
          f"carrier cap={cap}/metro (live census + L&I queries)")
    result = col.collect(since, store, registry)
    print(f"status:        {result.status}")
    print(f"entities_seen: {result.entities_seen}")
    print(f"signals_added: {result.signals_added}")
    if result.error:
        print(f"error/warn:    {result.error}")

    sigs = store.get_signals(avenue="trucking")
    for s in sigs[:5]:
        a = json.loads(s["attrs"])
        print(f"  {s['entity_key']:<14} {s['entity_name'][:34]:<34} "
              f"window {a.get('window_start')}..{a.get('window_end')}")

    fixture_path = _ENGINE_ROOT / "fixtures" / f"{col.source_id}_sample.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(json.dumps({
        "spike_evidence": {
            "liview": "reCAPTCHA-gated search form (g_recaptcha_response); "
                      "direct GET/POST re-renders the form; Bright Data "
                      "unlocker returned empty bodies. BLOCKED.",
            "soql": f"{DS_ACTPEND} coverage: 12/12 hot DOTs with "
                    "effective_date; 81/150 random census DOTs with an "
                    "active filing (2026-07-06 spike).",
        },
        "raw_samples": self_fixture_or_note(col),
        "example_signals": sigs[:3],
    }, indent=1, default=str), encoding="utf-8")
    print(f"fixture saved: {fixture_path}")
    store.close()
    return result


def self_fixture_or_note(col):
    return col._fixture or {"note": "no active filings returned in window"}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="FMCSA insurance-renewal timing collector (SoQL L&I)")
    ap.add_argument("--self-test", action="store_true",
                    help="last 30 days into a throwaway store; fixture only")
    ap.add_argument("--cap", type=int, default=200,
                    help="self-test: max carriers per metro (default 200)")
    ap.add_argument("--metro", choices=("houston", "atlanta"), default=None,
                    help="self-test: restrict to one metro")
    args = ap.parse_args()
    if args.self_test:
        res = _self_test(args.cap, args.metro)
        sys.exit(0 if res.status in ("OK", "EMPTY") else 1)
    ap.print_help()
    sys.exit(0)
