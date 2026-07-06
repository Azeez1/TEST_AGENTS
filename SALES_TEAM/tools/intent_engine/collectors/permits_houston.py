"""permits_houston — Houston mechanical-permit volume growth collector.

Avenue:    mechanical   (Meridian demo)
Source id: permits_houston
Metro:     houston

PINNED SOURCE (verified live 2026-07-05):
    POST https://cohtora.houstontx.gov/ibi_apps/WFServlet
    form fields: IBIF_ex=online_per_se.fex, IBIAPP_app=soldpermits,
                 IBIC_server=EDASERVE, SELTD=PT (search by permit type),
                 PTYPE=14 (Mechanical), BDT/EDT dates as YYYY/MM/DD (WebFOCUS
                 YYMD), WFFMT=HTML.
    Launch page: http://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm
    (linked from houstonpermittingcenter.org "Sold Permits Search").

Why not an ArcGIS FeatureServer: the COHGIS hub (cohgis-mycity.opendata.arcgis.com,
org NummVBqZSIJKUeVR) exposes NO permit-level layer — the "ILMS Permits Dataset"
web map points at a retired service (mycity.houstontx.gov/arcgisv91/.../PD/
Permits_wm/MapServer, now 404) and the only permit layers are stale analyst
extracts (SF_2015_to_2021, ActivePermits_SZ) without buyer fields. The
data.houstontx.gov CKAN permit datasets end in 2013. The Sold Permits Search is
the only live, date-filterable permit-level source.

Source semantics and caveats:
  * The response is a WebFOCUS "Active Report": data rows are embedded in the
    HTML as a string table (ARstrings) plus row index arrays (T_cont). At most
    100 rows are embedded per query, but the TRUE match count is reported in
    the header, so windows are subdivided until each returns <= 100 rows.
  * The public report exposes the permit BUYER in the OWNER_OCCUPANT column
    (business buyers are prefixed with '*'); a separate "contractor of record"
    field is NOT public. Repeat business buyers of mechanical permits are the
    entities tracked. Individual owner-occupants (no '*' prefix) are skipped.
  * The servlet must be POSTed to: a GET renders the fex source instead of
    running the report (verified). common/http.fetch is GET-only, so this
    module holds a narrow POST wrapper that reuses common/http's throttle
    table, User-Agent, retry and backoff constants — it does not re-implement
    policy, only the verb.

Time-series design:
  * Only COMPLETE calendar months are fetched and snapshotted
    (snapshots: item_key = normalized buyer name, snapshot_date = month start,
    payload = {count, zip, ...}; plus per-month "__entity_index__" and
    "__month_complete__" sentinel rows for enumeration/resumability).
  * permit_volume_growth fires when a buyer's trailing complete quarter is
    >30% above the same quarter one year earlier (or year-ago quarter is 0).
    Needs a backfill first:  --backfill  == run with `since` ~15-24 months
    back; months are fetched newest/priority first and the run is resumable
    (completed months are skipped via sentinels).

Self-test:
    python -m collectors.permits_houston --self-test
collects the last 30 days into an in-memory store, prints counts, saves
fixtures/permits_houston_sample.json and writes NOTHING to any sheet.
"""
import json
import re
import sys
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from common import http as _http  # noqa: E402
from common.normalize import clean_zip, entity_key, normalize_name  # noqa: E402

SERVLET_URL = "https://cohtora.houstontx.gov/ibi_apps/WFServlet"
LAUNCH_URL = "http://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm"
PTYPE_MECHANICAL = "14"        # option list on the launch page: 11 Electrical,
                               # 12 Plumbing, 13 Structural, 14 Mechanical, ...
