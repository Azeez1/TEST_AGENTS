"""violations_houston — Houston building-code violation cluster collector.

Avenue:    property_mgmt   (Stonebridge demo)
Source id: violations_houston
Metro:     houston

PINNED SOURCE (verified live 2026-07-05):
    CKAN dataset "City of Houston Building Code Enforcement Violations (DON)"
    https://data.houstontx.gov/dataset/city-of-houston-building-code-enforcement-violations-don
    resource (datastore, "All Code Enforcement Violations in FORMS Since 2014"):
        1446a3ec-2633-4cf1-b15d-6dae9a07c4ed
    queried through the datastore SQL API:
        https://data.houstontx.gov/api/3/action/datastore_search_sql

DATA CAVEAT (checked 2026-07-05): the datastore is live and queryable
(376,092 rows) but it is a static extract — max(RecordCreateDate) =
2018-08-22 across every resource in the dataset (the companion "History
Data" resource covers pre-2014). A collect() over any recent window
therefore returns EMPTY. The collector stays enabled: it costs one API call
per run and will light up if the Department of Neighborhoods refreshes the
extract. Records carry NO owner name — only the HCAD appraisal account and
the situs address — so clusters are keyed by HCAD account (falling back to
normalized address+zip) and the entity is the property itself.

Signal: violation_cluster — >= CLUSTER_MIN violations against the same
HCAD account / address inside the collect window. magnitude scales with
cluster size (count/10, capped at 1.0).

Self-test:
    python -m collectors.violations_houston --self-test
collects the last 30 days into an in-memory store (expected EMPTY, see
caveat), prints counts, saves fixtures/violations_houston_sample.json from a
live unfiltered sample, and writes NOTHING to any sheet.
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from common.http import fetch  # noqa: E402
from common.normalize import clean_zip, entity_key, normalize_name  # noqa: E402

CKAN_SQL_URL = "https://data.houstontx.gov/api/3/action/datastore_search_sql"
CKAN_SEARCH_URL = "https://data.houstontx.gov/api/3/action/datastore_search"
RESOURCE_ID = "1446a3ec-2633-4cf1-b15d-6dae9a07c4ed"
DATASET_URL = ("https://data.houstontx.gov/dataset/"
               "city-of-houston-building-code-enforcement-violations-don")

PAGE_SIZE = 5000
MAX_PAGES = 40                # hard stop: 200k rows per run
CLUSTER_MIN = 3               # violations at one property to call it a cluster
COLUMNS = ('"NPPRJID","Sr_Request_Num","RecordCreateDate","HCAD",'
           '"Merged_Situs","Zip","CouncilDistrict","Violation_Category",'
           '"ShortDescription","Project_Status"')


def _ckan_sql(sql):
    resp = fetch(CKAN_SQL_URL, params={"sql": sql})
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"CKAN SQL error: {json.dumps(data)[:300]}")
    return data["result"]["records"]


def _cluster_key(rec):
    """HCAD appraisal account when present, else normalized situs+zip."""
    hcad = (rec.get("HCAD") or "").strip()
    if hcad and hcad.strip("0"):
        return f"hcad:{hcad}"
    situs = normalize_name(rec.get("Merged_Situs") or "").lower()
    return f"addr:{situs}|{clean_zip(rec.get('Zip'))}"


class Collector(BaseCollector):
    avenue = "property_mgmt"
    source_id = "violations_houston"
    metros = ("houston",)

    def __init__(self):
        self._fixture = None

    # -- source IO ----------------------------------------------------------

    def _fetch_since(self, since):
        """Page violations with RecordCreateDate >= since (text column,
        'YYYY-MM-DD HH:MM:SS', so ISO-date comparison is lexicographic-safe).
        """
        records = []
        for page in range(MAX_PAGES):
            sql = (f'SELECT {COLUMNS} FROM "{RESOURCE_ID}" '
                   f'WHERE "RecordCreateDate" >= \'{since.isoformat()}\' '
                   f'ORDER BY "RecordCreateDate", "_id" '
                   f'LIMIT {PAGE_SIZE} OFFSET {page * PAGE_SIZE}')
            batch = _ckan_sql(sql)
            records.extend(batch)
            if batch and self._fixture is None:
                self._fixture = {"source": CKAN_SQL_URL,
                                 "resource_id": RESOURCE_ID,
                                 "sql": sql,
                                 "sample_records": batch[:10]}
            if len(batch) < PAGE_SIZE:
                break
        return records

    # -- contract ------------------------------------------------------------

    def collect(self, since, store, registry):
        today = date.today()
        signals_added = 0
        entities = set()
        notes = []
        try:
            records = self._fetch_since(since)
            if not records:
                notes.append("0 rows since "
                             f"{since.isoformat()} - dataset is a static "
                             "extract ending 2018-08-22 (still pinned; will "
                             "light up if the city refreshes it)")
                return CollectorResult(self.source_id, 0, 0, "EMPTY",
                                       error="; ".join(notes))
            clusters = defaultdict(list)
            for rec in records:
                clusters[_cluster_key(rec)].append(rec)
            for key, recs in clusters.items():
                entities.add(key)
                dates = sorted((r.get("RecordCreateDate") or "")[:10]
                               for r in recs if r.get("RecordCreateDate"))
                last_date = dates[-1] if dates else since.isoformat()
                categories = Counter((r.get("Violation_Category") or "?")
                                     for r in recs)
                situs_counts = Counter((r.get("Merged_Situs") or "").strip()
                                       for r in recs
                                       if (r.get("Merged_Situs") or "").strip())
                situs = (situs_counts.most_common(1)[0][0]
                         if situs_counts else key)
                zip5 = ""
                for r in recs:
                    zip5 = clean_zip(r.get("Zip"))
                    if zip5:
                        break
                # snapshot every property's window count (baseline diffs)
                store.add_snapshot(self.source_id, today.isoformat(), key, {
                    "window_start": since.isoformat(),
                    "count": len(recs),
                    "last_violation": last_date,
                    "situs": situs,
                    "zip": zip5,
                    "categories": dict(categories),
                })
                if len(recs) < CLUSTER_MIN:
                    continue
                ids = sorted({str(r.get("NPPRJID")) for r in recs
                              if r.get("NPPRJID")})
                sig = Signal(
                    entity_key=entity_key(situs, zip5),
                    entity_name=situs,
                    metro="houston",
                    avenue=self.avenue,
                    signal_type="violation_cluster",
                    signal_date=last_date,
                    magnitude=round(min(1.0, len(recs) / 10.0), 3),
                    source_id=self.source_id,
                    source_ref=f"{DATASET_URL}#{key}",
                    raw={
                        "cluster_key": key,
                        "violations_in_window": len(recs),
                        "window_start": since.isoformat(),
                        "categories": dict(categories),
                        "project_ids": ids[:25],
                        "resource_id": RESOURCE_ID,
                    },
                    attrs={"street": situs, "zip": zip5},
                )
                if store.add_signal(sig):
                    signals_added += 1
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
    if col._fixture is None:
        # expected: no rows in a recent window (extract ends 2018-08-22).
        # Save a live raw sample from the datastore instead so the fixture
        # proves the source is reachable and shows real record shape.
        try:
            resp = fetch(CKAN_SEARCH_URL,
                         params={"resource_id": RESOURCE_ID, "limit": 5})
            col._fixture = {
                "source": CKAN_SEARCH_URL,
                "resource_id": RESOURCE_ID,
                "note": ("unfiltered sample; datastore is live but the "
                         "extract ends 2018-08-22, so recent windows are "
                         "EMPTY"),
                "response": resp.json().get("result", {}).get("records", []),
            }
        except Exception as exc:  # noqa: BLE001
            col._fixture = {"source": CKAN_SEARCH_URL,
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
