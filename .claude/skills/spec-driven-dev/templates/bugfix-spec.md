# Bugfix Spec: {Bug Title}

| Field | Value |
|-------|-------|
| **Author** | {name} |
| **Date** | {YYYY-MM-DD} |
| **Team** | {team} |
| **Severity** | Critical / High / Medium / Low |
| **Status** | Investigating / Root Cause Found / Fix In Progress / Resolved |

## Symptoms

{What is the user experiencing? Be specific — include error messages, screenshots, or logs if available.}

**Observed behavior:** {What happens}
**Expected behavior:** {What should happen}
**Frequency:** {Always / Intermittent / Under specific conditions}

## Reproduction Steps

1. {Step 1}
2. {Step 2}
3. {Step 3}
4. **Result:** {What goes wrong}

**Environment:** {Browser, OS, API version, etc.}

## Root Cause Hypothesis

{What do you think is causing this? Reference specific files, functions, or configurations if known.}

**Suspected file(s):** `{path/to/file.py}`
**Suspected logic:** {Description of what's likely wrong}

## Fix Criteria

The fix is complete when:

```gherkin
Given {the conditions that trigger the bug}
When {the action that causes the failure}
Then {the correct behavior occurs instead}

Given the fix is deployed
When {normal usage scenario}
Then {no regression in existing functionality}
```

## Regression Test Plan

- [ ] {Test that the specific bug is fixed}
- [ ] {Test that related functionality still works}
- [ ] {Test edge case that's close to the bug scenario}

## Out of Scope

- {Related issues that are separate bugs}
- {Refactoring that would be nice but isn't required for the fix}

## Notes

{Links to error logs, related tickets, prior discussions}
