"""Ability-to-pay collector: FMCSA census fleet size (source_id: pay_census_size).

Light enrichment for EXISTING trucking entities (dot:{dot} keys): pulls
power_units + mcs150_mileage from the FMCSA census Socrata dataset (the same
az4n-8mr2 the trucking_fmcsa pain collector reads) and emits a `size_fleet`
pay signal per carrier. Trucking matches its pay source by construction —
the DOT number IS the join key, so there is no name-matching risk at all.

trucking_fmcsa already stamps power_units on its signal attrs (which is why
trucking rows show pay_data=partial today); this collector upgrades that to a
proper solvency signal and adds mcs150_mileage (annual miles — the best free
revenue proxy for a carrier).

Signal contract (frozen v2):
    signal_type  size_fleet   (registered under solvency_signals)
    magnitude    max(log10(power_units+1)/log10(501), log10(miles+1)/7)
                 (SIZE_ATTR_NORMALIZERS['power_units' / 'mcs150_mileage'])
    signal_date  today, CHANGE-GATED via snapshots: emitted only when the
                 census values change (or on first sight) so daily scans do
                 not re-emit unchanged fleet data.
    attrs        power_units + mcs150_mileage stamped on the entity via
                 upsert_entity AND on the signal (SIZE-ATTR fallback).

Self-test (seeds real-DB trucking entities read-only into a throwaway store):
    python -m collectors.pay_census_size --self-test [--cap N]
"""
import sys
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._pay_common import pay_selftest_main  # noqa: E402
from common.http import soda  # noqa: E402
from common.solvency import SIZE_ATTR_NORMALIZERS  # noqa: E402

DS_CENSUS = "az4n-8mr2"        # FMCSA census (same dataset trucking_fmcsa uses)
DOT_BATCH = 100
CENSUS_SELECT = ("dot_number, legal_name, power_units, mcs150_mileage, "
                 "mcs150_mileage_year")


def _safer_url(dot):
    return ("https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY"
            f"&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={dot}")


def _num(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class PayCensusSizeCollector(BaseCollector):
    avenue = "trucking"
    source_id = "pay_census_size"
    metros = ("houston", "atlanta")

    def __init__(self):
        self.sample_payload = None

    def _fleet_magnitude(self, pu, mi):
        """max over the two explicit size normalizations (registry formula)."""
        mags = []
        if pu > 0:
            mags.append(SIZE_ATTR_NORMALIZERS["power_units"](pu))
        if mi > 0:
            mags.append(SIZE_ATTR_NORMALIZERS["mcs150_mileage"](mi))
        return max(mags) if mags else None

    def _emit(self, store, entity, row, today):
        """Snapshot-gated size_fleet emission for one carrier."""
        dot = entity["entity_key"].split(":", 1)[1]
        pu = _num(row.get("power_units"))
        mi = _num(row.get("mcs150_mileage"))
        mag = self._fleet_magnitude(pu, mi)
        if mag is None:
            return False                    # census has no size data at all
        payload = {"power_units": pu, "mcs150_mileage": mi}
        snaps = store.get_snapshots(self.source_id, entity["entity_key"])
        prev = None
        for s in snaps:
            if s["snapshot_date"] < today.isoformat():
                prev = s["payload"]
        store.add_snapshot(self.source_id, today.isoformat(),
                           entity["entity_key"], payload)
        # stamp raw size attrs regardless (SIZE-ATTR fallback contract)
        store.upsert_entity(entity["entity_key"], entity["avenue"],
                            entity["metro"], entity["name"], attrs=payload)
        if isinstance(prev, dict) and all(prev.get(k) == v
                                          for k, v in payload.items()):
            return False                    # unchanged -> no re-emit
        sig = Signal(
            entity_key=entity["entity_key"],
            entity_name=entity["name"],
            metro=entity["metro"],
            avenue=entity["avenue"],
            signal_type="size_fleet",
            signal_date=today.isoformat(),
            magnitude=round(mag, 4),
            source_id=self.source_id,
            source_ref=_safer_url(dot),
            raw={"census": row,
                 "mcs150_mileage_year": row.get("mcs150_mileage_year")},
            attrs=payload,
        )
        return store.add_signal(sig)

    def collect(self, since, store, registry):
        try:
            notes = []
            today = date.today()
            ents = {}
            for metro in self.metros:
                for e in store.iter_entities(avenue=self.avenue, metro=metro):
                    key = e.get("entity_key", "")
                    if key.startswith("dot:") and key.split(":", 1)[1].isdigit():
                        ents[key.split(":", 1)[1]] = e
            if not ents:
                return CollectorResult(
                    self.source_id, 0, 0, "EMPTY",
                    "no trucking dot:* entities in store — pay signals "
                    "attach to existing entities; run trucking_fmcsa first")
            added, seen = 0, set()
            failed_batches = 0
            batches = list(_batched(sorted(ents, key=int), DOT_BATCH))
            for batch in batches:
                inlist = ",".join(f"'{d}'" for d in batch)
                try:
                    rows = soda(DS_CENSUS, {
                        "$select": CENSUS_SELECT,
                        "$where": f"dot_number in ({inlist})",
                        "$limit": str(DOT_BATCH * 2),
                    })
                except Exception as exc:
                    failed_batches += 1
                    notes.append(f"census batch failed: "
                                 f"{type(exc).__name__}: {exc}")
                    continue
                for row in rows:
                    dot = str(row.get("dot_number", "")).strip()
                    ent = ents.get(dot)
                    if ent is None:
                        continue
                    if self._emit(store, ent, row, today):
                        added += 1
                    seen.add(ent["entity_key"])
                    if self.sample_payload is None:
                        self.sample_payload = {"census": row,
                                               "entity_key": ent["entity_key"]}
            if failed_batches == len(batches):
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       "; ".join(notes[:3]))
            if added == 0 and seen:
                notes.append(f"{len(seen)} carriers matched, all census "
                             "values unchanged since last snapshot")
                status = "OK"
            else:
                status = "OK" if added > 0 else "EMPTY"
            return CollectorResult(self.source_id, added, len(seen), status,
                                   "; ".join(notes[:5]))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = PayCensusSizeCollector


if __name__ == "__main__":
    sys.exit(pay_selftest_main(Collector, ("trucking",),
                               __doc__.splitlines()[0], default_cap=150))
