---
description: Generate verified Houston-metro leasing office leads (commercial + flex-space) and append to Google Sheet
arguments:
  - name: count
    description: Number of leads to generate (default 100)
    required: false
---

# Leasing Offices Lead Generation (Houston Metro)

Generate **$ARGUMENTS** (default: 100) NEW verified leasing office leads and append to the Google Sheet.

## Target Spreadsheet

- **Spreadsheet ID:** `1aKraLljvYPr2h9RmcDr_U2iW7aarvMAjPAo_p6UmHIk`
- **Sheet tab:** `Leads`
- **Google Account:** sabaazeez12@gmail.com

## Target Audience

- **Property Types:**
  - (a) Commercial real estate / office space leasing (CRE brokers, office towers, business parks)
  - (c) Coworking / flex-space operators (WeWork-style, executive suites, shared office)
- **EXCLUDE:** Multifamily/apartment leasing, retail-only, industrial-only, residential

- **Target Roles:**
  - Leasing Manager
  - Property Manager
  - Senior/Regional Leasing Manager
  - General Manager (coworking/flex space)
  - Community Manager (coworking — only if they hold leasing/sales authority)

- **Geography (HARD FILTER):** Houston, Katy, Cypress, Spring (TX). Skip anything outside Houston metro.

- **Core Qualifier:** The property must lease to **businesses as tenants** (not individuals). This is the main criterion — we are targeting leasing offices whose book of tenants IS a book of businesses. Commercial office and coworking/flex both qualify; residential/multifamily does not.

## Process (MUST FOLLOW EXACTLY)

### Step 1: Read Sheet & Build Deduplication Set

Use Google Workspace MCP to:
1. Read current sheet to find the last row with data.
2. Read ALL existing LinkedIn URLs from column E in chunks (E2:E500, E501:E1000, etc.).
3. Build a deduplication SET (normalized: lowercase, no trailing slash) for O(1) lookup.
4. New leads start at `lastRow + 1`.

### Step 2: Search-First Approach (NO EXCEPTIONS)

**NEVER construct LinkedIn URLs from names. Only use URLs extracted from live search results.**

Run Bright Data `search_engine` queries (mix role × property-type × city):

```
"Leasing Manager" Houston office site:linkedin.com/in
"Leasing Manager" Katy site:linkedin.com/in
"Leasing Manager" Cypress TX site:linkedin.com/in
"Leasing Manager" Spring TX site:linkedin.com/in
"Property Manager" Houston commercial site:linkedin.com/in
"Property Manager" Houston office building site:linkedin.com/in
"Commercial Leasing Manager" Houston site:linkedin.com/in
"Senior Leasing Manager" Houston site:linkedin.com/in
"Regional Leasing Manager" Texas Houston site:linkedin.com/in
"General Manager" coworking Houston site:linkedin.com/in
"Community Manager" WeWork Houston site:linkedin.com/in
"Community Manager" "Common Desk" Houston site:linkedin.com/in
"General Manager" "Industrious" Houston site:linkedin.com/in
"Leasing" "Regus" Houston site:linkedin.com/in
"Flex space" Houston manager site:linkedin.com/in
"Executive Suites" Houston manager site:linkedin.com/in
"Coworking" Houston manager site:linkedin.com/in
"Property Manager" Katy TX office site:linkedin.com/in
"Property Manager" Cypress TX office site:linkedin.com/in
"Property Manager" Spring TX office site:linkedin.com/in
```

Extract from each result: actual LinkedIn URL, name, title, employer, location hint, any activity signal.

### Step 3: Filter & Deduplicate (BEFORE ADDING)

For each candidate:
1. Normalize URL. If in dedup set → SKIP.
2. **Geography gate:** Location must be Houston / Katy / Cypress / Spring (or explicit Houston-metro suburb). Otherwise SKIP.
3. **Property type gate:** Employer must be commercial office OR coworking/flex-space. If multifamily/apartment/retail/industrial → SKIP.
4. **Tenant gate:** Confirm the property leases to businesses (visible in title, company, or snippet). If unclear, keep but flag in Notes.
5. Add URL to dedup set after inclusion.

### Step 4: Score Using Rubric (max 10)

| Criteria | Points |
|----------|--------|
| Title match (Leasing Mgr / Property Mgr / GM at flex-space) | +3 |
| Employer is commercial office OR coworking/flex (business tenants) | +3 |
| Houston / Katy / Cypress / Spring explicitly | +2 |
| Portfolio signal (manages multiple properties or a named Class A building) | +1 |
| Decision authority (Manager+ title, not coordinator/assistant) | +1 |

Score meanings: 9–10 Hot (Green) · 8 Warm (Yellow) · 7 Cool (Red). Drop anything below 7.

### Step 5: Write to Google Sheet

Use `modify_sheet_values` to append, starting at `lastRow + 1`. Batches of 20–30 rows.

11-column format:

| Col | Content |
|-----|---------|
| A | Name |
| B | Title |
| C | Company |
| D | Location (Houston / Katy / Cypress / Spring / metro) |
| E | LinkedIn URL |
| F | Property Type (Commercial Office / Coworking / Flex) |
| G | Tenant Score (7–10) |
| H | Portfolio Signal (e.g., "Class A Galleria tower", "3 flex locations") |
| I | Notes |
| J | Date of Initial Contact (leave blank) |
| K | Company Phone (Houston office main line, scraped from company website — REQUIRED) |

### Step 5b: Company Phone Enrichment (REQUIRED)

For every new lead, before final verification:
1. Identify the Houston office main line for the lead's employer
2. Use Bright Data `scrape_as_markdown` on the firm's `/contact`, `/locations`, `/offices/houston`, or equivalent page
3. Extract the Houston office main phone line (format: `(xxx) xxx-xxxx`)
4. For coworking/flex brands (Regus, WeWork, Venture X, Industrious, Spaces, Life Time Work), scrape the specific Houston location page
5. If Houston line isn't published, use corporate HQ main line and note "HQ line (no Houston direct)" in column I
6. Cache phones by company — one lookup per firm, reuse across all leads at that firm

Column K must be populated on every row. "Not found" is acceptable only after a verified scrape attempt — flag in Notes.

### Step 6: Final Duplicate Verification

After writing: read column E end-to-end, confirm 0 duplicates. If any found, replace with fresh search results and re-verify.

## Output Report

- Total leads added
- Starting / ending row numbers
- Score distribution (10s / 9s / 8s / 7s)
- Property-type split (Commercial vs Coworking)
- City split (Houston / Katy / Cypress / Spring)
- Duplicates found & fixed (should be 0)
- Verification status: PASSED
- Spreadsheet link

## Usage

```
/lead-gen-leasing 100    # 100 new leads
/lead-gen-leasing 50     # 50 new leads
/lead-gen-leasing        # default 100
```
