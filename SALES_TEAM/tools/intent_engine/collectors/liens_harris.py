"""Harris County Clerk Real Property lien/judgment collector (avenue: pe_distress).

Source: https://www.cclerk.hctx.net/applications/websearch/RP.aspx
Classic ASP.NET WebForms: GET the page for __VIEWSTATE / __EVENTVALIDATION
hidden fields, then POST the search form. Verified live 2026-07-05.

Instrument codes (exact match required; probed against the live index):
    A/J   Abstract of Judgment            -> judgment_filed  (mag 1.0)
    LIEN  all liens incl. state/federal tax liens, mechanic's & materialman's,
          municipal — classified by claimant name -> lien_filed
          (federal_tax 1.0 / state_tax 1.0 / municipal 0.6 / mechanics 0.7)
    L/P   Lis Pendens                     -> lien_filed      (mag 0.6)
Long-form spellings ("ABSTRACT OF JUDGMENT", "TAX LIEN", "MECHANICS LIEN",
"LIS PENDENS", "M/L", "FTL", "STL") return zero records — do not use them.

Role convention (verified empirically, e.g. WELLS FARGO BANK NA is Grantor on
its A/Js and CITY OF PASADENA is Grantor on its liens): in this index the
GRANTOR is the claimant/creditor and the GRANTEE is the debtor. The Signal
entity is therefore the business-looking GRANTEE (the distressed debtor),
matching the avenue's intent of "grantor/debtor business name". The index
exposes no address, so zip is empty: entity_key "biz:{name_norm}|".

Result cap: the server returns at most ~200 records per query, so date windows
are chunked per instrument (CHUNK_DAYS, tuned to observed volumes) and any
capped multi-day chunk is re-queried day by day. A capped SINGLE day cannot be
split further — accepted, with a truncation note in CollectorResult.error.
Each search needs a fresh GET first: posting against a results page's
viewstate fails __EVENTVALIDATION and silently returns zero records.

GA (Fulton etc.) lien indexes are PAID (GSCCCA) — intentionally NOT attempted;
leave for v2. This collector is Houston/Harris only.

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_harris --self-test
Collects the last 30 days into a throwaway in-memory store, prints status and
per-type counts, writes NOTHING to the sheet, and saves one raw sample record
to fixtures/liens_harris_sample.json.
"""
import argparse
import json
import re
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from common.http import TIMEOUT, USER_AGENT  # noqa: E402
from common.normalize import entity_key as biz_entity_key  # noqa: E402

SOURCE_ID = "liens_harris"
AVENUE = "pe_distress"

SEARCH_URL = "https://www.cclerk.hctx.net/applications/websearch/RP.aspx"
RESULT_CAP = 200                 # server truncates result sets at ~200 rows
# initial chunk size per instrument, tuned to observed filing volumes so most
# chunks land under the cap on the first try (A/J caps even at 2 days)
CHUNK_DAYS = {"A/J": 1, "LIEN": 2, "L/P": 7}
COURTESY_SLEEP = 0.8             # seconds before each GET+POST pair
MAX_ATTEMPTS = 3

# instrument code -> signal_type (magnitude decided per-record for LIEN)
INSTRUMENT_CODES = ("A/J", "LIEN", "L/P")

_HIDDEN_RE = re.compile(
    r'<input[^>]*type="hidden"[^>]*name="(__[A-Za-z]+)"[^>]*value="([^"]*)"')
_BLOCK_SPLIT_RE = re.compile(
    r'(?=<span id="ctl00_ContentPlaceHolder1_ListView1_ctrl\d+_lblFileNo")')
_FILENO_RE = re.compile(r'lblFileNo">([^<]*)')
_FILEDATE_RE = re.compile(r'lblFileDate">([^<]*)')
_TYPE_RE = re.compile(r'lnkdetailtest[^>]*>([^<]*)')
_PARTY_RE = re.compile(r"<b>(Grantor|Grantee)</b>:.*?lblNames\">([^<]*)", re.S)
_NO_RECORDS_RE = re.compile(r"No records found", re.I)

