"""
Router Tools for Test Agent
Intent classification and agent selection for test generation
"""

from claude_agent_sdk import tool
import json
from typing import Dict, List


@tool(
    "classify_test_intent",
    "Classify user's testing intent and determine which agents to invoke",
    {
        "user_message": str,
        "conversation_history": list  # Optional conversation context
    }
)
async def classify_test_intent(args):
    """
    Analyze user message and classify testing intent
    """
    user_message = args["user_message"].lower()
    conversation_history = args.get("conversation_history", [])

    # Intent classification logic
    intent_data = {
        "intent": "unclear",
        "confidence": 0.0,
        "agents_to_invoke": [],
        "suggested_clarification": ""
    }

    # Keyword-based classification
    keywords = {
        "scan": ["scan", "analyze", "inspect", "examine", "parse"],
        "unit_test": ["unit test", "function test", "class test", "method test"],
        "integration": ["integration", "workflow", "end-to-end", "e2e", "pipeline"],
        "edge_case": ["edge case", "boundary", "edge", "corner case", "error case"],
        "fixture": ["fixture", "test data", "mock", "conftest"],
        "run": ["run", "execute", "pytest", "test execution"],
        "coverage": ["coverage", "uncovered", "missing", "gaps", "analyze"],
        "generate": ["generate", "create", "write", "build"],
        "comprehensive": ["comprehensive", "complete", "full", "all tests"]
    }

    # Detect scan + generate (most common)
    if any(kw in user_message for kw in keywords["scan"]) and \
       (any(kw in user_message for kw in keywords["generate"]) or \
        any(kw in user_message for kw in keywords["comprehensive"])):
        intent_data = {
            "intent": "scan_and_test",
            "confidence": 0.95,
            "agents_to_invoke": ["test-orchestrator"],
            "reasoning": "User wants to scan codebase and generate comprehensive tests"
        }

    # Unit tests only
    elif any(kw in user_message for kw in keywords["unit_test"]):
        intent_data = {
            "intent": "unit_tests_only",
            "confidence": 0.9,
            "agents_to_invoke": ["unit-test-agent"],
            "reasoning": "User wants to generate unit tests specifically"
        }

    # Integration tests
    elif any(kw in user_message for kw in keywords["integration"]):
        intent_data = {
            "intent": "integration_tests",
            "confidence": 0.9,
            "agents_to_invoke": ["integration-test-agent"],
            "reasoning": "User wants integration/workflow tests"
        }

    # Edge cases
    elif any(kw in user_message for kw in keywords["edge_case"]):
        intent_data = {
            "intent": "edge_cases",
            "confidence": 0.9,
            "agents_to_invoke": ["edge-case-agent"],
            "reasoning": "User wants edge case and boundary tests"
        }

    # Fixtures only
    elif any(kw in user_message for kw in keywords["fixture"]):
        intent_data = {
            "intent": "fixtures_only",
            "confidence": 0.9,
            "agents_to_invoke": ["fixture-agent"],
            "reasoning": "User wants pytest fixtures and test data"
        }

    # Run tests
    elif any(kw in user_message for kw in keywords["run"]) and not any(kw in user_message for kw in keywords["generate"]):
        intent_data = {
            "intent": "run_tests",
            "confidence": 0.95,
            "agents_to_invoke": ["test-orchestrator"],
            "reasoning": "User wants to run existing tests"
        }

    # Coverage analysis
    elif any(kw in user_message for kw in keywords["coverage"]):
        intent_data = {
            "intent": "analyze_coverage",
            "confidence": 0.95,
            "agents_to_invoke": ["test-orchestrator"],
            "reasoning": "User wants coverage analysis"
        }

    # Scan only (analyze codebase)
    elif any(kw in user_message for kw in keywords["scan"]):
        intent_data = {
            "intent": "scan_only",
            "confidence": 0.85,
            "agents_to_invoke": ["test-orchestrator"],
            "reasoning": "User wants to scan/analyze codebase"
        }

    # Comprehensive tests (all types)
    elif any(kw in user_message for kw in keywords["comprehensive"]):
        intent_data = {
            "intent": "comprehensive_tests",
            "confidence": 0.9,
            "agents_to_invoke": ["test-orchestrator", "unit-test-agent", "integration-test-agent", "edge-case-agent", "fixture-agent"],
            "reasoning": "User wants comprehensive testing with all test types"
        }

    # Help/agents list
    elif "help" in user_message or "what can" in user_message or "capabilities" in user_message:
        intent_data = {
            "intent": "help",
            "confidence": 1.0,
            "agents_to_invoke": [],
            "reasoning": "User wants help or agent information"
        }

    # Unclear intent
    else:
        intent_data = {
            "intent": "unclear",
            "confidence": 0.0,
            "agents_to_invoke": [],
            "suggested_clarification": """I can help you with testing! Please specify what you'd like:

• **Scan & Generate** - Analyze codebase and create all tests
• **Unit Tests** - Generate tests for specific functions/classes
• **Integration Tests** - Test module interactions and workflows
• **Edge Cases** - Identify and test boundary conditions
• **Fixtures** - Create pytest fixtures and test data
• **Run Tests** - Execute existing tests
• **Coverage** - Analyze test coverage gaps

Example: "Scan USER_STORY_AGENT and generate comprehensive tests"
"""
        }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(intent_data, indent=2)
        }]
    }


