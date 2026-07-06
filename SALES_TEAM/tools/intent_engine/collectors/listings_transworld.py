"""Transworld (tworld.com) dead-listings collector (avenue: dead_listings) - BLOCKED.

SHIPPED enabled:false, collect() always returns SKIPPED. Recon 2026-07-06
(live-probed):

BLOCKER: https://www.tworld.com/buy-a-business/business-listings/ returns 200
but is a 998KB client-side Apollo/GraphQL app shell (Laravel+Vite) with ZERO
listing data in the HTML - no prices, no cards, no embedded JSON. A JWT is
embedded in the page (window graphqlToken) but the GraphQL endpoint is not
statically discoverable: POST /graphql -> 405, POST /api/graphql -> 405,
api.tworld.com does not resolve, endpoint absent from app-C2PJo9h_.js and the
graphql-lib bundles. brightdata_unlock does NOT help - it returns the same
empty app shell (listings render only in a browser). Their per-office
subsites redirect into the same app. There is currently no honest way to
collect Transworld with plain requests.

UNBLOCK PATH (cheap, one-time): open the listings page with Chrome MCP, read
the network tab for the GraphQL request (endpoint + query shape + how the
page JWT is sent). After that a collector is pure requests: fetch page ->
regex graphqlToken -> POST the captured query with a location filter.
Entity prefix reserved: "twx:{listing_id}" (add to LISTING_SITES when built).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_transworld --self-test
Prints the SKIPPED status and saves fixtures/listings_transworld_sample.json
documenting the blocker. No network calls, nothing written to the sheet.
"""
import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, run_live_self_test)

SOURCE_ID = "listings_transworld"

BLOCKED_REASON = (
    "blocked: tworld.com listings page is a client-side Apollo/GraphQL app "
    "shell with zero listing data in the HTML; the GraphQL endpoint is not "
    "statically discoverable and brightdata_unlock returns the same empty "
    "shell. Unblock: one-time Chrome MCP network capture of the GraphQL "
    "request, then rebuild as fetch page -> regex graphqlToken -> POST query.")


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "twx"
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