# ---- debtor / claimant heuristics -----------------------------------------

_BUSINESS_TOKENS = {
    "LLC", "L.L.C", "INC", "CORP", "CORPORATION", "CO", "COMPANY", "LP",
    "LLP", "LTD", "PLLC", "PC", "PA", "ENTERPRISES", "ENTERPRISE", "HOLDINGS",
    "GROUP", "SERVICES", "SERVICE", "PARTNERS", "ASSOCIATES", "TRUCKING",
    "LOGISTICS", "TRANSPORT", "CONSTRUCTION", "BUILDERS", "CONTRACTORS",
    "RESTAURANT", "REPAIR", "INVESTMENTS", "PROPERTIES", "SOLUTIONS",
    "INDUSTRIES", "MANAGEMENT", "VENTURES", "AUTOMOTIVE", "MECHANICAL",
    "PLUMBING", "ELECTRIC", "ROOFING", "CONCRETE", "FABRICATION", "SUPPLY",
    "DISTRIBUTORS", "FOODS", "HOSPITALITY", "REALTY", "STUDIO", "CLINIC",
}
_GOV_MARKERS = (
    "STATE OF", "CITY OF", "COUNTY", "UNITED STATES", "INTERNAL REVENUE",
    "US TREASURY", "U S TREASURY", "SCHOOL", "ISD", "AUTHORITY", "COMMISSION",
    "DEPARTMENT", "ATTORNEY GENERAL", "MUNICIPAL", "UTILITY DISTRICT",
    "COMPTROLLER", "ADMINISTRATION",
)
_FEDERAL_MARKERS = ("INTERNAL REVENUE", "UNITED STATES", "US TREASURY",
                    "U S TREASURY", "IRS", "US SMALL BUSINESS", "U S SMALL")
_STATE_TX_MARKERS = ("STATE OF TEXAS", "TEXAS WORKFORCE", "COMPTROLLER",
                     "ATTORNEY GENERAL", "EMPLOYMENT COMMISSION")
_MUNI_MARKERS = ("CITY OF", "COUNTY", "MUNICIPAL", "UTILITY DISTRICT", "ISD",
                 "SCHOOL DISTRICT", "AUTHORITY")


def _looks_gov(name):
    return any(m in name for m in _GOV_MARKERS)


def _looks_business(name):
    if _looks_gov(name):
        return False
    words = set(re.sub(r"[^\w\s]", " ", name.upper()).split())
    return bool(words & _BUSINESS_TOKENS)


def _classify_lien(grantors):
    """Map a LIEN record to (lien_kind, magnitude) from its claimant names."""
    joined = " | ".join(g.upper() for g in grantors)
    if any(m in joined for m in _FEDERAL_MARKERS):
        return "federal_tax_lien", 1.0
    if any(m in joined for m in _STATE_TX_MARKERS):
        return "state_tax_lien", 1.0
    if any(m in joined for m in _MUNI_MARKERS):
        return "municipal_lien", 0.6
    return "mechanics_or_private_lien", 0.7


# ---- WebForms plumbing ------------------------------------------------------
# common/http.fetch() is GET-only and stateless; this WebForms flow needs a
# cookie session + POST, so we use requests directly but keep common.http's
# UA/timeout and a courtesy sleep. No secrets involved (public index).

def _hidden_fields(html):
    return dict(_HIDDEN_RE.findall(html))


def _blank_form(hidden, instrument, d_from, d_to):
    form = dict(hidden)
    p = "ctl00$ContentPlaceHolder1$"
    for f in ("txtFileNo", "txtFilmCd", "txtOR", "txtEE", "txtNameTee",
              "txtDesc", "txtVolNo", "txtPageNo", "txtSection", "txtLot",
              "txtBlock", "txtUnit", "txtAbstract", "txtOutLot", "txtTract",
              "txtReserve"):
        form[p + f] = ""
    form[p + "txtFrom"] = d_from.strftime("%m/%d/%Y")
    form[p + "txtTo"] = d_to.strftime("%m/%d/%Y")
    form[p + "txtInstrument"] = instrument
    form[p + "btnSearch"] = "Search"
    return form


