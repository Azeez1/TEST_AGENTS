# PRE-FLIGHT CHECKS - Mandatory Workflow

**Last Updated:** 2025-11-03
**Applies To:** All 37 agents before creating/declaring/using any tool or skill
**Enforcement:** CTO agent + all engineering agents

---

## 🎯 Purpose

This document defines **mandatory checklists** agents MUST complete before:
1. Declaring a skill in agent YAML frontmatter
2. Creating a new custom tool
3. Using an existing tool/skill for the first time

**Goal:** Prevent duplication, configuration errors, and ensure proper tool/skill/MCP usage

---

## ✅ Part 1: Before Declaring a SKILL in Agent YAML

### The Problem

**Common Mistake:**
```yaml
# ❌ WRONG - Declaring skills that aren't enabled
skills:
  - pdf
  - pptx
  - docx
  - xlsx
```

**Why This Fails:**
- `pdf` and `pptx` ARE enabled in MARKETING_TEAM settings ✅
- `docx` and `xlsx` are NOT enabled ❌
- Agent will fail silently when trying to use disabled skills
- No clear error message, just "skill not found"

### ✅ Skill Declaration Checklist

**Before adding a skill to your agent's YAML frontmatter, complete ALL steps:**

#### Step 1: Verify Skill Exists

```bash
# Check if skill folder exists
ls .claude/skills/<skill-name>/

# Example: Check if pdf skill exists
ls .claude/skills/pdf/
# Expected output: SKILL.md, forms.md, reference.md
```

**If skill doesn't exist:**
- ❌ DO NOT declare it in agent YAML
- ✅ Request skill creation (use `skill-creator` skill or file issue)

---

#### Step 2: Verify Skill is Enabled in Settings

```bash
# Check team-level settings (MARKETING_TEAM example)
cat MARKETING_TEAM/.claude/settings.json | grep "<skill-name>"

# Example: Check if pdf skill is enabled
cat MARKETING_TEAM/.claude/settings.json | grep "pdf"
# Expected output: "pdf": { "enabled": true }
```

**Alternative:** Check root-level settings
```bash
cat .claude/settings.json | grep "<skill-name>"
```

**If skill is NOT in settings.json:**
- ❌ DO NOT declare it in agent YAML yet
- ✅ Request addition to settings.json
- ✅ Test skill works after enabling
- ✅ THEN declare in agent YAML

---

#### Step 3: Check Enabled Skills by Team

**MARKETING_TEAM** (`.claude/settings.json`):
```
✅ Enabled Skills:
- algorithmic-art (p5.js generative art)
- artifacts-builder (React + shadcn/ui)
- brand-guidelines (Anthropic brand colors)
- canvas-design (50+ fonts, professional design)
- flow-diagram (Mermaid diagrams)
- internal-comms (status reports, newsletters)
- mcp-builder (create MCP servers)
- pdf (pypdf library - comprehensive PDF creation)
- pdf-filler (fillable PDF forms)
- pptx (html2pptx, PowerPoint generation)
- skill-creator (create new skills)
- slack-gif-creator (animated GIFs for Slack)
- theme-factory (10 pre-set themes)
- filesystem (file read/write/list/delete)
- figma (Figma API integration)
- context7 (context management)

❌ NOT Enabled (do not declare unless added to settings):
- docx (use Google Docs MCP instead)
- xlsx (use Google Sheets MCP instead)
```

**Why docx/xlsx are NOT enabled:**
- Google Workspace MCP provides superior cloud-based docs/sheets
- MCP enables collaboration, sharing, real-time editing
- Skills would be local-only, less feature-rich
- **Exception:** If offline work or advanced Excel features needed, request enablement

---

#### Step 4: Check for MCP Alternative

**Before declaring a skill, check if MCP server provides same functionality:**

| Skill | MCP Alternative | Recommendation |
|-------|----------------|----------------|
| `pdf` | Google Docs → PDF export | ✅ Use skill (more comprehensive, offline capable) |
| `pptx` | N/A | ✅ Use skill (no MCP alternative) |
| `docx` | `mcp__google-workspace__create_doc` | ⚠️ Prefer MCP (cloud-based, collaborative) |
| `xlsx` | `mcp__google-workspace__create_spreadsheet` | ⚠️ Prefer MCP (cloud-based, collaborative) |
| `canvas-design` | `mcp__marketing-tools__generate_gpt4o_image` | ✅ Both valid (skill for design, MCP for AI images) |
| `filesystem` | N/A | ✅ Use skill (local file operations) |

