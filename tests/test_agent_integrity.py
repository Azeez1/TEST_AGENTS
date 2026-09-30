"""Validate real YAML, dynamic source discovery and the generated contract."""
import json
from pathlib import Path

import pytest

from scripts.export_codex_layer import parse_frontmatter, content_hash
from tools.workspace_registry import REPO_ROOT, discover_agents, load_registry

SOURCES = [(team, path) for team, paths in discover_agents().items() for path in paths]


@pytest.mark.parametrize("team,path", SOURCES, ids=[f"{t}/{p.stem}" for t,p in SOURCES])
def test_source_contract(team, path):
    header, body = parse_frontmatter(path.read_text(encoding="utf-8-sig"))
    assert header["name"] == path.stem
    assert isinstance(header.get("description"), str) and header["description"].strip()
    assert body.strip()
    for key in ("tools", "skills"):
        entries = header.get(key, [])
        assert isinstance(entries, list)
        assert all(isinstance(x, str) and "*" not in x for x in entries)
    if team == "ROOT" and "reviewer" in path.stem:
        assert not {"Write", "Edit", "Bash", "PowerShell"}.intersection(header["tools"])


def test_registry_discovers_every_source_directory():
    configured = {p.parent for _,p in SOURCES}
    actual = {p for pattern in ("*/.claude/agents", "*/.codex/agents", ".claude/agents")
              for p in REPO_ROOT.glob(pattern)}
    assert actual == configured
    for team, cfg in load_registry()["teams"].items():
        assert any(p.stem == cfg["orchestrator"] for p in discover_agents()[team])


def test_manifest_covers_sources_and_valid_generated_metadata():
    manifest = json.loads((REPO_ROOT / ".codex/manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "test-agents/codex-layer/v2"
    expected = {(team, p.stem) for team,p in SOURCES}
    actual = [(a["team"], a["slug"]) for a in manifest["agents"]]
    assert len(actual) == len(set(actual))
    assert set(actual) == expected
    for agent in manifest["agents"]:
        text = (REPO_ROOT / agent["codex_instructions"]).read_text(encoding="utf-8")
        header, _ = parse_frontmatter(text)
        assert header["description"] == agent["description"]
        assert header["model_policy"] == "inherit_session_unless_user_selects"
        assert header["codex_model"] == "inherit"
        assert agent["source_sha256"] == content_hash((REPO_ROOT / agent["source"]).read_text(encoding="utf-8-sig"))
        assert agent["rendered_sha256"] == content_hash(text)
        assert all(isinstance(header[k], list) for k in ("tools", "skills", "capabilities"))
