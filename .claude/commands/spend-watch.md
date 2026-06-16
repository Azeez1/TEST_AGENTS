---
description: One API-spend check against the daily budget (designed to be repeated via /loop during campaigns)
arguments:
  - name: budget
    description: Daily budget in USD (default 50)
    required: false
---

# API Spend Watch (single pass)

Run ONE spend check. Designed to be repeated via `/loop 1h /spend-watch` while image/video generation campaigns are running; each invocation is self-contained.

## Process

1. Daily budget = **$ARGUMENTS** (default: $50). If `.claude/hooks/api_cost_gate.ps1` defines a different budget constant, that value wins — read it.
2. Read today's spend: `LOGS/api-spend-<today>.total` if present, plus tail `LOGS/api-spend.log` for today's entries. Sum only TODAY's lines (match today's date stamp).
3. Identify the top 3 cost drivers by tool (e.g. generate_sora_video, generate_gpt4o_image).

## Output rules (keep the loop quiet)

- Under 80% of budget: ONE line, e.g. `Spend $18.40 / $50 (37%) — top: sora $12, gpt4o $4`.
- At or above 80%: WARN prominently with the projected end-of-day total at the current hourly burn rate, and name which running workflow to pause first (highest spender).
- At or above 100%: state plainly that the budget is breached and that the api_cost_gate hook should be blocking further generation calls — if spend is still growing past 100%, flag that the gate may not be firing.