def parse_results(html):
    """Parse a results page into raw record dicts."""
    if _NO_RECORDS_RE.search(html):
        return []
    records = []
    for block in _BLOCK_SPLIT_RE.split(html)[1:]:
        fileno = _FILENO_RE.search(block)
        if not fileno or not fileno.group(1).strip():
            continue
        filedate = _FILEDATE_RE.search(block)
        ftype = _TYPE_RE.search(block)
        parties = _PARTY_RE.findall(block)
        records.append({
            "file_no": fileno.group(1).strip(),
            "file_date": filedate.group(1).strip() if filedate else "",
            "instrument": ftype.group(1).strip() if ftype else "",
            "grantors": [n.strip() for r, n in parties
                         if r == "Grantor" and n.strip()],
            "grantees": [n.strip() for r, n in parties
                         if r == "Grantee" and n.strip()],
        })
    return records


class Collector(BaseCollector):
    avenue = AVENUE
    source_id = SOURCE_ID
    metros = ("houston",)

    # -- HTTP --------------------------------------------------------------

    def _get_session(self):
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        return s

    def _search(self, session, instrument, d_from, d_to):
        """One GET (fresh viewstate) + one POST. Returns records.

        The hidden fields MUST come from a fresh GET of the search form:
        posting a new search against a results page's viewstate fails
        __EVENTVALIDATION and the server silently returns zero records
        (verified live 2026-07-05).
        """
        last_exc = None
        for attempt in range(MAX_ATTEMPTS):
            try:
                time.sleep(COURTESY_SLEEP)
                r0 = session.get(SEARCH_URL, timeout=TIMEOUT)
                r0.raise_for_status()
                hidden = _hidden_fields(r0.text)
                if "__VIEWSTATE" not in hidden:
                    raise requests.RequestException("no __VIEWSTATE on GET")
                r = session.post(
                    SEARCH_URL,
                    data=_blank_form(hidden, instrument, d_from, d_to),
                    timeout=120)
                r.raise_for_status()
                return parse_results(r.text)
            except requests.RequestException as exc:
                last_exc = exc
                session = self._get_session()   # fresh cookies on retry
                time.sleep(2.0 * (attempt + 1))
        raise last_exc

    def _collect_range(self, session, instrument, d_from, d_to, notes):
        """Chunked + cap-splitting search over [d_from, d_to]. Returns records.

        Capped multi-day chunks are re-queried as single days (no halving
        cascade). A capped single day cannot be split — noted as truncated.
        """
        chunk = CHUNK_DAYS.get(instrument, 4)
        out = []
        stack = []
        cur = d_from
        while cur <= d_to:
            end = min(cur + timedelta(days=chunk - 1), d_to)
            stack.append((cur, end))
            cur = end + timedelta(days=1)
        while stack:
            a, b = stack.pop(0)
            records = self._search(session, instrument, a, b)
            if len(records) >= RESULT_CAP and a != b:
                days = [(a + timedelta(days=i),) * 2
                        for i in range((b - a).days + 1)]
                stack[0:0] = days
                continue
            if len(records) >= RESULT_CAP:
                notes.append(f"{instrument} {a.isoformat()} capped at "
                             f"{RESULT_CAP} rows (single day, truncated)")
            out.extend(records)
        return out

    # -- signal emission -----------------------------------------------------

    def _emit(self, store, record, since):
        """Emit 0+ Signals for one raw record. Returns (added, entity_keys)."""
        try:
            fdate = datetime.strptime(record["file_date"], "%m/%d/%Y").date()
        except ValueError:
            return 0, set()
        if fdate < since:
            return 0, set()
        instrument = record["instrument"].upper()
        if instrument == "A/J":
            signal_type, lien_kind, magnitude = \
                "judgment_filed", "abstract_of_judgment", 1.0
        elif instrument == "L/P":
            signal_type, lien_kind, magnitude = \
                "lien_filed", "lis_pendens", 0.6
        elif instrument == "LIEN":
            signal_type = "lien_filed"
            lien_kind, magnitude = _classify_lien(record["grantors"])
        else:
            return 0, set()

        debtors = [g for g in record["grantees"] if _looks_business(g)]
        added = 0
        keys = set()
        for name in debtors:
            key = biz_entity_key(name, "")
            claimant = record["grantors"][0] if record["grantors"] else ""
            sig = Signal(
                entity_key=key,
                entity_name=name,
                metro="houston",
                avenue=self.avenue,
                signal_type=signal_type,
                signal_date=fdate.isoformat(),
                magnitude=magnitude,
                source_id=self.source_id,
                source_ref=record["file_no"],
                raw=dict(record),
                attrs={
                    "lien_kind": lien_kind,
                    "claimant": claimant,
                    "county": "HARRIS",
                    "instrument_type": instrument,
                },
            )
            if store.add_signal(sig):
                added += 1
            keys.add(key)
        return added, keys

    # -- contract entrypoint ---------------------------------------------------

    def collect(self, since, store, registry):
        try:
            today = date.today()
            session = self._get_session()
            notes = []
            errors = []
            total_added = 0
            entities = set()
            seen_files = set()
            any_query_ok = False
            for instrument in INSTRUMENT_CODES:
                try:
                    records = self._collect_range(
                        session, instrument, since, today, notes)
                    any_query_ok = True
                except Exception as exc:
                    errors.append(f"{instrument}: {type(exc).__name__}: {exc}")
                    continue
                for rec in records:
                    if rec["file_no"] in seen_files:
                        continue
                    seen_files.add(rec["file_no"])
                    added, keys = self._emit(store, rec, since)
                    total_added += added
                    entities |= keys
            if not any_query_ok:
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       "; ".join(errors) or "all queries failed")
            status = "OK" if total_added else "EMPTY"
            detail = "; ".join(errors + notes)
            return CollectorResult(self.source_id, total_added, len(entities),
                                   status, detail)
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

