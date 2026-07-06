"""Fort Bend County Clerk lien/judgment collector (avenue: pe_distress).

Source: https://ccweb.co.fort-bend.tx.us/RealEstate/SearchEntry.aspx
Aumentum Recorder (Harris Recording Solutions) — classic ASP.NET WebForms with
Infragistics controls. Free public index search, no login, no captcha.
All mechanics below were verified live 2026-07-06:

  * GET SearchEntry.aspx for __VIEWSTATE/__EVENTVALIDATION AND the form's real
    action, which is "./SearchEntry.aspx?e=newSession" — POSTing to the bare
    page URL silently re-renders the form with zero results.
  * The search must be triggered via __EVENTTARGET =
    "ctl00$cphNoMargin$SearchButtons1$btnSearch" (+ __EVENTARGUMENT="0").
    Posting the button's name=value key instead lands on the "Selection
    Criteria" page without running the search.
  * Dates are Infragistics WebDatePicker controls: the visible input has no
    name; the value travels in cphNoMargin_f_ddcDateFiled{From,To}_clientState
    using the pipe format  |0|09YYYY-MM-DD||[[[[]],[],[]],[{},[]],"09YYYY-MM-DD"]
    ("09" date-type prefix; value and JSON tail must match; slash and tilde
    encodings are silently dropped).
  * The page-level login RequiredFieldValidators run on EVERY postback and
    Page.IsValid=false silently blocks the search, so the login textboxes are
    filled with throwaway text ("x"). No logon is attempted — btnLogon is
    never the postback target; this only satisfies validation on a free
    public search.
  * Document types are an 86-item CheckBoxList; indices are parsed from the
    live form each run (name="ctl00$cphNoMargin$f$dclDocType$<idx>" value=CODE)
    rather than hard-coded. Codes used here:
        AJ      ABSTRACT OF JUDGMENT -> judgment_filed (mag 1.0)
        JUDGE   JUDGEMENT            -> judgment_filed (mag 1.0)
        FEDLIEN FEDERAL LIEN         -> lien_filed federal_tax_lien (1.0)
        STLIEN  STATE LIEN           -> lien_filed state_tax_lien   (1.0)
        LIEN    LIEN                 -> lien_filed, kind/mag by claimant name
        LISPEN  LIS PENDENS          -> lien_filed lis_pendens      (0.6)
    One combined search covers all six codes; each result row carries its own
    doc-type code.
  * Results: server transfers to SearchResults.aspx (20 rows/page, display cap
    300 rows / 15 pages). Paging is a plain GET SearchResults.aspx?pg=N on the
    same cookie session. TotalRows >= 300 means capped -> multi-day chunks are
    re-queried day by day (a capped single day is accepted with a truncation
    note), mirroring liens_harris.
  * Row roles carry explicit [R]/[E] markers (R = Grantor = claimant/creditor,
    E = Grantee = debtor; verified: JPMORGAN CHASE / HOAs are [R] on their
    AJs). The Signal entity is the business-looking [E] party. The index page
    shows one party per side plus a "(+)" more-names indicator; additional
    debtors on multi-party instruments are not visible without paid detail
    fetches — accepted limitation. No address in the index, so zip is empty:
    entity_key "biz:{name_norm}|".

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_fortbend --self-test
Collects the last 30 days into a throwaway in-memory store, prints status and
per-type counts, writes NOTHING to the sheet, and saves one raw sample record
to fixtures/liens_fortbend_sample.json.
"""
import argparse
import json
import math
import re
import sys
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._liens_common import classify_lien, looks_business  # noqa: E402
from common.http import TIMEOUT, USER_AGENT  # noqa: E402
from common.normalize import entity_key as biz_entity_key  # noqa: E402

SOURCE_ID = "liens_fortbend"
AVENUE = "pe_distress"

SEARCH_URL = "https://ccweb.co.fort-bend.tx.us/RealEstate/SearchEntry.aspx"
RESULTS_URL = "https://ccweb.co.fort-bend.tx.us/RealEstate/SearchResults.aspx"

ROWS_PER_PAGE = 20
RESULT_CAP = 300            # display cap: TotalRows never exceeds 300 (15 pages)
CHUNK_DAYS = 7              # combined 6-code query; day-split on cap
COURTESY_SLEEP = 0.8
MAX_ATTEMPTS = 3

# code -> (signal_type, lien_kind, magnitude); LIEN classified per record
CODE_MAP = {
    "AJ": ("judgment_filed", "abstract_of_judgment", 1.0),
    "JUDGE": ("judgment_filed", "judgment", 1.0),
    "FEDLIEN": ("lien_filed", "federal_tax_lien", 1.0),
    "STLIEN": ("lien_filed", "state_tax_lien", 1.0),
    "LISPEN": ("lien_filed", "lis_pendens", 0.6),
    "LIEN": ("lien_filed", None, None),
}
DOC_CODES = tuple(CODE_MAP)

_HIDDEN_RE = re.compile(
    r'<input[^>]*type="hidden"[^>]*name="([^"]+)"(?:[^>]*value="([^"]*)")?')
