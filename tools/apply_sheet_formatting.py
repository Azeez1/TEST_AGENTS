"""
Apply conditional formatting to PE_FIRMS sheet:
  - Red (light red fill) on rows where col L contains "Bounced"
  - Green (light green fill) on rows where col L contains "Sent"

Idempotent: removes any prior rules using the same formulas before re-adding,
so re-running cleanly replaces (won't stack duplicates).
"""
import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

MCP_CRED_PATH = Path.home() / ".google_workspace_mcp" / "credentials" / "sabaazeez12@gmail.com.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1QN5uQENnfPlgE8qy9EfC9JjBH1qFyHvUISoX9GReQUc"
TAB_NAME = "PE_FIRMS"

# Range: A2:Q35 (rows 2-35 = data rows; widen as you add more firms)
START_ROW = 1   # 0-indexed: row 2 in user view
END_ROW = 35    # exclusive: covers through row 35
START_COL = 0   # A
END_COL = 17    # exclusive: through Q

GREEN_FORMULA = '=REGEXMATCH($L2, "Sent")'
RED_FORMULA   = '=REGEXMATCH($L2, "Bounced")'

# Color values (Google uses 0-1 floats)
RED_FILL   = {"red": 0.98, "green": 0.85, "blue": 0.85}   # light red / pinkish
GREEN_FILL = {"red": 0.85, "green": 0.94, "blue": 0.85}   # light green


def get_sheets_service():
    with open(MCP_CRED_PATH, encoding="utf-8") as f:
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


def get_tab_id(service, spreadsheet_id, tab_name):
    sheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for s in sheet["sheets"]:
        if s["properties"]["title"] == tab_name:
            return s["properties"]["sheetId"], s
    raise ValueError(f"Tab {tab_name} not found")


def existing_rule_indices_to_delete(sheet_props):
    """Return 0-based indices of any existing conditional rules that use our
    formulas (so we can replace them cleanly). Returns descending order so
    deleting by index doesn't shift later targets."""
    rules = sheet_props.get("conditionalFormats", []) or []
    targets = []
    for i, r in enumerate(rules):
        booleans = r.get("booleanRule", {})
        cond = booleans.get("condition", {})
        if cond.get("type") != "CUSTOM_FORMULA":
            continue
        vals = cond.get("values") or []
        if not vals:
            continue
        formula = vals[0].get("userEnteredValue", "")
        if formula in (GREEN_FORMULA, RED_FORMULA):
            targets.append(i)
    return sorted(targets, reverse=True)


def main():
    service = get_sheets_service()
    sheet_id, sheet_props = get_tab_id(service, SPREADSHEET_ID, TAB_NAME)

    # Build delete requests for any existing matching rules
    delete_indices = existing_rule_indices_to_delete(sheet_props)
    requests = []
    for idx in delete_indices:
        requests.append({"deleteConditionalFormatRule": {"sheetId": sheet_id, "index": idx}})

    # Common range
    grid_range = {
        "sheetId": sheet_id,
        "startRowIndex": START_ROW,
        "endRowIndex": END_ROW,
        "startColumnIndex": START_COL,
        "endColumnIndex": END_COL,
    }

    # RED rule first (more specific — takes precedence on overlap)
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [grid_range],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": RED_FORMULA}],
                    },
                    "format": {"backgroundColor": RED_FILL},
                },
            },
            "index": 0,
        }
    })

    # GREEN rule second
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
            "index": 1,
        }
    })

    print(f"Sending {len(requests)} requests:")
    print(f"  - Delete {len(delete_indices)} existing rules with matching formulas")
    print(f"  - Add red rule for 'Bounced' in col L (range A2:Q35)")
    print(f"  - Add green rule for 'Sent' in col L (range A2:Q35)")

    result = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": requests},
    ).execute()

    print(f"\nDone. Replies: {len(result.get('replies', []))}")


if __name__ == "__main__":
    main()
