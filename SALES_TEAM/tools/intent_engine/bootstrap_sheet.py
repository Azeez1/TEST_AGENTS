"""One-time bootstrap: create the INTENT_SIGNALS spreadsheet with its 7 tabs.

Prints the new spreadsheet id — paste it into ~/.dux_intent/.env as:
    INTENT_SPREADSHEET_ID=<id>

Usage: python bootstrap_sheet.py
"""
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from export_sheet import TABS, get_sheets_service  # noqa: E402


def main():
    existing = config.get_env("INTENT_SPREADSHEET_ID")
    if existing:
        print(f"INTENT_SPREADSHEET_ID is already set ({existing}).")
        print("Delete it from ~/.dux_intent/.env first if you really want a fresh spreadsheet.")
        return 1
    if not config.MCP_CRED_PATH.exists():
        print(f"ERROR: Google credentials not found at {config.MCP_CRED_PATH}")
        return 1

    service = get_sheets_service()
    body = {
        "properties": {"title": "INTENT_SIGNALS"},
        "sheets": [{"properties": {"title": t}} for t in TABS],
    }
    result = service.spreadsheets().create(body=body).execute()
    sid = result["spreadsheetId"]
    print("Created INTENT_SIGNALS spreadsheet.")
    print(f"  URL: https://docs.google.com/spreadsheets/d/{sid}")
    print(f"  ID:  {sid}")
    print()
    print("NEXT STEP - paste this line into ~/.dux_intent/.env :")
    print(f"  INTENT_SPREADSHEET_ID={sid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
