"""DealStream dead-listings collector (avenue: dead_listings) - BLOCKED.

SHIPPED enabled:false, collect() always returns SKIPPED. Recon 2026-07-06
(live-probed: plain GET = hard 403 774-byte block page; brightdata_unlock DOES
fetch it - 140KB, 57 price tokens):

TWO BLOCKERS (do not enable until both are cleared):
 1. METRO SCOPING UNPROVEN. The geo URL
        https://dealstream.com/businesses-for-sale/texas/houston
    returns the GLOBAL unfiltered feed - canonical/rel-next claim
    texas/houston while the cards are from SC, NY, UK, Arkansas, BC, ...
    Location filtering happens via the search form's hidden inputs
    (location_city, location_admin1, location_countrycode, set by a JS
    location_picker) and was not reproducible by URL alone. A collector built
    today would snapshot a global feed and pollute Houston/Atlanta with
    foreign listings - fake metro data, which this engine does not do.
 2. DETAIL PAGES LOGIN-GATED. 'Details' lock icon -> free membership wall, so
    broker/contact enrichment is behind auth.

UNBLOCK PATH (cheap, one-time): drive the search form once with Chrome MCP,
capture the location-filter POST (endpoint + hidden-input values for Houston
and Atlanta), then this becomes a normal brightdata_unlock collector.

Card anatomy for that future build (parseable, captured via unlocker):
    <a class='card...post' data-postid={mongoid} href=/d/biz-sale/{category}/{slug6}>
    title in h2 span.headline_*, price in div.h2, state-level location span.
Entity prefix reserved: "dst:{postid}".

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_dealstream --self-test
Prints the SKIPPED status and saves fixtures/listings_dealstream_sample.json
documenting the blockers. No network calls, nothing written to the sheet.
"""
import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, run_live_self_test)

SOURCE_ID = "listings_dealstream"

BLOCKED_REASON = (
    "blocked: geo URLs return the GLOBAL feed (metro scoping unproven - the "
    "search form's JS-set hidden inputs were not reproducible by URL), and "
    "detail pages are login-gated. Collecting now would pollute the metros "
    "with foreign listings. Unblock: one-time Chrome MCP capture of the "
    "location-filter POST, then rebuild on brightdata_unlock.")


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "dst"
    blocked_reason = BLOCKED_REASON


COLLECTOR = Collector()


def _self_test():
    print(f"[{SOURCE_ID}] --self-test")
    print(f"  blocked: {BLOCKED_REASON}")
    result = run_live_self_test(Collector(), SOURCE_ID, None)
    return 0 if result.status == "SKIPPED" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="print SKIPPED status + save the reason fixture; "
                             "no network, nothing written to the sheet")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    parser.print_help()
