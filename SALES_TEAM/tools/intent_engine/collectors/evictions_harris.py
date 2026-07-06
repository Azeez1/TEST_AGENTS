"""evictions_harris — Harris County JP eviction filings -> eviction_spike signals.

Avenue: property_mgmt | Metro: houston | Source: Harris County JP Public Data
Extract Service (https://jpwebsite.harriscountytx.gov/PublicExtracts/).

How the source works (reverse-engineered from search.jsp + scripts/requestscripts.js):
    GET https://jpwebsite.harriscountytx.gov/PublicExtracts/GetExtractData
        extractCaseType=CV      civil
        extract=7               "Cases Filed" extract
        court=300               all 16 JP courts
        casetype=8464           Eviction (forcible entry & detainer)
        format=csv              CSV output (also: tab, xml)
        fdate=MM/DD/YYYY        window start
        tdate=MM/DD/YYYY        window end
    Response: quoted CSV, header row, ~70 columns (Case Number, Case File Date,
    Plaintiff Name/Addr, Defendant Name/Addr, hearing + judgment fields...).
    The site caps a hearing-extract query at 31 days; we conservatively apply the
    31-day cap to every query and chunk longer lookbacks (e.g. --backfill-days 90).

Signal logic (eviction_spike):
    Plaintiff on an eviction case = landlord / property manager. We keep only
    entity-looking plaintiffs (LLC/INC/PROPERTIES/MANAGEMENT/APARTMENTS/...),
    group filings per plaintiff entity per window, and store a snapshot
    (source_id, window_end, entity_key) -> {filings, weekly_rate} every run.
    Baseline = mean weekly_rate of this entity's PRIOR snapshots (dates before
    this window's end). A spike fires when:
        - filings in window >= MIN_FILINGS_ABS, and
        - no baseline yet (first run): weekly_rate >= FIRST_RUN_MIN_WEEKLY, or
        - baseline exists: weekly_rate - baseline >= MIN_EXCESS_WEEKLY.
    magnitude = clamp(excess_weekly / FULL_SCALE_EXCESS, 0.05, 1.0)
    (calibrated on a real 7-day pull: 384 entity plaintiffs, median 1 filing,
    top plaintiff 15 filings/week).

Self-test:  python -m collectors.evictions_harris --self-test
    Collects the last 30 days into an in-memory store, prints counts, saves
    fixtures/evictions_harris_sample.json. Touches no sheet, no real DB.
"""
import csv
import io
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from common import http  # noqa: E402
from common.normalize import clean_zip, entity_key as make_entity_key  # noqa: E402

EXTRACT_URL = "https://jpwebsite.harriscountytx.gov/PublicExtracts/GetExtractData"
CASE_TYPE_EVICTION = "8464"       # from requestscripts.js civil case-type list
EXTRACT_CASES_FILED = "7"         # civil "Cases Filed" extract
COURT_ALL = "300"                 # all JP courts
MAX_WINDOW_DAYS = 31              # hard cap per query (site-enforced for hearings;
                                  # applied to all queries to stay safe)

# --- spike calibration (see module docstring) ---
MIN_FILINGS_ABS = 3               # never signal below this many filings in window
FIRST_RUN_MIN_WEEKLY = 5.0        # no baseline yet: weekly rate needed to signal
MIN_EXCESS_WEEKLY = 2.0           # with baseline: filings/week above baseline
FULL_SCALE_EXCESS = 15.0          # excess filings/week that maps to magnitude 1.0
MAGNITUDE_FLOOR = 0.05

# CSV column indexes (validated against a live pull 2026-07-05)
COL_CASE_NUMBER = 0
COL_COURT = 1
COL_CASE_TYPE = 2
COL_FILE_DATE = 3
COL_STYLE = 4
COL_CAUSE = 5
COL_STATUS = 7
COL_PLAINTIFF_NAME = 8
COL_PLAINTIFF_ADDR1 = 9
COL_PLAINTIFF_CITY = 11
COL_PLAINTIFF_STATE = 12
COL_PLAINTIFF_ZIP = 13
COL_DEFENDANT_NAME = 20
MIN_ROW_LEN = 26

