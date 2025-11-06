"""
Workspace enforcement validation tests

Tests that all 37 agents operate in correct workspaces
"""

import pytest
import os
from pathlib import Path
import sys

# Add tools to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from tools.workspace_enforcer import validate_workspace, get_absolute_paths
from tools.path_validator import validate_save_path, validate_read_path, get_team_from_path


class TestWorkspaceEnforcement:

    def test_marketing_agents_workspace(self):
        """Test all 17 MARKETING_TEAM agents have correct workspace"""
        agents = [
            "router-agent", "content-strategist", "research-agent",
            "lead-gen-agent", "automation-agent", "copywriter", "editor",
            "social-media-manager", "visual-designer", "video-producer",
            "seo-specialist", "email-specialist", "gmail-agent",
            "landing-page-specialist", "pdf-specialist",
            "presentation-designer", "analyst"
        ]

        for agent in agents:
            status = validate_workspace(agent, "MARKETING_TEAM")
            assert status["valid"] == True, f"{agent} workspace validation failed: {status['errors']}"
            assert "MARKETING_TEAM" in status["workspace_path"]

    def test_qa_agents_workspace(self):
        """Test all 5 QA_TEAM agents have correct workspace"""
        agents = [
            "test-orchestrator", "unit-test-agent",
            "integration-test-agent", "edge-case-agent", "fixture-agent"
        ]

        for agent in agents:
            status = validate_workspace(agent, "QA_TEAM")
            assert status["valid"] == True, f"{agent} workspace validation failed: {status['errors']}"
            assert "QA_TEAM" in status["workspace_path"]

    def test_engineering_agents_workspace(self):
        """Test all 14 ENGINEERING_TEAM agents have correct workspace"""
        agents = [
            "cto", "devops-engineer", "frontend-developer",
            "backend-architect", "security-auditor", "technical-writer",
            "system-architect", "ai-engineer", "ui-ux-designer",
            "code-reviewer", "test-engineer", "prompt-engineer",
            "database-architect", "debugger"
        ]

        for agent in agents:
            status = validate_workspace(agent, "ENGINEERING_TEAM")
            assert status["valid"] == True, f"{agent} workspace validation failed: {status['errors']}"
            assert "ENGINEERING_TEAM" in status["workspace_path"]

    def test_absolute_paths_generation(self):
        """Test get_absolute_paths returns correct paths"""
        paths = get_absolute_paths("MARKETING_TEAM")

        assert "memory" in paths
        assert "outputs" in paths
        assert "tools" in paths
        assert "MARKETING_TEAM" in paths["memory"] and "memory" in paths["memory"]
        assert "MARKETING_TEAM" in paths["outputs"] and "outputs" in paths["outputs"]

    def test_path_validator_save(self):
        """Test path validator creates correct absolute paths"""
        path = validate_save_path("blog_posts/article.md", "MARKETING_TEAM")
        assert "MARKETING_TEAM" in path and "outputs" in path and "blog_posts" in path and "article.md" in path

        path = validate_save_path("tests/test_example.py", "QA_TEAM")
        assert "QA_TEAM" in path and "tests" in path and "test_example.py" in path

    def test_path_validator_read(self):
        """Test path validator for reading files"""
        # This will raise FileNotFoundError if file doesn't exist, which is expected
        # We're testing the path construction is correct
        try:
            path = validate_read_path("brand_voice.json", "MARKETING_TEAM")
            assert "MARKETING_TEAM" in path and "memory" in path and "brand_voice.json" in path
        except FileNotFoundError as e:
            # Expected if file doesn't exist - check error message has correct path
            assert "MARKETING_TEAM" in str(e) and "memory" in str(e) and "brand_voice.json" in str(e)

    def test_workspace_folders_exist(self):
        """Test all team workspace folders exist"""
        teams = ["MARKETING_TEAM", "QA_TEAM", "ENGINEERING_TEAM", "USER_STORY_AGENT"]

        for team in teams:
            team_path = repo_root / team
            assert team_path.exists(), f"{team} folder missing"

            # Check memory folders (except USER_STORY_AGENT uses different structure)
            if team != "USER_STORY_AGENT":
                memory_path = team_path / "memory"
                assert memory_path.exists(), f"{team}/memory/ folder missing"


