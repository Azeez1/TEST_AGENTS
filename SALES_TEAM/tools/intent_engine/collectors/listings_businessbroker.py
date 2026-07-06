"""BusinessBroker.net dead-listings collector (avenue: dead_listings).

Independent inventory, PLAIN fetch (no unlocker). Verified live 2026-07-06:
    https://www.businessbroker.net/city/houston-tx-businesses-for-sale.aspx
    https://www.businessbroker.net/city/atlanta-ga-businesses-for-sale.aspx
23 listings/page, pagination ?page=2..N. Old ASP.NET site but the city pages
are plain GETs — no viewstate needed for search results (unlike liens_harris).
No usable price URL param exists, so the $1M-$10M band is filtered client-side
(the ListingSiteCollector base does that from parsed asking_price).

Card anatomy (server-rendered, captured live):
    <div class="result-item listing" id="listing_998841" data-invest="00319000"
         data-fbo="998841" ...>
      <a href="/business-for-sale/{slug}/{id}.aspx">...
        <span>Asking Price: $319,000</span></a>
      <h3>title</h3>
      <div class="location">Houston, TX</div><div class="location">Harris County</div>
      <div class="financials"><span>Cash Flow</span> $300,000</div>
data-invest is the asking price zero-padded (fallback parse path).

Broker: NOT on the card. Bounded detail-page enrichment parses the detail
page's JSON-LD (LocalBusiness with founder Person = the listing agent, plus
broker email/phone — verified live 2026-07-06, note the JSON needs
control-character cleanup before json.loads).

Days-on-market: weekly snapshot diff keyed on the numeric listing id via
collectors._listings_common.diff_and_emit (stale_180d / price_cut / relisting,
same semantics as listings_bizbuysell). Cross-site dedupe via CrossSiteDeduper.

Entity key: "bbn:{listing_id}" (or the canonical cross-site key on exact match).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_businessbroker --self-test
Offline parser regression + shared synthetic snapshot exercise + real collect()
into a throwaway store. Writes NOTHING to the sheet; saves
fixtures/listings_businessbroker_sample.json.
"""
import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, parse_price, synthetic_exercise, run_live_self_test)
from common.http import fetch  # noqa: E402

SOURCE_ID = "listings_businessbroker"
MAX_PAGES = 4                    # 23 cards/page; the $1M-$10M band is a thin slice

CITY_URLS = {
    "houston": "https://www.businessbroker.net/city/houston-tx-businesses-for-sale.aspx",
    "atlanta": "https://www.businessbroker.net/city/atlanta-ga-businesses-for-sale.aspx",
}

_BLOCK_SPLIT_RE = re.compile(r'<div class="result-item listing"')
_ID_RE = re.compile(r'data-fbo="(\d+)"')
_ID_FALLBACK_RE = re.compile(r'id="listing_(\d+)"')
_TITLE_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_ASKING_RE = re.compile(r"Asking Price:\s*\$([\d,]+)")
_INVEST_RE = re.compile(r'data-invest="(\d+)"')
_HREF_RE = re.compile(r'href="(/business-for-sale/[^"]+/(\d{5,8})\.aspx)"')
_LOCATION_RE = re.compile(r'<div class="location">([^<]*)</div>')
_CASHFLOW_RE = re.compile(r"<span>Cash Flow</span>\s*([^<]+)")
_LDJSON_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
_FOUNDER_FALLBACK_RE = re.compile(
    r'"founder"\s*:\s*{\s*"@type"\s*:\s*"Person"\s*,\s*"name"\s*:\s*"([^"]+)"')

_WS_RE = re.compile(r"\s+")


def _clean(s):
    return _WS_RE.sub(" ", html_lib.unescape(s or "")).strip()


def parse_listings(page_html):
    """Parse one city results page. Returns {listing_id: listing dict}."""
    listings = {}
    for block in _BLOCK_SPLIT_RE.split(page_html)[1:]:
        im = _ID_RE.search(block[:400]) or _ID_FALLBACK_RE.search(block[:400])
        tm = _TITLE_RE.search(block)
        if not im or not tm:
            continue
        lid = im.group(1)
        price = None
        pm = _ASKING_RE.search(block)
        if pm:
            price = parse_price(pm.group(1))
        if price is None:
            vm = _INVEST_RE.search(block[:400])
            if vm:
                n = int(vm.group(1).lstrip("0") or "0")
                price = n if n > 0 else None
        hm = _HREF_RE.search(block)
        url = f"https://www.businessbroker.net{hm.group(1)}" if hm else ""
        locs = [_clean(x) for x in _LOCATION_RE.findall(block) if _clean(x)]
        cm = _CASHFLOW_RE.search(block)
        listings[lid] = {
            "listing_id": lid,
            "title": _clean(tm.group(1)),
            "asking_price": price,
            "url": url,
            "broker": "",
            "location": " | ".join(locs),
            "cash_flow": parse_price(_clean(cm.group(1))) if cm else None,
            "parse_strategy": "result_item",
        }
    return listings


