#!/usr/bin/env python3
"""
Agent Definition Validator

Validates all agent definitions in ENGINEERING_TEAM for:
- Valid YAML frontmatter
- Correct naming format (lowercase-kebab-case)
- Model field present and up-to-date
- Tools format (inline, capitalized)
- Description present
- Agent file exists and readable

Usage:
    python validate_agents.py
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple

# Expected latest model versions
LATEST_SONNET = "claude-sonnet-4-5-20250929"
LATEST_OPUS = "claude-opus-4-20250514"

# Valid model versions
VALID_MODELS = {LATEST_SONNET, LATEST_OPUS}


def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract YAML frontmatter from markdown file"""
    lines = content.split('\n')

    if not lines or lines[0].strip() != '---':
        return {}, content

    frontmatter_lines = []
    content_start = 0

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            content_start = i + 1
            break
        frontmatter_lines.append(line)

    # Parse simple YAML (key: value format)
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    remaining_content = '\n'.join(lines[content_start:])
    return frontmatter, remaining_content


def validate_agent(agent_path: str) -> Dict[str, any]:
    """Validate single agent definition"""
    result = {
        'path': agent_path,
        'name': os.path.basename(agent_path),
        'valid': True,
        'issues': [],
        'warnings': [],
        'info': {}
    }

    # Read file
    try:
        with open(agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result['valid'] = False
        result['issues'].append(f"Cannot read file: {e}")
        return result

    # Extract frontmatter
    frontmatter, _ = extract_frontmatter(content)

    if not frontmatter:
        result['valid'] = False
        result['issues'].append("No valid YAML frontmatter found")
        return result

    # Check name field
    if 'name' not in frontmatter:
        result['valid'] = False
        result['issues'].append("Missing 'name' field")
    else:
        name = frontmatter['name']
        result['info']['name'] = name

        # Check for kebab-case format
        if ' ' in name:
            result['valid'] = False
            result['issues'].append(f"Name contains spaces: '{name}' (should be kebab-case)")
        elif name != name.lower():
            result['warnings'].append(f"Name not lowercase: '{name}'")
        elif '_' in name:
            result['warnings'].append(f"Name uses underscores: '{name}' (prefer hyphens)")

    # Check description field
    if 'description' not in frontmatter:
        result['valid'] = False
        result['issues'].append("Missing 'description' field")
    else:
        result['info']['description'] = frontmatter['description'][:50] + "..."

    # Check model field
    if 'model' not in frontmatter:
        result['valid'] = False
        result['issues'].append("Missing 'model' field")
    else:
        model = frontmatter['model']
        result['info']['model'] = model

        if model not in VALID_MODELS:
            if model in ['sonnet', 'opus']:
                result['valid'] = False
                result['issues'].append(f"Model uses short name: '{model}' (should be explicit version)")
            else:
                result['warnings'].append(f"Model version may be outdated: '{model}'")

        # Check if using latest
        if model == LATEST_SONNET:
            result['info']['model_status'] = "(Latest Sonnet)"
        elif model == LATEST_OPUS:
            result['info']['model_status'] = "(Latest Opus)"
        else:
            result['info']['model_status'] = "(Check version)"

    # Check tools field
    if 'tools' not in frontmatter:
        result['valid'] = False
        result['issues'].append("Missing 'tools' field")
    else:
        tools = frontmatter['tools']
        result['info']['tools'] = tools

        # Check if inline format (not array)
        if tools.startswith('-') or tools.startswith('['):
            result['valid'] = False
            result['issues'].append("Tools in array format (should be inline comma-separated)")

        # Count tools
        tools_list = [t.strip() for t in tools.split(',')]
        result['info']['tool_count'] = len(tools_list)

    return result


def validate_all_agents(team_path: str) -> List[Dict]:
    """Validate all agents in a team"""
    agents_dir = os.path.join(team_path, '.claude', 'agents')

    if not os.path.exists(agents_dir):
        print(f"❌ Agents directory not found: {agents_dir}")
        return []

    agent_files = glob.glob(os.path.join(agents_dir, '*.md'))
    results = []

    for agent_file in sorted(agent_files):
        result = validate_agent(agent_file)
        results.append(result)

    return results


def print_results(results: List[Dict]):
    """Print validation results"""
    print("=" * 70)
    print("ENGINEERING_TEAM Agent Validation Report")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for result in results:
        if result['valid']:
            passed += 1
            print(f"[PASS] {result['name']}")
            if 'name' in result['info']:
                print(f"   Name: {result['info']['name']}")
            if 'model' in result['info']:
                status = result['info'].get('model_status', '')
                print(f"   Model: {result['info']['model']} {status}")
            if 'tool_count' in result['info']:
                print(f"   Tools: {result['info']['tool_count']} tools")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   [WARN] {warning}")
        else:
            failed += 1
            print(f"[FAIL] {result['name']}")
            for issue in result['issues']:
                print(f"   [ERROR] {issue}")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   [WARN] {warning}")

        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total Agents: {len(results)}")
    print(f"[PASS] Passed: {passed} ({passed/len(results)*100:.0f}%)")
    print(f"[FAIL] Failed: {failed} ({failed/len(results)*100:.0f}%)")

    if failed == 0:
        print("\nAll agents validated successfully!")
    else:
        print(f"\n{failed} agent(s) need fixes")
        print("\nFailed agents:")
        for result in results:
            if not result['valid']:
                print(f"  - {result['name']}")

    return failed == 0


def main():
    """Main validation function"""
    # Get ENGINEERING_TEAM path
    script_dir = Path(__file__).parent.parent

    results = validate_all_agents(str(script_dir))

    if not results:
        print("No agents found to validate")
        return 1

    success = print_results(results)

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