class TestAgentDefinitions:
    """Test agent definition files have workspace headers"""

    def test_marketing_agents_have_workspace_headers(self):
        """Test all MARKETING_TEAM agents have workspace context section"""
        agents_dir = repo_root / "MARKETING_TEAM" / ".claude" / "agents"
        agent_files = [f for f in agents_dir.iterdir() if f.suffix == ".md"]

        assert len(agent_files) == 17, f"Expected 17 MARKETING_TEAM agents, found {len(agent_files)}"

        for agent_file in agent_files:
            with open(agent_file, encoding='utf-8') as f:
                content = f.read()
                assert "WORKSPACE CONTEXT" in content, f"{agent_file.name} missing workspace context"
                assert "MARKETING_TEAM" in content, f"{agent_file.name} doesn't specify MARKETING_TEAM"
                assert "ABSOLUTE PATHS" in content or "absolute path" in content.lower(), f"{agent_file.name} missing absolute path guidance"

    def test_qa_agents_have_workspace_headers(self):
        """Test all QA_TEAM agents have workspace context section"""
        agents_dir = repo_root / "QA_TEAM" / ".claude" / "agents"
        agent_files = [f for f in agents_dir.iterdir() if f.suffix == ".md"]

        assert len(agent_files) == 5, f"Expected 5 QA_TEAM agents, found {len(agent_files)}"

        for agent_file in agent_files:
            with open(agent_file, encoding='utf-8') as f:
                content = f.read()
                assert "WORKSPACE CONTEXT" in content, f"{agent_file.name} missing workspace context"
                assert "QA_TEAM" in content, f"{agent_file.name} doesn't specify QA_TEAM"

    def test_engineering_agents_have_workspace_headers(self):
        """Test all ENGINEERING_TEAM agents have workspace context section"""
        agents_dir = repo_root / "ENGINEERING_TEAM" / ".claude" / "agents"
        agent_files = [f for f in agents_dir.iterdir() if f.suffix == ".md"]

        assert len(agent_files) == 14, f"Expected 14 ENGINEERING_TEAM agents, found {len(agent_files)}"

        for agent_file in agent_files:
            with open(agent_file, encoding='utf-8') as f:
                content = f.read()
                assert "WORKSPACE CONTEXT" in content, f"{agent_file.name} missing workspace context"
                assert "ENGINEERING_TEAM" in content, f"{agent_file.name} doesn't specify ENGINEERING_TEAM"

    def test_agents_have_workspace_enforcer_tool(self):
        """Test agents have workspace_enforcer in YAML frontmatter"""
        teams = ["MARKETING_TEAM", "QA_TEAM", "ENGINEERING_TEAM"]

        for team in teams:
            agents_dir = repo_root / team / ".claude" / "agents"
            agent_files = [f for f in agents_dir.iterdir() if f.suffix == ".md"]

            for agent_file in agent_files:
                with open(agent_file, encoding='utf-8') as f:
                    content = f.read()
                    # Check YAML frontmatter has workspace_enforcer
                    assert "workspace_enforcer" in content or "path_validator" in content, \
                        f"{agent_file.name} missing workspace tools in YAML"


class TestTeamFromPath:
    """Test get_team_from_path utility"""

    def test_get_team_from_path(self):
        """Test extracting team name from file paths"""
        assert get_team_from_path("MARKETING_TEAM/outputs/blog_posts/article.md") == "MARKETING_TEAM"
        assert get_team_from_path("QA_TEAM/tests/test_example.py") == "QA_TEAM"
        assert get_team_from_path("ENGINEERING_TEAM/docs/spec.md") == "ENGINEERING_TEAM"
        assert get_team_from_path("some/random/path.txt") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
