"""Shared GSCCCA State Tax Lien scrape flow for the Atlanta-metro lien collectors.

NOT a collector itself (underscore prefix, never listed in collectors_enabled).
collectors/liens_fulton.py, liens_dekalb.py, liens_cobb.py and liens_gwinnett.py
subclass GSCCCAStateTaxCollector with their county name + GSCCCA county id.

Source: https://search.gsccca.org/liensearch/StateTaxLienSearch.aspx
GA Dept of Revenue SOLVED pending state-tax-lien registry (post-2018
centralized). FREE, NO LOGIN — the only fully free programmatic lien slice
for the Atlanta metro (verified live 2026-07-06 with plain requests; Bright
Data not needed). Every record links to gtc.dor.ga.gov/Services/SOLVED/Link/
?REV=<control#> which doubles as the evidence URL.

Three-step ASP.NET WebForms flow (all verified live 2026-07-06):
  1. GET  StateTaxLienSearch.aspx  -> __VIEWSTATE/__EVENTVALIDATION/__PREVIOUSPAGE
  2. cross-page POST StateTaxLienNames.aspx with txtSearchName, ddlCounties,
     txtDateFrom/txtDateTo (MM/DD/YYYY), ddlRecordsPerPage=100, ddlDisplayType=1,
     btnSearch='Begin Search' (exact value) -> name-occurrence grid
  3. harvest EVERY input/select from the names page, tick
     ctl00$BodyContent$gvOccurrences$ctlNN$chkSelect=on, cross-page POST
     StateTaxLienNamesSelected.aspx with btnSearch='Display Checked Details'
     -> full records (county, 'State Tax Lien', filed datetime, Control/REV #
     link, Direct Party = debtor(s), Reverse Party = GA DOR).

Hard-won flow facts (each one cost a live debugging round):
  * txtSearchName='%' is a match-everything wildcard -> no A-Z name
    enumeration needed. ''=bounces (302), '*'=zero rows. Single letters are
    plain prefix matches.
  * The date range filters on the lien Filed date (wrong-window control query
    returned 0 rows). The registry is a rolling recent-pending window: a
    6-month Fulton wildcard returned barely more than 30 days (77 vs 76).
  * Step-3 MUST replay every input AND every select with its *selected*
    option ('selected' precedes value= in the markup — a lazy regex reads the
    first option, silently resets the search to All Counties and bounces you
    back to the names page).
  * Checking a name shows ALL of that name's records, and joint debtors pull
    each other's filings in — 40 checked Fulton names fanned out to 118
    records. Details paginate at 100/page and in-place pager postbacks 500,
    so batches are kept small and halved when a details page overflows.
  * Each details POST gets its own fresh step-1+2 (viewstate reuse across
    cross-page posts is unverified; fresh is proven).

Signals emitted (avenue pe_distress, metro atlanta):
    lien_filed / lien_kind=state_tax_lien / magnitude 1.0 — one per
    business-looking direct party (same debtor heuristics as liens_harris;
    individuals are skipped). The index exposes no address, so zip is empty:
    entity_key "biz:{name_norm}|".

Coverage honesty: this registry holds ONLY GA DOR state tax liens. FIFAs
(money judgments on the General Execution Docket), federal tax liens,
mechanics liens and lis pendens live in the GSCCCA statewide lien index,
which requires a paid account — see each county module's docstring for the
exact v2 unlock. Do NOT mistake this collector for full judgment coverage.
"""
import argparse
import html as htmllib
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

AVENUE = "pe_distress"
METRO = "atlanta"

BASE = "https://search.gsccca.org/liensearch/"
SEARCH_PAGE = BASE + "StateTaxLienSearch.aspx"
NAMES_PAGE = BASE + "StateTaxLienNames.aspx"
SELECTED_PAGE = BASE + "StateTaxLienNamesSelected.aspx"

# ddlCounties option values, read from the live dropdown 2026-07-06
# (same ids the paid lien index uses as intCountyID)
COUNTY_IDS = {"FULTON": "60", "DEKALB": "44", "COBB": "33", "GWINNETT": "67"}

WILDCARD = "%"                # matches every name (verified live)
BATCH_NAMES = 15              # names per details POST; halved on overflow
COURTESY_SLEEP = 1.2          # seconds before each HTTP request
MAX_ATTEMPTS = 3

_HIDDEN_RE = re.compile(
    r'<input[^>]*type="hidden"[^>]*name="(__[A-Za-z]+)"[^>]*value="([^"]*)"')
_INPUT_RE = re.compile(r"<input[^>]*>", re.I)
_ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
_SELECT_RE = re.compile(r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>',
                        re.S | re.I)
