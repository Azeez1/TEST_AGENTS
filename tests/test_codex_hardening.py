"""Regression probes for real exporter and hook failures found in the audit."""
import importlib.util
import io
import json
import os
from pathlib import Path

import pytest

from scripts import export_codex_layer as exporter
from tools.codex_export_transaction import publish, differing_files
from tools.runtime_events import parse_event
from tools.workspace_registry import REPO_ROOT


def load_hook(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / f".codex/hooks/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("tool,field", [("PowerShell", "command"), ("exec_command", "cmd"),
    ("functions.exec_command", "cmd"), ("functions.exec", "code"), ("container.exec", "cmd")])
def test_boundary_handles_current_shell_payloads(tool, field, monkeypatch):
    hook = load_hook("claude_boundary_gate")
    payload = {"tool_name": tool, "tool_input": {field: "Set-Content .claude/agents/a.md x"}}
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(json.dumps(payload)))
    with pytest.raises(SystemExit) as result:
        hook.main()
    assert result.value.code == 1


@pytest.mark.parametrize("arguments", ["*** Update File: .claude/agents/a.md\n+x",
    {"patch": "*** Update File: .claude/agents/a.md\n+x"},
    {"file_path": ".claude/agents/a.md", "content": "x"},
    {"file_path": ".claude\\agents\\a.md", "content": "x"}])
def test_boundary_handles_patch_payloads(arguments, monkeypatch):
    hook = load_hook("claude_boundary_gate")
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(json.dumps({"name": "apply_patch", "arguments": arguments})))
    with pytest.raises(SystemExit) as result:
        hook.main()
    assert result.value.code == 1


@pytest.mark.parametrize("tool,arguments", [("exec_command", {"cmd": "Get-Content .claude/agents/a.md"}),
    ("apply_patch", "*** Update File: CODEX_TEAM/docs/guide.md\n+x")])
def test_boundary_allows_reads_and_codex_edits(tool, arguments, monkeypatch):
    hook = load_hook("claude_boundary_gate")
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(json.dumps({"tool_name": tool, "tool_input": arguments})))
    with pytest.raises(SystemExit) as result:
        hook.main()
    assert result.value.code == 0


def test_json_arguments_and_command_arrays():
    event = parse_event({"name": "exec_command", "arguments": json.dumps({"cmd": ["python", "tool.py"]})})
    assert event.command == "python tool.py"
    assert event.arguments["cmd"] == ["python", "tool.py"]


def test_general_enforcement_uses_same_payload_parser(monkeypatch, tmp_path):
    gate = load_hook("enforcement_gate")
    monkeypatch.setattr(gate, "LOG_DIR", tmp_path)
    monkeypatch.setattr(gate, "LOG", tmp_path / "hook.log")
    payload = {"name": "functions.exec_command", "arguments": json.dumps({"cmd": "git reset --hard"})}
    monkeypatch.setattr(gate.sys, "stdin", io.StringIO(json.dumps(payload)))
    with pytest.raises(SystemExit) as result:
        gate.main()
    assert result.value.code == 1


def test_yaml_serializer_quotes_values_and_empty_lists():
    agent = exporter.AgentExport("x", "Name: x", "ROOT", "x.md", ".codex/agents/ROOT/x.md",
        "claude", None, "inherit", [], [], [], description="Description: # literal")
    header, _ = exporter.parse_frontmatter(exporter.build_agent_doc(agent, "Body"))
    assert header["skills"] == []
    assert header["description"] == "Description: # literal"


def test_hash_does_not_depend_on_checkout_line_endings():
    assert exporter.content_hash("a\r\nb\r\n") == exporter.content_hash("a\nb\n")
    assert exporter.content_hash("new") != exporter.content_hash("old")


def test_workspace_adaptation_preserves_domain_sections_and_fenced_headings():
    body = "# Agent\n\n## 🏢 WORKSPACE CONTEXT & VALIDATION\nShared\n```md\n## Example\n```\n## Domain rules\nKeep all these rules.\n"
    adapted, changes = exporter.adapt_workspace_boilerplate(body)
    assert changes == ["shared_workspace_contract"]
    assert "Shared" not in adapted
    assert adapted.endswith("## Domain rules\nKeep all these rules.\n")
    assert exporter.adapt_workspace_boilerplate("## Domain rules\nUnchanged")[0] == "## Domain rules\nUnchanged"


def test_failed_publish_restores_old_generation(tmp_path, monkeypatch):
    stage, dest, backup = [tmp_path / x for x in ("stage", "dest", "backup")]
    for root in (stage, dest):
        root.mkdir()
        for filename in ("a.md", "b.md"):
            (root / filename).write_text(root.name)
    original = os.replace
    count = 0
    def fail_second(source, target):
        nonlocal count
        count += 1
        if count == 2:
            raise OSError("injected publish failure")
        return original(source, target)
    monkeypatch.setattr(os, "replace", fail_second)
    with pytest.raises(OSError):
        publish(stage, dest, backup)
    assert (dest / "a.md").read_text() == "dest"
    assert (dest / "b.md").read_text() == "dest"


def test_publish_prunes_obsolete_agents_preserves_native_files(tmp_path):
    stage, dest = tmp_path / "stage", tmp_path / "dest"
    (stage / "agents/ROOT").mkdir(parents=True)
    (dest / "agents/ROOT").mkdir(parents=True)
    (stage / "agents/ROOT/new.md").write_text("new")
    (dest / "agents/ROOT/old.md").write_text("old")
    (dest / "local.env").write_text("local state")
    assert "agents/ROOT/old.md" in differing_files(stage, dest)
    publish(stage, dest, tmp_path / "backup")
    assert not (dest / "agents/ROOT/old.md").exists()
    assert (dest / "local.env").read_text() == "local state"


def test_export_check_accepts_windows_checkout_newlines(tmp_path):
    stage, dest = tmp_path / "stage", tmp_path / "dest"
    stage.mkdir(); dest.mkdir()
    (stage / "manifest.json").write_bytes(b'{"agents": []}\n')
    (dest / "manifest.json").write_bytes(b'{"agents": []}\r\n')
    before = (dest / "manifest.json").stat().st_mtime_ns
    assert differing_files(stage, dest) == []
    publish(stage, dest, tmp_path / "backup")
    assert (dest / "manifest.json").stat().st_mtime_ns == before
