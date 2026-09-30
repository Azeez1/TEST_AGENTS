"""Evaluate deterministic routing contracts; no LLM calls or external actions."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.workspace_registry import discover_agents, get_team


def resolve_workflow(name: str, available_capabilities: list[str], authorized_actions: list[str]) -> dict:
    catalog = json.loads((ROOT / "CODEX_TEAM/config/workflows.json").read_text(encoding="utf-8"))
    workflow = catalog["workflows"][name]
    missing = sorted(set(workflow["required_capabilities"]) - set(available_capabilities))
    unauthorized = sorted(set(workflow["external_actions"]) - set(authorized_actions))
    return {**workflow, "workflow": name, "model_policy": catalog["model_policy"],
            "output_root": get_team(workflow["team"])["outputs"],
            "status": "blocked" if missing or unauthorized else "ready",
            "missing_capabilities": missing, "unauthorized_actions": unauthorized}


def evaluate() -> dict:
    fixtures = json.loads((ROOT / "CODEX_TEAM/config/workflow-evals.json").read_text(encoding="utf-8"))
    sources = discover_agents()
    outcomes = []
    for case in fixtures["cases"]:
        result = resolve_workflow(case["workflow"], case["available_capabilities"], case["authorized_actions"])
        roles = {p.stem for p in sources[result["team"]]}
        valid = (result["owner"] == case["expected_owner"] and result["status"] == case["expected_status"]
                 and result["owner"] in roles and bool(result["acceptance_checks"])
                 and set(result["related_roles"]).issubset(roles))
        outcomes.append({"id": case["id"], "passed": valid, "owner": result["owner"], "status": result["status"]})
    return {"ok": all(item["passed"] for item in outcomes), "scope": fixtures["scope"], "cases": outcomes}


if __name__ == "__main__":
    report = evaluate()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
