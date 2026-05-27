"""
VOICE_TEAM Webhook Receiver — Auto-Dispatch After Each Call

FastAPI service that receives Retell's call_analyzed webhook and:
  1. Verifies HMAC signature (x-retell-signature header)
  2. Extracts intake fields from post_call_analysis
  3. Creates a Google Calendar event for the requested callback slot
  4. Sends a formatted HTML email summary to the firm's notification address
  5. Runs the SAME white-label validation rules as voice_email_gate.ps1
     (no vendor leaks, required sections, [Firm Name] subject prefix)

Once deployed to a public URL (Render / Fly / Cloudflare / etc.), Retell
fires this webhook automatically after every call. No Claude Code session
needed. Your laptop can be closed.

Deploy:
  - Render: `render.yaml` included, push to GitHub, click "New Web Service"
  - Local test: `uvicorn main:app --port 8000` then point ngrok at it

Required env vars (set in hosting platform):
  RETELL_API_KEY              — for signature verification + call fetching
  RETELL_WEBHOOK_SECRET       — optional, for HMAC verification
  GOOGLE_OAUTH_CLIENT_ID
  GOOGLE_OAUTH_CLIENT_SECRET
  GOOGLE_OAUTH_REFRESH_TOKEN  — copied from your existing MCP credentials file
  GOOGLE_USER_EMAIL           — sabaazeez12@gmail.com (the authorized account)
  FIRM_CONFIGS_DIR            — relative or absolute path to firm.yml configs
                                (default: ./firms/ — bundle them with the deploy)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import dateparser
import httpx
import yaml
from fastapi import FastAPI, HTTPException, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("voice_webhook")

# --- Config ----------------------------------------------------------------

RETELL_API_KEY = os.getenv("RETELL_API_KEY", "")
RETELL_WEBHOOK_SECRET = os.getenv("RETELL_WEBHOOK_SECRET", "")
RETELL_BASE = os.getenv("RETELL_API_BASE", "https://api.retellai.com")

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_OAUTH_REFRESH_TOKEN = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN", "")
GOOGLE_USER_EMAIL = os.getenv("GOOGLE_USER_EMAIL", "sabaazeez12@gmail.com")

FIRM_CONFIGS_DIR = Path(os.getenv("FIRM_CONFIGS_DIR", "./firms"))

# Vendor leak terms (mirrors voice_email_gate.ps1)
FORBIDDEN_VENDOR_TERMS = [
    "retell", "retellai", "dashboard.retellai",
    "gpt-realtime", "openai-realtime",
    "11labs", "elevenlabs", "cartesia", "minimax", "deepgram", "twilio",
]
REQUIRED_SECTIONS = ["Caller", "Incident", "Action Required"]
SUBJECT_PREFIX_RE = re.compile(r"^\[[^\]]+\]")

app = FastAPI(title="VOICE_TEAM Webhook Receiver")


# --- Google API helpers ----------------------------------------------------

class _TokenCache:
    access_token: str | None = None
    expires_at: datetime | None = None


_token_cache = _TokenCache()


def _refresh_google_access_token() -> str:
    """Mint a new access token using the refresh token. Caches until ~5 min before expiry."""
    if _token_cache.access_token and _token_cache.expires_at and _token_cache.expires_at > datetime.now(tz=timezone.utc) + timedelta(minutes=5):
        return _token_cache.access_token

    resp = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "refresh_token": GOOGLE_OAUTH_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache.access_token = data["access_token"]
    _token_cache.expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=data.get("expires_in", 3600))
    return _token_cache.access_token


def create_calendar_event(calendar_id: str, summary: str, description: str,
                          start_iso: str, end_iso: str, tz_name: str = "America/New_York") -> dict:
    token = _refresh_google_access_token()
    body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_iso, "timeZone": tz_name},
        "end": {"dateTime": end_iso, "timeZone": tz_name},
        "reminders": {"useDefault": True},
    }
    resp = httpx.post(
        f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
        timeout=15.0,
    )
    resp.raise_for_status()
    return resp.json()


def send_gmail(to: str, subject: str, body_html: str) -> dict:
    token = _refresh_google_access_token()
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["From"] = GOOGLE_USER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    resp = httpx.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"raw": raw},
        timeout=15.0,
    )
    resp.raise_for_status()
    return resp.json()


# --- Retell API ------------------------------------------------------------

def fetch_call(call_id: str) -> dict:
    resp = httpx.get(
        f"{RETELL_BASE}/v2/get-call/{call_id}",
        headers={"Authorization": f"Bearer {RETELL_API_KEY}"},
        timeout=15.0,
    )
    resp.raise_for_status()
    return resp.json()


def verify_signature(body: bytes, signature_header: str | None) -> bool:
    if not RETELL_WEBHOOK_SECRET:
        return True  # secret not configured — skip verification (fail open)
    if not signature_header:
        return False
    expected = hmac.new(RETELL_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


# --- Field extraction (mirrors book_pending_consults.py) -------------------

def extract_fields(call: dict) -> dict[str, Any]:
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
        "recording_url": call.get("recording_url") or "",
        "recording_multi_channel_url": call.get("recording_multi_channel_url") or "",
        "call_duration_sec": (call.get("call_cost") or {}).get("total_duration_seconds") or 0,
    }


# --- Slot parsing ----------------------------------------------------------

def parse_slot(day_str: str, time_str: str, tz_name: str = "America/New_York") -> datetime | None:
    """Parse a caller-stated 'day + time' into a timezone-aware datetime.

    Robust against:
      - Time strings with trailing timezone hints ("3 PM Eastern", "5pm ET", "2pm CT")
      - Vague time labels ("morning", "afternoon", "evening", "noon")
      - Common 24h and 12h formats
    """
    if not day_str:
        log.warning("parse_slot: day_str empty")
        return None

    time_norm = (time_str or "10am").lower().strip()

    # Strip common US-timezone suffixes — we apply timezone via settings, not as text.
    tz_suffixes = [
        " eastern time", " pacific time", " central time", " mountain time",
        " eastern", " pacific", " central", " mountain",
        " est", " edt", " pst", " pdt", " cst", " cdt", " mst", " mdt",
        " et", " pt", " ct", " mt",
    ]
    for suf in tz_suffixes:
        if time_norm.endswith(suf):
            time_norm = time_norm[: -len(suf)].strip()
            break

    # Vague labels → concrete times (if no digit present)
    vague_map = {"morning": "10am", "afternoon": "2pm", "evening": "6pm", "noon": "12pm", "midday": "12pm"}
    for k, v in vague_map.items():
        if k in time_norm and not any(d in time_norm for d in "0123456789"):
            time_norm = v
            break

    combined = f"{day_str} {time_norm}"
    result = dateparser.parse(
        combined,
        settings={"PREFER_DATES_FROM": "future", "TIMEZONE": tz_name, "RETURN_AS_TIMEZONE_AWARE": True},
    )
    if result is None:
        log.warning("parse_slot: dateparser returned None for input %r", combined)
    else:
        log.info("parse_slot: parsed %r -> %s", combined, result.isoformat())
    return result


# --- Firm config -----------------------------------------------------------

def load_firm_by_phone(phone: str) -> dict | None:
    """Find a firm.yml whose retell.phone_number matches the given E.164 number."""
    if not FIRM_CONFIGS_DIR.exists():
        log.warning("FIRM_CONFIGS_DIR does not exist: %s", FIRM_CONFIGS_DIR)
        return None
    for path in FIRM_CONFIGS_DIR.glob("*.yml"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if (doc.get("retell") or {}).get("phone_number") == phone:
            return doc
    return None


# --- Email body builder ----------------------------------------------------

def build_email_html(firm: dict, fields: dict, slot_dt: datetime | None) -> tuple[str, str]:
    """Return (subject, html_body)."""
    urgency = fields["urgency"]
    urgency_label = {
        "emergency": "EMERGENCY", "this_week": "This week",
        "this_month": "This month", "flexible": "Flexible",
    }.get(urgency, urgency)
    slot_str = slot_dt.strftime("%a %b %d, %I:%M %p %Z") if slot_dt else "Not specified"
    subject = f"[{firm['name']}] New Intake — {fields['caller_name']} — {fields.get('incident_type') or 'Unknown'} — {urgency_label}"

    rec = fields.get("recording_url") or ""
    multi = fields.get("recording_multi_channel_url") or ""

    html = f"""<!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;max-width:640px;margin:0 auto;padding:24px;color:#1a1a1a;">
