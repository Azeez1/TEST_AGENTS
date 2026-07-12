# AGENT GOVERNANCE RULES

**Last Updated:** 2025-11-26
**Applies To:** All 73 agents across 8 teams (MARKETING, ENGINEERING, QA, PROPOSAL, FINANCIAL, SALES, VOICE, HEDGE_FUND — see [CLAUDE.md](CLAUDE.md), single source of truth for roster counts)
**Enforced By:** CTO agent + security-auditor (quarterly audits)

---

## 🎯 Purpose

This document establishes **agent-specific governance rules** for:
1. Skill declaration and usage
2. Tool creation and duplication
3. Priority order documentation
4. Configuration consistency
5. Deprecation processes

**Goal:** Ensure all agents follow consistent governance patterns to prevent skill/tool conflicts, duplication, and configuration errors

---

## 📋 Rule 1: Skill Declaration Rules

### 1.1 Verify Before Declaring ⭐ CRITICAL

**NEVER declare a skill in agent YAML unless:**
- ✅ Skill exists in `.claude/skills/` folder
- ✅ Skill is enabled in team `.claude/settings.json`
- ✅ You've tested skill actually works

### Common Mistakes

**❌ WRONG - Declaring disabled skills:**
```yaml
# pdf-specialist.md YAML frontmatter
skills:
  - pdf       # ✅ Enabled in MARKETING_TEAM settings
  - pptx      # ✅ Enabled in MARKETING_TEAM settings
  - docx      # ❌ NOT enabled! Will fail silently!
  - xlsx      # ❌ NOT enabled! Will fail silently!
```

**✅ CORRECT - Only declare enabled skills:**
```yaml
# pdf-specialist.md YAML frontmatter
skills:
  - pdf           # ✅ Enabled
  - pdf-filler    # ✅ Enabled
  - canvas-design # ✅ Enabled
  # NOT declaring docx/xlsx (not enabled in settings)
```

### 1.2 Configuration Status (MARKETING_TEAM)

**✅ ENABLED Skills (safe to declare):**
```
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
```

**❌ NOT ENABLED Skills (do not declare unless settings updated):**
```
- docx (Word document generation)
  Reason: Use google-workspace MCP for Google Docs instead (cloud-based, collaborative)
- xlsx (Excel operations)
  Reason: Use google-workspace MCP for Google Sheets instead (cloud-based, collaborative)
```

**If you need disabled skill:**
1. ✅ Request addition to `.claude/settings.json`
2. ✅ Test skill works after enabling
3. ✅ Update TOOL_REGISTRY.md with new status
4. ✅ THEN declare in agent YAML

### 1.3 Skill Verification Workflow

**Before adding skill to agent YAML:**

```bash
# Step 1: Check skill exists
ls .claude/skills/<skill-name>/
# Expected: SKILL.md and related files

# Step 2: Check skill enabled
cat MARKETING_TEAM/.claude/settings.json | grep "<skill-name>"
# Expected: "skill-name": { "enabled": true }

# Step 3: Check TOOL_REGISTRY.md for status
grep "<skill-name>" TOOL_REGISTRY.md
# Expected: ✅ Active or 🔧 Config Required
```

**Only declare skill if ALL checks pass!**

---

## 📋 Rule 2: Skill vs Tool Priority

### 2.1 When You Have BOTH Skill and MCP Tool

**If your agent can use BOTH skill and MCP tool for same function:**

**REQUIRED: Document priority in agent instructions**

#### Example 1: Excel/Spreadsheets (analyst.md)

**Scenario:** Agent has `xlsx` skill (if enabled) AND Google Sheets MCP

