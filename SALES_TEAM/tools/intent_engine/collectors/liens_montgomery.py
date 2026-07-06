"""Montgomery County (TX) Clerk lien/judgment collector (avenue: pe_distress).

Source: https://montgomery.tx.publicsearch.us (Kofile/Neumo "publicsearch.us")
Search URL pattern (verified live 2026-07-06 in a real browser):
    /results?department=RP&limit=50&offset=0&searchType=advancedSearch
        &docTypes=<CODE>[,<CODE>...]&recordedDateRange=YYYYMMDD,YYYYMMDD
The result records are embedded as JSON inside `window.__data` in the SSR
HTML document (no separate XHR). Free public search + index metadata; only
document-image download / bulk export requires sign-in.

DISABLED (enabled:false in signal_registry.json) — WHY, verified 2026-07-06:
    curl/requests AND Bright Data Web Unlocker receive only the JS loading
    shell (title "Loading Search Results...") — bot detection keyed on the
    TLS/JA3 fingerprint, not cookies (a real Chrome gets the SSR JSON with
    credentials omitted; there is no captcha). Bright Data
    scrape_as_markdown is additionally robots.txt-blocked for this host
    ("not available for immediate access mode"). A collector fetch therefore
    needs a browser-fingerprinted path (Chrome MCP session or headless
    Chromium) which is not wired into the engine yet. NOT paywalled, NOT
    captcha-walled — re-enable once a browser-driven fetch exists.

Doc-type codes MATCH the Harris taxonomy (pulled from the live 154-entry
docTypeMappings): A/J=ABSTRACT OF JUDGMENT, J=JUDGMENT, FTL=FEDERAL TAX LIEN,
STL=STATE TAX LIEN, M/L=MECHANIC LIEN, L/P=LIS PENDENS. (FTLP personal federal
tax liens, H/L hospital and C/L child-support liens target individuals, not
business distress — intentionally excluded.) Verified live sample:
docTypes=FTL over 04/01-07/06/2026 returned 146 records, Grantor=INTERNAL
REVENUE, Grantee=debtor businesses (SB AND K BENEFITS, ELLIOTT OIL AND GAS,
US ONCOLOGY INC) — grantee is the debtor, same role convention as
liens_harris/liens_fortbend. The index exposes no address: zip is empty,
entity_key "biz:{name_norm}|".

collect() still attempts honestly (one plain GET, then one Bright Data
unlock) so the block is re-checked on every self-test; when both return the
shell it reports ERROR with the bot-block message — it never fakes data.
The window.__data parser below is exercised offline against an embedded
format-regression fixture so the wiring work later is parse-ready.

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_montgomery --self-test
Runs the offline parser regression plus one live attempt into a throwaway
in-memory store; writes NOTHING to the sheet; saves
fixtures/liens_montgomery_sample.json documenting the live status.
"""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._liens_common import classify_lien, looks_business  # noqa: E402
from common.http import brightdata_unlock, fetch  # noqa: E402
from common.normalize import entity_key as biz_entity_key  # noqa: E402

SOURCE_ID = "liens_montgomery"
AVENUE = "pe_distress"

BASE_URL = "https://montgomery.tx.publicsearch.us/results"
PAGE_LIMIT = 50

# code -> (signal_type, lien_kind, magnitude); M/L classified per record
CODE_MAP = {
    "A/J": ("judgment_filed", "abstract_of_judgment", 1.0),
    "J": ("judgment_filed", "judgment", 1.0),
    "FTL": ("lien_filed", "federal_tax_lien", 1.0),
    "STL": ("lien_filed", "state_tax_lien", 1.0),
    "M/L": ("lien_filed", None, None),      # classify by claimant
    "L/P": ("lien_filed", "lis_pendens", 0.6),
}
DOC_CODES = tuple(CODE_MAP)

_SHELL_RE = re.compile(r"Loading Search Results", re.I)
_DATA_RE = re.compile(r"window\.__data\s*=\s*(\{.*?\})\s*;?\s*</script>", re.S)

BLOCK_MSG = (
    "bot-blocked: montgomery.tx.publicsearch.us returns only the JS loading "
    "shell to non-browser TLS fingerprints (plain requests AND Bright Data "
    "Web Unlocker; scrape_as_markdown robots-blocked). Needs a "
    "browser-fingerprinted fetch (Chrome MCP / headless Chromium) — see "
    "module docstring. No captcha, not paywalled."
)


