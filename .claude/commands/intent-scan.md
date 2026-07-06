---
description: One pass over the intent engine hot list - pick top hot accounts, draft evidence-cited outreach, queue for approval (never sends)
arguments:
  - name: options
    description: "Optional: 'fresh' to force a re-scan, 'avenue=<name>' to filter (trucking|property_mgmt|mechanical|manufacturing|dead_listings|pe_distress), 'n=<count>' for how many drafts (default 5)"
    required: false
---

# Intent Scan Watch (single pass)

Run ONE pass over the Dux Intent Signal Engine hot list with **$ARGUMENTS**. Designed to be repeated (e.g. Monday mornings after the scheduled scan, or via `/loop`); each invocation is self-contained.

## HARD RULE

**This command NEVER sends anything. Every draft goes to a queue file for human review. EZ approves each item personally before any send, and any send happens in a separate, explicitly approved step. The team_email_gate 50/day limit and the Money Rule (if it touches money, a human approves. Period.) apply on top.**

## Process

1. **Load the hot list.** Find the newest `SALES_TEAM/outputs/prospecting/intent_hotlist_*.csv` (ignore the `dry_run/` subfolder). If none exists, OR the newest is older than 7 days, OR `$ARGUMENTS` contains `fresh`: re-run the engine first via Bash:
   `python C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\SALES_TEAM\tools\intent_engine\run_intent_scan.py --since-days 7`
   (drop `--no-sheet` only if INTENT_SPREADSHEET_ID is set in `~/.dux_intent/.env`; otherwise add `--no-sheet`). Then reload the newest hotlist CSV.
2. **Filter and pick.** Keep rows where `hot=TRUE`. If `$ARGUMENTS` contains `avenue=<name>`, keep only that avenue. Skip any entity whose `entity_key` or `entity_name` already appears in a `SALES_TEAM/outputs/outreach/intent_drafts_*.md` file from the last 30 days (already drafted - do not re-pitch). Take the top N by `score` (N from `n=<count>` in `$ARGUMENTS`, default 5).
3. **Draft outreach per account.** For each picked row write a short cold email draft (subject + body, 90-140 words) that:
   - Opens with the SPECIFIC signal evidence: name the actual events from `top_signals` in plain English (e.g. "two insurance cancellations and an OOS rate double the national average", "14 eviction filings in the last 30 days") and cite the `evidence_urls` as proof links.
   - Frames the pitch around the avenue's `demo_asset` from `signal_registry.json` (trucking=Ironhaul, property_mgmt=Stonebridge, mechanical=Meridian, manufacturing=Plantview, dead_listings=broker-play, pe_distress=acquisition-hunt): "here is a working demo of the exact visibility system for this problem".
   - Ends with the Leak Scan CTA (duxmachina.com/visibility), calm-power voice, NO em dashes, no hashtags, no AI-tells.
   - Includes the contact fields available (phone/email/street) and flags `match_conf < 1.0` rows as "verify identity before sending".
4. **Queue for approval.** Append all drafts to `SALES_TEAM/outputs/outreach/intent_drafts_{YYYY-MM-DD}.md`. Each draft gets a header block:
   ```
   ## [ ] APPROVE  [ ] EDIT  [ ] SKIP  -  {entity_name}  ({avenue}/{metro}, score {score})
   Signals: {top_signals}
   Evidence: {evidence_urls}
   Contact: {email} {phone} {street}
   Match confidence: {match_conf}
   ```
   followed by the subject line and body.

## Output rules (keep the loop quiet)

- Queued drafts: report ONE summary line per draft: `{entity_name} ({avenue}, {score}) -> queued`.
- No hot rows after filtering: ONE line only, e.g. `No new hot accounts (hotlist 2026-07-05, 3 already drafted, 0 matching filter)`.
- Never mark an entity as contacted; this command only drafts. Sending is a separate human-approved action.
