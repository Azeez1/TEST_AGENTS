"""Google Sheets export — one INTENT_SIGNALS spreadsheet, one tab per avenue + SUMMARY.

Auth block cloned from tools/apply_sheet_formatting.py (MCP creds, spreadsheets scope,
sheets v4). Spreadsheet id comes from INTENT_SPREADSHEET_ID in ~/.dux_intent/.env —
if unset, this module no-ops with a clear message (run bootstrap_sheet.py once to
create the spreadsheet and get the id).

Behavior per run:
    - ensure the 7 tabs exist
    - clear + rewrite each avenue tab (<=30 rows per values.update batch)
    - green conditional format on the hot column (delete-then-add rule pattern)
    - SUMMARY tab gets run timestamp + per avenue/metro counts
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from export_csv import COLUMNS, _fmt  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TAB_FOR_AVENUE = {
    "trucking": "TRUCKING",
    "property_mgmt": "PROPERTY_MGMT",
    "mechanical": "MECHANICAL",
    "manufacturing": "MANUFACTURING",
    "dead_listings": "DEAD_LISTINGS",
    "pe_distress": "PE_DISTRESS",
}
TABS = ["TRUCKING", "PROPERTY_MGMT", "MECHANICAL", "MANUFACTURING",
        "DEAD_LISTINGS", "PE_DISTRESS", "SUMMARY"]

ROWS_PER_BATCH = 30
# hot is column C in the frozen column order; TRUE/FALSE written as strings
GREEN_FORMULA = '=$C2="TRUE"'
GREEN_FILL = {"red": 0.85, "green": 0.94, "blue": 0.85}   # light green
FORMAT_END_ROW = 1000
LAST_COL_LETTER = "P"   # 16 columns: A..P


def get_sheets_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    with open(config.MCP_CRED_PATH, encoding="utf-8") as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )
    if not creds.valid:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)


def _tab_ids(service, spreadsheet_id):
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {s["properties"]["title"]: (s["properties"]["sheetId"], s)
            for s in meta["sheets"]}


def _ensure_tabs(service, spreadsheet_id):
    existing = _tab_ids(service, spreadsheet_id)
    missing = [t for t in TABS if t not in existing]
    if missing:
        requests = [{"addSheet": {"properties": {"title": t}}} for t in missing]
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()
        existing = _tab_ids(service, spreadsheet_id)
    return existing


def _write_values(service, spreadsheet_id, tab, values):
    """Clear the tab, then write header+values in chunks of <=30 rows per update."""
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=f"'{tab}'"
    ).execute()
    all_rows = values
    row_cursor = 1
    for i in range(0, len(all_rows), ROWS_PER_BATCH):
        chunk = all_rows[i:i + ROWS_PER_BATCH]
        rng = f"'{tab}'!A{row_cursor}"
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=rng,
            valueInputOption="RAW", body={"values": chunk},
        ).execute()
        row_cursor += len(chunk)


def _apply_hot_formatting(service, spreadsheet_id, tab_name, sheet_id, sheet_props):
    """Delete any prior rule using our formula, then add the green rule (idempotent)."""
    rules = sheet_props.get("conditionalFormats", []) or []
    delete_indices = []
    for i, r in enumerate(rules):
        cond = r.get("booleanRule", {}).get("condition", {})
        if cond.get("type") != "CUSTOM_FORMULA":
            continue
        vals = cond.get("values") or []
        if vals and vals[0].get("userEnteredValue", "") == GREEN_FORMULA:
            delete_indices.append(i)
    requests = [
        {"deleteConditionalFormatRule": {"sheetId": sheet_id, "index": idx}}
        for idx in sorted(delete_indices, reverse=True)
    ]
    grid_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,               # row 2 (skip header)
        "endRowIndex": FORMAT_END_ROW,
        "startColumnIndex": 0,            # A
        "endColumnIndex": len(COLUMNS),   # through P
    }
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [grid_range],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": GREEN_FORMULA}],
                    },
                    "format": {"backgroundColor": GREEN_FILL},
                },
            },
            "index": 0,
        }
    })
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()


def export_sheet(rows, summary_rows=None):
    """rows: same row dicts fed to export_csv. summary_rows: list of lists for SUMMARY.
    Returns True if the sheet was updated, False if skipped."""
    spreadsheet_id = config.get_env("INTENT_SPREADSHEET_ID")
    if not spreadsheet_id:
        print("[sheet] INTENT_SPREADSHEET_ID not set in ~/.dux_intent/.env - "
              "skipping Google Sheet export. Run bootstrap_sheet.py once, then "
              "paste the printed id into the .env file.")
        return False
    if not config.MCP_CRED_PATH.exists():
        print(f"[sheet] Google credentials not found at {config.MCP_CRED_PATH} - "
              "skipping Google Sheet export.")
        return False

    service = get_sheets_service()
    _ensure_tabs(service, spreadsheet_id)

    groups = {}
    for r in rows:
        groups.setdefault(r["avenue"], []).append(r)

    for avenue, tab in TAB_FOR_AVENUE.items():
        grp = sorted(groups.get(avenue, []), key=lambda r: -float(r.get("score", 0.0)))
        formatted = [_fmt(r, i + 1) for i, r in enumerate(grp)]
        values = [COLUMNS] + [[str(fr[c]) for c in COLUMNS] for fr in formatted]
        _write_values(service, spreadsheet_id, tab, values)

    # SUMMARY tab
    header = [["INTENT SIGNAL ENGINE - last run",
               datetime.now().isoformat(timespec="seconds")], []]
    body = summary_rows or []
    _write_values(service, spreadsheet_id, "SUMMARY", header + body)

    # conditional formatting needs fresh sheet props (rules may have shifted)
    tabs = _tab_ids(service, spreadsheet_id)
    for avenue, tab in TAB_FOR_AVENUE.items():
        sheet_id, props = tabs[tab]
        _apply_hot_formatting(service, spreadsheet_id, tab, sheet_id, props)

    print(f"[sheet] Updated spreadsheet {spreadsheet_id}: "
          f"{sum(len(v) for v in groups.values())} rows across {len(TAB_FOR_AVENUE)} tabs.")
    return True
