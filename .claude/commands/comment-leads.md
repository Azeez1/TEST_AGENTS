---
description: Find active LinkedIn business owners who post regularly and add to Google Sheet
arguments:
  - name: count
    description: Number of leads to generate (default 50)
    required: false
---

# LinkedIn Comment Engine — Lead Discovery

Generate **$ARGUMENTS** (default: 50) NEW verified active business owner leads and append to Google Sheet.

## Target Spreadsheet

- **Spreadsheet Name:** "Dux Machina Comment Engine"
- **Google Account:** sabaazeez12@gmail.com
- **Tab:** "Active Leads"

**FIRST RUN:** Search Google Drive for spreadsheet named "Dux Machina Comment Engine". If not found, create it using Google Workspace MCP with headers in Row 1. If found, use existing spreadsheet ID.

## Sheet Structure — "Active Leads" Tab

Row 1 Headers (18 columns):

| Col | Header | Description |
|-----|--------|-------------|
| A | Name | Full name |
| B | Title | Their job title |
| C | Company | Company name |
| D | Industry | healthcare, restaurant, agency, service, real estate, dental, tech, other |
| E | LinkedIn Profile URL | Their profile URL (for dedup) |
| F | Latest Post URL | URL of their most recent post (filled by /comment-engine) |
| G | Post Text Summary | Summary of post content (filled by /comment-engine) |
| H | Post Date | Date of latest post (filled by /comment-engine) |
| I | Post Type | PROBLEM/ADVICE/WIN/QUESTION/OPINION/STORY (filled by /comment-engine) |
| J | Post Engagement | Likes + comments count (filled by /comment-engine) |
| K | Drafted Comment | AI-generated comment (filled by /comment-engine) |
| L | Comment Quality Score | 1-10 self-score (filled by /comment-engine) |
| M | Status | NEW / ACTIVE / DRAFTED / APPROVED / POSTED / ENGAGED / CONVERTED / INACTIVE / ARCHIVED |
| N | Date Commented | When comment was posted |
| O | Last Commented Date | For 14-day cooldown tracking |
| P | Posts Commented On | Pipe-separated list of post URLs already commented on |
| Q | Consecutive Inactive Count | Number of times no recent post found (0 = active) |
| R | Notes | Any additional notes |

## Process (MUST FOLLOW EXACTLY)

### Step 0: Plan First, Execute Second (Lesson 3)

**BEFORE invoking any tool or searching anything**, write a one-page plan to `tmp/plans/comment-leads-{YYYY-MM-DD-HHmm}.md` containing:

1. **Target count** — how many leads (default 50, from $ARGUMENTS)
2. **Industry mix goal** — rough split across healthcare / dental / restaurant / agency / service / real estate / other (sum to total)
3. **Geographic mix** — Houston-Texas priority %, other US %
4. **Query themes you'll use** — 5-8 specific Bright Data queries from the lists below (don't just pick all of them — pick the ones that match this batch's intent)
5. **Score distribution expected** — rough split of Hot 9-10 / Warm 7-8 / Cool 5-6
6. **Failure modes to watch for** — non-US slip-ins, image-only posts, dead profiles, duplicates with existing sheet

Then **STOP** and present the plan to the user with: "Plan ready at `tmp/plans/comment-leads-{ts}.md` — approve to execute, or push back on the mix?"

**DO NOT proceed to Step 1 until the user explicitly approves the plan.**

If the user pushes back (e.g., "shift more to dental this time"), update the plan, present again, wait for approval. Only on explicit approval do you execute Steps 1-6 below.

**Rationale (Lesson 3):** without a plan, deviations are silent. With a plan, deviations get caught at the cheapest possible time — before any search tokens are spent.

### Step 1: Read Sheet & Build Deduplication Set (CRITICAL)

Use Google Workspace MCP to:
1. Search Drive for "Dux Machina Comment Engine" spreadsheet
2. If found, read the spreadsheet. If not found, create it with headers.
3. Read ALL existing LinkedIn Profile URLs from column E — read in chunks if needed (E2:E500, E501:E1000, etc.)
4. **DO NOT rely on truncated results** — if you see "...and X more rows", read MORE
5. Build a DEDUPLICATION SET of all existing URLs (normalize: lowercase, remove trailing slashes)
6. Find last row with data — new leads start at lastRow + 1

### Step 2: Search for Active Business Owners

**CRITICAL: Search for POSTS not PROFILES. Posts guarantee the person is ACTIVE.**

Use Bright Data `search_engine` queries (rotate through these):

**General Business Owner Posts:**
```
site:linkedin.com/posts "business owner" 2026
site:linkedin.com/posts "practice owner" 2026
site:linkedin.com/posts "founder" "struggling with" 2026
site:linkedin.com/posts "CEO" "small business" 2026
site:linkedin.com/posts "franchise owner" 2026
site:linkedin.com/posts "service company" founder 2026
site:linkedin.com/posts "managing partner" 2026
```

