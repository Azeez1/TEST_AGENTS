---
description: Generate intelligent LinkedIn comments for active business owner leads
arguments:
  - name: input
    description: A number (process N leads from sheet), a LinkedIn profile URL (direct mode), or blank (default 10)
    required: false
---

# LinkedIn Comment Engine — Comment Generator

Process leads and generate LinkedIn comments. Supports two modes:

**Mode 1 — Batch (default):** Process **N** leads from the Google Sheet.
```
/comment-engine 10     # Process 10 leads from sheet
/comment-engine 5      # Process 5 leads
/comment-engine        # Default: 10
```

**Mode 2 — Direct Link:** Pass a LinkedIn profile URL to skip lead discovery entirely.
```
/comment-engine https://www.linkedin.com/in/someone
```
Direct link mode will:
1. Open their profile in Chrome MCP
2. Read their latest post
3. Check if it's worth commenting on (if not, report and stop)
4. Extract their name, title, company from the profile
5. Draft a comment
6. Add them to the sheet with the post and comment
7. No `/comment-leads` needed — one command does everything

## Target Spreadsheet

- **Spreadsheet Name:** "Dux Machina Comment Engine"
- **Google Account:** sabaazeez12@gmail.com
- **Tab:** "Active Leads"

**PREREQUISITE:** Run `/comment-leads` first to populate the sheet with leads.

## Process (MUST FOLLOW EXACTLY)

### Step 1: Read Lead List and Select Targets

Use Google Workspace MCP to read "Active Leads" tab:

1. Read all rows with data
2. **FILTER** for leads where:
   - Column M (Status) = "NEW" or "ACTIVE"
   - Column O (Last Commented Date) is EMPTY or older than 14 days (cooldown)
   - Column Q (Consecutive Inactive Count) < 3 (not stale)
3. **PRIORITIZE** by:
   - Highest score first (if available from lead-gen)
   - Status "ACTIVE" over "NEW" (re-engage known active posters)
4. **SELECT** top [count] leads (default 10)
5. If fewer than [count] qualify, report how many are available

### Step 2: Find Their Latest Post

For EACH selected lead, find their most recent LinkedIn post:

**CRITICAL: You MUST use Chrome MCP first. DO NOT skip to Bright Data for speed. Bright Data search snippets are unreliable — they can misrepresent post content, age, and substance. Chrome shows you the REAL post.**

**Method 1 — Chrome MCP (MANDATORY FIRST STEP):**
Chrome is the default browser with your logged-in LinkedIn session.
1. Use `mcp__claude-in-chrome__navigate` to go to the lead's LinkedIn post URL or profile activity page
2. Use `mcp__claude-in-chrome__get_page_text` (fastest) or `read_page` to read the full post text
3. Extract: full post text, exact post age, exact engagement (reactions + comments count)
4. If navigating to profile activity, pick the most recent original post with HIGHEST engagement
5. **VERIFY the post is real and recent before drafting any comment**

**Method 2 — Bright Data Search (FALLBACK ONLY):**
Use ONLY if Chrome MCP can't find recent posts (profile restricted, activity hidden, Chrome not responding):
```
site:linkedin.com/posts "[person's full name]" 2026
```
- If you use Bright Data to find a post URL, you MUST still navigate to it in Chrome to verify and read the full text before drafting
- NEVER draft a comment from a search snippet alone

**IF person has NO commentable post (no post in 7 days, or only promos/link shares):**
- DELETE the lead's row from the sheet entirely — do not leave dead rows
- Report them as "REMOVED — no genuine post found" in the output
- Pull a REPLACEMENT from remaining leads in the sheet
- Continue until you have [count] leads with real posts OR you've exhausted the list

**SKIP posts that are:**
- Less than 20 words of text (image/video only)
- Reshares with no original commentary
- Job postings or event promotions
- Purely promotional CTAs ("Comment KEYWORD below", "Book a free call", "DM me for...")
- Link shares with no original thought added
- Listicle-style lead magnets disguised as posts
- Posts that are basically ads for their own service/program
- Older than 7 days

**"WORTH COMMENTING ON" FILTER (CRITICAL):**
After reading the full post in Chrome, ask: **"Did this person share a genuine thought, experience, or opinion?"**
- ✅ YES = They told a real story, shared a hard-won lesson, asked a real question, or took a stance on something
- ❌ NO = They're promoting their service, running a campaign, posting engagement bait, or just sharing a link