**Required Documentation:**
```markdown
## Data Export Workflow

### Excel/Spreadsheet Generation

**Method 1: Google Sheets (RECOMMENDED)**
```yaml
tool: mcp__google-workspace__create_spreadsheet
```
**Use Google Sheets MCP for:**
- Cloud-based sharing with stakeholders
- Real-time collaboration
- Direct Google Drive integration
- Cross-platform access

**Method 2: Local Excel (Offline Alternative)**
```yaml
skill: xlsx (NOT ENABLED - requires settings.json update)
```
**Use xlsx skill when:**
- Offline work required
- Advanced Excel features needed (macros, complex formulas)
- Local file storage preferred

**Current Status:** xlsx skill NOT enabled in settings.json

**Priority Order:** Try MCP first → If MCP fails, skill not available (notify user)

**Fallback Logic:**
1. Attempt Google Sheets MCP
2. If MCP fails (no API key, network error): Notify user xlsx skill not enabled
3. If xlsx skill were enabled: Fallback to xlsx skill for local Excel file
```

**Required Elements:**
- ✅ List BOTH methods (MCP and skill)
- ✅ Specify which is PRIMARY (Method 1/2)
- ✅ Explain WHEN to use each method (use cases)
- ✅ Note current status (skill enabled/not enabled)
- ✅ Document fallback logic (what happens if primary fails)

---

#### Example 2: PDF Creation (pdf-specialist.md)

**Scenario:** Agent has `pdf` skill AND Google Docs MCP

**Required Documentation:**
```markdown
## PDF Generation Workflow

### Method 1: pdf Skill (PRIMARY - ENABLED)
```yaml
skill: pdf (pypdf library)
```
**Use pdf skill for:**
- Multi-page whitepapers, reports, eBooks
- Complex PDF features (bookmarks, annotations, forms)
- Offline PDF generation (no API required)
- Comprehensive PDF manipulation

**Method 2: Google Docs MCP → PDF Export (FALLBACK)
```yaml
tool: mcp__google-workspace__create_doc + export_as_pdf
```
**Use Google Docs MCP for:**
- Collaborative document editing
- Cloud-based draft sharing
- Basic PDF export (limited formatting)

**Priority Order:** pdf skill (PRIMARY) → Google Docs MCP (FALLBACK)

**Rationale:** pdf skill provides comprehensive pypdf library features that Docs → PDF export cannot match. Use skill for production PDFs, MCP for basic drafts.
```

---

#### Example 3: Images (visual-designer.md)

**Scenario:** Agent has `canvas-design` skill AND GPT-4o MCP

**Required Documentation:**
```markdown
## Image Generation Methods

### Method 1: GPT-4o AI Images (PRIMARY for AI-generated content)
```yaml
tool: mcp__marketing-tools__generate_gpt4o_image
```
**Use GPT-4o MCP for:**
- AI-generated images (photos, illustrations, realistic scenes)
- Quick concept visualization
- Stock-photo-style imagery

### Method 2: canvas-design Skill (PRIMARY for design work)
```yaml
skill: canvas-design
```
**Use canvas-design skill for:**
- Design-focused graphics (typography, layout, brand consistency)
- Precise design control (50+ fonts, color palettes)
- Static posters, banners, infographics

**Decision Matrix:**
| Need | Use |
|------|-----|
| AI-generated photo/illustration | GPT-4o MCP |
| Design-focused graphic (typography, layout) | canvas-design skill |
| Quick concept visualization | GPT-4o MCP |
| Brand-consistent poster | canvas-design skill |

**Priority:** Depends on use case (AI vs Design), not hierarchical
```

**Key Insight:** Not all priorities are hierarchical! Sometimes tools are **complementary** rather than fallbacks.

---

### 2.2 Priority Order Templates

**Hierarchical Priority (MCP → Skill → Error):**
```markdown
**Priority Order:**
1. Try MCP tool (cloud-based, collaborative)
2. If MCP fails: Try skill (offline, advanced features)
3. If both fail: Raise clear error with troubleshooting steps
```

**Complementary Tools (Use Case Driven):**
```markdown
**Decision Matrix:**
| Use Case | Tool/Skill | Rationale |
|----------|------------|-----------|
| AI images | GPT-4o MCP | AI generation |
| Design graphics | canvas-design skill | Precise design control |
| Generative art | algorithmic-art skill | p5.js patterns |
```

