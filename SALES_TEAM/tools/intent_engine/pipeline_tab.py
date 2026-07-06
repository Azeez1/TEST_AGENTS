"""Durable PIPELINE tracker tab for the Dux Machina intent engine spreadsheet.

One row per unique company (entity+metro) drawn from the two freshest funnel
CSVs (intent_customers_*.csv + intent_acquisitions_*.csv). Unlike the other
tabs this one is USER-OWNED: the first column, Status, is a hand-edited
pipeline stage. A weekly refresh must NEVER reset a status a human set — so
before rewriting we read the existing tab, remember every non-default Status
(and each row's First Seen), and carry them forward. New companies arrive as
"New"; everything else keeps what the human chose.

Auth / spreadsheet-id / chunked-write helpers are reused verbatim from
export_sheet.py (OAuth creds at config.MCP_CRED_PATH, spreadsheets scope).

Run standalone:  python -m pipeline_tab
Wired into run_intent_scan.py so every full (non --no-sheet) run refreshes it.
"""
import csv
import sys
from datetime import date
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from export_sheet import (get_sheets_service, _tab_ids,  # noqa: E402
                          _write_values)

PIPELINE_TAB = "PIPELINE"

# Column schema (Status FIRST — the human edits it by hand).
HEADER = ["Status", "Funnel", "Entity", "Metro", "Avenue", "Expected Value",
          "Top Signals", "Ability to Pay", "Contact", "Evidence",
          "First Seen", "Last Updated"]
COL_WIDTHS = [90, 100, 240, 90, 130, 110, 170, 100, 260, 280, 100, 110]

STATUS_VALUES = ["New", "Drafted", "Sent", "Replied", "Meeting", "Won", "Dead"]
DEFAULT_STATUS = "New"
STATUS_NOTE = (
    "Status (edit by hand — pick from the dropdown).\n"
    "New / Drafted / Sent / Replied / Meeting / Won / Dead.\n"
    "The weekly refresh PRESERVES any status you set here; only brand-new "
    "companies are added as 'New'. Your pipeline is never reset."
)

FORMAT_END_ROW = 1000              # dropdown + reads cover future manual rows
HEADER_FILL = {"red": 0.85, "green": 0.85, "blue": 0.85}

# indices of the fields we care about when reading the EXISTING tab back
_C_STATUS, _C_ENTITY, _C_METRO, _C_FIRST_SEEN = 0, 2, 3, 10


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _norm_entity(name):
    return " ".join((name or "").split()).upper()


def _norm_metro(metro):
    return (metro or "").strip().lower()


def _newest_csv(prefix):
    """Newest SALES outputs CSV whose name is intent_{prefix}_{YYYY-MM-DD}.csv,
    chosen by the date in the filename (fallback: mtime)."""
    out_dir = config.OUTPUT_DIR
    candidates = list(out_dir.glob(f"intent_{prefix}_*.csv"))
    if not candidates:
        return None

    def _key(p):
        stem = p.stem  # intent_customers_2026-07-06
        datepart = stem.rsplit("_", 1)[-1]
        return (datepart, p.stat().st_mtime)

    return max(candidates, key=_key)


def _read_csv_rows(path, funnel):
    """Read a v2 funnel CSV into normalized dicts tagged with `funnel`."""
    rows = []
    if not path or not path.exists():
        return rows
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            entity = r.get("entity", "")
            if not entity:
                continue
            rows.append({
                "funnel": funnel,
                "entity": entity,
                "metro": r.get("metro", ""),
                "avenue": r.get("avenue", ""),
                "expected_value": r.get("expected_value", ""),
                "top_signals": r.get("top_signals", ""),
                "ability_to_pay": r.get("ability_to_pay", ""),
                "contact": r.get("contact", ""),
                "evidence": r.get("evidence", ""),
                "entity_norm": _norm_entity(entity),
                "metro_norm": _norm_metro(r.get("metro", "")),
            })
    return rows


def load_pipeline_rows():
    """Freshest customers + acquisitions CSVs, de-duped to one row per
    unique entity+metro (a company in both lists shows once; the higher
    expected_value row wins, and its funnel is kept). Sorted EV desc."""
    cust_path = _newest_csv("customers")
    acq_path = _newest_csv("acquisitions")
    combined = _read_csv_rows(cust_path, "customers") + \
        _read_csv_rows(acq_path, "acquisitions")

    def _ev(row):
        try:
            return float(row.get("expected_value") or 0.0)
        except ValueError:
            return 0.0

    deduped = {}
    for row in combined:
        key = (row["entity_norm"], row["metro_norm"])
        prev = deduped.get(key)
        if prev is None or _ev(row) > _ev(prev):
            deduped[key] = row
    return sorted(deduped.values(), key=_ev, reverse=True), cust_path, acq_path


# --------------------------------------------------------------------------- #
# existing-tab read (status preservation)
# --------------------------------------------------------------------------- #
def _read_existing(service, spreadsheet_id):
    """Return (status_map, firstseen_map, n_preserved).

    status_map: {(entity_norm, metro_norm) -> Status} plus an
    (entity_norm, None) fallback, ONLY for rows whose Status a human set to
    something other than blank/'New'. firstseen_map keyed the same way holds
    each existing row's First Seen so it survives the rewrite.
    """
    from googleapiclient.errors import HttpError
    status_map, firstseen_map, n_preserved = {}, {}, 0
    try:
        resp = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{PIPELINE_TAB}'!A1:L{FORMAT_END_ROW}",
        ).execute()
    except HttpError:
        return status_map, firstseen_map, n_preserved  # tab absent/empty

    values = resp.get("values", [])
    for i, row in enumerate(values):
        def cell(idx):
            return row[idx].strip() if len(row) > idx and row[idx] else ""
        entity = cell(_C_ENTITY)
        # skip the header row (first row that literally reads "Status")
        if i == 0 and cell(_C_STATUS).lower() == "status":
            continue
        if not entity:
            continue
        en, mn = _norm_entity(entity), _norm_metro(cell(_C_METRO))
        first_seen = cell(_C_FIRST_SEEN)
        if first_seen:
            firstseen_map[(en, mn)] = first_seen
            firstseen_map.setdefault((en, None), first_seen)
        status = cell(_C_STATUS)
        if status and status != DEFAULT_STATUS:
            status_map[(en, mn)] = status
            status_map.setdefault((en, None), status)
            n_preserved += 1
    return status_map, firstseen_map, n_preserved


