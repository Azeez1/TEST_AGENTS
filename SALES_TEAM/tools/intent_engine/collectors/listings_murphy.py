"""Murphy Business dead-listings collector (avenue: dead_listings).

PLAIN fetch (WordPress). The national list (/business-brokerage/view-our-listings/)
paginates via JS and its cards carry only state-level or 'Confidential'
locations — metro assignment from it is fuzzy. The pragmatic metro route
(recon-endorsed) is the PER-OFFICE listings pages, which are properly scoped
to each office's inventory. Office slugs enumerated live 2026-07-06 from
https://murphybusiness.com/offices/tx/ and /offices/ga/:
    houston: centralhouston, cypressnorth-tomball, easthouston,
             houstonnorthwest, northcentralhouston
    atlanta: northfultoncounty, eastcobbcounty, nwgeorgia
Each office page (https://murphybusiness.com/{slug}/businesses-for-sale/)
serves ~10 newest cards server-side. KNOWN LIMIT: the page's AJAX pagination
endpoint ({office}/wp-admin/admin-ajax.php action=business_listings_new) was
probed live 2026-07-06 and returns the NATIONAL feed (Michigan/Ontario/...)
— NOT office-scoped — so it is deliberately NOT used; we take page 1 per
office only (~10 newest listings x 8 offices) rather than pollute the metros.

Card anatomy (captured live): <div class="card"> ... <p class="price">$10,000,000</p>
<h5 class="card-title">title</h5> <li>SDE: $628,189</li>
<li><img ...pin.png>Texas|Confidential</li>
<a href="https://murphybusiness.com/business-brokerage/detail/{id}/{slug}">
Cards are duplicated in the DOM (desktop+mobile) — dict-by-id dedupes.

Broker: the office itself (Murphy office = the broker relationship to work).
Detail pages carry NO agent name (verified live — only a 'Contact Listing
Owner' form), so detail-page enrichment is disabled (detail_fetch_cap=0).

Days-on-market: weekly snapshot diff keyed on the numeric detail id via
collectors._listings_common.diff_and_emit (stale_180d / price_cut /
relisting). Cross-site dedupe via CrossSiteDeduper.

Entity key: "mur:{listing_id}" (or the canonical cross-site key on exact match).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_murphy --self-test
Offline parser regression + shared synthetic snapshot exercise + real collect()
into a throwaway store. Writes NOTHING to the sheet; saves
fixtures/listings_murphy_sample.json.
"""
import argparse
import html as html_lib
import re
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, parse_price, synthetic_exercise, run_live_self_test)
from common.http import fetch  # noqa: E402

SOURCE_ID = "listings_murphy"

# Office slugs enumerated live 2026-07-06 (see module docstring). Dallas
# offices exist on /offices/tx/ but are intentionally excluded (wrong metro).
OFFICE_PAGES = {
    "houston": ["centralhouston", "cypressnorth-tomball", "easthouston",
                "houstonnorthwest", "northcentralhouston"],
    "atlanta": ["northfultoncounty", "eastcobbcounty", "nwgeorgia"],
}
OFFICE_URL = "https://murphybusiness.com/{slug}/businesses-for-sale/"

# Two card shapes exist (both captured live 2026-07-06):
#   national list: <h5 class="card-title">Title</h5>, detail href without
#     office prefix, <li>SDE: $628,189</li>
#   office pages:  <h5 class="card-title min-height"><a href=...>Title</a></h5>,
#     detail href prefixed with the office slug
#     (https://murphybusiness.com/{office}/business-brokerage/detail/{id}/...),
#     SDE as an icon li (<img ...dollar.png ...> $628,189)
_CARD_SPLIT_RE = re.compile(r'<div class="card">')
_HREF_RE = re.compile(
    r'href="(https://murphybusiness\.com/(?:[a-z0-9\-]+/)?'
    r'business-brokerage/detail/(\d+)/[^"]*)"')
_TITLE_RE = re.compile(r'card-title[^"]*">\s*(.*?)\s*</h5>', re.S)
_PRICE_RE = re.compile(r'<p class="price">\s*([^<]+?)\s*</p>')
_SDE_RE = re.compile(r"<li>\s*SDE:\s*([^<]+?)\s*</li>")
_SDE_ICON_RE = re.compile(r'dollar\.png"[^>]*>\s*([^<]+?)\s*</li>', re.S)
_PIN_RE = re.compile(r'pin\.png"[^>]*>\s*([^<]+?)\s*</li>', re.S)
_TAG_RE = re.compile(r"<[^>]+>")

_WS_RE = re.compile(r"\s+")


def _clean(s):
    return _WS_RE.sub(" ", html_lib.unescape(_TAG_RE.sub(" ", s or ""))).strip()