def parse_detail_broker(page_html):
    """Broker agent name (+ firm contact) from the detail page's JSON-LD."""
    for block in _LDJSON_RE.findall(page_html or ""):
        try:
            data = json.loads(re.sub(r"[\x00-\x1f]", " ", block.strip()))
        except (TypeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        founder = data.get("founder")
        if isinstance(founder, dict) and founder.get("name"):
            return _clean(str(founder["name"]))
    m = _FOUNDER_FALLBACK_RE.search(page_html or "")
    return _clean(m.group(1)) if m else ""


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "bbn"

    def _fetch_metro_listings(self, metro):
        base = CITY_URLS[metro]
        found = {}
        for page in range(1, MAX_PAGES + 1):
            params = None if page == 1 else {"page": page}
            resp = fetch(base, params=params)
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

# Real card shapes captured live 2026-07-06 from the Houston city page, trimmed.
_PARSER_FIXTURE_HTML = """
<div class="result-item listing" id="listing_1005572" data-rate="" data-invest="00073000" data-name="Turnkey Pet Supply Amazon FBA Store Fully Managed" data-id="17" data-fbo="1005572" data-order="0000"><a class="anchor"></a><div class="item ">
<a class="" href="/business-for-sale/turnkey-pet-supply-amazon-fba-store-fully-managed-houston-texas/1005572.aspx"><div class="result-img">
<span>Asking Price: $73,000</span></div>
<h3 class="">Turnkey Pet Supply Amazon FBA Store Fully Managed</h3>
<div class="location">Houston, TX</div><div class="location">Harris County</div>
<p class="summary ">This turnkey pet supply Amazon FBA store ...</p></a>
<div class="listing-financials"><div class="financials"><span>Cash Flow</span> $300,000</div><div class="financials"><span>Revenue</span> $275,000</div></div>
</div></div>
<div class="result-item listing" id="listing_998841" data-rate="" data-invest="00319000" data-name="Bring your offers" data-id="17" data-fbo="998841" data-order="0000"><a class="anchor"></a><div class="item ">
<a class="" href="/business-for-sale/marcos-and-pizza-franchise-houston-texas/998841.aspx"><div class="result-img">
<span>Asking Price: $319,000</span></div>
<h3 class="">Bring your offers for this Houston area Marco&#039;s Pizza for sale!</h3>
<div class="location">Houston, TX</div><div class="location">Harris County</div></a>
<div class="listing-financials"><div class="financials"><span>Cash Flow</span> Not Disclosed</div><div class="financials"><span>Revenue</span> $530,000</div></div>
</div></div>
<div class="result-item listing" id="listing_1010489" data-invest="01400000" data-fbo="1010489"><div class="item ">
<a class="" href="/business-for-sale/precision-machine-shop-houston-texas/1010489.aspx"><div class="result-img">
<span>Asking Price: $1,400,000</span></div>
<h3 class="">Precision Machine Shop with Long-Term Contracts</h3>
<div class="location">Houston, TX</div><div class="location">Harris County</div></a>
<div class="listing-financials"><div class="financials"><span>Cash Flow</span> $450,000</div></div>
</div></div>
"""

# Real detail-page JSON-LD shape captured live 2026-07-06 (trimmed).
_DETAIL_FIXTURE_HTML = """
<script type="application/ld+json">
{ "@context": "https://schema.org", "@type": "LocalBusiness",
  "name": "Bring your offers for this Houston area Marco&amp;#039;s Pizza for sale!",
  "description": "This highly motivated seller...",
  "email": "inquiry@wesellrestaurants.com", "telephone": "+1-832-473-7164",
  "founder": { "@type": "Person", "name": "Tamara Hamilton" } }
</script>
"""


def _parser_regression():
    parsed = parse_listings(_PARSER_FIXTURE_HTML)
    assert len(parsed) == 3, f"parser found {len(parsed)} of 3 cards"
    a = parsed["1005572"]
    assert a["asking_price"] == 73_000 and a["cash_flow"] == 300_000, a
    b = parsed["998841"]
    assert b["asking_price"] == 319_000 and b["cash_flow"] is None, b
    assert "Marco's Pizza" in b["title"], b
    c = parsed["1010489"]
    assert c["asking_price"] == 1_400_000, c
    assert c["url"].endswith("/1010489.aspx"), c
    in_band = [l for l in parsed.values()
               if l["asking_price"] and 1_000_000 <= l["asking_price"] <= 10_000_000]
    assert len(in_band) == 1, in_band
    broker = parse_detail_broker(_DETAIL_FIXTURE_HTML)
    assert broker == "Tamara Hamilton", broker
    print(f"  parser regression: {len(parsed)} cards parsed, {len(in_band)} in "
          f"$1M-$10M band, detail broker '{broker}'  OK")
    return c


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
