# TOOL CLEANUP WORKFLOW - Deprecation Process

**Last Updated:** 2025-11-03
**Responsibility:** Security-auditor + CTO agents
**Process Duration:** 30 days (deprecation → archival)

---

## 🎯 Purpose

This document defines the **5-step deprecation workflow** for retiring tools/skills/MCPs when:
- MCP server now provides same functionality
- Tool is orphaned (zero agent declarations)
- Better alternative exists
- Tool is broken and not worth fixing

**Goal:** Clean deprecation with clear migration path and 30-day grace period

---

## 📋 When to Deprecate a Tool

### ✅ Deprecation Triggers

**1. MCP Server Replacement**
- MCP server now provides functionality that custom tool was filling
- Example: If Google Workspace MCP adds binary file upload support → deprecate `upload_to_drive.py`

**2. Tool Orphaned**
- Zero agents declare tool in YAML frontmatter
- Tool not referenced in any agent instructions
- Example: `pdf_generator.py` (no agents use it)

**3. Better Alternative Exists**
- Skill or MCP provides superior functionality
- Custom tool is redundant or inferior
- Example: `pdf` skill more comprehensive than `pdf_generator.py`

**4. Tool Broken**
- Tool no longer works (API changed, library deprecated)
- Not worth fixing (better alternatives exist)
- Example: API endpoint deprecated by provider

### ❌ When NOT to Deprecate

