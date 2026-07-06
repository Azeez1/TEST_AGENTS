"""OSHA enforcement collector (avenue: manufacturing, source_id: osha_dol).

Primary source — DOL Open Data API v4 (requires DOL_API_KEY in ~/.dux_intent/.env):
    GET https://apiprod.dol.gov/v4/get/osha/osha_inspection/json
    GET https://apiprod.dol.gov/v4/get/osha/osha_violation/json
    Auth: X-API-KEY header. Filtering via filter_object JSON
    (e.g. {"and":[{"field":"site_state","operator":"eq","value":"TX"},
                  {"field":"open_date","operator":"gt","value":"2026-06-01"}]}).

Fallback when DOL_API_KEY is missing — keyless CSV catalog at enforcedata.dol.gov:
    1) any manually cached osha_inspection*.csv/.zip under ~/.dux_intent/cache/osha/
    2) attempt to discover + download osha_inspection_*.csv.zip from
       https://enfxfr.dol.gov/data_catalog/OSHA/ (validated as a real ZIP —
       the site currently serves an SPA HTML shell to non-browser clients,
       in which case we return SKIPPED with instructions).

Emits `osha_citation` Signals. Magnitude scales with total current penalty for the
inspection (violations joined by activity_nr). Manufacturing NAICS (31-33) keeps
full magnitude; other industries are kept at reduced (0.6x) magnitude.
Entity identity = establishment name + site zip ("biz:{name_norm}|{zip}").
"""
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._federal import (  # noqa: E402
    clamp, metro_of, parse_date_any, selftest_main,
)
from common import http  # noqa: E402
from common.normalize import clean_zip, entity_key  # noqa: E402

API_BASE = "https://apiprod.dol.gov/v4/get/osha"
CATALOG_URLS = (
    "https://enfxfr.dol.gov/data_catalog/OSHA/",
    "https://enforcedata.dol.gov/views/data_catalogs.php",
)
PAGE_LIMIT = 200          # records per API page
MAX_PAGES = 25            # cap per state (5000 inspections)
VIOLATION_BATCH = 50      # activity_nrs per "in" filter batch
MAX_PER_ACTIVITY_LOOKUPS = 40   # fallback cap if the "in" operator is rejected
MANUFACTURING_PREFIXES = ("31", "32", "33")
PENALTY_FULL_SCALE = 50_000.0   # penalty at which magnitude core maxes out


class _SourceUnavailable(Exception):
    """Keyless fallback has no usable data (not an error — maps to SKIPPED)."""


