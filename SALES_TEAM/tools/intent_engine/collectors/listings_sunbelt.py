"""Sunbelt Network dead-listings collector (avenue: dead_listings).

Largest broker network = true broker-relationship play. PLAIN requests, no
unlocker. Two routes verified live 2026-07-06; this collector uses the AJAX
endpoint the site itself uses (no nonce required):
    POST https://www.sunbeltnetwork.com/wp-admin/admin-ajax.php
      action=sunbelt_filter_city, filterValue=, nameCity=houston|atlanta,
      nameState=texas|georgia, numberPaged=1..N  -> listing-card HTML fragment
Fallback when the AJAX route breaks: GET the results page
    https://www.sunbeltnetwork.com/business-search/business-results/
        city-{city}-state-{state}/
(same card markup, page 1 only).

Card anatomy (WordPress, captured live): <article> blocks with
    <a href=".../listing-details/{slug}-59450/"><h4 class="latestBusinesses__item--title">
    <span class="latestBusinesses__location">Houston, Texas</span>
    <strong class="latestBusinesses__item--rightPrice"> $1.600m </strong>
    values boxes: <strong>$258.5k</strong><span>Cash Flow</span>
Asking prices are abbreviated ('$1.600m', '$850k', '$258.5k') — parse_price
handles k/m; exact price lives on the detail page, so price_cut granularity is
coarser here. Detail URLs come in two shapes (both live):
    /{office-slug}/buy-a-business/listings/listing-details/{slug}-{id}/
    /business-search/business-details/{slug}-{id}/          (no office slug)
The office slug (e.g. houston-west-tx) identifies the Sunbelt office = broker
on the card; the agent's name is on the detail page ("Business Listed by"
box, verified live) and fills broker via the bounded detail-page enrichment
when the card carried no office slug.

Atlanta city-level inventory is small (~4 listings live) — honest but thin;
consider adding suburb cities in v2 if the avenue needs more Georgia volume.

Days-on-market: weekly snapshot diff keyed on the trailing numeric listing id
via collectors._listings_common.diff_and_emit (stale_180d / price_cut /
relisting). Cross-site dedupe via CrossSiteDeduper.

Entity key: "snb:{listing_id}" (or the canonical cross-site key on exact match).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_sunbelt --self-test
Offline parser regression + shared synthetic snapshot exercise + real collect()
into a throwaway store. Writes NOTHING to the sheet; saves
fixtures/listings_sunbelt_sample.json.
"""
import argparse
import html as html_lib
import re
import sys
import time
from pathlib import Path

import requests

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, parse_price, synthetic_exercise, run_live_self_test)
from common.http import TIMEOUT, USER_AGENT, fetch  # noqa: E402

SOURCE_ID = "listings_sunbelt"
MAX_PAGES = 4                    # 10 cards per AJAX page
COURTESY_SLEEP = 1.0             # seconds between AJAX POSTs

AJAX_URL = "https://www.sunbeltnetwork.com/wp-admin/admin-ajax.php"
METRO_CITY_STATE = {
    "houston": ("houston", "texas"),
    "atlanta": ("atlanta", "georgia"),
}
RESULTS_URL = ("https://www.sunbeltnetwork.com/business-search/"
               "business-results/city-{city}-state-{state}/")

_CARD_SPLIT_RE = re.compile(r"<article\b")
_TITLE_RE = re.compile(
    r'<a href="(https://www\.sunbeltnetwork\.com/[^"]*?'
    r'(?:listing-details|business-details)/[^"]*?-(\d{3,9})/)"\s*>'
    r'\s*<h4 class="latestBusinesses__item--title">\s*(.*?)\s*</h4>', re.S)
_LOCATION_RE = re.compile(
    r'latestBusinesses__location">\s*(.*?)\s*</span>', re.S)
_ASKING_RE = re.compile(r'rightPrice">\s*(.*?)\s*<', re.S)
_CASHFLOW_RE = re.compile(
    r"<strong>\s*([^<]+?)\s*</strong>\s*<span>Cash Flow</span>", re.S)
_OFFICE_RE = re.compile(r"sunbeltnetwork\.com/([a-z0-9\-]+)/buy-a-business")
_DETAIL_BROKER_RE = re.compile(
    r'Business Listed by.*?<h5 class="title">\s*([^<]+?)\s*</h5>'
    r'(?:\s*<span class="subtitle">\s*([^<]+?)\s*</span>)?', re.S)

_WS_RE = re.compile(r"\s+")


def _clean(s):
    return _WS_RE.sub(" ", html_lib.unescape(s or "")).strip()


def parse_listings(fragment_html):
    """Parse a results page / AJAX fragment. Returns {listing_id: listing}."""
    listings = {}
    for block in _CARD_SPLIT_RE.split(fragment_html)[1:]:
        tm = _TITLE_RE.search(block)
        if not tm:
            continue
        url, lid, title = tm.group(1), tm.group(2), _clean(tm.group(3))
        pm = _ASKING_RE.search(block)
        lm = _LOCATION_RE.search(block)
        cm = _CASHFLOW_RE.search(block)
        om = _OFFICE_RE.search(url)
        listings[lid] = {
            "listing_id": lid,
            "title": title,
            "asking_price": parse_price(pm.group(1)) if pm else None,
            "price_display": _clean(pm.group(1)) if pm else "",
            "url": url,
            # office slug on the card = the broker office; agent name comes
            # from detail-page enrichment when no office slug is present
            "broker": f"Sunbelt office: {om.group(1)}" if om else "",
            "location": _clean(lm.group(1)) if lm else "",
            "cash_flow": parse_price(cm.group(1)) if cm else None,
            "parse_strategy": "article_card",
        }
    return listings


