# ADR-0002: Hook Scripts Must Be ASCII-Only or UTF-8 With BOM

## Status

**Accepted** — 2026-05-13

## Context

On 2026-05-12, several hook scripts were authored in `.claude/hooks/` using markdown-style em-dashes (`—`, U+2014) and box-drawing characters (`═`, `─`) for visual section dividers and prose readability inside comments and string literals.

Within hours of deployment, every Bash command run in the user's terminal produced a `PreToolUse:Bash hook error: Failed with non-blocking status code` warning. Investigation traced the cause to PowerShell on Windows defaulting to **CP1252 (Windows-1252) encoding** when reading `.ps1` files. CP1252 cannot decode U+2014, U+2500, U+2550 and similar Unicode code points.

The script failed at **parse time** — it never reached its early-exit logic that should have allowed non-matching commands to pass through silently. The result: the hook was effectively broken for every Bash command, not just its intended trigger pattern.

The failure mode was non-blocking (Claude Code reported non-blocking status, so commands still ran), making it a **"silent friction"** bug. Users could mentally filter the error and continue working without reporting it. This is the worst kind of regression: not blocking, but slowly eroding trust in the toolchain.

The bug was caught only when the user ran an adversarial probe (an unrelated `start ""` command to open a `.docx`) and surfaced the persistent error to Claude for diagnosis.

## Decision

**All scripts in `.claude/hooks/` MUST be either:**

1. **ASCII-only (preferred)** — code points 0-127 only. No em-dashes, no box drawings, no smart quotes, no emoji.
2. **UTF-8 with BOM** — if non-ASCII content is genuinely needed, the file must include a UTF-8 BOM (`0xEF 0xBB 0xBF`) so PowerShell can detect the encoding correctly.

This decision applies retroactively to all existing hooks. A one-time sweep was performed on 2026-05-13 to sanitize all `.ps1` files in `.claude/hooks/`.

## Alternatives Considered

### 1. Save all hook scripts as plain UTF-8 (no BOM)
Rejected. PowerShell on Windows reads `.ps1` files in CP1252 by default. UTF-8-without-BOM looks identical to CP1252 in the file header, so PowerShell guesses wrong on any file containing multi-byte sequences. This is exactly the failure mode that triggered this ADR.

### 2. Configure PowerShell to default to UTF-8
Theoretically possible via `$PSDefaultParameterValues` or a profile setting, but this would be a per-machine configuration change that doesn't travel with the repository. New collaborators or fresh machines would re-experience the bug.

### 3. ASCII-only forever (no BOM exception)
Considered. Cleanest rule but potentially overly restrictive — there are legitimate cases for non-ASCII content (e.g., a hook that produces user-facing messages in multiple languages). The BOM exception preserves flexibility without sacrificing reliability.

## Consequences

### Positive
- **Hook scripts parse reliably** on any PowerShell version, any default code page, any machine.
- **No more silent friction** — encoding bugs of this class are eliminated structurally.
- **Easy to enforce** — a simple grep or Python check can validate the rule (and is implemented in `tools/verify_system.py` as `check_hook_encoding`).

### Negative
- **Source visual aesthetics slightly degraded** — section dividers now use `# ----` instead of `# ═══════`. Minor cost.
- **Authors must remember the rule** — but the verify_system check catches violations before they reach production.

### Mitigations
- `tools/verify_system.py` runs a hook-encoding check on every invocation. Weekly operator review catches violations early.
- This ADR + `OPERATOR_CHEATSHEET.md` ("Hook authoring rules" section) codify the rule so future authors learn it without re-discovering through outage.

## Follow-up

- ✅ All 5 `.ps1` files in `.claude/hooks/` sanitized to ASCII + UTF-8 BOM on 2026-05-13.
- ✅ `OPERATOR_CHEATSHEET.md` "Hook authoring rules" section updated with the rule + reference to this ADR.
- ✅ `tools/verify_system.py` includes `check_hook_encoding()` as a built-in property test.

## Lesson learned

**Silent failures are worse than loud failures.** A hook that blocks commands gets fixed in 10 minutes because nothing works. A hook that produces a confusing-but-non-blocking error gets ignored for hours/days while it slowly erodes operator trust. The right design for hook errors is **fail open** (exit 0 on internal hook error so user work proceeds) — but **also log the error somewhere durable** so it can be triaged later. The current hooks use `try/catch ... exit 0` which fails open correctly, but the encoding bug happened *before* the try block could run.
