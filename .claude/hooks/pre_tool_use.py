#!/usr/bin/env python3
"""PreToolUse hook dispatcher for TEST_AGENTS multi-agent system."""
import sys
import json
import argparse
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True, choices=[
        "workspace_boundary", "secret_exposure", "path_normalizer"
    ])
    args = parser.parse_args()

    # Read tool call from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Fail open on bad input

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    try:
        if args.gate == "workspace_boundary":
            from workspace_gate import check_workspace_boundary
            result = check_workspace_boundary(tool_name, tool_input)
        elif args.gate == "secret_exposure":
            from security_gate import check_secret_exposure
            result = check_secret_exposure(tool_name, tool_input)
        elif args.gate == "path_normalizer":
            from path_normalizer import normalize_path
            result = normalize_path(tool_name, tool_input)
        else:
            result = {"allowed": True}

        if not result.get("allowed", True):
            # Output rejection message for the agent to see
            print(json.dumps({"error": result.get("message", "Blocked by policy")}))
            sys.exit(1)

        # If path was normalized, output the updated input
        if result.get("updated_input"):
            print(json.dumps(result["updated_input"]))

        sys.exit(0)

    except Exception as e:
        # Fail open on errors -- log but don't block
        sys.stderr.write(f"Hook error ({args.gate}): {str(e)}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