**Skill-First Priority (Skill → MCP → Error):**
```markdown
**Priority Order:**
1. Try skill (comprehensive, offline capable)
2. If skill fails/not enabled: Try MCP (basic functionality)
3. If both fail: Raise clear error
```

**Choose template based on tool relationship!**

---

## 📋 Rule 3: Avoid Redundant Declarations

### 3.1 Canvas-Design Governance ⭐ MULTI-AGENT SKILL

**Problem:** 4 agents declare `canvas-design` skill - is this duplication?

**Answer:** NO - Multi-agent use is ACCEPTABLE if each agent has SPECIALIZED use case

**Current canvas-design Users:**

| Agent | Use Case | Status |
|-------|----------|--------|
| **visual-designer** | **PRIMARY OWNER** - All visual design tasks | ✅ PRIMARY |
| **pdf-specialist** | **SPECIALIZED** - One-page marketing materials (flyers, brochures) only | ✅ SPECIALIZED |
| **social-media-manager** | **SPECIALIZED** - Social graphics, infographics only | ✅ SPECIALIZED |
| **presentation-designer** | **RARE USE** - Poster-style slides (pptx is primary) | ⚠️ RARE USE |

**Required: Each agent MUST document when to use canvas-design vs other visual tools**

---

#### visual-designer.md (PRIMARY OWNER)

```markdown
## Visual Generation Methods

### canvas-design Skill (PRIMARY for Design Work)
**visual-designer is PRIMARY OWNER of canvas-design skill**

**Use canvas-design for:**
- All design-focused graphics (typography, layout, brand consistency)
- Posters, banners, infographics (where design quality > AI generation)
- Precise design control (50+ fonts, color palettes, professional layouts)

**When other agents should defer to visual-designer:**
- pdf-specialist: One-page materials only (visual-designer handles complex designs)
- social-media-manager: Basic social graphics (visual-designer handles brand campaigns)
- presentation-designer: Rare poster slides (visual-designer handles standalone posters)

**Ownership:** visual-designer coordinates canvas-design usage across all agents
```

---

#### pdf-specialist.md (SPECIALIZED USE)

```markdown
## Visual Content in PDFs

### canvas-design Skill (For One-Pagers Only)

**Use canvas-design when:**
- Creating one-page marketing materials (flyers, brochures, posters)
- Design quality is paramount
- Single-page PDF with visual focus

**When to defer to visual-designer:**
- Complex multi-element designs (defer to visual-designer, PRIMARY OWNER)
- Brand campaign visuals (defer to visual-designer)
- Multi-page visual layouts (use pdf skill instead)

**For multi-page PDFs:** Use `pdf` skill (pypdf) instead of canvas-design
**For fillable forms:** Use `pdf-filler` skill instead
```

---

#### social-media-manager.md (SPECIALIZED USE)

```markdown
## Social Media Graphics

### canvas-design Skill (For Social Graphics Only)

**Use canvas-design for:**
- Social media graphics (infographics, quote cards, announcement graphics)
- Posters for social sharing
- Design-focused visuals (not AI-generated)

**When to defer to visual-designer:**
- Brand campaign visuals (defer to visual-designer, PRIMARY OWNER)
- Complex designs with multiple elements
- High-stakes visual content (product launches, major announcements)

**For AI-generated images:** Defer to visual-designer (calls GPT-4o MCP)
**For Slack GIFs:** Use `slack-gif-creator` skill instead
```

---

#### presentation-designer.md (RARE USE)

```markdown
## Presentation Visual Methods

### Primary: pptx Skill
**Use pptx skill for ALL PowerPoint presentations** (html2pptx workflow)

### Rare Case: canvas-design Skill (Poster Slides Only)

**Use canvas-design ONLY when:**
- Single slide needs exceptional design quality (poster-style slide)
- Slide is standalone visual (not part of deck)

**For full decks:** ALWAYS use `pptx` skill (html2pptx), never canvas-design

**For complex visuals:** Defer to visual-designer (PRIMARY OWNER of canvas-design)
```

---

