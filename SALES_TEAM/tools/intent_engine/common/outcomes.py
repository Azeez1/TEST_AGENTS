"""Outcome log — ground truth for tuning v2 weights later.

Records what actually happened per entity after outreach so EXPECTED_VALUE
weights stop being guesses. Tiny scaffold, same intent.db, own table.

FROZEN INTERFACE:
    record_outcome(entity_key, stage, note="", funnel="", db_path=None) -> int (row id)
        stage must be one of STAGES = drafted|sent|replied|meeting|won|lost
    get_outcomes(entity_key=None, stage=None, db_path=None) -> list[dict]
    outcome_stats(db_path=None) -> {stage: count}

CLI:
    python -m common.outcomes record <entity_key> <stage> [--note TEXT] [--funnel F]
    python -m common.outcomes list [--entity-key K] [--stage S]
    python -m common.outcomes stats
    python -m common.outcomes --self-test

NOTE: 'sent' exists for the future; v2 outbound is DRAFT-ONLY (Money Rule) —
nothing in this engine sends anything.
"""
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

STAGES = ("drafted", "sent", "replied", "meeting", "won", "lost")

SCHEMA = """
CREATE TABLE IF NOT EXISTS outcomes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_key  TEXT NOT NULL,
    stage       TEXT NOT NULL,
    funnel      TEXT DEFAULT '',
    note        TEXT DEFAULT '',
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_outcomes_entity ON outcomes(entity_key);
CREATE INDEX IF NOT EXISTS idx_outcomes_stage ON outcomes(stage);
"""


def _connect(db_path=None):
    if db_path is None:
        config.ensure_dirs()
        db_path = config.DB_PATH
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def record_outcome(entity_key, stage, note="", funnel="", db_path=None):
    """Append one outcome event. Returns the new row id. Raises ValueError on
    a bad stage (caller bug, not a source error)."""
    stage = str(stage).strip().lower()
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}, got {stage!r}")
    if not entity_key:
        raise ValueError("entity_key is required")
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO outcomes (entity_key, stage, funnel, note, recorded_at) "
            "VALUES (?,?,?,?,?)",
            (str(entity_key), stage, str(funnel or ""), str(note or ""),
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_outcomes(entity_key=None, stage=None, db_path=None):
    conn = _connect(db_path)
    try:
        q, args = "SELECT * FROM outcomes WHERE 1=1", []
        if entity_key:
            q += " AND entity_key=?"
            args.append(entity_key)
        if stage:
            q += " AND stage=?"
            args.append(str(stage).strip().lower())
        q += " ORDER BY recorded_at"
        return [dict(r) for r in conn.execute(q, args).fetchall()]
    finally:
        conn.close()


def outcome_stats(db_path=None):
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT stage, COUNT(*) AS n FROM outcomes GROUP BY stage").fetchall()
        stats = {s: 0 for s in STAGES}
        for r in rows:
            stats[r["stage"]] = r["n"]
        return stats
    finally:
        conn.close()


def _self_test():
    import tempfile
    with tempfile.TemporaryDirectory(prefix="intent_outcomes_") as td:
        db = Path(td) / "outcomes_test.db"
        rid = record_outcome("dot:2422093", "drafted", note="touch 1 queued",
                             funnel="customers", db_path=db)
        assert rid == 1
        record_outcome("dot:2422093", "replied", db_path=db)
        record_outcome("biz:acme fabrication|77041", "drafted",
                       funnel="acquisitions", db_path=db)
        try:
            record_outcome("dot:1", "ghosted", db_path=db)
            raise AssertionError("bad stage accepted")
        except ValueError:
            pass
        rows = get_outcomes(entity_key="dot:2422093", db_path=db)
        assert [r["stage"] for r in rows] == ["drafted", "replied"], rows
        stats = outcome_stats(db_path=db)
        assert stats["drafted"] == 2 and stats["replied"] == 1, stats
    print("outcomes self-test PASS (record/list/stats + stage validation)")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return _self_test()
    parser = argparse.ArgumentParser(description="Intent engine outcome log")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_rec = sub.add_parser("record")
    p_rec.add_argument("entity_key")
    p_rec.add_argument("stage", choices=STAGES)
    p_rec.add_argument("--note", default="")
    p_rec.add_argument("--funnel", default="")
    p_list = sub.add_parser("list")
    p_list.add_argument("--entity-key", default=None)
    p_list.add_argument("--stage", default=None)
    sub.add_parser("stats")
    args = parser.parse_args(argv)
    if args.cmd == "record":
        rid = record_outcome(args.entity_key, args.stage, note=args.note,
                             funnel=args.funnel)
        print(f"recorded outcome #{rid}: {args.entity_key} -> {args.stage}")
    elif args.cmd == "list":
        for r in get_outcomes(entity_key=args.entity_key, stage=args.stage):
            print(json.dumps(r))
    elif args.cmd == "stats":
        print(json.dumps(outcome_stats(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
