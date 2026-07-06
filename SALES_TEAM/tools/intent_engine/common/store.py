"""SQLite persistence for the Intent Signal Engine.

FROZEN INTERFACE — methods collectors may call:
    store.upsert_entity(entity_key, avenue, metro, name, zip=None, phone=None, email=None, street=None, attrs=None)
    store.add_signal(sig)                                   # idempotent via dedup_hash
    store.add_snapshot(source_id, snapshot_date, item_key, payload)
    store.get_snapshots(source_id, item_key)                # ordered by snapshot_date
    store.first_seen(source_id, item_key)                   # ISO date or None

Additional methods (orchestrator/scoring use — collectors must not call):
    start_run, finish_run, get_signals, get_entity, iter_entities, save_score
"""
import hashlib
import json
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    entity_key  TEXT PRIMARY KEY,
    avenue      TEXT NOT NULL,
    metro       TEXT NOT NULL,
    name        TEXT NOT NULL,
    name_norm   TEXT,
    zip         TEXT,
    phone       TEXT,
    email       TEXT,
    street      TEXT,
    attrs       TEXT,                 -- JSON
    first_seen  TEXT NOT NULL,        -- ISO date
    last_seen   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signals (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    dedup_hash   TEXT NOT NULL UNIQUE,
    entity_key   TEXT NOT NULL,
    entity_name  TEXT NOT NULL,
    metro        TEXT NOT NULL,
    avenue       TEXT NOT NULL,
    signal_type  TEXT NOT NULL,
    signal_date  TEXT NOT NULL,       -- ISO date
    magnitude    REAL NOT NULL,
    source_id    TEXT NOT NULL,
    source_ref   TEXT NOT NULL,
    raw          TEXT,                -- JSON
    attrs        TEXT,                -- JSON
    created_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_signals_entity ON signals(entity_key);
CREATE INDEX IF NOT EXISTS idx_signals_avenue_metro ON signals(avenue, metro);
CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date);

CREATE TABLE IF NOT EXISTS snapshots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id     TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    item_key      TEXT NOT NULL,
    payload       TEXT NOT NULL,      -- JSON
    created_at    TEXT NOT NULL,
    UNIQUE(source_id, snapshot_date, item_key)
);
CREATE INDEX IF NOT EXISTS idx_snapshots_item ON snapshots(source_id, item_key);

CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    args        TEXT,                 -- JSON of CLI args
    status      TEXT DEFAULT 'RUNNING',
    summary     TEXT                  -- JSON per-collector results
);

CREATE TABLE IF NOT EXISTS scores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER,
    entity_key   TEXT NOT NULL,
    avenue       TEXT NOT NULL,
    metro        TEXT NOT NULL,
    score        REAL NOT NULL,
    hot          INTEGER NOT NULL,
    signal_types TEXT,                -- JSON list
    scored_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_scores_run ON scores(run_id);
