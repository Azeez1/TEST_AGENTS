"""permits_atlanta — Atlanta building-permit collector (DISABLED, see notes).

Avenue:    mechanical   (Meridian demo)
Source id: permits_atlanta
Metro:     atlanta

STATUS: enabled:false in signal_registry.json collectors_enabled.

PINNED LAYER (best available, verified 2026-07-05 via the DPCD hub
dpcd-coaplangis.opendata.arcgis.com -> AGOL org 5RxyIIJ9boPdptdo):
    https://services5.arcgis.com/5RxyIIJ9boPdptdo/arcgis/rest/services/Building_Permit_latest/FeatureServer/0
    fields: RecordID, Name, OrigOpened, Opend, TypeCombo, Use_, Subtype,
            Group_, Address, Status_1, StatusDate, JOB_VALUE, PARCEL,
            JobValue, ACA_Link, ... (NO contractor / buyer / applicant field)

Why this collector is disabled rather than emitting signals:
  1. No contractor identity. Neither the pinned layer nor the alternative
     "Building Permit Tracker" service
     (https://services5.arcgis.com/5RxyIIJ9boPdptdo/arcgis/rest/services/Building_Permit_Tracker/FeatureServer/2)
     carries the pulling contractor, permit buyer, or applicant — only the
     project name and address. A per-contractor job-count time series (the
     permit_volume_growth signal this avenue requires) cannot be built from
     these fields.
  2. Staleness. Building_Permit_latest data ends 2026-01-28 (item last
     modified 2026-01-29; range 2022-09-19..2026-01-28, 36,115 records) — it
     cannot cover a current trailing quarter. Building_Permit_Tracker ends
     2024-11-19.
  3. Fallback checked: Accela Citizen Access (ATLANTA_GA):
     https://aca-prod.accela.com/ATLANTA_GA/ exposes contractor ("licensed
     professional") only on per-record detail pages behind an ASP.NET
     postback flow — a 12-24 month backfill would require tens of thousands
     of stateful page fetches, which is out of budget/fragility bounds for
     this engine. Also checked: gis.atlantaga.gov/dpcd REST (no permit
     service; the AccelaPermits MapServer referenced by old items is 404).

Re-enable path: if the city refreshes Building_Permit_latest AND adds a
contractor/applicant field (or publishes an Accela extract), flip
collectors_enabled.permits_atlanta to true and extend collect() with the
same monthly snapshot + trailing-quarter growth logic used by
collectors/permits_houston.py.

collect() performs a light live probe of the pinned layer (so a future data
refresh is noticed in run logs) and returns SKIPPED. It never raises.

Self-test:
    python -m collectors.permits_atlanta --self-test
probes the layer for the last 30 days AND fetches a raw sample for
fixtures/permits_atlanta_sample.json, writes NOTHING to any sheet.
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from collectors import BaseCollector, CollectorResult  # noqa: E402
from common.http import arcgis_query  # noqa: E402

FEATURE_SERVER = ("https://services5.arcgis.com/5RxyIIJ9boPdptdo/arcgis/rest/"
                  "services/Building_Permit_latest/FeatureServer/0")
TRACKER_LAYER = ("https://services5.arcgis.com/5RxyIIJ9boPdptdo/arcgis/rest/"
                 "services/Building_Permit_Tracker/FeatureServer/2")
ACCELA_FALLBACK = "https://aca-prod.accela.com/ATLANTA_GA/"

SKIP_REASON = (
    "pinned layer (Building_Permit_latest/0) has no contractor/buyer field "
    "and its data ends 2026-01-28, so per-contractor permit_volume_growth "
    "cannot be computed; Accela ACA fallback needs per-record ASP.NET "
    "scraping (out of scope). Disabled in collectors_enabled - see module "
    "docstring for the re-enable path."
)

OUT_FIELDS = ("RecordID,Name,Opend,TypeCombo,Use_,Subtype,Group_,Address,"
              "Status_1,JobValue,ACA_Link")


def _epoch_ms_to_date(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).date()


class Collector(BaseCollector):
    avenue = "mechanical"
    source_id = "permits_atlanta"
    metros = ("atlanta",)

    def __init__(self):
        self._fixture = None

    def _probe(self, since):
        """One page of permits opened since `since` (usually 0 rows: the
        layer is stale). Keeps the run log honest about layer freshness."""
        where = f"Opend >= DATE '{since.isoformat()}'"
        data = arcgis_query(FEATURE_SERVER, where=where,
                            out_fields=OUT_FIELDS)
        feats = data.get("features", [])
        if feats:
            self._fixture = {"source": FEATURE_SERVER, "where": where,
                             "features": feats[:5]}
        return feats

    def collect(self, since, store, registry):
        try:
            feats = self._probe(since)
            fresh = len(feats)
            note = SKIP_REASON
            if fresh:
                newest = max((f["attributes"].get("Opend") or 0)
                             for f in feats)
                note = (f"LAYER HAS {fresh}+ ROWS SINCE {since} (newest "
                        f"{_epoch_ms_to_date(newest)}) - data refreshed? "
                        "Still no contractor field; ") + SKIP_REASON
            return CollectorResult(self.source_id, 0, 0, "SKIPPED",
                                   error=note)
        except Exception as exc:  # noqa: BLE001 — contract: never raise
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   error=f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


def _self_test():
    from common.store import Store
    since = date.today() - timedelta(days=30)
    store = Store(db_path=":memory:")      # throwaway; nothing touches sheets
    registry = config.load_registry()
    col = Collector()
    print(f"[self-test] {col.source_id}: probing since {since} "
          "(last 30 days) ...")
    res = col.collect(since, store, registry)
    print(f"[self-test] status={res.status} signals_added={res.signals_added} "
          f"entities_seen={res.entities_seen}")
    if res.error:
        print(f"[self-test] notes: {res.error}")
    # fixture: the 30-day probe is expected to be empty (stale layer), so
    # pull a raw sample from the tail of the data instead.
    if col._fixture is None:
        try:
            data = arcgis_query(FEATURE_SERVER,
                                where="Opend >= DATE '2025-12-01'",
                                out_fields=OUT_FIELDS)
            col._fixture = {
                "source": FEATURE_SERVER,
                "where": "Opend >= DATE '2025-12-01'",
                "note": ("sample from layer tail; data ends 2026-01-28 and "
                         "has no contractor field — collector disabled"),
                "features": data.get("features", [])[:5],
            }
        except Exception as exc:  # noqa: BLE001
            col._fixture = {"source": FEATURE_SERVER,
                            "error": f"{type(exc).__name__}: {exc}"}
    fixtures = Path(__file__).resolve().parent.parent / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    out = fixtures / f"{col.source_id}_sample.json"
    out.write_text(json.dumps(col._fixture, indent=2, default=str),
                   encoding="utf-8")
    print(f"[self-test] fixture saved: {out}")
    store.close()
    return res


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _self_test()
    else:
        print(__doc__)