# Tokens that mark a plaintiff as a landlord / PM company rather than a person.
# Matched on the RAW uppercased name (normalize_name strips legal suffixes).
_ENTITY_TOKENS = {
    "LLC", "INC", "CORP", "CORPORATION", "LP", "LLP", "LTD", "CO", "COMPANY",
    "PROPERTIES", "PROPERTY", "MANAGEMENT", "MGMT", "APARTMENTS", "APARTMENT",
    "APTS", "REALTY", "HOMES", "HOUSING", "INVESTMENTS", "INVESTMENT", "GROUP",
    "PARTNERS", "PARTNERSHIP", "ASSOCIATES", "HOLDINGS", "ENTERPRISES", "TRUST",
    "ESTATES", "VILLAS", "RESIDENCES", "COMMUNITIES", "VENTURES", "CAPITAL",
    "ASSETS", "EQUITIES", "HOA", "ASSOCIATION", "CONDOMINIUM", "CONDOMINIUMS",
    "AUTHORITY", "DEVELOPMENT", "RENTALS", "LEASING", "VILLAGE", "PLAZA",
    "TOWNHOMES", "LOFTS", "REIT", "FUND", "PORTFOLIO",
}
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def _is_entity(name):
    """True when a plaintiff name looks like a company, not a private person."""
    return any(t.upper() in _ENTITY_TOKENS for t in _TOKEN_RE.findall(name or ""))


def _mmddyyyy(d):
    return d.strftime("%m/%d/%Y")


def _iso_from_mmddyyyy(s):
    """'06/29/2026' -> '2026-06-29' (returns None on garbage)."""
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    if not m:
        return None
    mm, dd, yyyy = (int(g) for g in m.groups())
    try:
        return date(yyyy, mm, dd).isoformat()
    except ValueError:
        return None


def _windows(since, until):
    """Chunk [since, until] into inclusive windows of at most MAX_WINDOW_DAYS."""
    out = []
    start = since
    while start <= until:
        end = min(start + timedelta(days=MAX_WINDOW_DAYS - 1), until)
        out.append((start, end))
        start = end + timedelta(days=1)
    return out


def _query_params(w_start, w_end, fmt="csv"):
    return {
        "extractCaseType": "CV",
        "extract": EXTRACT_CASES_FILED,
        "court": COURT_ALL,
        "casetype": CASE_TYPE_EVICTION,
        "format": fmt,
        "fdate": _mmddyyyy(w_start),
        "tdate": _mmddyyyy(w_end),
    }


def _query_url(params):
    return f"{EXTRACT_URL}?{urlencode(params)}"


def _fetch_window(w_start, w_end):
    """Pull one window of eviction filings. Returns (parsed_rows, query_url).

    Each parsed row is a dict for an entity-plaintiff eviction case.
    """
    params = _query_params(w_start, w_end)
    resp = http.fetch(EXTRACT_URL, params=params)
    url = _query_url(params)
    rows = []
    reader = csv.reader(io.StringIO(resp.text))
    header_seen = False
    for row in reader:
        if not header_seen:
            header_seen = True          # first row is the column header
            continue
        if len(row) < MIN_ROW_LEN:
            continue                    # blank/truncated tail rows
        name = (row[COL_PLAINTIFF_NAME] or "").strip()
        if not name:
            continue
        rows.append({
            "case_number": row[COL_CASE_NUMBER].strip(),
            "court": row[COL_COURT].strip(),
            "case_type": row[COL_CASE_TYPE].strip(),
            "file_date": _iso_from_mmddyyyy(row[COL_FILE_DATE]),
            "style": row[COL_STYLE].strip(),
            "cause_of_action": row[COL_CAUSE].strip(),
            "status": row[COL_STATUS].strip(),
            "plaintiff_name": name,
            "plaintiff_street": (row[COL_PLAINTIFF_ADDR1] or "").strip(),
            "plaintiff_city": (row[COL_PLAINTIFF_CITY] or "").strip(),
            "plaintiff_state": (row[COL_PLAINTIFF_STATE] or "").strip(),
            "plaintiff_zip": clean_zip(row[COL_PLAINTIFF_ZIP]),
            "defendant_name": (row[COL_DEFENDANT_NAME] or "").strip(),
        })
    return rows, url