_OPTION_RE = re.compile(r"<option([^>]*)>", re.I)
_GRID_RE = re.compile(r"<table[^>]*gvOccurrences[^>]*>(.*?)</table>", re.S)
_ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
_CHK_RE = re.compile(
    r'name="(ctl00\$BodyContent\$gvOccurrences\$ctl\d+\$chkSelect)"')
_CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
_PAGES_RE = re.compile(r"Page (\d+) of (\d+)")
_NO_RECORDS_RE = re.compile(r"No records were found", re.I)
_BLOCK_SPLIT_RE = re.compile(
    r'(?=<span id="BodyContent_lvStandard_lblStandardCounty_\d+")')
_D_COUNTY_RE = re.compile(r'lblStandardCounty_\d+">([^<]*)')
_D_TYPE_RE = re.compile(r'lblInstrumentType_\d+">([^<]*)')
_D_FILED_RE = re.compile(r'lblDateFiled_\d+">([^<]*)')
_D_CTRL_RE = re.compile(
    r'lnkControlNumber_\d+"[^>]*href="([^"]*)"[^>]*>[^<]*?([\d]+)\s*<')
_D_DIRECT_RE = re.compile(r'lblDirectPartyName_\d+">([^<]*)')
_D_REVERSE_RE = re.compile(r'lblReversePartyName_\d+">([^<]*)')

# ---- debtor heuristics (mirrors collectors/liens_harris.py) -----------------

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
    "COMPTROLLER", "ADMINISTRATION", "DEPT OF REVENUE",
)


def _looks_business(name):
    up = name.upper()
    if any(m in up for m in _GOV_MARKERS):
        return False
    words = set(re.sub(r"[^\w\s]", " ", up).split())
    return bool(words & _BUSINESS_TOKENS)


def _clean_text(s):
    """Unescape (twice — grid text arrives double-escaped) and tidy."""
    return re.sub(r"\s+", " ", htmllib.unescape(htmllib.unescape(s))).strip()


# ---- WebForms plumbing -------------------------------------------------------
# common/http.fetch() is GET-only and stateless; this flow needs a cookie
# session + cross-page POSTs, so requests is used directly with common.http's
# UA/timeout and a courtesy sleep (same approach as collectors/liens_harris.py).

def harvest_form(html):
    """Replicate every input + select a browser would submit from form1.

    Skips submit buttons and unchecked checkboxes; selects contribute their
    *selected* option ('selected' precedes value= in GSCCCA markup — reading
    the first option instead silently resets the search; verified live).
    """
    fields = {}
    for tag in _INPUT_RE.findall(html):
        attrs = dict(_ATTR_RE.findall(tag))
        name = attrs.get("name")
        if not name or name == "search":     # 'search' is the sitewide box
            continue
        typ = attrs.get("type", "text").lower()
        if typ in ("submit", "button", "image"):
            continue
        if typ in ("checkbox", "radio"):
            if "checked" in tag.lower():
                fields[name] = attrs.get("value", "on")
            continue
        fields[name] = attrs.get("value", "")
    for name, body in _SELECT_RE.findall(html):
        chosen, first = None, None
        for m in _OPTION_RE.finditer(body):
            val = dict(_ATTR_RE.findall(m.group(1))).get("value", "")
            if first is None:
                first = val
            if "selected" in m.group(1).lower():
                chosen = val
        fields[name] = chosen if chosen is not None else (first or "")
    return fields


def parse_names_grid(html):
    """Names page -> (rows, total_pages). rows = [(chk_field, occurs, name)]."""
    if _NO_RECORDS_RE.search(html):
        return [], 1
    rows = []
    grid = _GRID_RE.search(html)
    if grid:
        for row in _ROW_RE.findall(grid.group(1)):
            chk = _CHK_RE.search(row)
            cells = [re.sub(r"<[^>]+>", " ", c) for c in _CELL_RE.findall(row)]
            if chk and len(cells) >= 3:
                rows.append((chk.group(1), _clean_text(cells[1]),
                             _clean_text(cells[2])))
    pages = _PAGES_RE.search(html)
    return rows, (int(pages.group(2)) if pages else 1)


