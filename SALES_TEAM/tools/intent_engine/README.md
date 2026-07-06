# Dux Machina Intent Signal Engine

Scans public data sources for buying-intent signals across 6 avenues (trucking, property_mgmt, mechanical, manufacturing, dead_listings, pe_distress) in 2 metros (Houston, Atlanta), resolves entities, scores them, and exports ranked prospect lists (CSV + Google Sheet). Pure Python, no LLM calls, no sending. Outreach drafting is a separate human-approved step (`/intent-scan` command).

## v2 scoring: EXPECTED_VALUE (pain x timing x ability-to-pay x deal-size)

A wound is not a customer. v2 ranks by:

```
EXPECTED_VALUE = pain_norm x timing x ability_to_pay x (0.5 + 0.5*deal_size)   in 0..2
```

- `pain_norm` (0..1) = v1 pain score / (pain + hot_threshold); v1 pain now has a PER-TYPE CAP (first 3 signals of a type count fully, the rest diminish geometrically) so 20 identical bulk-filed liens cannot dominate diverse distress.
- `timing` (1..2) = receptiveness-window boost (`common/timing.py`): trucking insurance renewal (policy effective + 12mo), contractor permit-growth window, eviction-spike window, dead-listing DOM-180 crossing, OSHA abatement deadline, distress acceleration. No window = exactly 1.0.
- `ability_to_pay` (0..1) = `common/solvency.py`: SIZE (fleet/mileage, HCAD parcels, permit volume, OSHA employees) + CREDIT (SBA GrossApproval bucket, GA UCC presence — TX UCC/SOS is paywalled, so credit is GA-only) + a distress-density guardrail (few wounds + sizable = solvent; many stacked severe = dying). **Missing pay data = 0.5 neutral + `pay_data=unknown`, the row is NEVER dropped.**
- `deal_size` (0..1) = the SIZE proxy; balanced weighting — its EV factor spans only 0.5..1.0 so an acute-pain company in its window can outrank a big calm one.

Two funnel outputs, ranked by EV: **CUSTOMERS** (trucking, property_mgmt, mechanical, manufacturing) and **ACQUISITIONS** (dead_listings, pe_distress) — `intent_customers_{date}.csv` / `intent_acquisitions_{date}.csv` + same-named sheet tabs. Outcome log for later weight tuning: `python -m common.outcomes record <entity_key> <stage>` (drafted/replied/meeting/won...).

Known limits (do not mistake the list for the market): sources are selection-biased (OSHA = inspected-only, SBA = borrowers-only, listings = already-selling); solvency data can be stale (confidence decays with a 2-year half-life, stamped per signal); manufacturing pay coverage is inspection-gated so `pay_data=unknown` is common there.

v2 regression test: `python fixtures/v2_test.py`

## Layout

```
intent_engine/
  config.py            paths + env loading (data home = ~/.dux_intent, OUTSIDE OneDrive)
  signal_registry.json avenues, signal weights, hot thresholds, collectors_enabled map
  common/              http (retry/soda/ckan), normalize, store (SQLite), score (decay+stacking)
  collectors/          one module per source_id (see status table below)
  resolve.py           entity resolution (cross-avenue merge at conf >= 0.9)
  export_csv.py        per-avenue/metro CSVs + combined hotlist
  export_sheet.py      INTENT_SIGNALS spreadsheet (tabs per avenue, green hot rows)
  bootstrap_sheet.py   one-time spreadsheet creation
  run_intent_scan.py   orchestrator CLI
  fixtures/            synthetic_test.py + one raw sample payload per collector
```

Data home: `~/.dux_intent/` (SQLite `intent.db`, `cache/` for big CSVs, `.env` for keys). Deliberately outside OneDrive: SQLite corrupts under sync.

## Setup (one time)