<div style="border-bottom:3px solid #1a1a1a;padding-bottom:12px;margin-bottom:24px;">
  <div style="font-size:12px;color:#888;text-transform:uppercase;">{firm['name']} — AI Intake</div>
  <h1 style="font-size:22px;margin:6px 0 0 0;font-weight:600;">New {firm.get('practice_area_display','Personal Injury')} Intake</h1>
  <div style="font-size:13px;color:#666;margin-top:4px;">Captured {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')} — Inbound call to {firm.get('phone_main','')}</div>
</div>
<h2 style="font-size:16px;border-bottom:1px solid #e5e5e5;padding-bottom:6px;">Caller</h2>
<table style="width:100%;font-size:14px;"><tr><td style="color:#666;width:140px;">Name</td><td><strong>{fields['caller_name']}</strong></td></tr>
<tr><td style="color:#666;">Phone</td><td><a href="tel:{fields['callback_phone']}">{fields['callback_phone']}</a></td></tr>
<tr><td style="color:#666;">Urgency</td><td><strong>{urgency_label}</strong></td></tr></table>
<h2 style="font-size:16px;border-bottom:1px solid #e5e5e5;padding-bottom:6px;margin-top:20px;">Incident</h2>
<table style="width:100%;font-size:14px;"><tr><td style="color:#666;width:140px;">Type</td><td>{fields.get('incident_type','-')}</td></tr>
<tr><td style="color:#666;">When</td><td>{fields.get('incident_date','-')}</td></tr>
<tr><td style="color:#666;">Currently injured</td><td>{fields.get('currently_injured','-')}</td></tr>
<tr><td style="color:#666;">Fault (per caller)</td><td>{fields.get('fault_assessment','-')}</td></tr>
<tr><td style="color:#666;">Police report</td><td>{fields.get('police_report_filed','-')}</td></tr>
<tr><td style="color:#666;">Insurance contact</td><td>{fields.get('insurance_contact','-')}</td></tr></table>
<h2 style="font-size:16px;border-bottom:1px solid #e5e5e5;padding-bottom:6px;margin-top:20px;">Call Recording</h2>
<div style="background:#f5f5f5;border-radius:6px;padding:14px 16px;font-size:14px;">
{'<a href="' + rec + '" style="display:inline-block;padding:8px 14px;background:#2563eb;color:#fff;text-decoration:none;border-radius:4px;font-size:13px;font-weight:600;">Play recording (.wav)</a>' if rec else 'No recording URL available.'}
{'<br><br><a href="' + multi + '" style="color:#2563eb;font-size:13px;">Multi-channel recording (caller + receptionist on separate tracks)</a>' if multi else ''}
</div>
<h2 style="font-size:16px;border-bottom:1px solid #e5e5e5;padding-bottom:6px;margin-top:20px;">Callback</h2>
<div style="background:#f5f5f5;border-radius:6px;padding:12px 16px;font-size:14px;">
  <strong>{firm.get('calendar',{}).get('event_template', firm['name']+' — Consultation')} — {fields['caller_name']}</strong><br>
  <span style="color:#666;">{slot_str}</span>
</div>
<h2 style="font-size:16px;border-bottom:1px solid #e5e5e5;padding-bottom:6px;margin-top:20px;">Action Required</h2>
<ol style="font-size:14px;line-height:1.8;padding-left:20px;">
  <li>Listen to the recording before the callback</li>
  <li>Pull any prior history if {fields['caller_name']} is an existing contact</li>
  <li>Call {fields['callback_phone']} at the scheduled time</li>
</ol>
<div style="margin-top:32px;padding-top:16px;border-top:1px solid #e5e5e5;font-size:11px;color:#999;text-align:center;">
  Generated automatically by the {firm['name']} AI Intake System.
</div></body></html>"""
    return subject, html


# --- Validation gate (same rules as voice_email_gate.ps1) ------------------

def validate_email(subject: str, body: str, to: str) -> list[str]:
    errors = []
    low_s = subject.lower()
    low_b = body.lower()
    for term in FORBIDDEN_VENDOR_TERMS:
        if term in low_s:
            errors.append(f"Subject contains forbidden term: {term}")
        if term in low_b:
            errors.append(f"Body contains forbidden term: {term}")
    if not SUBJECT_PREFIX_RE.match(subject):
        errors.append("Subject must start with [Firm Name]")
    for section in REQUIRED_SECTIONS:
        if section.lower() not in low_b:
            errors.append(f"Missing required section: {section}")
    if not to or "@" not in to:
        errors.append(f"Invalid recipient: {to}")
    return errors


# --- Routes ---------------------------------------------------------------

@app.get("/")
async def root():
    return {"service": "voice_team_webhook", "status": "ok"}


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/retell/webhook")
async def retell_webhook(req: Request):
    body_bytes = await req.body()
    sig = req.headers.get("x-retell-signature")
    if not verify_signature(body_bytes, sig):
        log.warning("Invalid signature on Retell webhook")
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = json.loads(body_bytes)
    event = payload.get("event")
    call = payload.get("call", {})
    call_id = call.get("call_id")
    log.info("event=%s call_id=%s", event, call_id)

    # Only act on call_analyzed (post-call analysis ready). Ignore other events.
    if event != "call_analyzed":
        return {"status": "ignored", "event": event}

    # Identify firm by inbound phone number
    phone = call.get("to_number") or ""
    firm_doc = load_firm_by_phone(phone)
    if not firm_doc:
        log.warning("No firm config matches phone %s", phone)
        return {"status": "no_firm_match", "phone": phone}
    firm = firm_doc["firm"]

    # Optional fresh fetch (Retell sometimes sends partial data in webhook)
    try:
        call = fetch_call(call_id)
    except Exception as e:
        log.warning("Fresh fetch failed, using webhook payload: %s", e)

    fields = extract_fields(call)
    if fields["outside_practice"]:
        log.info("Out-of-practice caller, skipping booking")
        return {"status": "skipped_out_of_practice"}
    if fields["caller_name"] == "Unknown caller":
        log.info("No caller name captured (probably a hang-up)")
        return {"status": "skipped_no_name"}

    tz_name = (firm_doc.get("calendar") or {}).get("timezone") or "America/New_York"
    slot_dt = parse_slot(fields["preferred_day"], fields["preferred_time"], tz_name)

    # 1) Calendar event — surface errors in the response (not just logs) so we can diagnose.
    booked = None
    calendar_status = "skipped_no_slot"
    calendar_error = None
    if slot_dt:
        duration = (firm_doc.get("calendar") or {}).get("event_duration_min", 30)
        end_dt = slot_dt + timedelta(minutes=duration)
        cal_id = (firm_doc.get("calendar") or {}).get("google_calendar_id") or "primary"
        cal_summary = f"{firm.get('calendar',{}).get('event_template', firm['name'] + ' — Consultation')} — {fields['caller_name']}"
        cal_desc = (
            f"Caller: {fields['caller_name']}\n"
            f"Phone: {fields['callback_phone']}\n"
            f"Incident: {fields['incident_type']} ({fields['incident_date']})\n"
            f"Injured: {fields['currently_injured']}\n"
            f"Urgency: {fields['urgency']}\n"
            f"Case quality: {fields['case_quality']}\n\n"
            f"Recording: {fields.get('recording_url','')}\n\n"
            f"AI summary:\n{fields.get('call_summary','')}"
        )
        log.info(
            "Calendar attempt: cal_id=%s start=%s end=%s tz=%s",
            cal_id, slot_dt.isoformat(), end_dt.isoformat(), tz_name,
        )
        try:
            booked = create_calendar_event(cal_id, cal_summary, cal_desc, slot_dt.isoformat(), end_dt.isoformat(), tz_name)
            calendar_status = "ok"
            log.info("Calendar event created: %s", booked.get("id"))
        except httpx.HTTPStatusError as e:
            calendar_status = f"http_error_{e.response.status_code}"
            calendar_error = f"{e.response.status_code}: {e.response.text[:500]}"
            log.error("Calendar HTTP error: %s body=%s", e.response.status_code, e.response.text)
        except Exception as e:
            calendar_status = "exception"
            calendar_error = f"{type(e).__name__}: {e}"
            log.exception("Calendar event failed: %s", e)

    # 2) Email summary
    subject, body_html = build_email_html(firm, fields, slot_dt)
    notify_to = firm.get("notification_email") or (firm_doc.get("notifications") or {}).get("intake_email") or GOOGLE_USER_EMAIL
    errors = validate_email(subject, body_html, notify_to)
    if errors:
        log.error("Email validation failed for call %s: %s", call_id, errors)
        return {"status": "email_validation_failed", "errors": errors, "calendar": booked}

    try:
        send_result = send_gmail(notify_to, subject, body_html)
        log.info("Email sent to %s: %s", notify_to, send_result.get("id"))
    except Exception as e:
        log.exception("Email send failed: %s", e)
        return {"status": "email_send_failed", "error": str(e), "calendar": booked}

    return {
        "status": "ok",
        "call_id": call_id,
        "firm": firm["slug"],
        "calendar_status": calendar_status,
        "calendar_event_id": (booked or {}).get("id"),
        "calendar_error": calendar_error,
        "slot_preferred_day": fields.get("preferred_day"),
        "slot_preferred_time": fields.get("preferred_time"),
        "slot_parsed_iso": slot_dt.isoformat() if slot_dt else None,
        "email_to": notify_to,
    }
