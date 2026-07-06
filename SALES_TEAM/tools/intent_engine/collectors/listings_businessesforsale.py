"""BusinessesForSale.com dead-listings collector (avenue: dead_listings).

Best independent (non-CoStar) inventory. PLAIN fetch — no Bright Data spend.
Server-side price filter VERIFIED live 2026-07-06:
    https://us.businessesforsale.com/us/search/businesses-for-sale-in-houston
        ?Price.From=1000000&Price.To=10000000&PriceDisclosedOnly=1
    (Houston 26 in-band, Atlanta 7). Pagination: ...-in-houston-2 suffix
    (kept as a guard; PageSize=100 fits each metro on one page today).

Cards are server-rendered tables: <h2><a href={detail}.aspx>title</a></h2>,
Location / Asking Price / Revenue / Cash Flow cells, stable numeric listing id
from the shortlist link (addListingId={id}). Asking Price is occasionally a
band like '$1M - $5M' — parsed to the midpoint (price_cut granularity is
coarser for those; raw text kept in price_display).

Broker: NOT on the card. A bounded, throttled detail-page fetch (cap
DETAIL_FETCH_CAP per metro, oldest listings first) parses the
'Listed by' <div class="broker-details"> block (verified live 2026-07-06).

Days-on-market: weekly snapshot diff keyed on the numeric listing id via
collectors._listings_common.diff_and_emit (same stale_180d / price_cut /
relisting semantics as listings_bizbuysell). Cross-site dedupe via
CrossSiteDeduper — a business also on BizBuySell resolves to its bbs: entity.

Entity key: "bfs:{listing_id}" (or the canonical cross-site key on exact match).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_businessesforsale --self-test
Offline parser regression against embedded real-format HTML + shared synthetic
snapshot exercise + a real collect() into a throwaway store. Writes NOTHING to
the sheet; saves fixtures/listings_businessesforsale_sample.json.
"""
import argparse
import html as html_lib
import re
import sys
from pathlib import Path

import requests

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, parse_price, synthetic_exercise, run_live_self_test,
    PRICE_MIN, PRICE_MAX)
from common.http import fetch  # noqa: E402

SOURCE_ID = "listings_businessesforsale"
MAX_PAGES = 3

SEARCH_URLS = {
    "houston": "https://us.businessesforsale.com/us/search/businesses-for-sale-in-houston",
    "atlanta": "https://us.businessesforsale.com/us/search/businesses-for-sale-in-atlanta",
}
SEARCH_PARAMS = {
    "Price.From": PRICE_MIN,
    "Price.To": PRICE_MAX,
    "PriceDisclosedOnly": 1,
    "PageSize": 100,
}

_BLOCK_SPLIT_RE = re.compile(r'<div class="result">')
_TITLE_RE = re.compile(
    r'<h2[^>]*>\s*<a href="(https://us\.businessesforsale\.com/us/[^"]+\.aspx)"\s*>'
    r'\s*(.*?)\s*</a>', re.S)
_ID_RE = re.compile(r'addListingId=(\d+)')
_LOCATION_RE = re.compile(r'Location:</th>\s*<td>\s*(.*?)\s*</td>', re.S)
_ASKING_RE = re.compile(r'Asking Price:</th>\s*<td>\s*(.*?)\s*</td>', re.S)
_CASHFLOW_RE = re.compile(r'Cash Flow:</th>\s*<td>\s*(.*?)\s*</td>', re.S)
_DETAIL_BROKER_RE = re.compile(
    r'class="broker-details".*?<h3>\s*Listed by:?\s*</h3>\s*<h4>\s*([^<]+?)\s*</h4>',
    re.S)

_WS_RE = re.compile(r"\s+")


def _clean(s):
    return _WS_RE.sub(" ", html_lib.unescape(s or "")).strip()


def parse_listings(page_html):
    """Parse one search-results page. Returns {listing_id: listing dict}."""
    listings = {}
    for block in _BLOCK_SPLIT_RE.split(page_html)[1:]:
        if "result-table" not in block:
            continue
        tm = _TITLE_RE.search(block)
        im = _ID_RE.search(block)
        if not tm or not im:
            continue
        lid = im.group(1)
        price_text = _clean(_ASKING_RE.search(block).group(1)) \
            if _ASKING_RE.search(block) else ""
        cash_text = _clean(_CASHFLOW_RE.search(block).group(1)) \
            if _CASHFLOW_RE.search(block) else ""
        listings[lid] = {
            "listing_id": lid,
            "title": _clean(tm.group(2)),
            "asking_price": parse_price(price_text),
            "price_display": price_text,
            "url": tm.group(1),
            "broker": "",
            "location": _clean(_LOCATION_RE.search(block).group(1))
            if _LOCATION_RE.search(block) else "",
            "cash_flow": parse_price(cash_text),
            "parse_strategy": "result_table",
        }
    return listings