1. Deps (already installed into `C:\Python314`): `pip install requests pandas python-dotenv beautifulsoup4 google-api-python-client google-auth`
2. Keys in `~/.dux_intent/.env` (never in the repo):
   - `DOL_API_KEY` - free, register at https://dataportal.dol.gov/registration (enables osha_dol)
   - `BRIGHTDATA_API_TOKEN` + `BRIGHTDATA_ZONE=mcp_unlocker` - from the Bright Data dashboard (enables listings_bizbuysell; other listing sites are plain fetch)
   - `SOCRATA_APP_TOKEN` - optional, raises rate limits for FMCSA/TX WARN pulls
   - `INTENT_SPREADSHEET_ID` - printed by bootstrap_sheet.py (step 3)
3. Google Sheet: needs valid google-workspace credentials at `~/.google_workspace_mcp/credentials/sabaazeez12@gmail.com.json` WITH the spreadsheets scope. If auth is stale (invalid_grant / invalid_scope): delete that json, kill port 8000, restart Claude Code, re-auth the google-workspace MCP, then run:
   `python SALES_TEAM\tools\intent_engine\bootstrap_sheet.py`
   and paste the printed id into `~/.dux_intent/.env` as `INTENT_SPREADSHEET_ID=...`
4. Weekly schedule (optional): `powershell -ExecutionPolicy Bypass -File scripts\register_intent_task.ps1` registers "DuxOS intent-engine weekly" (Mon 07:00, StartWhenAvailable, python only - never claude.exe). Kill switch: add 'intent-engine' to `$disabledTasks` in `scripts/run_intent_engine.ps1`.

## How to run

```
# weekly incremental scan (default 7-day window), all avenues/metros, with sheet
python SALES_TEAM\tools\intent_engine\run_intent_scan.py

# no sheet, wider window, specific metros/avenues
python SALES_TEAM\tools\intent_engine\run_intent_scan.py --no-sheet --since-days 30 --metros houston,atlanta
python SALES_TEAM\tools\intent_engine\run_intent_scan.py --avenues trucking pe_distress

# deep backfill (permits_houston growth signals need ~15 months of history)
python SALES_TEAM\tools\intent_engine\run_intent_scan.py --backfill-days 450 --avenues mechanical --no-sheet

# safe rehearsal: in-memory store + synthetic signals, CSVs to outputs/prospecting/dry_run/
python SALES_TEAM\tools\intent_engine\run_intent_scan.py --dry-run --no-sheet

# core regression test (synthetic fixtures, throwaway store)
python SALES_TEAM\tools\intent_engine\fixtures\synthetic_test.py

# any collector standalone (30-day throwaway-store self test, writes fixture sample)
python -m collectors.trucking_fmcsa --self-test     (run from the intent_engine dir)
```

Outputs land in `SALES_TEAM/outputs/prospecting/`: `intent_{avenue}_{metro}_{date}.csv` per avenue/metro, `intent_hotlist_{date}.csv` (all hot rows), and the two v2 funnel lists `intent_customers_{date}.csv` + `intent_acquisitions_{date}.csv` ranked by expected_value. Then `/intent-scan` in Claude Code drafts a full 4-touch, evidence-cited sequence per top target into `SALES_TEAM/outputs/outreach/intent_drafts_{date}.md`.

**Outbound is DRAFT-ONLY.** `/intent-scan` never sends anything; every touch sits in the queue file with APPROVE/EDIT/SKIP checkboxes and EZ approves each personally. **Do NOT blast sequences from the primary Gmail (sabaazeez12@gmail.com)** - cold volume from the primary inbox is a deliverability/reputation risk. Sending infrastructure (separate domain, warmed inbox, SPF/DKIM/DMARC) is a separate future decision.

## Per-source status (verified 2026-07-06)

Metros now cover counties: Houston = Harris, Fort Bend, Montgomery, Galveston, Brazoria; Atlanta = Fulton, DeKalb, Cobb, Gwinnett.

