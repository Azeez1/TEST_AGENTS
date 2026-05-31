"""claude_p_summary.py - analyze LOGS/claude-p-runs.jsonl

Estimates programmatic Claude spend based on invocations logged by
tools/claude_p_logged.ps1. Useful for sizing whether Anthropic's June 15 2026
dedicated programmatic credit (~$200/month rumored) will cover your actual
usage volume.

Usage:
    python tools/claude_p_summary.py             # all-time summary
    python tools/claude_p_summary.py --week      # last 7 days
    python tools/claude_p_summary.py --month     # last 30 days
    python tools/claude_p_summary.py --by-day    # daily breakdown
    python tools/claude_p_summary.py --by-caller # group by caller script

Token / cost estimates use these rates (per million tokens):
    sonnet 4.6 / default :  $3 input, $15 output
    opus 4.7              : $15 input, $75 output
    haiku 4.5             : $1 input,  $5 output
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "LOGS" / "claude-p-runs.jsonl"

# Pricing per million tokens (USD)
PRICES = {
    "claude-opus-4-7":   {"in": 15.0, "out": 75.0},
    "claude-sonnet-4-6": {"in":  3.0, "out": 15.0},
    "claude-haiku-4-5":  {"in":  1.0, "out":  5.0},
    "default":           {"in":  3.0, "out": 15.0},  # assume Sonnet
}


def load_log(since=None):
    if not LOG_PATH.exists():
        return []
    rows = []
    # utf-8-sig strips the BOM that PowerShell's Add-Content -Encoding utf8 prepends
    with open(LOG_PATH, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if since:
                try:
                    ts = datetime.fromisoformat(row["ts"].replace("Z", "+00:00"))
                except (KeyError, ValueError):
                    continue
                if ts < since:
                    continue
            rows.append(row)
    return rows


def estimate_cost(row):
    model = row.get("model", "default")
    price = PRICES.get(model, PRICES["default"])
    in_tok = row.get("approx_input_tokens", 0)
    out_tok = row.get("approx_output_tokens", 0)
    in_cost = (in_tok / 1_000_000.0) * price["in"]
    out_cost = (out_tok / 1_000_000.0) * price["out"]
    return in_cost + out_cost


def summarize(rows, label):
    if not rows:
        print(f"\n{label}: no entries\n")
        return

    total_calls = len(rows)
    total_input = sum(r.get("approx_input_tokens", 0) for r in rows)
    total_output = sum(r.get("approx_output_tokens", 0) for r in rows)
    total_cost = sum(estimate_cost(r) for r in rows)
    total_duration_ms = sum(r.get("duration_ms", 0) for r in rows)
    failures = sum(1 for r in rows if r.get("exit_code", 0) != 0)

    # By-model
    by_model = defaultdict(lambda: {"calls": 0, "cost": 0.0})
    for r in rows:
        m = r.get("model", "default")
        by_model[m]["calls"] += 1
        by_model[m]["cost"] += estimate_cost(r)

    print(f"\n{label}")
    print("=" * len(label))
    print(f"  Total calls:        {total_calls}")
    print(f"  Total input tokens: {total_input:,}")
    print(f"  Total output tokens:{total_output:,}")
    print(f"  Total est. cost:    ${total_cost:.2f}")
    print(f"  Total duration:     {total_duration_ms/1000:.1f}s")
    print(f"  Failures:           {failures} ({100*failures/total_calls:.1f}%)")
    print(f"  Avg cost / call:    ${total_cost/total_calls:.4f}")

    if len(by_model) > 1:
        print("\n  By model:")
        for m, stats in sorted(by_model.items()):
            print(f"    {m:25s} {stats['calls']:>4} calls  ${stats['cost']:>7.2f}")

    # Annualize
    if "month" in label.lower() or "30 day" in label.lower():
        print(f"\n  Annualized run rate: ${total_cost * 12:.2f}/year")
        print(f"  Vs $200/mo credit:   {'WITHIN' if total_cost <= 200 else 'OVER'} budget ({total_cost/200*100:.1f}% of credit)")
    elif "week" in label.lower() or "7 day" in label.lower():
        monthly_proj = total_cost * 4.33
        print(f"\n  Monthly projection (x 4.33): ${monthly_proj:.2f}/mo")
        print(f"  Vs $200/mo credit:           {'WITHIN' if monthly_proj <= 200 else 'OVER'} budget ({monthly_proj/200*100:.1f}% of credit)")


def by_day(rows):
    by = defaultdict(lambda: {"calls": 0, "cost": 0.0})
    for r in rows:
        ts = r.get("ts", "")[:10]
        if ts:
            by[ts]["calls"] += 1
            by[ts]["cost"] += estimate_cost(r)
    print("\nDay         Calls   Cost")
    print("-" * 30)
    for day in sorted(by):
        print(f"{day}  {by[day]['calls']:>4}    ${by[day]['cost']:>6.3f}")


def by_caller(rows):
    by = defaultdict(lambda: {"calls": 0, "cost": 0.0})
    for r in rows:
        c = r.get("caller", "") or "(unknown)"
        by[c]["calls"] += 1
        by[c]["cost"] += estimate_cost(r)
    print("\nCaller                          Calls   Cost")
    print("-" * 50)
    for caller in sorted(by, key=lambda k: -by[k]["cost"]):
        print(f"{caller:30s}  {by[caller]['calls']:>4}    ${by[caller]['cost']:>6.3f}")


def main():
    parser = argparse.ArgumentParser(description="Summarize claude -p usage log.")
    parser.add_argument("--week", action="store_true", help="last 7 days only")
    parser.add_argument("--month", action="store_true", help="last 30 days only")
    parser.add_argument("--by-day", action="store_true", help="day-by-day breakdown")
    parser.add_argument("--by-caller", action="store_true", help="group by caller script")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    if args.week:
        since = now - timedelta(days=7)
        rows = load_log(since)
        summarize(rows, f"Last 7 days (since {since.strftime('%Y-%m-%d')})")
    elif args.month:
        since = now - timedelta(days=30)
        rows = load_log(since)
        summarize(rows, f"Last 30 days (since {since.strftime('%Y-%m-%d')})")
    else:
        rows = load_log()
        summarize(rows, "All-time")

    if args.by_day and rows:
        by_day(rows)
    if args.by_caller and rows:
        by_caller(rows)

    if not rows:
        print("\nLog is empty. Run a few `claude -p` invocations through")
        print("tools\\claude_p_logged.ps1 to start populating data.")


if __name__ == "__main__":
    main()
