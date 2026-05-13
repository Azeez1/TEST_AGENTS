# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the TEST_AGENTS repo.

## What is an ADR?

A short markdown document capturing **one** non-obvious architectural decision. Each ADR documents:

1. **Context** — what problem was being solved
2. **Decision** — what was chosen
3. **Alternatives Considered** — and why they were rejected
4. **Consequences** — pros, cons, mitigations

Once accepted, ADRs are **immutable**. To revise a decision, write a new ADR that supersedes the old one (the old one stays in the directory as historical record).

## When to write an ADR

Write an ADR when:

- A decision affects more than one file or component
- A future engineer might wonder "why did we do it this way?"
- An alternative was non-obviously rejected
- A new convention is being established that others should follow
- A bug exposed a previously implicit assumption (write the ADR as part of the fix)

Don't write an ADR for:

- Trivial implementation choices (use a `for` loop vs `while` loop)
- Personal style preferences
- Decisions already captured in commit messages or runbooks

## Index

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](ADR-0001-hooks-use-absolute-paths.md) | Use Absolute Paths in Claude Code Hook Commands | Accepted | 2026-05-12 |
| [ADR-0002](ADR-0002-hook-scripts-ascii-or-utf8-bom.md) | Hook Scripts Must Be ASCII-Only or UTF-8 With BOM | Accepted | 2026-05-13 |

## Naming convention

`ADR-NNNN-kebab-case-summary.md`

- **NNNN** is a 4-digit sequence number, starting at `0001`, incrementing by 1
- **Title** is kebab-case (lowercase, hyphens between words)
- **Extension** is `.md`

Examples:
- `ADR-0001-hooks-use-absolute-paths.md` ✅
- `ADR-0042-migrate-to-postgres.md` ✅
- `adr1.md` ❌ (no zero-padding, no descriptive title)
- `ADR-0001-Hooks-Use-Absolute-Paths.md` ❌ (not kebab-case)
- `decision.md` ❌ (no ADR prefix, no number)

The pattern is enforced by `output_routing_gate.ps1`. Non-conforming files trigger a WARN in `LOGS/routing-violations.log`.

## How to write a new ADR

1. **Find the next number** — look at the highest `ADR-NNNN-*` in this directory, add 1
2. **Pick a kebab-case title** — short, descriptive, no jargon
3. **Copy the template structure** from `ADR-0001-hooks-use-absolute-paths.md`
4. **Fill in the 5 sections:** Status, Context, Decision, Alternatives Considered, Consequences (+ optional Follow-up)
5. **Add a row to the Index** table above
6. **Commit** the ADR + the index update in the same commit

Total time per ADR: 5–15 minutes once the discipline is in place.

## ADR status values

- **Proposed** — under discussion, not yet committed to
- **Accepted** — the decision has been made and is in effect
- **Superseded by ADR-NNNN** — replaced by a newer decision (link to the new one)
- **Deprecated** — no longer recommended, but kept as historical record

## Further reading

The ADR concept was popularized by Michael Nygard in his 2011 essay *"Documenting Architecture Decisions."* It is widely adopted across Microsoft, AWS, ThoughtWorks, Spotify, and most open-source projects of any significant size.
