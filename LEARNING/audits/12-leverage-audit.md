# Audit 01 — The 12 Leverage Points

**Date:** 2026-05-11
**Lesson:** 02 — The 12 Leverage Points
**Status:** ✅ Passed

---

## Self-score vs. ground truth

| # | Leverage Point | Self-score | Reviewer grade | Final |
|---|---|---|---|---|
| 1 | CLAUDE.md files | USED | Agreed | ✅ USED |
| 2 | Agent definition YAML | USED | Agreed | ✅ USED |
| 3 | Slash commands | USED | Agreed | ✅ USED |
| 4 | Skills | USED | Agreed | ✅ USED |
| 5 | Subagents | USED | Push: defined ≠ deployed | ⚠️ PARTIAL |
| 6 | MCP servers | USED | Agreed | ✅ USED |
| 7 | Hooks | PARTIAL | Agreed | ⚠️ PARTIAL |
| 8 | Tool permissions | PARTIAL | Agreed | ⚠️ PARTIAL |
| 9 | Output routing | UNUSED | Push: convention exists, enforcement missing | ⚠️ PARTIAL |
| 10 | Type systems / schemas | UNUSED | Agreed | ❌ UNUSED |
| 11 | Tests / validators | PARTIAL | Agreed | ⚠️ PARTIAL |
| 12 | Stdout / logs | UNUSED | Push: logs exist, not structured | ⚠️ PARTIAL |

---

## Cluster diagnosis

| Cluster | Strength | Implication |
|---|---|---|
| A — Knowledge Layer (1, 2) | STRONG | Agents know what to do |
| B — Invocation Layer (3, 4) | STRONG | I can call work easily |
| C — Delegation Layer (5) | WEAK | I define subagents but rarely dispatch them |
| D — Capability Layer (6, 8) | STRONG-ISH | Capability is broad; permissions lack deny rules |
| E — Enforcement Layer (7, 9) | WEAK | Rules exist as prose, not as gates |
| F — Quality Layer (10, 11, 12) | WEAK | Output is faith-based; no schemas, one validator, no structured logs |

**Diagnosis:** Knowledge-layer-heavy, enforcement-and-quality-layer-light system.
Capability grew faster than controls.
The next 6 months of work is closing Clusters C, E, F — not adding more A/B/D.

---

## Prioritized fix list (dependency-ordered)

| Rank | Add | Cluster | Lesson |
|---|---|---|---|
| 1 | Second hook — a real PreToolUse, not just a Stop validator | E | 2, 5 |
| 2 | Routing enforcement hook | E | 2 |
| 3 | Second validator — visual reviewer for PE diagnoses | F | 6 |
| 4 | One JSON schema for lead-gen records | F | new |
| 5 | Structured stdout for one pipeline (lead-gen) | F | 8 prep |
| 6 | Subagent invocations in 3 existing pipelines (Task tool, not just definitions) | C | 6 |
| 7 | Deny rules in settings.json for dangerous bash (rm, drop, force-push) | D | 2 |
| 8 | Per-agent JSONL log (one line per invocation) | F | 8 |

---

## Key insights surfaced during the audit

1. **Subagents are defined but not dispatched.** 64 agent files exist; very few workflows actually spawn subagents via Task. Definitions are capability, invocations are usage.
2. **Output routing has a map but no border patrol.** Convention is documented; nothing enforces it. One hook fixes this universally.
3. **Validators have a scope problem, not just a count problem.** Adding more validators isn't enough — each one must match the failure mode it's checking against. (Per Diagnosis 01.)
4. **What's not on the fix list:** more agents, more skills, more MCPs. Capability is no longer the bottleneck. *Controls* are.

---

## Drill-down — Cluster C (Delegation) verified state

Ground truth check via grep on `tools:` frontmatter:

| Total agents | Agents with `Task` in tools | % capable of orchestrating |
|---|---|---|
| 65 | 2 (`supervisor`, `test-orchestrator`) | 3% |

**Implication:** 63 of 65 agents are leaves — they cannot autonomously spawn or delegate to other agents. The remaining orchestration happens via:
- **Main-session orchestration:** I (user, in chat) call Task multiple times sequentially. Linear by default.
- **Future-tense narration:** an agent writes "I'll now hand this off to X" — this is NOT delegation, this is narration. No Task call fires.
- **Tool / skill / MCP use:** the agent uses a capability itself. That's tool use, not delegation.

**Agents misleadingly named as orchestrators** (have orchestrator-suggesting names, do NOT have Task tool):
- `router-agent` (MARKETING)
- `cto` (ENGINEERING)
- `cfo-agent` (FINANCIAL)
- `sales-manager` (SALES)
- `rfp-agent` (PROPOSAL)

These cannot orchestrate today. They can only describe what should happen.

## Parallelism unlock — separate from orchestrator promotion

Even with the current 2-orchestrator state, **parallelism is available from the main session** by batching Task calls in one assistant turn. Independent subtasks run concurrently. Most current workflows do not exploit this — they call Task sequentially across multiple turns.

**Rule:** Linear is the default, not the limit. Parallel is unlocked by batching.

## Updated action items

- [ ] Build PreToolUse hook for path enforcement (Bucket: cleanup + Lesson 2 + Lesson 5)
- [ ] Build pe-diagnosis-visual-reviewer subagent (from Diagnosis 01)
- [ ] Draft schemas/leads.schema.json
- [ ] Add deny rules to .claude/settings.json
- [ ] **Promote 5-7 agents to real orchestrators** (add Task to tools + name subagents in prompt): router-agent, cto, cfo-agent, sales-manager, rfp-agent
- [ ] **Train orchestrator prompts to batch Task calls** for independent subtasks (parallelism is a prompt skill, not just a tool capability)
