"""FMCSA trucking collector — Houston + Atlanta carrier distress signals.

Ported from the proven _reference/fmcsa_bleed.py + fmcsa_rank.py aggregation logic.

Socrata datasets on data.transportation.gov:
    az4n-8mr2   FMCSA census (carrier identity, fleet size, contact)
    rbkj-cgst   SMS inspections (trailing 24-month window)
    4wxs-vbns   SMS crashes (trailing 24-month window)
    6sqe-dvqs   L&I "InsHist - All With History"  (insurance cancellations)
    qh9u-swkp   L&I "ActPendInsur - All With History" (pending cancellations)

NOTE on jeyh-5nsj: the task pointed at Socrata id jeyh-5nsj for L&I insurance.
Verified 2026-07-05: jeyh-5nsj is an `href` link asset (assetType=href pointing
at http://li.fmcsa.dot.gov/) with NO tabular rows — /resource/jeyh-5nsj.json
returns 403. The actual tabular L&I data it links to lives in 6sqe-dvqs
(InsHist) and qh9u-swkp (ActPendInsur), which are used here instead.
L&I datasets key dot_number as an 8-digit zero-padded string ("00264184");
census/SMS use unpadded ("264184").

Signals emitted (avenue "trucking"):
    oos_rate_high          magnitude = clamp((veh_oos_rate - 0.207) / 0.5, 0, 1)
                           requires >= 5 vehicle-relevant inspections
    recent_crash           one per crash with report_date in the last 60 days
    bleed_score            fmcsa_rank.py refined score, normalized /300, clamped;
                           requires >= 10 inspections in the SMS window
    insurance_cancellation magnitude 1.0 — InsHist row with mod_col_1='Cancelled'
                           or ActPendInsur row carrying a cancl_effective_date
                           (pending cancellation), within the date window

oos_rate_high / bleed_score are aggregate observations: they are snapshot-gated
(only emitted when the underlying SMS aggregates changed since the previous
snapshot, or on first sight) so repeated runs do not re-emit unchanged data.

source_ref for every signal is the FMCSA SAFER company-snapshot URL for the DOT.

Self-test (writes NOTHING to the sheet, uses an in-memory store):
    python -m collectors.trucking_fmcsa --self-test [--cap N] [--metro houston|atlanta]
"""
import json
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

_ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from common.http import soda                                   # noqa: E402
from common.normalize import clean_zip                         # noqa: E402

# ---- datasets -------------------------------------------------------------
DS_CENSUS = "az4n-8mr2"
DS_INSPECTIONS = "rbkj-cgst"
DS_CRASHES = "4wxs-vbns"
DS_INSHIST = "6sqe-dvqs"     # L&I insurance history (cancellations)
DS_ACTPEND = "qh9u-swkp"     # L&I active/pending insurance (pending cancels)

# ---- ported scoring constants (from _reference/fmcsa_bleed.py / fmcsa_rank.py)
NATL_V_OOS = 0.207           # national avg vehicle OOS rate
NATL_D_OOS = 0.059           # national avg driver OOS rate
MIN_INSP_FOR_BLEED = 10      # fmcsa_rank: too little signal to rank below this
MIN_VEH_INSP_FOR_OOS = 5     # fmcsa_bleed: min sample for an OOS-rate claim
BLEED_NORM = 300.0           # raw bleed score that maps to magnitude 1.0

# ---- collection parameters ------------------------------------------------
MIN_POWER_UNITS = 5          # skip owner-operators; ICP is real fleets
CRASH_WINDOW_DAYS = 60       # "recent_crash" = crash in the last 60 days
PENDING_CANCEL_HORIZON_DAYS = 120   # ignore junk far-future cancel dates
DOT_BATCH = 100              # DOTs per Socrata in-list query
CENSUS_PAGE = 2000

CENSUS_SELECT = (
    "dot_number, legal_name, dba_name, phy_street, phy_city, phy_state, phy_zip, "
    "phy_cnty, phone, email_address, power_units, truck_units, bus_units, "
    "total_drivers, mcs150_mileage, mcs150_mileage_year, carrier_operation, "
    "status_code, docket1prefix, docket1"
)