def build_url(codes, d_from, d_to, offset=0):
    """Advanced-search results URL for a date window + doc-type codes."""
    return (f"{BASE_URL}?department=RP&limit={PAGE_LIMIT}&offset={offset}"
            f"&searchType=advancedSearch"
            f"&docTypes={quote(','.join(codes), safe='')}"
            f"&recordedDateRange={d_from.strftime('%Y%m%d')},"
            f"{d_to.strftime('%Y%m%d')}")


def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _as_names(v):
    """Coerce a party field (list of strings/dicts, or string) to [names]."""
    if v is None:
        return []
    if isinstance(v, str):
        return [v.strip()] if v.strip() else []
    if isinstance(v, dict):
        n = v.get("name") or v.get("fullName") or ""
        return [n.strip()] if n.strip() else []
    if isinstance(v, list):
        out = []
        for item in v:
            out.extend(_as_names(item))
        return out
    return []


def parse_results(html):
    """Parse a publicsearch.us SSR results document into raw record dicts.

    Returns (records, is_shell): is_shell=True means the anti-bot loading
    shell came back instead of server-rendered data. Field names are matched
    flexibly (docType/documentType, recordedDate/recordDate, grantors/
    grantee variants) since the exact SSR key casing may shift between
    deployments.
    """
    if _SHELL_RE.search(html):
        return [], True
    m = _DATA_RE.search(html)
    if not m:
        return [], True
    try:
        data = json.loads(m.group(1))
    except (ValueError, TypeError):
        return [], True
    records = []
    seen = set()
    for d in _walk(data):
        dtype = d.get("docType") or d.get("documentType")
        rdate = d.get("recordedDate") or d.get("recordDate")
        if not dtype or not rdate:
            continue
        docno = str(d.get("instrumentNumber") or d.get("documentNumber")
                    or d.get("docNumber") or d.get("id") or "")
        key = (docno, str(dtype), str(rdate))
        if not docno or key in seen:
            continue
        seen.add(key)
        records.append({
            "doc_number": docno,
            "doc_code": str(dtype).strip().upper(),
            "recorded_date": str(rdate)[:10],
            "grantors": _as_names(d.get("grantors") or d.get("grantor")),
            "grantees": _as_names(d.get("grantees") or d.get("grantee")),
        })
    return records, False


class Collector(BaseCollector):
    avenue = AVENUE
    source_id = SOURCE_ID
    metros = ("houston",)

    def _fetch_page(self, url):
        """Plain fetch first (free), Bright Data second. Returns html.

        Raises RuntimeError with BLOCK_MSG when only the shell comes back.
        """
        html = None
        try:
            html = fetch(url).text
        except Exception:
            html = None
        if html is not None and not _SHELL_RE.search(html):
            return html
        if config.get_env("BRIGHTDATA_API_TOKEN"):
            html = brightdata_unlock(url)
            if not _SHELL_RE.search(html):
                return html
        raise RuntimeError(BLOCK_MSG)

    def _emit(self, store, record, since):
        try:
            fdate = date.fromisoformat(record["recorded_date"])
        except (ValueError, TypeError):
            return 0, set()
        if fdate < since:
            return 0, set()
        code = record["doc_code"]
        if code not in CODE_MAP:
            return 0, set()
        signal_type, lien_kind, magnitude = CODE_MAP[code]
        if magnitude is None:
            lien_kind, magnitude = classify_lien(record["grantors"])
        debtors = [g for g in record["grantees"] if looks_business(g)]
        added = 0
        keys = set()
        for name in debtors:
            key = biz_entity_key(name, "")
            sig = Signal(
                entity_key=key,
                entity_name=name,
                metro="houston",
                avenue=self.avenue,
                signal_type=signal_type,
                signal_date=fdate.isoformat(),
                magnitude=magnitude,
                source_id=self.source_id,
                source_ref=record["doc_number"],
                raw=dict(record),
                attrs={
                    "lien_kind": lien_kind,
                    "claimant": record["grantors"][0] if record["grantors"] else "",
                    "county": "MONTGOMERY",
                    "instrument_type": code,
                },
            )
            if store.add_signal(sig):
                added += 1
            keys.add(key)
        return added, keys

    def collect(self, since, store, registry):
        try:
            today = date.today()
            total_added = 0
            entities = set()
            offset = 0
            while True:
                url = build_url(DOC_CODES, since, today, offset)
                try:
                    html = self._fetch_page(url)
                except Exception as exc:
                    if total_added:
                        break        # partial success, stop paging
                    return CollectorResult(self.source_id, 0, 0, "ERROR",
                                           str(exc))
                records, is_shell = parse_results(html)
                if is_shell:
                    return CollectorResult(self.source_id, 0, 0, "ERROR",
                                           BLOCK_MSG)
                for rec in records:
                    added, keys = self._emit(store, rec, since)
                    total_added += added
                    entities |= keys
                if len(records) < PAGE_LIMIT:
                    break
                offset += PAGE_LIMIT
            status = "OK" if total_added else "EMPTY"
            return CollectorResult(self.source_id, total_added, len(entities),
                                   status)
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

