"""
Batch update ENGINEERING_TEAM agents with workspace headers

This script updates all 14 ENGINEERING_TEAM agents with workspace context headers.
"""

import os
from pathlib import Path

# Get repository root
repo_root = Path(__file__).parent.parent
agents_dir = repo_root / "ENGINEERING_TEAM" / ".claude" / "agents"

# All 14 ENGINEERING agents
engineering_agents = [
    "cto",
    "devops-engineer",
    "frontend-developer",
    "backend-architect",
    "security-auditor",
    "technical-writer",
    "system-architect",
    "ai-engineer",
    "ui-ux-designer",
    "code-reviewer",
    "test-engineer",
    "prompt-engineer",
    "database-architect",
    "debugger"
]

# Workspace header template for ENGINEERING_TEAM
WORKSPACE_HEADER = """
## 🏢 WORKSPACE CONTEXT & VALIDATION

**You are an ENGINEERING_TEAM agent** located at `ENGINEERING_TEAM/.claude/agents/{agent_name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

```
TEST_AGENTS/
└── ENGINEERING_TEAM/         ← YOUR ROOT
    ├── memory/               ← Deployment configs, infrastructure settings
    ├── outputs/              ← PRDs, specs, diagrams, deployment configs
    ├── docs/                 ← Technical documentation
    ├── tools/                ← Engineering utilities
    └── .claude/agents/       ← Your definition file
```

**Required paths (use ABSOLUTE only):**
- **Memory:** `ENGINEERING_TEAM/memory/` or `{{TEST_AGENTS_ROOT}}/ENGINEERING_TEAM/memory/`
- **Outputs:** `ENGINEERING_TEAM/outputs/` or `{{TEST_AGENTS_ROOT}}/ENGINEERING_TEAM/outputs/`
- **Docs:** `ENGINEERING_TEAM/docs/` or `{{TEST_AGENTS_ROOT}}/ENGINEERING_TEAM/docs/`

### 🔒 WORKSPACE ENFORCEMENT (CRITICAL)

**BEFORE EVERY TASK - MANDATORY:**

1. **Validate workspace context:**
   ```python
   from tools.workspace_enforcer import validate_workspace
   status = validate_workspace("{agent_name}", "ENGINEERING_TEAM")
   # Confirms you're in correct workspace
   ```

2. **Get absolute paths:**
   ```python
   from tools.workspace_enforcer import get_absolute_paths
   paths = get_absolute_paths("ENGINEERING_TEAM")
   # Use paths['memory'], paths['outputs'], paths['docs'], etc.
   ```

3. **Verify working directory:**
   ```bash
   pwd  # Should show TEST_AGENTS or TEST_AGENTS/ENGINEERING_TEAM
   ```

### 📁 File Operations - ALWAYS USE ABSOLUTE PATHS

**Full workspace access:** ENGINEERING_TEAM agents can work with ALL 4 systems:
- `USER_STORY_AGENT/` - Deploy, optimize, review
- `MARKETING_TEAM/` - Code review, optimize agents, deploy tools
- `QA_TEAM/` - Optimize test generation, review code
- `ENGINEERING_TEAM/` - Your own system

**❌ NEVER do this:**
```python
save_prd("outputs/prds/feature_spec.md")  # Ambiguous!
```

**✅ ALWAYS do this:**
```python
from tools.path_validator import validate_save_path, validate_read_path

# Saving files
path = validate_save_path("prds/feature_spec.md", "ENGINEERING_TEAM")
# Returns: "ENGINEERING_TEAM/outputs/prds/feature_spec.md"
save_file(path)

# Reading memory files
config = validate_read_path("deployment_configs.json", "ENGINEERING_TEAM")
# Returns: "ENGINEERING_TEAM/memory/deployment_configs.json"
read_from_file(config)
```

**When working with OTHER teams:**
```python
# Reviewing MARKETING_TEAM code
target = "MARKETING_TEAM/tools/sora_video.py"  # Absolute path
review = validate_save_path("code_reviews/marketing_sora_review.md", "ENGINEERING_TEAM")
# Saves to: ENGINEERING_TEAM/outputs/code_reviews/marketing_sora_review.md
```

### 👥 Your Team & Collaboration Scope

**ENGINEERING_TEAM (14 agents):**
cto, devops-engineer, frontend-developer, backend-architect, security-auditor, technical-writer, system-architect, ai-engineer, ui-ux-designer, code-reviewer, test-engineer, prompt-engineer, database-architect, debugger

**Cross-team collaboration:**
- ✅ Invoke other ENGINEERING_TEAM agents directly (especially via CTO coordinator)
- ✅ READ/WRITE access to all 4 team folders (for optimization, deployment, review)
- ✅ Review and optimize agents from any team
- ✅ Deploy systems across all teams
- ⚠️ Save YOUR outputs to ENGINEERING_TEAM/outputs/ (keep work organized)
- ⚠️ For complex multi-agent workflows, coordinate through CTO

### 🚨 Workspace Violation Handling

**If workspace validation fails:**
1. Report the error to user
2. Show current directory: `pwd`
3. Show expected directory: `TEST_AGENTS/ENGINEERING_TEAM/`
4. Ask user: "Should I navigate to ENGINEERING_TEAM folder?"
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

    # Find the "# Agent Name" heading (or use yaml_end if no heading)
    heading_idx = -1
    for i in range(yaml_end, len(lines)):
        if lines[i].strip().startswith('#') and not lines[i].strip().startswith('##'):
            heading_idx = i
            break

    # If no heading found, insert right after YAML frontmatter
    if heading_idx == -1:
        heading_idx = yaml_end

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
    print("BATCH UPDATE: ENGINEERING_TEAM Agents Workspace Headers")
    print("=" * 70)
    print()

    success_count = 0
    fail_count = 0

    for agent_name in engineering_agents:
        if update_agent(agent_name):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 70)
    print(f"Successfully updated: {success_count}/{len(engineering_agents)}")
    if fail_count > 0:
        print(f"Failed: {fail_count}/{len(engineering_agents)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