_ACTION_RE = re.compile(r'<form[^>]*action="([^"]*)"')
_DOCTYPE_IDX_RE = re.compile(
    r'name="ctl00\$cphNoMargin\$f\$dclDocType\$(\d+)"[^>]*value="([^"]*)"')
_TOTAL_RE = re.compile(r'SearchCriteriaTop_TotalRows"[^>]*>(?:<b>)?(\d+)')
_ROW_SPLIT_RE = re.compile(
    r'(?=<a href="\./SearchResults\.aspx\?global_id=OPR\d+&(?:amp;)?type=dtl">)')
_INST_RE = re.compile(
    r'global_id=(OPR\d+)&(?:amp;)?type=dtl">\s*([^<]+)</a>')
_ROWDATE_RE = re.compile(r'val:&quot;(\d{4})~(\d{1,2})~(\d{1,2})~')
_CODE_RE = re.compile(r'val:&quot;(' + "|".join(DOC_CODES) + r')&quot;')
_TOR_RE = re.compile(r'lblTorType"[^>]*>\[(R|E)\]</span>\s*<span[^>]*lblTor">([^<]*)')
_TEE_RE = re.compile(r'lblTeeType"[^>]*>\[(R|E)\]</span>\s*<span[^>]*lblTee">([^<]*)')

# empty text fields the WebForms POST must carry (Infragistics inputs post
# plain underscore names, not the ctl00$ unique-id path)
_TEXT_FIELDS = (
    "txtParty", "txtGrantor", "txtGrantee", "txtInstrumentNoFrom",
    "txtInstrumentNoTo", "txtBook", "txtPage", "DataTextEdit1",
    "txtLDLot", "txtLDBook", "txtLDSection", "txtLDStreetAddress",
    "txtLDFreeForm", "txtLDVolume", "txtLDPage", "txtLDMapcase", "txtLDSlide",
)


def _ig_date(d):
    """Infragistics WebDatePicker clientState for a datetime.date (verified:
    the '09' date prefix + ISO yyyy-mm-dd, identical value and JSON tail)."""
    v = f"09{d.isoformat()}"
    return f'|0|{v}||[[[[]],[],[]],[{{}},[]],"{v}"]'


def _clean_party(name):
    """Strip the '(+)' other-names indicator artifacts and whitespace."""
    return re.sub(r"\s*\(\+\)\s*$", "", name.replace("?", " ").strip()).strip()


def parse_results_page(html):
    """Parse one SearchResults.aspx page into raw record dicts."""
    records = []
    for block in _ROW_SPLIT_RE.split(html)[1:]:
        inst = _INST_RE.search(block)
        if not inst:
            continue
        dm = _ROWDATE_RE.search(block)
        file_date = ""
        if dm:
            file_date = f"{int(dm.group(1)):04d}-{int(dm.group(2)):02d}-{int(dm.group(3)):02d}"
        cm = _CODE_RE.search(block)
        grantors, grantees = [], []
        for regex in (_TOR_RE, _TEE_RE):
            m = regex.search(block)
            if m:
                name = _clean_party(m.group(2))
                if not name:
                    continue
                (grantors if m.group(1) == "R" else grantees).append(name)
        records.append({
            "global_id": inst.group(1),
            "instrument_no": inst.group(2).strip(),
            "file_date": file_date,
            "doc_code": cm.group(1) if cm else "",
            "grantors": grantors,
            "grantees": grantees,
        })
    return records


