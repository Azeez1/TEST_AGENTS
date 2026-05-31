---
name: "capture-as-skill"
description: "After a successful complex task, reflects on the pattern that worked and proposes a new skill capturing it for future reuse. Use this skill when the user says \"save this as a skill,\" \"capture this pattern,\" \"make this reusable,\" \"let's bottle this up,\" or after any multi-step workflow that the user is likely to repeat. Returns a draft SKILL.md proposal for user approval rather than auto-writing."
---

# Capture-as-Skill (Act-Learn-Reuse)

You are operating as the Capture-as-Skill meta-skill. Your job: look at a recently-completed successful workflow and **extract its reusable pattern as a new Claude Code skill proposal**.

This is the **Learn** phase of the Act-Learn-Reuse loop (Lesson 13). The user just did something well; you turn that into a skill so the agent fleet doesn't have to re-discover the pattern next time.

## When to fire

Trigger when:
- User says "save this as a skill," "capture this pattern," "make this reusable," "bottle this up"
- A multi-step workflow just completed successfully and the user marks it as worth keeping
- The conversation history shows a workflow that succeeded after iteration — even if user didn't explicitly ask, suggest capture proactively

## Process — 5 phases

### Phase 1 — Reflect

Read back through the recent conversation. Identify:

1. **What was the workflow?** (one sentence)
2. **Why did it succeed?** What sequence of steps worked? What clarifying questions were asked? What checks happened?
3. **What was the deliverable?** What artifact was produced?
4. **What near-failures were avoided?** Did the user correct course mid-way? Note the corrections — those become guardrails in the skill.

Output a 1-paragraph reflection. Show it to the user.

### Phase 2 — Pattern extraction

From the reflection, identify the **reusable pattern**:

- What's the trigger (when should this skill fire)?
- What inputs does it take?
- What's the sequence of steps?
- What decision points exist?
- What's the success criteria?
- What edge cases came up?

If the workflow was too unique to repeat → tell the user "this looks like a one-off, not a pattern. Don't recommend capturing it as a skill." Stop here.

If a real pattern exists → continue.

### Phase 3 — Draft the SKILL.md proposal

Produce a complete SKILL.md body in the standard format:

```markdown
---
name: <kebab-case-name>
description: <one-sentence trigger>
---

# <Skill Title>

## Role
## Task
## Inputs
## Outputs
## Process
## Guardrails
## Examples
## When NOT to use
```

Save the draft to `.claude/skills/<proposed-name>/SKILL.md.proposed` (note the `.proposed` suffix — do NOT save directly to SKILL.md yet).

### Phase 4 — Present for approval

Tell the user:

> "I've drafted a new skill at `.claude/skills/<name>/SKILL.md.proposed`. Review and approve to make it live, or push back on the framing / scope / examples."

Show a 3-bullet summary of what the skill captures so the user can decide without reading the full file.

### Phase 5 — Promote on approval (or iterate)

If user approves → rename `.proposed` → `SKILL.md` (this is the activation).
If user pushes back → iterate on Phase 3 with their corrections.

## Hard rules

- **Never auto-write the final SKILL.md.** Always go through `.proposed` first.
- **Never capture as a skill if the workflow was actually a one-off.** Tell the user instead.
- **The skill description must be specific enough to trigger correctly.** Bad: "helps with marketing." Good: "drafts a LinkedIn post about a specific topic with brand-voice-compliant tone." If you can't write a specific trigger, the pattern isn't ready.
- **Capture the WHY in the skill body, not just the WHAT.** Future Claude reading the skill should understand why each step exists.
- **Reference the source conversation** in the proposal — "Captured from workflow run on YYYY-MM-DD." Provenance helps when the skill needs updating later.

## What makes a good skill candidate

| ✅ Good candidate | ❌ Not a good candidate |
|---|---|
| Multi-step workflow with consistent shape | One-off creative task |
| Repeated 2+ times already OR likely to repeat | Unique problem unlikely to recur |
| Has clear inputs and outputs | Vague intent, no defined outputs |
| Required iteration to get right | Worked first try (probably too simple to need a skill) |
| Brand-voice or quality rules matter | Pure information lookup (use grep instead) |

## Relationship to other skills

- **`skill-builder`** — interview-driven *upfront* design. Use that when designing a new skill from scratch with no prior workflow.
- **`skill-creator`** — passive reference doc for SKILL.md format.
- **THIS skill (`capture-as-skill`)** — *retrospective* capture of a workflow that already happened.

The three form the skill-authoring stack: design (`skill-builder`) | capture (`capture-as-skill`) | reference (`skill-creator`).

## Output format

After Phase 5 completes, return:

```
CAPTURE COMPLETE
================

Skill: <name>
Location: .claude/skills/<name>/SKILL.md
Captured from: <source conversation date>
Status: Live / Awaiting approval / Declined

Summary: <3-bullet recap of what this skill does>

To use: <how the user should invoke it next time>
```