**Industry-Specific Posts:**
```
site:linkedin.com/posts "dental practice" owner 2026
site:linkedin.com/posts "restaurant owner" 2026
site:linkedin.com/posts "healthcare" CEO 2026
site:linkedin.com/posts "agency founder" 2026
site:linkedin.com/posts "real estate" broker owner 2026
site:linkedin.com/posts "med spa" owner 2026
site:linkedin.com/posts "clinic" founder 2026
```

**Problem-Based Posts (people talking about issues you solve):**
```
site:linkedin.com/posts "hiring challenges" founder 2026
site:linkedin.com/posts "scaling" "business owner" 2026
site:linkedin.com/posts "revenue declining" 2026
site:linkedin.com/posts "operations" bottleneck CEO 2026
site:linkedin.com/posts "customer acquisition" founder 2026
site:linkedin.com/posts "AI" "small business" owner 2026
site:linkedin.com/posts "no-show" practice 2026
site:linkedin.com/posts "employee turnover" owner 2026
```

**Geographic (Houston/Texas priority):**
```
site:linkedin.com/posts "business owner" Houston 2026
site:linkedin.com/posts "founder" Houston 2026
site:linkedin.com/posts "practice owner" Texas 2026
site:linkedin.com/posts "CEO" Houston 2026
```

From each search result, extract:
- Person's name (from post author/snippet)
- LinkedIn profile URL (extract from post URL pattern — linkedin.com/in/username)
- Post URL (the actual result link)
- Title/company hints (from snippet)
- Industry classification (from context)
- Activity timestamp (from search result date)

### Step 3: Filter & Deduplicate

For EACH potential lead:
1. **Normalize URL** (lowercase, remove trailing slash)
2. **CHECK against dedup set** — if exists, SKIP immediately
3. **US-ONLY (CRITICAL — ZERO EXCEPTIONS):**
   - Skip ANY profile with ca.linkedin.com, uk.linkedin.com, au.linkedin.com, or any non-US LinkedIn domain
   - Skip ANY profile where the name, company, or post content indicates they are based outside the US (UK, Canada, Europe, Australia, Asia, Africa, etc.)
   - Look for US location signals: US city names, US states, US-specific references
   - When in doubt about location, SKIP the lead — do NOT include
   - WE ONLY SERVE US-BASED BUSINESSES. NO EXCEPTIONS.
4. **Post recency** — must be from last 30 days
5. **Text check** — post must have 20+ words (skip image-only posts)
6. **Add URL to dedup set** after including (prevents duplicates within batch)

### Step 4: Score Using Rubric (max 10 points)

| Criteria | Points |
|----------|--------|
| Title match (owner, founder, CEO, managing partner, practice owner) | +3 |
| Industry signal (healthcare, dental, restaurant, service, agency, real estate) | +2 |
| Activity signal (posted in last 7 days vs last 30 days) | +2 / +1 |
| Engagement (post has 50+ likes visible) | +1 |
| Location (Houston/Texas) | +1 |
| Decision maker (independent, small firm, practice owner, <200 employees) | +1 |

**Score meanings:**
- 9-10 = Hot (high priority for commenting)
- 7-8 = Warm (good target)
- 5-6 = Cool (lower priority, still valid)
- Below 5 = Skip

### Step 5: Write to Google Sheet

Use Google Workspace MCP `modify_sheet_values` to append leads:
- Start at lastRow + 1
- Write in batches of 20-30 rows max
- Fill columns A-E only (Name, Title, Company, Industry, LinkedIn Profile URL)
- Set column M (Status) = "NEW"
- Set column Q (Consecutive Inactive Count) = "0"
- Leave columns F-L and N-R empty (filled by /comment-engine)

### Step 6: Final Duplicate Verification (REQUIRED)

1. Read column E for ALL rows (from row 2 to new last row)
2. Check for any duplicate URLs in the ENTIRE column
3. If duplicates found:
   - Report which rows contain duplicates
   - Replace duplicate rows with new unique leads
   - Re-verify until 0 duplicates confirmed
4. Only report completion when verification passes

## Output Report

```
COMMENT LEADS — BATCH COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total leads added: X
Starting row: X
Ending row: X

Score Distribution:
  Hot (9-10): X leads
  Warm (7-8): X leads
  Cool (5-6): X leads

Industry Mix:
  Healthcare: X | Dental: X | Restaurant: X
  Agency: X | Service: X | Real Estate: X
  Other: X

Geography:
  Houston/Texas: X | Other US: X

Duplicates found and fixed: 0
Verification status: PASSED ✅

Spreadsheet: [link]

Next step: Run /comment-engine 10 to generate comments.
```

## Usage
```
/comment-leads 50      # Find 50 active business owners
/comment-leads 100     # Find 100
/comment-leads         # Default: 50
```
