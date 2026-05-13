# Diagnosis 02 — Lessons 5, 6, 7 (The Structural Upgrade)

**Date:** 2026-05-11
**Lessons:** 05 (Closed Loop), 06 (Reviewer Subagents), 07 (ZTE)
**Status:** ✅ Design understood / ⚠️ Implementation pending

---

## Recall summary (self-explained)

**Closed Loop (5):** Stop hook fires when agent says done → runs validator → if fail, re-invokes agent with the error → loops until pass. Removes the manual retry button.

**Reviewer Subagents (6):** Implementer, reviewer, documenter are separate agents. The agent that writes ≠ the agent that grades ≠ the agent that documents. Self-grading bias is avoided by role separation.

**ZTE (7):** Closed loop + reviewer subagents + scheduling (cron) + triggering + escalation + audit log. Pipeline runs without human involvement; escalates only on failure.

## Corrections / gaps identified

| Gap | Why it matters | Fix |
|---|---|---|
| **No retry budget in closed loop recall** | Infinite loops on impossible failures → cost runaway | Max N attempts → escalate to Telegram |
| **"Sink" terminology vs "sync"** | Two different things — sink = destination, sync = synchronize | Use "sink"; recognize sink = Lesson 2 leverage point #9 (output routing) |
| **Reviewer tool restriction unmentioned** | Without excluding Write/Edit from reviewer, role separation collapses | Reviewer's `tools:` frontmatter must NOT include Write/Edit |

## The compounding chain

```
L5 alone        → self-corrects but biased (no independent reviewer)
L6 alone        → reviewer flags problems, no auto-fix
L7 attempt w/o L5+L6 → pipeline runs on schedule, produces unreviewed garbage
L5 + L6         → self-healing against quality bar, but you trigger it
L5 + L6 + L7    → self-healing pipeline on schedule, escalates only on real failure = ZTE
```

## Vocabulary collapse — senior pattern spotting

Noticed during recall: "sink" (Lesson 7) = "output routing" (Lesson 2 leverage point #9). Same concept, two names.

**Implication:** the 14 lessons are not 14 separate concepts. They are roughly 6 concepts named 14 ways. Build a personal glossary as the manual progresses to compress the mental model.

## Done-when status

| Lesson | Done When | Status |
|---|---|---|
| 5 | PE diagnosis self-heals up to 3 times unattended | ⚠️ Pending implementation |
| 6 | Top-3 pipelines spawn a reviewer with Write/Edit excluded from tools | ⚠️ Pending implementation |
| 7 | Cron pipeline runs 3 Mondays untouched | ⚠️ Pending implementation |

**Design grade:** Solid.
**Implementation grade:** Zero.

## Action items added

- [ ] Upgrade `pe_validation_gate.ps1` from "block + page" to "block + re-invoke up to 3 + page on 4th" (Lesson 5 implementation)
- [ ] Build `pe-diagnosis-visual-reviewer` subagent with `tools:` excluding Write/Edit (Lesson 6 implementation, from Diagnosis 01)
- [ ] Build `linkedin-brand-reviewer` subagent with `tools:` excluding Write/Edit (Lesson 6 implementation)
- [ ] Schedule first cron-triggered ZTE pipeline: `lead-gen-cleaning` weekly (Lesson 7 implementation)
- [ ] Maintain `LEARNING/glossary.md` for vocabulary collapse as more lessons surface duplicate concepts

## Strategic decision pending

Continue-conceptual (Lessons 8-14 next) vs pause-and-build (ship one closed loop + one reviewer + one cron now). Tradeoff: momentum vs proof. Decision deferred to next turn.
