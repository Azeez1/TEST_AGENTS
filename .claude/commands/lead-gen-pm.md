---
description: Generate verified Property Management operations-leader leads and append to Google Sheet
arguments:
  - name: count
    description: Number of leads to generate (default 30)
    required: false
---

# Property Management Ops-Leader Lead Generation

Generate **$ARGUMENTS** (default: 30) NEW verified property-management operations-leader leads and append to the Google Sheet. This is the Dux Machina beachhead ICP (see `DUX_MACHINA/funnel.md`).

## Target Spreadsheet

- **Spreadsheet ID:** `1E9xutMC7zaJSdrgvUypBoc0JgEeSFA-g0uap5AK1_Ws`
- **Sheet title:** Dux Machina — Property Management Leads (Ops)
- **Google Account:** sabaazeez12@gmail.com

## Target Audience (ICP #1 — Property Management)

Operations decision-makers at **mid-size US property management firms** ($5M–$25M revenue, ~50–250 employees, multi-location; residential / multifamily / commercial PM). Titles:
- COO / Chief Operating Officer
- VP of Operations
- Director of Operations
- Director of Property Management
- Regional Operations Manager / Regional Director of Operations

**EXCLUDE (hard filters):**
- Enterprise giants: Greystar, CBRE, JLL, FirstService Residential, Morgan Properties, Asset Living, AvalonBay, Fairfield Residential, Cushman & Wakefield (they have internal IT + procurement = not our ICP)
- PropTech / software companies (they build their own)
- Non-US profiles (skip `ca.linkedin.com`, `uk.linkedin.com`, etc.)
- `/jobs/` listing URLs (not real profiles); individual landlords

## Process (MUST FOLLOW EXACTLY)

### Step 1: Read Sheet & Build Deduplication Set (CRITICAL)
1. Read the sheet to find the **last row with data**.
2. Read ALL existing LinkedIn URLs from **column E** in chunks (E2:E500, E501:E1000, …) until no more data. DO NOT rely on truncated results.
3. Build a **deduplication set**: normalize each URL (lowercase, strip trailing slash) for O(1) lookup. Check EVERY new lead against this set BEFORE adding.
4. New leads start at `lastRow + 1`.

### Step 2: Search-First Approach (CRITICAL — NO EXCEPTIONS)
**NEVER construct LinkedIn URLs from names. ONLY use URLs extracted directly from search results.**

Run Bright Data `search_engine` queries (use `search_engine_batch` if available; Google engine).
**LESSON LEARNED — lead with the niche term, NOT the bare title.** Bare `"VP of Operations"` / `"Chief Operating Officer"` queries get hijacked by political/brand noise (JD Vance, VICE, Chief.com). Phrase term-first:

```
"Director of Operations" "property management" site:linkedin.com/in
"Director of Property Management" site:linkedin.com/in
linkedin.com/in "VP of Operations" multifamily property management
linkedin.com/in "COO" property management
"Director of Operations" multifamily site:linkedin.com/in
"Operations Director" "property management" site:linkedin.com/in
"Regional Director of Operations" property management site:linkedin.com/in
```

Geographic expansions (rotate to widen pool):
```
"COO" "property management" Texas site:linkedin.com/in
"Director of Operations" "property management" Florida site:linkedin.com/in
"VP of Operations" "property management" California site:linkedin.com/in
"Director of Operations" "property management" Georgia site:linkedin.com/in
"COO" "property management" Arizona site:linkedin.com/in
```

From each result extract (real data only): verified LinkedIn URL (from the link), Name, Title, Company (if shown), Location hint.

### Step 3: Filter & Deduplicate (BEFORE ADDING)
For each potential lead: normalize URL → check dedup set (skip if present) → US-only → apply EXCLUDE list → add URL to set after deciding to include.

### Step 4: Score Using Rubric (max 10)
| Criteria | Points |
|----------|--------|
| Title match (COO / VP Ops / Dir Ops / Dir PM / Regional Ops) | +3 |
| Property-management / multifamily / real-estate-ops signal | +2 |
| Scale keywords (multi-location, # units/markets, portfolio growth, operations) | +2 |
| Company size (mid-market $5–25M, not enterprise) | +1 |
| US-based | +1 |
| Decision proximity (exec / ops leader) | +1 |

Keep only **7+**. 9-10 = Hot, 8 = Warm, 7 = Cool.

### Step 5: Write to Google Sheet
Use `modify_sheet_values` to append, starting at `lastRow + 1` (NEVER hardcode), batches of 20-30 rows. 10-column format:

| Col | Content |
|-----|---------|
| A | Name |
| B | Title |
| C | Company |
| D | Location |
| E | LinkedIn URL |
| F | Category (residential / multifamily / commercial PM) |
| G | Score (7-10) |
| H | Decision Proximity |
| I | Notes (flag if company unconfirmed) |
| J | Date of Initial Comment (leave blank — outreach tracking) |

### Step 6: Final Duplicate Verification (REQUIRED)
After writing, read column E for ALL rows, check for duplicate URLs across the ENTIRE column. If found, replace with new unique leads and re-verify until **0 duplicates**.

## Output Report
- Total leads added, starting/ending row
- Score distribution, title mix
- Duplicates found and fixed: X (should be 0)
- Verification status: PASSED
- Link to spreadsheet

## Why Search-First
URLs from search results are real (they exist in Google's index). Constructed/guessed URLs are ~50-70% accurate — never use them.

## Usage
```
/lead-gen-pm 30     # 30 new PM ops-leader leads
/lead-gen-pm 50     # 50 new leads
/lead-gen-pm        # default: 30
```
