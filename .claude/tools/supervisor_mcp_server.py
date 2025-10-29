#!/usr/bin/env python3
"""
MCP Server for Supervisor Tools
Exposes supervisor verification tools via Model Context Protocol
"""

import json
import asyncio
from typing import Any
from supervisor_tools import SupervisorTools

# Import MCP SDK (install with: pip install mcp)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp")
    exit(1)


# Initialize tools
supervisor = SupervisorTools()

# Create MCP server
server = Server("supervisor-tools")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available supervisor verification tools."""
    return [
        Tool(
            name="verify_task_completion",
            description="Main verification orchestrator that checks if a task is truly complete",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to verify"
                    },
                    "team": {
                        "type": "string",
                        "description": "Which team(s) to check (ENGINEERING_TEAM, MARKETING_TEAM, QA_TEAM, or ALL)",
                        "enum": ["ENGINEERING_TEAM", "MARKETING_TEAM", "QA_TEAM", "ALL"],
                        "default": "ALL"
                    },
                    "agents_involved": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent names that worked on the task"
                    },
                    "expected_deliverables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of expected file paths or outputs"
                    }
                },
                "required": ["task_description"]
            }
        ),
        Tool(
            name="check_git_changes",
            description="Verify git commits and file changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "expected_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of files that should have been changed"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch to check (defaults to current branch)"
                    }
                }
            }
        ),
        Tool(
            name="validate_deliverables",
            description="Check that expected files or outputs exist",
            inputSchema={
                "type": "object",
                "properties": {
                    "expected_deliverables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to check"
                    }
                },
                "required": ["expected_deliverables"]
            }
        ),
        Tool(
            name="run_verification_tests",
            description="Run tests and collect results",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of test file or directory paths"
                    },
                    "test_type": {
                        "type": "string",
                        "description": "Type of tests (unit, integration, e2e)",
                        "enum": ["unit", "integration", "e2e"],
                        "default": "unit"
                    }
                },
                "required": ["test_paths"]
            }
        ),
        Tool(
            name="check_code_quality",
            description="Perform code quality checks including syntax, docstrings, and security",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to check"
                    },
                    "criteria": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["no_syntax_errors", "has_docstrings", "no_security_issues"]
                        },
                        "description": "List of criteria to check"
                    }
                },
                "required": ["files"]
            }
        ),
        Tool(
            name="verify_documentation",
            description="Verify documentation exists and is complete",
            inputSchema={
                "type": "object",
                "properties": {
                    "docs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of documentation file paths"
                    },
                    "required_sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of section headers that must be present"
                    }
                },
                "required": ["docs"]
            }
        ),
        Tool(
            name="generate_verification_report",
            description="Generate a comprehensive verification report",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Unique identifier for the task"
                    },
                    "verification_status": {
                        "type": "string",
                        "description": "Overall verification status",
                        "enum": ["PASSED", "FAILED", "PARTIAL"]
                    },
                    "findings": {
                        "type": "object",
                        "description": "Dictionary of verification findings"
                    },
                    "issues_found": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of issues discovered"
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recommended actions"
                    }
                },
                "required": ["task_id", "verification_status", "findings", "issues_found", "recommendations"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute supervisor verification tools."""

    try:
        if name == "verify_task_completion":
            result = supervisor.verify_task_completion(
                task_description=arguments.get("task_description"),
                team=arguments.get("team", "ALL"),
                agents_involved=arguments.get("agents_involved"),
                expected_deliverables=arguments.get("expected_deliverables")
            )

        elif name == "check_git_changes":
            result = supervisor.check_git_changes(
                expected_files=arguments.get("expected_files"),
                branch=arguments.get("branch")
            )

        elif name == "validate_deliverables":
            result = supervisor.validate_deliverables(
                expected_deliverables=arguments["expected_deliverables"]
            )

        elif name == "run_verification_tests":
            result = supervisor.run_verification_tests(
                test_paths=arguments["test_paths"],
                test_type=arguments.get("test_type", "unit")
            )

        elif name == "check_code_quality":
            result = supervisor.check_code_quality(
                files=arguments["files"],
                criteria=arguments.get("criteria")
            )

        elif name == "verify_documentation":
            result = supervisor.verify_documentation(
                docs=arguments["docs"],
                required_sections=arguments.get("required_sections")
            )

        elif name == "generate_verification_report":
            result = supervisor.generate_verification_report(
                task_id=arguments["task_id"],
                verification_status=arguments["verification_status"],
                findings=arguments["findings"],
                issues_found=arguments["issues_found"],
                recommendations=arguments["recommendations"]
            )

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