def _lookup(m, en, mn):
    """Exact (entity,metro) match first, then an entity-only fallback so a
    hand-set status survives even if a metro label shifts."""
    if (en, mn) in m:
        return m[(en, mn)]
    return m.get((en, None))


# --------------------------------------------------------------------------- #
# tab creation + formatting
# --------------------------------------------------------------------------- #
def _ensure_pipeline_tab(service, spreadsheet_id):
    """Create the PIPELINE tab if missing. Returns True if it was created."""
    existing = _tab_ids(service, spreadsheet_id)
    if PIPELINE_TAB in existing:
        return False
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": PIPELINE_TAB}}}]},
    ).execute()
    return True


def _apply_formatting(service, spreadsheet_id, sheet_id):
    """Freeze + bold the header, dropdown-validate the Status column, note the
    allowed values, and set readable column widths. Idempotent."""
    ncols = len(HEADER)
    requests = [
        {"updateSheetProperties": {
            "properties": {"sheetId": sheet_id,
                           "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"}},
        {"repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1,
                      "startColumnIndex": 0, "endColumnIndex": ncols},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True},
                "backgroundColor": HEADER_FILL,
                "verticalAlignment": "MIDDLE"}},
            "fields": "userEnteredFormat(textFormat,backgroundColor,verticalAlignment)"}},
        {"setDataValidation": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1,
                      "endRowIndex": FORMAT_END_ROW,
                      "startColumnIndex": 0, "endColumnIndex": 1},
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in STATUS_VALUES]},
                "showCustomUi": True,
                "strict": False}}},
        {"updateCells": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1,
                      "startColumnIndex": 0, "endColumnIndex": 1},
            "rows": [{"values": [{"note": STATUS_NOTE}]}],
            "fields": "note"}},
    ]
    for idx, width in enumerate(COL_WIDTHS):
        requests.append({"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                      "startIndex": idx, "endIndex": idx + 1},
            "properties": {"pixelSize": width},
            "fields": "pixelSize"}})
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()


# --------------------------------------------------------------------------- #
# main sync
# --------------------------------------------------------------------------- #
def sync_pipeline(service=None):
    """Refresh the PIPELINE tab from the freshest CSVs, preserving hand-set
    Status. Returns a result dict; never raises for a missing id/creds (it
    prints and returns ok=False instead)."""
    spreadsheet_id = config.get_env("INTENT_SPREADSHEET_ID")
    if not spreadsheet_id:
        print("[pipeline] INTENT_SPREADSHEET_ID not set in ~/.dux_intent/.env - "
              "skipping PIPELINE tab.")
        return {"ok": False, "reason": "no_spreadsheet_id"}
    if not config.MCP_CRED_PATH.exists():
        print(f"[pipeline] Google credentials not found at {config.MCP_CRED_PATH} - "
              "skipping PIPELINE tab.")
        return {"ok": False, "reason": "no_creds"}

    if service is None:
        service = get_sheets_service()

    created = _ensure_pipeline_tab(service, spreadsheet_id)

    # READ existing statuses BEFORE we clear/rewrite.
    status_map, firstseen_map, n_preserved = _read_existing(service, spreadsheet_id)

    new_rows, cust_path, acq_path = load_pipeline_rows()
    today = date.today().isoformat()

    values = [HEADER]
    n_carried = 0
    for r in new_rows:
        en, mn = r["entity_norm"], r["metro_norm"]
        status = _lookup(status_map, en, mn)
        if status:
            n_carried += 1
        else:
            status = DEFAULT_STATUS
        first_seen = _lookup(firstseen_map, en, mn) or today
        values.append([
            status,
            r["funnel"].capitalize(),
            r["entity"],
            r["metro"],
            r["avenue"],
            r["expected_value"],
            r["top_signals"],
            r["ability_to_pay"],
            r["contact"],
            r["evidence"],
            first_seen,
            today,
        ])

    _write_values(service, spreadsheet_id, PIPELINE_TAB, values)

    sheet_id = _tab_ids(service, spreadsheet_id)[PIPELINE_TAB][0]
    _apply_formatting(service, spreadsheet_id, sheet_id)

    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    print(f"[pipeline] {'Created and populated' if created else 'Refreshed'} "
          f"PIPELINE tab: {len(new_rows)} companies "
          f"({n_carried} hand-set statuses preserved, "
          f"{n_preserved} were non-default in the tab). {url}")
    if cust_path:
        print(f"[pipeline]   customers source: {cust_path.name}")
    if acq_path:
        print(f"[pipeline]   acquisitions source: {acq_path.name}")
    return {"ok": True, "created": created, "rows": len(new_rows),
            "preserved": n_carried, "url": url}


def main():
    try:
        result = sync_pipeline()
    except Exception as exc:  # surface auth/refresh failures clearly, don't hang
        print(f"[pipeline] ERROR: {type(exc).__name__}: {exc}")
        return 1
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