def _records(payload):
    """DOL v4 responses: accept a bare list or a dict wrapping one list."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for k in ("data", "results", "Results", "records"):
            v = payload.get(k)
            if isinstance(v, list):
                return v
        lists = [v for v in payload.values() if isinstance(v, list)]
        if len(lists) == 1:
            return lists[0]
    return []


def _money(value):
    try:
        return max(0.0, float(str(value).replace(",", "").replace("$", "").strip()))
    except (TypeError, ValueError):
        return 0.0


class OshaDolCollector(BaseCollector):
    avenue = "manufacturing"
    source_id = "osha_dol"
    metros = ("houston", "atlanta")

    def __init__(self):
        self.sample_payload = None

    # ------------------------------------------------------------------ API

    def _api_get(self, endpoint, filter_object, api_key, limit=PAGE_LIMIT, offset=0):
        params = {
            "limit": limit,
            "offset": offset,
            "filter_object": json.dumps(filter_object, separators=(",", ":")),
        }
        resp = http.fetch(f"{API_BASE}/{endpoint}/json", params=params,
                          headers={"X-API-KEY": api_key})
        return _records(resp.json())

    def _fetch_inspections_api(self, api_key, state, since):
        """Page osha_inspection for one state filtered on open_date > since."""
        flt = {"and": [
            {"field": "site_state", "operator": "eq", "value": state},
            {"field": "open_date", "operator": "gt", "value": since.isoformat()},
        ]}
        out = []
        try:
            for page in range(MAX_PAGES):
                recs = self._api_get("osha_inspection", flt, api_key,
                                     offset=page * PAGE_LIMIT)
                out.extend(recs)
                if len(recs) < PAGE_LIMIT:
                    break
            return out, None
        except Exception as exc:
            # composite filter may be rejected on some deployments — retry with a
            # single eq filter and date-filter client-side (bounded pages).
            try:
                flt_simple = {"field": "site_state", "operator": "eq", "value": state}
                out = []
                for page in range(10):
                    recs = self._api_get("osha_inspection", flt_simple, api_key,
                                         offset=page * PAGE_LIMIT)
                    out.extend(recs)
                    if len(recs) < PAGE_LIMIT:
                        break
                kept = [r for r in out
                        if (parse_date_any(r.get("open_date")) or date.min) >= since]
                return kept, f"composite filter rejected ({exc}); client-side date filter"
            except Exception as exc2:
                raise RuntimeError(
                    f"osha_inspection query failed for {state}: {exc2}") from exc2

    def _fetch_penalties_api(self, api_key, activity_nrs):
        """Return {activity_nr: (total_current_penalty, violation_count)}.

        Tries batched 'in' filters; falls back to capped per-activity 'eq' lookups.
        Returns (penalties_dict, note_or_None). Never raises.
        """
        penalties = {}
        note = None
        ids = [str(a) for a in activity_nrs if a]
        try:
            for i in range(0, len(ids), VIOLATION_BATCH):
                batch = ids[i:i + VIOLATION_BATCH]
                flt = {"field": "activity_nr", "operator": "in", "value": batch}
                for page in range(5):
                    recs = self._api_get("osha_violation", flt, api_key,
                                         offset=page * PAGE_LIMIT)
                    for v in recs:
                        if str(v.get("delete_flag") or "").strip().upper() == "D":
                            continue
                        a = str(v.get("activity_nr") or "")
                        pen = _money(v.get("current_penalty"))
                        if pen <= 0:
                            pen = _money(v.get("initial_penalty"))
                        tot, cnt = penalties.get(a, (0.0, 0))
                        penalties[a] = (tot + pen, cnt + 1)
                    if len(recs) < PAGE_LIMIT:
                        break
            return penalties, note
        except Exception as exc:
            note = f"batched violation lookup failed ({type(exc).__name__}); "
            try:
                for a in ids[:MAX_PER_ACTIVITY_LOOKUPS]:
                    flt = {"field": "activity_nr", "operator": "eq", "value": a}
                    recs = self._api_get("osha_violation", flt, api_key)
                    tot, cnt = 0.0, 0
                    for v in recs:
                        if str(v.get("delete_flag") or "").strip().upper() == "D":
                            continue
                        pen = _money(v.get("current_penalty")) or _money(
                            v.get("initial_penalty"))
                        tot += pen
                        cnt += 1
                    penalties[a] = (tot, cnt)
                note += f"used per-activity lookups for first {MAX_PER_ACTIVITY_LOOKUPS}"
            except Exception as exc2:
                note += f"per-activity lookups also failed ({type(exc2).__name__})"
            return penalties, note

    # ------------------------------------------------- keyless CSV fallback

    def _cached_csv_files(self):
        cache = config.CACHE_DIR / "osha"
        if not cache.exists():
            return []
        return sorted(list(cache.glob("osha_inspection*.csv"))
                      + list(cache.glob("osha_inspection*.zip")))

    def _try_download_catalog(self):
        """Best-effort discovery of osha_inspection_*.csv.zip on the keyless catalog."""
        import re as _re
        cache = config.CACHE_DIR / "osha"
        cache.mkdir(parents=True, exist_ok=True)
        for base in CATALOG_URLS:
            try:
                page = http.fetch(base).text
            except Exception:
                continue
            links = _re.findall(r'href="([^"]*osha_inspection[^"]*\.zip)"', page)
            if not links:
                continue
            url = links[-1]
            if url.startswith("/"):
                from urllib.parse import urljoin
                url = urljoin(base, url)
            dest = cache / url.rsplit("/", 1)[-1]
            try:
                import requests
                with requests.get(url, stream=True, timeout=600,
                                  headers={"User-Agent": http.USER_AGENT}) as r:
                    r.raise_for_status()
                    first = b""
                    tmp = dest.with_suffix(dest.suffix + ".part")
                    with open(tmp, "wb") as f:
                        for chunk in r.iter_content(1 << 20):
                            if not first:
                                first = chunk[:4]
                                if not first.startswith(b"PK"):
                                    break   # HTML shell, not a zip
                            f.write(chunk)
                    if first.startswith(b"PK"):
                        tmp.replace(dest)
                        return dest
                    tmp.unlink(missing_ok=True)
            except Exception:
                continue
        return None

    def _iter_csv_rows(self, path):
        import csv
        import io
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as zf:
                for member in zf.namelist():
                    if not member.lower().endswith(".csv"):
                        continue
                    with zf.open(member) as fh:
                        text = io.TextIOWrapper(fh, encoding="utf-8-sig",
                                                errors="replace", newline="")
                        yield from csv.DictReader(text)
        else:
            with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
                yield from __import__("csv").DictReader(fh)

    def _collect_csv_fallback(self, since, states):
        """Yield inspection dicts from cached/downloaded catalog CSVs."""
        files = self._cached_csv_files()
        if not files:
            got = self._try_download_catalog()
            if got:
                files = [got]
        if not files:
            raise _SourceUnavailable(
                "DOL_API_KEY not set in ~/.dux_intent/.env and the keyless CSV "
                "catalog (enforcedata.dol.gov / enfxfr.dol.gov) serves only an HTML "
                "app shell to scripts. Set DOL_API_KEY (free key: "
                "https://dataportal.dol.gov/registration) or drop an "
                "osha_inspection*.csv(.zip) into ~/.dux_intent/cache/osha/.")
        for path in files:
            for row in self._iter_csv_rows(path):
                low = {str(k).strip().lower(): v for k, v in row.items() if k}
                st = str(low.get("site_state") or "").strip().upper()
                if st not in states:
                    continue
                od = parse_date_any(low.get("open_date"))
                if od is None or od < since:
                    continue
                yield low

    # ---------------------------------------------------------- signal emit

    def _magnitude(self, penalty, viol_count, naics, penalty_known):
        if penalty_known:
            core = 0.25 + 0.75 * min(1.0, penalty / PENALTY_FULL_SCALE)
            if penalty <= 0 and viol_count > 0:
                core = 0.25 + min(0.15, 0.03 * viol_count)
        else:
            core = 0.20
        naics_s = str(naics or "").strip()
        if not naics_s.startswith(MANUFACTURING_PREFIXES):
            core *= 0.6
        return clamp(core, 0.05, 1.0)

    def _emit(self, store, registry, insp, penalty, viol_count, penalty_known):
        name = str(insp.get("estab_name") or "").strip()
        if not name:
            return None
        zip5 = clean_zip(insp.get("site_zip"))
        metro = metro_of(registry, insp.get("site_state"), zip5=zip5,
                         city=insp.get("site_city"))
        if metro is None:
            return None
        od = parse_date_any(insp.get("open_date"))
        if od is None:
            return None
        activity_nr = str(insp.get("activity_nr") or "").strip()
        ek = entity_key(name, zip5)
        source_ref = (f"https://www.osha.gov/ords/imis/establishment."
                      f"inspection_detail?id={activity_nr}" if activity_nr
                      else f"dol-api:osha_inspection:{name}|{od.isoformat()}")
        raw = dict(insp)
        raw["_total_current_penalty"] = penalty if penalty_known else None
        raw["_violation_count"] = viol_count if penalty_known else None
        sig = Signal(
            entity_key=ek,
            entity_name=name,
            metro=metro,
            avenue=self.avenue,
            signal_type="osha_citation",
            signal_date=od.isoformat(),
            magnitude=self._magnitude(penalty, viol_count, insp.get("naics_code"),
                                      penalty_known),
            source_id=self.source_id,
            source_ref=source_ref,
            raw=raw,
            attrs={"street": str(insp.get("site_address") or "") or None,
                   "zip": zip5 or None,
                   "city": str(insp.get("site_city") or "") or None},
        )
        inserted = store.add_signal(sig)
        if activity_nr:
            store.add_snapshot(self.source_id, date.today(), activity_nr,
                               {"estab_name": name, "open_date": od.isoformat(),
                                "penalty": penalty if penalty_known else None})
        return ek, inserted

    # -------------------------------------------------------------- collect

    def collect(self, since, store, registry):
        try:
            states = {registry["metros"][m]["state"] for m in self.metros
                      if m in registry.get("metros", {})}
            api_key = config.get_env("DOL_API_KEY")
            notes = []
            added, entities = 0, set()

            if api_key:
                inspections = []
                for state in sorted(states):
                    recs, note = self._fetch_inspections_api(api_key, state, since)
                    inspections.extend(recs)
                    if note:
                        notes.append(f"{state}: {note}")
                if inspections and self.sample_payload is None:
                    self.sample_payload = {"osha_inspection": inspections[0]}
                activity_nrs = [str(i.get("activity_nr") or "") for i in inspections]
                penalties, pnote = self._fetch_penalties_api(
                    api_key, [a for a in activity_nrs if a])
                if pnote:
                    notes.append(pnote)
                penalty_known_globally = bool(penalties) or not inspections
                for insp in inspections:
                    a = str(insp.get("activity_nr") or "")
                    tot, cnt = penalties.get(a, (0.0, 0))
                    known = a in penalties or penalty_known_globally
                    emitted = self._emit(store, registry, insp, tot, cnt, known)
                    if emitted:
                        ek, inserted = emitted
                        entities.add(ek)
                        if inserted:
                            added += 1
            else:
                try:
                    count_scanned = 0
                    for insp in self._collect_csv_fallback(since, states):
                        count_scanned += 1
                        if self.sample_payload is None:
                            self.sample_payload = {"osha_inspection_csv": insp}
                        emitted = self._emit(store, registry, insp, 0.0, 0, False)
                        if emitted:
                            ek, inserted = emitted
                            entities.add(ek)
                            if inserted:
                                added += 1
                    notes.append("keyless CSV fallback (penalties unavailable "
                                 "without osha_violation join)")
                except _SourceUnavailable as exc:
                    return CollectorResult(self.source_id, 0, 0, "SKIPPED", str(exc))

            status = "OK" if added > 0 else "EMPTY"
            return CollectorResult(self.source_id, added, len(entities), status,
                                   "; ".join(notes))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = OshaDolCollector


if __name__ == "__main__":
    sys.exit(selftest_main(Collector))
