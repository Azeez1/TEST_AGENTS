"""Workspace contracts: no private setup, cwd assumptions or escaping writes."""
from pathlib import Path

import pytest

from tools import path_validator as paths
from tools.workspace_enforcer import validate_workspace, get_absolute_paths, list_all_agents
from tools.workspace_registry import REPO_ROOT, contained_path, discover_agents, load_registry


@pytest.mark.parametrize("team", load_registry()["teams"])
def test_every_registered_workspace(team, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for agent in discover_agents()[team]:
        assert validate_workspace(agent.stem, team)["valid"]
    assert Path(get_absolute_paths(team)["agents"]).is_absolute()
    assert list_all_agents()[team] == [p.stem for p in discover_agents()[team]]


def test_invalid_agent_or_team():
    assert not validate_workspace("../copywriter", "MARKETING_TEAM")["valid"]
    assert not validate_workspace("copywriter", "UNKNOWN")["valid"]


@pytest.mark.parametrize("path", ["../../FINANCIAL_TEAM/outputs/probe.txt",
    str(REPO_ROOT / "MARKETING_TEAM/outputs_extra/probe.txt"),
    str(REPO_ROOT / "MARKETING_TEAM/memory/probe.json"),
    "..\\..\\FINANCIAL_TEAM\\outputs\\probe.txt", "", "C:relative.txt"])
def test_save_rejects_escapes(path):
    with pytest.raises(ValueError):
        paths.validate_save_path(path, "MARKETING_TEAM")


@pytest.mark.parametrize("value", ["blog_posts/article.md", "outputs/blog_posts/article.md",
                                   "MARKETING_TEAM/outputs/blog_posts/article.md"])
def test_save_converges_with_arbitrary_cwd(value, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert Path(paths.validate_save_path(value, "MARKETING_TEAM")) == REPO_ROOT / "MARKETING_TEAM/outputs/blog_posts/article.md"
    assert paths.get_team_from_path("QA_TEAM/tests/test_example.py") == "QA_TEAM"


def test_qa_and_new_team_outputs():
    assert Path(paths.validate_save_path("tests/test_case.py", "QA_TEAM")) == REPO_ROOT / "QA_TEAM/tests/test_case.py"
    assert Path(paths.validate_save_path("audit.md", "CODEX_TEAM")) == REPO_ROOT / "CODEX_TEAM/outputs/audit.md"
    assert Path(paths.validate_save_path("call.json", "VOICE_TEAM")) == REPO_ROOT / "VOICE_TEAM/outputs/call.json"


def test_read_containment_and_config_precedence(tmp_path, monkeypatch):
    team = tmp_path / "MARKETING_TEAM"
    (tmp_path / "config").mkdir()
    (tmp_path / "config/workspaces.json").write_bytes((REPO_ROOT / "config/workspaces.json").read_bytes())
    for folder in ("memory", "config"):
        (team / folder).mkdir(parents=True)
        (team / folder / "settings.json").write_text("{}")
    monkeypatch.setattr(paths, "_get_repo_root", lambda: tmp_path)
    assert Path(paths.validate_read_path("settings.json", "MARKETING_TEAM")) == team / "config/settings.json"
    with pytest.raises(ValueError):
        paths.validate_read_path(str(tmp_path / "config/workspaces.json"), "MARKETING_TEAM")


def test_cross_team_policy_cannot_bypass_through_root():
    validate = paths.validate_cross_team_path
    assert validate("tools/api.py", "CODEX_TEAM", "SALES_TEAM")["allowed"]
    assert not validate("memory/private.json", "CODEX_TEAM", "SALES_TEAM")["allowed"]
    assert not validate("SALES_TEAM/memory/private.json", "CODEX_TEAM", "ROOT")["allowed"]
    assert not validate("tools/api.py", "MARKETING_TEAM", "SALES_TEAM")["allowed"]
    assert not validate("tools/api.py", "CODEX_TEAM", "SALES_TEAM", "delete")["allowed"]
    assert not validate("tools/api.py", "CODEX_TEAM", "SALES_TEAM", "write")["allowed"]
    assert validate("tools/api.py", "CODEX_TEAM", "SALES_TEAM", "write", infrastructure=True)["allowed"]
    assert not validate(".claude/agents/sdr.md", "CODEX_TEAM", "SALES_TEAM", "write", infrastructure=True)["allowed"]
    assert not validate(".mcp.json", "CODEX_TEAM", "ROOT", "write", infrastructure=True)["allowed"]


def test_symlink_escape(tmp_path):
    base, outside = tmp_path / "base", tmp_path / "outside"
    base.mkdir(); outside.mkdir()
    try:
        (base / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Creating symlinks requires OS permission")
    with pytest.raises(ValueError):
        contained_path(base, "link/secret.txt")