def _self_test(days=30):
    from common.store import Store
    print(f"[{SOURCE_ID}] --self-test  (last {days} days, live site, "
          f"throwaway in-memory store)")
    since = date.today() - timedelta(days=days)
    registry = config.load_registry()
    store = Store(":memory:")
    result = Collector().collect(since, store, registry)

    sigs = store.get_signals(avenue=AVENUE)
    by_type = Counter(s["signal_type"] for s in sigs)
    by_kind = Counter(json.loads(s["attrs"]).get("lien_kind", "?")
                      for s in sigs)
    sample = json.loads(sigs[0]["raw"]) if sigs else None
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture = {
        "source_id": SOURCE_ID,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "window_days": days,
        "note": ("raw record behind the first emitted signal" if sample else
                 "no signals emitted; " + (result.error or result.status)),
        "sample_record": sample,
        "signal_counts": dict(by_type),
        "lien_kind_counts": dict(by_kind),
    }
    fixture_path = fixtures_dir / f"{SOURCE_ID}_sample.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, default=str),
                            encoding="utf-8")

    print(f"  status={result.status} signals={result.signals_added} "
          f"entities={result.entities_seen}")
    if result.error:
        print(f"  detail: {result.error}")
    print(f"  by signal_type: {dict(by_type)}")
    print(f"  by lien_kind:   {dict(by_kind)}")
    print(f"  fixture saved: {fixture_path}")
    print(f"  RESULT: {result.status}")
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="collect last N days into a throwaway store; "
                             "writes nothing but fixtures/<source_id>_sample.json")
    parser.add_argument("--days", type=int, default=30,
                        help="self-test lookback window (default 30)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test(args.days))
    parser.print_help()
