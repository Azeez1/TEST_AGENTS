---
description: Generate verified local cleaning service leads and append to Google Sheet
arguments:
  - name: count
    description: Number of leads to generate (default 50)
    required: false
  - name: icp
    description: "Target ICP segment: all, residential, professionals, airbnb, property-managers (default: all)"
    required: false
---

# Cleaning Service Lead Generation — Lovey's Cleaning Services

Generate **$ARGUMENTS** (default: 50) NEW verified local leads for Lovey's Cleaning Services (Katy, TX) and append to the Google Sheet.

## Target Spreadsheet

- **Spreadsheet ID:** `1M7xa_qitgb0UGLB_lqMEgt9Ujs7mlwlinQSsQbVq06Q`
- **Sheet Tab:** `All Leads`
- **Google Account:** sabaazeez12@gmail.com

## Business Context

- **Company:** Lovey's Cleaning Services LLC
- **Location:** Katy, TX 77449
- **Primary Service Area (PRIORITIZE):** Katy, Cinco Ranch, Firethorne, Grand Lakes, Cane Island, Cross Creek Ranch
- **Secondary Service Area:** Cypress, Fulshear, Richmond, Brookshire, Sugar Land, Energy Corridor, Memorial (west Houston)
- **Phone:** (346) 457-9125
- **Services:** Residential, Deep Clean, Move In/Out, Post-Construction, Specialty
- **Website:** loveyscleaning.com

## 4 Tier 1 ICP Segments (FOCUS ONLY ON THESE)

| ICP # | Segment | Lead Type | Target Distribution |
|-------|---------|-----------|-------------------|
| 1 | **Recurring residential clients** (weekly/bi-weekly homeowners) | B2C | 35% of leads |
| 3 | **Busy professionals** (realtors, doctors, nurses, lawyers, remote workers) | B2C | 25% of leads |
| 5 | **Airbnb/short-term rental hosts** (1-2 units) | B2B | 20% of leads |
| 6 | **Property managers** (small firms, 2-10 units) | B2B | 20% of leads |

**If an ICP argument is provided, focus searches ONLY on that segment. Otherwise, distribute leads across all 4 segments using the target distribution above.**

## Process (MUST FOLLOW EXACTLY)

### Step 1: Read Sheet & Build Deduplication Set (CRITICAL)

Use Google Workspace MCP to:
1. Read current sheet to find the **last row with data**
2. **Read ALL existing entries from column D (Contact Name) and column F (Address/Location)** - read in chunks if needed:
   - Read D2:F500, then D501:F1000, etc. until no more data
   - **DO NOT rely on truncated results** - if you see "...and X more rows", you MUST read more
3. **Build a DEDUPLICATION SET** of all existing names + addresses:
   - Normalize names (lowercase, trim whitespace)
   - Normalize addresses (lowercase, remove suite/unit numbers)
   - Store every entry for O(1) lookup
   - This set will be used to check EVERY new lead BEFORE adding
4. New leads will start at `lastRow + 1`

**IMPORTANT:** The deduplication set must contain EVERY existing entry. If the sheet has 500+ rows, you MUST read ALL of them, not just the first batch.

### Step 2: Search-First Approach (CRITICAL - NO EXCEPTIONS)

**NEVER fabricate business names or addresses. ONLY use data extracted directly from search results.**

Run Bright Data `search_engine` queries. **Run Katy-specific queries FIRST, then expand to secondary areas only if needed to hit the target count.**

---

**ICP 1 — Recurring Residential Clients (35% of leads):**

Strategy: Find neighborhoods, HOAs, community Facebook groups, and new developments in Katy where homeowners need recurring cleaning.

```
"house cleaning" "Katy TX" reviews
"maid service" "Katy TX" -hiring -jobs
"Cinco Ranch" homeowners association Katy TX
"Grand Lakes" "Katy TX" community
"Firethorne" "Katy TX" homes
"Cane Island" "Katy TX" community homes
"Cross Creek Ranch" "Katy TX" neighborhood
"Elyson" community "Katy TX"
new home communities Katy TX 2025 2026
"neighborhood" "Katy TX" HOA contact
"master planned community" "Katy TX"
nextdoor "Katy TX" cleaning recommendations
"Facebook group" "Katy" moms community
```

