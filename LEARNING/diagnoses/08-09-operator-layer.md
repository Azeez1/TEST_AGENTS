# Diagnosis 03 — Lessons 8 & 9 (The Operator Layer)

**Date:** 2026-05-11
**Lessons:** 08 (Agentic Layer / Observability), 09 (Context Engineering / R&D)
**Status:** ✅ Design understood / ⚠️ Implementation pending

---

## Recap

**Agentic Layer (8):** Once you have many agents, you have a distributed system. Distributed systems need infrastructure: structured logs, trace IDs, cost tracking, failure rates, fallback policies. **Lesson 8 = the operator mindset on top of the engineer mindset.**

**Context Engineering (9):** Retrieve + Discard. Big context costs money, slows down, and makes the model dumber. Discipline: aggressive pruning, ephemeral working files, fresh-context subagents, lazy loading of tools and memory.

## Repo state — both clusters are mostly unbuilt

### Lesson 8 (Observability)
- Logs: scattered, no canonical JSONL ❌
- Trace IDs: none ❌
- Cost tracking per agent: none ❌
- Failure rate per agent: none ❌
- Fallback policies: partial (video model chain only) ⚠️

**Implication:** You're operating 65 agents blind. Cannot answer "which agent costs me most this week?" today.

### Lesson 9 (Context engineering)
- 4 of 12 techniques in active use
- Biggest gaps: tmp_* files at root, MCP not filtered per task, MEMORY.md bloated
- MEMORY.md currently ~10KB+; target is <4KB

## The two compound — L9 ⊂ L8

Context engineering is one specific concern within the broader agentic layer. You can't run cost-aware infrastructure (L8) without context discipline (L9). Doing both together = observe the cost AND have the lever to reduce it.

## Highest-ROI single moves identified

| Lesson | Move | Why it's highest-ROI |
|---|---|---|
| 8 | One JSONL line per agent invocation → `LOGS/agent-runs.jsonl` | From zero observability to full observability in one file |
| 9 | Archive MEMORY.md down to load-bearing entries (target <4KB) | Every future Claude session faster, cheaper, sharper |

## Action items added

- [ ] Build minimal agentic layer log: JSONL writer hook on agent invocations
- [ ] Build 50-line Python query script: "which agent costs most this week?"
- [ ] Curate MEMORY.md → archive stale entries to MEMORY-archive.md (target: cut 60%)
- [ ] Audit tmp_* directories at repo root (cleanup Bucket 1 from earlier)
- [ ] Audit MCP loading — filter per task if possible
- [ ] Add fallback policies to critical pipelines (PE diagnosis, lead-gen)

## Strategic state — end of conceptual sweep prep

Conceptual sweep status:
- ✅ Lessons 1-9 design-understood (9 of 14)
- 5 lessons remain (10-14)
- Implementation pending across L5-L9 done-when criteria

**Plan as stated by user:** finish conceptual sweep through L14, then enter implementation mode with full context. Implementation will draw from all artifacts in `LEARNING/diagnoses/` + `LEARNING/audits/`.

## Resume point for next session

Pick up at Lesson 10 — The 7 Prompt Levels. Then 11 (Domain agents), 12 (Multi-agent orchestration), 13 (Skills as learned behavior), 14 (Capstone — Codebase Singularity).

After L14, pivot to implementation phase. Reference all `LEARNING/` artifacts as the spec.
