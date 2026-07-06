"""BizQuest dead-listings collector (avenue: dead_listings).

SHIPPED enabled:false — DUPLICATE INVENTORY. BizQuest is a CoStar skin of
BizBuySell: its card ids are literally the BizBuySell numeric ids with a BW
prefix (BW2511364 == bbs:2511364, verified live 2026-07-05/06; Houston counts
match). With listings_bizbuysell already live, enabling this collector buys
near-zero incremental data while spending Bright Data unlocker credits on
every page. It exists so the avenue can flip it on if BizBuySell ever blocks
harder than BizQuest, and it ALWAYS keys entities as bbs:{numeric_id} so any
signals it emits dedup/stack against listings_bizbuysell instead of double
counting.

Access: brightdata_unlock ONLY (plain GET = 403 Akamai). Verified live
2026-07-06 via common.http.brightdata_unlock: 1.03MB HTML, parseable
server-side. Search URLs:
    https://www.bizquest.com/businesses-for-sale-in-houston-tx/   (428 listings)
    https://www.bizquest.com/businesses-for-sale-in-atlanta-ga/   (183)
Pagination: {base}page-2/, page-3/, ... WARNING: wrong-guess URLs soft-404 to
the homepage (aspxerrorpath) — every fetch validates it parsed real cards.

Parse strategies (Angular app but server-rendered; NO serverApp-state unlike
BizBuySell):
    1. ld+json SearchResultsPage block: about[].item = Product with name, url
       (/business-for-sale/{slug}/BW{id}/), productId, offers.price (richest —
       57 products on the live Houston page).
    2. card anchors: <a ... title="{title}" href=".../BW{id}/"> + first $price
       inside the anchor's card window.

Broker: on the detail page only ('Contact Broker' CTA on card). Detail pages
were NOT probed (unlocker spend on a disabled collector), so detail-page
broker enrichment is disabled here (detail_fetch_cap=0); revisit if enabled.

Days-on-market: weekly snapshot diff keyed on the numeric id via
collectors._listings_common.diff_and_emit. Cross-site dedupe via
CrossSiteDeduper (trivially collapses onto bbs: entities by shared id).

Entity key: "bbs:{numeric_id}" — BizBuySell's id space, BW prefix stripped.

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_bizquest --self-test
Offline parser regression + shared synthetic exercise + a real (unlocker,
1 page per metro to cap spend) collect into a throwaway store. Writes NOTHING
to the sheet; saves fixtures/listings_bizquest_sample.json.
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
    ListingSiteCollector, parse_price, synthetic_exercise, run_live_self_test,
    unlock_with_retry)

SOURCE_ID = "listings_bizquest"
MAX_PAGES = 3                    # unlocker requests cost money; ~47 cards/page

SEARCH_URLS = {
    "houston": "https://www.bizquest.com/businesses-for-sale-in-houston-tx/",
    "atlanta": "https://www.bizquest.com/businesses-for-sale-in-atlanta-ga/",
}

_LDJSON_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
_BW_URL_RE = re.compile(r"/business-for-sale/[^/\"]+/BW(\d{5,9})/")
_A_TAG_RE = re.compile(r"<a\b[^>]*>")
_HREF_RE = re.compile(
    r'href="((?:https?://www\.bizquest\.com)?/business-for-sale/[^"]+/BW(\d{5,9})/)"')
_TITLE_ATTR_RE = re.compile(r'title="([^"]*)"')
_PRICE_RE = re.compile(r"\$\s?([\d,]{6,})")
_SOFT404_MARKERS = ("aspxerrorpath", "Access Denied")

_WS_RE = re.compile(r"\s+")


def _clean(s):
    return _WS_RE.sub(" ", html_lib.unescape(s or "")).strip()


def parse_listings(page_html):
    """Parse one search-results page. Returns {numeric_id: listing dict}."""
    listings = {}

    # -- strategy 1: ld+json SearchResultsPage Products -------------------
    for block in _LDJSON_RE.findall(page_html):
        try:
            data = json.loads(re.sub(r"[\x00-\x1f]", " ", block.strip()))
        except (TypeError, ValueError):
            continue
        if not isinstance(data, dict) or data.get("@type") != "SearchResultsPage":
            continue
        for li in data.get("about", []):
            item = li.get("item") if isinstance(li, dict) else None
            if not isinstance(item, dict):
                continue
            url = str(item.get("url") or "")
            m = _BW_URL_RE.search(url)
            lid = m.group(1) if m else str(item.get("productId") or "")
            if not lid.isdigit():
                continue
            offers = item.get("offers") or {}
            price = parse_price(offers.get("price")
                                if isinstance(offers, dict) else None)
            title = _clean(item.get("name") or "")
            if not title or price is None:
                continue
            listings[lid] = {
                "listing_id": lid,
                "title": title,
                "asking_price": price,
                "url": url,
                "broker": "",
                "location": "",
                "cash_flow": None,
                "parse_strategy": "ld_json",
            }

    # -- strategy 2: card anchors + nearby price ---------------------------
    for m in _A_TAG_RE.finditer(page_html):
        tag = m.group(0)
        hm = _HREF_RE.search(tag)
        tm = _TITLE_ATTR_RE.search(tag)
        if not hm or not tm:
            continue
        lid = hm.group(2)
        if lid in listings:
            continue
        window = page_html[m.start():m.start() + 3500]
        pm = _PRICE_RE.search(window)
        if not pm:
            continue
        price = parse_price(pm.group(1))
        if price is None:
            continue
        path = hm.group(1)
        url = path if path.startswith("http") else f"https://www.bizquest.com{path}"
        listings[lid] = {
            "listing_id": lid,
            "title": _clean(tm.group(1)),
            "asking_price": price,
            "url": url,
            "broker": "",
            "location": "",
            "cash_flow": None,
            "parse_strategy": "anchor",
        }
    return listings


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "bbs"              # BizBuySell id space — see module docstring
    requires_brightdata = True
    detail_fetch_cap = 0        # detail markup unprobed; collector disabled
    max_pages = MAX_PAGES

    def _fetch_metro_listings(self, metro):
        base = SEARCH_URLS[metro]
        found = {}
        for page in range(1, self.max_pages + 1):
            url = base if page == 1 else f"{base}page-{page}/"
            page_html = unlock_with_retry(url)
            page_listings = parse_listings(page_html)
            if not page_listings and any(mk in page_html
                                         for mk in _SOFT404_MARKERS):
                raise RuntimeError(
                    f"soft-404/homepage redirect on {url} — URL scheme changed?")
            new = {k: v for k, v in page_listings.items() if k not in found}
            found.update(page_listings)
            if not new:
                break               # ran past the last page
        return found


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

# Real shapes captured live 2026-07-06 from the Houston page (trimmed):
# an ld+json SearchResultsPage with two real Products + one anchor-only card.
_PARSER_FIXTURE_HTML = """
<script type="application/ld+json">
{"@context": "http://schema.org", "@type": "SearchResultsPage",
 "about": [
  {"@type": "ListItem", "position": 0, "item": {"@type": "Product",
    "name": "Fully Equipped Indian Restaurant for sale on State Highway 249",
    "description": "Well Established Turn key Indian Restaurant",
    "url": "https://www.bizquest.com/business-for-sale/fully-equipped-indian-restaurant-for-sale-on-state-highway-249/BW2525530/",
    "productId": "2525530",
    "offers": {"@type": "Offer", "price": 98000, "priceCurrency": "USD"}}},
  {"@type": "ListItem", "position": 1, "item": {"@type": "Product",
    "name": "Profitable Turnkey Active Freight Trucking Company - Active Amazon R.",
    "url": "https://www.bizquest.com/business-for-sale/profitable-turnkey-active-freight-trucking-company-active-amazon-r/BW2511364/",
    "productId": "2511364",
    "offers": {"@type": "Offer", "price": 1350000, "priceCurrency": "USD"}}}
 ]}
