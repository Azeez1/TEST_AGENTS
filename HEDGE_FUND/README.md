# HEDGE_FUND — ICT Trading Agent

Single-agent trading desk built around the user's ICT (Inner Circle Trader) methodology.
Lives at the repo root as a sibling to MARKETING_TEAM, FINANCIAL_TEAM, etc.

## What this team does

- Reads charts and identifies setups using ICT concepts: FVG, Order Blocks, MMXM, BPR, liquidity sweeps, killzones, OTE.
- Produces structured trade setups with HTF bias, LTF entry, stop, target, and confluence notes.
- Alerts (does NOT execute) on actionable setups in user-selected instruments.
- Maintains a trade journal in `outputs/journal/` for later review/backtesting.

## What this team does NOT do (yet)

- **Does not place live orders.** v1 is analyze-and-alert only. Live execution requires a broker MCP + the human-approval gate in `memory/risk_rules.json`.
- **Does not replace `FINANCIAL_TEAM/trading-optimizer`** — that one handles portfolio-level position sizing across a strategy. `ict-trader` is the signal-generation side.

## File map

```
HEDGE_FUND/
├── README.md                              # This file
├── .claude/
│   ├── settings.json                      # Workspace + skill enablement
│   └── agents/
│       └── ict-trader.md                  # The agent definition
├── memory/                                # Read at task start
│   ├── ict_playbook.json                  # All ICT concepts (FVG, OB, MMXM, etc.)
│   ├── markets_config.json                # Instruments + sessions + killzones
│   ├── risk_rules.json                    # Per-trade %, DD limits, Money Rule
│   ├── tradingview_config.json            # TV MCP slot + Chrome fallback
│   └── llar_memory.json                   # Preferences, traits, strategies
├── outputs/                               # Gitignored deliverables
│   ├── setups/                            # One .md per identified setup
│   ├── journal/                           # Trade journal (closed + open)
│   ├── screenshots/                       # TV chart captures
│   └── backtests/                         # Historical replays
├── tools/                                 # (empty for v1 — custom Python lives here later)
└── tests/                                 # (empty for v1)
```

## ICT concepts covered (see `memory/ict_playbook.json` for rules)

| Category | Concepts |
|----------|----------|
| **HTF bias** | PD arrays, Premium/Discount, weekly profile, daily bias, DXY correlation |
| **Liquidity** | BSL, SSL, equal highs/lows, trendline liquidity, session liquidity, sweeps/runs |
| **Imbalances** | FVG, Inverted FVG (IFVG), BPR (Balanced Price Range), Volume Imbalance, Liquidity Void |
| **Order blocks** | Bullish/Bearish OB, Breaker Block, Mitigation Block, Propulsion Block |
| **Market structure** | BOS, MSS, CHoCH, internal vs swing |
| **Market maker models** | MMBM, MMSM (6-phase), Power of 3 (AMD), Judas Swing |
| **Time** | Killzones (London Open, NY AM/PM, Asia), Silver Bullet, macros |
| **Entries** | OTE (62/70.5/79 fib), breaker entry, FVG mitigation, OB mitigation, turtle soup |
| **Confluence** | SMT divergence, DXY, daily/weekly opens, session opens |

## Markets

FX majors/minors, indices (NQ/ES/YM/RTY), equities/options (SPY/QQQ/top movers), crypto (BTC/ETH/SOL).
Per-market session conventions live in `memory/markets_config.json`.

## TradingView integration

Two paths, agent auto-selects based on `memory/tradingview_config.json`:

1. **`tradesdontlie/tradingview-mcp`** (preferred — `READY_TO_INSTALL`). Drives **TradingView Desktop** locally via Chrome DevTools Protocol on port 9222. Capabilities: chart navigation, indicator reads, drawings, alerts, **Pine Script inject/compile** (so the agent can author FVG/OB detector scripts), replay (walk-forward backtest substitute), multi-pane layouts, screenshots. Requires paid TV Desktop + Node 18 + launching TV with `--remote-debugging-port=9222`. Install instructions live in `memory/tradingview_config.json.tradingview_mcp_slot.install_steps`.

2. **Chrome MCP fallback** (works today, no install). Drives logged-in TradingView Web via `mcp__claude-in-chrome__*`. Reads charts via screenshot + page text. Less powerful than Path 1 (no Pine, no drawings, no alerts), but zero setup.

Pine alerts → n8n webhook for execution automation is planned for v2.

## Invocation

```
"Use ict-trader to scan NQ for bullish FVGs in NY AM killzone"
"Use ict-trader to give me HTF bias on EURUSD for this week"
"Use ict-trader to journal the BTCUSD trade I just closed: entry 67200 stop 66900 exit 67800"
```

## Status

**v1 foundation** — 2026-05-25. Analyze-and-alert only. No live execution. No backtesting engine yet.
