"""
Agent integrity validation tests

Tests that all 62 agents have valid YAML frontmatter, correct MCP tool
namespaces, no wildcards, and consistent naming across documentation.
"""

import pytest
import os
import re
from pathlib import Path

repo_root = Path(__file__).parent.parent

TEAMS = {
    ".claude/agents": {"expected_count": 1, "name": "ROOT"},
    "MARKETING_TEAM/.claude/agents": {"expected_count": 18, "name": "MARKETING_TEAM"},
    "ENGINEERING_TEAM/.claude/agents": {"expected_count": 15, "name": "ENGINEERING_TEAM"},
    "QA_TEAM/.claude/agents": {"expected_count": 5, "name": "QA_TEAM"},
    "PROPOSAL_TEAM/.claude/agents": {"expected_count": 1, "name": "PROPOSAL_TEAM"},
    "FINANCIAL_TEAM/.claude/agents": {"expected_count": 13, "name": "FINANCIAL_TEAM"},
    "SALES_TEAM/.claude/agents": {"expected_count": 9, "name": "SALES_TEAM"},
}

VALID_MCP_SERVERS = [
    "google-workspace",
    "perplexity",
    "bright-data",
    "playwright",
    "n8n-mcp",
    "sequential-thinking",
    "marketing-tools",
    "claude-in-chrome",
    "codex-cli",
]


def get_all_agent_files():
    """Collect all agent .md files across all teams."""
    agents = []
    for team_path, info in TEAMS.items():
        agents_dir = repo_root / team_path
        if agents_dir.exists():
            for f in agents_dir.iterdir():
                if f.suffix == ".md":
                    agents.append((f, info["name"]))
    return agents


