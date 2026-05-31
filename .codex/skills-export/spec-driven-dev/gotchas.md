# Gotchas — Spec Driven Development

> Built from real experience rolling out SDD. Avoid these mistakes.

## 1. Mixing WHAT and HOW in the Spec
**Symptom:** Your spec says things like "Use NextAuth.js with JWT strategy" or "Store in PostgreSQL with a users table."
**Why it's wrong:** The spec is the functional layer — WHAT, not HOW. Technical decisions go in the Plan (Step 2). Mixing them creates branching paths that confuse the agent and make the spec technology-dependent.
**Fix:** If a sentence mentions a specific library, framework, or implementation detail, move it to the Plan. The spec should be readable by a non-technical stakeholder.

---

## 2. Overspeccing Simple Tasks
**Symptom:** You wrote a 2-page spec for a config change or a one-line bug fix.
**Why it's wrong:** SDD uses 2-3x more tokens. For simple tasks, this cost isn't justified. Plan mode or a direct prompt is faster and cheaper.
**Fix:** Use the decision rule: if the agent would need to make more than 3 assumptions, write a spec. Otherwise, just do it.

---

## 3. Untestable Acceptance Criteria
**Symptom:** Criteria like "The feature should be fast" or "The UI should look good" or "Handle errors gracefully."
**Why it's wrong:** If you can't write an automated test for it, the agent can't verify it either. Vague criteria lead to vague implementations.
**Fix:** Rewrite in Given/When/Then with specific, measurable conditions:
- Bad: "The page should load fast"
- Good: "Given a user on a 3G connection, When they load the dashboard, Then the first contentful paint occurs within 2 seconds"

---

## 4. Spec Becomes a Novel
**Symptom:** Your spec is 5+ pages with exhaustive detail about every possible scenario.
**Why it's wrong:** Overly long specs consume context window, dilute the agent's focus, and take longer to review than to just write the code.
**Fix:** 1-2 pages max for most features. Focus on the non-obvious: edge cases, gotchas, things the agent would get wrong without guidance. Skip anything the agent can infer from the codebase.

---

## 5. Skipping Human Review
**Symptom:** The agent writes the spec and immediately starts planning/implementing without showing it to you.
**Why it's wrong:** The spec is a contract. If it's wrong, everything downstream is wrong too. Catching a bad requirement in the spec is 10x cheaper than catching it in code.
**Fix:** Always review the spec before proceeding. The agent drafts, the human approves. No exceptions for complex features.

---

## 6. No Team Boundaries in Multi-Team Specs
**Symptom:** A spec for a cross-team feature doesn't say which team owns which part.
**Why it's wrong:** Without explicit boundaries, agents from different teams may duplicate work, conflict, or write to each other's directories.
**Fix:** Add a "Team Ownership" section: "MARKETING_TEAM owns content generation. ENGINEERING_TEAM owns the API endpoint. QA_TEAM owns the test suite." Each team's work should be independently implementable.

---

## 7. Treating SDD as Mandatory for Everything
**Symptom:** Every single task gets a full spec-plan-tasks cycle, including trivial changes.
**Why it's wrong:** SDD is a tool, not a religion. Overhead kills velocity when applied to the wrong tasks.
**Fix:** Reserve SDD for complex, ambiguous, or high-stakes work. Use Plan mode for medium tasks. Use direct prompts for simple tasks.