def parse_listings(page_html, office=""):
    """Parse one office listings page. Returns {listing_id: listing dict}.
    Cards appear twice in the DOM (desktop+mobile); dict-by-id dedupes."""
    listings = {}
    for block in _CARD_SPLIT_RE.split(page_html)[1:]:
        hm = _HREF_RE.search(block)
        tm = _TITLE_RE.search(block)
        pm = _PRICE_RE.search(block)
        if not hm or not tm or not pm:
            continue
        lid = hm.group(2)
        sm = _SDE_RE.search(block) or _SDE_ICON_RE.search(block)
        lm = _PIN_RE.search(block)
        listings[lid] = {
            "listing_id": lid,
            "title": _clean(tm.group(1)),
            "asking_price": parse_price(pm.group(1)),
            "url": hm.group(1),
            "broker": f"Murphy Business ({office})" if office else "Murphy Business",
            "location": _clean(lm.group(1)) if lm else "",
            "cash_flow": parse_price(sm.group(1)) if sm else None,  # SDE
            "office": office,
            "parse_strategy": "office_card",
        }
    return listings


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "mur"
    detail_fetch_cap = 0        # detail pages carry no agent name (verified)

    def _fetch_metro_listings(self, metro):
        found = {}
        errors = []
        for slug in OFFICE_PAGES[metro]:
            try:
                resp = fetch(OFFICE_URL.format(slug=slug))
            except Exception as exc:
                errors.append(f"{slug}: {type(exc).__name__}")
                continue
            office_listings = parse_listings(resp.text, office=slug)
            for lid, listing in office_listings.items():
                found.setdefault(lid, listing)   # first office wins
        if not found and errors:
            raise RuntimeError("all office pages failed: " + "; ".join(errors))
        return found


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

# Real card shapes captured live 2026-07-06 (national list + office pages),
# trimmed. Includes a 'Confidential' location and a duplicated card (DOM
# renders each card twice) to prove dict-by-id dedupe.
_PARSER_FIXTURE_HTML = """
<div class="card">
 <div class="banner"><img src="x.jpg" class="card-img-top" alt="...">
  <p class="tags">Active</p></div>
 <div class="card-body">
  <h5 class="card-title">
  18-Hole Golf Club over 300 Acres-Growing Membership                                        </h5>
  <p class="price">$19,900,000</p>
  <ul><li>SDE: $1,597,102</li><li>|</li>
   <li><img src="https://murphybusiness.com/wp-content/themes/murphybusiness/images/pin.png" alt="">Confidential</li></ul>
  <a href="https://murphybusiness.com/business-brokerage/detail/21543/18-hole-golf-club-over-300-acres-growing-membership" target="_blank" class="btn btn-primary">LEARN MORE</a>
 </div>
</div>
<div class="card">
 <div class="banner"><img src="y.jpg" class="card-img-top" alt="...">
  <p class="tags">Active</p></div>
 <div class="card-body">
  <h5 class="card-title">
  Absentee SaaS Platform for Retailers                                        </h5>
  <p class="price">$10,000,000</p>
  <ul><li>SDE: $628,189</li><li>|</li>
   <li><img src="https://murphybusiness.com/wp-content/themes/murphybusiness/images/pin.png" alt="">Texas</li></ul>
  <a href="https://murphybusiness.com/business-brokerage/detail/18794/absentee-saas-platform-for-retailers" target="_blank" class="btn btn-primary">LEARN MORE</a>
 </div>
</div>
<div class="card">
 <div class="card-body">
  <h5 class="card-title">
  Absentee SaaS Platform for Retailers                                        </h5>
  <p class="price">$10,000,000</p>
  <ul><li>SDE: $628,189</li><li>|</li>
   <li><img src="https://murphybusiness.com/wp-content/themes/murphybusiness/images/pin.png" alt="">Texas</li></ul>
  <a href="https://murphybusiness.com/business-brokerage/detail/18794/absentee-saas-platform-for-retailers" target="_blank" class="btn btn-primary">LEARN MORE</a>
 </div>
</div>
<div class="card"> <div class="banner">
 <img class="image" alt="Gulf Coast Scaffolding" src="z.jpg" width="360" height="254">
 <p class="tags">Active</p> <!-- <p class="price">$7,600,000</p> --> </div>
 <div class="card-body">
  <h5 class="card-title min-height"><a href="https://murphybusiness.com/houstonnorthwest/business-brokerage/detail/21865/gulf-coast-based-industrial-scaffolding-insulation-company" target="_blank">Gulf Coast Based Industrial Scaffolding &amp; Insulation Company</a></h5>
  <p class="price">$7,600,000</p>
  <ul class="flex-wrap">
   <li> <img src="https://murphybusiness.com/houstonnorthwest/wp-content/themes/murphy-common/images/businesses-for-sale/customer-support.png" alt=""> business </li>
   <li>|</li>
   <li> <img src="https://murphybusiness.com/houstonnorthwest/wp-content/themes/murphy-common/images/businesses-for-sale/pin.png" alt=""> Texas </li>
   <li>|</li>
   <li> <img src="https://murphybusiness.com/houstonnorthwest/wp-content/themes/murphy-common/images/businesses-for-sale/dollar.png" alt=""> $1,943,000 </li>
  </ul>
 </div>
</div>
"""


def _parser_regression():
    parsed = parse_listings(_PARSER_FIXTURE_HTML, office="houstonnorthwest")
    assert len(parsed) == 3, f"parser found {len(parsed)} unique of 4 cards"
    a = parsed["21543"]
    assert a["asking_price"] == 19_900_000 and a["location"] == "Confidential", a
    b = parsed["18794"]
    assert b["asking_price"] == 10_000_000 and b["cash_flow"] == 628_189, b
    assert b["broker"] == "Murphy Business (houstonnorthwest)", b
    c = parsed["21865"]                                # office-page card shape
    assert c["asking_price"] == 7_600_000 and c["cash_flow"] == 1_943_000, c
    assert c["title"].startswith("Gulf Coast Based"), c
    assert c["location"] == "Texas", c
    in_band = [l for l in parsed.values()
               if l["asking_price"] and 1_000_000 <= l["asking_price"] <= 10_000_000]
    assert len(in_band) == 2, in_band                  # $19.9M golf club is out
    print(f"  parser regression: 4 cards (both shapes) -> {len(parsed)} unique "
          f"(dup dedup), {len(in_band)} in $1M-$10M band  OK")
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