**Rule:** If MCP provides same functionality AND is cloud-based, prefer MCP over skill

---

#### Step 5: Document Priority Order in Agent Instructions

**If your agent has BOTH skill and MCP for same function:**

**✅ REQUIRED: Add decision matrix to agent instructions**

**Example (analyst.md):**
```markdown
## Data Export Workflow

### Excel/Spreadsheet Generation

**Method 1: Google Sheets (RECOMMENDED)**
```yaml
tool: mcp__google-workspace__create_spreadsheet
```
Use Google Sheets MCP for:
- Cloud-based sharing with stakeholders
- Real-time collaboration
- Direct Google Drive integration

**Method 2: Local Excel (Offline Alternative - NOT ENABLED)**
```yaml
skill: xlsx (requires settings.json enablement)
```
Use xlsx skill when:
- Offline work required
- Advanced Excel features needed (macros, complex formulas)
- Local file storage preferred

**Current Status:** xlsx skill NOT enabled in settings.json
**Priority:** Try MCP first → If MCP fails, notify user xlsx skill not available
```

**Required Elements:**
1. ✅ List both methods (MCP and skill)
2. ✅ Specify which is PRIMARY (Method 1)
3. ✅ Explain WHEN to use each method
4. ✅ Note if skill is NOT enabled (current status)
5. ✅ Document fallback logic (MCP fails → try skill)

---

### ✅ Skill Declaration Template

**Correct YAML frontmatter:**
```yaml
---
name: Agent Name
description: What this agent does
tools:
  - mcp__google-workspace__create_doc  # MCP tools listed first
  - mcp__google-workspace__create_spreadsheet
  - upload_to_drive  # Custom Python tools
skills:
  - pdf           # ✅ Enabled in settings
  - pdf-filler    # ✅ Enabled in settings
  - canvas-design # ✅ Enabled in settings
  # ❌ NOT declaring docx/xlsx (not enabled)
---
```

---

## 🛠️ Part 2: Before Creating a NEW TOOL

### The Problem

**Common Mistake:**
```python
# Agent creates new email_sender.py
# ...but send_email_with_attachment.py already exists!
# Result: Duplicate tool, wasted effort
```

### ✅ Tool Creation Checklist

**Before writing ANY new tool code, complete ALL steps:**

#### Step 1: Check TOOL_REGISTRY.md

```markdown
**READ:** TOOL_REGISTRY.md (complete inventory)

**Search for:**
1. Similar tool names (e.g., searching for "email" finds send_email_with_attachment.py)
2. Similar functionality (e.g., "PDF generation" finds pdf_generator.py, pdf skill)
3. Tools in same category (e.g., "Integration" category lists all email/drive tools)
```

**If tool exists in registry:**
- ❌ DO NOT create duplicate tool
- ✅ Use existing tool
- ✅ Update agent YAML to declare existing tool
- ✅ Read tool documentation for usage examples

---

#### Step 2: Check MCP Servers (.mcp.json)

```bash
# Read MCP server configuration
cat .mcp.json

# Check for relevant MCP servers
# Example: Looking for email functionality
cat .mcp.json | grep -A 10 "google-workspace"
# Result: Finds send_email, search_emails, get_email tools
```

**7 MCP Servers Available:**
1. **marketing-tools** - OpenAI APIs (GPT-4o images, Sora videos)
2. **google-workspace** - Gmail, Docs, Sheets, Drive, Calendar
3. **perplexity** - Web research with citations
4. **bright-data** - Web scraping, SERP scraping (5K free/month)
5. **playwright** - Browser automation, screenshots, web navigation
6. **n8n-mcp** - Workflow automation (400+ integrations)
7. **sequential-thinking** - Step-by-step problem solving

**If MCP provides functionality:**
- ❌ DO NOT create custom tool
- ✅ Use MCP tool (e.g., `mcp__google-workspace__send_email`)
- ✅ Update agent YAML to declare MCP tool
- ✅ Test MCP tool works with your use case

---

#### Step 3: Check .claude/skills/