# FORMAT regression fixture (synthetic, clearly labeled): reconstructs the
# window.__data SSR shape from field observations verified live 2026-07-06
# (docTypes=FTL: Grantor=INTERNAL REVENUE, Grantee=debtor businesses). Used
# ONLY to prove the parser; never stored as real data.
_PARSER_FIXTURE_HTML = """<!doctype html><html><head><title>Search Results
</title></head><body><script>window.__data = {"search":{"searchResults":
{"results":[
 {"id":"9001","instrumentNumber":"2026-071001","docType":"FTL",
  "recordedDate":"2026-06-15","grantors":["INTERNAL REVENUE SERVICE"],
  "grantees":["SB AND K BENEFITS LLC"]},
 {"id":"9002","instrumentNumber":"2026-071002","docType":"A/J",
  "recordedDate":"2026-06-20","grantors":[{"name":"CAPITAL ONE NA"}],
  "grantees":[{"name":"ELLIOTT OIL AND GAS SERVICES INC"}]},
 {"id":"9003","instrumentNumber":"2026-071003","docType":"L/P",
  "recordedDate":"2026-06-25","grantors":["WOODLANDS LENDING LP"],
  "grantees":["JOHNSON MARY"]}
]}}};</script></body></html>"""

_SHELL_FIXTURE_HTML = ("<html><head><title>Loading Search Results...</title>"
                       "</head><body><div id='root'></div></body></html>")


def _parser_regression():
    from common.store import Store
    records, is_shell = parse_results(_PARSER_FIXTURE_HTML)
    assert not is_shell, "fixture wrongly detected as shell"
    assert len(records) == 3, f"parsed {len(records)} of 3 fixture records"
    assert records[0]["doc_code"] == "FTL", records[0]
    assert records[0]["grantees"] == ["SB AND K BENEFITS LLC"], records[0]
    _, shell2 = parse_results(_SHELL_FIXTURE_HTML)
    assert shell2, "loading shell not detected"

    # emission: FTL + A/J hit business grantees; L/P grantee is an individual
    store = Store(":memory:")
    c = Collector()
    since = date(2026, 6, 1)
    added = 0
    for rec in records:
        a, _ = c._emit(store, rec, since)
        added += a
    sigs = store.get_signals(avenue=AVENUE)
    by_type = Counter(s["signal_type"] for s in sigs)
    assert dict(by_type) == {"lien_filed": 1, "judgment_filed": 1}, by_type
    assert added == 2, added
    store.close()
    print(f"  parser regression: 3 records parsed, shell detected, "
          f"emission {dict(by_type)}  OK")


def _self_test(days=30):
    from common.store import Store
    print(f"[{SOURCE_ID}] --self-test  (offline parser regression + one live "
          f"attempt, last {days} days)")
    _parser_regression()

    since = date.today() - timedelta(days=days)
    registry = config.load_registry()
    store = Store(":memory:")
    result = Collector().collect(since, store, registry)
    sigs = store.get_signals(avenue=AVENUE)
    by_type = Counter(s["signal_type"] for s in sigs)
    sample = json.loads(sigs[0]["raw"]) if sigs else None
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture = {
        "source_id": SOURCE_ID,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "window_days": days,
        "enabled": False,
        "blocked_reason": BLOCK_MSG if result.status == "ERROR" else "",
        "note": ("raw record behind the first emitted signal" if sample else
                 "no live data; " + (result.error or result.status)
                 + " — parser proven against embedded format fixture"),
        "sample_record": sample,
        "signal_counts": dict(by_type),
        "search_url_example": build_url(
            DOC_CODES, since, date.today()),
    }
    fixture_path = fixtures_dir / f"{SOURCE_ID}_sample.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, default=str),
                            encoding="utf-8")

    print(f"  live attempt: status={result.status} "
          f"signals={result.signals_added} entities={result.entities_seen}")
    if result.error:
        print(f"  detail: {result.error}")
    print(f"  fixture saved: {fixture_path}")
    print(f"  RESULT: {result.status}")
    # ERROR is the EXPECTED honest outcome while the host bot-blocks
    # non-browser clients; the module ships enabled:false.
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="offline parser regression + one live attempt; "
                             "writes nothing but fixtures/<source_id>_sample.json")
    parser.add_argument("--days", type=int, default=30,
                        help="self-test lookback window (default 30)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test(args.days))
    parser.print_help()
