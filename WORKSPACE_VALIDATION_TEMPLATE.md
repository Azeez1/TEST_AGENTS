# Workspace Validation Template

This template provides the standard workspace validation section to include in all agent definitions. This ensures consistency and reduces duplication across all 39+ agents.

## Purpose

Every agent MUST validate its workspace context before performing file operations to:
- Prevent "file not found" errors
- Enable reliable multi-agent coordination
- Simplify debugging
- Ensure absolute path usage

---

## Standard Template for Agent Definitions

Copy this entire section into your agent definition file:

```markdown
## 🏢 WORKSPACE CONTEXT & VALIDATION

**You are a {TEAM_NAME} agent** located at `{TEAM_NAME}/.claude/agents/{agent-name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

\`\`\`
TEST_AGENTS/
└── {TEAM_NAME}/              ← YOUR ROOT
    ├── memory/               ← {Description of memory files}
    ├── outputs/              ← ALL generated content goes here
    ├── docs/                 ← Team documentation
    ├── tools/                ← Custom tools (if applicable)
    └── .claude/agents/       ← Your definition file
\`\`\`

**Required paths (use ABSOLUTE only):**
- **Memory:** `{TEAM_NAME}/memory/` or `{TEST_AGENTS_ROOT}/{TEAM_NAME}/memory/`
- **Outputs:** `{TEAM_NAME}/outputs/` or `{TEST_AGENTS_ROOT}/{TEAM_NAME}/outputs/`
- **Docs:** `{TEAM_NAME}/docs/` or `{TEST_AGENTS_ROOT}/{TEAM_NAME}/docs/`

### 🔒 WORKSPACE ENFORCEMENT (CRITICAL)

**BEFORE EVERY TASK - MANDATORY:**

1. **Validate workspace context:**
   \`\`\`python
   from tools.workspace_enforcer import validate_workspace
   status = validate_workspace("{agent-name}", "{TEAM_NAME}")
   # Confirms you're in correct workspace
   \`\`\`

2. **Get absolute paths:**
   \`\`\`python
   from tools.workspace_enforcer import get_absolute_paths
   paths = get_absolute_paths("{TEAM_NAME}")
   # Use paths['memory'], paths['outputs'], paths['docs'], etc.
   \`\`\`

3. **Verify working directory:**
   \`\`\`bash
   pwd  # Should show TEST_AGENTS or TEST_AGENTS/{TEAM_NAME}
   \`\`\`

### 📁 File Operations - ALWAYS USE ABSOLUTE PATHS

**❌ NEVER do this:**
\`\`\`python
save_to_file("outputs/report.md")          # Ambiguous!
read_from_file("memory/config.json")       # Which memory?
\`\`\`

**✅ ALWAYS do this:**
\`\`\`python
from tools.path_validator import validate_save_path, validate_read_path

# Saving files
path = validate_save_path("report.md", "{TEAM_NAME}")
# Returns: "{TEAM_NAME}/outputs/report.md"
save_to_file(path)

# Reading memory files
config = validate_read_path("config.json", "{TEAM_NAME}")
# Returns: "{TEAM_NAME}/memory/config.json"
read_from_file(config)
\`\`\`

### 👥 Your Team & Collaboration Scope

**{TEAM_NAME} ({X} agents):**
{list-of-agents}

**Cross-team collaboration:**
- ✅ Invoke other {TEAM_NAME} agents directly
- ✅ Reference cross-team resources (TOOL_REGISTRY.md, MULTI_AGENT_GUIDE.md)
- ✅ Use shared MCP servers
- ⚠️ For other teams' agents, user must explicitly request coordination
- ⚠️ NEVER read from other teams' memory folders directly

### 🚨 Workspace Violation Handling

**If workspace validation fails:**
1. Report the error to user
2. Show current directory: `pwd`
3. Show expected directory: `TEST_AGENTS/{TEAM_NAME}/`
4. Ask user: "Should I navigate to {TEAM_NAME} folder?"
5. Do NOT proceed with file operations until workspace is correct

---
```

## Variables to Replace

When using this template, replace these placeholders:

| Variable | Description | Example |
|----------|-------------|---------|
| `{TEAM_NAME}` | Team name | `MARKETING_TEAM`, `ENGINEERING_TEAM`, `QA_TEAM` |
| `{agent-name}` | Agent file name without .md | `copywriter`, `code-reviewer`, `test-engineer` |
| `{Description of memory files}` | What memory folder contains | `Brand voice, email configs, Drive settings` |
| `{X}` | Number of agents in team | `17` (for MARKETING_TEAM) |
| `{list-of-agents}` | Comma-separated agent names | `copywriter, editor, visual-designer, ...` |
| `{TEST_AGENTS_ROOT}` | Optional: Use if absolute path needed | `/home/user/TEST_AGENTS` |

---

## Team-Specific Variations

### MARKETING_TEAM Template

```markdown
**You are a MARKETING_TEAM agent** located at `MARKETING_TEAM/.claude/agents/{agent-name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

\`\`\`
TEST_AGENTS/
└── MARKETING_TEAM/           ← YOUR ROOT
    ├── memory/               ← Brand voice, email configs, Drive settings
    ├── outputs/              ← ALL generated content goes here
    ├── tools/                ← Custom Python tools (GPT-4o images, Sora videos, Gmail, Drive)
    └── .claude/agents/       ← Your definition file
\`\`\`

**MARKETING_TEAM (17 agents):**
router-agent, content-strategist, research-agent, lead-gen-agent, automation-agent, copywriter, editor, social-media-manager, visual-designer, video-producer, seo-specialist, email-specialist, gmail-agent, landing-page-specialist, pdf-specialist, presentation-designer, analyst
```

### ENGINEERING_TEAM Template

```markdown
**You are an ENGINEERING_TEAM agent** located at `ENGINEERING_TEAM/.claude/agents/{agent-name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

\`\`\`
TEST_AGENTS/
└── ENGINEERING_TEAM/         ← YOUR ROOT
    ├── memory/               ← Deployment configs, infrastructure settings
    ├── outputs/              ← PRDs, specs, diagrams, deployment configs
    ├── docs/                 ← Technical documentation
    ├── tools/                ← Engineering utilities
    └── .claude/agents/       ← Your definition file
\`\`\`

**Full workspace access:** ENGINEERING_TEAM agents can work with ALL 4 systems:
- `USER_STORY_AGENT/` - Deploy, optimize, review
- `MARKETING_TEAM/` - Code review, optimize agents, deploy tools
- `QA_TEAM/` - Optimize test generation, review code
- `ENGINEERING_TEAM/` - Your own system

**ENGINEERING_TEAM (14 agents):**
cto, devops-engineer, frontend-developer, backend-architect, security-auditor, technical-writer, system-architect, ai-engineer, ui-ux-designer, code-reviewer, test-engineer, prompt-engineer, database-architect, debugger
```

### QA_TEAM Template

```markdown
**You are a QA_TEAM agent** located at `QA_TEAM/.claude/agents/{agent-name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

\`\`\`
TEST_AGENTS/
└── QA_TEAM/                  ← YOUR ROOT
    ├── test_results/         ← Test execution results
    ├── fixtures/             ← Test data and fixtures
    ├── outputs/              ← Test reports, coverage data
    └── .claude/agents/       ← Your definition file
\`\`\`

**QA_TEAM (5 agents):**
unit-test-agent, integration-test-agent, edge-case-agent, fixture-agent, test-orchestrator
```

### PROPOSAL_TEAM Template

```markdown
**You are a PROPOSAL_TEAM agent** located at `PROPOSAL_TEAM/.claude/agents/{agent-name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

\`\`\`
TEST_AGENTS/
└── PROPOSAL_TEAM/            ← YOUR ROOT
    ├── knowledge_base/       ← RFP templates, past proposals
    ├── outputs/              ← Generated proposals
    └── .claude/agents/       ← Your definition file
\`\`\`

**PROPOSAL_TEAM (1 agent):**
rfp-agent
```

---

## Usage Instructions

### For New Agents

1. Copy the appropriate team template above
2. Replace `{agent-name}` with your agent's name
3. Update any team-specific details
4. Paste into your agent definition after the YAML frontmatter

### For Existing Agents

1. Check if agent already has workspace validation section
2. If outdated or incomplete, replace with template
3. Keep any team-specific variations
4. Ensure absolute paths are used throughout agent definition

---

## Benefits of Using This Template

**Consistency:**
- All agents validate workspace the same way
- Standardized error messages
- Uniform absolute path usage

**Maintainability:**
- Single source of truth for workspace validation
- Easy to update all agents if validation logic changes
- Reduces copy-paste errors

**Reliability:**
- Prevents 90% of file operation errors
- Enables robust multi-agent coordination
- Simplifies debugging

**Developer Experience:**
- Clear expectations for file paths
- Easy to understand workspace structure
- Obvious error messages when validation fails

---

## Related Documentation

- [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) - Complete workspace enforcement guide
- [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - Agent usage patterns
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All agents overview
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Workspace issues debugging

---

## Maintenance

**When to update this template:**
- Workspace structure changes
- New validation logic added
- Team structure reorganization
- Path validation tools updated

**How to propagate updates:**
1. Update this template file
2. Review all agent definitions
3. Update agents that deviate from template
4. Test workspace validation still works
5. Document changes in CHANGELOG.md

---

**Last Updated:** 2025-01-18
**Template Version:** 1.0
