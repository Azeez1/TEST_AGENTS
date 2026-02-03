---
description: Generate verified fractional executive leads and append to Google Sheet
arguments:
  - name: count
    description: Number of leads to generate (default 100)
    required: false
---

# Fractional Executive Lead Generation

Generate **$ARGUMENTS** (default: 100) NEW verified fractional executive leads and append to the Google Sheet.

## Target Spreadsheet

- **Spreadsheet ID:** `1XhuEwrC59NIiAkKnVEBTijeCf4U6OHg3SXtWovP-F38`
- **Google Account:** sabaazeez12@gmail.com

## Target Audience

- Fractional COOs and CFOs
- EOS Integrators and Implementers
- Operations Consultants/Advisors
- Interim executives
- Business operations consultants

**Profile:** Independent or small-firm decision makers serving SMBs/mid-market with scaling, transformation, operational improvements

## Process (MUST FOLLOW EXACTLY)

### Step 1: Read Sheet & Build Deduplication Set (CRITICAL)

Use Google Workspace MCP to:
1. Read current sheet to find the **last row with data**
2. **Read ALL existing LinkedIn URLs from column E** - read in chunks if needed:
   - Read E2:E500, then E501:E1000, etc. until no more data
   - **DO NOT rely on truncated results** - if you see "...and X more rows", you MUST read more
3. **Build a DEDUPLICATION SET** of all existing URLs:
   - Normalize URLs (lowercase, remove trailing slashes)
   - Store every URL for O(1) lookup
   - This set will be used to check EVERY new lead BEFORE adding
4. New leads will start at `lastRow + 1`

**IMPORTANT:** The deduplication set must contain EVERY existing URL. If the sheet has 500+ rows, you MUST read ALL of them, not just the first batch.

### Step 2: Search-First Approach (CRITICAL - NO EXCEPTIONS)

**NEVER construct LinkedIn URLs from names. ONLY use URLs extracted directly from search results.**

Run Bright Data `search_engine` queries:
```
"Fractional COO" site:linkedin.com/in
"Fractional CFO" site:linkedin.com/in
"EOS Implementer" site:linkedin.com/in
"EOS Integrator" site:linkedin.com/in
"Operations Consultant" fractional site:linkedin.com/in
"Fractional Integrator" site:linkedin.com/in
"Fractional Executive" operations site:linkedin.com/in
"Interim COO" site:linkedin.com/in
"Fractional COO" scaling site:linkedin.com/in
"Fractional CFO" growth site:linkedin.com/in
"Fractional COO" healthcare site:linkedin.com/in
"Fractional CFO" manufacturing site:linkedin.com/in
```

Additional geographic searches to expand pool:
```
"Fractional COO" Texas site:linkedin.com/in
"Fractional CFO" California site:linkedin.com/in
"Fractional COO" New York site:linkedin.com/in
"Fractional COO" Florida site:linkedin.com/in
"EOS Implementer" Ohio site:linkedin.com/in
"Fractional CFO" Nashville site:linkedin.com/in
"Fractional COO" Seattle site:linkedin.com/in
"Fractional COO" Boston site:linkedin.com/in
"Fractional CFO" Phoenix site:linkedin.com/in
"Fractional COO" Chicago site:linkedin.com/in
```

From each search result, extract:
- Actual LinkedIn URL (from result link) - VERIFIED
- Name and title (from snippet)
- Location hint (from snippet)
- Activity timestamp (when shown)

### Step 3: Filter & Deduplicate Leads (BEFORE ADDING)

For EACH potential lead from search results:

1. **Normalize the URL** (lowercase, remove trailing slash)
2. **CHECK AGAINST DEDUPLICATION SET** - Is this URL already in the set?
   - If YES: **SKIP this lead entirely** - do not add
   - If NO: Continue to next checks
3. **US-only** - Skip profiles from Canada, UK, or other countries (check URL prefix like `ca.linkedin.com`, `uk.linkedin.com`)
4. **Verify activity** - Use search timestamps when available (e.g., "2 months ago")
5. **Add URL to deduplication set** after deciding to include (prevents duplicates within new batch)

**CRITICAL:** The deduplication check happens BEFORE scoring, BEFORE adding to the sheet. If a URL exists in your set, skip it immediately.

### Step 4: Score Using Rubric (max 10 points)

| Criteria | Points |
|----------|--------|
| Title match (Fractional COO/CFO, EOS Integrator, Ops Consultant) | +3 |
| Industry signal (Healthcare, GovCon, finance, manufacturing) | +2 |
| Pain keywords ("scaling", "growth", "transformation", "operations") | +2 |
| Company size (SMB/mid-market focus) | +1 |
| Location (US-based) | +1 |
| Decision proximity (Independent or small firm) | +1 |

**Score Meanings:**
- 9-10 = Hot (Green)
- 8 = Warm (Yellow)
- 7 = Cool (Red)

### Step 5: Write to Google Sheet

Use Google Workspace MCP `modify_sheet_values` to append leads:
- Start at `lastRow + 1` (NEVER hardcode row numbers)
- Write in batches of 20-30 rows max
- Use 10-column format:

| Column | Content |
|--------|---------|
| A | Name |
| B | Title |
| C | Company |
| D | Location |
| E | LinkedIn URL |
| F | Category |
| G | Pain Score (7-10) |
| H | Decision Proximity |
| I | Notes |
| J | Date of Initial Comment (leave blank) |

### Step 6: Final Duplicate Verification (REQUIRED)

**After ALL leads are written, perform mandatory verification:**

1. Read column E for ALL rows (from row 2 to the new last row)
2. Check for any duplicate URLs in the ENTIRE column
3. If duplicates found:
   - Report which specific rows contain duplicates
   - Identify the original row and the duplicate row
   - Replace duplicate rows with new unique leads from additional searches
   - Re-run verification until **0 duplicates** confirmed
4. **Only report completion when verification passes with 0 duplicates**

**Verification Query:**
```
For each URL in new rows (516+), check:
- Does this exact URL appear anywhere in rows 2-515?
- If yes, this is a duplicate that must be replaced
```

## Output Report

After completion AND verification, report:
- Total leads added
- Starting row number
- Ending row number
- Score distribution (how many 10s, 9s, 8s, etc.)
- **Duplicates found and fixed: X** (should be 0 if process followed correctly)
- **Verification status: PASSED** (only after confirming 0 duplicates)
- Link to spreadsheet

## Why This Process Works

| Approach | URL Accuracy | Use? |
|----------|-------------|------|
| Construct from names | ~60-70% | NO |
| Guess patterns | ~50% | NO |
| **Search-extracted** | **100%** | YES |

URLs from search results are real because they exist in Google's index.

## Common Duplicate Causes & Prevention

| Cause | Prevention |
|-------|------------|
| Truncated MCP reads | Read ALL rows in chunks |
| Checking after adding | Check BEFORE adding each lead |
| Same person in multiple searches | Add to dedup set as you go |
| Off-by-one row errors | Final verification catches these |

## Usage Examples

```
/lead-gen-fractional 100     # Generate 100 new leads
/lead-gen-fractional 50      # Generate 50 new leads
/lead-gen-fractional         # Default: 100 leads
```