class Collector(BaseCollector):
    avenue = "property_mgmt"
    source_id = "evictions_harris"
    metros = ("houston",)

    def collect(self, since, store, registry):
        signals_added = 0
        entities = set()
        any_rows = False
        try:
            today = date.today()
            if since > today:
                since = today
            for w_start, w_end in _windows(since, today):
                rows, url = _fetch_window(w_start, w_end)
                if rows:
                    any_rows = True
                signals_added, seen = self._process_window(
                    store, rows, url, w_start, w_end, signals_added)
                entities |= seen
            status = "OK" if any_rows else "EMPTY"
            return CollectorResult(
                source_id=self.source_id,
                signals_added=signals_added,
                entities_seen=len(entities),
                status=status,
            )
        except Exception as exc:  # noqa: BLE001 — contract: never raise
            return CollectorResult(
                source_id=self.source_id,
                signals_added=signals_added,
                entities_seen=len(entities),
                status="ERROR",
                error=f"{type(exc).__name__}: {exc}",
            )

    def _process_window(self, store, rows, url, w_start, w_end, signals_added):
        """Group one window's filings per entity plaintiff, snapshot, and signal."""
        window_days = (w_end - w_start).days + 1
        by_entity = {}
        for r in rows:
            if not _is_entity(r["plaintiff_name"]):
                continue
            ekey = make_entity_key(r["plaintiff_name"], r["plaintiff_zip"])
            by_entity.setdefault(ekey, []).append(r)

        seen = set(by_entity)
        for ekey, cases in by_entity.items():
            first = cases[0]
            filings = len(cases)
            weekly_rate = filings * 7.0 / window_days

            # Baseline BEFORE adding this window's snapshot.
            prior = [
                s for s in store.get_snapshots(self.source_id, ekey)
                if s["snapshot_date"] < w_end.isoformat()
            ]
            baseline = (
                sum(float(s["payload"].get("weekly_rate", 0.0)) for s in prior)
                / len(prior)
            ) if prior else None

            store.add_snapshot(self.source_id, w_end.isoformat(), ekey, {
                "window_start": w_start.isoformat(),
                "window_end": w_end.isoformat(),
                "filings": filings,
                "weekly_rate": round(weekly_rate, 3),
                "plaintiff_name": first["plaintiff_name"],
            })

            store.upsert_entity(
                ekey, self.avenue, "houston", first["plaintiff_name"],
                zip=first["plaintiff_zip"] or None,
                street=first["plaintiff_street"] or None,
                attrs={"city": first["plaintiff_city"],
                       "state": first["plaintiff_state"]},
            )

            if filings < MIN_FILINGS_ABS:
                continue
            if baseline is None:
                if weekly_rate < FIRST_RUN_MIN_WEEKLY:
                    continue
                excess = weekly_rate
            else:
                excess = weekly_rate - baseline
                if excess < MIN_EXCESS_WEEKLY:
                    continue

            magnitude = max(MAGNITUDE_FLOOR,
                            min(1.0, excess / FULL_SCALE_EXCESS))
            signal_date = max(
                (c["file_date"] for c in cases if c["file_date"]),
                default=w_end.isoformat(),
            )
            sig = Signal(
                entity_key=ekey,
                entity_name=first["plaintiff_name"],
                metro="houston",
                avenue=self.avenue,
                signal_type="eviction_spike",
                signal_date=signal_date,
                magnitude=round(magnitude, 3),
                source_id=self.source_id,
                source_ref=url,
                raw={
                    "filings_in_window": filings,
                    "window": [w_start.isoformat(), w_end.isoformat()],
                    "weekly_rate": round(weekly_rate, 3),
                    "baseline_weekly": round(baseline, 3) if baseline is not None else None,
                    "excess_weekly": round(excess, 3),
                    "case_numbers": [c["case_number"] for c in cases][:25],
                    "sample_case": first,
                },
                attrs={
                    "street": first["plaintiff_street"] or None,
                    "zip": first["plaintiff_zip"] or None,
                },
            )
            if store.add_signal(sig):
                signals_added += 1
        return signals_added, seen


def _self_test():
    from common.store import Store

    print(f"[{Collector.source_id}] self-test: last 30 days, in-memory store")
    store = Store(db_path=":memory:")
    since = date.today() - timedelta(days=30)

    # Grab one raw sample payload for the fixture (independent of collect()
    # so the fixture shows the true wire format).
    sample = {"query_url": None, "sample_record": None, "rows_in_window": 0}
    try:
        w_end = date.today()
        w_start = w_end - timedelta(days=6)
        rows, url = _fetch_window(w_start, w_end)
        sample["query_url"] = url
        sample["rows_in_window"] = len(rows)
        sample["sample_record"] = rows[0] if rows else None
    except Exception as exc:  # noqa: BLE001
        sample["fixture_error"] = f"{type(exc).__name__}: {exc}"

    result = Collector().collect(since, store, {})

    _FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    fixture_path = _FIXTURES_DIR / f"{Collector.source_id}_sample.json"
    fixture_path.write_text(json.dumps(sample, indent=2, default=str),
                            encoding="utf-8")

    n_signals = len(store.get_signals(avenue=Collector.avenue))
    n_entities = len(store.iter_entities(avenue=Collector.avenue))
    print(f"  status        : {result.status}")
    print(f"  signals_added : {result.signals_added}")
    print(f"  entities_seen : {result.entities_seen}")
    print(f"  store signals : {n_signals}")
    print(f"  store entities: {n_entities}")
    if result.error:
        print(f"  error         : {result.error}")
    print(f"  fixture       : {fixture_path}")
    store.close()
    return 0 if result.status in ("OK", "EMPTY") else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print("Usage: python -m collectors.evictions_harris --self-test")