**1. MCP Gap-Fillers**
- Tool fills gap MCP servers can't handle
- Example: `upload_to_drive.py` (MCP can't handle binary files) → Keep
- Example: `send_email_with_attachment.py` (MCP can't send attachments) → Keep

**2. Unique Functionality**
- No MCP or skill alternative exists
- Tool provides specialized workflow
- Example: `sora_video.py` multi-clip stitching → Keep

**3. High Usage**
- Tool used by 3+ agents actively
- No migration path available
- Example: `upload_to_drive.py` used by 4+ agents → Keep (until MCP alternative exists)

---

## 🔄 5-Step Deprecation Process

### Step 1: Mark as Deprecated (Day 0)

#### 1.1 Add Deprecation Docstring to Tool File

**For Python Tools:**
```python
"""
⚠️ DEPRECATED as of YYYY-MM-DD
Deprecation Reason: [Explain why deprecated]
Migration Path: Use [alternative tool/skill/MCP] instead
Migration Guide: [Link to migration documentation or instructions]
Removal Date: YYYY-MM-DD (30 days from deprecation)
Archive Location: Will be moved to archive/tools/deprecated/

[Original docstring below for reference]
---
Tool Name - Original description
...
"""
```

**Example (`pdf_generator.py`):**
```python
"""
⚠️ DEPRECATED as of 2025-11-03
Deprecation Reason: Replaced by `pdf` skill (pypdf-based, more comprehensive)
                    Tool is orphaned (zero agents declare it in YAML frontmatter)
Migration Path: Use `pdf` skill instead (enabled in MARKETING_TEAM/.claude/settings.json)
Migration Guide: See AGENT_GOVERNANCE_RULES.md Section 2.1 for pdf skill usage
Removal Date: 2025-12-03 (30 days from deprecation)
Archive Location: archive/tools/deprecated/pdf_generator.py

[Original docstring]
PDF Generator - Create PDF documents from text content
...
"""
```

---

#### 1.2 Update TOOL_REGISTRY.md

**Mark tool as DEPRECATED with strikethrough:**

**Before:**
```markdown
| **PDF Creation** | `pdf` | google-workspace MCP | `pdf_generator.py` | 1. Skill → 2. Custom Tool | pdf-specialist | ✅ Active |
```

**After:**
```markdown
| **PDF Creation** | `pdf` | google-workspace MCP | ~~pdf_generator.py~~ | 1. Skill → 2. MCP | pdf-specialist | 🚫 DEPRECATED (2025-11-03) |
```

**Add deprecation note:**
```markdown
**Deprecated Tools:**
- 🚫 `pdf_generator.py` (MARKETING_TEAM/tools/) - Deprecated 2025-11-03
  - Reason: Replaced by `pdf` skill (more comprehensive), orphaned (zero declarations)
  - Migration: Use `pdf` skill instead
  - Removal: 2025-12-03 (moved to archive/tools/deprecated/)
```

---

#### 1.3 Update Agent YAML Frontmatter

**Remove from `tools:` section and add deprecation comment:**

**Before:**
```yaml
# pdf-specialist.md
tools:
  - pdf_generator  # ✅ Active
  - mcp__google-workspace__create_doc
  - upload_to_drive
```

**After:**
```yaml
# pdf-specialist.md
tools:
  # ❌ DEPRECATED 2025-11-03: pdf_generator (use pdf skill instead)
  - mcp__google-workspace__create_doc  # ✅ Active
  - upload_to_drive                     # ✅ Active
```

**If tool IS declared (not orphaned), update agent instructions:**
```markdown
## PDF Generation

### ~~Method: pdf_generator Tool (DEPRECATED)~~
**⚠️ DEPRECATED as of 2025-11-03**
This tool has been replaced by the `pdf` skill (more comprehensive).

**Migration:**
Use `pdf` skill instead:
```yaml
skill: pdf (pypdf library)
```

See TOOL_REGISTRY.md for pdf skill usage examples.
```

---

#### 1.4 Update CHANGELOG.md

**Add deprecation entry:**
```markdown
## [2025-11-03] - Tool Deprecated

### Deprecated
- `pdf_generator.py` (MARKETING_TEAM/tools/) - Replaced by `pdf` skill
  - Reason: Orphaned (zero agent declarations), `pdf` skill more comprehensive
  - Migration: Use `pdf` skill (enabled in MARKETING_TEAM/.claude/settings.json)
  - Removal Date: 2025-12-03 (30 days)
  - Archive Location: archive/tools/deprecated/pdf_generator.py
```

---

### Step 2: Announce Deprecation (Day 0-3)

#### 2.1 Notify Affected Agents (If Any)

**For orphaned tools (zero agents):**
- ✅ No notification needed (no agents using tool)
- ✅ Document deprecation in CHANGELOG.md

**For tools with agent declarations:**
- ✅ Update agent instructions with deprecation warning
- ✅ Provide migration guide in agent file
- ✅ Test migration path works (agents can use alternative)

---

#### 2.2 Document Migration Path

**Create migration guide (if complex):**

**Example:** `docs/migration/pdf_generator_to_pdf_skill.md`
```markdown
# Migration Guide: pdf_generator.py → pdf Skill

## Overview
The `pdf_generator.py` custom tool has been deprecated in favor of the `pdf` skill (pypdf-based).

## Why the Change?
- `pdf` skill provides more comprehensive PDF features (bookmarks, annotations, encryption)
- `pdf_generator.py` was orphaned (zero agents declared it)
- Skill is enabled in MARKETING_TEAM/.claude/settings.json

## Migration Steps

### Old Code (pdf_generator.py):
```python
from tools.pdf_generator import generate_pdf

pdf_file = generate_pdf(
    content="Whitepaper content",
    output_path="whitepaper.pdf"
)
```

### New Code (pdf skill):
```yaml
# Declare in agent YAML frontmatter
skills:
  - pdf
```

```python
# Use pdf skill in agent workflow
use_skill("pdf")
create_pdf_from_content(
    content="Whitepaper content",
    output_path="whitepaper.pdf"
)
```

## Additional Resources
- See .claude/skills/pdf/SKILL.md for pdf skill documentation
- See TOOL_REGISTRY.md for pdf skill usage examples
```

---

### Step 3: Monitor Migration (Day 0-30)

#### 3.1 Track Migration Progress

**For tools with declarations (not orphaned):**
```bash
# Check if agents still reference deprecated tool
grep -r "pdf_generator" .claude/agents/*.md

# Expected: Only deprecation notices, no active usage
```

**For orphaned tools:**
- ✅ No monitoring needed (already orphaned)

---

#### 3.2 Address Migration Issues

**If agents struggle with migration:**
- ✅ Update migration guide with troubleshooting
- ✅ Provide additional examples
- ✅ Extend deprecation period if necessary (document reason)

---

### Step 4: Archive Tool (Day 30)

#### 4.1 Move to Archive Folder

**Create archive folder if doesn't exist:**
```bash
mkdir -p archive/tools/deprecated/
```

**Move deprecated tool:**
```bash
# Move tool to archive
mv MARKETING_TEAM/tools/pdf_generator.py archive/tools/deprecated/pdf_generator.py

# Preserve deprecation docstring in archived file
```

**Update archived file with archival note:**
```python
"""
🗄️ ARCHIVED TOOL (Originally deprecated 2025-11-03, archived 2025-12-03)

This tool is preserved for historical reference only. DO NOT USE in production.

Original Deprecation Notice:
⚠️ DEPRECATED as of 2025-11-03
Deprecation Reason: Replaced by `pdf` skill (pypdf-based, more comprehensive)
                    Tool was orphaned (zero agents declared it)
Migration Path: Use `pdf` skill instead
...

[Original docstring below]
---
PDF Generator - Create PDF documents from text content
...
"""
```

---

#### 4.2 Update TOOL_REGISTRY.md

**Mark tool as ARCHIVED:**

**Before:**
```markdown
| **PDF Creation** | `pdf` | google-workspace MCP | ~~pdf_generator.py~~ | 1. Skill → 2. MCP | pdf-specialist | 🚫 DEPRECATED (2025-11-03) |
```

**After:**
```markdown
| **PDF Creation** | `pdf` | google-workspace MCP | N/A | 1. Skill → 2. MCP | pdf-specialist | ✅ Active |
```

**Move to "Archived Tools" appendix:**
```markdown
## 📦 Archived Tools (Historical Reference)

| Tool | Location | Deprecated | Archived | Replacement |
|------|----------|------------|----------|-------------|
| `pdf_generator.py` | archive/tools/deprecated/ | 2025-11-03 | 2025-12-03 | `pdf` skill |
```

---

#### 4.3 Update CHANGELOG.md

**Add archival entry:**
```markdown
## [2025-12-03] - Tool Archived

### Removed
- `pdf_generator.py` (MARKETING_TEAM/tools/) - Moved to archive/tools/deprecated/
  - Originally deprecated: 2025-11-03 (30 days ago)
  - Reason: Replaced by `pdf` skill, orphaned
  - Archived location: archive/tools/deprecated/pdf_generator.py
  - Migration complete: All agents using `pdf` skill
```

---

### Step 5: Verify Removal (Day 30+)

#### 5.1 Verify Tool Not in Active Use

**Check no agents reference tool:**
```bash
# Search for tool references in active agents
grep -r "pdf_generator" .claude/agents/*.md

# Expected: Zero results (all references removed in Step 2)
```

**Check no imports in active code:**
```bash
# Search for imports
grep -r "from tools.pdf_generator import" . --exclude-dir=archive

# Expected: Zero results
```

---

#### 5.2 Update Documentation

**Verify all documentation updated:**
- ☐ TOOL_REGISTRY.md: Tool removed from active list, added to archived list
- ☐ CHANGELOG.md: Deprecation and archival entries added
- ☐ Agent YAML: Tool removed from `tools:` section (if declared)
- ☐ Agent Instructions: Deprecation warnings removed, migration guides removed
- ☐ Migration guides: Marked as complete (if created)

---

#### 5.3 Final Audit Report

**Generate deprecation completion report:**

```markdown
# Tool Deprecation Completion Report

**Tool:** pdf_generator.py
**Deprecation Date:** 2025-11-03
**Archival Date:** 2025-12-03
**Duration:** 30 days

## Deprecation Summary

**Reason:** Replaced by `pdf` skill (more comprehensive), orphaned (zero declarations)

**Migration Path:** Use `pdf` skill instead (enabled in MARKETING_TEAM/.claude/settings.json)

**Affected Agents:** None (tool was orphaned)

## Verification Checklist

- ✅ Tool moved to archive/tools/deprecated/
- ✅ TOOL_REGISTRY.md updated (removed from active, added to archived)
- ✅ CHANGELOG.md updated (deprecation + archival entries)
- ✅ Agent YAML updated (zero declarations, nothing to update)
- ✅ Agent instructions updated (removed misleading section header)
- ✅ No active references found (grep search clean)
- ✅ Migration complete (all agents using `pdf` skill)

## Archival Location

`archive/tools/deprecated/pdf_generator.py`

File preserved for historical reference with deprecation notice in docstring.

## Post-Deprecation Metrics

- **Total tools:** 18 active (down from 19)
- **Orphaned tools:** 0 (down from 1)
- **Tool registry coverage:** 100% (18/18 tools documented)
- **Deprecation duration:** 30 days (standard)

## Lessons Learned

- Orphaned tool detection process effective (quarterly audit)
- Section header in pdf-specialist.md was misleading (removed)
- pdf skill is superior alternative (comprehensive pypdf features)
```

---

## 🔄 Deprecation Timeline Summary

| Day | Step | Actions |
|-----|------|---------|
| **Day 0** | Mark Deprecated | Add deprecation docstring, update registry, update CHANGELOG, remove from agent YAML |
| **Day 0-3** | Announce | Notify affected agents, create migration guide (if needed) |
| **Day 0-30** | Monitor | Track migration progress, address issues |
| **Day 30** | Archive | Move to archive/tools/deprecated/, update registry, update CHANGELOG |
| **Day 30+** | Verify | Confirm no active references, final audit report |

**Total Duration:** 30 days (deprecation warning → archival)

---

## 📊 Deprecation Metrics

**Track for governance health:**

| Metric | Target | Notes |
|--------|--------|-------|
| **Deprecation Duration** | 30 days | Standard grace period |
| **Migration Completion Rate** | 100% | All affected agents migrated before archival |
| **Orphaned Tool Detection** | Quarterly | Security-auditor audit |
| **Deprecation Backlog** | 0 tools | No deprecated tools pending archival >30 days |

---

## 🚨 Emergency Deprecation (Broken Tools)

**For tools that are critically broken (security issue, API shutdown):**

### Fast-Track Process (7 days instead of 30)

**Day 0:**
- ✅ Mark deprecated with CRITICAL severity
- ✅ Immediately remove from agent YAML (break agents if necessary)
- ✅ Create urgent migration guide
- ✅ Notify all agents (comment in agent files)

**Day 0-7:**
- ✅ Monitor migration aggressively
- ✅ Provide support for migration issues

**Day 7:**
- ✅ Archive tool (don't wait 30 days)
- ✅ Verify migration complete

**Document in CHANGELOG:**
```markdown
## [YYYY-MM-DD] - Emergency Tool Deprecation

### Removed (Emergency)
- `broken_tool.py` - CRITICAL security issue found
  - Reason: API endpoint deprecated by provider, exposes credentials
  - Migration: Use [alternative] immediately
  - Fast-tracked deprecation: 7 days instead of standard 30 days
  - Archived location: archive/tools/deprecated/broken_tool.py
```

---

## 📋 Deprecation Checklist Template

**Use for each deprecation:**

```markdown
# Deprecation Checklist: <tool_name>

## Step 1: Mark as Deprecated ☐
- ☐ Add deprecation docstring to tool file
- ☐ Update TOOL_REGISTRY.md (strikethrough, 🚫 DEPRECATED status)
- ☐ Remove from agent YAML frontmatter (if declared)
- ☐ Update agent instructions with deprecation warning (if declared)
- ☐ Update CHANGELOG.md with deprecation entry

## Step 2: Announce Deprecation ☐
- ☐ Notify affected agents (if any)
- ☐ Create migration guide (if complex)
- ☐ Test migration path works

## Step 3: Monitor Migration (30 days) ☐
- ☐ Track migration progress (grep for references)
- ☐ Address migration issues (update guide)
- ☐ Extend deprecation if necessary (document reason)

## Step 4: Archive Tool (Day 30) ☐
- ☐ Move to archive/tools/deprecated/
- ☐ Update archived file with archival note
- ☐ Update TOOL_REGISTRY.md (remove from active, add to archived)
- ☐ Update CHANGELOG.md with archival entry

## Step 5: Verify Removal ☐
- ☐ Verify no agent references (grep search)
- ☐ Verify no imports in active code
- ☐ Update all documentation
- ☐ Generate deprecation completion report
```

---

## 🔗 Related Documentation

- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Tool inventory and status tracking
- **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - When to deprecate vs keep tools
- **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Verify deprecation candidates
- **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Deprecation markers
- **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Quarterly deprecation candidate detection
- **[GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)** - Deprecation metrics tracking

---

**End of Workflow**