def parse_detail_broker(page_html):
    m = _DETAIL_BROKER_RE.search(page_html or "")
    if not m:
        return ""
    name = _clean(m.group(1))
    office = _clean(m.group(2) or "")
    return f"{name} ({office})" if office else name


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "snb"

    def _ajax_page(self, city, state, page):
        time.sleep(COURTESY_SLEEP)
        resp = requests.post(
            AJAX_URL,
            data={"action": "sunbelt_filter_city", "filterValue": "",
                  "nameCity": city, "nameState": state, "numberPaged": page},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text

    def _fetch_metro_listings(self, metro):
        city, state = METRO_CITY_STATE[metro]
        found = {}
        try:
            for page in range(1, MAX_PAGES + 1):
                fragment = self._ajax_page(city, state, page)
                page_listings = parse_listings(fragment)
                new = {k: v for k, v in page_listings.items() if k not in found}
                found.update(page_listings)
                if not new:
                    break           # ran past the last page
        except Exception:
            if found:
                return found        # keep what the AJAX route already got
            # fallback: server-rendered results page (page 1)
            resp = fetch(RESULTS_URL.format(city=city, state=state))
            found = parse_listings(resp.text)
        return found

    def _fetch_detail_html(self, url):
        return fetch(url).text

    def _parse_detail_broker(self, page_html):
        return parse_detail_broker(page_html)


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

# Real card shapes captured live 2026-07-06 (Houston AJAX fragment + Atlanta
# results page), trimmed. Exercises both detail-URL shapes and the k/m parser.
_PARSER_FIXTURE_HTML = """
<article class="flex flex-col latestBusinesses__item md:flex-row">
 <div class="latestBusinesses__item--middle">
  <a href="https://www.sunbeltnetwork.com/houston-west-tx/buy-a-business/listings/listing-details/houston-auto-repair-business-profitable-59450/">
    <h4 class="latestBusinesses__item--title">Profitable Houston Auto Repair Business with Growing Earnings</h4>
  </a>
  <span class="latestBusinesses__location">
    Houston, Texas            </span>
  <div class="latestBusinesses__values">
    <div class="latestBusinesses__values--box"><strong>
      $1.166m                        </strong><span>Gross Revenue</span></div>
    <div class="latestBusinesses__values--box"><strong>
      $258.5k                        </strong><span>Cash Flow</span></div>
  </div>
 </div>
 <div class="latestBusinesses__item--right">
  <span class="latestBusinesses__item--rightTitle">Asking Price</span>
  <strong class="latestBusinesses__item--rightPrice">
    $1.600m                </strong>
 </div>
</article>
<article class="flex flex-col latestBusinesses__item md:flex-row">
 <div class="latestBusinesses__item--middle">
  <a href="https://www.sunbeltnetwork.com/business-search/business-details/atlanta-residential-painting-franchise-59243/">
    <h4 class="latestBusinesses__item--title">B2B &amp; Residential Painting Franchise in Atlanta with Area Developer Opportunity</h4>
  </a>
  <span class="latestBusinesses__location">
    Atlanta, Georgia            </span>
 </div>
 <div class="latestBusinesses__item--right">
  <span class="latestBusinesses__item--rightTitle">Asking Price</span>
  <strong class="latestBusinesses__item--rightPrice">
    $700k                </strong>
 </div>
</article>
"""

# Real detail-page "Business Listed by" block captured live 2026-07-06, trimmed.
_DETAIL_FIXTURE_HTML = """
<h5 class="resultsBusiness__detailsListed--header"> Business Listed by </h5>
<div class="resultsBusiness__detailsListed--box">
 <div class="resultsBusiness__detailsListed--boxTop">
  <figure><img src="x.jpg" alt="image of David Quintanilla"></figure>
  <div>
   <h5 class="title">David Quintanilla</h5>
   <span class="subtitle">Sunbelt of Houston - West</span>
  </div>
 </div>
</div>
"""


def _parser_regression():
    parsed = parse_listings(_PARSER_FIXTURE_HTML)
    assert len(parsed) == 2, f"parser found {len(parsed)} of 2 cards"
    a = parsed["59450"]
    assert a["asking_price"] == 1_600_000, a       # $1.600m
    assert a["cash_flow"] == 258_500, a            # $258.5k
    assert a["broker"] == "Sunbelt office: houston-west-tx", a
    b = parsed["59243"]
    assert b["asking_price"] == 700_000, b         # $700k
    assert b["broker"] == "", b                    # business-details URL: no office
    assert "Painting Franchise" in b["title"], b
    broker = parse_detail_broker(_DETAIL_FIXTURE_HTML)
    assert broker == "David Quintanilla (Sunbelt of Houston - West)", broker
    print(f"  parser regression: {len(parsed)} cards (k/m prices, both URL "
          f"shapes), detail broker '{broker}'  OK")
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
