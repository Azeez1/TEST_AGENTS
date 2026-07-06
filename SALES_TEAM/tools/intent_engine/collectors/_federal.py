"""Shared helpers for the FEDERAL-API collectors (osha_dol, epa_echo, warn_tx_ga, sba_loans).

Internal to these four collectors only — NOT part of the frozen interface and never
loaded by load_collectors() (which imports strictly by source_id).
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

FIXTURES_DIR = ENGINE_ROOT / "fixtures"

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Minimal city -> metro fallback, used only when a record has no county AND no zip.
CITY_TO_METRO = {
    "houston": {
        "HOUSTON", "PASADENA", "BAYTOWN", "KATY", "SPRING", "HUMBLE", "CYPRESS",
        "TOMBALL", "SUGAR LAND", "MISSOURI CITY", "STAFFORD", "RICHMOND",
        "ROSENBERG", "THE WOODLANDS", "CONROE", "LA PORTE", "PEARLAND", "WEBSTER",
        "CHANNELVIEW", "DEER PARK",
    },
    "atlanta": {
        "ATLANTA", "MARIETTA", "SMYRNA", "KENNESAW", "ACWORTH", "LAWRENCEVILLE",
        "DULUTH", "NORCROSS", "SUWANEE", "BUFORD", "DECATUR", "TUCKER",
        "STONE MOUNTAIN", "LITHONIA", "ALPHARETTA", "SANDY SPRINGS", "ROSWELL",
        "EAST POINT", "COLLEGE PARK", "AUSTELL", "POWDER SPRINGS", "SNELLVILLE",
    },
}


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))


def strip_tags(s):
    """Remove HTML tags/entities and collapse whitespace."""
    import html as _html
    if s is None:
        return ""
    s = re.sub(r"<br\s*/?>", ", ", str(s), flags=re.I)
    s = _TAG_RE.sub(" ", s)
    s = _html.unescape(s)
    return _WS_RE.sub(" ", s).strip()


def parse_date_any(value):
    """Parse ISO / M/D/YYYY / 'June 29, 2026' style dates -> datetime.date or None."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    if not s:
        return None
    s = s.split("T")[0].strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%B %d, %Y", "%b %d, %Y",
                "%Y/%m/%d", "%d-%b-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _clean_county(county):
    if not county:
        return ""
    c = _WS_RE.sub(" ", str(county).upper().strip())
    if c.endswith(" COUNTY"):
        c = c[: -len(" COUNTY")].strip()
    return c


def metro_of(registry, state, county=None, zip5=None, city=None):
    """Map a record's location to 'houston'/'atlanta' or None.

    Precedence: county (authoritative when present) > zip prefix > city fallback.
    A known county that is NOT in the metro's county list rejects the record even
    if the zip prefix would match (zip prefixes are intentionally broad).
    """
    if not state:
        return None
    st = str(state).strip().upper()
    cn = _clean_county(county)
    from common.normalize import clean_zip
    z = clean_zip(zip5) if zip5 else ""
    ct = _WS_RE.sub(" ", str(city).upper().strip()) if city else ""
    for metro, m in registry.get("metros", {}).items():
        if str(m.get("state", "")).upper() != st:
            continue
        counties = {_clean_county(c) for c in m.get("counties", [])}
        if cn:
            return metro if cn in counties else None
        if z:
            if any(z.startswith(p) for p in m.get("zip_prefixes", [])):
                return metro
            continue
        if ct and ct in CITY_TO_METRO.get(metro, set()):
            return metro
    return None


def write_fixture(source_id, sample_payload, result=None):
    """Save one raw sample payload to fixtures/<source_id>_sample.json."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    doc = {
        "source_id": source_id,
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "self_test_status": getattr(result, "status", None),
        "self_test_error": getattr(result, "error", "") or "",
        "sample": sample_payload,
    }
    path = FIXTURES_DIR / f"{source_id}_sample.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, default=str)
    return path


def run_self_test(collector):
    """Shared --self-test harness: last 30 days into an in-memory store.

    Prints status + counts, saves fixtures/<source_id>_sample.json,
    writes NOTHING to the sheet or the real DB.
    """
    import config
    from common.store import Store

    since = date.today() - timedelta(days=30)
    registry = config.load_registry()
    store = Store(":memory:")
    print(f"[self-test] {collector.source_id}: collecting since {since.isoformat()} "
          f"into in-memory store ...")
    result = collector.collect(since, store, registry)
    sigs = store.get_signals()
    ents = store.iter_entities()
    print(f"[self-test] status          = {result.status}")
    print(f"[self-test] signals_added   = {result.signals_added}")
    print(f"[self-test] entities_seen   = {result.entities_seen}")
    if result.error:
        print(f"[self-test] error/notes     = {result.error}")
    print(f"[self-test] signals_in_store={len(sigs)} entities_in_store={len(ents)}")
    for s in sigs[:5]:
        print(f"    {s['signal_date']}  {s['signal_type']:<20} mag={s['magnitude']:.2f} "
              f"{s['metro']:<8} {s['entity_name'][:48]}")
    path = write_fixture(collector.source_id,
                         getattr(collector, "sample_payload", None), result)
    print(f"[self-test] fixture -> {path}")
    store.close()
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


def selftest_main(collector_cls, argv=None):
    parser = argparse.ArgumentParser(
        description=f"Intent Engine collector: {collector_cls.source_id}")
    parser.add_argument("--self-test", action="store_true",
                        help="collect last 30 days into a throwaway store, "
                             "print counts, save a fixture sample; no sheet, no real DB")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test(collector_cls())
    parser.print_help()
    print("\nThis module is normally run by run_intent_scan.py; "
          "standalone use supports --self-test only.")
    return 2
