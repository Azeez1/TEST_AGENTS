"""
VOICE_TEAM Factory — Retell SPEECH-TO-SPEECH (Realtime 2) Deployment Script

Multi-Prompt edition — converts our intake_flow_template.yml node graph into
Retell `states`, giving us the structured state-machine that prevents looping
while keeping Realtime latency.

Idempotent: if a deployment artifact exists for this firm at
outputs/deployments/<slug>_s2s.json, PATCHes the existing LLM + agent instead
of creating new ones (no orphaning resources on every redeploy).

Usage:
    python deploy_retell_agent_s2s.py memory/firms/sterling_legal.yml

Dependencies:
    pip install pyyaml jinja2 httpx python-dotenv

Author: VOICE_TEAM Factory
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import httpx
import yaml
from dotenv import load_dotenv
from jinja2 import Template

# --- Paths -----------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
VOICE_TEAM = REPO_ROOT / "VOICE_TEAM"
ENV_FILE = REPO_ROOT / "MARKETING_TEAM" / ".env"
VOICE_CONFIG = VOICE_TEAM / "memory" / "voice_config.json"
OUTPUT_PATHS = VOICE_TEAM / "memory" / "output_paths.json"
GLOBAL_PROMPT_TEMPLATE = VOICE_TEAM / "prompts" / "global_prompt_template.md"
INTAKE_FLOW_TEMPLATE = VOICE_TEAM / "prompts" / "intake_flow_template.yml"

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


# --- HTTP helpers ----------------------------------------------------------

def _api(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{RETELL_BASE}{path}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.request(method, url, headers=HEADERS, json=body)
    if resp.status_code >= 400:
        print(f"\n[ERROR] {method} {url} returned {resp.status_code}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        resp.raise_for_status()
    return resp.json() if resp.text else {}


def _render(template_path: Path, context: dict[str, Any]) -> str:
    return Template(template_path.read_text(encoding="utf-8")).render(**context)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


# --- Convert intake_flow_template.yml → Retell `states` -------------------

TERMINAL_TARGETS = {"end_call"}


def build_states(intake_template: dict, firm: dict) -> list[dict]:
    """
    Translate the declarative intake_flow_template.yml node graph into Retell
    multi-prompt `states`. Each non-end node becomes a state. Always_edges
    and conditional edges become `edges` on the state. Nodes whose always_edge
    points at `end_call` get an `end_call` tool attached instead of a transition.
    """
    nodes = [n for n in intake_template["nodes"] if n["type"] != "end"]
    states: list[dict] = []

    for n in nodes:
        # Render the state's focused instruction
        state_prompt = Template(n["instruction"]["text"]).render(firm=firm).strip()

        # Build edges
        edges: list[dict] = []

        # Conditional edges (e.g., initial_inquiry → qualifying / polite_decline / emergency)
        for e in n.get("edges", []) or []:
            if e["to"] in TERMINAL_TARGETS:
                continue  # handled via end_call tool, not as a state transition
            edges.append({
                "destination_state_name": e["to"],
                "description": Template(e["condition"]).render(firm=firm).strip(),
            })

        # Single unconditional transition (always_edge)
        always = n.get("always_edge")
        if always and always not in TERMINAL_TARGETS:
            edges.append({
                "destination_state_name": always,
                "description": "Move forward to this next phase once you have completed the goal of the current state.",
            })

        # State-level tools: end_call attached to states whose always_edge → end_call
        state_tools: list[dict] = []
        if always in TERMINAL_TARGETS:
            state_tools.append({
                "type": "end_call",
                "name": f"end_call_from_{n['name']}",
                "description": (
                    "Hang up the call. CALL THIS IMMEDIATELY after you deliver your "
                    "closing line in this state. Do NOT wait for the caller to say "
                    "goodbye. Do NOT add additional sentences. Calling this function "
                    "is the ONLY way to actually end the call — without it the line "
                    "stays open and the caller hears silence."
                ),
            })

        state: dict[str, Any] = {
            "name": n["name"],
            "state_prompt": state_prompt,
            "edges": edges,
        }
        if state_tools:
            state["tools"] = state_tools

        states.append(state)

    return states


# --- Post-call analysis ---------------------------------------------------

def build_post_call_analysis(firm: dict) -> list[dict]:
    out: list[dict] = []
    for field in firm.get("post_call_analysis", []) or []:
        item: dict[str, Any] = {
            "type": field["type"],
            "name": field["name"],
            "description": field.get("description", ""),
        }
        if field["type"] == "enum":
            item["choices"] = field.get("choices", [])
        out.append(item)
    return out


# --- LLM + Agent body builders --------------------------------------------

def build_llm_body(firm_doc: dict, general_prompt: str, states: list[dict]) -> dict[str, Any]:
    firm = firm_doc["firm"]
    retell_cfg = firm_doc.get("retell", {})
    s2s_model = retell_cfg.get("s2s_model") or "gpt-realtime-2"
    begin_message = (
        f"Hi, thank you for calling {firm['name']}. I'm the AI assistant — "
        f"your call may be recorded. How can I help you today?"
    )
    return {
        "s2s_model": s2s_model,
        "model_temperature": retell_cfg.get("llm_temperature", 0.3),
        "model_high_priority": retell_cfg.get("fast_tier", True),
        "tool_call_strict_mode": True,
        "start_speaker": "agent",
        "begin_message": begin_message,
        "general_prompt": general_prompt,
        "starting_state": states[0]["name"],
        "states": states,
    }


def build_agent_body(firm_doc: dict, llm_id: str) -> dict[str, Any]:
    firm = firm_doc["firm"]
    retell_cfg = firm_doc.get("retell", {})
    s2s_voice_id = (
        retell_cfg.get("s2s_voice_id")
        or VOICE_CFG.get("voice", {}).get("s2s_default_voice_id")
        or "openai-Marin"
    )
    return {
        "response_engine": {"type": "retell-llm", "llm_id": llm_id},
        "agent_name": f"{firm['name']} — Voice Receptionist (S2S MP)",
        "voice_id": s2s_voice_id,
        "language": retell_cfg.get("language", "en-US"),
        "data_storage_setting": VOICE_CFG["compliance"]["data_storage_setting"],
        "max_call_duration_ms": VOICE_CFG["retell"]["max_call_duration_ms"],
        "interruption_sensitivity": retell_cfg.get(
            "interruption_sensitivity", VOICE_CFG["retell"]["interruption_sensitivity"]
        ),
        "stt_mode": VOICE_CFG["retell"]["stt_mode"],
        "normalize_for_speech": VOICE_CFG["retell"]["normalize_for_speech"],
        "denoising_mode": VOICE_CFG["retell"]["denoising_mode"],
        "post_call_analysis_model": VOICE_CFG["retell"]["post_call_analysis_model"],
        "post_call_analysis_data": build_post_call_analysis(firm_doc),
        "handbook_config": VOICE_CFG["handbook_defaults"].copy(),
        "pii_config": {"mode": VOICE_CFG["compliance"]["pii_redaction_mode"], "categories": []},
        "timezone": VOICE_CFG["google_calendar"]["default_timezone"],
    }


# --- Main deploy / re-deploy pipeline -------------------------------------

def load_existing_artifact(firm_slug: str) -> dict[str, Any] | None:
    p = Path(PATHS["deployments"]) / f"{firm_slug}_s2s.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def deploy_s2s(firm_yml_path: Path) -> dict[str, Any]:
    firm_doc = yaml.safe_load(firm_yml_path.read_text(encoding="utf-8"))
    firm = firm_doc["firm"]
    retell_cfg = firm_doc.get("retell", {})

    print(f"\n=== Deploying [S2S MULTI-PROMPT] agent for: {firm['name']} ({firm['slug']}) ===")

    # 1. Render the general prompt (identity / rules / tone)
    general_prompt = _render(GLOBAL_PROMPT_TEMPLATE, {"firm": firm})

    # 2. Build the states array from intake_flow_template.yml
    intake_template = yaml.safe_load(INTAKE_FLOW_TEMPLATE.read_text(encoding="utf-8"))
    states = build_states(intake_template, firm)
    print(f"    Built {len(states)} states: {[s['name'] for s in states]}")
    print(f"    Starting state: {states[0]['name']}")

    # 3. Build the LLM body
    llm_body = build_llm_body(firm_doc, general_prompt, states)
    print(f"    s2s_model: {llm_body['s2s_model']}")

    # 4. Idempotent: PATCH if artifact exists, else POST
    existing = load_existing_artifact(firm["slug"])
    if existing and existing.get("llm_id") and existing.get("agent_id"):
        print(f"    Existing deployment found — PATCH mode")
        print(f"      llm_id: {existing['llm_id']}")
        print(f"      agent_id: {existing['agent_id']}")
        try:
            llm_resp = _api("PATCH", f"/update-retell-llm/{existing['llm_id']}", llm_body)
            llm_id = llm_resp.get("llm_id", existing["llm_id"])
            print(f"    ✓ LLM updated: {llm_id}")
        except httpx.HTTPStatusError as e:
            print(f"    [WARN] PATCH llm failed ({e.response.status_code}). Falling back to CREATE.")
            llm_resp = _api("POST", "/create-retell-llm", llm_body)
            llm_id = llm_resp["llm_id"]
            print(f"    ✓ LLM created (new): {llm_id}")

        agent_body = build_agent_body(firm_doc, llm_id)
        try:
            agent_resp = _api("PATCH", f"/update-agent/{existing['agent_id']}", agent_body)
            agent_id = agent_resp.get("agent_id", existing["agent_id"])
            print(f"    ✓ Agent updated: {agent_id}")
        except httpx.HTTPStatusError as e:
            print(f"    [WARN] PATCH agent failed ({e.response.status_code}). Falling back to CREATE.")
            agent_resp = _api("POST", "/create-agent", agent_body)
            agent_id = agent_resp["agent_id"]
            print(f"    ✓ Agent created (new): {agent_id}")
    else:
        print(f"    No existing deployment — CREATE mode")
        llm_resp = _api("POST", "/create-retell-llm", llm_body)
        llm_id = llm_resp["llm_id"]
        print(f"    ✓ LLM created: {llm_id}")

        agent_body = build_agent_body(firm_doc, llm_id)
        agent_resp = _api("POST", "/create-agent", agent_body)
        agent_id = agent_resp["agent_id"]
        print(f"    ✓ Agent created: {agent_id}")

    # 5. Ensure phone number is bound to this agent
    phone = retell_cfg.get("phone_number")
    if phone:
        print(f"    Binding phone {phone} → agent {agent_id}")
        _api("PATCH", f"/update-phone-number/{phone}", {"inbound_agent_id": agent_id})
        print(f"    ✓ Phone bound")

    # 6. Write/update artifact
    artifact = {
        "firm_slug": firm["slug"],
        "firm_name": firm["name"],
        "tier": "platinum",
        "engine": "retell-llm-s2s-multi-prompt",
        "agent_id": agent_id,
        "llm_id": llm_id,
        "s2s_model": llm_body["s2s_model"],
        "phone_number": phone,
        "voice_id": agent_body["voice_id"],
        "language": agent_body["language"],
        "state_names": [s["name"] for s in states],
        "starting_state": llm_body["starting_state"],
        "first_deployed_at": existing.get("first_deployed_at") if existing else _now_iso(),
        "last_modified": _now_iso(),
        "deployed_via": "deploy_retell_agent_s2s.py (multi-prompt)",
    }
    out_path = Path(PATHS["deployments"]) / f"{firm['slug']}_s2s.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\n    Artifact written: {out_path}")

    print(f"\n=== DEPLOY COMPLETE (S2S Multi-Prompt / Realtime 2) ===")
    print(f"    Call {phone} to test — state machine enforces flow, no looping.")
    print(f"    Dashboard: https://dashboard.retellai.com/agents/{agent_id}")
    return artifact


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_retell_agent_s2s.py <firm.yml path>", file=sys.stderr)
        sys.exit(1)
    firm_path = Path(sys.argv[1])
    if not firm_path.is_absolute():
        firm_path = (Path.cwd() / firm_path).resolve()
    if not firm_path.exists():
        print(f"FATAL: firm.yml not found at {firm_path}", file=sys.stderr)
        sys.exit(1)
    deploy_s2s(firm_path)
