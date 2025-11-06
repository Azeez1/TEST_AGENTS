"""
Workspace Enforcer - Validate agent workspace context and enforce folder boundaries

This tool ensures all 37 agents operate in their correct team workspaces and prevents
location confusion by validating workspace context before every task.

Usage:
    from tools.workspace_enforcer import validate_workspace, get_absolute_paths

    # Validate agent is in correct workspace
    status = validate_workspace("copywriter", "MARKETING_TEAM")

    # Get absolute paths for a team
    paths = get_absolute_paths("MARKETING_TEAM")

Author: Claude Code + USER
Created: 2025-01-06
Version: 1.0
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Claude Agent SDK tool decorator (mock for testing outside Claude Code)
try:
    from anthropic import tool
except (ImportError, AttributeError):
    # Mock tool decorator for testing
    def tool(func):
        """Mock tool decorator for testing"""
        return func


# Define workspace structure for all 4 teams
WORKSPACE_STRUCTURE = {
    "MARKETING_TEAM": {
        "agents": 17,
        "folders": ["memory", "outputs", "tools", ".claude/agents"],
        "memory_files": [
            "brand_voice.json",
            "email_config.json",
            "google_drive_config.json",
            "visual_guidelines.json",
            "output_paths.json",
            "docs_folder_structure.json",
            "seo_config.json",
            "campaign_templates.json",
            "voice_interface_config.json",
            "learned_preferences.json",
            "social_media_accounts.json",
            "content_calendar.json"
        ],
        "agents_list": [
            "router-agent", "content-strategist", "research-agent",
            "lead-gen-agent", "automation-agent", "copywriter", "editor",
            "social-media-manager", "visual-designer", "video-producer",
            "seo-specialist", "email-specialist", "gmail-agent",
            "landing-page-specialist", "pdf-specialist",
            "presentation-designer", "analyst"
        ]
    },
    "QA_TEAM": {
        "agents": 5,
        "folders": ["memory", "tests", "tools", ".claude/agents"],
        "memory_files": [
            "learned_patterns.json",
            "test_settings.json"
        ],
        "agents_list": [
            "test-orchestrator", "unit-test-agent",
            "integration-test-agent", "edge-case-agent", "fixture-agent"
        ]
    },
    "ENGINEERING_TEAM": {
        "agents": 14,
        "folders": ["memory", "outputs", "docs", "tools", ".claude/agents"],
        "memory_files": [
            "deployment_configs.json",
            "infrastructure_settings.json"
        ],
        "agents_list": [
            "cto", "devops-engineer", "frontend-developer",
            "backend-architect", "security-auditor", "technical-writer",
            "system-architect", "ai-engineer", "ui-ux-designer",
            "code-reviewer", "test-engineer", "prompt-engineer",
            "database-architect", "debugger"
        ]
    },
    "USER_STORY_AGENT": {
        "agents": 1,
        "folders": ["memory", "output", "tools"],
        "memory_files": ["preferences_store.json"],
        "agents_list": ["user_story_agent"]
    }
}


def _get_repo_root() -> Path:
    """Get the TEST_AGENTS repository root directory"""
    current = Path.cwd()

    # Check if we're already in TEST_AGENTS
    if current.name == "TEST_AGENTS":
        return current

    # Check if TEST_AGENTS is a parent directory
    for parent in current.parents:
        if parent.name == "TEST_AGENTS":
            return parent

    # Check if we're inside a team folder
    team_folders = ["MARKETING_TEAM", "QA_TEAM", "ENGINEERING_TEAM", "USER_STORY_AGENT"]
    for team in team_folders:
        if team in str(current):
            # Navigate up to find TEST_AGENTS
            parts = current.parts
            if team in parts:
                idx = parts.index(team)
                return Path(*parts[:idx])

    # Default: assume current directory is repo root
    return current


@tool
def validate_workspace(agent_name: str, expected_team: str) -> Dict[str, any]:
    """
    Validate that an agent is operating in the correct workspace.

    This is the FIRST function every agent must call before starting any task.
    It verifies the agent's team membership and workspace context.

    Args:
        agent_name: Name of the agent (e.g., "copywriter", "test-orchestrator")
        expected_team: Expected team name (e.g., "MARKETING_TEAM", "QA_TEAM")

    Returns:
        Dictionary with validation status:
        {
            "valid": bool,                    # Whether workspace is valid
            "agent_name": str,                # Agent name
            "expected_team": str,             # Expected team
            "current_directory": str,         # Current OS working directory
            "repo_root": str,                 # TEST_AGENTS root path
            "team_path": str,                 # Full path to team folder
            "workspace_path": str,            # Expected workspace path
            "agent_exists": bool,             # Whether agent definition exists
            "team_folders_exist": bool,       # Whether team folders exist
            "message": str,                   # Human-readable status message
            "errors": List[str],              # List of validation errors
            "suggestions": List[str]          # Suggestions to fix errors
        }

    Example:
        >>> status = validate_workspace("copywriter", "MARKETING_TEAM")
        >>> if not status["valid"]:
        ...     print(status["message"])
        ...     print("Errors:", status["errors"])
        ...     print("Suggestions:", status["suggestions"])
    """
    errors = []
    suggestions = []

    # Validate team exists
    if expected_team not in WORKSPACE_STRUCTURE:
        return {
            "valid": False,
            "agent_name": agent_name,
            "expected_team": expected_team,
            "message": f"Invalid team name: {expected_team}",
            "errors": [f"Team '{expected_team}' not found in workspace structure"],
            "suggestions": [f"Valid teams: {', '.join(WORKSPACE_STRUCTURE.keys())}"]
        }

    # Get team structure
    team_info = WORKSPACE_STRUCTURE[expected_team]

    # Validate agent belongs to team
    if agent_name not in team_info["agents_list"]:
        errors.append(f"Agent '{agent_name}' not found in {expected_team}")
        suggestions.append(f"Valid {expected_team} agents: {', '.join(team_info['agents_list'][:5])}...")

    # Get paths
    repo_root = _get_repo_root()
    current_dir = Path.cwd()
    team_path = repo_root / expected_team
    workspace_path = f"{repo_root}/{expected_team}"

    # Check team folder exists
    if not team_path.exists():
        errors.append(f"Team folder not found: {team_path}")
        suggestions.append(f"Create folder: mkdir {team_path}")

    # Check required folders exist
    team_folders_exist = True
    for folder in team_info["folders"]:
        folder_path = team_path / folder
        if not folder_path.exists():
            team_folders_exist = False
            errors.append(f"Required folder missing: {folder_path}")
            suggestions.append(f"Create folder: mkdir -p {folder_path}")

    # Check agent definition file exists
    agent_def_path = team_path / ".claude" / "agents" / f"{agent_name}.md"
    agent_exists = agent_def_path.exists()
    if not agent_exists:
        errors.append(f"Agent definition not found: {agent_def_path}")
        suggestions.append(f"Check agent name spelling or create definition file")

    # Determine if valid
    valid = len(errors) == 0

    # Generate message
    if valid:
        message = f"✅ Workspace valid: {agent_name} operating in {expected_team}"
    else:
        message = f"❌ Workspace validation failed for {agent_name} in {expected_team}"

    return {
        "valid": valid,
        "agent_name": agent_name,
        "expected_team": expected_team,
        "current_directory": str(current_dir),
        "repo_root": str(repo_root),
        "team_path": str(team_path),
        "workspace_path": workspace_path,
        "agent_exists": agent_exists,
        "team_folders_exist": team_folders_exist,
        "message": message,
        "errors": errors,
        "suggestions": suggestions
    }


@tool
def get_absolute_paths(team: str) -> Dict[str, str]:
    """
    Get absolute paths for all folders in a team's workspace.

    This function returns the absolute paths that agents should use for all file operations.
    Use this instead of relative paths to eliminate ambiguity.

    Args:
        team: Team name (e.g., "MARKETING_TEAM", "QA_TEAM")

    Returns:
        Dictionary with absolute paths:
        {
            "team_root": str,           # Team root folder
            "memory": str,              # Memory configuration folder
            "outputs": str,             # Outputs folder (or "tests" for QA_TEAM)
            "tools": str,               # Tools folder
            "agents": str,              # Agent definitions folder
            "docs": str,                # Docs folder (ENGINEERING_TEAM only)
            "repo_root": str            # TEST_AGENTS root
        }

    Example:
        >>> paths = get_absolute_paths("MARKETING_TEAM")
        >>> print(paths["memory"])
        "/path/to/TEST_AGENTS/MARKETING_TEAM/memory"
        >>>
        >>> # Use in file operations
        >>> config_path = f"{paths['memory']}/brand_voice.json"
    """
    if team not in WORKSPACE_STRUCTURE:
        raise ValueError(f"Invalid team: {team}. Valid teams: {', '.join(WORKSPACE_STRUCTURE.keys())}")

    repo_root = _get_repo_root()
    team_path = repo_root / team

    paths = {
        "team_root": str(team_path),
        "memory": str(team_path / "memory"),
        "tools": str(team_path / "tools"),
        "agents": str(team_path / ".claude" / "agents"),
        "repo_root": str(repo_root)
    }

    # Add outputs or tests depending on team
    if team == "QA_TEAM":
        paths["outputs"] = str(team_path / "tests")
        paths["tests"] = str(team_path / "tests")
    elif team == "USER_STORY_AGENT":
        paths["outputs"] = str(team_path / "output")
        paths["output"] = str(team_path / "output")
    else:
        paths["outputs"] = str(team_path / "outputs")

    # Add docs for ENGINEERING_TEAM
    if team == "ENGINEERING_TEAM":
        paths["docs"] = str(team_path / "docs")

    return paths


@tool
def ensure_team_context(team: str) -> Dict[str, any]:
    """
    Ensure the working directory is correct for the team.

    This function checks if the current directory is appropriate for the team's context.
    If not, it provides instructions to navigate to the correct directory.

    Note: This function does NOT automatically change directories (that's the user's choice).
    It only validates and provides guidance.

    Args:
        team: Team name (e.g., "MARKETING_TEAM", "QA_TEAM")

    Returns:
        Dictionary with context status:
        {
            "correct_context": bool,        # Whether context is correct
            "current_directory": str,       # Current working directory
            "expected_directory": str,      # Expected directory
            "team": str,                    # Team name
            "message": str,                 # Human-readable message
            "navigation_command": str       # Command to navigate to correct directory
        }

    Example:
        >>> context = ensure_team_context("MARKETING_TEAM")
        >>> if not context["correct_context"]:
        ...     print(context["message"])
        ...     print(f"Run: {context['navigation_command']}")
    """
    if team not in WORKSPACE_STRUCTURE:
        raise ValueError(f"Invalid team: {team}")

    repo_root = _get_repo_root()
    current_dir = Path.cwd()
    team_path = repo_root / team

    # Check if we're in TEST_AGENTS root or team folder
    correct_context = (
        current_dir == repo_root or
        current_dir == team_path or
        team in str(current_dir)
    )

    if correct_context:
        message = f"✅ Working directory context is correct for {team}"
        nav_command = ""
    else:
        message = f"⚠️ Working directory is not in {team} context"
        # Provide navigation command (relative to current location)
        if repo_root in current_dir.parents or current_dir == repo_root:
            nav_command = f"cd {team}"
        else:
            nav_command = f"cd {team_path}"

    return {
        "correct_context": correct_context,
        "current_directory": str(current_dir),
        "expected_directory": str(team_path),
        "team": team,
        "message": message,
        "navigation_command": nav_command
    }


def get_team_info(team: str) -> Dict[str, any]:
    """
    Get comprehensive information about a team's workspace structure.

    Args:
        team: Team name

    Returns:
        Dictionary with team information (from WORKSPACE_STRUCTURE)
    """
    if team not in WORKSPACE_STRUCTURE:
        raise ValueError(f"Invalid team: {team}")

    return WORKSPACE_STRUCTURE[team].copy()


def list_all_agents() -> Dict[str, List[str]]:
    """
    List all 37 agents organized by team.

    Returns:
        Dictionary mapping team names to agent lists
    """
    return {
        team: info["agents_list"]
        for team, info in WORKSPACE_STRUCTURE.items()
    }


# CLI interface for testing
if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("WORKSPACE ENFORCER - Test Mode")
    print("=" * 70)

    # Test validate_workspace
    print("\n1. Testing validate_workspace()...")
    print("-" * 70)

    test_cases = [
        ("copywriter", "MARKETING_TEAM"),
        ("test-orchestrator", "QA_TEAM"),
        ("cto", "ENGINEERING_TEAM"),
        ("invalid-agent", "MARKETING_TEAM"),
        ("copywriter", "INVALID_TEAM")
    ]

    for agent, team in test_cases:
        print(f"\nTesting: {agent} in {team}")
        result = validate_workspace(agent, team)
        print(f"Valid: {result['valid']}")
        print(f"Message: {result['message']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")

    # Test get_absolute_paths
    print("\n\n2. Testing get_absolute_paths()...")
    print("-" * 70)

    for team in ["MARKETING_TEAM", "QA_TEAM", "ENGINEERING_TEAM"]:
        print(f"\n{team} paths:")
        paths = get_absolute_paths(team)
        for key, value in paths.items():
            print(f"  {key}: {value}")

    # Test ensure_team_context
    print("\n\n3. Testing ensure_team_context()...")
    print("-" * 70)

    for team in ["MARKETING_TEAM", "QA_TEAM"]:
        print(f"\n{team} context:")
        context = ensure_team_context(team)
        print(f"Correct: {context['correct_context']}")
        print(f"Message: {context['message']}")
        if context['navigation_command']:
            print(f"Command: {context['navigation_command']}")

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
