"""
Test Generator Tool
Generates pytest test code for functions and classes
"""

from claude_agent_sdk import tool
import json
from pathlib import Path
from typing import Dict, List


@tool(
    "generate_unit_tests",
    "Generate pytest unit tests for functions or classes",
    {
        "module_name": str,  # Name of the module (e.g., "story_generator")
        "components": list,  # List of functions/classes to test
        "output_path": str  # Where to save test file
    }
)
async def generate_unit_tests(args):
    """
    Generate unit test file for given components
    """
    module_name = args["module_name"]
    components = args["components"]
    output_path = args.get("output_path", f"tests/test_{module_name}.py")

    # Generate test code
    test_code = _generate_test_file(module_name, components)

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write test file
    output_file.write_text(test_code)

    result = {
        "status": "scaffold_created",
        "validated": False,
        "output_path": str(output_file),
        "estimated_test_count": len(components) * 3,
        "warning": "Generated tests are skipped until inputs, dependencies and assertions are reviewed",
        "module_tested": module_name
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "generate_integration_tests",
    "Generate integration tests for module interactions",
    {
        "test_name": str,  # Name of integration test (e.g., "story_generation_workflow")
        "modules": list,  # List of modules involved
        "workflow_description": str,  # Description of workflow to test
        "output_path": str
    }
)
async def generate_integration_tests(args):
    """
    Generate integration test file
    """
    test_name = args["test_name"]
    modules = args["modules"]
    workflow_desc = args["workflow_description"]
    output_path = args.get("output_path", f"tests/test_integration_{test_name}.py")

    # Generate integration test code
    test_code = _generate_integration_test_file(test_name, modules, workflow_desc)

    # Write file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(test_code)

    result = {
        "status": "scaffold_created",
        "validated": False,
        "output_path": str(output_file),
        "test_type": "integration",
        "modules_tested": modules
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "create_fixtures",
    "Generate pytest fixtures in conftest.py",
    {
        "fixtures": list,  # List of fixture definitions
        "output_path": str  # Path to conftest.py
    }
)
async def create_fixtures(args):
    """
    Generate conftest.py with fixtures
    """
    fixtures = args["fixtures"]
    output_path = args.get("output_path", "tests/conftest.py")

    # Generate conftest code
    conftest_code = _generate_conftest_file(fixtures)

    # Write file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(conftest_code)

    result = {
        "status": "scaffold_created",
        "validated": False,
        "output_path": str(output_file),
        "fixtures_created": len(fixtures)
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


# Preserve legacy helper imports while keeping templates independently testable.
from QA_TEAM.tools.test_templates import (
    _generate_test_file, _generate_function_tests, _generate_class_tests,
    _generate_integration_test_file, _generate_conftest_file, _needs_mocking,
)
