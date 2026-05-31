#!/usr/bin/env python3
"""PostToolUse hook dispatcher for TEST_AGENTS multi-agent system."""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True, choices=[
        "audit_logger", "output_verifier", "brand_voice"
    ])
    args = parser.parse_args()

    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    tool_output = hook_input.get("tool_output", "")

    try:
        if args.gate == "audit_logger":
            from audit_logger import log_tool_usage
            log_tool_usage(tool_name, tool_input, tool_output)
        elif args.gate == "output_verifier":
            from quality_gate import verify_output_location
            result = verify_output_location(tool_name, tool_input)
            if not result.get("valid", True):
                print(json.dumps({"warning": result.get("message", "")}))
        elif args.gate == "brand_voice":
            from quality_gate import check_brand_voice
            result = check_brand_voice(tool_name, tool_input)
            if result.get("needs_review"):
                print(json.dumps({"warning": result.get("message", "")}))

        sys.exit(0)

    except Exception as e:
        sys.stderr.write(f"Hook error ({args.gate}): {str(e)}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
