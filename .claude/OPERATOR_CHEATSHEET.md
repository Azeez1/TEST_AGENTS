# Operator Cheat Sheet — TEST_AGENTS

**Last updated:** 2026-05-12
**Purpose:** One-page reference for daily operation. Don't memorize the system — glance at this when you need it.

---

## What runs automatically (you don't trigger these)

| Hook event | Script | What it does |
|---|---|---|
| PreToolUse on Bash | `pe_validation_gate.ps1` | Blocks PE diagnosis uploads unless validated. Closed-loop: retries 3× with hints, then escalates. |
| PreToolUse on Write/Edit | `output_routing_gate.ps1` | Inspects output paths. WARN-only today (logs violations, doesn't block). |
| Stop (any agent finishes) | `log_agent_run.ps1` | Appends one JSONL line per run to `LOGS/agent-runs.jsonl`. |

---

## Reviewers you can invoke via the Task tool

| Agent name | Use case | Tools |
|---|---|---|
| `pe-diagnosis-visual-reviewer` | Score a new PE diagnosis against past canonical ones | Read-only |
| `linkedin-brand-reviewer` | Check a LinkedIn draft against brand voice rules | Read-only |
| `pe-diagnosis-validator` | Run 7-rule structural validation, write `.validation_pass` | Read + Write |

**Invocation pattern:** "Use [agent-name] to review [path]"

---

## Three files to glance at weekly (5 min total)

```
LOGS/agent-runs.jsonl          # Agent activity & cost — empty until first run lands
LOGS/routing-violations.log    # Output routing health — empty = healthy
LOGS/escalations.log           # PE failures past retry budget — empty = self-healing worked
```

**If all three are empty/healthy → the system is working. Trust it.**

---

## Quick commands

```bash
# Cost & failure summary for the past 7 days
python tools/agent_log_query.py --this-week

# Drill into one agent's activity
python tools/agent_log_query.py --agent pe-diagnosis-validator

# Cost breakdown across all agents
python tools/agent_log_query.py --cost-summary
```

---

## When something feels off

1. **Hook prints WARN to stderr?** → It's logging the violation but letting the write through. Check `LOGS/routing-violations.log`.
2. **PE diagnosis fails repeatedly?** → Check `LOGS/escalations.log` for the specific failure reason after 3 retries.
3. **Reference something archived?** → Grep `~/.claude/projects/.../memory/MEMORY-archive.md` for the topic.
4. **Unsure where new memory belongs?** → Read `MEMORY_ROUTING.md` (5-question decision matrix).
5. **Want to roll back today's memory swap?** → Rename `MEMORY.md.OLD` back to `MEMORY.md`.

---

## When to revisit deferred work

| When this happens | Then do this |
|---|---|
| `routing-violations.log` stays clean for 7 days | Flip `$ENFORCE_MODE = $true` in `output_routing_gate.ps1` |
| You want routing applied to other teams | Extend the team list in `output_routing_gate.ps1` |
| It's been ~30 days | Build the memory routing audit script (Phase 2 of MEMORY_ROUTING.md) |
| Closed-loop + reviewers have a few weeks of data | Start the Lesson 14 capstone — PE Outreach ZTE pipeline |

---

## Key locations (memorize ONLY these paths)

```
.claude/agents/           # Subagent definitions
.claude/hooks/            # Hook scripts
.claude/settings.local.json   # Hook wiring (NOT committed)
LOGS/                     # All operational logs (gitignored)
tools/                    # Utility scripts
MEMORY_ROUTING.md         # Memory placement governance
~/.claude/projects/.../memory/   # User-level memory
```

---

## Hook authoring rules

- **Always use absolute paths** in `.claude/settings.local.json` hook commands. Relative paths fail under different cwds. See [ADR-0001](../docs/adr/ADR-0001-hooks-use-absolute-paths.md).
- **Hook scripts must be ASCII-only or UTF-8 with BOM.** PowerShell on Windows defaults to CP1252 and chokes on em-dashes (`-` not `—`), box-drawing chars, smart quotes. See [ADR-0002](../docs/adr/ADR-0002-hook-scripts-ascii-or-utf8-bom.md). Run `python tools/verify_system.py` to check.
- Hooks must **fail open** — wrap logic in try/catch and exit 0 on internal errors. A broken hook should never block real work.
- New hooks register via PreToolUse / PostToolUse / Stop / SubagentStop matchers. Match on tool name or regex (`Write|Edit|MultiEdit`).
- Each new hook should have a corresponding **log destination in `LOGS/`** (gitignored) so its activity is observable.

## How to add a new architectural decision

When you make a non-obvious decision worth capturing:

1. Open `docs/adr/README.md` — find the highest ADR number, add 1
2. Create `docs/adr/ADR-NNNN-kebab-case-title.md`
3. Use the 5-section template: Status · Context · Decision · Alternatives Considered · Consequences
4. Add a row to the index table in `docs/adr/README.md`
5. Commit both files together

The `output_routing_gate.ps1` hook enforces the naming pattern. ADRs are immutable once accepted — supersede via a new ADR rather than editing.

---

**Operator principle:** You don't remember the system. The system surfaces what needs attention. Your only job is the weekly glance.