If NO, **skip the lead for this cycle** and move to the next one. Do NOT force a comment on a post that's just a promo. It's better to comment on 4 genuine posts than 10 promos.

Report skipped leads as "SKIPPED — no commentable post" in the output.

### Step 3: Classify Post and Generate Comment

For each post found that PASSED the "worth commenting on" filter:

**A. READ the full post text carefully**

**B. CLASSIFY the post type:**

| Type | Signal Words |
|------|-------------|
| PROBLEM | "struggling with", "frustrated", "challenge", "issue", "losing", "declining" |
| ADVICE | "here's what I learned", "tip", "lesson", "what works", "how to", "strategy" |
| WIN | "excited to announce", "milestone", "just hit", "celebrating", "grateful for" |
| QUESTION | "anyone dealt with?", "looking for advice", "what would you do?", "recommendations?" |
| OPINION | "I think", "unpopular opinion", "hot take", "the industry needs", "stop doing" |
| STORY | "last week", "a client told me", "I remember when", "true story", "here's what happened" |

**C. GENERATE comment — THE FORMULA:**

The formula is simple: **Read the post. Agree with something specific. Add one thought. Keep it human.**

Do NOT use rigid templates. Instead, follow this natural flow:

1. **Anchor** — Reference a specific line, phrase, or detail from THEIR post that shows you actually read it
2. **Agree + Add** — Build on their point with one genuine insight, observation, or related experience
3. **Close** — Either a short thought that lands, or a genuine question that invites conversation

**Tone calibration by post type:**
- **PROBLEM** — Validate the pain, add context on why it's harder than people think
- **ADVICE** — Agree with their strongest point, add one thing they didn't mention
- **WIN** — Acknowledge the specific achievement, note what made it hard
- **QUESTION** — Give a direct, useful answer from experience
- **OPINION** — Agree and extend, or respectfully add nuance (never attack their premise)
- **STORY** — Connect their experience to a broader pattern you've noticed

**D. COMMENT RULES (CRITICAL — MUST FOLLOW ALL):**

✅ MUST DO:
- Max 3-4 sentences
- Reference at least ONE specific detail from THEIR post (a phrase, number, or situation) that couldn't apply to any other post
- Add ONE genuine thought they didn't say — not five, just one
- Sound like a peer having a conversation, not a consultant dropping a framework
- Voice: conversational, genuine, informed but not showy
- Read the comment back and ask: "Would a real person actually say this in conversation?" If no, rewrite.

