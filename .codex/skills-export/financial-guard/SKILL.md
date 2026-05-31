---
name: "financial-guard"
description: "Workspace boundary enforcement for FINANCIAL_TEAM operations. Blocks Edit and Write operations outside FINANCIAL_TEAM/ directory. Activate when running financial analysis, deal evaluations, valuations, or any FINANCIAL_TEAM agent task to prevent accidental writes to other teams directories. Works alongside existing workspace_enforcer but provides a hard hook-based gate."
---

# Financial Guard — FINANCIAL_TEAM Boundary Enforcement

## What It Does

Hard gate that prevents any file edits or writes outside the `FINANCIAL_TEAM/` directory. This ensures financial agents (deal-analyst, valuation-agent, portfolio-manager, CFO, etc.) cannot accidentally modify marketing content, engineering code, or other teams' data.

## Why This Exists

The existing `workspace_enforcer` tool provides instruction-based boundary enforcement — agents are told not to write outside their team. But instructions are best-effort. This hook is a **hard gate** that blocks the operation before it executes.

Think of it as defense-in-depth:
- **workspace_enforcer** = soft boundary (instructions)
- **financial-guard** = hard boundary (hook that blocks)

## When to Activate

- Running any FINANCIAL_TEAM agent (deal-analyst, valuation-agent, fpna-agent, etc.)
- Financial analysis sessions with sensitive data
- Deal evaluations where accidental data leaks to other teams would be problematic
- Trading optimization with the trading-optimizer agent

## Which Agents Benefit

All 14 FINANCIAL_TEAM agents:
- deal-analyst, valuation-agent, portfolio-manager, financial-analyst
- forecasting-agent, fpna-agent, accountant, controller
- tax-advisor, treasury-agent, financial-data-analyst
- investor-relations-agent, cfo-agent, trading-optimizer

## Limitations

- Only blocks Edit and Write tools — does not block Bash file operations (use `careful` for that)
- Does not block Read operations — financial agents can still read from other teams (which is sometimes needed for cross-team analysis)
- The path match is substring-based — any path containing "FINANCIAL_TEAM" is allowed
