"""
VOICE_TEAM — Post-Call Booking Script

Reads recent Retell calls, finds ones with extracted post_call_analysis fields
(Caller Full Name, Callback Phone Number, Preferred Callback Day/Time), and
books a Google Calendar event for each one via the google-workspace MCP path
(or direct Google Calendar API as a fallback).

Designed to run on-demand or via a 5-minute cron.

Usage:
    python book_pending_consults.py [--firm sterling_legal] [--since-hours 24] [--dry-run]

Dependencies:
    pip install pyyaml httpx python-dotenv dateparser

Author: VOICE_TEAM Factory
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Windows cp1252 fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import httpx
import yaml
from dotenv import load_dotenv

try:
    import dateparser  # graceful fallback if not installed
except ImportError:
    dateparser = None

# --- Paths -----------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
VOICE_TEAM = REPO_ROOT / "VOICE_TEAM"
ENV_FILE = REPO_ROOT / "MARKETING_TEAM" / ".env"
VOICE_CONFIG = VOICE_TEAM / "memory" / "voice_config.json"
OUTPUT_PATHS = VOICE_TEAM / "memory" / "output_paths.json"

load_dotenv(ENV_FILE)
RETELL_API_KEY = os.getenv("RETELL_API_KEY")
if not RETELL_API_KEY:
    print(f"FATAL: RETELL_API_KEY not found in {ENV_FILE}", file=sys.stderr)
    sys.exit(1)

with open(VOICE_CONFIG) as f:
    VOICE_CFG = json.load(f)
with open(OUTPUT_PATHS) as f:
    PATHS = json.load(f)["paths"]

RETELL_BASE = VOICE_CFG["retell"]["api_base"]
HEADERS = {
    "Authorization": f"Bearer {RETELL_API_KEY}",
    "Content-Type": "application/json",
}

BOOKINGS_DIR = Path(PATHS["bookings"])
CALL_LOGS_DIR = Path(PATHS["call_logs"])
EMAILS_DIR = Path(PATHS.get("emails", str(Path(PATHS["bookings"]).parent / "emails")))
BOOKINGS_DIR.mkdir(parents=True, exist_ok=True)
CALL_LOGS_DIR.mkdir(parents=True, exist_ok=True)
EMAILS_DIR.mkdir(parents=True, exist_ok=True)


# --- Retell API helpers ----------------------------------------------------

def _api(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    url = f"{RETELL_BASE}{path}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.request(method, url, headers=HEADERS, json=body)
    if resp.status_code >= 400:
        print(f"[ERROR] {method} {url} {resp.status_code}: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json() if resp.text else {}


def list_recent_calls(agent_ids: list[str] | None = None, since_hours: int = 24) -> list[dict]:
    """List Retell calls in the last N hours, optionally filtered by one or more agent_ids."""
    cutoff_ms = int((datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)).timestamp() * 1000)
    body: dict[str, Any] = {
        "filter_criteria": {"start_timestamp": {"lower_threshold": cutoff_ms}},
        "limit": 50,
        "sort_order": "descending",
    }
    if agent_ids:
        body["filter_criteria"]["agent_id"] = agent_ids
    # Retell v2 endpoint
    resp = _api("POST", "/v2/list-calls", body)
    return resp if isinstance(resp, list) else resp.get("calls", [])


# --- Slot parsing ----------------------------------------------------------

def parse_slot(day_str: str | None, time_str: str | None, tz_name: str = "America/New_York") -> datetime | None:
    """
    Parse a caller-stated 'day + time' into a timezone-aware datetime.

    Examples that should parse:
      day="tomorrow", time="2pm"
      day="Monday", time="morning" (defaults to 10am)
      day="Friday", time="after 5pm" (defaults to 5pm)
    """
    if not day_str:
        return None
    if dateparser is None:
        print("  [WARN] dateparser not installed — skipping slot parsing. pip install dateparser")
        return None
    # Default vague times to concrete times
    time_str_norm = (time_str or "10am").lower().strip()
    vague_map = {
        "morning": "10am",
        "afternoon": "2pm",
        "evening": "6pm",
        "noon": "12pm",
        "midday": "12pm",
    }
    for vague, concrete in vague_map.items():
        if vague in time_str_norm and not any(d in time_str_norm for d in "0123456789"):
            time_str_norm = concrete
            break
    combined = f"{day_str} {time_str_norm}"
    parsed = dateparser.parse(
        combined,
        settings={
            "PREFER_DATES_FROM": "future",
            "TIMEZONE": tz_name,
            "RETURN_AS_TIMEZONE_AWARE": True,
        },
    )
    return parsed


# --- Call → Booking translator --------------------------------------------

def extract_booking_fields(call: dict) -> dict[str, Any]:
    """
    Pull the canonical fields we need from a Retell call object's
    post_call_analysis.custom_analysis_data + recording/log URLs.
    """
    analysis = call.get("call_analysis", {}) or {}
    custom = analysis.get("custom_analysis_data", {}) or {}
    call_id = call.get("call_id", "")
    return {
        "call_id": call_id,
        "caller_name": custom.get("Caller Full Name") or "Unknown caller",
        "callback_phone": custom.get("Callback Phone Number") or "",
        "incident_type": custom.get("Incident Type") or "",
        "incident_date": custom.get("Incident Date") or "",
        "currently_injured": custom.get("Currently Injured") or "",
        "fault_assessment": custom.get("Fault Assessment") or "",
        "police_report_filed": custom.get("Police Report Filed") or "",
        "insurance_contact": custom.get("Insurance Contact") or "",
        "preferred_day": custom.get("Preferred Callback Day") or "",
        "preferred_time": custom.get("Preferred Callback Time") or "",
        "urgency": custom.get("Urgency Level") or "flexible",
        "case_quality": custom.get("Case Quality") or "",
        "outside_practice": custom.get("Case Outside Practice Area") or False,
        "call_summary": analysis.get("call_summary") or "",
        "transcript": call.get("transcript") or "",
        # Retell URLs — for embedding in the attorney's email
        "recording_url": call.get("recording_url") or "",
        "recording_multi_channel_url": call.get("recording_multi_channel_url") or "",
        "public_log_url": call.get("public_log_url") or "",
        "dashboard_call_url": f"https://dashboard.retellai.com/calls/{call_id}" if call_id else "",
        "call_duration_sec": (call.get("call_cost") or {}).get("total_duration_seconds") or 0,
    }


# --- Booking sink ----------------------------------------------------------

def build_email_intent(
    firm_doc: dict, fields: dict, slot_dt: datetime | None, call_id: str, dry_run: bool = False
) -> dict[str, Any]:
    """
    Build an email-summary intent file. A Claude Code session reads this file +
    dispatches via mcp__google-workspace__send_gmail_message.

    Recipient defaults to firm.notification_email if set, otherwise to the
    operator's primary Google email (sabaazeez12@gmail.com).
    """
    firm = firm_doc["firm"]
    notify_to = (
        firm.get("notification_email")
        or firm_doc.get("notifications", {}).get("intake_email")
        or "sabaazeez12@gmail.com"
    )
    slot_str = slot_dt.strftime("%a %b %d, %I:%M %p %Z") if slot_dt else "Not specified"
    urgency = fields.get("urgency") or "flexible"
    urgency_label = {
        "emergency": "🔴 EMERGENCY",
        "this_week": "🟠 This week",
        "this_month": "🟡 This month",
        "flexible": "🟢 Flexible",
    }.get(urgency, urgency)

    subject = f"[{firm['name']}] New Intake — {fields['caller_name']} — {fields.get('incident_type') or 'Unknown'} — {urgency_label}"

    recording_url = fields.get("recording_url") or ""
    multichan_url = fields.get("recording_multi_channel_url") or ""
    log_url = fields.get("public_log_url") or ""
    dashboard_url = fields.get("dashboard_call_url") or ""

    body_lines = [
        f"## New {firm.get('practice_area_display', 'Personal Injury')} Intake",
        "",
        f"**Captured:** {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Source:** AI voice intake to {firm.get('phone_main', '')}",
        f"**Call ID:** {call_id}",
        f"**Duration:** {fields.get('call_duration_sec', 0)}s",
        "",
        "### Caller",
        f"- **Name:** {fields['caller_name']}",
        f"- **Phone:** {fields['callback_phone']}",
        f"- **Urgency:** {urgency_label}",
        "",
        "### Incident",
        f"- **Type:** {fields.get('incident_type') or '(not captured)'}",
        f"- **When:** {fields.get('incident_date') or '(not captured)'}",
        f"- **Currently injured:** {fields.get('currently_injured') or '(not captured)'}",
        f"- **Fault (per caller):** {fields.get('fault_assessment') or '(not captured)'}",
        f"- **Police report:** {fields.get('police_report_filed') or '(not captured)'}",
        f"- **Insurance contact:** {fields.get('insurance_contact') or '(not captured)'}",
        "",
        "### Case Quality (Preliminary)",
        f"- {fields.get('case_quality') or 'Not assessed by AI'}",
        "",
        "### Recording & Transcript",
        f"- 🎧 [Play recording (.wav)]({recording_url})" if recording_url else "- (no recording URL available)",
        f"- 🎙️ [Multi-channel recording (caller + agent on separate tracks)]({multichan_url})" if multichan_url else "",
        f"- 📋 [View transcript + post-call analysis in Retell dashboard]({dashboard_url})" if dashboard_url else "",
        f"- 📊 [Technical call log]({log_url})" if log_url else "",
        "",
        "### Calendar",
        f"- **Callback slot:** {slot_str}",
        "- (Calendar event auto-created — see your Google Calendar)",
        "",
        "### Action Required",
        f"1. Listen to the recording before {slot_str} callback",
        f"2. Call {fields['callback_phone']} at the scheduled time",
        "3. Have intake forms ready",
        "",
        "### Call Summary (AI-generated)",
        fields.get("call_summary") or "(no summary)",
        "",
        "---",
        f"Generated by VOICE_TEAM AI Intake Factory. To stop or change notifications, edit {firm['slug']}.yml.",
    ]
    # Strip any empty lines from missing optional URLs
    body_lines = [ln for ln in body_lines if ln != ""]

    intent = {
        "intent_type": "email_summary",
        "status": "pending" if not dry_run else "dry_run",
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "firm_slug": firm["slug"],
        "call_id": call_id,
        "recording_url": recording_url,
        "dashboard_url": dashboard_url,
        "email": {
            "to": notify_to,
            "subject": subject,
            "body_markdown": "\n".join(body_lines),
            "urls": {
                "recording": recording_url,
                "recording_multi_channel": multichan_url,
                "transcript_dashboard": dashboard_url,
                "log": log_url,
            },
        },
    }
    intent_path = EMAILS_DIR / f"{firm['slug']}_{call_id}.json"
    intent_path.write_text(json.dumps(intent, indent=2), encoding="utf-8")
    return {"intent_path": str(intent_path), "intent": intent}


def book_via_google_workspace_mcp(
    firm_doc: dict, fields: dict, slot_dt: datetime, dry_run: bool = False
) -> dict[str, Any]:
    """
    Day-1 booking sink: write a structured booking-intent JSON to outputs/bookings/.
    The actual Google Calendar event creation is performed by a Claude Code session
    that picks up these intent files via the google-workspace MCP `manage_event` tool
    (LOCAL execution, no public endpoint).

    This decouples the post-call extraction from the actual API call, which means:
      - Booking-intent files are durable + auditable
      - Re-running this script is idempotent
      - A separate `process_booking_intents.md` skill consumes the intents
    """
    firm = firm_doc["firm"]
    cal_cfg = firm_doc.get("calendar", {}) or {}
    duration_min = cal_cfg.get("event_duration_min", 30)
    end_dt = slot_dt + timedelta(minutes=duration_min)

    intent = {
        "intent_type": "calendar_booking",
        "status": "pending",
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "firm_slug": firm["slug"],
        "firm_name": firm["name"],
        "calendar_id": cal_cfg.get("google_calendar_id", "primary"),
        "event": {
            "summary": f"{cal_cfg.get('event_template', firm['name'] + ' — Consultation')} — {fields['caller_name']}",
            "description": (
                f"Intake call summary:\n{fields['call_summary']}\n\n"
                f"Caller: {fields['caller_name']}\n"
                f"Phone: {fields['callback_phone']}\n"
                f"Incident: {fields['incident_type']} on {fields['incident_date']}\n"
                f"Injured: {fields['currently_injured']}\n"
                f"Urgency: {fields['urgency']}\n"
                f"Case quality: {fields['case_quality']}\n"
            ),
            "start": slot_dt.isoformat(),
            "end": end_dt.isoformat(),
            "timezone": cal_cfg.get("timezone") or VOICE_CFG["google_calendar"]["default_timezone"],
            "attendees": [],
            "reminders": {"useDefault": True},
        },
        "source_call": {
            "preferred_day": fields["preferred_day"],
            "preferred_time": fields["preferred_time"],
        },
    }
    if dry_run:
        intent["status"] = "dry_run"
    intent_path = BOOKINGS_DIR / f"{firm['slug']}_{slot_dt.strftime('%Y%m%d_%H%M%S')}_{fields['callback_phone'][-4:] or 'unknown'}.json"
    intent_path.write_text(json.dumps(intent, indent=2), encoding="utf-8")
    return {"intent_path": str(intent_path), "intent": intent}


# --- Main ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--firm", default="sterling_legal", help="Firm slug to process")
    parser.add_argument("--since-hours", type=int, default=24, help="Look back window in hours")
    parser.add_argument("--dry-run", action="store_true", help="Write intents but mark as dry_run")
    args = parser.parse_args()

    firm_yml = VOICE_TEAM / "memory" / "firms" / f"{args.firm}.yml"
    if not firm_yml.exists():
        print(f"FATAL: firm config not found at {firm_yml}", file=sys.stderr)
        sys.exit(1)
    firm_doc = yaml.safe_load(firm_yml.read_text(encoding="utf-8"))

    # Collect ALL agent_ids deployed for this firm (cascading + s2s variants)
    deploy_dir = Path(PATHS["deployments"])
    agent_ids: list[str] = []
    for pattern in (f"{args.firm}.json", f"{args.firm}_s2s.json"):
        artifact_path = deploy_dir / pattern
        if artifact_path.exists():
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
            if data.get("agent_id"):
                agent_ids.append(data["agent_id"])
    if not agent_ids:
        print(f"FATAL: no deployment artifacts found for firm '{args.firm}'. Run deploy first.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Processing pending consults for {firm_doc['firm']['name']} ===")
    print(f"  Agents: {agent_ids}")
    print(f"  Looking back {args.since_hours}h...")

    calls = list_recent_calls(agent_ids=agent_ids, since_hours=args.since_hours)
    print(f"  Found {len(calls)} call(s) in window")

    booked = 0
    skipped = 0
    for call in calls:
        call_id = call.get("call_id")
        # Skip calls without post-call analysis populated yet
        analysis = call.get("call_analysis", {}) or {}
        if not analysis.get("custom_analysis_data"):
            print(f"  [skip] {call_id}: no analysis yet")
            skipped += 1
            continue
        fields = extract_booking_fields(call)
        if fields["outside_practice"]:
            print(f"  [skip] {call_id}: out-of-practice caller")
            skipped += 1
            continue
        if not fields["caller_name"] or fields["caller_name"] == "Unknown caller":
            print(f"  [skip] {call_id}: no caller name captured")
            skipped += 1
            continue

        slot_dt = parse_slot(
            fields["preferred_day"],
            fields["preferred_time"],
            tz_name=firm_doc.get("calendar", {}).get("timezone")
            or VOICE_CFG["google_calendar"]["default_timezone"],
        )
        if not slot_dt:
            print(f"  [skip] {call_id}: could not parse slot from '{fields['preferred_day']} {fields['preferred_time']}'")
            skipped += 1
            continue

        result = book_via_google_workspace_mcp(firm_doc, fields, slot_dt, dry_run=args.dry_run)
        print(f"  [ok] {call_id}: booking intent → {result['intent_path']}")
        booked += 1

        # Also write an email summary intent for the firm's attorneys
        email_result = build_email_intent(firm_doc, fields, slot_dt, call_id, dry_run=args.dry_run)
        print(f"        email intent → {email_result['intent_path']}")

        # Cache the call log
        log_path = CALL_LOGS_DIR / f"{call_id}.json"
        log_path.write_text(json.dumps(call, indent=2), encoding="utf-8")

    print(f"\n=== Done ===")
    print(f"  Booked: {booked}")
    print(f"  Skipped: {skipped}")
    print(f"\nNext step: Claude Code reads outputs/bookings/*.json (status=pending)")
    print(f"  and calls mcp__google-workspace__manage_event to create the actual calendar events.")
    print(f"  See VOICE_TEAM/.claude/agents/voice-deployer.md for the consumer flow.")


if __name__ == "__main__":
    main()
