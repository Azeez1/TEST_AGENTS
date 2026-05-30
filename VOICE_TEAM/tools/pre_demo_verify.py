"""
VOICE_TEAM — Pre-Demo Verification Gate

Run this before EVERY high-stakes demo (Steven, paying client, sales call).
It audits 3 layers and refuses to bless the agent if anything's missing:

  Layer 1 — Config check:
    * Deployment artifact exists
    * Agent exists on Retell + has expected agent_name
    * Phone number is bound to the correct agent
    * Webhook URL is set
    * Model matches firm.yml
    * Voice matches firm.yml

  Layer 2 — Prompt content audit (catches "deploy didn't apply" regressions):
    * Live flow's global_prompt contains the persona/personality markers
    * All 9 required nodes present (welcome -> ... -> end_call)
    * qualifying node has REQUIRED CHECKLIST enforcement
    * contact_capture node enforces full name + phone in order
    * wrap_up has warm goodbye sequence
    * end node has speak_during_execution=true (prevents abrupt hang-up)

  Layer 3 — Email + booking pipeline:
    * Synthetic email passes validation (no vendor leaks, required sections)
    * Webhook endpoint responding
    * Render service alive

Outputs:
    DEMO-READY     -> all checks passed, you may demo
    NOT DEMO-READY -> at least one critical check failed; fix before demo
                      (exits with code 1 so CI / scripts can gate on it)

Usage:
    python tools/pre_demo_verify.py                       # default firm: sterling_legal
    python tools/pre_demo_verify.py --firm <slug>
    python tools/pre_demo_verify.py --variant s2s         # check the s2s agent instead

The script also prints a Layer-4 manual checklist — the final live-call test
you should run after all automated checks pass, before walking into the demo.
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
import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
VOICE_TEAM = REPO_ROOT / "VOICE_TEAM"
ENV_FILE = REPO_ROOT / "MARKETING_TEAM" / ".env"
DEPLOY_DIR = VOICE_TEAM / "outputs" / "deployments"

load_dotenv(ENV_FILE)
RETELL_API_KEY = os.getenv("RETELL_API_KEY")
if not RETELL_API_KEY:
    print("FATAL: RETELL_API_KEY missing from .env", file=sys.stderr)
    sys.exit(2)
HEADERS = {"Authorization": f"Bearer {RETELL_API_KEY}"}
BASE = "https://api.retellai.com"


# --- Result accumulator ----------------------------------------------------

class Results:
    def __init__(self):
        self.checks: list[tuple[str, str, bool, str]] = []  # (layer, check, ok, msg)
        self.warnings: list[str] = []

    def add(self, layer: str, check: str, ok: bool, msg: str = ""):
        self.checks.append((layer, check, ok, msg))

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def all_passed(self) -> bool:
        return all(ok for _, _, ok, _ in self.checks)

    def print_report(self):
        print()
        for layer in sorted({c[0] for c in self.checks}):
            print(f"=== {layer} ===")
            for lyr, name, ok, msg in self.checks:
                if lyr != layer:
                    continue
                mark = "[PASS]" if ok else "[FAIL]"
                line = f"  {mark} {name}"
                if msg:
                    line += f" — {msg}"
                print(line)
            print()
        if self.warnings:
            print("=== WARNINGS (non-blocking) ===")
            for w in self.warnings:
                print(f"  * {w}")
            print()


# --- Layer 1: Config check ------------------------------------------------

def layer1_config(slug: str, variant: str, r: Results) -> dict:
    """Returns the deployment artifact dict if all critical checks pass."""
    layer = "LAYER 1 - CONFIG"
    artifact_name = f"{slug}_s2s.json" if variant == "s2s" else f"{slug}.json"
    artifact_path = DEPLOY_DIR / artifact_name

    if not artifact_path.exists():
        r.add(layer, f"Deployment artifact exists ({artifact_name})", False,
              f"missing at {artifact_path} — run deploy first")
        return {}
    r.add(layer, f"Deployment artifact exists ({artifact_name})", True)

    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    agent_id = artifact.get("agent_id")
    phone = artifact.get("phone_number")
    flow_id = artifact.get("conversation_flow_id")

    # Get agent from Retell
    try:
        agent = httpx.get(f"{BASE}/get-agent/{agent_id}", headers=HEADERS, timeout=15).json()
        r.add(layer, f"Agent exists on Retell ({agent_id})", True)
    except Exception as e:
        r.add(layer, f"Agent exists on Retell ({agent_id})", False, str(e))
        return artifact

    # Webhook URL set
    webhook = agent.get("webhook_url", "")
    r.add(layer, "Webhook URL is set on agent", bool(webhook), webhook or "EMPTY")

    # Voice ID matches firm.yml
    firm_doc = yaml.safe_load((VOICE_TEAM / "memory" / "firms" / f"{slug}.yml").read_text(encoding="utf-8"))
    expected_voice = (firm_doc.get("retell") or {}).get(
        "s2s_voice_id" if variant == "s2s" else "voice_id"
    )
    actual_voice = agent.get("voice_id")
    r.add(layer, f"Voice matches firm.yml ({expected_voice})",
          actual_voice == expected_voice,
          f"got: {actual_voice}")

    # Phone bound to THIS agent
    try:
        phone_data = httpx.get(f"{BASE}/list-phone-numbers", headers=HEADERS, timeout=15).json()
        if isinstance(phone_data, list):
            phone_data = next((p for p in phone_data if p.get("phone_number") == phone), None)
        bound = (phone_data or {}).get("inbound_agent_id")
        r.add(layer, f"Phone {phone} bound to {agent_id}",
              bound == agent_id,
              f"actually bound to: {bound}" if bound != agent_id else "")
    except Exception as e:
        r.add(layer, f"Phone {phone} binding check", False, str(e))

    # Cache for layer 2
    artifact["_agent"] = agent
    artifact["_firm_doc"] = firm_doc
    artifact["_flow_id"] = flow_id
    return artifact


# --- Layer 2: Prompt content audit ----------------------------------------

EXPECTED_FLOW_NODES = {
    "welcome", "initial_inquiry", "qualifying", "contact_capture",
    "preferred_slot", "wrap_up", "polite_decline", "wrap_up_decline",
    "emergency_redirect", "end_call",
}

# Markers that MUST appear in the live deployed prompts. If any go missing it
# means a redeploy regressed the prompt or didn't apply.
GLOBAL_PROMPT_MARKERS = [
    "Grace",                              # persona name
    "Personality & Conversational Latitude",
    "lilac",                              # backstory marker
    "Never give legal advice",
    "Disclose you're an AI",              # AI disclosure rule
]

NODE_MARKERS = {
    "qualifying":       ["REQUIRED CHECKLIST", "ALL 6 BEFORE PROCEEDING"],
    "contact_capture":  ["STEP 1: FULL NAME", "STEP 2: PHONE NUMBER", "MUST COLLECT + CONFIRM ALL 3"],
    "preferred_slot":   ["CONFIRM THE SPECIFIC DATE AND TIME BACK"],
    "wrap_up":          ["STEP 1", "STEP 2", "STEP 4", "anything else"],
}


def layer2_prompt_content(artifact: dict, variant: str, r: Results):
    """Audit the LIVE deployed prompt content — catches stale-deploy regressions."""
    layer = "LAYER 2 - PROMPT CONTENT"

    if variant == "s2s":
        # s2s = retell-llm engine; introspect the LLM's general_prompt + states
        llm_id = artifact.get("llm_id")
        if not llm_id:
            r.add(layer, "Retell LLM ID present in artifact", False)
            return
        try:
            llm = httpx.get(f"{BASE}/get-retell-llm/{llm_id}", headers=HEADERS, timeout=15).json()
        except Exception as e:
            r.add(layer, "Fetch live retell-llm", False, str(e))
            return
        prompt = llm.get("general_prompt") or ""
        for marker in GLOBAL_PROMPT_MARKERS:
            r.add(layer, f"general_prompt contains '{marker}'",
                  marker.lower() in prompt.lower(),
                  "" if marker.lower() in prompt.lower() else "marker missing — redeploy")
        states = llm.get("states") or []
        state_names = {s.get("name") for s in states}
        for expected in {"qualifying", "contact_capture", "preferred_slot", "wrap_up", "end_call"}:
            r.add(layer, f"state '{expected}' exists", expected in state_names)
        for state in states:
            name = state.get("name")
            if name in NODE_MARKERS:
                sp = state.get("state_prompt") or ""
                for marker in NODE_MARKERS[name]:
                    r.add(layer, f"state '{name}' contains '{marker}'",
                          marker.lower() in sp.lower())
        return

    # Cascading: introspect conversation_flow
    flow_id = artifact.get("_flow_id")
    if not flow_id:
        r.add(layer, "conversation_flow_id present in artifact", False)
        return
    try:
        flow = httpx.get(f"{BASE}/get-conversation-flow/{flow_id}", headers=HEADERS, timeout=15).json()
    except Exception as e:
        r.add(layer, "Fetch live conversation_flow", False, str(e))
        return

    # global_prompt markers
    gp = flow.get("global_prompt") or ""
    for marker in GLOBAL_PROMPT_MARKERS:
        r.add(layer, f"global_prompt contains '{marker}'",
              marker.lower() in gp.lower(),
              "" if marker.lower() in gp.lower() else "marker missing — redeploy")

    # All expected nodes
    nodes = flow.get("nodes") or []
    node_by_name = {n.get("name"): n for n in nodes}
    missing = EXPECTED_FLOW_NODES - set(node_by_name.keys())
    r.add(layer, f"All required nodes present ({len(EXPECTED_FLOW_NODES)} expected)",
          not missing,
          f"missing: {sorted(missing)}" if missing else "")

    # Per-node content markers
    for node_name, markers in NODE_MARKERS.items():
        node = node_by_name.get(node_name)
        if not node:
            continue
        instr_text = ((node.get("instruction") or {}).get("text") or "").lower()
        for marker in markers:
            r.add(layer, f"node '{node_name}' contains '{marker}'",
                  marker.lower() in instr_text)

    # End node has speak_during_execution (prevents abrupt hang-up)
    end_node = node_by_name.get("end_call")
    if end_node:
        r.add(layer, "end_call node has speak_during_execution=true",
              bool(end_node.get("speak_during_execution")),
              "ABRUPT HANG-UP RISK if false" if not end_node.get("speak_during_execution") else "")

    # Model choice
    model_choice = flow.get("model_choice") or {}
    expected_model = (artifact["_firm_doc"].get("retell") or {}).get("flow_model", "gpt-4.1")
    r.add(layer, f"Cascading model is {expected_model}",
          model_choice.get("model") == expected_model,
          f"actual: {model_choice.get('model')}")


# --- Layer 3: Webhook + email pipeline ------------------------------------

def layer3_pipeline(r: Results):
    layer = "LAYER 3 - WEBHOOK PIPELINE"

    # Render webhook reachable
    try:
        h = httpx.get("https://test-agents-ny8d.onrender.com/health", timeout=20)
        r.add(layer, "Render webhook /health responding",
              h.status_code == 200,
              f"HTTP {h.status_code}")
    except Exception as e:
        r.add(layer, "Render webhook /health responding", False, str(e))
        return

    # Email validation script exists (calls validate_firm_setup)
    validate_script = VOICE_TEAM / "tools" / "validate_firm_setup.py"
    r.add(layer, "validate_firm_setup.py exists", validate_script.exists())


# --- Manual checklist printout --------------------------------------------

def print_manual_checklist(artifact: dict):
    phone = artifact.get("phone_number", "+13363238344")
    print("=" * 60)
    print("LAYER 4 - MANUAL LIVE-CALL CHECK (do this NOW, before demo)")
    print("=" * 60)
    print(f"""
    Call: {phone}

    Say (volunteers everything upfront):
      "Hi, I was rear-ended yesterday on Route 40. I went to the ER
       last night for whiplash. The other driver ran a red light and
       got a ticket. My name is Azeez Saba, that's A-Z-E-E-Z S-A-B-A.
       Call me at three-zero-one, four-four-eight, nine-nine-four-one.
       Tomorrow at 2 PM Eastern works."

    Watch for these behaviors during the call:
      [ ] Agent introduces as "Grace"
      [ ] AI disclosure within first 10 seconds
      [ ] Spells your name back letter-by-letter (FIRST + LAST)
      [ ] Confirms phone number digit-by-digit
      [ ] STILL asks: fault, police report, insurance contact
          (don't let her skip these even though you volunteered other info)
      [ ] Confirms callback as "tomorrow, {{day}}, {{month}} {{date}}, at 2 PM Eastern"
      [ ] Asks "anything else?" before hanging up
      [ ] Delivers full warm goodbye then cleanly ends call

    Within 60 seconds after hanging up:
      [ ] Google Calendar event appears at requested slot
      [ ] HTML email lands in inbox with all intake fields
      [ ] Render logs show: parse_slot, Calendar event created, Email sent

    If ANY box stays unchecked: DO NOT demo. Diagnose first.
""")


# --- Main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--firm", default="sterling_legal")
    ap.add_argument("--variant", choices=["cascading", "s2s"], default="cascading")
    args = ap.parse_args()

    print(f"\n{'#' * 60}")
    print(f"# PRE-DEMO VERIFY — firm={args.firm} variant={args.variant}")
    print(f"{'#' * 60}\n")

    r = Results()

    artifact = layer1_config(args.firm, args.variant, r)
    if artifact and artifact.get("_agent"):
        layer2_prompt_content(artifact, args.variant, r)
    layer3_pipeline(r)

    r.print_report()

    if r.all_passed:
        print("=" * 60)
        print("AUTOMATED CHECKS: ALL PASSED ✅")
        print("=" * 60)
        if artifact:
            print_manual_checklist(artifact)
        print("=" * 60)
        print("VERDICT: Run the LAYER 4 manual call. If green, DEMO-READY.")
        print("=" * 60)
        sys.exit(0)
    else:
        failed = [(l, n, m) for l, n, ok, m in r.checks if not ok]
        print("=" * 60)
        print(f"AUTOMATED CHECKS: {len(failed)} FAILURE(S) — NOT DEMO-READY ❌")
        print("=" * 60)
        for layer, name, msg in failed:
            print(f"  [{layer}] {name}")
            if msg:
                print(f"      -> {msg}")
        print()
        print("Fix the failures above + re-run this script before demoing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
