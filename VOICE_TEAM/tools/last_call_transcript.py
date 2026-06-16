"""Pull the most recent call's full two-sided transcript from Retell for review."""
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
load_dotenv(REPO / "MARKETING_TEAM" / ".env")
KEY = os.getenv("RETELL_API_KEY")
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
BASE = "https://api.retellai.com"

r = httpx.post(f"{BASE}/v2/list-calls", headers=H, json={"limit": 3, "sort_order": "descending"}, timeout=20)
r.raise_for_status()
calls = r.json()
if not calls:
    raise SystemExit("no calls found")
c = calls[0]
print("call_id:", c.get("call_id"))
print("from:", c.get("from_number"), " duration_ms:", (c.get("call_cost") or {}).get("total_duration_seconds"))
print("disconnect_reason:", c.get("disconnection_reason"))
print("=" * 60)
print(c.get("transcript") or "(no transcript field)")
