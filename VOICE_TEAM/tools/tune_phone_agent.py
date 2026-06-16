"""Tune the live phone-line agent for a more natural, less robotic feel.
Enables backchanneling and nudges responsiveness/interruption to near-max.
Reversible: re-run with prior values, or it prints the before-state first.
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
if not agent_id:
    sys.exit("no inbound agent bound")

before = httpx.get(f"{BASE}/get-agent/{agent_id}", headers=H, timeout=20).json()
show = ["responsiveness", "interruption_sensitivity", "enable_backchannel",
        "backchannel_frequency", "backchannel_words"]
print("BEFORE:", json.dumps({k: before.get(k) for k in show}, indent=1))

patch = {
    "responsiveness": 0.95,
    "interruption_sensitivity": 0.85,
    "enable_backchannel": True,
    "backchannel_frequency": 0.8,
    "backchannel_words": ["yeah", "mhm", "uh-huh", "right", "got it"],
}
r = httpx.patch(f"{BASE}/update-agent/{agent_id}", headers=H, json=patch, timeout=20)
r.raise_for_status()
after = r.json()
print("AFTER:", json.dumps({k: after.get(k) for k in show}, indent=1))
print("OK — tuned agent", agent_id)
