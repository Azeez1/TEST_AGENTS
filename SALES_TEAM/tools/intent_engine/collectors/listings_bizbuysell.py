"""BizBuySell dead-listings collector (avenue: dead_listings).

Scrapes BizBuySell search results for Houston + Atlanta (asking $1M-$10M band,
filtered client-side because BizBuySell ignores naive price_min/price_max URL
params) through Bright Data Web Unlocker (common.http.brightdata_unlock).
Requires BRIGHTDATA_API_TOKEN in ~/.dux_intent/.env; when the token is missing
collect() returns CollectorResult(status="SKIPPED") and never crashes.

Days-on-market strategy (on-page "listed" dates are unreliable):
    Every run stores each parsed listing as a snapshot keyed by listing_id
    (store.add_snapshot). Age is derived from store.first_seen(source_id,
    listing_id) — i.e. the first weekly run that observed the listing. Signals:

    stale_180d  age >= 180 days since first_seen. magnitude 1.0.
                signal_date = the day the listing crossed 180d (stable, so the
                weekly re-emission dedups instead of stacking).
    price_cut   asking price dropped vs the latest prior snapshot (> 0.5% to
                ignore rounding noise). magnitude = min(1.0, pct_drop / 0.25).
    relisting   listing_id reappears after >= 21 days without a snapshot
                (~3 missed weekly runs). magnitude = clamp(gap/90, 0.5, 1.0).
                Caveat: if the whole engine is paused > 21 days, the first run
                back will read as a wave of relistings — check runs table.

    Note: age counts from the FIRST sighting ever, across absences; a listing
    that vanished and returned gets both its true age and a relisting signal.

Broker aggregation: per-run count of stale listings per (best-effort parsed)
broker; a broker holding >= 2 stale listings is a coffee target — stale
signals carry attrs broker_stale_count + coffee_target.

Broker enrichment: listings still missing a broker after the search-page parse
get a bounded detail-page fetch (oldest first, cap DETAIL_FETCH_CAP_BBS per
metro — unlocker requests cost money). The detail page's "Business Listed By:"
broker-name anchor was verified live 2026-07-06.

Cross-site dedupe: snapshot diffing stays keyed on the BizBuySell listing id,
but signal entity keys resolve through _listings_common.CrossSiteDeduper so a
business cross-posted on BusinessesForSale/BusinessBroker/Sunbelt/Murphy
stacks onto ONE entity with source_refs of every site (exact fingerprint
matches only; near-misses are just flagged in attrs).

Entity key: "bbs:{listing_id}" (canonical for the whole avenue — BizBuySell is
the highest-priority listing site; BizQuest/LoopNet share this id space).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.listings_bizbuysell --self-test
Runs (1) an offline parser regression test against embedded real-format HTML,
(2) a synthetic prior-snapshot exercise that proves the days-on-market /
price-cut / relisting / broker-aggregation logic, and (3) a real collect()
over the last 30 days into a throwaway in-memory store. Writes NOTHING to the
sheet; saves one raw sample payload to fixtures/listings_bizbuysell_sample.json.
"""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402, F401
from collectors._listings_common import (  # noqa: E402
    CrossSiteDeduper, diff_and_emit, enrich_brokers, unlock_with_retry)
from common.http import brightdata_unlock  # noqa: E402

SOURCE_ID = "listings_bizbuysell"
AVENUE = "dead_listings"

PRICE_MIN = 1_000_000
PRICE_MAX = 10_000_000
MAX_PAGES = 4                    # Bright Data requests cost money; ~90 cards/metro
STALE_DAYS = 180
RELIST_MIN_GAP_DAYS = 21
PRICE_CUT_MIN_DROP = 0.005       # ignore <0.5% wiggles
BROKER_COFFEE_THRESHOLD = 2
DETAIL_FETCH_CAP_BBS = 3         # detail fetches go through the unlocker ($)

SEARCH_URLS = {
    "houston": "https://www.bizbuysell.com/texas/houston-businesses-for-sale/",
    "atlanta": "https://www.bizbuysell.com/georgia/atlanta-businesses-for-sale/",
}

# listing card anchors observed live 2026-07-05 via Bright Data:
#   https://www.bizbuysell.com/business-opportunity/{slug}/{id}/
#   https://www.bizbuysell.com/business-asset/{slug}/{id}/
_ANCHOR_RE = re.compile(
    r'href="(?:https?://www\.bizbuysell\.com)?'
    r'(/business-(?:opportunity|asset)/[^"/]+/(\d{5,9})/)"'
    r'[^>]*title="([^"]*)"')