@tool(
    "list_test_agents",
    "List all available testing agents and their capabilities",
    {}
)
async def list_test_agents(args):
    """
    Return information about all specialist testing agents
    """
    agents = [
        {
            "name": "test-orchestrator",
            "purpose": "Main coordinator for test generation and execution",
            "capabilities": [
                "Code scanning and analysis",
                "Test strategy planning",
                "Coordinating specialist agents",
                "Test execution and reporting",
                "Coverage analysis"
            ],
            "tools": [
                "scan_codebase",
                "run_tests",
                "analyze_coverage",
                "Task (for subagents)"
            ],
            "use_for": "Full test suite generation, running tests, coverage analysis"
        },
        {
            "name": "unit-test-agent",
            "purpose": "Generates unit tests for functions and classes",
            "capabilities": [
                "Function/method testing",
                "Class testing",
                "Mock creation",
                "Parametrized tests"
            ],
            "tools": [
                "analyze_function",
                "generate_unit_tests",
                "create_fixtures"
            ],
            "use_for": "Testing individual functions, methods, and classes"
        },
        {
            "name": "integration-test-agent",
            "purpose": "Creates integration tests for module interactions",
            "capabilities": [
                "Workflow testing",
                "Module interaction testing",
                "End-to-end scenarios",
                "External service integration"
            ],
            "tools": [
                "scan_codebase",
                "generate_integration_tests"
            ],
            "use_for": "Testing how modules work together, complete user workflows"
        },
        {
            "name": "edge-case-agent",
            "purpose": "Identifies and tests edge cases and boundary conditions",
            "capabilities": [
                "Boundary value analysis",
                "Error scenario testing",
                "Negative testing",
                "Security testing (SQL injection, XSS)"
            ],
            "tools": [
                "identify_edge_cases",
                "analyze_function"
            ],
            "use_for": "Finding and testing edge cases, boundary values, error conditions"
        },
        {
            "name": "fixture-agent",
            "purpose": "Creates pytest fixtures and reusable test data",
            "capabilities": [
                "Pytest fixture creation",
                "Test data generation",
                "Mock object creation",
                "conftest.py generation"
            ],
            "tools": [
                "create_fixtures",
                "analyze_function"
            ],
            "use_for": "Creating reusable test data, mocks, and fixtures"
        }
    ]

    result = {
        "total_agents": len(agents),
        "agents": agents,
        "coordination": {
            "parallel_execution": "Agents can work simultaneously on different tasks",
            "autonomous": "Each agent makes decisions independently",
            "coordinated": "Test Orchestrator coordinates all agents"
        }
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "extract_target_path",
    "Extract file or directory path from user message",
    {
        "user_message": str
    }
)
async def extract_target_path(args):
    """
    Extract target path for testing from user message
    """
    user_message = args["user_message"]

    # Common patterns for path extraction
    import re

    # Look for explicit paths
    path_patterns = [
        r"['\"]([^'\"]+)['\"]",  # Quoted paths
        r"(?:scan|test|analyze)\s+([^\s]+)",  # After action verbs
        r"(?:path|directory|folder):\s*([^\s]+)",  # Explicit path labels
        r"(?:for|in)\s+([A-Z_]+)",  # ALL_CAPS folder names like USER_STORY_AGENT
        r"\.\./([A-Za-z_]+)",  # Relative paths like ../USER_STORY_AGENT
    ]

    extracted_path = None
    for pattern in path_patterns:
        match = re.search(pattern, user_message)
        if match:
            extracted_path = match.group(1)
            break

    # If no path found, check for common folder names
    if not extracted_path:
        common_folders = ["USER_STORY_AGENT", "MARKETING_TEAM", "QA_TEAM"]
        for folder in common_folders:
            if folder in user_message:
                extracted_path = f"../{folder}"
                break

    result = {
        "found_path": extracted_path is not None,
        "path": extracted_path,
        "suggestion": "Please specify a path like: '../USER_STORY_AGENT'" if not extracted_path else None
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }
