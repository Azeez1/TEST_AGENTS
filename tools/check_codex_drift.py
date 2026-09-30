"""Content-based drift checks for both source runtimes; no mtime assumptions."""
from __future__ import annotations

import json
import sys
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.export_codex_layer import content_hash, parse_frontmatter, parse_skill_frontmatter
from tools.workspace_registry import contained_path, discover_agents


def check_drift(root: Path = REPO) -> dict:
    findings, warnings = [], []
    try:
        manifest = json.loads((root / ".codex/manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schema") != "test-agents/codex-layer/v2":
            findings.append("Manifest schema must be test-agents/codex-layer/v2")
        discovered = {p.relative_to(root).as_posix() for paths in discover_agents(root).values() for p in paths}
        recorded = [a["source"] for a in manifest["agents"]]
        if len(recorded) != len(set(recorded)):
            findings.append("Duplicate manifest agent source")
        findings += [f"Unexported source: {p}" for p in sorted(discovered - set(recorded))]
        findings += [f"Missing source: {p}" for p in sorted(set(recorded) - discovered)]
        expected_outputs = set()
        for agent in manifest["agents"]:
            source = contained_path(root, agent["source"])
            mirror = contained_path(root / ".codex/agents", root / agent["codex_instructions"])
            expected_outputs.add(mirror)
            if not source.is_file() or not mirror.is_file():
                findings.append(f"Missing agent file: {agent['source']}")
                continue
            source_text = source.read_text(encoding="utf-8-sig")
            text = mirror.read_text(encoding="utf-8")
            header, _ = parse_frontmatter(text)
            if not header.get("description") or header.get("model_policy") != "inherit_session_unless_user_selects":
                findings.append(f"Invalid generated metadata: {agent['slug']}")
            if content_hash(source_text) != agent.get("source_sha256"):
                findings.append(f"Changed source: {agent['source']}")
            if content_hash(text) != agent.get("rendered_sha256"):
                findings.append(f"Changed generated file: {agent['codex_instructions']}")
        findings += [f"Obsolete generated agent: {p.relative_to(root)}"
                     for p in (root / ".codex/agents").rglob("*.md") if p.resolve() not in expected_outputs]
        for skill in manifest.get("skills", []):
            if skill.get("status") == "missing_source":
                findings.append(f"Missing skill source: {skill['name']}")
            if skill.get("codexPath") and not contained_path(root, skill["codexPath"]).is_file():
                findings.append(f"Missing skill file: {skill['name']}")
            if skill.get("skippedFiles"):
                warnings.append(f"Skill assets were unavailable during export: {skill['name']}")
            if skill.get("source") not in (None, "generated"):
                source = contained_path(root, skill["source"]) / "SKILL.md"
                mirror = contained_path(root, skill["codexPath"])
                if not source.is_file():
                    findings.append(f"Missing skill source: {skill['name']}")
                elif mirror.is_file():
                    src_header, src_body = parse_skill_frontmatter(source.read_text(encoding="utf-8-sig"))
                    dst_header, dst_body = parse_frontmatter(mirror.read_text(encoding="utf-8-sig"))
                    if src_body.lstrip() != dst_body.lstrip() or src_header.get("description") != dst_header.get("description"):
                        findings.append(f"Changed skill instructions: {skill['name']}")
        return {"ok": not findings, "drift_count": len(findings), "findings": findings,
                "warnings": warnings, "agents": len(manifest["agents"]),
                "scope": "Agent hashes and skill instructions; binary skill assets and live integrations are not checked"}
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        return {"ok": False, "drift_count": 1, "findings": [str(exc)], "warnings": []}


def main() -> None:
    result = check_drift()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
