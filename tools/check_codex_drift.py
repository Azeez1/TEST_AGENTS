"""Content-based drift checks for both source runtimes; no mtime assumptions."""
from __future__ import annotations

import json
import re
import sys
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.export_codex_layer import content_hash, parse_frontmatter, parse_skill_frontmatter
from tools.workspace_registry import contained_path, discover_agents

SCOPE = ("Checked: agent files (new, removed, changed), skill instructions, skills on disk "
         "missing from the manifest, hook scripts, MCP server list. Not checked: binary skill "
         "assets, the global ~/.codex/skills install, secrets values, slash commands (not "
         "mirrored by the exporter), and whether Codex itself loads or runs any of it.")


def check_unexported_skills(root: Path, manifest: dict) -> list[str]:
    """Skills present on disk but absent from the manifest (e.g. installed after the last sync)."""
    recorded = {s.get("name") for s in manifest.get("skills", [])}
    skills_dir = root / ".claude/skills"
    on_disk = {p.parent.name for p in skills_dir.rglob("SKILL.md")} if skills_dir.is_dir() else set()
    return [f"Unexported skill: {name}" for name in sorted(on_disk - recorded)]


def check_hooks(root: Path) -> list[str]:
    """Every Claude hook gate must have a byte-identical Codex copy."""
    src_dir, dst_dir = root / ".claude/hooks", root / ".codex/hooks"
    if not src_dir.is_dir():
        return []
    out = []
    for src in sorted(src_dir.glob("*.ps1")):
        dst = dst_dir / src.name
        if not dst.is_file():
            out.append(f"Missing hook mirror: {src.name}")
        elif src.read_bytes() != dst.read_bytes():
            out.append(f"Changed hook: {src.name}")
    return out


def check_mcp_servers(root: Path) -> list[str]:
    """Server names in .mcp.json must match .codex/mcp.generated.toml (both gitignored; skipped if absent)."""
    src, dst = root / ".mcp.json", root / ".codex/mcp.generated.toml"
    if not src.is_file() or not dst.is_file():
        return []
    claude = set(json.loads(src.read_text(encoding="utf-8-sig")).get("mcpServers", {}))
    codex = set(re.findall(r"^\[mcp_servers\.([^\]]+)\]", dst.read_text(encoding="utf-8"), re.M))
    return ([f"MCP server not mirrored to Codex: {n}" for n in sorted(claude - codex)]
            + [f"Stale Codex MCP server: {n}" for n in sorted(codex - claude)])


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
        findings += check_unexported_skills(root, manifest)
        findings += check_hooks(root)
        findings += check_mcp_servers(root)
        return {"ok": not findings, "drift_count": len(findings), "findings": findings,
                "warnings": warnings, "agents": len(manifest["agents"]),
                "scope": SCOPE}
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        return {"ok": False, "drift_count": 1, "findings": [str(exc)], "warnings": []}


def main() -> None:
    result = check_drift()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