class Collector(BaseCollector):
    avenue = AVENUE
    source_id = SOURCE_ID
    metros = ("houston",)

    # -- HTTP ----------------------------------------------------------------
    # common/http.fetch() is GET-only and stateless; this WebForms flow needs a
    # cookie session + POST, so requests is used directly (same UA/timeout as
    # common.http, courtesy sleep per request). Public index, no secrets.

    def _get_session(self):
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        return s

    def _search(self, session, d_from, d_to):
        """Fresh GET (viewstate + doc-type indices) then the search POST.

        Returns (records_page1, total_rows, session). Retries with a fresh
        session on transport errors.
        """
        last_exc = None
        for attempt in range(MAX_ATTEMPTS):
            try:
                time.sleep(COURTESY_SLEEP)
                r0 = session.get(SEARCH_URL, timeout=TIMEOUT)
                r0.raise_for_status()
                hidden = {m.group(1): (m.group(2) or "")
                          for m in _HIDDEN_RE.finditer(r0.text)}
                if "__VIEWSTATE" not in hidden:
                    raise requests.RequestException("no __VIEWSTATE on GET")
                am = _ACTION_RE.search(r0.text)
                if not am:
                    raise requests.RequestException("no form action on GET")
                action = urljoin(SEARCH_URL, am.group(1))
                doc_idx = {code: idx for idx, code
                           in _DOCTYPE_IDX_RE.findall(r0.text)}
                missing = [c for c in DOC_CODES if c not in doc_idx]
                if missing:
                    raise requests.RequestException(
                        f"doc-type checkboxes missing from form: {missing}")

                form = dict(hidden)
                for f in _TEXT_FIELDS:
                    form[f"cphNoMargin_f_{f}"] = ""
                form["ctl00$cphNoMargin$f$NameSearchMode"] = "rdoCombine"
                form["ctl00$cphNoMargin$f$drbPartyType"] = ""
                for code in DOC_CODES:
                    form[f"ctl00$cphNoMargin$f$dclDocType${doc_idx[code]}"] = code
                form["cphNoMargin_f_ddcDateFiledFrom_clientState"] = _ig_date(d_from)
                form["cphNoMargin_f_ddcDateFiledTo_clientState"] = _ig_date(d_to)
                # satisfy page-level login RequiredFieldValidators only —
                # btnLogon is never the postback target, no logon happens
                form["LoginForm1_txtLogonName"] = "x"
                form["LoginForm1_txtPassword"] = "x"
                form["ctl00$LoginForm1$logonType"] = "rdoPubCpu"
                form["__EVENTTARGET"] = "ctl00$cphNoMargin$SearchButtons1$btnSearch"
                form["__EVENTARGUMENT"] = "0"

                r1 = session.post(action, data=form, timeout=120)
                r1.raise_for_status()
                if "SearchResults.aspx" not in r1.url:
                    raise requests.RequestException(
                        f"search did not reach results page (landed {r1.url})")
                tm = _TOTAL_RE.search(r1.text)
                total = int(tm.group(1)) if tm else 0
                return parse_results_page(r1.text), total, session
            except requests.RequestException as exc:
                last_exc = exc
                session = self._get_session()
                time.sleep(2.0 * (attempt + 1))
        raise last_exc

    def _fetch_window(self, session, d_from, d_to):
        """One search + all result pages. Returns (records, total, session)."""
        records, total, session = self._search(session, d_from, d_to)
        pages = min(math.ceil(total / ROWS_PER_PAGE),
                    RESULT_CAP // ROWS_PER_PAGE)
        for pg in range(2, pages + 1):
            time.sleep(COURTESY_SLEEP)
            r = session.get(RESULTS_URL, params={"pg": pg}, timeout=120)
            r.raise_for_status()
            records.extend(parse_results_page(r.text))
        return records, total, session

    def _collect_range(self, session, d_from, d_to, notes, errors):
        """Chunked + cap-splitting search over [d_from, d_to].

        Capped multi-day chunks are re-queried as single days. A capped single
        day cannot be split — accepted with a truncation note (liens_harris
        pattern). A chunk that fails after retries is recorded in `errors`
        and skipped, so one bad window does not lose the whole run.
        Returns (records, chunks_ok).
        """
        out = []
        chunks_ok = 0
        stack = []
        cur = d_from
        while cur <= d_to:
            end = min(cur + timedelta(days=CHUNK_DAYS - 1), d_to)
            stack.append((cur, end))
            cur = end + timedelta(days=1)
        while stack:
            a, b = stack.pop(0)
            try:
                records, total, session = self._fetch_window(session, a, b)
            except Exception as exc:
                errors.append(f"{a.isoformat()}..{b.isoformat()}: "
                              f"{type(exc).__name__}: {exc}")
                session = self._get_session()
                continue
            chunks_ok += 1
            if total >= RESULT_CAP and a != b:
                stack[0:0] = [(a + timedelta(days=i),) * 2
                              for i in range((b - a).days + 1)]
                continue
            if total >= RESULT_CAP:
                notes.append(f"{a.isoformat()} capped at {RESULT_CAP} rows "
                             f"(single day, truncated)")
            out.extend(records)
        return out, chunks_ok

    # -- signal emission -------------------------------------------------------

    def _emit(self, store, record, since):
        """Emit 0+ Signals for one raw record. Returns (added, entity_keys)."""
        try:
            fdate = date.fromisoformat(record["file_date"])
        except (ValueError, TypeError):
            return 0, set()
        if fdate < since:
            return 0, set()
        code = record["doc_code"]
        if code not in CODE_MAP:
            return 0, set()
        signal_type, lien_kind, magnitude = CODE_MAP[code]
        if code == "LIEN":
            lien_kind, magnitude = classify_lien(record["grantors"])

        debtors = [g for g in record["grantees"] if looks_business(g)]
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
                source_ref=record["instrument_no"],
                raw=dict(record),
                attrs={
                    "lien_kind": lien_kind,
                    "claimant": claimant,
                    "county": "FORT BEND",
                    "instrument_type": code,
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
            seen_ids = set()
            records, chunks_ok = self._collect_range(
                session, since, today, notes, errors)
            if not chunks_ok:
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       "; ".join(errors) or "all chunks failed")
            for rec in records:
                if rec["global_id"] in seen_ids:
                    continue
                seen_ids.add(rec["global_id"])
                added, keys = self._emit(store, rec, since)
                total_added += added
                entities |= keys
            status = "OK" if total_added else "EMPTY"
            return CollectorResult(self.source_id, total_added, len(entities),
                                   status, "; ".join(errors + notes))
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
    by_kind = Counter(json.loads(s["attrs"]).get("lien_kind", "?") for s in sigs)
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
