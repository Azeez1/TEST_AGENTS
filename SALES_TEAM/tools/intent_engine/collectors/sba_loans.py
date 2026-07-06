"""SBA 7(a)/504 loan-maturity collector (avenue: pe_distress, source_id: sba_loans).

Source — SBA FOIA loan-level CSVs on data.sba.gov (CKAN):
    package_show id=7-a-504-foia  ->  resources (verified 2026-07):
        FOIA - 504 (FY1991-FY2009)   ~48 MB
        FOIA - 504 (FY2010-Present)  ~56 MB
        FOIA - 7(a) (FY2010-FY2019)  ~223 MB
        FOIA - 7(a) (FY2020-Present) ~151 MB
    (7(a) FY1991-FY1999 and FY2000-FY2009 are excluded by default: their loans
     have almost entirely matured; flip INCLUDE_7A_2000_2009 to catch the rare
     20/25-year 7(a) from that vintage at the cost of a 282 MB download.)

CSVs are cached in ~/.dux_intent/cache/sba/ and re-downloaded only when older
than CACHE_MAX_AGE_DAYS (80) — the FOIA files refresh quarterly.

Emits `sba_maturity_window` Signals for still-active loans whose
ApprovalDate + TermInMonths lands within the next ~13 months (maturity
pressure) for borrowers in the Houston / Atlanta metros (borrower zip prefix
or project county). Magnitude scales with loan size and proximity to maturity.
Maturity is a *future* event, so signal_date uses the snapshot first-seen date
(stable across daily runs -> idempotent signals).
Entity identity = borrower name + zip ("biz:{name_norm}|{zip}").
"""
import csv
import re
import sys
import time
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._federal import clamp, parse_date_any, selftest_main  # noqa: E402
from common import http  # noqa: E402
from common.normalize import clean_zip, entity_key  # noqa: E402

CKAN_PACKAGE_URL = "https://data.sba.gov/api/3/action/package_show"
DATASET_ID = "7-a-504-foia"
DATASET_PAGE = "https://data.sba.gov/dataset/7-a-504-foia"

CACHE_MAX_AGE_DAYS = 80
INCLUDE_7A_2000_2009 = False

WINDOW_MIN_DAYS = 0        # maturity from today ...
WINDOW_MAX_DAYS = 395      # ... to ~13 months out
SIZE_FULL_SCALE = 2_000_000.0   # gross approval at which size score maxes out
EXCLUDED_STATUSES = {"PIF", "CHGOFF", "CANCLD"}

NEEDED_COLS = ("program", "locationid", "borrname", "borrstreet", "borrcity",
               "borrstate", "borrzip", "grossapproval", "approvaldate",
               "approvalfy", "terminmonths", "naicscode", "naicsdescription",
               "projectcounty", "projectstate", "loanstatus")


def _slug(name):
    """Stable cache filename from a resource name, ignoring the 'asof' suffix."""
    n = re.sub(r"\s+", "", str(name).lower())
    prog = "7a" if "7(a)" in n or "7a" in n.split("(")[0] else "504"
    m = re.search(r"\(fy(\d{4})-(?:fy)?(\d{4}|present)\)", n)
    span = f"fy{m.group(1)}-{m.group(2)}" if m else re.sub(r"[^a-z0-9]+", "-", n)[:40]
    return f"sba_{prog}_{span}.csv"


def _wanted(name):
    n = re.sub(r"\s+", "", str(name).lower())
    if not n.endswith(".csv"):
        return False
    if "504" in n and "foia" in n:
        return True
    if "7(a)" in n:
        if "fy2010-fy2019" in n or "fy2020" in n:
            return True
        if INCLUDE_7A_2000_2009 and "fy2000-fy2009" in n:
            return True
    return False


def _add_months(d, months):
    import calendar
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _money(value):
    try:
        return max(0.0, float(str(value).replace(",", "").replace("$", "").strip()))
    except (TypeError, ValueError):
        return 0.0


