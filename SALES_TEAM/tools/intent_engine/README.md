# Dux Machina Intent Signal Engine

Scans public data sources for buying-intent signals across 6 avenues (trucking, property_mgmt, mechanical, manufacturing, dead_listings, pe_distress) in 2 metros (Houston, Atlanta), resolves entities, scores them, and exports ranked prospect lists (CSV + Google Sheet). Pure Python, no LLM calls, no sending. Outreach drafting is a separate human-approved step (`/intent-scan` command).

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
   - `BRIGHTDATA_API_TOKEN` - from the Bright Data dashboard (enables listings_bizbuysell)
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

Outputs land in `SALES_TEAM/outputs/prospecting/`: `intent_{avenue}_{metro}_{date}.csv` per avenue/metro plus `intent_hotlist_{date}.csv` (all hot rows). Then `/intent-scan` in Claude Code drafts evidence-cited outreach from the hotlist into `SALES_TEAM/outputs/outreach/intent_drafts_{date}.md` (queue only - NEVER sends).

## Per-source status (verified 2026-07-05)

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
| listings_bizbuysell | dead_listings | yes | NEEDS TOKEN | parser proven on real cards; SKIPPED until BRIGHTDATA_API_TOKEN set |
| sba_loans | pe_distress | yes | LIVE | SBA FOIA CSVs (~456MB cached, 80-day refresh), maturity-window signal |
| liens_harris | pe_distress | yes | LIVE | Harris County Clerk WebForms (A/J, LIEN, L/P instrument codes) |

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
