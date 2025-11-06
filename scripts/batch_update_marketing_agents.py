"""
Batch update remaining MARKETING_TEAM agents with workspace headers

This script updates the remaining 10 MARKETING_TEAM agents with workspace context headers.
"""

import os
from pathlib import Path

# Get repository root
repo_root = Path(__file__).parent.parent
agents_dir = repo_root / "MARKETING_TEAM" / ".claude" / "agents"

# Agents to update
remaining_agents = [
    "social-media-manager",
    "visual-designer",
    "video-producer",
    "seo-specialist",
    "email-specialist",
    "gmail-agent",
    "landing-page-specialist",
    "pdf-specialist",
    "presentation-designer",
    "analyst"
]

# Workspace header template
WORKSPACE_HEADER = """
## 🏢 WORKSPACE CONTEXT & VALIDATION

**You are a MARKETING_TEAM agent** located at `MARKETING_TEAM/.claude/agents/{agent_name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

```
TEST_AGENTS/
└── MARKETING_TEAM/           ← YOUR ROOT
    ├── memory/               ← Brand voice, email configs, Drive settings
    ├── outputs/              ← ALL generated content goes here
    ├── tools/                ← Custom Python tools (GPT-4o images, Sora videos, Gmail, Drive)
    └── .claude/agents/       ← Your definition file
```

**Required paths (use ABSOLUTE only):**
- **Memory:** `MARKETING_TEAM/memory/` or `{{TEST_AGENTS_ROOT}}/MARKETING_TEAM/memory/`
- **Outputs:** `MARKETING_TEAM/outputs/` or `{{TEST_AGENTS_ROOT}}/MARKETING_TEAM/outputs/`
- **Tools:** `MARKETING_TEAM/tools/` or `{{TEST_AGENTS_ROOT}}/MARKETING_TEAM/tools/`

### 🔒 WORKSPACE ENFORCEMENT (CRITICAL)

**BEFORE EVERY TASK - MANDATORY:**

1. **Validate workspace context:**
   ```python
   from tools.workspace_enforcer import validate_workspace
   status = validate_workspace("{agent_name}", "MARKETING_TEAM")
   # Confirms you're in correct workspace
   ```

2. **Get absolute paths:**
   ```python
   from tools.workspace_enforcer import get_absolute_paths
   paths = get_absolute_paths("MARKETING_TEAM")
   # Use paths['memory'], paths['outputs'], etc.
   ```

3. **Verify working directory:**
   ```bash
   pwd  # Should show TEST_AGENTS or TEST_AGENTS/MARKETING_TEAM
   ```

### 📁 File Operations - ALWAYS USE ABSOLUTE PATHS

**❌ NEVER do this:**
```python
save_to_file("outputs/blog_posts/article.md")  # Ambiguous!
read_from_file("memory/brand_voice.json")      # Which memory?
```

**✅ ALWAYS do this:**
```python
from tools.path_validator import validate_save_path, validate_read_path

# Saving files
path = validate_save_path("blog_posts/article.md", "MARKETING_TEAM")
# Returns: "MARKETING_TEAM/outputs/blog_posts/article.md"
save_to_file(path)

# Reading memory files
config = validate_read_path("brand_voice.json", "MARKETING_TEAM")
# Returns: "MARKETING_TEAM/memory/brand_voice.json"
read_from_file(config)
```

### 👥 Your Team & Collaboration Scope

**MARKETING_TEAM (17 agents):**
router-agent, content-strategist, research-agent, lead-gen-agent, automation-agent, copywriter, editor, social-media-manager, visual-designer, video-producer, seo-specialist, email-specialist, gmail-agent, landing-page-specialist, pdf-specialist, presentation-designer, analyst

**Cross-team collaboration:**
- ✅ Invoke other MARKETING_TEAM agents directly
- ✅ Reference cross-team resources (TOOL_REGISTRY.md, MULTI_AGENT_GUIDE.md)
- ✅ Use shared MCP servers (google-workspace, perplexity, bright-data, playwright, etc.)
- ⚠️ For QA_TEAM/ENGINEERING_TEAM agents, user must explicitly request coordination
- ⚠️ NEVER read from other teams' memory folders directly

### 🚨 Workspace Violation Handling

**If workspace validation fails:**
1. Report the error to user
2. Show current directory: `pwd`
3. Show expected directory: `TEST_AGENTS/MARKETING_TEAM/`
4. Ask user: "Should I navigate to MARKETING_TEAM folder?"
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
    print("BATCH UPDATE: MARKETING_TEAM Agents Workspace Headers")
    print("=" * 70)
    print()

    success_count = 0
    fail_count = 0

    for agent_name in remaining_agents:
        if update_agent(agent_name):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 70)
    print(f"Successfully updated: {success_count}/{len(remaining_agents)}")
    if fail_count > 0:
        print(f"Failed: {fail_count}/{len(remaining_agents)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
