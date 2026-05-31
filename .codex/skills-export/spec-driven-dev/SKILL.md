---
name: "spec-driven-dev"
description: "Spec Driven Development methodology for structured AI agent task execution. Use when building complex features, multi-agent workflows, client deliverables, or any task where ambiguity would cause agents to go sideways. Generates structured specs with acceptance criteria before planning and implementation. Not needed for quick fixes, config changes, or single-agent tasks."
---

# Spec Driven Development (SDD)

AI coding agents don't fail because the model is weak. They fail because the instructions are ambiguous. SDD eliminates ambiguity before code gets written.

## When to Use SDD

**Use SDD for:**
- Complex features with multi-step flows, multiple edge cases, or cross-team coordination
- Client deliverables where requirements need to be locked down before execution
- Multi-agent workflows where several agents need to coordinate on a single outcome
- Any task where getting it wrong means significant rework

**Skip SDD for:**
- Quick bug fixes, config changes, one-liner updates
- Single-agent tasks where Plan mode is sufficient
- Exploratory work where requirements are deliberately undefined
- Tasks that can be fully described in 1-2 sentences without ambiguity

**Rule of thumb:** If the agent would need to make more than 3 assumptions to start coding, write a spec first.

## The 4-Step Process

### Step 1: Specify (WHAT, not HOW)

The spec is the **functional layer**. It describes what the feature does, not how it's implemented. It's technology-agnostic on purpose.

A good spec defines:
- **Problem statement** — what problem does this solve and for whom
- **Requirements** — numbered, unambiguous functional requirements
- **Edge cases** — what happens in non-happy-path scenarios
- **Acceptance criteria** — Given/When/Then format (these become the test plan)
- **Out of scope** — explicitly what this does NOT include

> **Key insight:** Separating WHAT from HOW reduces LLM uncertainty. When you mix functional requirements with technical decisions, the model has to juggle both simultaneously. By keeping the spec purely functional, you give the agent a clear objective without polluting it with premature implementation decisions.

**Use the appropriate template from `templates/`:**
- `feature-spec.md` — General features
- `campaign-spec.md` — Marketing campaigns
- `integration-spec.md` — APIs and integrations
- `bugfix-spec.md` — Bug investigation (lighter weight)

### Step 2: Plan (HOW)

The plan is the **technical layer** — the implementation guide. This is where developer expertise matters most:
- Architecture decisions ("Use NextJS with App Router, follow existing auth pattern")
- Data models and contracts
- Testing strategy
- Performance constraints
- References to existing codebase patterns and custom rules

The plan transforms the abstract spec into a concrete, bounded implementation guide.

### Step 3: Break into Tasks

Break the plan into small, ordered tasks. Each task must be:
- **Self-contained** — the agent shouldn't need to make assumptions
- **Unambiguous** — all context is embedded in the task description
- **Right-sized** — completable in a single agent session

Review the task list for overengineering. Does it really need seven tasks, or can three cover it?

Independent tasks can be executed by multiple agents simultaneously. This is where SDD unlocks parallelism.

### Step 4: Implement

Execute one task at a time. The agent has everything it needs from the spec + plan + task description.

After each task, validate against the acceptance criteria from Step 1.

## Maturity Levels

| Level | Description | When |
|-------|-------------|------|
| **Spec-First** | Write spec before coding, discard after delivery | Starting out — eliminates most ambiguity issues |
| **Spec-Anchored** | Spec lives in repo alongside code, evolves with it | Established teams — specs become living documentation |
| **Spec-as-Source** | Spec IS the primary artifact, code regenerates to match | Frontier — change the spec, code updates automatically |

Start at Level 1. Progress as the value becomes clear.

## Acceptance Criteria Format

Use Given/When/Then to make validation unambiguous:

```
Given a new user
When they click "Sign in with Google" and authorize the app
Then they are redirected to the onboarding flow with their profile pre-filled

Given a user with an existing Google account
When they try to sign in with GitHub using the same email
Then the accounts are linked and they see a confirmation message
```

These aren't just documentation — they become the **test plan**. QA_TEAM agents can generate tests directly from these criteria.

## Output Routing

Specs are saved to: `{TEAM}/outputs/specs/spec-{date}-{name}.md`

Example: `MARKETING_TEAM/outputs/specs/spec-2026-03-22-product-launch-campaign.md`

## Integration with QA_TEAM

When a spec includes Given/When/Then acceptance criteria:
1. The spec can be handed to `test-orchestrator` for automated test generation
2. Tests verify implementation against the spec, not reverse-engineered from code
3. This catches "it works but doesn't match requirements" issues

## How Claude Should Use This Skill

When this skill is invoked:

1. **Ask clarifying questions** — Identify what's ambiguous before writing anything
2. **Select the right template** — Read from `templates/` based on the task type
3. **Generate the spec** — Fill in the template with the user's answers
4. **Review with the user** — Present the spec for approval before proceeding to planning
5. **Save the spec** — Write to `{TEAM}/outputs/specs/`

The agent writes the first draft. The human reviews and approves. Then planning begins.

## Tradeoffs

- **Token cost:** SDD uses 2-3x more tokens than direct implementation. Worth it for complex tasks, overkill for simple ones.
- **Learning curve:** Shifting from "describe the code I want" to "describe the behavior I need" takes practice.
- **First specs are slow:** They get faster with practice. The value compounds over time.

See `gotchas.md` for common mistakes to avoid.