```bash
# List all available skills
ls .claude/skills/

# Check specific skill details
cat .claude/skills/<skill-name>/SKILL.md

# Example: Check if PDF skill exists
cat .claude/skills/pdf/SKILL.md
# Result: Shows pypdf-based PDF creation capabilities
```

**18 Skills Available:**
- Visual (5): algorithmic-art, canvas-design, slack-gif-creator, theme-factory, flow-diagram
- Development (3): artifacts-builder, mcp-builder, skill-creator
- Content (3): internal-comms, brand-guidelines, pdf-filler
- Documents (4): pdf, pptx, docx, xlsx
- Integration (3): filesystem, figma, context7

**If skill provides functionality:**
- ❌ DO NOT create custom tool
- ✅ Use skill (e.g., `pdf` skill for PDF generation)
- ✅ Verify skill is enabled in `.claude/settings.json`
- ✅ Update agent YAML to declare skill
- ✅ Test skill works

---

#### Step 4: Check Existing Custom Tools

```bash
# List all custom tools by team
find . -name "*.py" -path "*/tools/*"

# Example output:
# MARKETING_TEAM/tools/openai_gpt4o_image.py
# MARKETING_TEAM/tools/sora_video.py
# MARKETING_TEAM/tools/upload_to_drive.py
# QA_TEAM/tools/test_generator.py
# ...
```

**Search for similar functionality:**
```bash
# Search tool code for keywords
grep -r "send.*email" */tools/*.py
# Result: Finds send_email_with_attachment.py

grep -r "upload.*drive" */tools/*.py
# Result: Finds upload_to_drive.py
```

**If similar tool exists:**
- ❌ DO NOT create duplicate
- ✅ Use existing tool
- ✅ Read tool docstring for usage
- ✅ Update agent YAML to declare existing tool

---

#### Step 5: Justify New Tool Creation

**If no existing solution (MCP/skill/tool), document justification:**

**Required Justification Format:**
```markdown
## New Tool Justification: <tool_name>

**Why MCP is insufficient:**
- [ ] No MCP server exists for this API/functionality
- [ ] MCP has technical limitation (e.g., can't handle binary files)
- [ ] Explain: _______________________________

**Why Skill is insufficient:**
- [ ] No skill exists for this functionality
- [ ] Skill exists but disabled in settings
- [ ] Skill lacks required features
- [ ] Explain: _______________________________

**Why existing custom tools are insufficient:**
- [ ] No existing tool provides this functionality
- [ ] Existing tool has different purpose
- [ ] Explain: _______________________________

**What this tool will do:**
- Purpose: _______________________________
- Use cases: _______________________________
- Which agents will use it: _______________________________
- Expected usage frequency: _______________________________

**MCP Gap-Filler?**
- [ ] YES - This tool fills a gap MCP servers can't handle
- [ ] NO - This is new functionality
```

**Example (upload_to_drive.py):**
```markdown
## New Tool Justification: upload_to_drive.py

**Why MCP is insufficient:**
- ✅ Google Workspace MCP can't handle binary files
- MCP create_drive_file only works with text files
- Technical limitation: MCP doesn't support binary uploads

**Why Skill is insufficient:**
- ✅ No skill exists for Google Drive uploads
- filesystem skill only does local file operations

**Why existing custom tools are insufficient:**
- ✅ No existing tool provides binary Drive uploads

**What this tool will do:**
- Purpose: Upload binary files (PDFs, images, videos) to Google Drive
- Use cases: PDF specialist uploads whitepapers, visual designer uploads images
- Which agents will use it: pdf-specialist, presentation-designer, visual-designer, video-producer
- Expected usage frequency: Multiple times per day (every file generation)

**MCP Gap-Filler?**
- ✅ YES - Fills Google Workspace MCP limitation (binary files)
```

---

#### Step 6: Create Tool with Proper Documentation

**If justified, create tool with:**

**1. Comprehensive Docstring:**
```python
"""
Tool Name - Brief one-line description

Purpose:
    Detailed explanation of what this tool does and why it exists.
    Explain any MCP gaps this fills.

Parameters:
    param1 (type): Description of parameter
    param2 (type): Description of parameter

Returns:
    return_type: Description of return value

Raises:
    ErrorType: When this error occurs

Usage Examples:
    >>> from tools.tool_name import function_name
    >>> result = function_name(param1="value1", param2="value2")
    >>> print(result)
    Expected output

MCP Gap-Filler:
    This tool fills a gap where MCP <server_name> can't <limitation>.
    Example: Google Workspace MCP can't upload binary files.

Used By:
    - agent1 (use case)
    - agent2 (use case)

See Also:
    - TOOL_REGISTRY.md entry
    - MCP server: <server_name>
    - Skill: <skill_name> (if related)
"""
```

