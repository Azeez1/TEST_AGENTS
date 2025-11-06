"""
Batch update QA_TEAM agents with workspace headers

This script updates all 5 QA_TEAM agents with workspace context headers.
"""

import os
from pathlib import Path

# Get repository root
repo_root = Path(__file__).parent.parent
agents_dir = repo_root / "QA_TEAM" / ".claude" / "agents"

# All 5 QA agents
qa_agents = [
    "test-orchestrator",
    "unit-test-agent",
    "integration-test-agent",
    "edge-case-agent",
    "fixture-agent"
]

# Workspace header template for QA_TEAM
WORKSPACE_HEADER = """
## 🏢 WORKSPACE CONTEXT & VALIDATION

**You are a QA_TEAM agent** located at `QA_TEAM/.claude/agents/{agent_name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

```
TEST_AGENTS/
└── QA_TEAM/                  ← YOUR ROOT
    ├── memory/               ← Test patterns, learned configurations
    ├── tests/                ← Generated test files go here
    ├── tools/                ← Test generation utilities
    └── .claude/agents/       ← Your definition file
```

**Required paths (use ABSOLUTE only):**
- **Memory:** `QA_TEAM/memory/` or `{{TEST_AGENTS_ROOT}}/QA_TEAM/memory/`
- **Tests:** `QA_TEAM/tests/` or `{{TEST_AGENTS_ROOT}}/QA_TEAM/tests/`
- **Tools:** `QA_TEAM/tools/` or `{{TEST_AGENTS_ROOT}}/QA_TEAM/tools/`

### 🔒 WORKSPACE ENFORCEMENT (CRITICAL)

**BEFORE EVERY TASK - MANDATORY:**

1. **Validate workspace context:**
   ```python
   from tools.workspace_enforcer import validate_workspace
   status = validate_workspace("{agent_name}", "QA_TEAM")
   # Confirms you're in correct workspace
   ```

2. **Get absolute paths:**
   ```python
   from tools.workspace_enforcer import get_absolute_paths
   paths = get_absolute_paths("QA_TEAM")
   # Use paths['memory'], paths['tests'], etc.
   ```

3. **Verify working directory:**
   ```bash
   pwd  # Should show TEST_AGENTS or TEST_AGENTS/QA_TEAM
   ```

### 📁 File Operations - ALWAYS USE ABSOLUTE PATHS

**Testing scope:** You can test ANY codebase in TEST_AGENTS:
- `USER_STORY_AGENT/` - User story generation system
- `MARKETING_TEAM/tools/` - Marketing tools and agents
- `ENGINEERING_TEAM/` - Engineering agents
- `QA_TEAM/` - Your own testing system

**❌ NEVER do this:**
```python
save_test("tests/test_example.py")  # Ambiguous!
```

**✅ ALWAYS do this:**
```python
from tools.path_validator import validate_save_path, validate_read_path

# Saving test files
path = validate_save_path("tests/test_copywriter.py", "QA_TEAM")
# Returns: "QA_TEAM/tests/test_copywriter.py"
save_test(path)

# Reading memory files
config = validate_read_path("learned_patterns.json", "QA_TEAM")
# Returns: "QA_TEAM/memory/learned_patterns.json"
read_from_file(config)
```

**When testing OTHER teams:**
```python
# Testing MARKETING_TEAM code
target = "MARKETING_TEAM/tools/openai_gpt4o_image.py"  # Absolute path
test_output = validate_save_path("tests/marketing/test_image_gen.py", "QA_TEAM")
# Saves test to: QA_TEAM/tests/marketing/test_image_gen.py
```

### 👥 Your Team & Collaboration Scope

**QA_TEAM (5 agents):**
test-orchestrator, unit-test-agent, integration-test-agent, edge-case-agent, fixture-agent

**Cross-team collaboration:**
- ✅ Invoke other QA_TEAM agents directly
- ✅ READ any codebase for testing (MARKETING_TEAM/tools/, USER_STORY_AGENT/, etc.)
- ✅ WRITE tests only to QA_TEAM/tests/ (organized by target: tests/marketing/, tests/user_story/, etc.)
- ⚠️ NEVER modify source code in other teams (read-only testing)
- ⚠️ For coordinating with ENGINEERING_TEAM, user must explicitly request

### 🚨 Workspace Violation Handling

**If workspace validation fails:**
1. Report the error to user
2. Show current directory: `pwd`
3. Show expected directory: `TEST_AGENTS/QA_TEAM/`
4. Ask user: "Should I navigate to QA_TEAM folder?"
5. Do NOT proceed with file operations until workspace is correct

---

"""

def update_agent(agent_name: str) -> bool:
    """Update a single agent file with workspace header"""

    agent_file = agents_dir / f"{agent_name}.md"

    if not agent_file.exists():
        print(f"[ERROR] Agent file not found: {agent_file}")
        return False

    # Read current content
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already updated
    if "WORKSPACE CONTEXT" in content:
        print(f"[SKIP] {agent_name}: Already updated, skipping")
        return True

    # Split into lines
    lines = content.split('\n')

    # Find the YAML frontmatter end (---)
    yaml_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            yaml_end = i
            break

    if yaml_end == -1:
        print(f"[ERROR] {agent_name}: Could not find YAML frontmatter")
        return False

    # Find the "# Agent Name" heading
    heading_idx = -1
    for i in range(yaml_end, len(lines)):
        if lines[i].strip().startswith('#') and not lines[i].strip().startswith('##'):
            heading_idx = i
            break

    if heading_idx == -1:
        print(f"[ERROR] {agent_name}: Could not find main heading")
        return False

    # Update YAML tools list
    tools_start = -1
    tools_end = -1
    for i in range(yaml_end):
        if lines[i].strip().startswith('tools:'):
            tools_start = i
        elif tools_start != -1 and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
            tools_end = i
            break

    if tools_start != -1:
        # Check if workspace tools already added
        tools_section = '\n'.join(lines[tools_start:tools_end if tools_end != -1 else yaml_end])
        if 'workspace_enforcer' not in tools_section:
            # Add workspace tools after "tools:" line
            lines.insert(tools_start + 1, "  - workspace_enforcer")
            lines.insert(tools_start + 2, "  - path_validator")
            heading_idx += 2  # Adjust heading index

    # Insert workspace header after heading
    workspace_header = WORKSPACE_HEADER.format(agent_name=agent_name)
    lines.insert(heading_idx + 1, workspace_header)

    # Write updated content
    updated_content = '\n'.join(lines)
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"[SUCCESS] {agent_name}: Updated successfully")
    return True


def main():
    print("=" * 70)
    print("BATCH UPDATE: QA_TEAM Agents Workspace Headers")
    print("=" * 70)
    print()

    success_count = 0
    fail_count = 0

    for agent_name in qa_agents:
        if update_agent(agent_name):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 70)
    print(f"Successfully updated: {success_count}/{len(qa_agents)}")
    if fail_count > 0:
        print(f"Failed: {fail_count}/{len(qa_agents)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
