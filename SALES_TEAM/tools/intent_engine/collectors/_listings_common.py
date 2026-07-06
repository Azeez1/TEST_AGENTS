"""Shared plumbing for dead_listings avenue collectors (business-for-sale sites).

Used by listings_bizbuysell (the reference collector) and every listings_* site
collector. Leading underscore keeps load_collectors() from ever importing this
as a collector module.

Provides:
    parse_price(text)         '$1,350,000' / '$1.6m' / '$258.5k' / '$1M - $5M'
                              (range -> midpoint) -> int or None
    LISTING_SITES             source_id -> {prefix, priority} for cross-site work
    CrossSiteDeduper          conservative cross-site listing dedupe (see below)
    enrich_brokers(...)       bounded, throttled detail-page broker fill-in
    diff_and_emit(...)        snapshot-diff -> stale_180d / price_cut / relisting
                              signal emission (single implementation, all sites)
    ListingSiteCollector      base class implementing the collect() contract
    synthetic_exercise(...)   shared self-test scenario for the diff logic
    dedupe_exercise()         shared self-test scenario for cross-site dedupe
    run_live_self_test(...)   shared live-collect + fixture-save harness

Cross-site dedupe design (conservative — flag, don't over-merge):
    The same business is routinely cross-posted on several listing sites. A
    listing fingerprint = (metro, sorted distinctive title tokens, asking-price
    bucket of $250K). Only an EXACT fingerprint match merges: the signal then
    carries the canonical entity_key of the highest-priority site (BizBuySell
    first — LoopNet/BizQuest share its numeric ids anyway) plus source_refs
    listing every cross-site URL. A fuzzy match (token Jaccard >= 0.6 and
    price within 10%) is only FLAGGED via attrs (xsite_match="uncertain",
    xsite_possible_duplicate=...) and never merged. Candidates come from other
    listing sources' snapshots in the shared store (read-only), so within one
    weekly scan later collectors dedupe against earlier ones from the same day
    and against every site's snapshots from prior weeks.
"""
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
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from common.normalize import normalize_name  # noqa: E402

AVENUE = "dead_listings"

PRICE_MIN = 1_000_000
PRICE_MAX = 10_000_000
STALE_DAYS = 180
RELIST_MIN_GAP_DAYS = 21
PRICE_CUT_MIN_DROP = 0.005          # ignore <0.5% wiggles
BROKER_COFFEE_THRESHOLD = 2
DETAIL_FETCH_CAP = 10               # max detail-page fetches per metro per run
PRICE_BUCKET = 250_000
FUZZY_JACCARD_MIN = 0.6
FUZZY_PRICE_TOLERANCE = 0.10
XSITE_WINDOW_DAYS = 45              # ignore other-site snapshots older than this

# Site priority decides which entity_key becomes canonical on an exact match.
# BizQuest and LoopNet are CoStar skins of BizBuySell and share its numeric
# listing ids, so they use the same "bbs" prefix (identical entity keys).
LISTING_SITES = {
    "listings_bizbuysell":        {"prefix": "bbs", "priority": 0},
    "listings_bizquest":          {"prefix": "bbs", "priority": 1},
    "listings_loopnet":           {"prefix": "bbs", "priority": 2},
    "listings_businessesforsale": {"prefix": "bfs", "priority": 3},
    "listings_businessbroker":    {"prefix": "bbn", "priority": 4},
    "listings_sunbelt":           {"prefix": "snb", "priority": 5},
    "listings_murphy":            {"prefix": "mur", "priority": 6},
    "listings_dealstream":        {"prefix": "dst", "priority": 7},
}


# ---------------------------------------------------------------------------
# price parsing
# ---------------------------------------------------------------------------

_NUM_RE = re.compile(r"\$?\s*(\d[\d,]*(?:\.\d+)?)\s*([kKmM])?")


def _one_price(text):
    m = _NUM_RE.search(text or "")
    if not m:
        return None
    try:
        num = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    suffix = (m.group(2) or "").lower()
    if suffix == "k":
        num *= 1_000
    elif suffix == "m":
        num *= 1_000_000
    n = int(round(num))
    return n if n > 0 else None


