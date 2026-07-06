"""timing_trajectory — receptiveness windows derived from EXISTING store history.

Avenue:    mechanical (also emits property_mgmt signals — see below)
Metro:     houston
Source id: timing_trajectory
Emits:     permit_growth_window, eviction_spike_window   (registry "timing_signals")

NO NETWORK. This collector reads snapshots that permits_houston (mechanical)
and evictions_harris (property_mgmt) already write via store.add_snapshot and
turns trajectory changes into v2 TIMING signals:

  permit_growth_window  (mechanical / houston)
      A permit buyer's trailing 3 COMPLETE calendar months of mechanical
      permits is >= ACCEL_THRESHOLD (30%) above the immediately preceding 3
      months (or the preceding quarter is 0 with real current volume), with
      at least MIN_TRAILING_JOBS jobs. Receptiveness: they are scaling RIGHT
      NOW. This intentionally differs from permits_houston's
      permit_volume_growth PAIN signal (trailing quarter vs the SAME quarter
      one year earlier): quarter-over-quarter acceleration needs only 6
      backfilled months and captures "busy now", seasonality included.
      Until >= 6 complete months exist in the store the permits half reports
      an honest "months not yet backfilled" note and emits nothing.

  eviction_spike_window  (property_mgmt / houston)
      A landlord's latest filing window (<= RECENT_MAX_AGE_DAYS old) shows
      weekly_rate >= baseline + MIN_EXCESS_WEEKLY, where baseline = mean
      weekly_rate of NON-OVERLAPPING prior windows (window_end <= the recent
      window's start — stricter than evictions_harris's own baseline, which
      is overlap-blind). First sight (no usable baseline) requires
      weekly_rate >= FIRST_RUN_MIN_WEEKLY. Thresholds mirror
      collectors/evictions_harris.py so the two stay calibrated together.
      Receptiveness: acute operational pain right now.
      A per-entity emit cooldown (EMIT_COOLDOWN_DAYS, tracked via this
      collector's OWN snapshots) prevents a persistent spike from emitting a
      near-duplicate signal every daily run.

Cross-avenue note: one collector module maps to one source_id and one gating
`avenue`, but each Signal carries its own natural avenue (frozen v2 contract
point 5) — permit signals go out under "mechanical", eviction signals under
"property_mgmt". Skipping this collector by selecting neither avenue is only
possible with --avenues filters that exclude mechanical.

Atlanta: not covered yet by construction — permits_atlanta is disabled (no
contractor field in the city's ArcGIS layer) and evictions_fulton is disabled
(re:SearchGA login wall), so there are no Atlanta snapshots to derive from.
Add ("permits_atlanta", "atlanta") / ("evictions_fulton", "atlanta") to
PERMIT_SOURCES / EVICTION_SOURCES when those collectors come online.

Store-API note: the frozen Store interface has no item_key enumeration
(get_snapshots requires the key up front). permits_houston writes an
"__entity_index__" sentinel per month, which this collector uses via plain
get_snapshots. evictions_harris has no such index, so _snapshot_item_keys()
falls back to ONE read-only SELECT DISTINCT item_key against the same
snapshots table get_snapshots reads — it writes nothing, scores nothing,
exports nothing.

Self-test (in-memory stores only; real DB opened READ-ONLY and cloned):
    python -m collectors.timing_trajectory --self-test
1) asserts the detection logic on synthetic snapshot histories, then
2) clones the real store's permits/evictions snapshots into a throwaway
   in-memory store and reports what a live run would emit.
Saves fixtures/timing_trajectory_sample.json. Writes NOTHING to sheet/real DB.
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

_ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors.evictions_harris import (_query_params,  # noqa: E402
                                         _query_url)
from common.normalize import entity_key as make_entity_key  # noqa: E402

# (source_id_to_read, metro) pairs; extend when Atlanta sources come online
PERMIT_SOURCES = (("permits_houston", "houston"),)
EVICTION_SOURCES = (("evictions_harris", "houston"),)

# permits_houston snapshot sentinels (mirrored constants)
MONTH_SENTINEL = "__month_complete__"
ENTITY_INDEX = "__entity_index__"
PERMITS_LAUNCH_URL = ("http://cohtora.houstontx.gov/approot/soldpermits/"
                      "online_permit.htm")

# permit-acceleration calibration (MIN_TRAILING_JOBS mirrors permits_houston)
MIN_TRAILING_JOBS = 4
ACCEL_THRESHOLD = 0.30

# eviction-spike calibration (mirrors collectors/evictions_harris.py)
MIN_FILINGS_ABS = 3
FIRST_RUN_MIN_WEEKLY = 5.0
MIN_EXCESS_WEEKLY = 2.0
FULL_SCALE_EXCESS = 15.0
MAGNITUDE_FLOOR = 0.05
RECENT_MAX_AGE_DAYS = 45          # latest eviction window must be this fresh
EMIT_COOLDOWN_DAYS = 14           # per-entity re-emit cooldown (own snapshots)


# ---------------------------------------------------------------- utilities

def _month_start(d):
    return d.replace(day=1)


def _add_months(mstart, n):
    y = mstart.year + (mstart.month - 1 + n) // 12
    m = (mstart.month - 1 + n) % 12 + 1
    return date(y, m, 1)


def _month_end(mstart):
    return _add_months(mstart, 1) - timedelta(days=1)


def _parse_iso(value):
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _snapshot_item_keys(store, source_id):
    """READ-ONLY enumeration of a source's snapshot item_keys.

    The frozen Store API cannot list item_keys (get_snapshots needs the key),
    so this is one SELECT DISTINCT against the same table get_snapshots
    reads. No writes, no scoring, no export.
    """
    try:
        cur = store.conn.execute(
            "SELECT DISTINCT item_key FROM snapshots WHERE source_id=?",
            (source_id,))
        return [r[0] for r in cur.fetchall()]
    except Exception:
        return []


# ---------------------------------------------------- permit acceleration

def evaluate_permit_acceleration(store, source_id, metro, today, notes):
    """Quarter-over-quarter permit acceleration -> permit_growth_window Signals."""
    cur = _month_start(today)
    trailing = [_add_months(cur, -3), _add_months(cur, -2), _add_months(cur, -1)]
    prev = [_add_months(m, -3) for m in trailing]
    complete = {s["snapshot_date"]
                for s in store.get_snapshots(source_id, MONTH_SENTINEL)}
    missing = [m.isoformat() for m in trailing + prev
               if m.isoformat() not in complete]
    if missing:
        notes.append(f"{source_id}: permit half skipped, months not yet "
                     f"backfilled: {','.join(missing)}")
        return []

    t_keys = {m.isoformat() for m in trailing}
    names = set()
    for snap in store.get_snapshots(source_id, ENTITY_INDEX):
        if snap["snapshot_date"] in t_keys:
            names.update(snap["payload"].get("entities", []))

    q_label = f"{trailing[0]:%Y%m}-{trailing[-1]:%Y%m}"
    signal_date = _month_end(trailing[-1]).isoformat()
    last_12 = [_add_months(cur, -i) for i in range(1, 13)]
    have_12 = all(m.isoformat() in complete for m in last_12)

    signals = []
    for nn in sorted(names):
        snaps = {s["snapshot_date"]: s["payload"]
                 for s in store.get_snapshots(source_id, nn)}
        t = sum(snaps.get(m.isoformat(), {}).get("count", 0) for m in trailing)
        p = sum(snaps.get(m.isoformat(), {}).get("count", 0) for m in prev)
        if t < MIN_TRAILING_JOBS:
            continue
        if p > 0:
            growth = t / p - 1.0
            if growth < ACCEL_THRESHOLD:
                continue
            magnitude = min(1.0, 0.25 + 0.75 * (growth - ACCEL_THRESHOLD)
                            / (2.0 - ACCEL_THRESHOLD))
            growth_pct = round(growth * 100.0, 1)
        else:
            magnitude = 1.0          # 0 -> t jobs: brand-new/expanding buyer
            growth_pct = None
        display, zip5, address = nn.upper(), "", ""
        for m in trailing:
            pl = snaps.get(m.isoformat(), {})
            display = pl.get("name", display) or display
            zip5 = pl.get("zip", zip5) or zip5
            address = pl.get("address", address) or address
        attrs = {"street": address or None, "zip": zip5 or None}
        if have_12:
            attrs["permit_count_12m"] = sum(
                snaps.get(m.isoformat(), {}).get("count", 0) for m in last_12)
        monthly = {m.isoformat(): snaps.get(m.isoformat(), {}).get("count", 0)
                   for m in prev + trailing}
        signals.append(Signal(
            entity_key=make_entity_key(display, zip5),
            entity_name=display,
            metro=metro,
            avenue="mechanical",
            signal_type="permit_growth_window",
            signal_date=signal_date,
            magnitude=round(magnitude, 3),
            source_id="timing_trajectory",
            source_ref=f"hpc-sold-permits-accel:{nn}:{q_label}",
            raw={
                "buyer": display,
                "trailing_quarter_jobs": t,
                "previous_quarter_jobs": p,
                "qoq_growth_pct": growth_pct,
                "monthly_counts": monthly,
                "evidence_url": PERMITS_LAUNCH_URL,
                "verify_hint": "search Buyer's Name on the HPC Sold Permits "
                               "page to reproduce",
            },
            attrs=attrs,
        ))
    return signals


# ------------------------------------------------------- eviction spikes

def evaluate_eviction_spikes(store, source_id, metro, today, notes):
    """Latest-window eviction spike vs non-overlapping baseline ->
    eviction_spike_window Signals (cooldown-gated)."""
    keys = [k for k in _snapshot_item_keys(store, source_id)
            if not k.startswith("__")]
    if not keys:
        notes.append(f"{source_id}: no eviction snapshots in store yet")
        return []
    signals = []
    for ekey in keys:
        snaps = store.get_snapshots(source_id, ekey)   # ordered by date asc
        if not snaps:
            continue
        latest = snaps[-1]
        pl = latest["payload"]
        if not isinstance(pl, dict):
            continue
        w_end = _parse_iso(pl.get("window_end")) or _parse_iso(
            latest["snapshot_date"])
        w_start = _parse_iso(pl.get("window_start"))
        if w_end is None or (today - w_end).days > RECENT_MAX_AGE_DAYS:
            continue
        filings = int(pl.get("filings") or 0)
        rate = float(pl.get("weekly_rate") or 0.0)
        if filings < MIN_FILINGS_ABS:
            continue
        prior_rates = []
        for s in snaps[:-1]:
            spl = s["payload"]
            if not isinstance(spl, dict):
                continue
            p_end = _parse_iso(spl.get("window_end")) or _parse_iso(
                s["snapshot_date"])
            if w_start is not None and p_end is not None and p_end <= w_start:
                prior_rates.append(float(spl.get("weekly_rate") or 0.0))
        if prior_rates:
            baseline = sum(prior_rates) / len(prior_rates)
            excess = rate - baseline
            if excess < MIN_EXCESS_WEEKLY:
                continue
        else:
            baseline = None
            if rate < FIRST_RUN_MIN_WEEKLY:
                continue
            excess = rate

        # cooldown: skip if we emitted for this entity in the last N days
        last_emits = store.get_snapshots("timing_trajectory", ekey)
        if last_emits:
            last = _parse_iso(last_emits[-1]["snapshot_date"])
            if last and (today - last).days < EMIT_COOLDOWN_DAYS:
                continue

        magnitude = max(MAGNITUDE_FLOOR,
                        min(1.0, excess / FULL_SCALE_EXCESS))
        zip5 = ekey.rsplit("|", 1)[-1] if "|" in ekey else ""
        name = pl.get("plaintiff_name") or ekey
        url = _query_url(_query_params(w_start or w_end, w_end))
        signals.append(Signal(
            entity_key=ekey,
            entity_name=name,
            metro=metro,
            avenue="property_mgmt",
            signal_type="eviction_spike_window",
            signal_date=w_end.isoformat(),
            magnitude=round(magnitude, 3),
            source_id="timing_trajectory",
            source_ref=url,
            raw={
                "filings_in_window": filings,
                "window": [w_start.isoformat() if w_start else None,
                           w_end.isoformat()],
                "weekly_rate": round(rate, 3),
                "baseline_weekly": (round(baseline, 3)
                                    if baseline is not None else None),
                "excess_weekly": round(excess, 3),
                "n_baseline_windows": len(prior_rates),
            },
            attrs={"zip": zip5 or None},
        ))
    return signals


# ------------------------------------------------------------------ collector

class Collector(BaseCollector):
    avenue = "mechanical"          # gating avenue; signals carry their own
    source_id = "timing_trajectory"
    metros = ("houston",)

    def collect(self, since, store, registry):
        today = date.today()
        signals_added = 0
        entities = set()
        notes = []
        try:
            for src, metro in PERMIT_SOURCES:
                for sig in evaluate_permit_acceleration(store, src, metro,
                                                        today, notes):
                    if store.add_signal(sig):
                        signals_added += 1
                    entities.add(sig.entity_key)
            for src, metro in EVICTION_SOURCES:
                for sig in evaluate_eviction_spikes(store, src, metro,
                                                    today, notes):
                    if store.add_signal(sig):
                        signals_added += 1
                    entities.add(sig.entity_key)
                    # cooldown marker (own snapshot namespace)
                    store.add_snapshot(self.source_id, today.isoformat(),
                                       sig.entity_key,
                                       {"emitted": sig.signal_date,
                                        "type": sig.signal_type})
            status = "OK" if signals_added else "EMPTY"
            return CollectorResult(self.source_id, signals_added,
                                   len(entities), status,
                                   error="; ".join(notes))
        except Exception as exc:  # noqa: BLE001 — contract: never raise
            return CollectorResult(self.source_id, signals_added,
                                   len(entities), "ERROR",
                                   error=f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


# ---------------------------------------------------------------------- #
#  self-test                                                             #
# ---------------------------------------------------------------------- #

def _inject_synthetic(store, today):
    """Synthetic snapshot histories exercising every detection branch."""
    cur = _month_start(today)
    months = [_add_months(cur, -i) for i in range(6, 0, -1)]   # 6 complete
    counts = {
        "accelerating hvac": [2, 2, 2, 4, 5, 6],   # 6 -> 15 jobs: fires
        "flat mechanical":   [3, 3, 3, 3, 3, 3],   # flat: must NOT fire
        "tiny shop":         [0, 0, 0, 1, 1, 1],   # 3 jobs < min: NOT fire
    }
    for i, m in enumerate(months):
        ents = []
        for nn, series in counts.items():
            if series[i]:
                store.add_snapshot("permits_houston", m.isoformat(), nn, {
                    "month": m.strftime("%Y-%m"), "name": nn.upper(),
                    "count": series[i], "zip": "77002",
                    "address": "123 MAIN ST HOUSTON TX 77002"})
                ents.append(nn)
        store.add_snapshot("permits_houston", m.isoformat(), ENTITY_INDEX,
                           {"entities": ents})
        store.add_snapshot("permits_houston", m.isoformat(), MONTH_SENTINEL,
                           {"rows": 99})

    def evict(ekey, name, end_offset, filings, rate):
        w_end = today - timedelta(days=end_offset)
        w_start = w_end - timedelta(days=30)
        store.add_snapshot("evictions_harris", w_end.isoformat(), ekey, {
            "window_start": w_start.isoformat(),
            "window_end": w_end.isoformat(),
            "filings": filings, "weekly_rate": rate,
            "plaintiff_name": name})

    # spiking landlord: baseline ~1.0/wk, latest 8.0/wk -> fires
    evict("biz:spike apartments|77001", "Spike Apartments LLC", 70, 4, 1.0)
    evict("biz:spike apartments|77001", "Spike Apartments LLC", 35, 4, 1.1)
    evict("biz:spike apartments|77001", "Spike Apartments LLC", 2, 34, 8.0)
    # calm landlord: steady 1.0/wk -> must NOT fire
    evict("biz:calm homes|77002", "Calm Homes LLC", 70, 4, 1.0)
    evict("biz:calm homes|77002", "Calm Homes LLC", 2, 4, 1.0)
    # first-sight acute landlord: no baseline, 7.2/wk -> fires
    evict("biz:acute villas|77003", "Acute Villas LP", 3, 31, 7.2)
    # first-sight mild landlord: no baseline, 2.0/wk -> must NOT fire
    evict("biz:mild manor|77004", "Mild Manor LLC", 3, 8, 2.0)


def _clone_real_snapshots(mem_store):
    """Copy permits/evictions snapshots from the real DB (opened READ-ONLY)
    into an in-memory store. Returns rows copied, or None if no real DB."""
    import sqlite3

    import config
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        return None
    src = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    src.row_factory = sqlite3.Row
    n = 0
    wanted = [s for s, _ in PERMIT_SOURCES] + [s for s, _ in EVICTION_SOURCES]
    marks = ",".join("?" for _ in wanted)
    for r in src.execute(
            f"SELECT source_id, snapshot_date, item_key, payload "
            f"FROM snapshots WHERE source_id IN ({marks})", wanted):
        try:
            payload = json.loads(r["payload"])
        except (TypeError, ValueError):
            continue
        mem_store.add_snapshot(r["source_id"], r["snapshot_date"],
                               r["item_key"], payload)
        n += 1
    src.close()
    return n


def _self_test():
    from common.store import Store

    today = date.today()
    print(f"[self-test] {Collector.source_id}: synthetic-logic pass")
    store = Store(db_path=":memory:")
    _inject_synthetic(store, today)
    res = Collector().collect(today - timedelta(days=30), store, {})
    got = {(s["signal_type"], s["entity_name"])
           for s in store.get_signals()}
    print(f"  status={res.status} signals_added={res.signals_added} "
          f"entities_seen={res.entities_seen}")
    for t, n in sorted(got):
        print(f"    {t}: {n}")
    assert ("permit_growth_window", "ACCELERATING HVAC") in got, got
    assert not any(n == "FLAT MECHANICAL" for _, n in got), got
    assert not any(n == "TINY SHOP" for _, n in got), got
    assert ("eviction_spike_window", "Spike Apartments LLC") in got, got
    assert ("eviction_spike_window", "Acute Villas LP") in got, got
    assert not any(n == "Calm Homes LLC" for _, n in got), got
    assert not any(n == "Mild Manor LLC" for _, n in got), got
    # cooldown: immediate second run emits nothing new for evictions
    res2 = Collector().collect(today - timedelta(days=30), store, {})
    assert res2.signals_added == 0, res2
    print("  synthetic assertions PASS (incl. dedup/cooldown on rerun)")
    example_signals = store.get_signals()[:3]
    store.close()

    print("[self-test] real-store read-only clone pass")
    real_report = {}
    try:
        mem = Store(db_path=":memory:")
        copied = _clone_real_snapshots(mem)
        if copied is None:
            real_report = {"note": "real DB not found; skipped"}
            print("  real DB not found; skipped")
        else:
            r = Collector().collect(today - timedelta(days=30), mem, {})
            by_type = {}
            for s in mem.get_signals():
                by_type[s["signal_type"]] = by_type.get(s["signal_type"], 0) + 1
            real_report = {"snapshots_cloned": copied, "status": r.status,
                           "signals_added": r.signals_added,
                           "by_type": by_type, "notes": r.error}
            print(f"  cloned {copied} snapshots -> status={r.status} "
                  f"signals_added={r.signals_added} by_type={by_type}")
            if r.error:
                print(f"  notes: {r.error}")
        mem.close()
    except Exception as exc:  # noqa: BLE001 — self-test must finish
        real_report = {"error": f"{type(exc).__name__}: {exc}"}
        print(f"  real-store pass failed: {real_report['error']}")

    fixtures = _ENGINE_ROOT / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    out = fixtures / f"{Collector.source_id}_sample.json"
    out.write_text(json.dumps({
        "note": "derived collector — reads permits_houston/evictions_harris "
                "snapshots already in the store; no network",
        "synthetic_example_signals": example_signals,
        "real_store_dry_pass": real_report,
    }, indent=1, default=str), encoding="utf-8")
    print(f"fixture saved: {out}")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print("Usage: python -m collectors.timing_trajectory --self-test")