What to extract: Neighborhood/HOA names, community manager contacts, Facebook group names, new development sales offices (potential partnerships for move-in cleans → recurring clients).

---

**ICP 3 — Busy Professionals (25% of leads):**

Strategy: Find individual realtors, medical/dental practices, and law firms in Katy who either need personal cleaning OR can become referral partners (realtors refer move-in/out clients).

```
"real estate agent" "Katy TX" site:linkedin.com/in
realtor "Katy TX" site:linkedin.com/in
"Keller Williams" "Katy" agent
"RE/MAX" "Katy TX" realtor
"Coldwell Banker" "Katy" agent
top realtors "Katy TX" 2025 2026
"medical practice" "Katy TX"
"dental office" "Katy TX"
"pediatrician" "Katy TX"
"dermatologist" "Katy TX"
"law firm" "Katy TX" small
"CPA" "Katy TX"
"therapist" office "Katy TX"
"veterinarian" "Katy TX"
```

What to extract: Name, title, brokerage/practice name, LinkedIn URL, office address. Realtors are DUAL-PURPOSE leads: personal cleaning clients AND referral partners for move-in/out cleans.

---

**ICP 5 — Airbnb / Short-Term Rental Hosts (20% of leads):**

Strategy: Find actual Airbnb/VRBO listings in Katy area, then identify hosts. Also search for STR hosts on LinkedIn and local host groups.

```
site:airbnb.com "Katy" Texas
site:airbnb.com "Cinco Ranch" Texas
site:airbnb.com "Cypress" Texas near Katy
site:vrbo.com "Katy" Texas
"short term rental" "Katy TX"
"vacation rental" "Katy TX"
"Airbnb host" "Katy" site:linkedin.com/in
"Airbnb host" "Houston" west site:linkedin.com/in
"Airbnb superhost" "Houston" "Katy"
"short term rental" host "Katy" OR "Cinco Ranch" OR "Fulshear"
"STR" "property" "Katy TX"
"turnover cleaning" "Katy" OR "Houston"
```

What to extract: Listing titles, host names (when visible), property locations, number of listings per host. Hosts with 2+ listings are higher priority (more recurring revenue).

---

**ICP 6 — Property Managers (20% of leads):**

Strategy: Find small property management companies and independent landlords in Katy managing rental units. These need move-in/out cleans and can become recurring clients.

```
"property management" "Katy TX"
"property manager" "Katy TX" site:linkedin.com/in
"rental properties" management "Katy TX"
"property management company" "Katy" OR "Cinco Ranch"
"apartment" management "Katy TX" small
landlord "rental property" "Katy TX"
"property management" "Katy TX" site:yelp.com
"property management" "Katy TX" site:google.com/maps
"real estate investor" "Katy TX" rental site:linkedin.com/in
"we manage" rental "Katy TX"
"move in" "move out" cleaning "Katy" property manager
```

What to extract: Company name, manager name, number of units managed, office address, phone, website. Prioritize smaller firms (2-20 units) — they're more accessible and more likely to try a new cleaner.

---

From each search result, extract:
- Business/Contact name (from result title/snippet) - VERIFIED
- Address or location (from snippet/result)
- Phone number (when visible in snippet)
- Website or LinkedIn URL (from result link)
- Category/ICP segment
- Context clues (size, reviews, number of units/listings, activity)

### Step 2B: Contact Enrichment — Scrape for Email & Phone (REQUIRED)

**For every lead that has a website URL, scrape the site to find email and phone.**

Use Bright Data `scrape_as_markdown` on the lead's website (NOT LinkedIn — LinkedIn blocks scraping). Target these pages in order:
1. Homepage (often has phone in header/footer)
2. `/contact`, `/contact-us`, `/about` pages

**Extract from scraped content:**
- **Phone numbers:** Look for patterns like (XXX) XXX-XXXX, XXX-XXX-XXXX, XXX.XXX.XXXX
- **Email addresses:** Look for patterns like name@domain.com, info@, contact@, hello@
- **Physical address:** Street address if not already captured
- **Owner/manager name:** If visible on About page