INSP_AGG_SELECT = (
    "dot_number, count(*) as n_insp,"
    "sum(vehicle_oos_total::number) as v_oos,"
    "sum(driver_oos_total::number) as d_oos,"
    "sum(oos_total::number) as t_oos,"
    "sum(case(insp_level_id in ('1','2','5','6'), 1, true, 0)) as veh_insp,"
    "sum(case(insp_level_id in ('1','2','3','6'), 1, true, 0)) as drv_insp,"
    "sum(case(unsafe_insp='true', 1, true, 0)) as unsafe,"
    "sum(case(fatigued_insp='true', 1, true, 0)) as fatigued"
)

CRASH_SELECT = ("dot_number, report_number, report_date, report_state, "
                "fatalities, injuries, tow_away")


def safer_url(dot):
    """FMCSA SAFER company-snapshot URL for a DOT number (used as source_ref)."""
    return ("https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY"
            f"&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={dot}")


def _clamp01(x):
    return max(0.0, min(1.0, x))


def _num(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _parse_date(s):
    """Parse the two date formats these datasets use:
    SMS: '17-JUL-25' -> date; L&I: '09/23/2004' -> date. Returns None on failure.
    """
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%d-%b-%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def _minimal_prefixes(prefixes):
    """Drop zip prefixes already covered by a shorter one (['77','770'] -> ['77'])."""
    out = []
    for p in sorted(prefixes, key=len):
        if not any(p.startswith(q) for q in out):
            out.append(p)
    return out


class Collector(BaseCollector):
    avenue = "trucking"
    source_id = "trucking_fmcsa"
    metros = ("houston", "atlanta")

    def __init__(self, carrier_cap=None):
        # carrier_cap limits carriers fetched per metro (used by --self-test)
        self.carrier_cap = carrier_cap
        self._fixture = {}          # raw sample payloads captured for --self-test

    # ------------------------------------------------------------------ #
    #  fetch helpers                                                     #
    # ------------------------------------------------------------------ #

    def _fetch_census(self, metro, metro_cfg):
        """Active non-bus carriers domiciled in the metro (state + zip prefixes)."""
        state = metro_cfg["state"]
        prefixes = _minimal_prefixes(metro_cfg.get("zip_prefixes", []))
        zip_clause = " OR ".join(f"starts_with(phy_zip,'{p}')" for p in prefixes)
        where = (f"phy_state='{state}' AND ({zip_clause}) AND status_code='A' "
                 f"AND power_units::number >= {MIN_POWER_UNITS} "
                 f"AND bus_units::number = 0")
        carriers, offset = [], 0
        while True:
            limit = CENSUS_PAGE
            if self.carrier_cap is not None:
                limit = min(limit, self.carrier_cap - len(carriers))
                if limit <= 0:
                    break
            rows = soda(DS_CENSUS, {
                "$select": CENSUS_SELECT, "$where": where,
                "$order": "dot_number", "$limit": str(limit), "$offset": str(offset),
            })
            carriers.extend(rows)
            if rows and "census" not in self._fixture:
                self._fixture["census"] = rows[0]
            if len(rows) < limit:
                break
            offset += len(rows)
        return carriers

    def _fetch_inspection_aggs(self, dots):
        """Per-DOT SMS inspection aggregates (24-month window) — ported query."""
        aggs = {}
        for batch in _batched(dots, DOT_BATCH):
            inlist = ",".join(f"'{d}'" for d in batch)
            rows = soda(DS_INSPECTIONS, {
                "$select": INSP_AGG_SELECT,
                "$where": f"dot_number in ({inlist})",
                "$group": "dot_number", "$limit": str(DOT_BATCH * 2),
            })
            for r in rows:
                aggs[r["dot_number"]] = r
            if rows and "inspection_agg" not in self._fixture:
                self._fixture["inspection_agg"] = rows[0]
        return aggs

    def _fetch_crashes(self, dots):
        """Per-DOT crash rows (24-month SMS window); aggregated client-side."""
        crashes = {}
        for batch in _batched(dots, DOT_BATCH):
            inlist = ",".join(f"'{d}'" for d in batch)
            rows = soda(DS_CRASHES, {
                "$select": CRASH_SELECT,
                "$where": f"dot_number in ({inlist})",
                "$limit": "50000",
            })
            for r in rows:
                crashes.setdefault(r["dot_number"], []).append(r)
            if rows and "crash" not in self._fixture:
                self._fixture["crash"] = rows[0]
        return crashes

    def _fetch_insurance(self, dots):
        """L&I cancelled + pending-cancel insurance rows, keyed by unpadded DOT.

        L&I datasets zero-pad dot_number to 8 digits; census/SMS do not.
        """
        padded = {str(d).zfill(8): str(d) for d in dots}
        cancelled, pending = {}, {}
        for batch in _batched(sorted(padded), DOT_BATCH):
            inlist = ",".join(f"'{p}'" for p in batch)
            hist = soda(DS_INSHIST, {
                "$where": f"dot_number in ({inlist}) AND mod_col_1='Cancelled'",
                "$limit": "50000",
            })
            for r in hist:
                cancelled.setdefault(padded.get(r.get("dot_number", "")), []).append(r)
            if hist and "inshist_cancelled" not in self._fixture:
                self._fixture["inshist_cancelled"] = hist[0]

            act = soda(DS_ACTPEND, {
                "$where": f"dot_number in ({inlist}) AND cancl_effective_date IS NOT NULL",
                "$limit": "50000",
            })
            for r in act:
                pending.setdefault(padded.get(r.get("dot_number", "")), []).append(r)
            if act and "actpend_pending" not in self._fixture:
                self._fixture["actpend_pending"] = act[0]
        cancelled.pop(None, None)
        pending.pop(None, None)
        return cancelled, pending

    # ------------------------------------------------------------------ #
    #  scoring (ported from _reference/fmcsa_rank.py)                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _metrics(carrier, insp_agg, crash_rows):
        pu = _num(carrier.get("power_units"))
        i = insp_agg or {}
        n_insp = _num(i.get("n_insp"))
        veh_insp = _num(i.get("veh_insp"))
        drv_insp = _num(i.get("drv_insp"))
        v_oos = _num(i.get("v_oos"))
        d_oos = _num(i.get("d_oos"))
        unsafe = _num(i.get("unsafe"))
        fatigued = _num(i.get("fatigued"))
        n_crash = len(crash_rows or [])
        v_rate = v_oos / veh_insp if veh_insp else None
        d_rate = d_oos / drv_insp if drv_insp else None

        # refined bleed score — fmcsa_rank.py, verbatim math
        bleed = None
        if n_insp >= MIN_INSP_FOR_BLEED:
            v_ex = max(0.0, (v_rate or 0) - NATL_V_OOS)
            d_ex = max(0.0, (d_rate or 0) - NATL_D_OOS)
            unsafe_rate = unsafe / n_insp
            fatig_rate = fatigued / n_insp
            crash_pu = n_crash / pu if pu else 0
            bleed = (v_ex * 100 * math.sqrt(min(veh_insp, 200))
                     + d_ex * 160 * math.sqrt(min(drv_insp, 200))
                     + crash_pu * 400
                     + unsafe_rate * 60 + fatig_rate * 60)
        return {
            "power_units": pu, "n_insp": n_insp,
            "veh_insp": veh_insp, "drv_insp": drv_insp,
            "v_oos": v_oos, "d_oos": d_oos,
            "unsafe": unsafe, "fatigued": fatigued, "n_crash": n_crash,
            "veh_oos_rate": round(v_rate, 4) if v_rate is not None else None,
            "drv_oos_rate": round(d_rate, 4) if d_rate is not None else None,
            "bleed_score": round(bleed, 2) if bleed is not None else None,
        }

    # ------------------------------------------------------------------ #
    #  collect                                                           #
    # ------------------------------------------------------------------ #

    def collect(self, since, store, registry):
        today = date.today()
        crash_cutoff = today - timedelta(days=CRASH_WINDOW_DAYS)
        ins_cutoff = min(since, today - timedelta(days=CRASH_WINDOW_DAYS))
        ins_horizon = today + timedelta(days=PENDING_CANCEL_HORIZON_DAYS)
        signals_added = 0
        entities_seen = 0
        warnings = []

        try:
            metros_cfg = registry.get("metros", {})
            for metro in self.metros:
                metro_cfg = metros_cfg.get(metro)
                if not metro_cfg:
                    warnings.append(f"{metro}: missing from registry metros")
                    continue
                try:
                    carriers = self._fetch_census(metro, metro_cfg)
                except Exception as exc:
                    warnings.append(f"{metro}: census fetch failed: {exc!r:.300}")
                    continue
                entities_seen += len(carriers)
                if not carriers:
                    continue
                dots = [str(int(c["dot_number"])) for c in carriers
                        if str(c.get("dot_number", "")).strip().isdigit()]

                insp_aggs, crash_rows_by_dot = {}, {}
                cancelled_by_dot, pending_by_dot = {}, {}
                try:
                    insp_aggs = self._fetch_inspection_aggs(dots)
                except Exception as exc:
                    warnings.append(f"{metro}: inspections fetch failed: {exc!r:.300}")
                try:
                    crash_rows_by_dot = self._fetch_crashes(dots)
                except Exception as exc:
                    warnings.append(f"{metro}: crashes fetch failed: {exc!r:.300}")
                try:
                    cancelled_by_dot, pending_by_dot = self._fetch_insurance(dots)
                except Exception as exc:
                    warnings.append(f"{metro}: L&I insurance fetch failed: {exc!r:.300}")

                for carrier in carriers:
                    raw_dot = str(carrier.get("dot_number", "")).strip()
                    if not raw_dot.isdigit():
                        continue
                    dot = str(int(raw_dot))
                    signals_added += self._emit_for_carrier(
                        store, metro, today, dot, carrier,
                        insp_aggs.get(dot),
                        crash_rows_by_dot.get(dot, []),
                        cancelled_by_dot.get(dot, []),
                        pending_by_dot.get(dot, []),
                        crash_cutoff, ins_cutoff, ins_horizon,
                    )
        except Exception as exc:
            return CollectorResult(
                source_id=self.source_id, signals_added=signals_added,
                entities_seen=entities_seen, status="ERROR",
                error=f"{exc!r:.500}",
            )

        error = "; ".join(warnings)
        if entities_seen == 0 and warnings:
            status = "ERROR"
        elif signals_added == 0:
            status = "EMPTY"
        else:
            status = "OK"
        return CollectorResult(
            source_id=self.source_id, signals_added=signals_added,
            entities_seen=entities_seen, status=status, error=error,
        )

    # ------------------------------------------------------------------ #
    #  per-carrier signal emission                                       #
    # ------------------------------------------------------------------ #

    def _emit_for_carrier(self, store, metro, today, dot, carrier, insp_agg,
                          crash_rows, cancelled_rows, pending_rows,
                          crash_cutoff, ins_cutoff, ins_horizon):
        added = 0
        entity_key = f"dot:{dot}"
        name = carrier.get("legal_name") or carrier.get("dba_name") or f"DOT {dot}"
        ref = safer_url(dot)
        attrs = {
            "phone": carrier.get("phone") or None,
            "email": carrier.get("email_address") or None,
            "street": carrier.get("phy_street") or None,
            "zip": clean_zip(carrier.get("phy_zip")) or None,
            "city": carrier.get("phy_city") or None,
            "dba": carrier.get("dba_name") or None,
            "power_units": _num(carrier.get("power_units")),
            "drivers": _num(carrier.get("total_drivers")),
        }
        m = self._metrics(carrier, insp_agg, crash_rows)

        def emit(signal_type, signal_date, magnitude, raw):
            nonlocal added
            sig = Signal(
                entity_key=entity_key, entity_name=name, metro=metro,
                avenue=self.avenue, signal_type=signal_type,
                signal_date=signal_date, magnitude=round(_clamp01(magnitude), 4),
                source_id=self.source_id, source_ref=ref, raw=raw, attrs=attrs,
            )
            if store.add_signal(sig):
                added += 1

        # --- snapshot + change gate for the aggregate signals ---
        changed = True
        if m["n_insp"] > 0 or m["n_crash"] > 0:
            gate_keys = ("n_insp", "veh_insp", "drv_insp", "v_oos", "d_oos",
                         "n_crash", "bleed_score")
            snaps = store.get_snapshots(self.source_id, entity_key)
            prev = None
            for s in snaps:
                if s["snapshot_date"] < today.isoformat():
                    prev = s["payload"]
            if isinstance(prev, dict):
                changed = any(prev.get(k) != m[k] for k in gate_keys)
            store.add_snapshot(self.source_id, today.isoformat(), entity_key, m)

        # --- oos_rate_high: clamp((veh_oos_rate - 0.207) / 0.5, 0, 1) ---
        if (changed and m["veh_oos_rate"] is not None
                and m["veh_insp"] >= MIN_VEH_INSP_FOR_OOS):
            mag = _clamp01((m["veh_oos_rate"] - NATL_V_OOS) / 0.5)
            if mag > 0:
                emit("oos_rate_high", today.isoformat(), mag,
                     {"metrics": m, "carrier": carrier})

        # --- bleed_score: fmcsa_rank score normalized /BLEED_NORM ---
        if changed and m["bleed_score"] is not None and m["bleed_score"] > 0:
            emit("bleed_score", today.isoformat(),
                 m["bleed_score"] / BLEED_NORM,
                 {"metrics": m, "carrier": carrier})

        # --- recent_crash: one per crash in the last CRASH_WINDOW_DAYS ---
        for cr in crash_rows:
            d = _parse_date(cr.get("report_date"))
            if d is None or d < crash_cutoff or d > today:
                continue
            fatal = _num(cr.get("fatalities"))
            inj = _num(cr.get("injuries"))
            tow = str(cr.get("tow_away", "")).lower() == "true"
            mag = 1.0 if fatal > 0 else 0.7 if inj > 0 else 0.55 if tow else 0.4
            emit("recent_crash", d.isoformat(), mag, cr)

        # --- insurance_cancellation: magnitude 1.0 ---
        for row in cancelled_rows:                      # InsHist 'Cancelled'
            d = _parse_date(row.get("cancl_effective_date"))
            if d is None or d < ins_cutoff or d > ins_horizon:
                continue
            sig_date = min(d, today)
            emit("insurance_cancellation", sig_date.isoformat(), 1.0,
                 {"li_dataset": DS_INSHIST, "kind": "cancelled", **row})
        for row in pending_rows:                        # ActPendInsur pending
            d = _parse_date(row.get("cancl_effective_date"))
            if d is None or d < ins_cutoff or d > ins_horizon:
                continue
            sig_date = min(d, today)
            emit("insurance_cancellation", sig_date.isoformat(), 1.0,
                 {"li_dataset": DS_ACTPEND, "kind": "pending_cancel", **row})

        return added


# ---------------------------------------------------------------------- #
#  self-test                                                             #
# ---------------------------------------------------------------------- #

def _self_test(cap, metro):
    """Collect the last 30 days into an in-memory store. No sheet, no real DB."""
    import config
    from common.store import Store

    registry = config.load_registry()
    store = Store(db_path=":memory:")
    collector = Collector(carrier_cap=cap)
    if metro:
        collector.metros = (metro,)
    since = date.today() - timedelta(days=30)

    print(f"[self-test] trucking_fmcsa  since={since}  metros={collector.metros}  "
          f"carrier cap={cap}/metro")
    result = collector.collect(since, store, registry)

    print(f"status:        {result.status}")
    print(f"entities_seen: {result.entities_seen}")
    print(f"signals_added: {result.signals_added}")
    if result.error:
        print(f"error/warn:    {result.error}")

    by_type = {}
    for s in store.get_signals(avenue="trucking"):
        by_type[s["signal_type"]] = by_type.get(s["signal_type"], 0) + 1
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")

    fixture_path = _ENGINE_ROOT / "fixtures" / f"{collector.source_id}_sample.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    sample_signals = store.get_signals(avenue="trucking")[:3]
    with open(fixture_path, "w", encoding="utf-8") as f:
        json.dump({"raw_samples": collector._fixture,
                   "example_signals": sample_signals}, f, indent=1, default=str)
    print(f"fixture saved: {fixture_path}")
    store.close()
    return result


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="FMCSA trucking collector")
    ap.add_argument("--self-test", action="store_true",
                    help="last 30 days into a throwaway store; writes fixture only")
    ap.add_argument("--cap", type=int, default=120,
                    help="self-test: max carriers per metro (default 120)")
    ap.add_argument("--metro", choices=("houston", "atlanta"), default=None,
                    help="self-test: restrict to one metro")
    args = ap.parse_args()
    if args.self_test:
        res = _self_test(args.cap, args.metro)
        sys.exit(0 if res.status in ("OK", "EMPTY") else 1)
    else:
        ap.print_help()
        sys.exit(0)