_PRICE_RE = re.compile(r"\$\s?([\d,]{6,})")
_LDJSON_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
_STATE_RE = re.compile(
    r'<script[^>]*id="serverApp-state"[^>]*>(.*?)</script>', re.S)


def _to_price(val):
    """Coerce '$1,350,000' / '1350000' / 1350000.0 -> int or None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return int(val) if val > 0 else None
    m = re.search(r"[\d,]+", str(val))
    if not m:
        return None
    try:
        n = int(m.group(0).replace(",", ""))
    except ValueError:
        return None
    return n if n > 0 else None


def _unescape_transfer_state(txt):
    """Angular TransferState escaping: &q;=&quot; &s;=' &l;=< &g;=> &a;=&."""
    for esc, ch in (("&q;", '"'), ("&s;", "'"), ("&l;", "<"), ("&g;", ">"),
                    ("&a;", "&")):
        txt = txt.replace(esc, ch)
    return txt


def _walk(obj):
    """Yield every dict nested anywhere inside obj."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _broker_from_dict(d):
    for key in ("brokerCompanyName", "brokerCompany", "brokerFirmName",
                "brokerName", "brokerContactFullName", "companyName",
                "contactFullName", "contactName"):
        v = d.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _listing_id_from_url(url):
    m = re.search(r"/business-(?:opportunity|asset)/[^/]+/(\d{5,9})/", url or "")
    return m.group(1) if m else None


# detail page: <span>Business Listed By:</span> ...
# <a class="broker-name ..." href="/business-broker/{person}/{firm}/{id}/">Name</a>
# (verified live 2026-07-06 on listing 2507558)
_DETAIL_BROKER_A_RE = re.compile(
    r'<a[^>]*broker-name[^>]*>\s*([^<]+?)\s*</a>')
_DETAIL_FIRM_RE = re.compile(r'href="/business-broker/[^/"]+/([^/"]+)/\d+/"')


def parse_detail_broker(html):
    """Broker 'Name (Firm)' from a listing detail page, or ''."""
    i = html.find("Business Listed By")
    window = html[i:i + 4000] if i >= 0 else html
    m = _DETAIL_BROKER_A_RE.search(window)
    if not m:
        return ""
    name = m.group(1).strip()
    fm = _DETAIL_FIRM_RE.search(window)
    if fm:
        firm = fm.group(1).replace("-", " ").title()
        return f"{name} ({firm})"
    return name


def parse_listings(html):
    """Parse a BizBuySell search-results page. Returns {listing_id: listing}.

    Layered strategies (page is an Angular app; markup shifts):
      1. serverApp-state transfer-state JSON (richest: price + broker)
      2. application/ld+json blocks (ItemList/Product offers)
      3. raw anchor regex + nearest $ amount inside the card anchor
    """
    listings = {}

    # -- strategy 1: Angular transfer state ------------------------------
    m = _STATE_RE.search(html)
    if m:
        try:
            state = json.loads(_unescape_transfer_state(m.group(1)))
        except (ValueError, TypeError):
            state = None
        if state is not None:
            for d in _walk(state):
                url = d.get("url") or d.get("urlStub") or d.get("listingUrl") or ""
                lid = _listing_id_from_url(str(url))
                if lid is None and str(d.get("id", "")).isdigit() and (
                        "header" in d or "title" in d):
                    lid = str(d["id"])
                if lid is None:
                    continue
                title = (d.get("header") or d.get("title") or d.get("name")
                         or "").strip()
                price = _to_price(d.get("price") or d.get("askingPrice")
                                  or d.get("listPrice"))
                if not title or price is None:
                    continue
                if not str(url).startswith("http"):
                    url = f"https://www.bizbuysell.com{url}" if url else \
                        f"https://www.bizbuysell.com/business-opportunity/listing/{lid}/"
                listings[lid] = {
                    "listing_id": lid, "title": title, "asking_price": price,
                    "url": str(url), "broker": _broker_from_dict(d),
                    "location": (d.get("location") or d.get("locationName")
                                 or ""),
                    "cash_flow": _to_price(d.get("cashFlow")),
                    "parse_strategy": "transfer_state",
                }

    # -- strategy 2: JSON-LD ----------------------------------------------
    for block in _LDJSON_RE.findall(html):
        try:
            data = json.loads(block.strip())
        except (ValueError, TypeError):
            continue
        for d in _walk(data):
            url = d.get("url") or (d.get("item") or {}).get("url") \
                if isinstance(d.get("item"), dict) else d.get("url")
            lid = _listing_id_from_url(str(url or ""))
            if lid is None or lid in listings:
                continue
            name = d.get("name") or ""
            offers = d.get("offers") or {}
            price = _to_price(offers.get("price") if isinstance(offers, dict)
                              else None) or _to_price(d.get("price"))
            if not name or price is None:
                continue
            listings[lid] = {
                "listing_id": lid, "title": str(name).strip(),
                "asking_price": price, "url": str(url), "broker": "",
                "location": "", "cash_flow": None, "parse_strategy": "ld_json",
            }

    # -- strategy 3: anchor + nearby price regex --------------------------
    for m in _ANCHOR_RE.finditer(html):
        path, lid, title = m.group(1), m.group(2), m.group(3)
        if lid in listings:
            continue
        window = html[m.start():m.start() + 3000]
        pm = _PRICE_RE.search(window)
        price = _to_price(pm.group(1)) if pm else None
        if price is None:
            continue
        listings[lid] = {
            "listing_id": lid, "title": title.strip(), "asking_price": price,
            "url": f"https://www.bizbuysell.com{path}", "broker": "",
            "location": "", "cash_flow": None, "parse_strategy": "anchor",
        }

    return listings


class Collector(BaseCollector):
    avenue = AVENUE
    source_id = SOURCE_ID
    metros = ("houston", "atlanta")

    # -- fetching ----------------------------------------------------------

    def _fetch_metro_listings(self, metro):
        """Fetch up to MAX_PAGES of search results; return {listing_id: listing}
        already filtered to the $1M-$10M asking band."""
        base = SEARCH_URLS[metro]
        found = {}
        for page in range(1, MAX_PAGES + 1):
            url = base if page == 1 else f"{base}{page}/"
            html = brightdata_unlock(url)
            page_listings = parse_listings(html)
            new = {k: v for k, v in page_listings.items() if k not in found}
            found.update(page_listings)
            if page > 1 and not new:
                break               # ran past the last page
        return {
            lid: l for lid, l in found.items()
            if l["asking_price"] is not None
            and PRICE_MIN <= l["asking_price"] <= PRICE_MAX
        }

    # -- broker enrichment (bounded detail-page fetches through the unlocker)

    def _enrich_brokers(self, store, listings):
        """Fill missing brokers via detail pages, oldest listings first, hard
        cap DETAIL_FETCH_CAP_BBS attempts per metro (unlocker spend)."""
        missing = [l for l in listings if not l.get("broker")]
        missing.sort(key=lambda l: store.first_seen(
            self.source_id, str(l["listing_id"])) or "9999-12-31")
        return enrich_brokers(missing, unlock_with_retry, parse_detail_broker,
                              cap=DETAIL_FETCH_CAP_BBS)

    # -- snapshot diffing (separable so the self-test can drive it) --------

    def _diff_and_emit(self, store, metro, listings, today):
        """Snapshot today's listings, diff against history, emit signals via
        the shared _listings_common.diff_and_emit (single implementation for
        all listing sites), with cross-site dedupe.

        listings: iterable of listing dicts (see parse_listings values).
        Returns (signals_added, entity_keys_set, Counter_by_signal_type).
        """
        deduper = CrossSiteDeduper(store, own_source=self.source_id)
        return diff_and_emit(
            store, self.source_id, self.avenue, "bbs", metro, listings, today,
            stale_days=STALE_DAYS, relist_min_gap_days=RELIST_MIN_GAP_DAYS,
            price_cut_min_drop=PRICE_CUT_MIN_DROP,
            broker_coffee_threshold=BROKER_COFFEE_THRESHOLD, deduper=deduper)

    # -- contract entrypoint -----------------------------------------------

    def collect(self, since, store, registry):
        try:
            if not config.get_env("BRIGHTDATA_API_TOKEN"):
                return CollectorResult(
                    self.source_id, 0, 0, "SKIPPED",
                    "BRIGHTDATA_API_TOKEN not set in ~/.dux_intent/.env")
            today = date.today()
            total_added = 0
            entities = set()
            errors = []
            fetched_any = False
            for metro in self.metros:
                try:
                    listings = self._fetch_metro_listings(metro)
                except Exception as exc:
                    errors.append(f"{metro}: {type(exc).__name__}: {exc}")
                    continue
                fetched_any = True
                try:
                    self._enrich_brokers(store, list(listings.values()))
                except Exception:
                    pass            # enrichment is best-effort
                added, keys, _ = self._diff_and_emit(
                    store, metro, list(listings.values()), today)
                total_added += added
                entities |= keys
            if not fetched_any:
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       "; ".join(errors) or "no metro fetched")
            status = "OK" if total_added else "EMPTY"
            return CollectorResult(self.source_id, total_added, len(entities),
                                   status, "; ".join(errors))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

# Real listing-card shapes captured from the live Houston results page
# (2026-07-05, via Bright Data). Exercises parse strategy 3.
_PARSER_FIXTURE_HTML = """
<div class="listing">
<a href="https://www.bizbuysell.com/business-opportunity/profitable-turnkey-active-freight-trucking-company-active-amazon-r/2511364/" title="Profitable Turnkey Active Freight Trucking Company - Active Amazon R.">
<span>Houston, TX</span><p>Confidential opportunity ...</p>
<span class="asking-price">$1,350,000</span><span>Cash Flow: $330,000</span></a></div>
<div class="listing">
<a href="https://www.bizbuysell.com/business-opportunity/large-fedex-line-haul-business-for-sale/2507558/" title="Large FedEx line haul Business for Sale">
<span>Houston, TX</span><span class="asking-price">$6,600,000</span></a></div>
<div class="listing">
<a href="https://www.bizbuysell.com/business-asset/collision-repair-business-and-real-estate-for-sale-asking-price-3-3m/2509430/" title="Collision Repair Business &amp; Real Estate For Sale Asking Price: $3.3m">
<span>Houston, TX</span><span class="asking-price">$3,300,000</span></a></div>
<div class="listing">
<a href="https://www.bizbuysell.com/business-opportunity/established-dog-daycare-and-boarding-houston/2516196/" title="Established Dog Daycare &amp; Boarding - Houston">
<span>Houston, TX</span><span class="asking-price">$100,000</span></a></div>
"""

# Real detail-page broker block captured live 2026-07-06 (listing 2507558).
_DETAIL_FIXTURE_HTML = """
<div class="broker-card"> <span class="f-14">Business Listed By:</span><br>
<a id="ctl00_ctl00_Content_ContentPlaceHolder1_wideProfile_ContactBrokerNameHyperLink"
 class="broker-name width-100 f-m normal"
 href="/business-broker/shawn-mcpeters/buyers-market-inc/9064/">Shawn McPeters</a>
