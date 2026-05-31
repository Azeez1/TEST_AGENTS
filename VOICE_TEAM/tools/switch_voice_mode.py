"""
VOICE_TEAM — Switch Voice Mode

Flips a firm's phone number between deployed agent variants without
destroying either. The phone number is just a pointer — this re-binds it.

Variants (read from deployment artifacts):
  realtime   -> <firm>_s2s.json  (gpt-realtime-2 + OpenAI voice, ~320ms)
  cascading  -> <firm>.json      (GPT-4.1 + ElevenLabs voice, ~500ms, warmer)

Usage:
    python switch_voice_mode.py realtime   [--firm sterling_legal]
    python switch_voice_mode.py cascading  [--firm sterling_legal]
    python switch_voice_mode.py status     [--firm sterling_legal]

Both agents stay deployed. Switching is instant and reversible forever.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
VOICE_TEAM = REPO_ROOT / "VOICE_TEAM"
ENV_FILE = REPO_ROOT / "MARKETING_TEAM" / ".env"
DEPLOY_DIR = VOICE_TEAM / "outputs" / "deployments"

load_dotenv(ENV_FILE)
RETELL_API_KEY = os.getenv("RETELL_API_KEY")
HEADERS = {"Authorization": f"Bearer {RETELL_API_KEY}", "Content-Type": "application/json"}
BASE = "https://api.retellai.com"


def _load_artifact(name: str) -> dict | None:
    p = DEPLOY_DIR / name
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["realtime", "cascading", "status"])
    ap.add_argument("--firm", default="sterling_legal")
    args = ap.parse_args()

    realtime = _load_artifact(f"{args.firm}_s2s.json")
    cascading = _load_artifact(f"{args.firm}.json")

    if not realtime and not cascading:
        print(f"FATAL: no deployment artifacts for '{args.firm}'", file=sys.stderr)
        sys.exit(1)

    phone = (realtime or cascading)["phone_number"]

    if args.mode == "status":
        p = httpx.get(f"{BASE}/list-phone-numbers", headers=HEADERS, timeout=15).json()
        if isinstance(p, list):
            p = next((x for x in p if x.get("phone_number") == phone), {})
        current = p.get("inbound_agent_id", "?")
        which = "realtime" if realtime and current == realtime.get("agent_id") else \
                "cascading" if cascading and current == cascading.get("agent_id") else "unknown"
        print(f"Phone {phone} -> {current}  [{which}]")
        if realtime:
            print(f"  realtime  agent: {realtime['agent_id']}  voice: {realtime.get('voice_id')}")
        if cascading:
            print(f"  cascading agent: {cascading['agent_id']}  voice: {cascading.get('voice_id')}")
        return

    target = realtime if args.mode == "realtime" else cascading
    if not target:
        print(f"FATAL: no '{args.mode}' deployment for '{args.firm}'. Deploy it first.", file=sys.stderr)
        sys.exit(1)

    agent_id = target["agent_id"]
    r = httpx.patch(
        f"{BASE}/update-phone-number/{phone}",
        headers=HEADERS,
        json={"inbound_agent_id": agent_id},
        timeout=15,
    )
    r.raise_for_status()
    print(f"✓ Switched to {args.mode.upper()}")
    print(f"  Phone {phone} -> {agent_id}")
    print(f"  Voice: {target.get('voice_id')}")
    print(f"  Call {phone} to hear it.")


if __name__ == "__main__":
    main()
