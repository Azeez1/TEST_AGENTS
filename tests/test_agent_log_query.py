"""Recovered run history must be visible without inflating agent totals."""

from datetime import datetime, timezone
import json
import sys

from tools import agent_log_query


def _write_rows(path, rows):
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_default_history_recovers_unique_rows_and_filters(tmp_path, monkeypatch):
    canonical = tmp_path / "agent-runs.jsonl"
    recovered = tmp_path / "recovered-agent-runs.jsonl"
    old = {"ts": "2026-06-01T10:00:00Z", "agent": "writer", "cost_usd": 1.0}
    current = {"ts": "2026-09-24T12:00:00Z", "agent": "reviewer", "cost_usd": 2.0}
    missing = {"ts": "2026-09-23T12:00:00Z", "agent": "reviewer", "cost_usd": 3.0}
    _write_rows(canonical, [old, current])
    _write_rows(recovered, [dict(reversed(list(current.items()))), missing])
    monkeypatch.setattr(agent_log_query, "LOG_PATH", canonical)
    monkeypatch.setattr(agent_log_query, "RECOVERED_LOG_PATH", recovered)

    rows = agent_log_query.load_default()
    assert len(rows) == 3
    assert sum(row["cost_usd"] for row in rows) == 6.0

    recent = agent_log_query.load_default(
        since=datetime(2026, 9, 1, tzinfo=timezone.utc), agent="reviewer"
    )
    assert {row["ts"] for row in recent} == {
        "2026-09-23T12:00:00Z", "2026-09-24T12:00:00Z"
    }


def test_path_override_reads_only_requested_log(tmp_path, monkeypatch, capsys):
    custom = tmp_path / "custom.jsonl"
    _write_rows(custom, [{"ts": "2026-09-24T12:00:00Z", "agent": "custom", "cost_usd": 4.0}])
    monkeypatch.setattr(sys, "argv", ["agent_log_query.py", "--path", str(custom)])

    agent_log_query.main()

    output = capsys.readouterr().out
    assert "custom" in output
    assert "across 1 runs" in output