**Governance Rule:** Multi-agent skill use is ACCEPTABLE if:
1. ✅ Each agent documents SPECIALIZED use case
2. ✅ PRIMARY OWNER designated (coordinates usage)
3. ✅ Agents defer to primary owner for complex cases
4. ✅ No overlap in use cases (each agent has distinct purpose)

---

### 3.2 Filesystem Skill Usage (Utility-Level)

**Multiple agents declare `filesystem` skill - is this acceptable?**

**Answer:** YES - `filesystem` is utility-level (like Python's `os` module)

**Current filesystem Users:**
- lead-gen-agent (export leads to local files)
- seo-specialist (export keyword data to local files)
- analyst (export analysis reports to local files)

**Why this is NOT duplication:**
- filesystem is general-purpose utility
- Like declaring `os`, `json`, `csv` in Python
- Each agent uses for different domain (leads, keywords, analysis)

**No governance action required** - utility skills can be widely declared

---

## 📋 Rule 4: Tool/Skill Status Tracking

### 4.1 Deprecation Markers

**When skill/tool becomes deprecated, mark it in 3 places:**

#### 1. Tool Docstring (for Python tools)

```python
"""
⚠️ DEPRECATED as of 2025-11-03
Reason: Replaced by pdf skill (pypdf-based, more comprehensive)
Migration: Use `pdf` skill instead (enabled in MARKETING_TEAM settings.json)
Migration Guide: /docs/migration/pdf_generator_to_pdf_skill.md
Removal Date: 2025-12-03 (30 days from deprecation)

[Original docstring below for reference]
"""
```

#### 2. TOOL_REGISTRY.md

```markdown
| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **PDF Creation** | `pdf` (pypdf) | google-workspace MCP | ~~pdf_generator.py~~ | 1. Skill → 2. MCP | pdf-specialist | ✅ Active (skill), 🚫 DEPRECATED (tool) |
```

**Use strikethrough** `~~tool_name.py~~` and status 🚫 DEPRECATED

#### 3. Agent YAML Frontmatter

```yaml
# pdf-specialist.md
tools:
  # ✅ Use pdf skill instead (enabled in settings)
  # ❌ DEPRECATED: pdf_generator (removed 2025-11-03)
  - mcp__google-workspace__create_doc  # ✅ Active
  - upload_to_drive                     # ✅ Active
```

**Remove from `tools:` list** and add comment explaining deprecation

---

### 4.2 Orphaned Tool Removal

**Tools with ZERO agent declarations are orphaned:**

**Current Orphaned Tool:**
- `MARKETING_TEAM/tools/pdf_generator.py` - NO agents declare it (section header mentions it but workflow doesn't use it)

**Orphaned Tool Workflow:**
1. ✅ Mark as 🚫 DEPRECATED in TOOL_REGISTRY.md
2. ✅ Add deprecation docstring to tool file
3. ✅ Move to `archive/tools/deprecated/` after 30 days
4. ✅ Update CHANGELOG.md with deprecation

**Audit Frequency:** Quarterly (security-auditor checks for orphaned tools)

---

### 4.3 Status Indicators

**TOOL_REGISTRY.md Status Codes:**

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| ✅ Active | Tool/skill/MCP in use, working properly | None |
| 🔧 Config Required | Tool/skill exists but not enabled in settings | Enable in `.claude/settings.json` OR remove declarations |
| ⚠️ Audit Needed | Potential overlap or duplication | Review tool, compare with similar tools |
| 🚫 Deprecated | Replaced by better alternative | Remove from agent declarations, archive tool |
| ❌ Disabled | Intentionally not enabled (use MCP instead) | Document why disabled, remove agent declarations |

---

## 📋 Rule 5: Configuration Consistency

### 5.1 Settings.json Audit ⭐ CRITICAL

**Quarterly audit (security-auditor) checks:**

```markdown
## Settings.json Consistency Check

☐ All skills declared in agent YAML are enabled in settings.json
☐ All enabled skills have at least 1 agent using them
☐ Document skills (pdf, pptx, docx, xlsx) status clarified
☐ No agents declare disabled skills
☐ Skill enablement rationale documented in TOOL_REGISTRY.md
```

**Critical Issue Found:**
- ❌ `docx` and `xlsx` skills declared by agents but NOT enabled in MARKETING_TEAM settings
- ✅ **FIX PRIORITY: HIGH** - Breaks agents silently

---

### 5.2 Document Skills Policy

**Current Issue:** pdf/pptx/docx/xlsx configuration inconsistent

**Decision Required - 3 Options:**

**Option A: Enable All Document Skills**
```json
// MARKETING_TEAM/.claude/settings.json
{
  "skills": {
    ...
    "pdf": { "enabled": true },
    "pptx": { "enabled": true },
    "docx": { "enabled": true },  // ✅ Enable
    "xlsx": { "enabled": true }   // ✅ Enable
  }
}
```
- **Pros:** Agents can use skills as declared, offline capability
- **Cons:** May prefer MCP for docs/sheets (cloud-based, collaborative)

**Option B: Remove All Skill Declarations (MCP-Only)**
```yaml
# Remove skill declarations from all agents
# Use MCP exclusively (google-workspace for docs/sheets)
```
- **Pros:** Consistent MCP usage, cloud-based collaboration
- **Cons:** No offline capability, MCP dependency

**Option C: Selective Enable (RECOMMENDED)**
```json
// MARKETING_TEAM/.claude/settings.json
{
  "skills": {
    ...
    "pdf": { "enabled": true },      // ✅ Enable (pypdf comprehensive)
    "pptx": { "enabled": true },     // ✅ Enable (no MCP alternative)
    "docx": { "enabled": false },    // ❌ Use Google Docs MCP instead
    "xlsx": { "enabled": false }     // ❌ Use Google Sheets MCP instead
  }
}
```
- **Pros:** Best of both (skills where superior, MCP where collaborative)
- **Cons:** Need to update agent docs to clarify

**Rationale for Option C:**
- `pdf` skill: pypdf library more comprehensive than Docs → PDF export
- `pptx` skill: No MCP alternative for PowerPoint (html2pptx unique)
- `docx` skill: Google Docs MCP superior (cloud-based, collaborative, real-time editing)
- `xlsx` skill: Google Sheets MCP superior (cloud-based, collaborative, formulas)

**RECOMMENDED: Option C** (document in TOOL_REGISTRY.md)

---

### 5.3 Configuration Update Workflow

**When changing settings.json:**

1. ✅ Update `.claude/settings.json` with skill enablement
2. ✅ Test skill actually works (create test agent, try using skill)
3. ✅ Update TOOL_REGISTRY.md with new status (✅ Active or ❌ Disabled)
4. ✅ Update affected agent instructions (document new priority order)
5. ✅ Update CHANGELOG.md with configuration change
6. ✅ Notify all agents via comments in agent files (if applicable)

---

## 📋 Rule 6: Naming Conventions

### 6.1 Avoid Naming Collisions

**Problem:** Multiple teams have `router_tools.py` with different purposes

**Current Collision:**
- `MARKETING_TEAM/tools/router_tools.py` (social media formatters)
- `QA_TEAM/tools/router_tools.py` (QA workflow routing)

**Resolution:**
```bash
# Rename QA_TEAM tool to be unique
mv QA_TEAM/tools/router_tools.py QA_TEAM/tools/qa_router_tools.py
```

**Update references:**
- test-orchestrator.md YAML `tools:` section
- Any imports in QA_TEAM agent files

---

### 6.2 Tool Naming Standards

**Custom Python Tools:**
```
Pattern: action_noun.py
Examples:
  - generate_image.py (not image_generator.py)
  - upload_to_drive.py (not drive_uploader.py)
  - send_email.py (not email_sender.py)
```

**MCP Tools:**
```
Pattern: mcp__server__action
Examples:
  - mcp__playwright__navigate
  - mcp__google-workspace__create_doc
  - mcp__marketing-tools__generate_gpt4o_image
```

**Skills:**
```
Pattern: kebab-case
Examples:
  - canvas-design (not canvas_design)
  - flow-diagram (not flowDiagram)
  - slack-gif-creator (not SlackGifCreator)
```

---

### 6.3 Cross-Team Tool Naming

**When tool serves multiple teams:**

**✅ GOOD: Descriptive, team-agnostic names**
```
upload_to_drive.py (used by MARKETING, ENGINEERING, QA)
email_template_renderer.py (used by MARKETING, generic enough for others)
```

**❌ BAD: Team-specific names for shared tools**
```
marketing_image_gen.py (what if ENGINEERING wants to use it?)
qa_only_router.py (confusing if other teams need routing)
```

**Rule:** If tool used by 2+ teams, name should be team-agnostic

---

## 📋 Rule 7: Documentation Requirements

### 7.1 All Tools Must Have

**1. Comprehensive Docstring:**
```python
"""
Tool Name - Brief one-line description

Purpose:
    Detailed explanation of what this tool does and why it exists.

Parameters:
    param1 (type): Description
    param2 (type): Description

Returns:
    return_type: Description

Raises:
    ErrorType: When this occurs

Usage Examples:
    >>> from tools.tool_name import function
    >>> result = function(param="value")
    >>> print(result)

MCP Gap-Filler: (if applicable)
    This tool fills a gap where MCP <server> can't <limitation>.

Used By:
    - agent1 (use case)
    - agent2 (use case)
```

**2. TOOL_REGISTRY.md Entry:**
```markdown
| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **<capability>** | <skill or N/A> | <mcp or N/A> | `tool.py` | 1. <order> | agent-list | ✅ Active |
```

**3. CHANGELOG.md Entry:**
```markdown
## [2025-11-03] - Tool Added

### Added
- `tool_name.py` - Brief description
  - Purpose: Why created
  - Location: MARKETING_TEAM/tools/
  - Used by: agent1, agent2
```

**Audit:** Security-auditor checks quarterly that all tools have documentation

---

### 7.2 Agent Instructions Must Have

**For agents with dual capabilities (skill + MCP):**

**Required Documentation:**
```markdown
## <Task> Workflow

### Method 1: <Primary Tool> (RECOMMENDED)
**Use <primary> for:**
- Use case 1
- Use case 2

### Method 2: <Fallback Tool> (Alternative)
**Use <fallback> when:**
- Use case 1
- Use case 2

**Priority Order:** <primary> → <fallback> → Error

**Current Status:** <skill enabled/not enabled>

**Fallback Logic:**
1. Try <primary> (explain why primary)
2. If <primary> fails: Try <fallback> (explain fallback use)
3. If both fail: Raise error with troubleshooting
```

---

## 📊 Compliance Checklist

**For All Agents:**

☐ Only declare skills that are enabled in `.claude/settings.json`
☐ Document priority order for dual capabilities (skill + MCP)
☐ No orphaned tool declarations (tool exists and is active)
☐ Follow naming conventions (kebab-case for skills, snake_case for tools)
☐ Multi-agent skill use has documented specialized use cases
☐ Configuration matches declarations (no disabled skills declared)

**For All Tools:**

☐ Comprehensive docstring with usage examples
☐ Entry in TOOL_REGISTRY.md (category, priority, status)
☐ Entry in CHANGELOG.md (date created, purpose, agents using)
☐ Deprecated tools marked in all 3 places (docstring, registry, agent YAML)
☐ No naming collisions with other teams' tools

**Audit Frequency:** Quarterly (security-auditor runs compliance check)

---

## 🔗 Related Documentation

- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Complete inventory (check for existing tools/skills)
- **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - Priority hierarchy (MCP → Skill → Tool)
- **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Mandatory pre-creation checklist
- **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Quarterly audit workflow
- **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - Deprecation process
- **[GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)** - Success tracking

---

**Last Audit:** Not yet conducted (first audit scheduled for 2025-12-03)

---

**End of Governance Rules**
