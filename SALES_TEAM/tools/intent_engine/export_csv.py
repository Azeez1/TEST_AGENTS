"""CSV export — one file per avenue/metro plus a combined hotlist.

FROZEN INTERFACE:
    export_csv(rows, run_date=None, output_dir=None) -> list[Path]

Files written into OUTPUT_DIR (or output_dir override):
    intent_{avenue}_{metro}_{YYYY-MM-DD}.csv    per avenue/metro with any rows
    intent_hotlist_{YYYY-MM-DD}.csv             all hot rows across avenues/metros

Columns (exact order):
    rank,score,hot,entity_name,metro,avenue,top_signals,signal_count,
    latest_signal_date,evidence_urls,phone,email,street,zip,first_seen,match_conf
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


def _write(path, formatted_rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
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
    return written