❌ MUST NOT:
- NO "Great post!" or "Love this!" or generic praise
- NO self-promotion ("I help businesses with...", "At my company we...")
- NO links or CTAs ("DM me", "check out my...", "book a call")
- NO mentioning Dux Machina, your services, or your business
- NO hashtags
- NO emoji-heavy responses
- NO comments that could apply to ANY post on the same topic — must be SPECIFIC to THIS post
- NO consultant jargon ("talent arbitrage," "revenue treadmill," "operational Dunning-Kruger," "contribution margin per menu square inch")
- NO fabricated statistics (don't invent "40-60% lower CPL" or "12-18% lift" — only use numbers if they came from the post or are genuinely well-known)
- NO attacking or challenging the poster's core premise — you're building on their point, not debating them
- NO trying to sound smarter than the poster — the goal is peer, not professor
- NO em dashes (—) — use periods, commas, or "and" instead

**E. BACKGROUND CONTEXT (use ONLY when naturally relevant — NEVER force):**

The commenter (Azeez) has practical experience in:
- Business diagnosis using first principles thinking (finding hidden revenue/cost leaks)
- AI automation for operations, scheduling, workflows
- Healthcare throughput optimization (patients per provider calculations)
- Restaurant operations (delivery commissions, online ordering optimization)
- Real estate CRM activation (dormant contact lists)
- Agency onboarding optimization (reducing time-to-value)
- DTC e-commerce (return rate analysis, UGC cost optimization)

RULES for using background context:
- MOST comments should NOT reference your case studies
- Only reference when the post is DIRECTLY about a topic you have real numbers on
- When you do reference, keep it vague: "I've seen this pattern" not "I analyzed a dental practice"
- The goal is to sound INFORMED, not to pitch
- Let the PROFILE do the selling, not the comment

**F. QUALITY SELF-SCORE (1-10):**

| Score | Criteria |
|-------|----------|
| 9-10 | References a specific detail from their post, adds one genuine thought, reads like a real person wrote it in 30 seconds after reading the post |
| 7-8 | Relevant and adds value, but could be slightly more specific or slightly more natural |
| 5-6 | Generic-leaning, could apply to similar posts, or sounds too "consultant-y" |
| Below 5 | Flag as LOW_CONFIDENCE — mark for human rewrite |

**QUALITY GUT CHECK:** Read the comment out loud. If it sounds like something you'd actually type on your phone after reading someone's post, it's good. If it sounds like a mini-essay or a consulting pitch, rewrite it simpler.

**G. VARIATION CHECK:**
- Compare each drafted comment against ALL other comments in this batch
- If any two comments are >70% similar in structure or content → REWRITE one with a completely different angle
- Each comment MUST be unique even if posts cover similar topics

### Step 4: Write to Google Sheet

For each processed lead, update their row:

| Column | Update With |
|--------|-------------|
| F | Latest Post URL (full clickable URL) |
| G | Post text summary (first 150 chars of post + topic keyword) |
| H | Post date (YYYY-MM-DD format) |
| I | Post type (PROBLEM / ADVICE / WIN / QUESTION / OPINION / STORY) |
| J | Post engagement (e.g., "47 likes, 12 comments" or "~50 likes" if estimated) |
| K | Drafted comment (the full AI-generated comment) |
| L | Comment quality score (number 1-10) |
| M | Status → change to "DRAFTED" |

**DO NOT** overwrite columns N, O, P, Q, R (tracking columns).

For leads that were INACTIVE (no recent post):
- Update column Q (increment Consecutive Inactive Count)
- If Q >= 3, set column M to "INACTIVE"

### Step 5: Output Report

Display results in this format:

```
COMMENT BATCH READY FOR REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [Name] | [Title] | [Company]
   Post: "[First 80 chars of their post]..."
   Type: [POST_TYPE] | Engagement: [X likes, Y comments]
   Comment: "[Full drafted comment]"
   Quality: [X]/10
   Post URL: [clickable link]

2. [Name] | [Title] | [Company]
   Post: "[First 80 chars]..."
   Type: [POST_TYPE] | Engagement: [X likes]
   Comment: "[Full drafted comment]"
   Quality: [X]/10
   Post URL: [clickable link]

[...continue for all processed leads]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BATCH SUMMARY:
  Total drafted: X
  Average quality: X.X/10
  Low confidence flags: X (needs extra review)
  Inactive leads skipped: X
  Replacement leads pulled: X
  Sheet updated: ✅

POST TYPE BREAKDOWN:
  PROBLEM: X | ADVICE: X | WIN: X
  QUESTION: X | OPINION: X | STORY: X

NEXT STEPS:
  1. Open Google Sheet → review "Active Leads" tab
  2. Click each Post URL → read original post (30 sec each)
  3. Review drafted comment → APPROVE, EDIT, or SKIP
  4. Change Status from DRAFTED to APPROVED
  5. Post approved comments to LinkedIn (manually or via automation)
  6. Update Status to POSTED and set Date Commented
```

## Anti-Spam Rules (ENFORCED BY THIS COMMAND)

- Max 12 comments recommended per day
- Minimum 14-day cooldown per person (enforced in Step 1 filter)
- Never comment on same post URL twice (check column P)
- Never include links, CTAs, or self-promotion in comments
- Max 4 sentences per comment
- Each comment must reference specific detail unique to THEIR post
- If person has been inactive 3+ times consecutively → auto-archive

## After Posting (Manual Update Process)

After you post comments on LinkedIn, update the sheet:
1. Change column M from "APPROVED" to "POSTED"
2. Set column N (Date Commented) to today's date
3. Set column O (Last Commented Date) to today's date
4. Add the post URL to column P (Posts Commented On) — append with pipe separator

When engagement happens:
- Someone replies to your comment → change Status to "ENGAGED"
- Someone DMs you from seeing the comment → change Status to "CONVERTED"
- Track these for ROI measurement

## Usage

```
/comment-engine 10                                      # Batch: process 10 leads from sheet
/comment-engine 5                                       # Batch: process 5 leads
/comment-engine                                         # Batch: default 10
/comment-engine https://www.linkedin.com/in/someone     # Direct: one person, full workflow
```
