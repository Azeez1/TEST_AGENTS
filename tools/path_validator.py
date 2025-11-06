"""
Path Validator - Validate and correct file paths to ensure correct locations

This tool ensures all file operations use absolute paths and end up in the correct team folders.
It prevents path ambiguity by converting relative paths to absolute paths.

Usage:
    from tools.path_validator import validate_save_path, validate_read_path

    # Validate save path (for writing files)
    path = validate_save_path("blog_posts/article.md", "MARKETING_TEAM")
    # Returns: "MARKETING_TEAM/outputs/blog_posts/article.md"

    # Validate read path (for reading files)
    config = validate_read_path("brand_voice.json", "MARKETING_TEAM")
    # Returns: "MARKETING_TEAM/memory/brand_voice.json"

Author: Claude Code + USER
Created: 2025-01-06
Version: 1.0
"""

import os
from pathlib import Path
from typing import Optional, Dict, List

# Claude Agent SDK tool decorator (mock for testing outside Claude Code)
try:
    from anthropic import tool
except (ImportError, AttributeError):
    # Mock tool decorator for testing
    def tool(func):
        """Mock tool decorator for testing"""
        return func


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


# Team-specific output folder structures
OUTPUT_STRUCTURES = {
    "MARKETING_TEAM": {
        "base": "outputs",
        "subfolders": [
            "blog_posts", "social_media", "images", "videos",
            "emails", "landing_pages", "pdfs", "presentations",
            "campaigns", "seo"
        ]
    },
    "QA_TEAM": {
        "base": "tests",
        "subfolders": [
            "marketing", "user_story", "engineering", "qa",
            "integration", "unit", "edge_cases"
        ]
    },
    "ENGINEERING_TEAM": {
        "base": "outputs",
        "subfolders": [
            "prds", "specs", "diagrams", "code_reviews",
            "security_reports", "deployment", "optimizations"
        ]
    },
    "USER_STORY_AGENT": {
        "base": "output",
        "subfolders": []
    }
}

# Team-specific memory folder structures
MEMORY_FILES = {
    "MARKETING_TEAM": [
        "brand_voice.json", "email_config.json", "google_drive_config.json",
        "visual_guidelines.json", "output_paths.json", "docs_folder_structure.json",
        "seo_config.json", "campaign_templates.json", "voice_interface_config.json",
        "learned_preferences.json", "social_media_accounts.json", "content_calendar.json"
    ],
    "QA_TEAM": [
        "learned_patterns.json", "test_settings.json"
    ],
    "ENGINEERING_TEAM": [
        "deployment_configs.json", "infrastructure_settings.json"
    ],
    "USER_STORY_AGENT": [
        "preferences_store.json"
    ]
}


@tool
def validate_save_path(
    path: str,
    team: str,
    create_missing_folders: bool = False
) -> str:
    """
    Validate and convert a relative save path to an absolute path.

    This function ensures files are saved to the correct team's output folder.
    It automatically prepends the team's output folder if the path is relative.

    Args:
        path: Relative or absolute file path (e.g., "blog_posts/article.md")
        team: Team name (e.g., "MARKETING_TEAM", "QA_TEAM")
        create_missing_folders: If True, create intermediate folders if they don't exist

    Returns:
        Absolute path to save the file (e.g., "MARKETING_TEAM/outputs/blog_posts/article.md")

    Raises:
        ValueError: If team is invalid or path is unsafe

    Example:
        >>> path = validate_save_path("blog_posts/article.md", "MARKETING_TEAM")
        >>> print(path)
        "MARKETING_TEAM/outputs/blog_posts/article.md"
        >>>
        >>> # With absolute path (returns as-is if already correct)
        >>> path = validate_save_path("MARKETING_TEAM/outputs/test.md", "MARKETING_TEAM")
        >>> print(path)
        "MARKETING_TEAM/outputs/test.md"
    """
    if team not in OUTPUT_STRUCTURES:
        raise ValueError(f"Invalid team: {team}. Valid teams: {', '.join(OUTPUT_STRUCTURES.keys())}")

    team_config = OUTPUT_STRUCTURES[team]
    base_folder = team_config["base"]

    repo_root = _get_repo_root()
    team_path = repo_root / team

    # Convert to Path object
    path_obj = Path(path)

    # Check if path is already absolute and correct
    if path_obj.is_absolute():
        # Verify it's in the correct team's output folder
        if str(team_path / base_folder) in str(path_obj):
            return str(path_obj)
        else:
            # Absolute path but wrong location - extract filename and redirect
            filename = path_obj.name
            return str(team_path / base_folder / filename)

    # Relative path - prepend team's output folder
    # Check if path already starts with team name
    parts = path_obj.parts
    if parts[0] == team:
        # Path like "MARKETING_TEAM/outputs/blog_posts/article.md"
        absolute_path = repo_root / path
    elif parts[0] == base_folder:
        # Path like "outputs/blog_posts/article.md"
        absolute_path = team_path / path
    else:
        # Path like "blog_posts/article.md" - prepend team's output folder
        absolute_path = team_path / base_folder / path

    # Create intermediate folders if requested
    if create_missing_folders:
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

    return str(absolute_path)


