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
import json
import os
import sqlite3
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
# Persisted owner-name -> parcel-count index. Building it means streaming +
# normalizing the 872 MB HCAD member (multi-minute); once persisted, later
# runs load only the counts for the entities they need (sub-second) and never
# touch the raw export until it is re-downloaded (see _counts_cache_fresh).
COUNTS_CACHE_NAME = "owner_parcel_counts.sqlite"

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

    def _owner_counts(self, zip_path, targets=None):
        """Stream real_acct.txt out of the ZIP; count parcels per normalized
        owner name. Returns {name_norm: {'count', 'accts', 'raw'}}.

        targets is a set -> keep only those names (memory O(matched entities));
        targets is None -> keep EVERY owner (used to build the persistent
        counts cache once, so subsequent runs never re-stream the export)."""
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
                    if targets is not None and nn not in targets:
                        continue
                    rec = counts.setdefault(nn, {"count": 0, "accts": [],
                                                 "raw": owner})
                    rec["count"] += 1
                    if len(rec["accts"]) < SAMPLE_ACCTS:
                        rec["accts"].append(cells[i_acct].strip())
        return counts

    # ---------------------------------------------------- persistent counts cache

    def _counts_cache_path(self):
        d = config.CACHE_DIR / "hcad"
        d.mkdir(parents=True, exist_ok=True)
        return d / COUNTS_CACHE_NAME

    @staticmethod
    def _counts_cache_fresh(cache_path, zip_path):
        """Cache is usable only if it exists and is at least as new as the raw
        HCAD ZIP. A re-download bumps the ZIP mtime past the cache -> rebuild."""
        try:
            return (cache_path.exists()
                    and cache_path.stat().st_mtime >= zip_path.stat().st_mtime)
        except OSError:
            return False

    def _build_counts_cache(self, zip_path, cache_path):
        """Parse the full owner-name -> parcel-count map ONCE and persist it to
        a small sqlite index. Written to a temp file then atomically renamed so
        a crash mid-build never leaves a half-written cache in place."""
        counts = self._owner_counts(zip_path, targets=None)   # ALL owners
        tmp = cache_path.with_suffix(cache_path.suffix + ".part")
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        conn = sqlite3.connect(str(tmp))
        try:
            conn.execute("PRAGMA journal_mode=OFF")
            conn.execute("PRAGMA synchronous=OFF")
            conn.execute(
                "CREATE TABLE owner_counts (name_norm TEXT PRIMARY KEY, "
                "cnt INTEGER NOT NULL, raw TEXT, accts TEXT)")
            conn.executemany(
                "INSERT OR REPLACE INTO owner_counts "
                "(name_norm, cnt, raw, accts) VALUES (?,?,?,?)",
                ((nn, rec["count"], rec["raw"], json.dumps(rec["accts"]))
                 for nn, rec in counts.items()))
            conn.commit()
        finally:
            conn.close()
        os.replace(str(tmp), str(cache_path))
        return len(counts)

    def _load_counts_cache(self, cache_path, targets):
        """Fetch counts for just the target names from the persisted cache."""
        conn = sqlite3.connect(f"file:{Path(cache_path).as_posix()}?mode=ro",
                               uri=True)
        conn.row_factory = sqlite3.Row
        out = {}
        try:
            names = list(targets)
            chunk = 400              # stay well under SQLite's variable limit
            for i in range(0, len(names), chunk):
                part = names[i:i + chunk]
                q = ("SELECT name_norm, cnt, raw, accts FROM owner_counts "
                     f"WHERE name_norm IN ({','.join('?' * len(part))})")
                for r in conn.execute(q, part):
                    try:
                        accts = json.loads(r["accts"]) if r["accts"] else []
                    except (TypeError, ValueError):
                        accts = []
                    out[r["name_norm"]] = {"count": r["cnt"],
                                           "raw": r["raw"] or "",
                                           "accts": accts}
        finally:
            conn.close()
        return out

    def _owner_counts_cached(self, targets, zip_path, notes):
        """Return {name_norm: rec} for target owners, using the persistent
        cache when it is newer than the raw ZIP, else (re)building it first."""
        cache_path = self._counts_cache_path()
        if self._counts_cache_fresh(cache_path, zip_path):
            try:
                counts = self._load_counts_cache(cache_path, targets)
                notes.append("owner-parcel counts served from cache")
                return counts
            except Exception as exc:
                notes.append(f"counts cache unreadable "
                             f"({type(exc).__name__}: {exc}); rebuilding")
        built = self._build_counts_cache(zip_path, cache_path)
        notes.append(f"owner-parcel counts cache built ({built} owners) "
                     "from HCAD export")
        return self._load_counts_cache(cache_path, targets)

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
            counts = self._owner_counts_cached(set(index), zip_path, notes)
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
