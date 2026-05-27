"""
VOICE_TEAM Factory — Retell Agent Deployment Script

Reads a firm.yml config + global_prompt_template.md + intake_flow_template.yml,
builds a Retell Conversation Flow + Agent via the Retell API, attaches the phone
number from firm.yml, and writes a deployment artifact to outputs/deployments/.

Usage:
    python deploy_retell_agent.py memory/firms/sterling_legal.yml

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

# Windows cp1252 stdout chokes on Unicode (checkmarks, em-dashes) — force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import httpx
import yaml
from dotenv import load_dotenv
from jinja2 import Template

# --- Configuration discovery -------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]  # TEST_AGENTS/
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


# --- Helpers ----------------------------------------------------------------

def _api(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make an authenticated request to the Retell API and return the JSON body."""
    url = f"{RETELL_BASE}{path}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.request(method, url, headers=HEADERS, json=body)
    if resp.status_code >= 400:
        print(f"\n[ERROR] {method} {url} returned {resp.status_code}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        resp.raise_for_status()
    return resp.json() if resp.text else {}


def _render(template_path: Path, context: dict[str, Any]) -> str:
    """Render a Jinja template file against a context dict."""
    return Template(template_path.read_text(encoding="utf-8")).render(**context)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


# --- Flow node builder ------------------------------------------------------

def build_conversation_flow_nodes(intake_template: dict, firm: dict) -> list[dict]:
    """
    Translate the declarative intake_flow_template.yml into Retell's
    conversation_flow.nodes array. Edges by name are resolved here to
    deterministic node IDs we generate locally.
    """
    name_to_id: dict[str, str] = {}
    for idx, n in enumerate(intake_template["nodes"]):
        name_to_id[n["name"]] = f"node-voice-{firm['slug']}-{idx:02d}-{n['name']}"

    nodes_out: list[dict] = []
    x_position = 100
    for idx, n in enumerate(intake_template["nodes"]):
        if n["type"] == "end":
            # Retell's end node is implicit — we represent it as a real "end" type node.
            nodes_out.append({
                "id": name_to_id[n["name"]],
                "type": "end",
                "name": n["name"],
                "display_position": {"x": x_position + idx * 300, "y": 600},
            })
            continue

        # Render instruction text against firm context
        instr_text = Template(n["instruction"]["text"]).render(firm=firm)
        node = {
            "id": name_to_id[n["name"]],
            "type": n["type"],
            "name": n["name"],
            "instruction": {
                "type": n["instruction"]["type"],
                "text": instr_text,
            },
            "edges": [],
            "display_position": {"x": x_position + idx * 300, "y": 200 + (idx % 3) * 200},
        }
        if n.get("start_speaker"):
            node["start_speaker"] = n["start_speaker"]

        # Single unconditional transition
        if n.get("always_edge"):
            node["always_edge"] = {
                "id": f"edge-always-{idx:02d}",
                "destination_node_id": name_to_id[n["always_edge"]],
                "transition_condition": {"type": "prompt", "prompt": "Always"},
            }

        # Conditional transitions
        for e_idx, edge in enumerate(n.get("edges", []) or []):
            cond_text = Template(edge["condition"]).render(firm=firm)
            node["edges"].append({
                "id": f"edge-{idx:02d}-{e_idx}",
                "destination_node_id": name_to_id[edge["to"]],
                "transition_condition": {"type": "prompt", "prompt": cond_text},
            })

        # Tool attachment skipped for v1 — no custom functions.

        nodes_out.append(node)

    return nodes_out


# --- Function & post-call analysis builders ---------------------------------

def build_tools(firm: dict) -> list[dict]:
    """Build the Retell custom function (tool) definitions from firm.intake_functions."""
    tools: list[dict] = []
    for fn in firm.get("intake_functions", []) or []:
        params_schema: dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        for pname, pspec in fn.get("parameters", {}).items():
            prop: dict[str, Any] = {
                "type": pspec.get("type", "string"),
                "description": pspec.get("description", ""),
            }
            if "enum" in pspec:
                prop["enum"] = pspec["enum"]
            params_schema["properties"][pname] = prop
            if pspec.get("required"):
                params_schema["required"].append(pname)

        tools.append({
            "type": "custom",
            "name": fn["name"],
            "description": fn["description"],
            "parameters": params_schema,
            "speak_after_execution": fn.get("speak_after_execution", True),
            "execution_message_description": fn.get("description", ""),
            "url": "",  # No public endpoint Day 1 — slot capture is structured-only; book_pending_consults.py handles post-call.
            "response_variables": [],
        })
    return tools


def build_post_call_analysis(firm: dict) -> list[dict]:
    """Build the post_call_analysis_data array."""
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


# --- Main deploy pipeline ---------------------------------------------------

def deploy(firm_yml_path: Path) -> dict[str, Any]:
    firm_doc = yaml.safe_load(firm_yml_path.read_text(encoding="utf-8"))
    firm = firm_doc["firm"]
    retell_cfg = firm_doc.get("retell", {})

    print(f"\n=== Deploying agent for: {firm['name']} ({firm['slug']}) ===")

    # 1. Render global prompt
    global_prompt = _render(GLOBAL_PROMPT_TEMPLATE, {"firm": firm})
    print(f"  Rendered global prompt ({len(global_prompt)} chars)")

    # 2. Load intake flow template + build conversation flow nodes
    intake_template = yaml.safe_load(INTAKE_FLOW_TEMPLATE.read_text(encoding="utf-8"))
    nodes = build_conversation_flow_nodes(intake_template, firm)
    print(f"  Built {len(nodes)} conversation flow nodes")

    # 3. Skip custom functions for v1 — post_call_analysis_data on the agent already
    # captures Preferred Callback Day/Time/Urgency from the transcript automatically.
    # Custom functions are a v2 add-on for mid-call booking integrations.
    print("  Skipping custom functions for v1 (post_call_analysis handles slot capture).")

    # 4. POST conversation flow
    # Use safe defaults for v1 deploy. Realtime model upgrade is a v2 follow-up
    # once the cascading path is proven.
    flow_model = retell_cfg.get("flow_model", "gpt-4.1")
    flow_body = {
        "global_prompt": global_prompt,
        "nodes": nodes,
        "start_node_id": nodes[0]["id"],
        "start_speaker": "agent",
        "model_choice": {
            "type": "cascading",
            "model": flow_model,
            "high_priority": retell_cfg.get("fast_tier", True),
        },
        "tool_call_strict_mode": True,
    }
    print("  Creating conversation flow on Retell...")
    flow_resp = _api("POST", "/create-conversation-flow", flow_body)
    flow_id = flow_resp["conversation_flow_id"]
    print(f"  ✓ Flow created: {flow_id}")

    # 5. Build agent body
    handbook = VOICE_CFG["handbook_defaults"].copy()
    agent_body: dict[str, Any] = {
        "response_engine": {
            "type": "conversation-flow",
            "conversation_flow_id": flow_id,
        },
        "agent_name": f"{firm['name']} — Voice Receptionist",
        "voice_id": retell_cfg.get("voice_id") or VOICE_CFG["voice"]["default_voice_id"],
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
        "handbook_config": handbook,
        "pii_config": {"mode": VOICE_CFG["compliance"]["pii_redaction_mode"], "categories": []},
        "timezone": VOICE_CFG["google_calendar"]["default_timezone"],
    }

    print("  Creating agent on Retell...")
    agent_resp = _api("POST", "/create-agent", agent_body)
    agent_id = agent_resp["agent_id"]
    print(f"  ✓ Agent created: {agent_id}")

    # 6. Attach phone number
    phone = retell_cfg.get("phone_number") or firm_doc.get("retell", {}).get("phone_number")
    if phone:
        print(f"  Attaching phone {phone} to agent...")
        _api("PATCH", f"/update-phone-number/{phone}", {"inbound_agent_id": agent_id})
        print(f"  ✓ Phone {phone} → agent {agent_id}")

    # 7. Write deployment artifact
    artifact = {
        "firm_slug": firm["slug"],
        "firm_name": firm["name"],
        "agent_id": agent_id,
        "conversation_flow_id": flow_id,
        "phone_number": phone,
        "voice_id": agent_body["voice_id"],
        "language": agent_body["language"],
        "deployed_at": _now_iso(),
        "deployed_via": "deploy_retell_agent.py",
    }
    out_path = Path(PATHS["deployments"]) / f"{firm['slug']}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\n  Artifact written: {out_path}")

    print(f"\n=== DEPLOY COMPLETE ===")
    print(f"  Call {phone} to test.")
    print(f"  Dashboard: https://dashboard.retellai.com/agents/{agent_id}")
    return artifact


# --- Entrypoint -------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_retell_agent.py <firm.yml path>", file=sys.stderr)
        sys.exit(1)
    firm_path = Path(sys.argv[1])
    if not firm_path.is_absolute():
        firm_path = (Path.cwd() / firm_path).resolve()
    if not firm_path.exists():
        print(f"FATAL: firm.yml not found at {firm_path}", file=sys.stderr)
        sys.exit(1)
    deploy(firm_path)