def parse_price(val):
    """Coerce any listing-price representation to int dollars (or None).

    Handles '$1,350,000', 1350000.0, '$1.600m', '$850k', '$258.5k', and ranges
    like '$1M - $5M' (midpoint). 'Not Disclosed' / 'N/A' / '' -> None.
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return int(val) if val > 0 else None
    s = str(val).strip()
    if not s or re.search(r"not\s+disclosed|n/?a|contact|inquire", s, re.I):
        return None
    parts = re.split(r"\s*[-–]\s*", s)
    if len(parts) == 2:
        lo, hi = _one_price(parts[0]), _one_price(parts[1])
        if lo and hi and hi >= lo:
            return int((lo + hi) / 2)
    return _one_price(s)


# ---------------------------------------------------------------------------
# cross-site dedupe
# ---------------------------------------------------------------------------

_GENERIC_TOKENS = frozenset("""
FOR SALE SELL SELLING BUSINESS BUSINESSES OPPORTUNITY COMPANY COMPANIES FIRM
ESTABLISHED PROFITABLE TURNKEY TURN KEY WELL SEMI ABSENTEE OWNER OPERATED
OPERATOR RUN GREAT EXCELLENT EXCEPTIONAL PREMIER PREMIUM HIGH STRONG GROWING
GROWTH POTENTIAL EARNINGS INCOME PRICED MOTIVATED SELLER REDUCED ASKING PRICE
INCLUDED REAL ESTATE PROPERTY SBA FINANCEABLE APPROVED CONFIDENTIAL ACTIVE
IN THE AND WITH OF A AN TO ON AT BY OR NEW BASED LOCAL LOCATED
TX GA TEXAS GEORGIA HOUSTON ATLANTA METRO AREA COUNTY CITY US USA
""".split())


def title_tokens(title):
    """Distinctive tokens from a listing title: normalized, generic sale-speak
    and metro/state words dropped, single letters dropped."""
    toks = normalize_name(title or "").split()
    return [t for t in toks if len(t) > 1 and t not in _GENERIC_TOKENS]


def listing_fingerprint(title, price, metro):
    """Exact-match fingerprint: metro | sorted distinctive tokens | $250K price
    bucket. Returns None when the title is too generic (<2 distinctive tokens)
    or the price is unknown — conservative: no fingerprint, no merge."""
    toks = sorted(set(title_tokens(title)))
    if len(toks) < 2 or not price:
        return None
    return f"{metro}|{'.'.join(toks)}|{int(price // PRICE_BUCKET)}"


class CrossSiteDeduper:
    """Resolve a listing to a canonical cross-site entity_key.

    Loads the latest snapshot per listing from every OTHER listing source in
    the store (read-only, last XSITE_WINDOW_DAYS days) and matches by
    fingerprint. See module docstring for merge/flag rules.
    """

    def __init__(self, store, own_source, window_days=XSITE_WINDOW_DAYS):
        self.own_source = own_source
        self.by_fp = {}
        self.by_metro = {}
        src_ids = [s for s in LISTING_SITES if s != own_source]
        if not src_ids:
            return
        cutoff = (date.today() - timedelta(days=window_days)).isoformat()
        qmarks = ",".join("?" * len(src_ids))
        try:
            rows = store.conn.execute(
                f"SELECT source_id, item_key, MAX(snapshot_date) AS sd, payload "
                f"FROM snapshots WHERE source_id IN ({qmarks}) "
                f"GROUP BY source_id, item_key HAVING sd >= ?",
                (*src_ids, cutoff),
            ).fetchall()
        except Exception:
            rows = []
        for r in rows:
            try:
                payload = json.loads(r["payload"])
            except (TypeError, ValueError):
                continue
            if not isinstance(payload, dict):
                continue
            metro = payload.get("metro") or ""
            if not metro:
                continue                      # pre-dedupe snapshots: skip, stay conservative
            title = payload.get("title") or ""
            price = parse_price(payload.get("asking_price"))
            site = LISTING_SITES[r["source_id"]]
            cand = {
                "source_id": r["source_id"],
                "priority": site["priority"],
                "entity_key": f"{site['prefix']}:{r['item_key']}",
                "url": payload.get("url", ""),
                "tokens": frozenset(title_tokens(title)),
                "price": price,
                "fp": listing_fingerprint(title, price, metro),
            }
            if cand["fp"]:
                self.by_fp.setdefault(cand["fp"], []).append(cand)
            self.by_metro.setdefault(metro, []).append(cand)

    def resolve(self, source_id, listing, metro):
        """Return (entity_key, xsite_attrs) for one parsed listing dict."""
        site = LISTING_SITES.get(source_id, {"prefix": source_id, "priority": 99})
        own_key = f"{site['prefix']}:{listing['listing_id']}"
        title = listing.get("title", "")
        price = parse_price(listing.get("asking_price"))
        fp = listing_fingerprint(title, price, metro)

        matches = self.by_fp.get(fp, []) if fp else []
        if matches:
            best = min(matches, key=lambda m: m["priority"])
            canonical = best["entity_key"] if best["priority"] < site["priority"] \
                else own_key
            refs = [listing.get("url", "")] + [m["url"] for m in matches]
            return canonical, {
                "xsite_match": "exact",
                "xsite_sources": sorted({source_id} | {m["source_id"] for m in matches}),
                "source_refs": [u for u in dict.fromkeys(refs) if u],
            }

        # fuzzy: FLAG only, never merge
        own_toks = frozenset(title_tokens(title))
        if own_toks and price:
            best, best_j = None, 0.0
            for c in self.by_metro.get(metro, []):
                if c["entity_key"] == own_key or not c["tokens"] or not c["price"]:
                    continue
                j = len(own_toks & c["tokens"]) / len(own_toks | c["tokens"])
                if (j >= FUZZY_JACCARD_MIN and j > best_j
                        and abs(price - c["price"])
                        <= FUZZY_PRICE_TOLERANCE * max(price, c["price"])):
                    best, best_j = c, j
            if best is not None:
                return own_key, {
                    "xsite_match": "uncertain",
                    "xsite_possible_duplicate": best["entity_key"],
                    "xsite_possible_source": best["source_id"],
                    "xsite_possible_ref": best["url"],
                    "xsite_jaccard": round(best_j, 2),
                }
        return own_key, {}


# ---------------------------------------------------------------------------
# unlocker helper
# ---------------------------------------------------------------------------

def unlock_with_retry(url, tries=2):
    """brightdata_unlock, retrying when the unlocker returns an empty 200 body
    (observed intermittently on BizBuySell detail pages, 2026-07-06)."""
    from common.http import brightdata_unlock
    body = ""
    for _ in range(max(1, tries)):
        body = brightdata_unlock(url)
        if body:
            return body
    return body


# ---------------------------------------------------------------------------
# bounded detail-page broker enrichment
# ---------------------------------------------------------------------------

def enrich_brokers(listings, fetch_html, parse_broker, cap=DETAIL_FETCH_CAP):
    """Fill missing listing['broker'] via per-listing detail-page fetches.

    listings:    iterable of listing dicts, mutated in place; caller pre-sorts
                 (oldest first) and pre-filters to the ones worth spending on.
    fetch_html:  url -> html string (common.http.fetch(...).text or
                 brightdata_unlock — both already throttle per domain).
    parse_broker: html -> broker string or "".
    cap:         hard bound on detail FETCH ATTEMPTS (not successes), so a run
                 stays cheap and polite no matter how many listings are stale.
    Per-listing errors are swallowed; returns number of attempts made.
    """
    attempts = 0
    for listing in listings:
        if attempts >= cap:
            break
        if listing.get("broker") or not listing.get("url"):
            continue
        attempts += 1
        try:
            html = fetch_html(listing["url"])
            broker = parse_broker(html) if html else ""
        except Exception:
            continue
        if broker:
            listing["broker"] = broker
            listing["broker_source"] = "detail_page"
    return attempts


# ---------------------------------------------------------------------------
# snapshot-diff signal emission (single implementation for every listing site)
# ---------------------------------------------------------------------------

def diff_and_emit(store, source_id, avenue, prefix, metro, listings, today,
                  stale_days=STALE_DAYS, relist_min_gap_days=RELIST_MIN_GAP_DAYS,
                  price_cut_min_drop=PRICE_CUT_MIN_DROP,
                  broker_coffee_threshold=BROKER_COFFEE_THRESHOLD, deduper=None):
    """Snapshot today's listings, diff against history, emit signals.

    Signals (identical semantics to the original listings_bizbuysell logic):
        stale_180d  age >= stale_days since first_seen; magnitude 1.0;
                    signal_date = the day the listing crossed the threshold.
        price_cut   asking price dropped vs latest prior snapshot (> min drop);
                    magnitude = min(1.0, pct_drop / 0.25).
        relisting   listing reappears after >= relist_min_gap_days absent;
                    magnitude = clamp(gap/90, 0.5, 1.0).
    Broker aggregation: a broker holding >= broker_coffee_threshold stale
    listings this run is a coffee target (attrs on the stale signals).
    deduper: optional CrossSiteDeduper — resolves canonical entity keys and
    attaches xsite_* attrs / source_refs.

    Returns (signals_added, entity_keys_set, Counter_by_signal_type).
    """
    today_iso = today.isoformat()
    added = 0
    entity_keys = set()
    by_type = Counter()
    stale = []          # (listing, crossed_iso, age_days)
    inline = []         # (listing, signal_type, signal_date, magnitude, extra)
    resolved = {}       # listing_id -> (entity_key, xsite_attrs)

    for listing in listings:
        lid = str(listing["listing_id"])
        prior = [s for s in store.get_snapshots(source_id, lid)
                 if s["snapshot_date"] < today_iso]
        listing.setdefault("metro", metro)
        store.add_snapshot(source_id, today_iso, lid, listing)
        if deduper is not None:
            ekey, xattrs = deduper.resolve(source_id, listing, metro)
        else:
            ekey, xattrs = f"{prefix}:{lid}", {}
        resolved[lid] = (ekey, xattrs)
        entity_keys.add(ekey)

        first = store.first_seen(source_id, lid)
        age = (today - date.fromisoformat(first)).days if first else 0
        if age >= stale_days:
            crossed = (date.fromisoformat(first)
                       + timedelta(days=stale_days)).isoformat()
            stale.append((listing, crossed, age))

        if prior:
            last = prior[-1]
            last_date = date.fromisoformat(last["snapshot_date"])
            payload = last["payload"] if isinstance(last["payload"], dict) else {}
            last_price = parse_price(payload.get("asking_price"))
            cur_price = parse_price(listing.get("asking_price"))
            if (last_price and cur_price
                    and cur_price < last_price * (1 - price_cut_min_drop)):
                drop = (last_price - cur_price) / last_price
                inline.append((listing, "price_cut", today_iso,
                               min(1.0, drop / 0.25),
                               {"prev_price": last_price,
                                "new_price": cur_price,
                                "drop_pct": round(drop * 100, 1)}))
            gap = (today - last_date).days
            if gap >= relist_min_gap_days:
                inline.append((listing, "relisting", today_iso,
                               max(0.5, min(1.0, gap / 90.0)),
                               {"gap_days": gap,
                                "last_seen": last["snapshot_date"]}))

    broker_counts = Counter(
        l.get("broker", "") for l, _, _ in stale if l.get("broker"))

    def emit(listing, signal_type, signal_date, magnitude, extra):
        nonlocal added
        lid = str(listing["listing_id"])
        ekey, xattrs = resolved[lid]
        attrs = {
            "asking_price": listing.get("asking_price"),
            "location": listing.get("location", ""),
            "broker": listing.get("broker", ""),
            "listing_url": listing.get("url", ""),
        }
        attrs.update(xattrs)
        attrs.update(extra)
        sig = Signal(
            entity_key=ekey,
            entity_name=listing.get("title", f"listing {lid}"),
            metro=metro,
            avenue=avenue,
            signal_type=signal_type,
            signal_date=signal_date,
            magnitude=round(float(magnitude), 3),
            source_id=source_id,
            source_ref=listing.get("url", ""),
            raw=dict(listing),
            attrs=attrs,
        )
        if store.add_signal(sig):
            added += 1
        by_type[signal_type] += 1

    for listing, crossed, age in stale:
        broker = listing.get("broker", "")
        n = broker_counts.get(broker, 0) if broker else 0
        emit(listing, "stale_180d", crossed, 1.0, {
            "days_on_market": age,
            "broker_stale_count": n,
            "coffee_target": n >= broker_coffee_threshold,
        })
    for listing, stype, sdate, mag, extra in inline:
        emit(listing, stype, sdate, mag, extra)

    return added, entity_keys, by_type


# ---------------------------------------------------------------------------
# base collector for listing sites
# ---------------------------------------------------------------------------

class ListingSiteCollector(BaseCollector):
    """collect() contract implementation shared by the listings_* collectors.

    Subclasses set source_id + prefix and implement _fetch_metro_listings().
    Optional: _fetch_detail_html/_parse_detail_broker for broker enrichment,
    requires_brightdata, blocked_reason (non-empty -> always SKIPPED),
    detail_fetch_cap.
    """
    avenue = AVENUE
    source_id = None
    prefix = None
    metros = ("houston", "atlanta")
    requires_brightdata = False
    blocked_reason = ""
    detail_fetch_cap = DETAIL_FETCH_CAP

    def _fetch_metro_listings(self, metro):
        """Return {listing_id: listing dict}. listing dict keys: listing_id,
        title, asking_price (int|None), url, broker, location, cash_flow."""
        raise NotImplementedError

    def _fetch_detail_html(self, url):          # pragma: no cover - per-site
        return None                             # None -> no broker enrichment

    def _parse_detail_broker(self, html):       # pragma: no cover - per-site
        return ""

    def _enrich_brokers(self, store, listings):
        if self.detail_fetch_cap <= 0:
            return 0
        if type(self)._fetch_detail_html is ListingSiteCollector._fetch_detail_html:
            return 0                            # subclass has no detail fetcher
        missing = [l for l in listings if not l.get("broker")]
        missing.sort(key=lambda l: store.first_seen(
            self.source_id, str(l["listing_id"])) or "9999-12-31")
        return enrich_brokers(missing, self._fetch_detail_html,
                              self._parse_detail_broker,
                              cap=self.detail_fetch_cap)

    def collect(self, since, store, registry):
        try:
            if self.blocked_reason:
                return CollectorResult(self.source_id, 0, 0, "SKIPPED",
                                       self.blocked_reason)
            if self.requires_brightdata and not config.get_env("BRIGHTDATA_API_TOKEN"):
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
                in_band = [l for l in listings.values()
                           if l.get("asking_price") is not None
                           and PRICE_MIN <= l["asking_price"] <= PRICE_MAX]
                try:
                    self._enrich_brokers(store, in_band)
                except Exception:
                    pass                        # enrichment is best-effort
                deduper = CrossSiteDeduper(store, own_source=self.source_id)
                added, keys, _ = diff_and_emit(
                    store, self.source_id, self.avenue, self.prefix, metro,
                    in_band, today, deduper=deduper)
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


# ---------------------------------------------------------------------------
# shared self-test pieces
# ---------------------------------------------------------------------------

def _mk_synth(lid, title, price, broker=""):
    return {"listing_id": lid, "title": title, "asking_price": price,
            "url": f"https://example.com/listing/{lid}/", "broker": broker,
            "location": "Houston, TX", "cash_flow": None, "metro": "houston",
            "parse_strategy": "synthetic"}


def synthetic_exercise(collector):
    """Prove days-on-market / price-cut / relisting / broker aggregation against
    a synthetic prior-snapshot history, for any listing collector."""
    from common.store import Store
    store = Store(":memory:")
    src, prefix = collector.source_id, collector.prefix
    today = date.today()

    def d(n):
        return (today - timedelta(days=n)).isoformat()

    # A: first seen 200d ago, still listed, price cut 2.5M -> 2.1M (stale+cut)
    store.add_snapshot(src, d(200), "9000001",
                       _mk_synth("9000001", "GULF FREIGHT CARRIERS", 2_500_000,
                                 "Gatsby Advisors"))
    store.add_snapshot(src, d(7), "9000001",
                       _mk_synth("9000001", "GULF FREIGHT CARRIERS", 2_500_000,
                                 "Gatsby Advisors"))
    # B: seen 60d and 40d ago, absent since -> reappears today (relisting)
    store.add_snapshot(src, d(60), "9000002",
                       _mk_synth("9000002", "BAYOU HVAC SERVICES", 1_800_000))
    store.add_snapshot(src, d(40), "9000002",
                       _mk_synth("9000002", "BAYOU HVAC SERVICES", 1_800_000))
    # C: first seen 190d ago, same broker as A -> broker coffee target
    store.add_snapshot(src, d(190), "9000003",
                       _mk_synth("9000003", "WESTSIDE MACHINE SHOP", 4_200_000,
                                 "Gatsby Advisors"))

    current = [
        _mk_synth("9000001", "GULF FREIGHT CARRIERS", 2_100_000, "Gatsby Advisors"),
        _mk_synth("9000002", "BAYOU HVAC SERVICES", 1_800_000),
        _mk_synth("9000003", "WESTSIDE MACHINE SHOP", 4_200_000, "Gatsby Advisors"),
    ]
    deduper = CrossSiteDeduper(store, own_source=src)
    added, keys, by_type = diff_and_emit(
        store, src, AVENUE, prefix, "houston", current, today, deduper=deduper)

    expect = {"stale_180d": 2, "price_cut": 1, "relisting": 2}
    assert dict(by_type) == expect, f"got {dict(by_type)}, want {expect}"
    assert added == 5, f"expected 5 inserted signals, got {added}"
    assert len(keys) == 3, keys

    sigs = store.get_signals(avenue=AVENUE)
    coffee = [s for s in sigs if s["signal_type"] == "stale_180d"
              and json.loads(s["attrs"]).get("coffee_target")]
    assert len(coffee) == 2, "both Gatsby stale listings must be coffee targets"
    cut = next(s for s in sigs if s["signal_type"] == "price_cut")
    assert abs(cut["magnitude"] - min(1.0, (400000 / 2500000) / 0.25)) < 1e-6

    added2, _, _ = diff_and_emit(
        store, src, AVENUE, prefix, "houston", current, today, deduper=deduper)
    assert added2 == 0, f"rerun must dedup, added {added2}"

    print(f"  synthetic snapshots: {dict(by_type)}  coffee_targets={len(coffee)}"
          f"  rerun_dedup=OK")
    store.close()
    return by_type


def dedupe_exercise():
    """Prove cross-site dedupe: exact fingerprint merges to the higher-priority
    site's entity_key; near-miss only flags; unrelated listing untouched."""
    from common.store import Store
    store = Store(":memory:")
    today = date.today().isoformat()
    store.add_snapshot("listings_bizbuysell", today, "2511364", {
        "listing_id": "2511364",
        "title": "Profitable Turnkey Active Freight Trucking Company - Active Amazon R.",
        "asking_price": 1_350_000,
        "url": "https://www.bizbuysell.com/business-opportunity/x/2511364/",
        "broker": "", "location": "Houston, TX", "metro": "houston"})

    ded = CrossSiteDeduper(store, own_source="listings_businessesforsale")

    # exact: same distinctive tokens + same $250K bucket -> merge onto bbs key
    key, attrs = ded.resolve("listings_businessesforsale", {
        "listing_id": "3970513",
        "title": "Active Freight Trucking Company Turnkey Amazon",
        "asking_price": 1_350_000,
        "url": "https://us.businessesforsale.com/us/x.aspx"}, "houston")
    assert key == "bbs:2511364", key
    assert attrs["xsite_match"] == "exact", attrs
    assert len(attrs["source_refs"]) == 2, attrs

    # near-miss: overlapping but not identical tokens -> FLAG, keep own key
    key2, attrs2 = ded.resolve("listings_businessesforsale", {
        "listing_id": "3970999",
        "title": "Active Freight Trucking Fleet Amazon",
        "asking_price": 1_400_000,
        "url": "https://us.businessesforsale.com/us/y.aspx"}, "houston")
    assert key2 == "bfs:3970999", key2
    assert attrs2.get("xsite_match") == "uncertain", attrs2
    assert attrs2["xsite_possible_duplicate"] == "bbs:2511364", attrs2

    # unrelated listing -> own key, no attrs
    key3, attrs3 = ded.resolve("listings_businessesforsale", {
        "listing_id": "3971000",
        "title": "Dental Practice Two Locations",
        "asking_price": 2_000_000,
        "url": "https://us.businessesforsale.com/us/z.aspx"}, "houston")
    assert key3 == "bfs:3971000" and attrs3 == {}, (key3, attrs3)

    print("  cross-site dedupe: exact merge -> bbs key, near-miss flagged, "
          "unrelated untouched  OK")
    store.close()


