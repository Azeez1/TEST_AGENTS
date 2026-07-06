"""EPA ECHO collector (avenue: manufacturing, source_id: epa_echo).

Source — EPA ECHO REST services (no key required):
    get_facilities: https://echodata.epa.gov/echo/echo_rest_services.get_facilities
        (p_st + p_fips county filter, p_qiv=GT1 to pre-narrow to facilities with
         quarters in significant violation)
    get_qid:        page the stored query's facilities as JSON (5000/page)
    get_download:   CSV of the stored query (fallback when get_qid misbehaves)

Emits `epa_violation` Signals for facilities currently in significant
non-compliance (FacSNCFlg == "Y"). Magnitude scales with quarters in
non-compliance over the last 3 years (FacQtrsWithNC, 0-12).

SNC is a *state*, not a dated event, so signal_date uses the snapshot
first-seen date (stable across daily runs -> idempotent signals that decay
naturally once the facility leaves SNC).
Entity identity = facility name + zip ("biz:{name_norm}|{zip}").
"""
import csv
import io
import sys
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._federal import clamp, metro_of, selftest_main  # noqa: E402
from common import http  # noqa: E402
from common.normalize import clean_zip, entity_key  # noqa: E402

ECHO_BASE = "https://echodata.epa.gov/echo/echo_rest_services"
FACILITY_REPORT = "https://echo.epa.gov/detailed-facility-report?fid={rid}"

# metro -> [(county_fips, county_name)] for the registry's metro counties
COUNTY_FIPS = {
    "houston": [("48201", "HARRIS"), ("48157", "FORT BEND"), ("48339", "MONTGOMERY")],
    "atlanta": [("13121", "FULTON"), ("13089", "DEKALB"), ("13067", "COBB"),
                ("13135", "GWINNETT")],
}
PAGE_SIZE = 5000
MAX_PAGES = 4


class EpaEchoCollector(BaseCollector):
    avenue = "manufacturing"
    source_id = "epa_echo"
    metros = ("houston", "atlanta")

    def __init__(self):
        self.sample_payload = None

    # ------------------------------------------------------------- fetching

    def _get_facilities_qid(self, state, fips):
        params = {"output": "JSON", "p_st": state, "p_fips": fips, "p_qiv": "GT1"}
        resp = http.fetch(f"{ECHO_BASE}.get_facilities", params=params)
        results = (resp.json() or {}).get("Results") or {}
        msg = str(results.get("Message") or "")
        if msg.lower() not in ("success", "ok"):
            raise RuntimeError(f"get_facilities: {msg or 'no Message'} "
                               f"{results.get('Error') or ''}".strip())
        qid = results.get("QueryID")
        rows = int(results.get("QueryRows") or 0)
        if not qid:
            raise RuntimeError("get_facilities returned no QueryID")
        return str(qid), rows

    def _get_qid_pages(self, qid, total_rows):
        facs = []
        pages = min(MAX_PAGES, max(1, -(-total_rows // PAGE_SIZE)))
        for pageno in range(1, pages + 1):
            resp = http.fetch(f"{ECHO_BASE}.get_qid",
                              params={"output": "JSON", "qid": qid,
                                      "pageno": pageno})
            results = (resp.json() or {}).get("Results") or {}
            page_facs = results.get("Facilities")
            if not isinstance(page_facs, list):
                raise RuntimeError("get_qid returned no Facilities list")
            facs.extend(page_facs)
            if len(page_facs) < PAGE_SIZE:
                break
        return facs

    def _get_download_rows(self, qid):
        """Fallback: full CSV of the stored query via get_download."""
        resp = http.fetch(f"{ECHO_BASE}.get_download", params={"qid": qid})
        text = resp.text
        reader = csv.DictReader(io.StringIO(text))
        return [dict(r) for r in reader]

    def _fetch_county(self, state, fips):
        qid, rows = self._get_facilities_qid(state, fips)
        if rows == 0:
            return []
        try:
            return self._get_qid_pages(qid, rows)
        except Exception:
            return self._get_download_rows(qid)

    # ---------------------------------------------------------- signal emit

    @staticmethod
    def _field(fac, *names):
        """Case-insensitive field lookup so JSON and CSV paths both work."""
        low = None
        for n in names:
            if n in fac:
                return fac[n]
            if low is None:
                low = {str(k).lower(): v for k, v in fac.items()}
            v = low.get(n.lower())
            if v is not None:
                return v
        return None

    def _emit(self, store, registry, fac):
        snc = str(self._field(fac, "FacSNCFlg") or "").strip().upper()
        if snc != "Y":
            return None
        name = str(self._field(fac, "FacName") or "").strip()
        if not name:
            return None
        zip5 = clean_zip(self._field(fac, "FacZip"))
        state = str(self._field(fac, "FacState") or "").strip().upper()
        county = str(self._field(fac, "FacCounty") or "").strip()
        metro = metro_of(registry, state, county=county or None, zip5=zip5,
                         city=self._field(fac, "FacCity"))
        if metro is None:
            return None
        try:
            qtrs = int(float(self._field(fac, "FacQtrsWithNC") or 0))
        except (TypeError, ValueError):
            qtrs = 0
        rid = str(self._field(fac, "RegistryID") or "").strip()
        item_key = rid or entity_key(name, zip5)
        today = date.today()
        store.add_snapshot(self.source_id, today, item_key, {
            "FacName": name, "FacSNCFlg": snc, "FacQtrsWithNC": qtrs,
            "FacComplianceStatus": self._field(fac, "FacComplianceStatus"),
        })
        signal_date = store.first_seen(self.source_id, item_key) or today.isoformat()
        ek = entity_key(name, zip5)
        sig = Signal(
            entity_key=ek,
            entity_name=name,
            metro=metro,
            avenue=self.avenue,
            signal_type="epa_violation",
            signal_date=str(signal_date)[:10],
            magnitude=clamp(0.4 + 0.6 * min(qtrs, 12) / 12.0, 0.05, 1.0),
            source_id=self.source_id,
            source_ref=(FACILITY_REPORT.format(rid=rid) if rid
                        else f"epa-echo:{item_key}"),
            raw=dict(fac),
            attrs={"street": str(self._field(fac, "FacStreet") or "") or None,
                   "zip": zip5 or None,
                   "city": str(self._field(fac, "FacCity") or "") or None},
        )
        inserted = store.add_signal(sig)
        return ek, inserted

    # -------------------------------------------------------------- collect

    def collect(self, since, store, registry):
        try:
            added, entities, errors = 0, set(), []
            counties_ok = 0
            for metro in self.metros:
                mcfg = registry.get("metros", {}).get(metro)
                if not mcfg:
                    continue
                state = mcfg["state"]
                for fips, county in COUNTY_FIPS.get(metro, []):
                    try:
                        facs = self._fetch_county(state, fips)
                        counties_ok += 1
                    except Exception as exc:
                        errors.append(f"{county}: {type(exc).__name__}: {exc}")
                        continue
                    for fac in facs:
                        emitted = self._emit(store, registry, fac)
                        if emitted:
                            ek, inserted = emitted
                            entities.add(ek)
                            if inserted:
                                added += 1
                            if self.sample_payload is None:
                                self.sample_payload = {"echo_facility": dict(fac)}
            note = "; ".join(errors)
            if counties_ok == 0:
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       note or "all county queries failed")
            status = "OK" if added > 0 else "EMPTY"
            return CollectorResult(self.source_id, added, len(entities), status, note)
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = EpaEchoCollector


if __name__ == "__main__":
    sys.exit(selftest_main(Collector))