**2. Error Handling:**
```python
try:
    # Tool logic
    result = perform_operation()
    return result
except APIKeyError:
    raise ToolError(
        "API key not found. Set GOOGLE_API_KEY environment variable. "
        "See docs/getting-started/api-setup.md for configuration."
    )
except RateLimitError as e:
    raise ToolError(
        f"API rate limit exceeded: {str(e)}. "
        "Wait 60 seconds and retry."
    )
except Exception as e:
    raise ToolError(
        f"Unexpected error in <tool_name>: {str(e)}. "
        "Check logs for details."
    )
```

**3. Logging:**
```python
import logging

logger = logging.getLogger(__name__)

def function_name():
    logger.info("Starting <operation>")
    try:
        result = perform_operation()
        logger.info(f"<operation> completed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"<operation> failed: {str(e)}", exc_info=True)
        raise
```

---

#### Step 7: Update Documentation After Creation

**Immediately after creating tool:**

**1. Update TOOL_REGISTRY.md:**
```markdown
## <Category> Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **<capability>** | <skill_name or N/A> | <mcp_tool or N/A> | `<tool_name>.py` | 1. <priority order> | <agent-list> | ✅ Active |
```

**2. Update CHANGELOG.md:**
```markdown
## [Date] - Tool Added

### Added
- `<tool_name>.py` - <brief description>
  - Purpose: <why created>
  - MCP Gap-Filler: <yes/no, explain if yes>
  - Used by: <agent-list>
  - Location: <team>/tools/<tool_name>.py
```

**3. Update Agent YAML (if tool used by agents):**
```yaml
---
name: Agent Name
tools:
  - <tool_name>  # Add to tools list
---
```

---

## 🔍 Part 3: Before Using an Existing Tool/Skill

### The Problem

**Common Mistake:**
```python
# Agent tries to use xlsx skill
use_skill("xlsx")
# Error: Skill not enabled (no clear message)
# Agent doesn't know to fallback to MCP
```

### ✅ Tool/Skill Usage Checklist

**Before using a tool/skill for the first time:**

#### Step 1: Verify Capability is Available

**For Skills:**
```bash
# Check skill is declared in agent YAML
grep "skills:" .claude/agents/<agent-name>.md -A 10
# Verify skill in list

# Check skill is enabled in settings
cat MARKETING_TEAM/.claude/settings.json | grep "<skill-name>"
# Verify "enabled": true
```

**For MCP Tools:**
```bash
# Check MCP server is configured
cat .mcp.json | grep "<server-name>" -A 10
# Verify server exists and has API key

# Check agent declares MCP tool in YAML
grep "tools:" .claude/agents/<agent-name>.md -A 10
# Verify mcp__<server>__<tool> in list
```

**For Custom Python Tools:**
```bash
# Check tool exists in tools/ folder
ls */tools/<tool-name>.py
# Verify file exists

# Check agent declares tool in YAML
grep "tools:" .claude/agents/<agent-name>.md -A 10
# Verify tool name in list
```

---

#### Step 2: Check TOOL_REGISTRY.md for Usage Examples

```markdown
**READ:** TOOL_REGISTRY.md entry for the tool/skill

**Find:**
1. Priority order (which to use first if multiple options)
2. Which agents use this tool (examples)
3. Status (Active/Deprecated/Not Enabled)
4. MCP alternatives (fallback options)
```

**Example:**
```markdown
# Looking up "PDF Creation" in TOOL_REGISTRY.md:

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **PDF Creation** | `pdf` (pypdf) | google-workspace MCP | ~~pdf_generator.py~~ | 1. Skill → 2. MCP | pdf-specialist | ✅ Active (skill), 🚫 Deprecated (tool) |

# Takeaway:
# - Use `pdf` skill as PRIMARY method
# - Fallback to Google Docs MCP → PDF export if skill fails
# - Do NOT use pdf_generator.py (deprecated)
```

---

#### Step 3: Read Tool/Skill Documentation