@tool
def validate_read_path(
    path: str,
    team: str,
    search_folders: Optional[List[str]] = None
) -> str:
    """
    Validate and convert a relative read path to an absolute path.

    This function finds files in the correct team's folder structure.
    By default, it searches memory/ first, then outputs/, then tools/.

    Args:
        path: Relative or absolute file path (e.g., "brand_voice.json")
        team: Team name (e.g., "MARKETING_TEAM", "QA_TEAM")
        search_folders: Custom list of folders to search (default: ["memory", "outputs", "tools"])

    Returns:
        Absolute path to read the file

    Raises:
        ValueError: If team is invalid
        FileNotFoundError: If file doesn't exist in any search location

    Example:
        >>> # Reading memory config
        >>> path = validate_read_path("brand_voice.json", "MARKETING_TEAM")
        >>> print(path)
        "MARKETING_TEAM/memory/brand_voice.json"
        >>>
        >>> # Reading from outputs
        >>> path = validate_read_path("blog_posts/article.md", "MARKETING_TEAM")
        >>> print(path)
        "MARKETING_TEAM/outputs/blog_posts/article.md"
    """
    if team not in OUTPUT_STRUCTURES:
        raise ValueError(f"Invalid team: {team}. Valid teams: {', '.join(OUTPUT_STRUCTURES.keys())}")

    repo_root = _get_repo_root()
    team_path = repo_root / team

    # Convert to Path object
    path_obj = Path(path)

    # Check if path is already absolute
    if path_obj.is_absolute():
        if path_obj.exists():
            return str(path_obj)
        else:
            raise FileNotFoundError(f"Absolute path does not exist: {path_obj}")

    # Relative path - search in team folders
    # Determine search order
    if search_folders is None:
        # Default search order: memory first (most common), then outputs, then tools
        base_folder = OUTPUT_STRUCTURES[team]["base"]
        search_folders = ["memory", base_folder, "tools"]

    # Check if path already starts with team name
    parts = path_obj.parts
    if parts[0] == team:
        # Path like "MARKETING_TEAM/memory/brand_voice.json"
        absolute_path = repo_root / path
        if absolute_path.exists():
            return str(absolute_path)

    # Search in each folder
    for folder in search_folders:
        if parts[0] == folder:
            # Path like "memory/brand_voice.json"
            test_path = team_path / path
        else:
            # Path like "brand_voice.json"
            test_path = team_path / folder / path

        if test_path.exists():
            return str(test_path)

    # File not found - provide helpful error message
    searched_locations = [str(team_path / folder / path) for folder in search_folders]
    raise FileNotFoundError(
        f"File not found: {path}\n"
        f"Searched in: {', '.join(searched_locations)}\n"
        f"Team: {team}\n"
        f"Hint: Check if file exists or use absolute path"
    )


@tool
def validate_cross_team_path(
    path: str,
    source_team: str,
    target_team: str,
    operation: str = "read"
) -> Dict[str, any]:
    """
    Validate cross-team file operations (when one team needs to access another team's files).

    This enforces cross-team boundaries:
    - All teams can READ from any team's folders
    - Only ENGINEERING_TEAM can WRITE to other teams' folders
    - QA_TEAM can READ any codebase but WRITE only to QA_TEAM/tests/

    Args:
        path: File path to validate
        source_team: Team performing the operation (e.g., "QA_TEAM")
        target_team: Team that owns the file (e.g., "MARKETING_TEAM")
        operation: "read" or "write"

    Returns:
        Dictionary with validation result:
        {
            "allowed": bool,
            "path": str,
            "source_team": str,
            "target_team": str,
            "operation": str,
            "message": str,
            "errors": List[str]
        }

    Example:
        >>> # QA reading MARKETING code (allowed)
        >>> result = validate_cross_team_path(
        ...     "MARKETING_TEAM/tools/openai_gpt4o_image.py",
        ...     "QA_TEAM",
        ...     "MARKETING_TEAM",
        ...     "read"
        ... )
        >>> print(result["allowed"])
        True
        >>>
        >>> # QA writing to MARKETING folder (blocked)
        >>> result = validate_cross_team_path(
        ...     "MARKETING_TEAM/tools/new_file.py",
        ...     "QA_TEAM",
        ...     "MARKETING_TEAM",
        ...     "write"
        ... )
        >>> print(result["allowed"])
        False
    """
    errors = []

    # Validate teams
    valid_teams = list(OUTPUT_STRUCTURES.keys())
    if source_team not in valid_teams:
        errors.append(f"Invalid source team: {source_team}")
    if target_team not in valid_teams:
        errors.append(f"Invalid target team: {target_team}")

    if errors:
        return {
            "allowed": False,
            "path": path,
            "source_team": source_team,
            "target_team": target_team,
            "operation": operation,
            "message": "Invalid team names",
            "errors": errors
        }

    # Cross-team rules
    if source_team == target_team:
        # Same team - always allowed
        return {
            "allowed": True,
            "path": path,
            "source_team": source_team,
            "target_team": target_team,
            "operation": operation,
            "message": "Same team operation - allowed",
            "errors": []
        }

    # READ operations
    if operation == "read":
        # All teams can read from any team
        return {
            "allowed": True,
            "path": path,
            "source_team": source_team,
            "target_team": target_team,
            "operation": operation,
            "message": f"{source_team} can read from {target_team}",
            "errors": []
        }

    # WRITE operations
    if operation == "write":
        # ENGINEERING_TEAM has full write access
        if source_team == "ENGINEERING_TEAM":
            return {
                "allowed": True,
                "path": path,
                "source_team": source_team,
                "target_team": target_team,
                "operation": operation,
                "message": "ENGINEERING_TEAM has full write access",
                "errors": []
            }

        # Other teams can't write to different teams
        errors.append(
            f"{source_team} cannot write to {target_team} folders. "
            f"Only ENGINEERING_TEAM has cross-team write access."
        )

        # Special note for QA_TEAM
        if source_team == "QA_TEAM":
            errors.append(
                "QA_TEAM can READ any codebase for testing, "
                "but must WRITE tests to QA_TEAM/tests/ only."
            )

        return {
            "allowed": False,
            "path": path,
            "source_team": source_team,
            "target_team": target_team,
            "operation": operation,
            "message": "Cross-team write operation blocked",
            "errors": errors
        }

    # Invalid operation
    return {
        "allowed": False,
        "path": path,
        "source_team": source_team,
        "target_team": target_team,
        "operation": operation,
        "message": f"Invalid operation: {operation}",
        "errors": [f"Operation must be 'read' or 'write', got: {operation}"]
    }