</div>
"""


def _mk_listing(lid, title, price, broker="", url=None):
    return {
        "listing_id": lid, "title": title, "asking_price": price,
        "url": url or f"https://www.bizbuysell.com/business-opportunity/x/{lid}/",
        "broker": broker, "location": "Houston, TX", "cash_flow": None,
        "parse_strategy": "synthetic",
    }


def _parser_regression():
    parsed = parse_listings(_PARSER_FIXTURE_HTML)
    assert len(parsed) == 4, f"parser found {len(parsed)} of 4 cards"
    assert parsed["2511364"]["asking_price"] == 1_350_000, parsed["2511364"]
    in_band = {k: v for k, v in parsed.items()
               if PRICE_MIN <= v["asking_price"] <= PRICE_MAX}
    assert set(in_band) == {"2511364", "2507558", "2509430"}, in_band
    broker = parse_detail_broker(_DETAIL_FIXTURE_HTML)
    assert broker == "Shawn McPeters (Buyers Market Inc)", broker
    print(f"  parser regression: {len(parsed)} cards parsed, "
          f"{len(in_band)} in $1M-$10M band, detail broker '{broker}'  OK")
    return parsed["2511364"]


def _synthetic_exercise():
    """Prove days-on-market / price-cut / relisting / broker logic against a
    synthetic prior-snapshot history."""
    from common.store import Store
    store = Store(":memory:")
    c = Collector()
    today = date.today()

    def d(n):
        return (today - timedelta(days=n)).isoformat()

    # A: first seen 200d ago, still listed, price cut 2.5M -> 2.1M (stale+cut)
    store.add_snapshot(SOURCE_ID, d(200), "9000001",
                       _mk_listing("9000001", "GULF FREIGHT CARRIERS",
                                   2_500_000, "Gatsby Advisors"))
    store.add_snapshot(SOURCE_ID, d(7), "9000001",
                       _mk_listing("9000001", "GULF FREIGHT CARRIERS",
                                   2_500_000, "Gatsby Advisors"))
    # B: seen 60d and 40d ago, absent since -> reappears today (relisting)
    store.add_snapshot(SOURCE_ID, d(60), "9000002",
                       _mk_listing("9000002", "BAYOU HVAC SERVICES", 1_800_000))
    store.add_snapshot(SOURCE_ID, d(40), "9000002",
                       _mk_listing("9000002", "BAYOU HVAC SERVICES", 1_800_000))
    # C: first seen 190d ago, same broker as A -> broker coffee target
    store.add_snapshot(SOURCE_ID, d(190), "9000003",
                       _mk_listing("9000003", "WESTSIDE MACHINE SHOP",
                                   4_200_000, "Gatsby Advisors"))

    current = [
        _mk_listing("9000001", "GULF FREIGHT CARRIERS", 2_100_000,
                    "Gatsby Advisors"),
        _mk_listing("9000002", "BAYOU HVAC SERVICES", 1_800_000),
        _mk_listing("9000003", "WESTSIDE MACHINE SHOP", 4_200_000,
                    "Gatsby Advisors"),
    ]
    added, keys, by_type = c._diff_and_emit(store, "houston", current, today)

    expect = {"stale_180d": 2, "price_cut": 1, "relisting": 2}
    assert dict(by_type) == expect, f"got {dict(by_type)}, want {expect}"
    assert added == 5, f"expected 5 inserted signals, got {added}"
    assert len(keys) == 3, keys

    sigs = store.get_signals(avenue=AVENUE)
    stale = [s for s in sigs if s["signal_type"] == "stale_180d"]
    coffee = [s for s in stale
              if json.loads(s["attrs"]).get("coffee_target")]
    assert len(coffee) == 2, "both Gatsby stale listings must be coffee targets"
    assert all(json.loads(s["attrs"])["broker_stale_count"] == 2
               for s in coffee)
    cut = next(s for s in sigs if s["signal_type"] == "price_cut")
    assert abs(cut["magnitude"] - min(1.0, (400000 / 2500000) / 0.25)) < 1e-6

    # idempotency: rerunning the same day adds no new signal rows
    added2, _, _ = c._diff_and_emit(store, "houston", current, today)
    assert added2 == 0, f"rerun must dedup, added {added2}"

    print(f"  synthetic snapshots: {dict(by_type)}  "
          f"coffee_targets={len(coffee)}  rerun_dedup=OK")
    store.close()
    return by_type


def _self_test():
    from common.store import Store
    print(f"[{SOURCE_ID}] --self-test")

    sample = _parser_regression()
    by_type = _synthetic_exercise()
    synthetic_total = sum(by_type.values())

    since = date.today() - timedelta(days=30)
    registry = config.load_registry()
    store = Store(":memory:")
    result = Collector().collect(since, store, registry)

    live_sample = None
    if result.status in ("OK", "EMPTY"):
        row = store.conn.execute(
            "SELECT payload FROM snapshots LIMIT 1").fetchone()
        if row:
            live_sample = json.loads(row["payload"])
    live_counts = Counter(s["signal_type"]
                          for s in store.get_signals(avenue=AVENUE))
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture = {
        "source_id": SOURCE_ID,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "synthetic": live_sample is None,
        "note": ("live listing snapshot" if live_sample else
                 "live scrape unavailable (" + (result.error or result.status)
                 + "); sample is the embedded real-format parser fixture"),
        "sample_listing": live_sample or sample,
        "synthetic_exercise_counts": dict(by_type),
    }
    fixture_path = fixtures_dir / f"{SOURCE_ID}_sample.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, default=str),
                            encoding="utf-8")

    print(f"  live collect (last 30d): status={result.status} "
          f"signals={result.signals_added} entities={result.entities_seen}"
          + (f" error={result.error}" if result.error else ""))
    if live_counts:
        print(f"  live signal counts: {dict(live_counts)}")
    print(f"  synthetic signal counts: {dict(by_type)} "
          f"(total {synthetic_total})")
    print(f"  fixture saved: {fixture_path}")
    print(f"  RESULT: {result.status}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="run offline logic tests + a live 30-day collect "
                             "into a throwaway store; writes nothing but "
                             "fixtures/<source_id>_sample.json")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    parser.print_help()