**For Skills:**
```bash
# Read skill documentation
cat .claude/skills/<skill-name>/SKILL.md

# Example: Read PDF skill docs
cat .claude/skills/pdf/SKILL.md
# Shows: pypdf library usage, PDF features, examples
```

**For Custom Tools:**
```bash
# Read tool docstring
head -50 <team>/tools/<tool-name>.py

# Example: Read upload_to_drive.py docstring
head -50 MARKETING_TEAM/tools/upload_to_drive.py
# Shows: Parameters, return values, usage examples
```

**For MCP Tools:**
```markdown
# MCP tools documented in TOOL_REGISTRY.md
# Or check MCP server documentation (if available)
```

---

#### Step 4: Verify Prerequisites (API Keys, Dependencies)

**For MCP Tools:**
```bash
# Check environment variables for API keys
env | grep "GOOGLE_API_KEY"
env | grep "OPENAI_API_KEY"
env | grep "PERPLEXITY_API_KEY"

# If missing:
# 1. Check .env file
# 2. See docs/getting-started/api-setup.md
# 3. Set environment variable
```

**For Custom Tools:**
```bash
# Check Python dependencies
pip list | grep <library-name>

# Example: Check if openai library installed
pip list | grep openai

# If missing:
# pip install <library-name>
```

**For Skills:**
```bash
# Most skills are self-contained
# No external API keys required (unless documented in SKILL.md)
```

---

#### Step 5: Follow Documented Priority Order

**Check agent instructions for priority:**

**Example (analyst.md - Excel generation):**
```markdown
## Data Export

**Priority:** MCP → Skill → Error

1. Try: mcp__google-workspace__create_spreadsheet (cloud-based, collaborative)
2. If MCP fails: Use xlsx skill (offline, advanced features)
3. If both fail: Raise clear error with troubleshooting
```

**Follow this order** - don't skip steps!

---

#### Step 6: Implement Fallback Logic

**Template:**
```python
# Priority 1: Try primary method
try:
    result = primary_method()
    # ✅ Success
    return result
except PrimaryMethodError as e:
    logger.warning(f"Primary method failed: {str(e)}, trying fallback")

    # Priority 2: Try fallback method
    try:
        result = fallback_method()
        # ✅ Success with fallback
        logger.info("Fallback method succeeded")
        return result
    except FallbackMethodError as e:
        logger.error(f"Fallback method failed: {str(e)}")

        # Priority 3: Raise clear error
        raise ToolError(
            "Cannot complete operation: "
            f"- Primary method ({primary_method.__name__}) failed: {primary_error} "
            f"- Fallback method ({fallback_method.__name__}) failed: {fallback_error} "
            "Troubleshooting: <troubleshooting steps>"
        )
```

---

## 📊 Summary: Quick Reference

### Before Declaring a Skill ✅
1. ☐ Verify skill exists (`.claude/skills/<skill-name>/`)
2. ☐ Verify skill enabled in settings.json
3. ☐ Check for MCP alternative (prefer MCP if cloud-based)
4. ☐ Document priority order in agent instructions

### Before Creating a Tool 🛠️
1. ☐ Check TOOL_REGISTRY.md for existing tools
2. ☐ Check .mcp.json for MCP servers
3. ☐ Check .claude/skills/ for skills
4. ☐ Check existing custom tools (find . -name "*.py" -path "*/tools/*")
5. ☐ Justify new tool creation (document MCP/skill gaps)
6. ☐ Create tool with comprehensive docstring + error handling
7. ☐ Update TOOL_REGISTRY.md, CHANGELOG.md, agent YAML

### Before Using a Tool/Skill 🔍
1. ☐ Verify capability available (YAML declaration + enabled status)
2. ☐ Check TOOL_REGISTRY.md for usage examples
3. ☐ Read tool/skill documentation
4. ☐ Verify prerequisites (API keys, dependencies)
5. ☐ Follow documented priority order
6. ☐ Implement fallback logic

---

## 🔗 Related Documentation

- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Complete tool/MCP/skill inventory (check FIRST)
- **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - Priority hierarchy (MCP → Skill → Tool → New)
- **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Agent-specific rules
- **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Quarterly audit process
- **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - Deprecation process

---

**Last Audit:** Not yet conducted (first audit scheduled for 2025-12-03)

---

**End of Checklist**