def parse_detail_broker(page_html):
    m = _DETAIL_BROKER_RE.search(page_html or "")
    return _clean(m.group(1)) if m else ""


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "bfs"

    def _fetch_metro_listings(self, metro):
        base = SEARCH_URLS[metro]
        found = {}
        for page in range(1, MAX_PAGES + 1):
            url = base if page == 1 else f"{base}-{page}"
            try:
                resp = fetch(url, params=SEARCH_PARAMS)
            except requests.HTTPError as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if page > 1 and status == 404:
                    break           # past the last page (PageSize=100 usually
                                    # fits a metro on page 1)
                raise
            page_listings = parse_listings(resp.text)
            new = {k: v for k, v in page_listings.items() if k not in found}
            found.update(page_listings)
            if not new:
                break               # ran past the last page
        return found

    def _fetch_detail_html(self, url):
        return fetch(url).text

    def _parse_detail_broker(self, page_html):
        return parse_detail_broker(page_html)


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

# Real card shapes captured live 2026-07-06 (Houston filtered search), trimmed.
# Card 2 exercises the price-band parse path with a real band string.
_PARSER_FIXTURE_HTML = """
<div class="result">
 <table class="result-table"><caption class="tile"><div class="result-header">
  <h2 class="with-label-2">
   <a href="https://us.businessesforsale.com/us/premier-franchise-early-childhood-education-center-cypress-area.aspx">
    Premier Franchise Early Childhood Education Center/Cypress Area
   </a></h2></div></caption>
  <tbody class="pure-g">
   <tr class="t-loc pure-u-1"><th class="hid">Location:</th><td>
    Houston, Texas, US
   </td></tr>
   <tr class="result-middle-row"><th class="hid">Details:</th><td colspan="2">
    <table><tbody>
     <tr><th>Asking Price:</th><td>
$5,000,000                                                    </td></tr>
     <tr><th>Revenue:</th><td> $2,000,000 </td></tr>
     <tr><th>Cash Flow:</th><td> $475,000 </td></tr>
    </tbody></table>
   </td></tr>
  </tbody></table>
 <div class="bottom-cta"><div class="result-contact"><div class="save-listing">
  <a href="https://us.businessesforsale.com/us/search/businesses-for-sale-in-houston?shortlist=1&addListingId=3970513" class="shortlist-ajax cta">Save</a>
 </div>
 <a class="contact-seller cta" href="https://us.businessesforsale.com/us/premier-franchise-early-childhood-education-center-cypress-area/contact">Contact seller</a>
 </div></div>
</div>
<div class="result">
 <table class="result-table"><caption class="tile"><div class="result-header">
  <h2 class="with-label-2">
   <a href="https://us.businessesforsale.com/us/sw-houston-specialty-grocery-sba-financeable-for-sale.aspx">
    SW Houston Specialty Grocery SBA Financeable
   </a></h2></div></caption>
  <tbody class="pure-g">
   <tr class="t-loc pure-u-1"><th class="hid">Location:</th><td>
    Houston, Texas, US
   </td></tr>
   <tr><th>Asking Price:</th><td> $1M - $5M </td></tr>
   <tr><th>Cash Flow:</th><td> Not Disclosed </td></tr>
  </tbody></table>
 <div class="bottom-cta">
  <a href="https://us.businessesforsale.com/us/search/x?shortlist=1&addListingId=3966017" class="shortlist-ajax cta">Save</a>
 </div>
</div>
"""

_DETAIL_FIXTURE_HTML = """
<div class="broker-details">
 <div>
  <h3>Listed by</h3>
  <h4>The Barnett Capital Group</h4>
  <p class="agentsSearchPathLink"><a href="https://us.businessesforsale.com/us/agents/the-barnett-capital-group">View 39 The Barnett Capital Group listings</a></p>
 </div>
</div>
"""


def _parser_regression():
    parsed = parse_listings(_PARSER_FIXTURE_HTML)
    assert len(parsed) == 2, f"parser found {len(parsed)} of 2 cards"
    a = parsed["3970513"]
    assert a["asking_price"] == 5_000_000 and a["cash_flow"] == 475_000, a
    assert a["title"].startswith("Premier Franchise"), a
    b = parsed["3966017"]
    assert b["asking_price"] == 3_000_000, b       # $1M-$5M band -> midpoint
    assert b["price_display"] == "$1M - $5M", b
    assert b["cash_flow"] is None, b
    broker = parse_detail_broker(_DETAIL_FIXTURE_HTML)
    assert broker == "The Barnett Capital Group", broker
    print(f"  parser regression: {len(parsed)} cards + band price + "
          f"detail broker '{broker}'  OK")
    return a


def _self_test():
    print(f"[{SOURCE_ID}] --self-test")
    sample = _parser_regression()
    by_type = synthetic_exercise(Collector())
    result = run_live_self_test(Collector(), SOURCE_ID, sample,
                                synthetic_counts=by_type)
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="offline parser regression + synthetic snapshot "
                             "exercise + live 30-day collect into a throwaway "
                             "store; writes only fixtures/<source_id>_sample.json")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    parser.print_help()