def run_live_self_test(collector, source_id, offline_sample,
                       synthetic_counts=None):
    """Shared self-test tail: run a real collect() over the last 30 days into a
    throwaway in-memory store, print honest counts, save the fixture. Writes
    NOTHING to the sheet. Returns the CollectorResult."""
    from common.store import Store
    since = date.today() - timedelta(days=30)
    registry = config.load_registry()
    store = Store(":memory:")
    result = collector.collect(since, store, registry)

    live_sample = None
    if result.status in ("OK", "EMPTY"):
        row = store.conn.execute(
            "SELECT payload FROM snapshots WHERE source_id=? LIMIT 1",
            (source_id,)).fetchone()
        if row:
            live_sample = json.loads(row["payload"])
    live_counts = Counter(s["signal_type"] for s in store.get_signals(avenue=AVENUE))
    snap_count = store.conn.execute(
        "SELECT COUNT(*) AS n FROM snapshots WHERE source_id=?",
        (source_id,)).fetchone()["n"]
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    if result.status == "SKIPPED":
        note = "collector intentionally disabled/skipped: " + (result.error or "")
    elif live_sample:
        note = "live listing snapshot"
    else:
        note = ("live scrape unavailable (" + (result.error or result.status)
                + "); sample is the embedded real-format parser fixture")
    fixture = {
        "source_id": source_id,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "live_error": result.error,
        "live_snapshots": snap_count,
        "synthetic": live_sample is None,
        "note": note,
        "sample_listing": live_sample or offline_sample,
        "synthetic_exercise_counts": dict(synthetic_counts or {}),
    }
    fixture_path = fixtures_dir / f"{source_id}_sample.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, default=str),
                            encoding="utf-8")

    print(f"  live collect (last 30d): status={result.status} "
          f"signals={result.signals_added} entities={result.entities_seen} "
          f"snapshots={snap_count}"
          + (f" error={result.error}" if result.error else ""))
    if live_counts:
        print(f"  live signal counts: {dict(live_counts)}")
    print(f"  fixture saved: {fixture_path}")
    print(f"  RESULT: {result.status}")
    return result


def _self_test():
    print("[_listings_common] --self-test (offline unit checks only)")
    assert parse_price("$1,350,000") == 1_350_000
    assert parse_price("$1.600m") == 1_600_000
    assert parse_price("$850k") == 850_000
    assert parse_price("$258.5k") == 258_500
    assert parse_price("$1M - $5M") == 3_000_000
    assert parse_price("$100K - $250K") == 175_000
    assert parse_price("Not Disclosed") is None
    assert parse_price(None) is None
    assert parse_price(2_500_000.0) == 2_500_000
    print("  parse_price: 9 cases OK")
    dedupe_exercise()

    class _Probe(ListingSiteCollector):
        source_id = "listings_bizbuysell"
        prefix = "bbs"

    synthetic_exercise(_Probe())
    print("  RESULT: OK")
    return 0


if __name__ == "__main__":
    sys.exit(_self_test())