def parse_details(html):
    """Details page -> (records, total_pages)."""
    records = []
    for block in _BLOCK_SPLIT_RE.split(html)[1:]:
        county = _D_COUNTY_RE.search(block)
        itype = _D_TYPE_RE.search(block)
        filed = _D_FILED_RE.search(block)
        ctrl = _D_CTRL_RE.search(block)
        records.append({
            "county": _clean_text(county.group(1)) if county else "",
            "instrument": _clean_text(itype.group(1)) if itype else "",
            "filed": _clean_text(filed.group(1)) if filed else "",
            "control_url": ctrl.group(1) if ctrl else "",
            "control_rev": ctrl.group(2) if ctrl else "",
            "direct_parties": [_clean_text(n)
                               for n in _D_DIRECT_RE.findall(block)],
            "reverse_parties": [_clean_text(n)
                                for n in _D_REVERSE_RE.findall(block)],
        })
    pages = _PAGES_RE.search(html)
    return records, (int(pages.group(2)) if pages else 1)


class GSCCCAStateTaxCollector(BaseCollector):
    """Base collector; subclasses set source_id, county_name, county_id."""

    avenue = AVENUE
    metros = (METRO,)
    county_name = None            # e.g. "FULTON"
    county_id = None              # e.g. "60"

    # -- HTTP ----------------------------------------------------------------

    def _session(self):
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        return s

    def _post_names(self, session, d_from, d_to):
        """Steps 1+2: fresh viewstate GET, then cross-page wildcard search.

        Returns the names-page HTML. Retries with a fresh session; raises the
        last exception after MAX_ATTEMPTS (caller catches).
        """
        last_exc = None
        for attempt in range(MAX_ATTEMPTS):
            try:
                time.sleep(COURTESY_SLEEP)
                r0 = session.get(SEARCH_PAGE, timeout=TIMEOUT)
                r0.raise_for_status()
                hidden = dict(_HIDDEN_RE.findall(r0.text))
                if "__VIEWSTATE" not in hidden:
                    raise requests.RequestException("no __VIEWSTATE on GET")
                payload = dict(hidden)
                payload.update({
                    "ctl00$BodyContent$txtSearchName": WILDCARD,
                    "ctl00$BodyContent$ddlCounties": self.county_id,
                    "ctl00$BodyContent$txtDateFrom": d_from.strftime("%m/%d/%Y"),
                    "ctl00$BodyContent$txtDateTo": d_to.strftime("%m/%d/%Y"),
                    "ctl00$BodyContent$ddlRecordsPerPage": "100",
                    "ctl00$BodyContent$ddlDisplayType": "1",
                    "ctl00$BodyContent$btnSearch": "Begin Search",
                })
                time.sleep(COURTESY_SLEEP)
                r1 = session.post(NAMES_PAGE, data=payload, timeout=TIMEOUT,
                                  headers={"Referer": SEARCH_PAGE},
                                  allow_redirects=False)
                if r1.status_code != 200:
                    raise requests.RequestException(
                        f"names POST bounced: HTTP {r1.status_code}")
                return r1.text
            except requests.RequestException as exc:
                last_exc = exc
                session.cookies.clear()
                time.sleep(2.0 * (attempt + 1))
        raise last_exc

    def _post_details(self, session, names_html, chk_fields):
        """Step 3: replay the full names form with chosen boxes ticked."""
        payload = harvest_form(names_html)
        for chk in chk_fields:
            payload[chk] = "on"
        payload["ctl00$BodyContent$btnSearch"] = "Display Checked Details"
        time.sleep(COURTESY_SLEEP)
        r = session.post(SELECTED_PAGE, data=payload, timeout=TIMEOUT,
                         headers={"Referer": NAMES_PAGE},
                         allow_redirects=False)
        if r.status_code != 200:
            raise requests.RequestException(
                f"details POST bounced: HTTP {r.status_code}")
        return r.text

    # -- window walking --------------------------------------------------------

    def _collect_window(self, session, d_from, d_to, notes):
        """Yield detail records for [d_from, d_to], splitting the window when
        the names grid overflows one page and halving detail batches when the
        details page overflows (in-place pager postbacks 500 on this site, so
        paging is avoided entirely)."""
        html = self._post_names(session, d_from, d_to)
        rows, pages = parse_names_grid(html)
        if pages > 1 and d_from != d_to:
            mid = d_from + timedelta(days=(d_to - d_from).days // 2)
            yield from self._collect_window(session, d_from, mid, notes)
            yield from self._collect_window(
                session, mid + timedelta(days=1), d_to, notes)
            return
        if pages > 1:
            notes.append(f"{d_from.isoformat()}: >100 debtor names in a "
                         "single day; page 1 only (truncated)")
        idx, batch = 0, BATCH_NAMES
        first = True
        while idx < len(rows):
            if not first:       # fresh viewstate per details POST (proven safe)
                html = self._post_names(session, d_from, d_to)
                rows, _ = parse_names_grid(html)
            first = False
            chks = [c for c, _, _ in rows[idx:idx + batch]]
            if not chks:
                break
            records, dpages = parse_details(
                self._post_details(session, html, chks))
            if dpages > 1 and len(chks) > 1:
                batch = max(1, len(chks) // 2)   # retry same slice, smaller
                continue
            if dpages > 1:
                notes.append(f"debtor {rows[idx][2]!r}: >100 records; "
                             "page 1 only (truncated)")
            yield from records
            idx += len(chks)
            batch = BATCH_NAMES

    # -- signal emission ---------------------------------------------------------

    def _emit(self, store, record, since, seen):
        """Emit 0+ lien_filed Signals for one record. Returns (added, keys)."""
        try:
            fdate = datetime.strptime(
                record["filed"].split()[0], "%m/%d/%Y").date()
        except (ValueError, IndexError):
            return 0, set()
        if fdate < since:
            return 0, set()
        claimant = (record["reverse_parties"][0]
                    if record["reverse_parties"]
                    else "GEORGIA STATE DEPT OF REVENUE")
        source_ref = (record["control_url"]
                      or f"GA-DOR-REV-{record['control_rev']}")
        added = 0
        keys = set()
        for name in record["direct_parties"]:
            if not _looks_business(name):
                continue                      # individuals are out of scope
            dedup = (record["control_rev"], name.upper())
            if dedup in seen:                 # joint debtors duplicate blocks
                continue
            seen.add(dedup)
            key = biz_entity_key(name, "")
            sig = Signal(
                entity_key=key,
                entity_name=name,
                metro=METRO,
                avenue=self.avenue,
                signal_type="lien_filed",
                signal_date=fdate.isoformat(),
                magnitude=1.0,
                source_id=self.source_id,
                source_ref=source_ref,
                raw=dict(record),
                attrs={
                    "lien_kind": "state_tax_lien",
                    "claimant": claimant,
                    "county": self.county_name,
                    "control_rev": record["control_rev"],
                    "registry": "GA_DOR_SOLVED",
                },
            )
            if store.add_signal(sig):
                added += 1
            keys.add(key)
        return added, keys

    # -- contract entrypoint --------------------------------------------------------

    def collect(self, since, store, registry):
        try:
            today = date.today()
            session = self._session()
            notes = []
            seen = set()
            total_added = 0
            entities = set()
            try:
                for record in self._collect_window(
                        session, since, today, notes):
                    added, keys = self._emit(store, record, since, seen)
                    total_added += added
                    entities |= keys
            except Exception as exc:
                return CollectorResult(
                    self.source_id, total_added, len(entities), "ERROR",
                    f"{type(exc).__name__}: {exc}")
            status = "OK" if total_added else "EMPTY"
            detail = "; ".join(notes)
            if status == "EMPTY" and not detail:
                detail = ("no business-debtor GA DOR state tax liens in "
                          f"{self.county_name} for the window (individuals "
                          "are filtered out); full FIFA/judgment index needs "
                          "the paid GSCCCA account — see module docstring")
            return CollectorResult(self.source_id, total_added, len(entities),
                                   status, detail)
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# shared --self-test runner (each county module's __main__ calls this)
# ---------------------------------------------------------------------------

def run_self_test(collector_cls, days=30):
    from common.store import Store
    source_id = collector_cls.source_id
    print(f"[{source_id}] --self-test  (last {days} days, live GSCCCA "
          f"state-tax-lien registry, throwaway in-memory store)")
    since = date.today() - timedelta(days=days)
    registry = config.load_registry()
    store = Store(":memory:")
    result = collector_cls().collect(since, store, registry)

    sigs = store.get_signals(avenue=AVENUE)
    by_type = Counter(s["signal_type"] for s in sigs)
    by_kind = Counter(json.loads(s["attrs"]).get("lien_kind", "?")
                      for s in sigs)
    sample = json.loads(sigs[0]["raw"]) if sigs else None
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture = {
        "source_id": source_id,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "window_days": days,
        "note": ("raw record behind the first emitted signal" if sample else
                 "no signals emitted; " + (result.error or result.status)),
        "sample_record": sample,
        "signal_counts": dict(by_type),
        "lien_kind_counts": dict(by_kind),
    }
    fixture_path = fixtures_dir / f"{source_id}_sample.json"
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


def self_test_main(collector_cls, doc):
    parser = argparse.ArgumentParser(description=doc.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="collect last N days into a throwaway store; "
                             "writes nothing but fixtures/<source_id>_sample.json")
    parser.add_argument("--days", type=int, default=30,
                        help="self-test lookback window (default 30)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(run_self_test(collector_cls, args.days))
    parser.print_help()