</script>
<app-listing-diamond><a applistingclick class="diamond"
 title="Established Dog Daycare &amp; Boarding - Houston" id="2516196"
 href="/business-for-sale/established-dog-daycare-and-boarding-houston/BW2516196/">
 <div class="text"><p class="asking-price"><span></span> $2,100,000 <span></span></p>
 <h3 class="title">Established Dog Daycare &amp; Boarding - Houston</h3>
 <p class="location"><a href="/businesses-for-sale-in-houston-tx/">Houston</a>, TX</p>
 </div></a></app-listing-diamond>
"""


def _parser_regression():
    parsed = parse_listings(_PARSER_FIXTURE_HTML)
    assert len(parsed) == 3, f"parser found {len(parsed)} of 3 listings"
    a = parsed["2511364"]                              # the shared-id proof
    assert a["asking_price"] == 1_350_000, a
    assert a["parse_strategy"] == "ld_json", a
    b = parsed["2516196"]
    assert b["asking_price"] == 2_100_000, b
    assert b["parse_strategy"] == "anchor", b
    assert b["title"].startswith("Established Dog Daycare"), b
    in_band = [l for l in parsed.values()
               if 1_000_000 <= l["asking_price"] <= 10_000_000]
    assert len(in_band) == 2, in_band
    print(f"  parser regression: {len(parsed)} listings (ld_json + anchor), "
          f"{len(in_band)} in $1M-$10M band; BW2511364 -> id 2511364 "
          f"(= bbs entity)  OK")
    return a


def _self_test():
    print(f"[{SOURCE_ID}] --self-test")
    sample = _parser_regression()
    by_type = synthetic_exercise(Collector())
    live = Collector()
    live.max_pages = 1              # cap unlocker spend during self-test
    result = run_live_self_test(live, SOURCE_ID, sample,
                                synthetic_counts=by_type)
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="offline parser regression + synthetic snapshot "
                             "exercise + live 30-day collect (1 unlocker page "
                             "per metro) into a throwaway store; writes only "
                             "fixtures/<source_id>_sample.json")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    parser.print_help()
