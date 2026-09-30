---
description: One pass over the intent engine v2 funnel lists - pick top targets by expected_value, draft a full 4-touch outreach sequence per target, queue for approval (never sends)
arguments:
  - name: options
    description: "Optional: 'fresh' to force a re-scan; 'list=<customers|acquisitions>' to draft from one funnel only; 'avenue=<name>' to filter (trucking|property_mgmt|mechanical|manufacturing|dead_listings|pe_distress); 'n=<count>' for how many targets (default 5)"
    required: false
---

# Intent Scan Watch (single pass, 4-touch draft engine)

Run ONE pass over the Dux Intent Signal Engine v2 funnel lists with **$ARGUMENTS**. Designed to be repeated (e.g. Monday mornings after the scheduled scan, or via `/loop`); each invocation is self-contained. For every picked target this drafts a FULL 4-touch sequence, queues it for human review, and logs `drafted` to the outcome log.

## HARD RULE

**This command NEVER sends anything. Every draft goes to a queue file for human review. EZ approves each item personally before any send, and any send happens in a separate, explicitly approved step. The team_email_gate 50/day limit and the Money Rule (if it touches money, a human approves. Period.) apply on top.**

## DELIVERABILITY WARNING (READ BEFORE ANY SEND DECISION)

**DO NOT blast these sequences from the primary Gmail (sabaazeez12@gmail.com). Cold outbound volume from the primary personal inbox is a deliverability and reputation risk: it can burn the domain/inbox that runs everything else.** Sending infrastructure (separate domain, warmed inbox, SPF/DKIM/DMARC) is a SEPARATE FUTURE DECISION that EZ makes explicitly. Until then, drafts sit in the queue file. This command has no opinion on sending because it never sends.

## Process

### 1. Load the funnel lists

Find the newest `SALES_TEAM/outputs/prospecting/intent_customers_*.csv` and `intent_acquisitions_*.csv` (ignore any `dry_run/` subfolder). If either is missing, OR the newest is older than 7 days, OR `$ARGUMENTS` contains `fresh`: re-run the engine first via Bash:

```
cd C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\SALES_TEAM\tools\intent_engine && python run_intent_scan.py --since-days 7
```

(drop `--no-sheet` only if INTENT_SPREADSHEET_ID is set in `~/.dux_intent/.env`; otherwise add `--no-sheet`). Then reload the newest CSVs.

V2 columns (exact): `rank, expected_value, pain, timing, ability_to_pay, deal_size, pay_data, entity, metro, top_signals, evidence, contact, avenue, timing_window, hot`. Rows are already ranked by `expected_value` (0..2 scale, comparable across funnels). `pay_data=unknown` rows are VALID targets (ability is neutral 0.5 by design); never exclude a row for missing pay data.

### 2. Filter and pick

- If `$ARGUMENTS` contains `list=customers` or `list=acquisitions`, use only that file. Otherwise merge both files and re-sort by `expected_value` descending.
- If `$ARGUMENTS` contains `avenue=<name>`, keep only that avenue.
- **30-day skip:** drop any entity already drafted in the last 30 days. Check BOTH: (a) the outcome log via Bash `cd .../SALES_TEAM/tools/intent_engine && python -m common.outcomes list --stage drafted` (compare `recorded_at` to today, match on entity name inside `entity_key` or note), and (b) entity names appearing in any `SALES_TEAM/outputs/outreach/intent_drafts_*.md` dated within 30 days. Skip on either hit. Do not re-pitch.
- Take the top N remaining by `expected_value` (N from `n=<count>` in `$ARGUMENTS`, default 5).

### 3. Resolve entity_key and funnel per target

For each picked row, look up the canonical `entity_key` from the engine DB via Bash (one call per target or one batched call):

```
cd C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\SALES_TEAM\tools\intent_engine && python -c "import sqlite3,config; c=sqlite3.connect(str(config.DB_PATH)); print((c.execute('SELECT entity_key FROM entities WHERE name=? AND metro=?',('<ENTITY>','<METRO>')).fetchone() or ['name:<entity lowercased>'])[0])"
```

If no DB match, fall back to `name:<entity lowercased>` as the key. Funnel comes from `signal_registry.json` `avenues.<avenue>.funnel` (customers: trucking, property_mgmt, mechanical, manufacturing; acquisitions: dead_listings, pe_distress); the demo asset from `avenues.<avenue>.demo_asset` (trucking=Ironhaul, property_mgmt=Stonebridge, mechanical=Meridian, manufacturing=Plantview, dead_listings=broker-play, pe_distress=acquisition-hunt).

### 4. Draft the 4-touch sequence per target