**Extraction rules:**
- If multiple phones found, prefer the one labeled "main", "office", or "call"
- If multiple emails found, prefer info@, contact@, or owner's personal email over generic noreply@
- Skip fax numbers
- Skip emails that are clearly automated (noreply@, donotreply@, support@)

**For LinkedIn profiles (ICP 3 professionals):**
- Do NOT scrape LinkedIn (it blocks Bright Data)
- Instead, search Google for their name + business: `"John Smith" realtor "Katy TX" email phone`
- Or search their brokerage/practice website for contact info

**Rate limiting:** Scrape max 5 sites in parallel to avoid getting blocked. Wait 2-3 seconds between batches.

### Step 2C: Validate Contact Info (REQUIRED)

**Before adding ANY lead, validate the phone and email:**

**Phone validation:**
- Must be 10 digits (US format)
- Must start with valid US area code (NOT 000, 111, 555)
- Houston/Katy area codes are preferred: 281, 346, 713, 832, 936
- Remove formatting, store as (XXX) XXX-XXXX in the sheet
- If phone fails validation → still add lead but put "PHONE UNVERIFIED" in Notes column

**Email validation:**
- Must match pattern: something@domain.tld
- Domain must have a valid TLD (.com, .net, .org, .io, etc.)
- Must NOT be: noreply@, donotreply@, example@, test@
- Must NOT be a competitor cleaning service email
- If email fails validation → still add lead but put "EMAIL UNVERIFIED" in Notes column

**If NEITHER phone nor email is found after scraping:**
- Still add the lead if score >= 7 (hot leads are worth manual research)
- Add "NO CONTACT INFO - NEEDS MANUAL LOOKUP" in Notes column
- If score < 7, SKIP the lead (not worth pursuing without contact info)

### Step 3: Filter & Deduplicate Leads (BEFORE ADDING)

For EACH potential lead from search results:

1. **Normalize the name and address** (lowercase, trim)
2. **CHECK AGAINST DEDUPLICATION SET** - Is this name+address already in the set?
   - If YES: **SKIP this lead entirely** - do not add
   - If NO: Continue to next checks
3. **Geography check — KATY FIRST:**
   - Katy proper, Cinco Ranch, Firethorne, Grand Lakes, Cane Island, Cross Creek = PRIORITY (score bonus)
   - Cypress, Fulshear, Richmond, Brookshire, Sugar Land, Energy Corridor, Memorial = ACCEPTABLE
   - Anything else = SKIP (outside service area)
4. **Relevance check** - Must match one of the 4 Tier 1 ICP segments
   - SKIP: job postings, competitor cleaning services, irrelevant businesses, national chains
5. **Add to deduplication set** after deciding to include (prevents duplicates within new batch)

**CRITICAL:** The deduplication check happens BEFORE scoring, BEFORE adding to the sheet. If an entry exists in your set, skip it immediately.

### Step 4: Score Using Rubric (max 10 points)

| Criteria | Points |
|----------|--------|
| ICP match (clearly fits one of the 4 Tier 1 segments) | +3 |
| Location: Katy proper / Cinco Ranch / master-planned community | +2 |
| Location: Secondary area (Cypress, Fulshear, Sugar Land, etc.) | +1 |
| Recurring revenue potential (weekly/bi-weekly opportunity, multiple units, repeat turnovers) | +2 |
| Contact info available (phone, email, or website found) | +1 |
| Decision-maker accessible (owner/manager identifiable, not a corporation) | +1 |
| Referral multiplier (realtors, PM companies that can send multiple clients) | +1 |

**Note:** Location scoring is either +2 (Katy) OR +1 (secondary) — not both. Max score = 10.

**Score Meanings:**
- 9-10 = Hot — High-value, contact immediately
- 7-8 = Warm — Good fit, schedule outreach
- 5-6 = Cool — Worth a try, lower priority

**Minimum score to add: 5.** Skip anything below 5.

### Step 5: Write to Google Sheet

Use Google Workspace MCP `modify_sheet_values` to append leads:
- Start at `lastRow + 1` (NEVER hardcode row numbers)
- Write in batches of 20-30 rows max
- Use 12-column format:

