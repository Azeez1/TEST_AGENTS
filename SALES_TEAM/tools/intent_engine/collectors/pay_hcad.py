"""Ability-to-pay collector: HCAD parcel ownership (source_id: pay_hcad).

property_mgmt's pay data MUST come from parcel ownership, not SBA — the spike
(2026-07-06) showed property_mgmt entities match SBA borrower names at only
0.2%. This collector groups Harris County (Houston) parcels by normalized
owner-of-record name and attaches `size_parcels` pay signals to EXISTING
property_mgmt entities: a landlord who owns 40 parcels can pay for software;
one who owns 1 cannot.

Data source — HCAD public CAMA export (hcad.org/pdata):
    https://download.hcad.org/data/CAMA/{year}/Real_acct_owner.zip  (~210 MB,
    verified live 2026-07-06, plain GET, no auth). Member real_acct.txt is
    ~872 MB tab-delimited with header; owner-of-record = `mailto` column.
    The ZIP is cached in ~/.dux_intent/cache/hcad/ and re-downloaded only
    when older than CACHE_MAX_AGE_DAYS (80). real_acct.txt is STREAMED
    straight out of the cached ZIP (zipfile + TextIOWrapper) — the 872 MB
    file is never extracted to disk nor loaded into RAM; only counts for
    owner names that match a store entity are kept.

Join rule (identity claim; signal lands on the entity's own entity_key):
    normalized owner name == entity name_norm (property_mgmt, houston),
    name passes name_quality_ok, owner name not in the placeholder set
    ("CURRENT OWNER" etc. — HCAD uses these when ownership is in flux).
    Limitation (documented in the registry): this measures parcels OWNED
    under the exact entity name. Third-party managers who own nothing, and
    owners who title each property in a separate LLC, both under-count.

Signal contract (frozen v2):
    signal_type  size_parcels   (registered under solvency_signals)
    magnitude    SIZE_ATTR_NORMALIZERS['parcel_count'](n)
                 = log10(n+1)/log10(201)  -> 200 parcels = 1.0
    signal_date  today, CHANGE-GATED via snapshots: a signal is emitted only
                 when the owner's parcel_count changes (or on first sight),
                 so daily scans do not re-emit unchanged counts.
    attrs        parcel_count stamped on the entity via upsert_entity AND on
                 the signal (SIZE-ATTR fallback contract).

Self-test (seeds real-DB entities read-only into a throwaway store):
    python -m collectors.pay_hcad --self-test [--cap N]
"""
import io
import sys
import time
import zipfile
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._pay_common import (entity_name_index,  # noqa: E402
                                    pay_selftest_main)
from common import http  # noqa: E402
from common.normalize import normalize_name  # noqa: E402
from common.solvency import SIZE_ATTR_NORMALIZERS  # noqa: E402

URL_TMPL = "https://download.hcad.org/data/CAMA/{year}/Real_acct_owner.zip"
PDATA_PAGE = "https://hcad.org/pdata/pdata-property-downloads.html"
ZIP_NAME = "Real_acct_owner.zip"
MEMBER = "real_acct.txt"
CACHE_MAX_AGE_DAYS = 80
SAMPLE_ACCTS = 3                     # parcel account numbers kept as evidence

# HCAD placeholder owner names (normalized) — never join on these
PLACEHOLDER_OWNERS = {
    "CURRENT OWNER", "OWNER CURRENT", "OWNER", "PROPERTY OWNER",
    "UNKNOWN", "UNKNOWN OWNER", "NOT AVAILABLE", "N A", "NA", "NONE",
}


