#!/usr/bin/env python3
"""Aggregate agent-run JSONL logs.

Each line is expected to look like:
  {"ts": "2026-05-12T14:03:11Z", "agent": "rfp-agent", "status": "ok",
   "duration_ms": 12450, "cost_usd": 0.0421, "session_id": "...", "model": "..."}

Missing fields are tolerated. Lines that fail to parse are skipped.
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "LOGS" / "agent-runs.jsonl"


def load(path: Path, since: datetime | None = None, agent: str | None = None):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if agent and r.get("agent") != agent:
            continue
        if since:
            ts = r.get("ts", "")
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                continue
            if dt < since:
                continue
        rows.append(r)
    return rows


def summarize(rows):
    by_agent_cost = defaultdict(float)
    by_agent_count = defaultdict(int)
    by_agent_fail = defaultdict(int)
    by_agent_ms = defaultdict(list)
    for r in rows:
        a = r.get("agent", "unknown")
        by_agent_count[a] += 1
        by_agent_cost[a] += float(r.get("cost_usd", 0) or 0)
        if r.get("status") not in ("ok", "success", "completed", None):
            by_agent_fail[a] += 1
        if "duration_ms" in r:
            by_agent_ms[a].append(int(r["duration_ms"]))
    print(f"{'agent':<28}{'runs':>6}{'fail%':>8}{'cost$':>10}{'p50_ms':>10}{'p95_ms':>10}")
    print("-" * 72)
    for a in sorted(by_agent_count, key=lambda x: -by_agent_cost[x]):
        n = by_agent_count[a]
        f = by_agent_fail[a] / n * 100 if n else 0
        ms = sorted(by_agent_ms[a])
        p50 = ms[len(ms) // 2] if ms else 0
        p95 = ms[int(len(ms) * 0.95)] if ms else 0
        print(f"{a:<28}{n:>6}{f:>7.1f}%{by_agent_cost[a]:>10.4f}{p50:>10}{p95:>10}")
    print(f"\nTOTAL cost: ${sum(by_agent_cost.values()):.4f} across {sum(by_agent_count.values())} runs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--this-week", action="store_true", help="Only last 7 days")
    ap.add_argument("--agent", help="Filter to a single agent name")
    ap.add_argument("--cost-summary", action="store_true", help="Print summary (default)")
    ap.add_argument("--path", default=str(LOG_PATH), help="Override JSONL path")
    args = ap.parse_args()

    since = datetime.now(timezone.utc) - timedelta(days=7) if args.this_week else None
    rows = load(Path(args.path), since=since, agent=args.agent)
    if not rows:
        print("No matching rows.", file=sys.stderr)
        return
    summarize(rows)


if __name__ == "__main__":
    main()
