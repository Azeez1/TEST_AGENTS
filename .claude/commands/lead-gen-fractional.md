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

### Step 1: Read Sheet First (CRITICAL)

Use Google Workspace MCP to:
1. Read current sheet to find the **last row with data**
2. Get ALL existing LinkedIn URLs from column E for deduplication
3. New leads will start at `lastRow + 1`

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

From each search result, extract:
- Actual LinkedIn URL (from result link) - VERIFIED
- Name and title (from snippet)
- Location hint (from snippet)
- Activity timestamp (when shown)

### Step 3: Filter Leads

- **US-only** - Skip profiles from Canada, UK, or other countries
- **No duplicates** - Check each URL against existing column E URLs
- **Verify activity** - Use search timestamps when available (e.g., "2 months ago")

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

## Output Report

After completion, report:
- Total leads added
- Starting row number
- Ending row number
- Score distribution (how many 9s, 8s, etc.)
- Link to spreadsheet

## Why This Process Works

| Approach | URL Accuracy | Use? |
|----------|-------------|------|
| Construct from names | ~60-70% | NO |
| Guess patterns | ~50% | NO |
| **Search-extracted** | **100%** | YES |

URLs from search results are real because they exist in Google's index.

## Usage Examples

```
/lead-gen-fractional 100     # Generate 100 new leads
/lead-gen-fractional 50      # Generate 50 new leads
/lead-gen-fractional         # Default: 100 leads
```