"""


def dedup_hash(entity_key, signal_type, signal_date, source_ref):
    payload = f"{entity_key}|{signal_type}|{signal_date}|{source_ref}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


class Store:
    def __init__(self, db_path=None):
        if db_path is None:
            config.ensure_dirs()
            db_path = config.DB_PATH
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ---------- entities ----------

    def upsert_entity(self, entity_key, avenue, metro, name, zip=None, phone=None,
                      email=None, street=None, attrs=None):
        from common.normalize import normalize_name
        today = date.today().isoformat()
        row = self.conn.execute(
            "SELECT entity_key, attrs FROM entities WHERE entity_key=?", (entity_key,)
        ).fetchone()
        if row is None:
            self.conn.execute(
                "INSERT INTO entities (entity_key, avenue, metro, name, name_norm, zip, "
                "phone, email, street, attrs, first_seen, last_seen) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (entity_key, avenue, metro, name, normalize_name(name), zip, phone,
                 email, street, json.dumps(attrs or {}), today, today),
            )
        else:
            merged = json.loads(row["attrs"] or "{}")
            merged.update(attrs or {})
            # COALESCE keeps existing non-null values when new ones are None
            self.conn.execute(
                "UPDATE entities SET avenue=?, metro=?, name=?, name_norm=?, "
                "zip=COALESCE(?, zip), phone=COALESCE(?, phone), email=COALESCE(?, email), "
                "street=COALESCE(?, street), attrs=?, last_seen=? WHERE entity_key=?",
                (avenue, metro, name, normalize_name(name), zip, phone, email, street,
                 json.dumps(merged), today, entity_key),
            )
        self.conn.commit()

    def get_entity(self, entity_key):
        row = self.conn.execute(
            "SELECT * FROM entities WHERE entity_key=?", (entity_key,)
        ).fetchone()
        return dict(row) if row else None

    def iter_entities(self, avenue=None, metro=None):
        q = "SELECT * FROM entities WHERE 1=1"
        args = []
        if avenue:
            q += " AND avenue=?"
            args.append(avenue)
        if metro:
            q += " AND metro=?"
            args.append(metro)
        return [dict(r) for r in self.conn.execute(q, args).fetchall()]

    # ---------- signals ----------

    def add_signal(self, sig):
        """Insert a Signal (idempotent). Returns True if newly inserted."""
        h = dedup_hash(sig.entity_key, sig.signal_type, sig.signal_date, sig.source_ref)
        try:
            self.conn.execute(
                "INSERT INTO signals (dedup_hash, entity_key, entity_name, metro, avenue, "
                "signal_type, signal_date, magnitude, source_id, source_ref, raw, attrs, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (h, sig.entity_key, sig.entity_name, sig.metro, sig.avenue,
                 sig.signal_type, sig.signal_date, float(sig.magnitude), sig.source_id,
                 sig.source_ref, json.dumps(sig.raw, default=str),
                 json.dumps(sig.attrs, default=str), datetime.now().isoformat(timespec="seconds")),
            )
            self.conn.commit()
            inserted = True
        except sqlite3.IntegrityError:
            inserted = False
        # keep the entities table in sync so resolve/export always have a row
        self.upsert_entity(
            sig.entity_key, sig.avenue, sig.metro, sig.entity_name,
            zip=sig.attrs.get("zip"), phone=sig.attrs.get("phone"),
            email=sig.attrs.get("email"), street=sig.attrs.get("street"),
        )
        return inserted

    def get_signals(self, avenue=None, metro=None, entity_key=None, since=None):
        q = "SELECT * FROM signals WHERE 1=1"
        args = []
        if avenue:
            q += " AND avenue=?"
            args.append(avenue)
        if metro:
            q += " AND metro=?"
            args.append(metro)
        if entity_key:
            q += " AND entity_key=?"
            args.append(entity_key)
        if since:
            q += " AND signal_date>=?"
            args.append(since if isinstance(since, str) else since.isoformat())
        q += " ORDER BY signal_date DESC"
        return [dict(r) for r in self.conn.execute(q, args).fetchall()]

    # ---------- snapshots ----------

    def add_snapshot(self, source_id, snapshot_date, item_key, payload):
        """Idempotent via UNIQUE(source_id, snapshot_date, item_key)."""
        if not isinstance(snapshot_date, str):
            snapshot_date = snapshot_date.isoformat()
        try:
            self.conn.execute(
                "INSERT INTO snapshots (source_id, snapshot_date, item_key, payload, created_at) "
                "VALUES (?,?,?,?,?)",
                (source_id, snapshot_date, item_key, json.dumps(payload, default=str),
                 datetime.now().isoformat(timespec="seconds")),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_snapshots(self, source_id, item_key):
        rows = self.conn.execute(
            "SELECT * FROM snapshots WHERE source_id=? AND item_key=? ORDER BY snapshot_date",
            (source_id, item_key),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["payload"] = json.loads(d["payload"])
            except (TypeError, ValueError):
                pass
            out.append(d)
        return out

    def first_seen(self, source_id, item_key):
        row = self.conn.execute(
            "SELECT MIN(snapshot_date) AS fs FROM snapshots WHERE source_id=? AND item_key=?",
            (source_id, item_key),
        ).fetchone()
        return row["fs"] if row and row["fs"] else None

    # ---------- runs ----------

    def start_run(self, args=None):
        cur = self.conn.execute(
            "INSERT INTO runs (started_at, args, status) VALUES (?,?,?)",
            (datetime.now().isoformat(timespec="seconds"),
             json.dumps(args or {}, default=str), "RUNNING"),
        )
        self.conn.commit()
        return cur.lastrowid

    def finish_run(self, run_id, status="OK", summary=None):
        self.conn.execute(
            "UPDATE runs SET finished_at=?, status=?, summary=? WHERE id=?",
            (datetime.now().isoformat(timespec="seconds"), status,
             json.dumps(summary or {}, default=str), run_id),
        )
        self.conn.commit()

    # ---------- scores ----------

    def save_score(self, run_id, entity_key, avenue, metro, score, hot, signal_types):
        self.conn.execute(
            "INSERT INTO scores (run_id, entity_key, avenue, metro, score, hot, "
            "signal_types, scored_at) VALUES (?,?,?,?,?,?,?,?)",
            (run_id, entity_key, avenue, metro, float(score), 1 if hot else 0,
             json.dumps(list(signal_types)), datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()