**Channel:** if the `contact` field contains an email address (an `@` token), draft email touches (subject + body each). If NOT, draft every touch as a **phone-script variant**: a call opener (2-3 sentences), talk track bullets, and a <=25-word voicemail line, using the phone number from `contact` if present.

**Funnel-aware framing (mandatory):**
- `customers` funnel: "I can fix this leak" posture. The signals are operational bleed; position Dux Machina operational visibility, reference the matching demo asset as a working system for exactly this problem, CTA = Leak Scan (duxmachina.com/visibility).
- `acquisitions` funnel: broker/seller or buy-interest posture, NOT a services pitch and NO Leak Scan CTA. `dead_listings`: the listing has sat (cite days on market / price cuts); frame as a serious, discreet buyer or buyer-side conversation. `pe_distress`: discreet interest in acquiring or partnering given the pressure signals; respectful, zero-shame tone. CTA = a short private call about the sale/exit.

**The four touches** (suggested send-day offsets are metadata for the human; nothing is scheduled or sent):

1. **T1 - Evidence opener (Day 0, 90-140 words).** Open with the SPECIFIC signal evidence: name the actual events from `top_signals` in plain English (e.g. "two insurance cancellations and an OOS rate double the national average", "listed 240 days with a price cut in March") and cite `evidence` URLs as proof links. Name the matching demo asset for customers-funnel targets. One CTA.
2. **T2 - Value + proof (Day 3-4, 80-120 words).** Different angle from T1: what the fix/deal looks like, with the demo link (customers) or a concrete signal of buyer seriousness (acquisitions). Reference T1 in one clause, do not repeat its evidence.
3. **T3 - Mini-diagnosis / different angle (Day 8, 100-150 words).** Customers: a 3-bullet mini-diagnosis of what the signals imply operationally and the one number they should check this week. Acquisitions: a different lens on the situation (timing window from `timing_window`, market context, or what similar operators did). Give value even if they never reply.
4. **T4 - Breakup (Day 14, 50-80 words).** Short, zero pressure, door stays open. One line restating the single most concrete signal, one line of exit.

**Voice for all touches:** calm power, stoic precision. NO em dashes, no hashtags, no AI-tells, no fake claims, no fabricated case studies (only Prime Fleet is real). Include a "verify identity and contact before approving any send" note per target.

### 5. Queue for approval

Append all sequences to `SALES_TEAM/outputs/outreach/intent_drafts_{YYYY-MM-DD}.md`. Start the file (if new) with the HARD RULE and the DELIVERABILITY WARNING verbatim. Each target gets a header block, then four touch blocks, each with its own approval line:

```
## TARGET: {entity}  ({avenue}/{metro}, funnel {funnel}, EV {expected_value}, hot {hot})
EV breakdown: pain {pain} | timing {timing} ({timing_window}) | ability {ability_to_pay} (pay_data={pay_data}) | deal_size {deal_size}
Signals: {top_signals}
Evidence: {evidence}
Contact: {contact}   Channel: {email|phone-script}
Entity key: {entity_key}
NOTE: verify identity and contact before approving any send.

### Touch 1 (Day 0) - evidence opener      [ ] APPROVE  [ ] EDIT  [ ] SKIP
Subject: ...
{body or phone script}

### Touch 2 (Day 3-4) - value + proof      [ ] APPROVE  [ ] EDIT  [ ] SKIP
...

### Touch 3 (Day 8) - mini-diagnosis       [ ] APPROVE  [ ] EDIT  [ ] SKIP
...

### Touch 4 (Day 14) - breakup             [ ] APPROVE  [ ] EDIT  [ ] SKIP
...
```

### 6. Log the outcome (drafted)

After the queue file is written, record ONE `drafted` outcome per target via Bash (this is the ground-truth log that later tunes EV weights):

```
cd C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\SALES_TEAM\tools\intent_engine && python -m common.outcomes record "{entity_key}" drafted --note "4-touch queued {YYYY-MM-DD} intent_drafts_{YYYY-MM-DD}.md" --funnel {funnel}
```

Never record `sent`, `replied`, `meeting`, `won`, or `lost` from this command; those stages are recorded manually by EZ after real-world events.

## Output rules (keep the loop quiet)

- Queued sequences: report ONE summary line per target: `{entity} ({avenue}/{funnel}, EV {expected_value}) -> 4 touches queued, outcome logged`.
- Nothing to draft after filtering: ONE line only, e.g. `No new targets (lists 2026-07-05, 3 skipped as drafted <30d, 0 matching filter)`.
- Never mark an entity as contacted; this command only drafts. Sending is a separate human-approved action with its own infrastructure decision.