def get_team_from_path(path: str) -> Optional[str]:
    """
    Extract team name from a file path.

    Args:
        path: File path (e.g., "MARKETING_TEAM/outputs/test.md")

    Returns:
        Team name if found, None otherwise

    Example:
        >>> get_team_from_path("MARKETING_TEAM/outputs/blog_posts/article.md")
        "MARKETING_TEAM"
    """
    path_obj = Path(path)
    parts = path_obj.parts

    valid_teams = list(OUTPUT_STRUCTURES.keys())
    for part in parts:
        if part in valid_teams:
            return part

    return None


# CLI interface for testing
if __name__ == "__main__":
    print("=" * 70)
    print("PATH VALIDATOR - Test Mode")
    print("=" * 70)

    # Test validate_save_path
    print("\n1. Testing validate_save_path()...")
    print("-" * 70)

    save_tests = [
        ("blog_posts/article.md", "MARKETING_TEAM"),
        ("outputs/blog_posts/article.md", "MARKETING_TEAM"),
        ("MARKETING_TEAM/outputs/blog_posts/article.md", "MARKETING_TEAM"),
        ("tests/test_example.py", "QA_TEAM"),
        ("prds/feature_spec.md", "ENGINEERING_TEAM"),
    ]

    for path, team in save_tests:
        print(f"\nInput: {path} (Team: {team})")
        result = validate_save_path(path, team)
        print(f"Output: {result}")

    # Test validate_read_path
    print("\n\n2. Testing validate_read_path()...")
    print("-" * 70)

    read_tests = [
        ("brand_voice.json", "MARKETING_TEAM"),
        ("memory/email_config.json", "MARKETING_TEAM"),
        ("learned_patterns.json", "QA_TEAM"),
    ]

    for path, team in read_tests:
        print(f"\nInput: {path} (Team: {team})")
        try:
            result = validate_read_path(path, team)
            print(f"Output: {result}")
        except FileNotFoundError as e:
            print(f"File not found (expected if file doesn't exist): {e}")

    # Test validate_cross_team_path
    print("\n\n3. Testing validate_cross_team_path()...")
    print("-" * 70)

    cross_team_tests = [
        ("MARKETING_TEAM/tools/test.py", "QA_TEAM", "MARKETING_TEAM", "read"),
        ("MARKETING_TEAM/tools/test.py", "QA_TEAM", "MARKETING_TEAM", "write"),
        ("MARKETING_TEAM/tools/test.py", "ENGINEERING_TEAM", "MARKETING_TEAM", "write"),
    ]

    for path, source, target, op in cross_team_tests:
        print(f"\n{source} trying to {op} {target} file: {path}")
        result = validate_cross_team_path(path, source, target, op)
        print(f"Allowed: {result['allowed']}")
        print(f"Message: {result['message']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")

    # Test get_team_from_path
    print("\n\n4. Testing get_team_from_path()...")
    print("-" * 70)

    path_tests = [
        "MARKETING_TEAM/outputs/blog_posts/article.md",
        "QA_TEAM/tests/test_example.py",
        "some/random/path.txt"
    ]

    for path in path_tests:
        team = get_team_from_path(path)
        print(f"\nPath: {path}")
        print(f"Team: {team if team else 'None (not in team folder)'}")

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
