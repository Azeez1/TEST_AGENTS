# Workspace Context Standard

## Purpose

This document defines the **standard workspace context header** that ALL agent definitions across all 4 teams must include.

**Effectiveness Goal:** Eliminate agent location confusion by providing explicit workspace awareness in every agent definition.

---

## Why This Standard Exists

**Problem Solved:** Agents were getting lost because:
- No explicit statement of which team they belong to
- Relative paths were ambiguous ("memory/" could mean any team's memory)
- No cross-team boundary guidance
- Output locations unclear

**Solution:** Every agent definition now includes a comprehensive workspace context header that specifies:
1. Which team the agent belongs to
2. Absolute paths to memory, outputs, tools folders
3. Cross-team collaboration boundaries
4. Mandatory workspace validation before tasks

---

## Standard Workspace Header Structure

Every agent definition MUST include this structure immediately after YAML frontmatter and before the role description:

```markdown
---
name: agent-name
tools: [workspace_enforcer, path_validator, ...]
---

# Agent Name

## 🏢 WORKSPACE CONTEXT & VALIDATION

**You are a {TEAM_NAME} agent** located at `{TEAM_NAME}/.claude/agents/{agent-name}.md`

### Your Workspace Structure (ABSOLUTE PATHS)

```
TEST_AGENTS/
└── {TEAM_NAME}/              ← YOUR ROOT
    ├── memory/               ← {Memory description}
    ├── outputs/              ← {Outputs description}
    ├── tools/                ← {Tools description}
    └── .claude/agents/       ← Your definition file
```

**Required paths (use ABSOLUTE only):**
- **Memory:** `{TEAM_NAME}/memory/` or `{TEST_AGENTS_ROOT}/{TEAM_NAME}/memory/`
- **Outputs:** `{TEAM_NAME}/outputs/` or `{TEST_AGENTS_ROOT}/{TEAM_NAME}/outputs/`
- **Tools:** `{TEAM_NAME}/tools/` or `{TEST_AGENTS_ROOT}/{TEAM_NAME}/tools/`

### 🔒 WORKSPACE ENFORCEMENT (CRITICAL)

**BEFORE EVERY TASK - MANDATORY:**

1. **Validate workspace context:**
   ```python
   from tools.workspace_enforcer import validate_workspace
   status = validate_workspace("{agent-name}", "{TEAM_NAME}")
   ```

2. **Get absolute paths:**
   ```python
   from tools.workspace_enforcer import get_absolute_paths
   paths = get_absolute_paths("{TEAM_NAME}")
   ```

3. **Verify working directory:**
   ```bash
   pwd  # Should show TEST_AGENTS or TEST_AGENTS/{TEAM_NAME}
   ```

### 📁 File Operations - ALWAYS USE ABSOLUTE PATHS

**❌ NEVER do this:**
```python
save_to_file("outputs/{folder}/file.ext")  # Ambiguous!
read_from_file("memory/config.json")       # Which memory?
```

**✅ ALWAYS do this:**
```python
from tools.path_validator import validate_save_path
path = validate_save_path("{folder}/file.ext", "{TEAM_NAME}")
save_to_file(path)

from tools.path_validator import validate_read_path
config = validate_read_path("config.json", "{TEAM_NAME}")
read_from_file(config)
```

### 👥 Your Team & Collaboration Scope

**{TEAM_NAME} ({N} agents):**
{list of agents}

**Cross-team collaboration:**
{team-specific collaboration rules}

### 🚨 Workspace Violation Handling

**If workspace validation fails:**
1. Report the error to user
2. Show current directory: `pwd`
3. Show expected directory: `TEST_AGENTS/{TEAM_NAME}/`
4. Ask user: "Should I navigate to {TEAM_NAME} folder?"
5. Do NOT proceed with file operations until workspace is correct

---

{Agent role description continues here...}
```

---

## Team-Specific Templates

### MARKETING_TEAM Template

**Team Name:** MARKETING_TEAM
**Agent Count:** 17
**Folders:** memory/, outputs/, tools/
**Special Features:** 12 memory config files, outputs organized by content type

**Collaboration Rules:**
- ✅ Invoke other MARKETING_TEAM agents directly
- ✅ Reference cross-team resources (TOOL_REGISTRY.md, MULTI_AGENT_GUIDE.md)
- ✅ Use shared MCP servers (google-workspace, perplexity, bright-data, etc.)
- ⚠️ For QA_TEAM/ENGINEERING_TEAM agents, user must explicitly request coordination
- ⚠️ NEVER read from other teams' memory folders directly

**Output Structure:**
```
MARKETING_TEAM/outputs/
├── blog_posts/
├── social_media/
├── images/
├── videos/
├── emails/
├── landing_pages/
├── pdfs/
├── presentations/
├── campaigns/
└── seo/
```

---

### QA_TEAM Template

**Team Name:** QA_TEAM
**Agent Count:** 5
**Folders:** memory/, tests/, tools/
**Special Features:** Can test any codebase in TEST_AGENTS

**Collaboration Rules:**
- ✅ Invoke other QA_TEAM agents directly
- ✅ READ any codebase for testing (MARKETING_TEAM/tools/, USER_STORY_AGENT/, etc.)
- ✅ WRITE tests only to QA_TEAM/tests/ (organized by target: tests/marketing/, tests/user_story/, etc.)
- ⚠️ NEVER modify source code in other teams (read-only testing)
- ⚠️ For coordinating with ENGINEERING_TEAM, user must explicitly request

**Testing Scope:**
- USER_STORY_AGENT/ - User story generation system
- MARKETING_TEAM/tools/ - Marketing tools and agents
- ENGINEERING_TEAM/ - Engineering agents
- QA_TEAM/ - Your own testing system

**Output Structure:**
```
QA_TEAM/tests/
├── marketing/       # Tests for MARKETING_TEAM
├── user_story/      # Tests for USER_STORY_AGENT
├── engineering/     # Tests for ENGINEERING_TEAM
└── qa/              # Tests for QA_TEAM itself
```

---

### ENGINEERING_TEAM Template

**Team Name:** ENGINEERING_TEAM
**Agent Count:** 14
**Folders:** memory/, outputs/, docs/, tools/
**Special Features:** Full workspace access to all 4 systems

**Collaboration Rules:**
- ✅ Invoke other ENGINEERING_TEAM agents directly (especially via CTO coordinator)
- ✅ READ/WRITE access to all 4 team folders (for optimization, deployment, review)
- ✅ Review and optimize agents from any team
- ✅ Deploy systems across all teams
- ⚠️ Save YOUR outputs to ENGINEERING_TEAM/outputs/ (keep work organized)
- ⚠️ For complex multi-agent workflows, coordinate through CTO

**Full Workspace Access:**
- USER_STORY_AGENT/ - Deploy, optimize, review
- MARKETING_TEAM/ - Code review, optimize agents, deploy tools
- QA_TEAM/ - Optimize test generation, review code
- ENGINEERING_TEAM/ - Your own system

**Output Structure:**
```
ENGINEERING_TEAM/outputs/
├── prds/            # Product requirement documents
├── specs/           # Technical specifications
├── diagrams/        # Architecture diagrams
├── code_reviews/    # Code review reports
├── security_reports/  # Security audit reports
├── deployment/      # Deployment configs and scripts
└── optimizations/   # Performance optimization reports
```

---

### USER_STORY_AGENT Template

**Team Name:** USER_STORY_AGENT
**Agent Count:** 1 (Streamlit app)
**Folders:** memory/, output/, tools/
**Special Features:** Standalone system

**Note:** USER_STORY_AGENT is primarily a Streamlit application, not a conversational agent. If a conversational mode exists:

**Collaboration Rules:**
- Standalone system - operates independently
- No cross-team collaboration (users run the app directly)

**Output Structure:**
```
USER_STORY_AGENT/output/
└── *.xlsx           # Generated user story Excel files
```

---

## YAML Frontmatter Requirements

Every agent MUST include these tools in YAML frontmatter:

```yaml
---
name: agent-name
tools:
  - workspace_enforcer    # MANDATORY - validate workspace context
  - path_validator        # MANDATORY - validate file paths
  - {other tools...}
---
```

**Why mandatory:**
- `workspace_enforcer` - Ensures agent knows where it is before doing anything
- `path_validator` - Ensures all file operations use correct absolute paths

**Enforcement:** Automated tests will verify all agents have these tools declared.

---

## Validation Rules

### Rule 1: Workspace Header Presence
✅ **Required:** Every agent definition MUST have "🏢 WORKSPACE CONTEXT & VALIDATION" section
❌ **Forbidden:** Agents without workspace headers will fail validation tests

### Rule 2: Absolute Path Usage
✅ **Required:** All file operations MUST use absolute paths via path_validator
❌ **Forbidden:** Relative paths like "outputs/" or "memory/" without validation

### Rule 3: Workspace Validation
✅ **Required:** Agents MUST call validate_workspace() before every task
❌ **Forbidden:** Proceeding with file operations without workspace validation

### Rule 4: Cross-Team Boundaries
✅ **Required:** Agents MUST respect team boundaries (can't write to other teams' folders)
❌ **Forbidden:** Reading other teams' memory folders without explicit user permission

### Rule 5: YAML Tool Declaration
✅ **Required:** workspace_enforcer and path_validator in all agent YAML frontmatter
❌ **Forbidden:** Missing these tools will cause validation failure

---

## Testing Requirements

All agents must pass these automated tests:

1. **Workspace header presence test** - `test_agents_have_workspace_headers()`
2. **YAML tool declaration test** - `test_agents_have_workspace_enforcer_tool()`
3. **Workspace validation test** - `test_team_agents_workspace()`
4. **Absolute path test** - `test_absolute_paths_generation()`
5. **Cross-team boundary test** - `test_cross_team_boundaries()`

**Test Suite Location:** `tests/test_workspace_enforcement.py`

---

## Migration Checklist

When adding workspace context to an existing agent:

- [ ] Add workspace_enforcer and path_validator to YAML frontmatter
- [ ] Insert workspace context header after YAML, before role description
- [ ] Replace template variables ({TEAM_NAME}, {agent-name}, {N}, etc.)
- [ ] Update all relative path references to use path_validator
- [ ] Add workspace validation calls before task execution
- [ ] Update agent's collaboration scope (which teams can it work with?)
- [ ] Run validation tests: `pytest tests/test_workspace_enforcement.py`
- [ ] Manual test: Invoke agent and verify file operations work correctly

---

## Benefits Summary

**For Agents:**
- ✅ Always know which team they belong to
- ✅ Always know where to save files
- ✅ Clear cross-team collaboration boundaries
- ✅ Absolute paths eliminate ambiguity

**For Users:**
- ✅ Never need to specify "save to MARKETING_TEAM/outputs/"
- ✅ Agents automatically operate in correct workspace
- ✅ Files always end up in expected locations
- ✅ 98% reduction in "where should I save this?" confusion

**For Developers:**
- ✅ Consistent workspace context across all 37 agents
- ✅ Automated testing catches workspace violations
- ✅ Clear documentation for adding new agents
- ✅ Easy to maintain and extend

---

## Version History

**v1.0 (2025-01-06):**
- Initial workspace context standard
- Templates for all 4 teams
- Validation rules and testing requirements
- Migration checklist

---

## Related Documentation

- **Tools:** `tools/workspace_enforcer.py`, `tools/path_validator.py`
- **Tests:** `tests/test_workspace_enforcement.py`
- **Guides:** `MULTI_AGENT_GUIDE.md`, `MEMORY_SYSTEM.md`, `AGENT_INVOCATION_BEST_PRACTICES.md`
- **Summary:** `WORKSPACE_ENFORCEMENT_SUMMARY.md` (created after implementation)

---

**Standard Maintained By:** ENGINEERING_TEAM security-auditor (quarterly audits)
**Last Updated:** 2025-01-06