| Column | Content |
|--------|---------|
| A | ICP # (1, 3, 5, or 6) |
| B | ICP Label ("Residential", "Busy Professional", "Airbnb Host", "Property Manager") |
| C | Lead Type (B2B or B2C) |
| D | Contact Name (person or business) |
| E | Business Name (if applicable — brokerage, PM company, etc.) |
| F | Address / Location |
| G | Phone (validated format: (XXX) XXX-XXXX) |
| H | Email (validated format: name@domain.com) |
| I | Website / LinkedIn URL |
| J | Lead Score (5-10) |
| K | Notes (# units, # listings, reviews, referral potential, contact status) |
| L | Outreach Status (leave blank — for manual tracking) |
| M | Date Added (today's date: YYYY-MM-DD) |

### Step 6: Final Duplicate Verification (REQUIRED)

**After ALL leads are written, perform mandatory verification:**

1. Read columns D+F for ALL rows (from row 2 to the new last row)
2. Check for any duplicate name+address combos in the ENTIRE sheet
3. If duplicates found:
   - Report which specific rows contain duplicates
   - Identify the original row and the duplicate row
   - Replace duplicate rows with new unique leads from additional searches
   - Re-run verification until **0 duplicates** confirmed
4. **Only report completion when verification passes with 0 duplicates**

## Output Report

After completion AND verification, report:
- Total leads added
- Starting row number -> Ending row number
- **ICP distribution:**
  - ICP 1 (Residential): X leads
  - ICP 3 (Professionals): X leads
  - ICP 5 (Airbnb): X leads
  - ICP 6 (Property Managers): X leads
- **Geography split:** X in Katy proper, Y in secondary areas
- Score distribution (how many 10s, 9s, 8s, etc.)
- **Lead type split:** X B2B leads, Y B2C leads
- **Duplicates found and fixed:** X (should be 0 if process followed correctly)
- **Verification status:** PASSED (only after confirming 0 duplicates)
- Link to spreadsheet
- **Top 5 hottest leads** (score 9-10) with brief description

## Outreach Playbook (Display After Report)

| ICP | Channel | Message Angle | Timing |
|-----|---------|--------------|--------|
| **Residential** | Neighborhood Facebook groups, Nextdoor, door flyers | "Your neighbors love us — here's 15% off your first clean" | Post weekday mornings when moms are scrolling |
| **Busy Professionals** | LinkedIn DM, email, or walk into their office | "We handle the cleaning so you can focus on closing deals / seeing patients" | Tuesday-Thursday, business hours |
| **Realtors (subset of ICP 3)** | LinkedIn + in-person at open houses | "Partner with us for move-in/out cleans — your clients will love the referral" | Ongoing — realtors are referral engines |
| **Airbnb Hosts** | Direct message via Airbnb host forums, Facebook STR groups, LinkedIn | "Fast turnover cleans — same-day availability, consistent quality" | After they post about needing a cleaner, or cold outreach |
| **Property Managers** | Cold call, email, walk-in to office | "Turnover cleaning packages for your units — volume discounts available" | Monday-Wednesday mornings |

## Common Duplicate Causes & Prevention

| Cause | Prevention |
|-------|------------|
| Truncated MCP reads | Read ALL rows in chunks |
| Checking after adding | Check BEFORE adding each lead |
| Same business in multiple searches | Add to dedup set as you go |
| Off-by-one row errors | Final verification catches these |
| Same business different address format | Normalize addresses before comparing |

## Usage Examples

```
/lead-gen-cleaning 50                    # Generate 50 leads across all 4 ICPs
/lead-gen-cleaning 30 residential        # Generate 30 recurring residential leads
/lead-gen-cleaning 20 professionals      # Generate 20 busy professional leads
/lead-gen-cleaning 25 airbnb             # Generate 25 Airbnb host leads
/lead-gen-cleaning 20 property-managers  # Generate 20 property manager leads
/lead-gen-cleaning 100                   # Generate 100 leads across all 4 ICPs
/lead-gen-cleaning                       # Default: 50 leads, all 4 ICPs
```
