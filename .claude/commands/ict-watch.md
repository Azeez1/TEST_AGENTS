---
description: One ICT scan pass on a symbol in the current killzone (designed to be repeated via /loop)
arguments:
  - name: symbol
    description: Instrument to scan (default NAS100 = OANDA:NAS100USD, EZ's primary chart)
    required: false
---

# ICT Killzone Watch (single pass)

Run ONE scan pass on **$ARGUMENTS** (default: `OANDA:NAS100USD`, the primary chart in `HEDGE_FUND/memory/user_chart_setup.json`). This command is designed to be repeated via `/loop 2h /ict-watch` during active sessions; each invocation is self-contained.

## Process

1. Determine the current killzone from the current Eastern time using `HEDGE_FUND/memory/ict_playbook.json` (killzone definitions live there). If we are OUTSIDE all killzones, output one line: `Outside killzones (next: <name> at <time ET>)` and STOP.
2. Use **ict-trader** to scan $ARGUMENTS in the current killzone, walking EZ's full timeframe cascade from `markets_config.json` `user_timeframe_cascade`: **W → D → 240 → 60 → 15 → 5**, in that order, never skipping. Weekly is read once per session (first loop pass); every subsequent pass walks the minimum-for-emission set D → 240 → 60 → 15 → 5 top-down.
3. The chart's indicators ARE the eyes (per `user_chart_setup.json`): read LuxAlgo ICT Concepts / SMC / Order Blocks and Nephew_Sam FVG boxes via the data_get_pine_* tools with study_filter set — do not re-detect what they already draw.
4. ict-trader reads its own configs (ict_playbook.json, markets_config.json, user_chart_setup.json, risk_rules.json, tradingview_config.json) per its Configuration Files section.
5. After the scan, restore the chart to NAS100USD 5m (the user_chart_setup default) if the symbol or timeframe was changed.

## Output rules (keep the loop quiet)

- Setup scoring **7+/10**: report it loudly — symbol, direction, entry zone, invalidation, R:R, score, and journal it to `HEDGE_FUND/outputs/journal/`.
- Score below 7 or nothing forming: ONE line only, e.g. `NQ NY-AM: no qualifying setup (best 5/10 bearish FVG, untested)`.
- Analyze and alert ONLY. v1 places no orders. The Money Rule applies: any order needs explicit human approval.
