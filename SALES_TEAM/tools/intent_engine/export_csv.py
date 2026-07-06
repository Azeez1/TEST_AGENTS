"""CSV export — one file per avenue/metro, a combined hotlist, and (v2) the
two funnel lists ranked by EXPECTED_VALUE.

FROZEN INTERFACE:
    export_csv(rows, run_date=None, output_dir=None) -> list[Path]

Files written into OUTPUT_DIR (or output_dir override):
    intent_{avenue}_{metro}_{YYYY-MM-DD}.csv    per avenue/metro with any rows
    intent_hotlist_{YYYY-MM-DD}.csv             all hot rows across avenues/metros
    intent_customers_{YYYY-MM-DD}.csv           v2: funnel=customers ranked by EV
    intent_acquisitions_{YYYY-MM-DD}.csv        v2: funnel=acquisitions ranked by EV

v1 columns (exact order, unchanged):
    rank,score,hot,entity_name,metro,avenue,top_signals,signal_count,
    latest_signal_date,evidence_urls,phone,email,street,zip,first_seen,match_conf
v2 funnel columns (exact order):
    rank,expected_value,pain,timing,ability_to_pay,deal_size,pay_data,entity,
    metro,top_signals,evidence,contact,avenue,timing_window,hot
"""
import csv
import sys
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402

COLUMNS = [
    "rank", "score", "hot", "entity_name", "metro", "avenue", "top_signals",
    "signal_count", "latest_signal_date", "evidence_urls", "phone", "email",
    "street", "zip", "first_seen", "match_conf",
]

V2_COLUMNS = [
    "rank", "expected_value", "pain", "timing", "ability_to_pay", "deal_size",
    "pay_data", "entity", "metro", "top_signals", "evidence", "contact",
    "avenue", "timing_window", "hot",
]

FUNNELS = ("customers", "acquisitions")
# fallback when a row lacks a funnel tag (registry avenues carry the canonical tag)
FUNNEL_BY_AVENUE = {
    "trucking": "customers", "property_mgmt": "customers",
    "mechanical": "customers", "manufacturing": "customers",
    "dead_listings": "acquisitions", "pe_distress": "acquisitions",
}


def _contact_str(row):
    parts = [row.get("phone") or "", row.get("email") or ""]
    street_zip = " ".join(p for p in (row.get("street") or "",
                                      row.get("zip") or "") if p)
    parts.append(street_zip)
    return " | ".join(p for p in parts if p)


def _fmt_v2(row, rank):
    return {
        "rank": rank,
        "expected_value": f"{float(row.get('expected_value', 0.0)):.4f}",
        "pain": f"{float(row.get('pain', row.get('score', 0.0))):.2f}",
        "timing": f"{float(row.get('timing', 1.0)):.2f}",
        "ability_to_pay": f"{float(row.get('ability_to_pay', 0.5)):.2f}",
        "deal_size": f"{float(row.get('deal_size', 0.5)):.2f}",
        "pay_data": row.get("pay_data", "unknown"),
        "entity": row.get("entity_name", ""),
        "metro": row.get("metro", ""),
        "top_signals": row.get("top_signals", ""),
        "evidence": row.get("evidence_urls", ""),
        "contact": _contact_str(row),
        "avenue": row.get("avenue", ""),
        "timing_window": row.get("timing_window", ""),
        "hot": "TRUE" if row.get("hot") else "FALSE",
    }


def row_funnel(row):
    return row.get("funnel") or FUNNEL_BY_AVENUE.get(row.get("avenue", ""),
                                                     "customers")


def _fmt(row, rank):
    return {
        "rank": rank,
        "score": f"{float(row.get('score', 0.0)):.2f}",
        "hot": "TRUE" if row.get("hot") else "FALSE",
        "entity_name": row.get("entity_name", ""),
        "metro": row.get("metro", ""),
        "avenue": row.get("avenue", ""),
        "top_signals": row.get("top_signals", ""),
        "signal_count": row.get("signal_count", 0),
        "latest_signal_date": row.get("latest_signal_date", ""),
        "evidence_urls": row.get("evidence_urls", ""),
        "phone": row.get("phone", "") or "",
        "email": row.get("email", "") or "",
        "street": row.get("street", "") or "",
        "zip": row.get("zip", "") or "",
        "first_seen": row.get("first_seen", ""),
        "match_conf": f"{float(row.get('match_conf', 1.0)):.2f}",
    }


def _write(path, formatted_rows, columns=COLUMNS):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(formatted_rows)


def export_csv(rows, run_date=None, output_dir=None):
    """rows: list of dicts (all COLUMNS except rank; 'hot' bool, 'score' float).
    Returns list of Paths written."""
    if run_date is None:
        run_date = date.today().isoformat()
    out_dir = Path(output_dir) if output_dir else config.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    groups = {}
    for r in rows:
        groups.setdefault((r["avenue"], r["metro"]), []).append(r)

    for (avenue, metro), grp in sorted(groups.items()):
        grp.sort(key=lambda r: -float(r.get("score", 0.0)))
        formatted = [_fmt(r, i + 1) for i, r in enumerate(grp)]
        path = out_dir / f"intent_{avenue}_{metro}_{run_date}.csv"
        _write(path, formatted)
        written.append(path)

    hot = sorted([r for r in rows if r.get("hot")],
                 key=lambda r: -float(r.get("score", 0.0)))
    hot_formatted = [_fmt(r, i + 1) for i, r in enumerate(hot)]
    hot_path = out_dir / f"intent_hotlist_{run_date}.csv"
    _write(hot_path, hot_formatted)
    written.append(hot_path)

    # v2: the two funnel lists, ranked by expected_value across avenues/metros
    for funnel in FUNNELS:
        frows = sorted([r for r in rows if row_funnel(r) == funnel],
                       key=lambda r: -float(r.get("expected_value", 0.0)))
        formatted = [_fmt_v2(r, i + 1) for i, r in enumerate(frows)]
        path = out_dir / f"intent_{funnel}_{run_date}.csv"
        _write(path, formatted, columns=V2_COLUMNS)
        written.append(path)
    return written