| source_id | avenue | enabled | live status | notes |
|---|---|---|---|---|
| trucking_fmcsa | trucking | yes | LIVE | FMCSA Socrata (census/inspections/crashes) + L&I insurance datasets |
| evictions_harris | property_mgmt | yes | LIVE | Harris JP Public Data Extract, eviction-spike detection per plaintiff |
| evictions_fulton | property_mgmt | NO | BLOCKED | re:SearchGA is login-walled (Tyler OIDC). Stub; set RESEARCHGA_COOKIE + re-enable per module docstring |
| violations_houston | property_mgmt | yes | STALE SOURCE | data.houstontx.gov extract frozen at 2018-08; kept enabled (1 cheap call), lights up if city refreshes |
| permits_houston | mechanical | yes | LIVE (needs backfill) | HPC Sold Permits WebFOCUS report; growth signal needs a year-ago baseline: run --backfill-days 450 once |
| permits_atlanta | mechanical | NO | BLOCKED | ArcGIS layer has no contractor field + data ends 2026-01; re-enable path in module docstring |
| osha_dol | manufacturing | yes | NEEDS KEY | DOL API v4 fully implemented; SKIPPED until DOL_API_KEY set |
| epa_echo | manufacturing | yes | LIVE | ECHO SNC facilities (FacSNCFlg=Y), 7 metro counties |
| warn_tx_ga | manufacturing | yes | LIVE | TX Socrata WARN + GA TCSG GravityView scrape |
| listings_bizbuysell | dead_listings | yes | LIVE | Bright Data unlocker; cross-site dedupe canonical site; bounded broker enrichment (3 detail fetches/metro) |
| listings_businessesforsale | dead_listings | yes | LIVE | plain fetch, server-side $1M-$10M filter; band prices -> midpoint; broker from detail 'Listed by' (cap 10/metro) |
| listings_businessbroker | dead_listings | yes | LIVE | plain fetch city pages, client-side price band; broker from detail JSON-LD founder Person |
| listings_sunbelt | dead_listings | yes | LIVE (thin) | admin-ajax city filter; Houston/Atlanta city inventory mostly under $1M, so few in-band listings; suburb cities = v2 |
| listings_murphy | dead_listings | yes | LIVE (page 1/office) | per-office pages (5 Houston + 3 Atlanta offices); office AJAX pagination returns the national feed, so page 1 only |
| listings_bizquest | dead_listings | NO | DUPLICATE SOURCE | fully working via unlocker but CoStar skin of BizBuySell (same listing ids) - near-zero incremental data; keys bbs:{id} if ever enabled |
| listings_loopnet | dead_listings | NO | DUPLICATE SOURCE | stub; loopnet.com/biz/ = CoStar syndication of BizBuySell, zero incremental listings |
| listings_dealstream | dead_listings | NO | BLOCKED | stub; geo URLs return global feed (JS-only metro filter) + detail pages login-gated; unblock path in module docstring |
| listings_transworld | dead_listings | NO | BLOCKED | stub; tworld.com = GraphQL app shell, endpoint not statically discoverable; unblock path in module docstring |
| sba_loans | pe_distress | yes | LIVE | SBA FOIA CSVs (~456MB cached, 80-day refresh), maturity-window signal |
| liens_harris | pe_distress | yes | LIVE | Harris County Clerk WebForms (A/J, LIEN, L/P instrument codes) |
| liens_fortbend | pe_distress | yes | LIVE | Fort Bend Aumentum Recorder (6 doc codes: AJ, JUDGE, FEDLIEN, STLIEN, LIEN, LISPEN); 300-row cap handled via day-split re-queries |
| liens_montgomery | pe_distress | NO | BLOCKED | publicsearch.us bot-blocks non-browser TLS fingerprints (plain requests AND unlocker get the JS shell); parser ready, needs browser-fingerprinted fetch |
| liens_galveston | pe_distress | NO | BLOCKED | Fidlar AVA needs a reCAPTCHA-v3-minted JWT; set GALVESTON_AVA_JWT in ~/.dux_intent/.env (from a Chrome session) to attempt |
| liens_brazoria | pe_distress | NO | BLOCKED | Tyler Self Service portal gates all search behind interactive reCAPTCHA v2; enable paths in module docstring |
| liens_fulton | pe_distress | yes | LIVE (free slice) | GA DOR state tax liens via GSCCCA (no login). Full FIFA/judgment/federal index needs GSCCCA paid ($14.95/mo); recipe in docstring |
| liens_dekalb | pe_distress | yes | LIVE (free slice) | GA DOR state tax liens via shared GSCCCA flow; full index = GSCCCA paid (intCountyID=44) |
| liens_cobb | pe_distress | yes | LIVE (free slice) | GA DOR state tax liens; Cobb's own LandmarkWeb withholds rows from non-browser sessions - never trust its zero-row responses |
| liens_gwinnett | pe_distress | yes | LIVE (free slice) | GA DOR state tax liens; full FIFA/judgment index = GSCCCA paid (intCountyID=67) |
| pay_sba | pay (credit) | yes | LIVE | credit_sba_loan: joins cached SBA FOIA CSVs to existing pe_distress/manufacturing/mechanical/trucking entities by normalized name + metro (name-quality guard, zip-conflict veto); magnitude = GrossApproval bucket; CANCLD/CHGOFF excluded; 3y window |
| pay_hcad | pay (size) | yes | LIVE (houston only) | size_parcels: HCAD Real_acct_owner.zip (210MB, streamed, 80-day refresh) grouped by mailto owner -> parcel count per property_mgmt landlord. Limits: per-property LLCs and 3rd-party managers under-count |
| pay_census_size | pay (size) | yes | LIVE | size_fleet: DOT-keyed join to FMCSA census (zero name-match risk); magnitude = max(power_units, mcs150_mileage) norms; snapshot change-gated |
| pay_ga_ucc | pay (credit) | NO | LOGIN-WALLED | credit_ucc_filing (GA): GSCCCA UCC search results are behind a login (auth wall, not bot wall - unlocker does not apply). Enable path: GSCCCA_USER/GSCCCA_PASS + ~$24.95/mo sub, playbook in module docstring |
| timing_insurance | timing | yes | LIVE | insurance_renewal: policy EFFECTIVE dates via FMCSA L&I SoQL (qh9u-swkp); projects to calendar anniversary, emits when the +/-30d renewal window is open or opens within 60d. LIVIEW scrape is reCAPTCHA-blocked (documented) |
| timing_trajectory | timing | yes | LIVE (derived) | permit_growth_window (needs 6 complete permit months in store - accumulating) + eviction_spike_window (live now) from existing snapshots; no network |