ROW_CAP = 100                  # Active Report embeds at most 100 data rows
TARGET_ROWS = 85               # aim under the cap when sizing windows
MAX_REQUESTS = 600             # per-run request budget (resumable via sentinels)
BACKFILL_FLOOR_MONTHS = 24     # never fetch further back than this
MIN_TRAILING_JOBS = 4          # ignore tiny-volume buyers (1 -> 2 jobs = noise)
GROWTH_THRESHOLD = 0.30        # >30% above year-ago quarter
MONTH_SENTINEL = "__month_complete__"
ENTITY_INDEX = "__entity_index__"

_BS = chr(92)                  # backslash (kept out of literals for clarity)


class _BudgetExhausted(Exception):
    pass


# ---------------------------------------------------------------- month math

def _month_start(d):
    return d.replace(day=1)


def _add_months(mstart, n):
    y = mstart.year + (mstart.month - 1 + n) // 12
    m = (mstart.month - 1 + n) % 12 + 1
    return date(y, m, 1)


def _month_end(mstart):
    return _add_months(mstart, 1) - timedelta(days=1)


def _quarter_months(today):
    """(trailing 3 complete month-starts asc, same months one year earlier)."""
    cur = _month_start(today)
    trailing = [_add_months(cur, -3), _add_months(cur, -2), _add_months(cur, -1)]
    year_ago = [_add_months(m, -12) for m in trailing]
    return trailing, year_ago


# ------------------------------------------------- WebFOCUS Active Report IO

def _post_servlet(params):
    """POST to the WFServlet reusing common/http retry/throttle policy.

    common/http.fetch is GET-only and a GET against this servlet returns the
    fex source instead of running the report, hence this narrow POST wrapper.
    """
    domain = "cohtora.houstontx.gov"
    headers = {"User-Agent": _http.USER_AGENT}
    last_exc = None
    for attempt in range(_http.MAX_RETRIES):
        _http._throttle(domain)
        try:
            resp = requests.post(SERVLET_URL, data=params, headers=headers,
                                 timeout=180)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(
                    f"HTTP {resp.status_code} from {domain}", response=resp)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < _http.MAX_RETRIES - 1:
                time.sleep(_http.BACKOFF_BASE * (2 ** attempt))
    raise last_exc


def _scan_js_array(html, start):
    """Return html[start:close] for the JS array opening at html[start]=='['."""
    i = start
    depth = 0
    in_str = False
    esc = False
    quote = ""
    while i < len(html):
        c = html[i]
        if in_str:
            if esc:
                esc = False
            elif c == _BS:
                esc = True
            elif c == quote:
                in_str = False
        else:
            if c in ("'", '"'):
                in_str = True
                quote = c
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return html[start:i + 1]
        i += 1
    raise ValueError("unterminated JS array in Active Report")


def _js_strings(arr_src):
    """Flatten a JS array source into its string/number atoms, in order."""
    bs2 = _BS + _BS
    pat = "'((?:[^'" + bs2 + "]|" + bs2 + ".)*)'|(-?" + r"\d+(?:\.\d+)?)"
    out = []
    for m in re.finditer(pat, arr_src):
        if m.group(2) is not None:
            g = m.group(2)
            out.append(float(g) if "." in g else int(g))
        else:
            s = m.group(1)
            s = s.replace(_BS + "'", "'").replace(_BS + '"', '"')
            s = s.replace(bs2, _BS)
            out.append(s)
    return out


def parse_active_report(html):
    """Parse a Sold Permits Active Report page.

    Returns (total_reported, rows) where each row is
    [project_no, permit_desc, owner_occupant, address, project_desc,
     valuation, permit_code].
    """
    if "no record found" in html.lower():
        return 0, []
    m = re.search(r"ARstrings\s*=\s*\[\s*'", html)
    if not m:
        raise ValueError("Active Report markers not found (layout change?)")
    strings = _js_strings(_scan_js_array(html, html.index("[", m.start())))
    # header layout: strings[2] = "<N>" match count (see fixtures sample)
    total = None
    for s in strings[:6]:
        if isinstance(s, str) and s.isdigit():
            total = int(s)
            break
    m2 = re.search(r"T_cont\[NumOfTable\]\s*=(\s*)\[\s*\[", html)
    if not m2:
        raise ValueError("Active Report row table not found (layout change?)")
    tc_src = _scan_js_array(html, html.index("[", m2.start(1)))
    row_defs = json.loads(tc_src.replace("'", '"'))
    rows = []
    for r in row_defs:
        cells = []
        for cell in r[:7]:
            if isinstance(cell, list):
                idx = cell[0]
                if isinstance(idx, int) and 0 <= idx < len(strings):
                    cells.append(strings[idx])
                else:
                    cells.append(None)
            else:
                cells.append(cell)
        rows.append(cells)
    if total is None:
        total = len(rows)
    return total, rows


