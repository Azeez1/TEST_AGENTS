"""Read-only: show the live phone-line agent's smoothness-relevant settings.
Uses the same RETELL_API_KEY location as the team's other voice tools.
"""
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
load_dotenv(REPO / "MARKETING_TEAM" / ".env")
KEY = os.getenv("RETELL_API_KEY")
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
BASE = "https://api.retellai.com"
PHONE = "+13363238344"

nums = httpx.get(f"{BASE}/list-phone-numbers", headers=H, timeout=20).json()
rec = next((x for x in nums if x.get("phone_number") == PHONE), {}) if isinstance(nums, list) else {}
agent_id = rec.get("inbound_agent_id")
print("bound inbound agent:", agent_id)

if not agent_id:
    sys.exit("no inbound agent bound")

a = httpx.get(f"{BASE}/get-agent/{agent_id}", headers=H, timeout=20).json()
keys = [
    "agent_name", "voice_id", "voice_model", "fallback_voice_ids", "voice_temperature",
    "voice_speed", "responsiveness", "interruption_sensitivity", "enable_backchannel",
    "backchannel_frequency", "backchannel_words", "reminder_trigger_ms", "reminder_max_count",
    "ambient_sound", "ambient_sound_volume", "language", "normalize_for_speech",
    "end_call_after_silence_ms", "max_call_duration_ms", "begin_message_delay_ms",
    "stt_mode", "vocab_specialization", "boosted_keywords", "denoising_mode",
    "response_engine",
]
print(json.dumps({k: a.get(k) for k in keys if k in a}, indent=2))