def extract_yaml_frontmatter(content):
    """Extract YAML frontmatter from agent .md file."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    return match.group(1) if match else None


def extract_tools_from_yaml(yaml_text):
    """Extract tool names from YAML frontmatter tools: section."""
    tools = []
    in_tools = False
    for line in yaml_text.split("\n"):
        if line.strip().startswith("tools:"):
            in_tools = True
            continue
        if in_tools:
            if line.strip().startswith("- "):
                tools.append(line.strip()[2:].strip())
            elif line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                break
    return tools


class TestAgentCounts:
    """Verify correct agent counts per team."""

    def test_total_agent_count(self):
        """Total agents across all teams should be 62."""
        agents = get_all_agent_files()
        assert len(agents) == 62, f"Expected 62 agents, found {len(agents)}"

    @pytest.mark.parametrize("team_path,info", TEAMS.items())
    def test_team_agent_count(self, team_path, info):
        """Each team should have the expected number of agents."""
        agents_dir = repo_root / team_path
        if not agents_dir.exists():
            pytest.fail(f"{info['name']} agents directory missing: {agents_dir}")
        agent_files = [f for f in agents_dir.iterdir() if f.suffix == ".md"]
        assert len(agent_files) == info["expected_count"], (
            f"{info['name']}: expected {info['expected_count']} agents, found {len(agent_files)}"
        )


class TestYAMLFrontmatter:
    """Verify all agents have valid YAML frontmatter."""

    @pytest.fixture
    def all_agents(self):
        return get_all_agent_files()

    def test_all_agents_have_frontmatter(self, all_agents):
        """Every agent must have YAML frontmatter."""
        missing = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                missing.append(f"{team}/{agent_file.name}")
        assert not missing, f"Agents missing YAML frontmatter: {missing}"

    def test_all_agents_have_name(self, all_agents):
        """Every agent must have a name field."""
        missing = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml and "name:" not in yaml:
                missing.append(f"{team}/{agent_file.name}")
        assert not missing, f"Agents missing name field: {missing}"

    def test_all_agents_have_description(self, all_agents):
        """Every agent must have a description field."""
        missing = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml and "description:" not in yaml:
                missing.append(f"{team}/{agent_file.name}")
        assert not missing, f"Agents missing description field: {missing}"

    def test_all_agents_have_tools(self, all_agents):
        """Every agent must have a tools field."""
        missing = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml and "tools:" not in yaml:
                missing.append(f"{team}/{agent_file.name}")
        assert not missing, f"Agents missing tools field: {missing}"

    def test_all_agents_have_skills(self, all_agents):
        """Every agent must have a skills field."""
        missing = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml and "skills:" not in yaml:
                missing.append(f"{team}/{agent_file.name}")
        assert not missing, f"Agents missing skills field: {missing}"


class TestMCPNamespaces:
    """Verify MCP tool references use correct format."""

    @pytest.fixture
    def all_agents(self):
        return get_all_agent_files()

    def test_no_underscore_google_workspace(self, all_agents):
        """No agent should use mcp__google_workspace__ (underscores)."""
        violations = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml and "mcp__google_workspace__" in yaml:
                violations.append(f"{team}/{agent_file.name}")
        assert not violations, (
            f"Agents using wrong namespace mcp__google_workspace__ (should be google-workspace): {violations}"
        )

    def test_no_wildcard_mcp_tools(self, all_agents):
        """No agent should use wildcard MCP tool references in YAML."""
        violations = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml:
                tools = extract_tools_from_yaml(yaml)
                for tool in tools:
                    if tool.endswith("*"):
                        violations.append(f"{team}/{agent_file.name}: {tool}")
        assert not violations, f"Agents using wildcard MCP tools (must list specific tools): {violations}"

    def test_mcp_tools_reference_valid_servers(self, all_agents):
        """All mcp__ tool references must use a known server name."""
        violations = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml:
                tools = extract_tools_from_yaml(yaml)
                for tool in tools:
                    if tool.startswith("mcp__"):
                        parts = tool.split("__")
                        if len(parts) >= 3:
                            server = parts[1]
                            if server not in VALID_MCP_SERVERS:
                                violations.append(f"{team}/{agent_file.name}: unknown server '{server}' in {tool}")
        assert not violations, f"Agents referencing unknown MCP servers: {violations}"

    def test_no_hyphen_in_perplexity_tool_names(self, all_agents):
        """Perplexity tools use underscores not hyphens (perplexity_search not perplexity-search)."""
        violations = []
        for agent_file, team in all_agents:
            content = agent_file.read_text(encoding="utf-8")
            yaml = extract_yaml_frontmatter(content)
            if yaml:
                tools = extract_tools_from_yaml(yaml)
                for tool in tools:
                    if "perplexity" in tool and "-" in tool.split("__")[-1]:
                        violations.append(f"{team}/{agent_file.name}: {tool}")
        assert not violations, f"Agents using hyphens in Perplexity tool names (should be underscores): {violations}"


class TestSettingsIntegrity:
    """Verify settings.json files are consistent."""

    def test_root_settings_has_all_teams(self):
        """Root settings.json should list all 6 teams in workspaces."""
        import json
        settings_file = repo_root / ".claude" / "settings.json"
        content = settings_file.read_text(encoding="utf-8")
        settings = json.loads(content)

        workspaces = settings.get("workspaces", {})
        expected_teams = ["MARKETING_TEAM", "ENGINEERING_TEAM", "QA_TEAM", "PROPOSAL_TEAM", "FINANCIAL_TEAM", "SALES_TEAM"]
        missing = [t for t in expected_teams if t not in workspaces]
        assert not missing, f"Root settings.json missing workspaces: {missing}"

    def test_no_linux_paths_in_settings(self):
        """No settings.json should contain /home/user/ paths."""
        violations = []
        # Check known team settings.json locations explicitly to avoid node_modules
        settings_locations = [
            repo_root / ".claude" / "settings.json",
            repo_root / "MARKETING_TEAM" / ".claude" / "settings.json",
            repo_root / "ENGINEERING_TEAM" / ".claude" / "settings.json",
            repo_root / "QA_TEAM" / ".claude" / "settings.json",
            repo_root / "PROPOSAL_TEAM" / ".claude" / "settings.json",
            repo_root / "FINANCIAL_TEAM" / ".claude" / "settings.json",
            repo_root / "SALES_TEAM" / ".claude" / "settings.json",
        ]
        for settings_file in settings_locations:
            if settings_file.exists():
                content = settings_file.read_text(encoding="utf-8")
                if "/home/user/" in content:
                    violations.append(str(settings_file.relative_to(repo_root)))
        assert not violations, f"Settings files with hardcoded Linux paths: {violations}"

    def test_financial_team_agent_roster(self):
        """FINANCIAL_TEAM settings should list all 13 agents."""
        import json
        settings_file = repo_root / "FINANCIAL_TEAM" / ".claude" / "settings.json"
        content = settings_file.read_text(encoding="utf-8")
        settings = json.loads(content)

        agents = settings["teams"]["FINANCIAL_TEAM"]["agents"]
        assert len(agents) == 13, f"FINANCIAL_TEAM settings has {len(agents)} agents, expected 13"
        for required in ["treasury-agent", "financial-data-analyst", "investor-relations-agent"]:
            assert required in agents, f"FINANCIAL_TEAM settings missing {required}"

    def test_sales_team_agent_roster(self):
        """SALES_TEAM settings should list all 9 agents."""
        import json
        settings_file = repo_root / "SALES_TEAM" / ".claude" / "settings.json"
        content = settings_file.read_text(encoding="utf-8")
        settings = json.loads(content)

        agents = settings["teams"]["SALES_TEAM"]["agents"]
        assert len(agents) == 9, f"SALES_TEAM settings has {len(agents)} agents, expected 9"
        assert "pe-outreach-agent" in agents, "SALES_TEAM settings missing pe-outreach-agent"

    def test_no_nonexistent_tools_paths(self):
        """Team settings should not reference tools/ folders that don't exist."""
        import json
        for team in ["FINANCIAL_TEAM", "SALES_TEAM"]:
            settings_file = repo_root / team / ".claude" / "settings.json"
            content = settings_file.read_text(encoding="utf-8")
            settings = json.loads(content)

            team_config = settings["teams"][team]
            if "tools" in team_config:
                tools_path = repo_root / team_config["tools"]
                assert tools_path.exists(), f"{team} settings references non-existent tools path: {team_config['tools']}"


class TestDocumentationConsistency:
    """Verify documentation matches reality."""

    def test_multi_agent_guide_says_62(self):
        """MULTI_AGENT_GUIDE.md should reference 62 agents, not 58/59."""
        content = (repo_root / "MULTI_AGENT_GUIDE.md").read_text(encoding="utf-8")
        assert "58 perfectly defined" not in content, "MULTI_AGENT_GUIDE.md still says 58"
        assert "59 Agents" not in content, "MULTI_AGENT_GUIDE.md still says 59"
        assert "62" in content, "MULTI_AGENT_GUIDE.md should mention 62 agents"

    def test_agents_md_no_phantom_names(self):
        """AGENTS.md should not reference agent names that don't exist as files."""
        content = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
        phantom_names = [
            "landing-page-designer",
            "ux-designer",
            "qa-engineer",
            "testing-specialist",
            "performance-optimizer",
            "database-engineer",
            "troubleshooter",
            "brand-manager",
            "campaign-manager",
        ]
        found = [name for name in phantom_names if f"**{name}**" in content]
        assert not found, f"AGENTS.md still references phantom agent names: {found}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