Cross-site listing dedupe: `collectors/_listings_common.py` (CrossSiteDeduper) - exact fingerprint (metro + distinctive title tokens + $250K price bucket) merges to the highest-priority site's entity_key with all source_refs; fuzzy matches only flagged. County lien collectors share `collectors/_liens_common.py` (kind classification) and `collectors/_gsccca.py` (GA DOR flow); all key debtors as `biz:{name_norm}|` so the same business stacks across counties.

## Adding a collector

1. Create `collectors/<source_id>.py` implementing `BaseCollector` (see `collectors/__init__.py` for the frozen contract): `collect(since, store, registry) -> CollectorResult`, never raise, emit via `store.add_signal(Signal(...))`, snapshot aggregates via `store.add_snapshot`.
2. Support `python -m collectors.<source_id> --self-test` (30-day pull into a throwaway store, saves `fixtures/<source_id>_sample.json`, never touches sheet/real DB). The `collectors/_federal.py` helper has a reusable harness.
3. Register: add the signal type(s) under the right avenue in `signal_registry.json` (weight + half_life_days) and add `"<source_id>": true` to `collectors_enabled`. Add the source_id to the avenue's `collectors` list.
4. `load_collectors` discovers it by module name = source_id; expose a `Collector` class or `COLLECTOR` instance.

## Backup

`intent.db` accumulates all history (signals, snapshots, runs, scores). Weekly, after the Monday scan:

```
python -c "import sqlite3,os; s=sqlite3.connect(os.path.expanduser('~/.dux_intent/intent.db')); d=sqlite3.connect(os.path.expanduser('~/.dux_intent/intent_backup.db')); s.backup(d); d.close(); s.close(); print('backup ok')"
```

Uses SQLite's online `.backup` API (safe while readers exist). Keep the backup in `~/.dux_intent/` (outside OneDrive, same as the live DB).