class PayHcadCollector(BaseCollector):
    avenue = "property_mgmt"
    source_id = "pay_hcad"
    metros = ("houston",)

    def __init__(self):
        self.sample_payload = None

    # ------------------------------------------------------ download / cache

    def _cache_path(self):
        d = config.CACHE_DIR / "hcad"
        d.mkdir(parents=True, exist_ok=True)
        return d / ZIP_NAME

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
                # sanity: must be a zip containing the member we parse
                with zipfile.ZipFile(tmp) as zf:
                    if MEMBER not in zf.namelist():
                        raise RuntimeError(
                            f"{url} zip is missing {MEMBER} "
                            f"(members: {zf.namelist()[:10]})")
                tmp.replace(dest)
                return dest
            except Exception as exc:
                last_exc = exc
                tmp.unlink(missing_ok=True)
                time.sleep(http.BACKOFF_BASE * (2 ** attempt))
        raise last_exc

    def _ensure_zip(self, notes):
        """Return the cached ZIP path, downloading/refreshing when > 80d old.
        Tries the current CAMA year then the previous (year rolls over before
        the new export appears). Stale cache beats a failed refresh."""
        dest = self._cache_path()
        if dest.exists():
            age_days = (time.time() - dest.stat().st_mtime) / 86400.0
            if age_days < CACHE_MAX_AGE_DAYS:
                return dest
        year = date.today().year
        last_exc = None
        for y in (year, year - 1):
            try:
                return self._download_stream(URL_TMPL.format(year=y), dest)
            except Exception as exc:
                last_exc = exc
                notes.append(f"CAMA {y} download failed: "
                             f"{type(exc).__name__}: {exc}")
        if dest.exists():
            notes.append("using stale cached ZIP (refresh failed)")
            return dest
        raise last_exc if last_exc else RuntimeError("HCAD download failed")

    # ------------------------------------------------------------- scanning

    def _owner_counts(self, zip_path, targets):
        """Stream real_acct.txt out of the ZIP; count parcels per matching
        normalized owner name. Returns {name_norm: {'count', 'accts', 'raw'}}.
        Only target names are kept, so memory stays O(matched entities)."""
        counts = {}
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open(MEMBER) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8",
                                        errors="replace", newline="")
                header = text.readline().rstrip("\r\n").split("\t")
                idx = {h.strip().lower(): i for i, h in enumerate(header)}
                if "mailto" not in idx or "acct" not in idx:
                    raise RuntimeError(
                        f"{MEMBER}: expected 'mailto'/'acct' columns, got "
                        f"{header[:10]}")
                i_owner, i_acct = idx["mailto"], idx["acct"]
                n_cols = max(i_owner, i_acct) + 1
                for line in text:
                    cells = line.split("\t")
                    if len(cells) < n_cols:
                        continue
                    owner = cells[i_owner].strip()
                    if not owner:
                        continue
                    nn = normalize_name(owner).lower()
                    if nn not in targets:
                        continue
                    rec = counts.setdefault(nn, {"count": 0, "accts": [],
                                                 "raw": owner})
                    rec["count"] += 1
                    if len(rec["accts"]) < SAMPLE_ACCTS:
                        rec["accts"].append(cells[i_acct].strip())
        return counts

    # ------------------------------------------------------------- emission

    def _emit(self, store, entity, rec, today):
        """Snapshot-gated size_parcels emission for one matched entity."""
        n = rec["count"]
        item_key = f"owner:{(entity.get('name_norm') or '').lower()}"
        snaps = store.get_snapshots(self.source_id, item_key)
        prev = None
        for s in snaps:
            if s["snapshot_date"] < today.isoformat():
                prev = s["payload"]
        store.add_snapshot(self.source_id, today.isoformat(), item_key,
                           {"parcel_count": n})
        # stamp the raw size attr regardless (SIZE-ATTR fallback contract)
        store.upsert_entity(entity["entity_key"], entity["avenue"],
                            entity["metro"], entity["name"],
                            attrs={"parcel_count": n})
        if isinstance(prev, dict) and prev.get("parcel_count") == n:
            return False                       # unchanged -> no re-emit
        sig = Signal(
            entity_key=entity["entity_key"],
            entity_name=entity["name"],
            metro=entity["metro"],
            avenue=entity["avenue"],
            signal_type="size_parcels",
            signal_date=today.isoformat(),
            magnitude=SIZE_ATTR_NORMALIZERS["parcel_count"](n),
            source_id=self.source_id,
            source_ref=(f"{PDATA_PAGE}#real_acct:"
                        + (entity.get("name_norm") or "").replace(" ", "_")),
            raw={"parcel_count": n, "owner_name_raw": rec["raw"],
                 "sample_accts": rec["accts"], "county": "HARRIS"},
            attrs={"parcel_count": n},
        )
        return store.add_signal(sig)

    # -------------------------------------------------------------- collect

    def collect(self, since, store, registry):
        try:
            notes = []
            today = date.today()
            index = entity_name_index(store, (self.avenue,),
                                      metros=self.metros)
            index = {nn: ents for nn, ents in index.items()
                     if nn.upper() not in PLACEHOLDER_OWNERS}
            if not index:
                return CollectorResult(
                    self.source_id, 0, 0, "EMPTY",
                    "no property_mgmt/houston entities in store — pay "
                    "signals attach to existing entities; run the pain "
                    "collectors first")
            zip_path = self._ensure_zip(notes)
            counts = self._owner_counts(zip_path, set(index))
            added, entities = 0, set()
            for nn, rec in counts.items():
                for ent in index[nn]:
                    if self._emit(store, ent, rec, today):
                        added += 1
                    entities.add(ent["entity_key"])
                    if self.sample_payload is None:
                        self.sample_payload = {
                            "matched_entity": {
                                k: ent.get(k) for k in
                                ("entity_key", "name", "avenue", "metro")},
                            "parcel_count": rec["count"],
                            "owner_name_raw": rec["raw"],
                            "sample_accts": rec["accts"],
                            "zip_file": str(zip_path),
                        }
            if not counts:
                notes.append(f"0 of {len(index)} entity names own parcels "
                             "under their exact name (third-party managers "
                             "and per-property LLCs under-count; documented "
                             "limitation)")
            status = "OK" if added > 0 else "EMPTY"
            if entities and added == 0:
                # matches existed but every count was unchanged (steady state)
                status = "OK"
                notes.append(f"{len(entities)} matched entities, all "
                             "parcel counts unchanged since last snapshot")
            return CollectorResult(self.source_id, added, len(entities),
                                   status, "; ".join(notes))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = PayHcadCollector


if __name__ == "__main__":
    sys.exit(pay_selftest_main(Collector, ("property_mgmt",),
                               __doc__.splitlines()[0]))
