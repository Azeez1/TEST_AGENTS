# Diagnosis 01 — Core Four Applied

**Date:** 2026-05-11
**Lesson:** 01 — The Core Four
**Status:** ✅ Passed

---

## The failure

**What I asked:** Generate a PE diagnosis matching the formatting of past diagnoses.

**What came back:** A valid PDF, but the formatting was wrong — didn't match the canonical look of prior diagnoses in `outputs/diagnoses/`.

**Why it was wrong:** Two levers misfiring at the same time.

---

## Lever 1 — Context (under-specified)

The model had loaded *some* context about past diagnoses but the relevant formatting patterns were buried under newer tokens in the session. Context wasn't missing — it was *diluted*. The pattern of "this is how a Dux Machina diagnosis looks" was technically present but no longer salient.

> Earlier patterns get buried under newer tokens. The fix isn't "load more context" — it's "make the format pattern *explicit and retrievable* instead of relying on implicit recall."

## Lever 4 — Tools (missing)

The agent had no explicit tool for "produce a diagnosis in the canonical Dux Machina format." It was operating off implicit memory of past examples instead of calling a deterministic formatter. That's the wrong reliability mode — memory drifts, tools don't.

> Memory-based pattern matching is fragile. Encoded skill is reliable.

---

## The senior fix (not the junior fix)

**Junior fix would have been:** rewrite the prompt with more explicit formatting rules. ("MAKE SURE the header is bold, MAKE SURE the recommendation block uses these exact phrases...") Works for a week, drifts.

**Senior fix:** create a `pe-diagnosis-format` skill that encodes the canonical structure. The agent invokes it; the skill enforces format deterministically.

Promotes implicit knowledge → explicit reusable tool.
This is also the Lesson 13 (Act-Learn-Reuse) pattern — reached organically while diagnosing a Lesson 1 problem.

---

## Meta-issue surfaced — Validator scope mismatch

The existing `pe_validation_gate.ps1` hook checked **structural integrity** (file exists, page count, no placeholders) but not **visual fidelity** (does this look like prior diagnoses?). The validator passed — but it was the wrong validator for this failure mode.

> A passing validator doesn't mean quality. It means the validator's scope was matched.

**Follow-up:** Build a second reviewer subagent (`pe-diagnosis-visual-reviewer`) that compares output to recent canonical diagnoses for format match. This is Lesson 6 work — visible before the lesson is formally studied.

---

## What I learned that wasn't in the lesson card

1. **Failures are usually 2+ levers, not one.** Forcing a single-cause story misses real fixes.
2. **The right diagnostic order also tells you the right *type* of fix.** Tools-lever problems → structural fixes (skills, schemas, validators). Prompt-lever problems → prompt patches. Pulling the right lever and writing the right fix are the same skill.
3. **A validator's *scope* is itself a leverage point.** "I have a validator" ≠ "I'm validated." What does it actually check?

---

## Action items dropped into the queue

- [ ] Create `pe-diagnosis-format` skill encoding the canonical structure
- [ ] Build `pe-diagnosis-visual-reviewer` subagent (Lesson 6 deliverable)
- [ ] Audit: which of my other validators are scope-mismatched?
