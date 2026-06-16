---
description: Run EZ's daily LinkedIn + X social engagement round (on-brand, batch-approved)
argument-hint: "[both|linkedin|x] [draft-only]"
---

# Daily Social Round

**Scope = `$ARGUMENTS`.** Parse it:
- empty or `both` → run BOTH platforms (default)
- `linkedin` (or `li`) → LinkedIn ONLY (skip all X steps)
- `x` (or `twitter`) → X ONLY (skip all LinkedIn steps)
- `draft-only` (can combine, e.g. `x draft-only`) → do everything through the batch + log, but do NOT post; notify EZ to approve later.

Run the **daily-social-round** skill now (`.claude/skills/daily-social-round/SKILL.md`), limited to the scope above. Follow it exactly. Summary of the run:

1. **Connect + verify:** `tabs_context_mcp`; if multiple Chrome browsers, ask EZ which (`AskUserQuestion`) then `select_browser`. Open LinkedIn + X. **Verify logged in as EZ (X = @EZdaArchitect).** If a login wall or wrong account, STOP and tell EZ.
2. **Read voice:** `DUX_MACHINA/social/voice-foundation.md` (the 3 platform voices + banned patterns).
3. **Find on-brand targets** in both feeds (operations / business / building / AI / PM niche; ~10-50 comments; EZ has a POV). Skip politics, drama, tragedy, anything off-brand.
4. **Capture each PERMALINK first**, then draft in the platform voice and self-check (no em/en dashes, no hashtags, no AI-tells, no fabricated claims, fits 280 on X).
5. **Write the batch to** `DUX_MACHINA/social/log/round-YYYY-MM-DD.md` and **present it to EZ as link + draft pairs for ONE approval.** WAIT.
6. **On approval, post by navigating to each permalink**, screenshot-verify, then click post. Update the log. Log any PM ICP-lead comments to the leads sheet.

**Default volume (per scope):** BOTH = 5 LinkedIn comments (3 growth + 2 PM ICP) + 5 X replies + 4 quote-posts + 1 X post. LinkedIn-only = 5 comments + 1 post. X-only = 5 replies + 4 quote-posts + 1 post. Tune on request.

**Never post without EZ's approval.** The brand-voice hook (`brand_voice_gate.ps1`) is a hard backstop, but self-check first.

## Looping this
- **Live (recommended):** `/loop /social-round` — runs daily, drafts the batch, pauses for your approval, posts. Approval works naturally because you're in the session.
- **Args:** `linkedin` / `x` to scope to one platform; `draft-only` to stop after step 5 (no posting, approve later). Combine them, e.g. `/social-round x draft-only` or `/loop /social-round linkedin`.
