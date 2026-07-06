"""Brazoria County Clerk lien/judgment collector (avenue: pe_distress).

Source: https://brazoriacountytx-web.tylerhost.net/web
(Tyler Technologies "Self Service" / Eagle Recorder, version 2026.1.9; linked
from https://www.brazoriacountyclerktx.gov/search-records/
real-property-and-vital-records).

DISABLED (enabled:false in signal_registry.json) — WHY, verified 2026-07-06:
    The free public search sits behind a disclaimer-accept page gated by a
    reCAPTCHA v2 "I'm not a robot" INTERACTIVE CHECKBOX — the challenge must
    be passed and "I Accept" clicked before ANY search form is reachable.
    This is a hard interactive challenge (not v3 score-based); solving or
    bypassing captchas is out of scope, so automated collection is genuinely
    blocked. The post-captcha search form could not even be characterized
    without solving the challenge (instrument-type + date-range filters
    almost certainly exist behind the gate — standard Tyler Eagle search).

Paths to enable later (in preference order):
    1. Human-in-the-loop: a person solves the captcha once and exports the
       session cookie for this collector to replay until it expires.
    2. Chrome-MCP driven session where EZ clicks the checkbox himself.
    3. Paid bulk data via TexasFile (covers Brazoria).

collect() therefore ALWAYS returns SKIPPED with the block reason — it makes
no network attempt (there is nothing meaningful to attempt behind an
interactive captcha) and never fakes data.

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_brazoria --self-test
Prints the SKIPPED result, writes NOTHING to the sheet, and saves
fixtures/liens_brazoria_sample.json documenting the block.
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult  # noqa: E402

SOURCE_ID = "liens_brazoria"
AVENUE = "pe_distress"

PORTAL_URL = "https://brazoriacountytx-web.tylerhost.net/web"

SKIP_MSG = (
    "hard-blocked: Tyler Self Service portal gates ALL search behind a "
    "reCAPTCHA v2 interactive checkbox on the disclaimer-accept page "
    "(verified 2026-07-06). Captcha solving is out of scope. Options: "
    "human-in-the-loop session cookie, Chrome-MCP session with a human "
    "click, or paid bulk via TexasFile. See module docstring."
)


class Collector(BaseCollector):
    avenue = AVENUE
    source_id = SOURCE_ID
    metros = ("houston",)

    def collect(self, since, store, registry):
        # No network attempt: the disclaimer gate needs an interactive
        # captcha, so any automated request is dead on arrival.
        return CollectorResult(self.source_id, 0, 0, "SKIPPED", SKIP_MSG)


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

def _self_test(days=30):
    from common.store import Store
    print(f"[{SOURCE_ID}] --self-test  (last {days} days)")
    since = date.today() - timedelta(days=days)
    registry = config.load_registry()
    store = Store(":memory:")
    result = Collector().collect(since, store, registry)
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture = {
        "source_id": SOURCE_ID,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "window_days": days,
        "enabled": False,
        "blocked_reason": SKIP_MSG,
        "portal_url": PORTAL_URL,
        "sample_record": None,
        "signal_counts": {},
    }
    fixture_path = fixtures_dir / f"{SOURCE_ID}_sample.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, default=str),
                            encoding="utf-8")

    print(f"  status={result.status} signals={result.signals_added} "
          f"entities={result.entities_seen}")
    print(f"  detail: {result.error}")
    print(f"  fixture saved: {fixture_path}")
    print(f"  RESULT: {result.status}")
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="print the SKIPPED result; writes nothing but "
                             "fixtures/<source_id>_sample.json")
    parser.add_argument("--days", type=int, default=30,
                        help="self-test lookback window (default 30)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test(args.days))
    parser.print_help()
