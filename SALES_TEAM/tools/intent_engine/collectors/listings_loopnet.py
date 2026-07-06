"""LoopNet /biz/ dead-listings collector (avenue: dead_listings) - DO NOT BUILD.

SHIPPED enabled:false, collect() always returns SKIPPED. Recon 2026-07-06:

WHY NOT COLLECTED (not a technical blocker - a data-value decision):
    LoopNet's business-for-sale section (loopnet.com/biz/) is CoStar
    syndication of BizBuySell. CoStar owns both; SERP counts confirm one
    inventory in three skins (Atlanta: LoopNet 182 vs BizQuest 183 vs
    BizBuySell ~same). The already-live listings_bizbuysell collector covers
    this inventory, so a LoopNet collector adds ZERO incremental listings and
    would only add Bright Data unlocker spend and duplicate signals.

Access notes (if ever revisited): plain GET = 403 'Access Denied' (same
CoStar/Akamai edge as BizBuySell/BizQuest, which both unlock fine in
production, so brightdata_unlock is expected to work). Presumed search URLs
(SERP-corroborated for Atlanta, unconfirmed by probe - recon budget went to
BizQuest + DealStream):
    https://www.loopnet.com/biz/texas/houston-businesses-for-sale/
    https://www.loopnet.com/biz/georgia/atlanta-businesses-for-sale/
If a collector is ever built here, it MUST key entities as bbs:{listing_id}
(BizBuySell's id space) so signals dedup against listings_bizbuysell - model
on collectors/listings_bizquest.py, which does exactly that for the same
reason.

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_loopnet --self-test
Prints the SKIPPED status and saves fixtures/listings_loopnet_sample.json
documenting the reason. No network calls, nothing written to the sheet.
"""
import argparse
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._listings_common import (  # noqa: E402
    ListingSiteCollector, run_live_self_test)

SOURCE_ID = "listings_loopnet"

BLOCKED_REASON = (
    "not collected by design: loopnet.com/biz/ is CoStar syndication of "
    "BizBuySell (one inventory, three skins) - zero incremental listings over "
    "listings_bizbuysell, only extra unlocker spend + duplicate signals. If "
    "ever built, key entities as bbs:{id} (see listings_bizquest).")


class Collector(ListingSiteCollector):
    source_id = SOURCE_ID
    prefix = "bbs"              # BizBuySell id space, were it ever collected
    blocked_reason = BLOCKED_REASON


COLLECTOR = Collector()


def _self_test():
    print(f"[{SOURCE_ID}] --self-test")
    print(f"  intentionally not collected: {BLOCKED_REASON}")
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