# ------------------------------------------------------------- row semantics

def _business_name(owner):
    """Business buyers are prefixed '*'; individual owner-occupants are not."""
    if not owner or not isinstance(owner, str):
        return None
    s = owner.strip()
    if not s.startswith("*"):
        return None
    s = s.strip("*").strip()
    if len(s) < 3:
        return None
    return s


_ZIP_TAIL = re.compile(r"(\d{5})\s*$")


def _zip_from_address(addr):
    if not addr or not isinstance(addr, str):
        return ""
    m = _ZIP_TAIL.search(addr.strip())
    return m.group(1) if m else ""


# ------------------------------------------------------------------ collector

class Collector(BaseCollector):
    avenue = "mechanical"
    source_id = "permits_houston"
    metros = ("houston",)

    def __init__(self):
        self._fixture = None    # last raw window payload, for --self-test

    # -- source IO ----------------------------------------------------------

    def _query_window(self, bdt, edt):
        params = {
            "IBIF_ex": "online_per_se.fex",
            "IBIAPP_app": "soldpermits",
            "IBIC_server": "EDASERVE",
            "SELTD": "PT",
            "PTYPE": PTYPE_MECHANICAL,
            "SRH": "",
            "BDT": bdt.strftime("%Y/%m/%d"),
            "EDT": edt.strftime("%Y/%m/%d"),
            "VALMN": "",
            "VALMX": "",
            "WFFMT": "HTML",
            "RPTID": "",
        }
        html = _post_servlet(params)
        total, rows = parse_active_report(html)
        if rows:
            self._fixture = {
                "source": SERVLET_URL,
                "query": params,
                "total_reported": total,
                "rows_embedded": len(rows),
                "columns": ["PROJECT_NO", "PERMIT_DESC", "OWNER_OCCUPANT",
                            "Address", "PROJECT_DESC", "CURRENT_VALUATION",
                            "PERMIT_TYPE"],
                "sample_rows": rows[:20],
            }
        return total, rows

    def _fetch_month(self, mstart, budget):
        """Fetch every mechanical permit sold in a month.

        Probes the whole month first (total is always reported); if the row
        cap was hit, re-queries in day-windows sized from the observed
        density, bisecting any window that still caps. Returns
        (rows, truncated_days).
        """
        mend = _month_end(mstart)
        rows_all = []
        truncated = []
        if budget["used"] >= MAX_REQUESTS:
            raise _BudgetExhausted()
        budget["used"] += 1
        total, rows = self._query_window(mstart, mend)
        if total <= len(rows):
            return rows, truncated
        ndays = (mend - mstart).days + 1
        per_day = max(total / ndays, 0.1)
        wdays = max(1, int(TARGET_ROWS / per_day))
        stack = []
        s = mstart
        while s <= mend:
            e = min(s + timedelta(days=wdays - 1), mend)
            stack.append((s, e))
            s = e + timedelta(days=1)
        stack.reverse()          # pop() walks the month in order
        while stack:
            s, e = stack.pop()
            if budget["used"] >= MAX_REQUESTS:
                raise _BudgetExhausted()
            budget["used"] += 1
            total, rows = self._query_window(s, e)
            if total > len(rows) and s < e:
                mid = s + (e - s) // 2
                stack.append((mid + timedelta(days=1), e))
                stack.append((s, mid))
                continue
            rows_all.extend(rows)
            if total > len(rows):
                truncated.append(s.isoformat())   # 1-day window still capped
        return rows_all, truncated

    # -- aggregation ---------------------------------------------------------

    @staticmethod
    def _aggregate(rows):
        """rows -> {name_norm: {name, count, zips Counter, sample_address}}"""
        per = {}
        for row in rows:
            if len(row) < 4:
                continue
            name = _business_name(row[2])
            if not name:
                continue
            nn = normalize_name(name).lower()
            if not nn:
                continue
            info = per.setdefault(nn, {"name": name, "count": 0,
                                       "zips": Counter(), "address": ""})
            info["count"] += 1
            z = _zip_from_address(row[3])
            if z:
                info["zips"][z] += 1
            if not info["address"] and isinstance(row[3], str):
                info["address"] = row[3].strip()
        return per

    # -- growth evaluation ---------------------------------------------------

    def _evaluate(self, store, today, notes):
        trailing, year_ago = _quarter_months(today)
        have = {s["snapshot_date"]
                for s in store.get_snapshots(self.source_id, MONTH_SENTINEL)}
        needed = [m.isoformat() for m in trailing + year_ago]
        missing = [d for d in needed if d not in have]
        if missing:
            notes.append("growth eval skipped, months not yet backfilled: "
                         + ",".join(missing))
            return []
        t_keys = {m.isoformat() for m in trailing}
        names = set()
        for snap in store.get_snapshots(self.source_id, ENTITY_INDEX):
            if snap["snapshot_date"] in t_keys:
                names.update(snap["payload"].get("entities", []))
        signals = []
        q_label = f"{trailing[0]:%Y%m}-{trailing[-1]:%Y%m}"
        signal_date = _month_end(trailing[-1]).isoformat()
        for nn in sorted(names):
            snaps = {s["snapshot_date"]: s["payload"]
                     for s in store.get_snapshots(self.source_id, nn)}
            t = sum(snaps.get(m.isoformat(), {}).get("count", 0)
                    for m in trailing)
            y = sum(snaps.get(m.isoformat(), {}).get("count", 0)
                    for m in year_ago)
            if t < MIN_TRAILING_JOBS:
                continue
            if y > 0:
                growth = t / y - 1.0
                if growth < GROWTH_THRESHOLD:
                    continue
                magnitude = min(1.0, 0.25 + 0.75 * (growth - GROWTH_THRESHOLD)
                                / (2.0 - GROWTH_THRESHOLD))
                growth_pct = round(growth * 100.0, 1)
            else:
                magnitude = 1.0            # 0 -> t jobs: new/expanding buyer
                growth_pct = None
            zips = Counter()
            display = nn.upper()
            address = ""
            for m in trailing:
                p = snaps.get(m.isoformat(), {})
                if p.get("zip"):
                    zips[p["zip"]] += p.get("count", 0)
                display = p.get("name", display) or display
                address = p.get("address", address) or address
            zip5 = zips.most_common(1)[0][0] if zips else ""
            monthly = {m.isoformat(): snaps.get(m.isoformat(), {}).get("count", 0)
                       for m in trailing + year_ago}
            signals.append(Signal(
                entity_key=entity_key(display, zip5),
                entity_name=display,
                metro="houston",
                avenue=self.avenue,
                signal_type="permit_volume_growth",
                signal_date=signal_date,
                magnitude=round(magnitude, 3),
                source_id=self.source_id,
                source_ref=f"hpc-sold-permits:{nn}:{q_label}",
                raw={
                    "buyer": display,
                    "trailing_quarter_jobs": t,
                    "year_ago_quarter_jobs": y,
                    "growth_pct": growth_pct,
                    "monthly_counts": monthly,
                    "evidence_url": LAUNCH_URL,
                    "verify_hint": "search Buyer's Name on the HPC Sold "
                                   "Permits page to reproduce",
                },
                attrs={"street": address, "zip": zip5},
            ))
        return signals

    # -- contract ------------------------------------------------------------

    def collect(self, since, store, registry):
        today = date.today()
        signals_added = 0
        entities = set()
        notes = []
        try:
            floor = _add_months(_month_start(today), -BACKFILL_FLOOR_MONTHS)
            start = max(_month_start(since), floor)
            cur = _month_start(today)
            months = []
            m = start
            while m < cur:                       # complete months only
                months.append(m)
                m = _add_months(m, 1)
            done = {s["snapshot_date"] for s in
                    store.get_snapshots(self.source_id, MONTH_SENTINEL)}
            trailing, year_ago = _quarter_months(today)
            prio = [m for m in trailing + year_ago
                    if m in months and m.isoformat() not in done]
            rest = [m for m in sorted(months, reverse=True)
                    if m not in prio and m.isoformat() not in done]
            plan = prio + rest
            budget = {"used": 0}
            for mstart in plan:
                try:
                    rows, truncated = self._fetch_month(mstart, budget)
                except _BudgetExhausted:
                    notes.append(f"request budget ({MAX_REQUESTS}) exhausted "
                                 f"before {mstart:%Y-%m}; rerun to resume")
                    break
                per = self._aggregate(rows)
                for nn, info in per.items():
                    zip5 = (info["zips"].most_common(1)[0][0]
                            if info["zips"] else "")
                    store.add_snapshot(self.source_id, mstart.isoformat(), nn, {
                        "month": mstart.strftime("%Y-%m"),
                        "name": info["name"],
                        "count": info["count"],
                        "zip": zip5,
                        "address": info["address"],
                    })
                    entities.add(nn)
                store.add_snapshot(self.source_id, mstart.isoformat(),
                                   ENTITY_INDEX,
                                   {"entities": sorted(per)})
                store.add_snapshot(self.source_id, mstart.isoformat(),
                                   MONTH_SENTINEL, {
                    "rows": len(rows),
                    "business_buyers": len(per),
                    "truncated_days": truncated,
                    "requests_used": budget["used"],
                })
                if truncated:
                    notes.append(f"{mstart:%Y-%m}: {len(truncated)} capped "
                                 "1-day windows (rows beyond 100 dropped)")
            for sig in self._evaluate(store, today, notes):
                if store.add_signal(sig):
                    signals_added += 1
                entities.add(sig.entity_key)
            status = "OK" if entities or signals_added else "EMPTY"
            return CollectorResult(self.source_id, signals_added,
                                   len(entities), status,
                                   error="; ".join(notes))
        except Exception as exc:  # noqa: BLE001 — contract: never raise
            return CollectorResult(self.source_id, signals_added,
                                   len(entities), "ERROR",
                                   error=f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


def _self_test():
    from common.store import Store
    since = date.today() - timedelta(days=30)
    store = Store(db_path=":memory:")      # throwaway; nothing touches sheets
    registry = config.load_registry()
    col = Collector()
    print(f"[self-test] {col.source_id}: collecting since {since} "
          "(last 30 days) ...")
    res = col.collect(since, store, registry)
    print(f"[self-test] status={res.status} signals_added={res.signals_added} "
          f"entities_seen={res.entities_seen}")
    if res.error:
        print(f"[self-test] notes: {res.error}")
    fixtures = Path(__file__).resolve().parent.parent / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    payload = col._fixture or {"note": "no rows returned in window",
                               "source": SERVLET_URL}
    out = fixtures / f"{col.source_id}_sample.json"
    out.write_text(json.dumps(payload, indent=2, default=str),
                   encoding="utf-8")
    print(f"[self-test] fixture saved: {out}")
    store.close()
    return res


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _self_test()
    else:
        print(__doc__)