class SbaLoansCollector(BaseCollector):
    avenue = "pe_distress"
    source_id = "sba_loans"
    metros = ("houston", "atlanta")

    def __init__(self):
        self.sample_payload = None

    # ------------------------------------------------------ download / cache

    def _cache_dir(self):
        d = config.CACHE_DIR / "sba"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _list_resources(self):
        resp = http.fetch(CKAN_PACKAGE_URL, params={"id": DATASET_ID})
        doc = resp.json()
        if not doc.get("success"):
            raise RuntimeError(f"CKAN package_show failed: {str(doc)[:200]}")
        return doc["result"].get("resources", [])

    def _download_stream(self, url, dest):
        import requests
        tmp = dest.with_suffix(dest.suffix + ".part")
        last_exc = None
        for attempt in range(http.MAX_RETRIES):
            try:
                with requests.get(url, stream=True, timeout=600,
                                  headers={"User-Agent": http.USER_AGENT}) as r:
                    r.raise_for_status()
                    with open(tmp, "wb") as f:
                        for chunk in r.iter_content(1 << 20):
                            f.write(chunk)
                tmp.replace(dest)
                return dest
            except Exception as exc:
                last_exc = exc
                tmp.unlink(missing_ok=True)
                time.sleep(http.BACKOFF_BASE * (2 ** attempt))
        raise last_exc

    def _ensure_files(self, notes):
        """Return list of local CSV paths, downloading/refreshing as needed."""
        cache = self._cache_dir()
        try:
            resources = self._list_resources()
        except Exception as exc:
            cached = sorted(cache.glob("sba_*.csv"))
            if cached:
                notes.append(f"CKAN listing failed ({type(exc).__name__}); "
                             f"using {len(cached)} cached file(s)")
                return cached
            raise
        files = []
        now = time.time()
        for res in resources:
            name = res.get("name") or ""
            url = res.get("url") or ""
            if not url or not _wanted(name):
                continue
            dest = cache / _slug(name)
            age_days = ((now - dest.stat().st_mtime) / 86400.0
                        if dest.exists() else None)
            if age_days is not None and age_days < CACHE_MAX_AGE_DAYS:
                files.append(dest)
                continue
            try:
                self._download_stream(url, dest)
                files.append(dest)
            except Exception as exc:
                if dest.exists():   # stale cache beats nothing
                    notes.append(f"refresh failed for {dest.name} "
                                 f"({type(exc).__name__}); using stale cache")
                    files.append(dest)
                else:
                    notes.append(f"download failed for {name}: "
                                 f"{type(exc).__name__}: {exc}")
        if not files:
            raise RuntimeError("no SBA FOIA CSVs available (all downloads failed "
                               "and cache is empty)")
        return files

    # -------------------------------------------------------------- parsing

    def _metro_for_loan(self, registry, row):
        from collectors._federal import metro_of
        m = metro_of(registry, row.get("borrstate"),
                     zip5=row.get("borrzip"))
        if m:
            return m
        return metro_of(registry, row.get("projectstate"),
                        county=row.get("projectcounty") or None)

    def _iter_window_loans(self, path, registry, today):
        """Yield (row_dict, maturity_date, days_to_maturity) for in-window loans."""
        states = {str(m["state"]).upper()
                  for m in registry.get("metros", {}).values()}
        with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if not header:
                return
            idx = {str(h).strip().lower(): i for i, h in enumerate(header)}
            need = ("borrstate", "approvaldate", "terminmonths", "borrname")
            if any(k not in idx for k in need):
                raise RuntimeError(f"{path.name}: missing columns "
                                   f"{[k for k in need if k not in idx]}")
            i_state = idx["borrstate"]
            i_pstate = idx.get("projectstate", i_state)
            for cells in reader:
                if len(cells) <= i_state:
                    continue
                st = cells[i_state].strip().upper()
                pst = (cells[i_pstate].strip().upper()
                       if len(cells) > i_pstate else "")
                if st not in states and pst not in states:
                    continue
                row = {k: (cells[i].strip() if len(cells) > i else "")
                       for k, i in idx.items() if k in NEEDED_COLS}
                ad = parse_date_any(row.get("approvaldate"))
                if ad is None:
                    continue
                try:
                    term = int(float(row.get("terminmonths") or 0))
                except (TypeError, ValueError):
                    continue
                if term <= 0:
                    continue
                status = str(row.get("loanstatus") or "").strip().upper()
                if status in EXCLUDED_STATUSES:
                    continue
                maturity = _add_months(ad, term)
                days = (maturity - today).days
                if WINDOW_MIN_DAYS <= days <= WINDOW_MAX_DAYS:
                    yield row, maturity, days

    # ---------------------------------------------------------- signal emit

    def _magnitude(self, gross, days):
        size = min(1.0, gross / SIZE_FULL_SCALE)
        prox = 1.0 - clamp(days / float(WINDOW_MAX_DAYS))
        return clamp(0.2 + 0.45 * size + 0.35 * prox, 0.05, 1.0)

    def _emit(self, store, registry, row, maturity, days, today):
        name = str(row.get("borrname") or "").strip()
        if not name:
            return None
        metro = self._metro_for_loan(registry, row)
        if metro is None:
            return None
        zip5 = clean_zip(row.get("borrzip"))
        gross = _money(row.get("grossapproval"))
        loc_id = str(row.get("locationid") or "").strip()
        program = str(row.get("program") or "").strip() or "sba"
        item_key = (f"{program}:{loc_id}" if loc_id else
                    f"{program}:{name}|{row.get('approvaldate')}")
        store.add_snapshot(self.source_id, today, item_key, {
            "borrname": name, "maturity": maturity.isoformat(),
            "gross": gross, "loanstatus": row.get("loanstatus"),
        })
        signal_date = store.first_seen(self.source_id, item_key) or today.isoformat()
        ek = entity_key(name, zip5)
        raw = dict(row)
        raw["_maturity_date"] = maturity.isoformat()
        raw["_days_to_maturity"] = days
        sig = Signal(
            entity_key=ek,
            entity_name=name,
            metro=metro,
            avenue=self.avenue,
            signal_type="sba_maturity_window",
            signal_date=str(signal_date)[:10],
            magnitude=self._magnitude(gross, days),
            source_id=self.source_id,
            source_ref=f"{DATASET_PAGE}#{item_key.replace(' ', '_')}",
            raw=raw,
            attrs={"street": str(row.get("borrstreet") or "") or None,
                   "zip": zip5 or None,
                   "city": str(row.get("borrcity") or "") or None},
        )
        inserted = store.add_signal(sig)
        return ek, inserted

    # -------------------------------------------------------------- collect

    def collect(self, since, store, registry):
        try:
            notes = []
            files = self._ensure_files(notes)
            today = date.today()
            added, entities = 0, set()
            for path in files:
                for row, maturity, days in self._iter_window_loans(path, registry,
                                                                   today):
                    emitted = self._emit(store, registry, row, maturity, days,
                                         today)
                    if emitted:
                        ek, inserted = emitted
                        entities.add(ek)
                        if inserted:
                            added += 1
                        if self.sample_payload is None:
                            sample = dict(row)
                            sample["_maturity_date"] = maturity.isoformat()
                            sample["_days_to_maturity"] = days
                            sample["_source_file"] = path.name
                            self.sample_payload = {"sba_loan": sample}
            status = "OK" if added > 0 else "EMPTY"
            return CollectorResult(self.source_id, added, len(entities), status,
                                   "; ".join(notes))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = SbaLoansCollector


if __name__ == "__main__":
    sys.exit(selftest_main(Collector))
