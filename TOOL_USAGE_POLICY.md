# TOOL USAGE POLICY - Hierarchy of Authority

**Last Updated:** 2025-11-26
**Applies To:** All 73 agents across 8 teams (see [CLAUDE.md](CLAUDE.md) — single source of truth for roster counts)
**Enforced By:** CTO agent + security-auditor (quarterly audits)

---

## 🎯 Purpose

This policy establishes a **clear priority order** for tool/MCP/skill usage to prevent:
- ❌ Creating duplicate tools when functionality already exists
- ❌ Declaring skills that aren't enabled in `.claude/settings.json`
- ❌ Ambiguity about which tool to use when multiple options available
- ❌ MCP gap-fillers being created when MCP servers provide functionality

---

## 📊 The Canonical Priority Hierarchy

When executing ANY task, agents **MUST** follow this priority order:

```
1️⃣ MCP SERVERS (HIGHEST PRIORITY)
   ↓ (if MCP unavailable or insufficient)
2️⃣ SKILLS (SECOND PRIORITY)
   ↓ (if skill unavailable or MCP gap exists)
3️⃣ CUSTOM PYTHON TOOLS (THIRD PRIORITY)
   ↓ (if no existing solution)
4️⃣ CREATE NEW TOOL (LAST RESORT)
```

---

## 1️⃣ MCP SERVERS (HIGHEST PRIORITY)

**Rule:** Check MCP tools FIRST for all operations

### When to Use MCP

**ALWAYS use MCP when available for:**
- Email operations (Gmail)
- Document creation/editing (Google Docs, Sheets)
- File storage (Google Drive - text files only)
- Web research (Perplexity)
- Web scraping (Bright Data)
- Browser automation (Playwright)
- Workflow automation (n8n)
- Structured reasoning (sequential-thinking)

### Available MCP Servers

| Server | Tools | Use For |
|--------|-------|---------|
| **google-workspace** | `send_email`, `create_doc`, `create_spreadsheet`, `create_drive_file`, `list_drive_files`, `get_drive_file`, `search_emails`, `get_email`, `update_doc`, `modify_sheet_values`, `read_sheet_values` | Gmail, Google Docs, Google Sheets, Google Drive (text files) |
| **perplexity** | `perplexity_ask`, `perplexity_reason`, `perplexity_search` | Web research with citations, reasoning |
| **bright-data** | `search_engine` (Google/Bing/Yandex), `scrape_as_markdown`, `scrape_batch` | SERP scraping, web scraping (5K free/month) |
| **playwright** | `navigate`, `screenshot`, `click`, `fill`, `evaluate`, `get_visible_html`, `go_back`, `press_key`, `save_as_pdf` | Browser automation, web navigation, screenshots |
| **marketing-tools** | `generate_gpt4o_image`, `generate_sora_video` | AI image generation (GPT-4o), video generation (Sora) |
| **n8n-mcp** | n8n workflow execution | Workflow automation (400+ integrations) |
| **sequential-thinking** | `sequentialthinking` | Step-by-step problem solving, complex reasoning |

### Why MCP First?

✅ **Most Maintained** - External services kept up-to-date by providers
✅ **Best Error Handling** - MCP servers have robust error handling
✅ **Widest Compatibility** - Work across all agents without Python dependencies
✅ **Cloud-Based** - Google Workspace MCP enables collaboration, sharing
✅ **No Local Dependencies** - No need to install Python libraries

### Examples

**✅ CORRECT:**
```
Task: Send an email with meeting notes
Agent: "I'll use mcp__google-workspace__send_email to send the email"
```

**❌ WRONG:**
```
Task: Send an email with meeting notes
Agent: "I'll create a new email_sender.py tool to send emails"
Reason: MCP already provides this functionality!
```

---

## 2️⃣ SKILLS (SECOND PRIORITY)

**Rule:** Use skills when MCP unavailable OR when skill is purpose-built for specialized workflows

### When to Use Skills

**Use skills when:**
- ✅ No MCP alternative exists (e.g., PowerPoint → `pptx` skill)
- ✅ Skill provides specialized workflow (e.g., `pdf-filler` for fillable forms)
- ✅ Design-focused work (e.g., `canvas-design` with 50+ fonts)
- ✅ Offline capability needed (no internet connection)
- ✅ Skill explicitly requested by user (e.g., "use canvas-design skill")

### Available Skills by Category

**Visual Skills (5):**
- `algorithmic-art` - p5.js generative art (no MCP alternative)
- `canvas-design` - Professional design with 50+ fonts (design-focused, not AI-generated)
- `slack-gif-creator` - Slack-optimized animated GIFs (size-constrained)
- `theme-factory` - 10 pre-set themes for artifacts (design system)
- `flow-diagram` - Mermaid diagrams with interactive HTML (system architecture)

**Development Skills (3):**
- `artifacts-builder` - React + shadcn/ui (elaborate multi-component artifacts)
- `mcp-builder` - Create MCP servers (no MCP for creating MCPs!)
- `skill-creator` - Create new skills (meta-skill)

**Content Skills (3):**
- `internal-comms` - Internal communications templates (status reports, FAQs, newsletters)
- `brand-guidelines` - Anthropic brand colors/typography (design standards)
- `pdf-filler` - PDF form filling (specialized forms workflow)

**Document Skills (4 - Configuration Required):**
- `pdf` - PDF creation via pypdf (✅ ENABLED in MARKETING_TEAM)
- `pptx` - PowerPoint via html2pptx (✅ ENABLED in MARKETING_TEAM)
- `docx` - Word documents (❌ NOT enabled - use Google Docs MCP)
- `xlsx` - Excel operations (❌ NOT enabled - use Google Sheets MCP)

**Integration Skills (3):**
- `filesystem` - File read/write/list/delete (local file operations)
- `figma` - Figma design extraction via API (specialized integration)
- `context7` - Context management (utility)

### Skill Advantages Over MCP

| Skill | Advantage Over MCP |
|-------|--------------------|
| `pptx` | html2pptx workflow optimized for presentations (no MCP alternative) |
| `pdf` | pypdf library comprehensive features (MCP only has Docs → PDF export) |
| `canvas-design` | 50+ fonts, precise design control (MCP GPT-4o is AI-generated, not design-focused) |
| `flow-diagram` | Mermaid expertise with interactive HTML (specialized for architecture diagrams) |
| `filesystem` | Local file operations (MCP Google Drive is cloud-only) |

### ⚠️ CRITICAL: Verify Skill is Enabled

**Before declaring a skill in agent YAML:**
1. ✅ Check `.claude/skills/` folder - does skill exist?
2. ✅ Check team `.claude/settings.json` - is skill enabled?
3. ✅ Test skill works before adding to agent definition

**Common Mistake:**
```yaml
# ❌ WRONG - xlsx skill NOT enabled in MARKETING_TEAM settings
skills:
  - xlsx
```

```yaml
# ✅ CORRECT - Only declare enabled skills
skills:
  - pdf        # ✅ Enabled
  - pdf-filler # ✅ Enabled
```

**Current Status (MARKETING_TEAM/.claude/settings.json):**
- ✅ **ENABLED:** algorithmic-art, artifacts-builder, brand-guidelines, canvas-design, flow-diagram, internal-comms, mcp-builder, pdf, pdf-filler, pptx, skill-creator, slack-gif-creator, theme-factory, filesystem, figma, context7
- ❌ **NOT ENABLED:** docx, xlsx (use Google Workspace MCP instead)

### Examples

**✅ CORRECT:**
```
Task: Create a PowerPoint presentation
Agent: "I'll use the pptx skill (html2pptx workflow) to create the presentation"
Reason: No MCP alternative, skill purpose-built for PowerPoint
```

**✅ CORRECT:**
```
Task: Create a system architecture diagram
Agent: "I'll use the flow-diagram skill to create an interactive Mermaid diagram"
Reason: Skill specialized for diagrams, provides interactive HTML output
```

**❌ WRONG:**
```
Task: Create an Excel spreadsheet
Agent: "I'll use the xlsx skill to create the spreadsheet"
Reason: xlsx skill NOT enabled! Should use mcp__google-workspace__create_spreadsheet
```

---

## 3️⃣ CUSTOM PYTHON TOOLS (THIRD PRIORITY)

**Rule:** Use custom tools ONLY for MCP gap-fillers (when MCP has technical limitations)

### When Custom Tools are Justified

**MCP Gap-Fillers (ACCEPTABLE):**
- ✅ Binary file uploads (MCP Google Workspace can't handle) → `upload_to_drive.py`
- ✅ Email attachments (MCP Google Workspace limitation) → `send_email_with_attachment.py`
- ✅ gpt-image-1 model API (unique OpenAI API) → `openai_gpt4o_image.py`
- ✅ Sora video generation (unique API) → `sora_video.py`
- ✅ Multi-clip video stitching (specialized workflow) → `sora_video.py`
- ✅ Custom Perplexity research workflows (HYBRID with MCP fallback) → `conduct_research()`, `quick_research()`, `strategic_analysis()`

### Current Custom Tools (19 total)

**Visual Tools (2):**
- `openai_gpt4o_image.py` - GPT-4o image generation (wrapped by marketing-tools MCP, but also callable directly)
- `sora_video.py` - Sora video generation + multi-clip stitching (MCP can't handle multi-clip workflows)

**Integration Tools (4):**
- `upload_to_drive.py` - Binary file uploads (MCP gap-filler)
- `send_email_with_attachment.py` - Gmail with attachments (MCP gap-filler)
- `email_template_renderer.py` - Branded HTML email templates (4 themes)
- `mcp_server.py` - Bridges Python tools to MCP protocol

**Research Tools (3 - HYBRID Strategy):**
- `conduct_research()` - Comprehensive research (PRIMARY, MCP fallback)
- `quick_research()` - Fast facts (PRIMARY, MCP fallback)
- `strategic_analysis()` - Strategic reasoning (PRIMARY, MCP fallback)

**Documents (1):**
- ~~pdf_generator.py~~ - 🚫 DEPRECATED (orphaned, replaced by `pdf` skill)

**Content (2):**
- `router_tools.py` - Social media platform formatters (Twitter, LinkedIn)
- `platform_formatters.py` - Social media formatting utilities (⚠️ Audit needed - may overlap with router_tools)

**Testing (3):**
- `test_generator.py` - pytest test generation
- `code_scanner.py` - AST analysis for test opportunities
- `coverage_analyzer.py` - pytest-cov analysis

**Orchestration (4):**
- `engineering_coordinator_tools.py` - CTO coordination (658 lines - critical)
- `qa_router_tools.py` - QA workflow routing (renamed from router_tools.py)
- `validate_agents.py` - Agent YAML schema validation
- `update_agent_tools.py` - Bulk agent config updates

### Examples

**✅ CORRECT (MCP Gap-Filler):**
```
Task: Upload a PDF file to Google Drive
Agent: "I'll use upload_to_drive.py because Google Workspace MCP can't handle binary files"
Reason: Technical limitation of MCP (binary file uploads)
```

**✅ CORRECT (Specialized Workflow):**
```
Task: Create a 30-second product video from 3 separate clips
Agent: "I'll use sora_video.py with multi-clip stitching to combine the clips"
Reason: MCP can generate single clips but can't stitch multiple clips
```

**❌ WRONG (MCP Already Provides This):**
```
Task: Create a Google Doc
Agent: "I'll create a custom create_doc.py tool"
Reason: WRONG! mcp__google-workspace__create_doc already exists!
```

---

## 4️⃣ CREATE NEW TOOL (LAST RESORT)

**Rule:** Only create new tools if #1-3 don't cover the need

### Pre-Creation Checklist

**Before creating ANY new tool, you MUST:**

1. ☐ Read [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Check complete inventory
2. ☐ Check `.mcp.json` - Verify no MCP server provides this functionality
3. ☐ Check `.claude/skills/` - Verify no skill provides this functionality
4. ☐ Check `tools/` folders - Verify no custom tool already exists
5. ☐ Justify new tool creation:
   - Why is MCP insufficient? (e.g., "MCP can't handle binary files")
   - Why is skill insufficient? (e.g., "No skill for this API")
   - Why is custom tool insufficient? (e.g., "No existing tool for this workflow")
6. ☐ Document in TOOL_REGISTRY.md after creation
7. ☐ Update CHANGELOG.md with new tool details

### Tool Naming Conventions

**Custom Tools:**
```
action_noun.py (e.g., generate_image.py, upload_to_drive.py, send_email.py)
```

**MCP Tools:**
```
mcp__server__action (e.g., mcp__playwright__navigate, mcp__google-workspace__create_doc)
```

### Documentation Requirements

**All new tools MUST have:**
1. ✅ Comprehensive docstring with:
   - Purpose and use cases
   - Parameters and return values
   - Usage examples
   - Error handling details
2. ✅ Entry in TOOL_REGISTRY.md with:
   - Tool name and location
   - Purpose and capabilities
   - Which agents use it
   - Priority order (vs MCP/skills)
   - Status (Active/Deprecated)
3. ✅ Agent YAML declaration (if used by agents)
4. ✅ CHANGELOG.md entry (date created, why created, who uses it)

### Examples

**✅ CORRECT (Justified New Tool):**
```
Task: Integrate with a proprietary company API (no MCP, no skill, no existing tool)
Agent:
1. Checked TOOL_REGISTRY.md - no existing tool
2. Checked .mcp.json - no MCP server for this API
3. Checked .claude/skills/ - no skill for this API
4. Created proprietary_api_client.py with comprehensive docstring
5. Updated TOOL_REGISTRY.md
6. Updated CHANGELOG.md
```

**❌ WRONG (Didn't Check Registry):**
```
Task: Send an email with an attachment
Agent: "I'll create a new email_with_attachment.py tool"
Reason: WRONG! send_email_with_attachment.py already exists in tools/!
```

---

## 🔄 Fallback Strategy

When your primary tool fails, follow this logic:

### Example 1: Excel Generation (Analyst Agent)

**Priority:** MCP → Skill → Error

```python
# Priority 1: Google Sheets MCP (cloud-based, collaborative)
try:
    spreadsheet_id = mcp__google-workspace__create_spreadsheet(
        title="Campaign Analysis",
        data=analysis_data
    )
    # ✅ Success - Use Google Sheets
except MCPError as e:
    # Priority 2: xlsx skill (offline, local file)
    try:
        use_skill("xlsx")
        create_excel_file("campaign_analysis.xlsx", analysis_data)
        # ⚠️ Note: xlsx skill NOT enabled in settings - this will fail
    except SkillNotEnabled:
        # Priority 3: Raise clear error with troubleshooting
        raise ToolError(
            "Cannot create spreadsheet: "
            "- Google Workspace MCP unavailable (check API key) "
            "- xlsx skill not enabled in .claude/settings.json "
            "Recommendation: Fix MCP credentials or enable xlsx skill"
        )
```

**Rationale:** MCP is primary (cloud-based, collaborative), skill is fallback (offline, advanced features)

---

### Example 2: PDF Generation (PDF Specialist)

**Priority:** Skill → MCP → Error

```python
# Priority 1: pdf skill (comprehensive, offline capable)
try:
    use_skill("pdf")
    create_pdf_from_content(content, "whitepaper.pdf")
    # ✅ Success - Full pypdf capabilities
except SkillNotEnabled:
    # Priority 2: Google Docs MCP → Export as PDF
    try:
        doc_id = mcp__google-workspace__create_doc(
            title="Whitepaper",
            content=content
        )
        mcp__google-workspace__export_as_pdf(doc_id, "whitepaper.pdf")
        # ⚠️ Limited formatting, but functional
    except MCPError as e:
        # Priority 3: Raise clear error
        raise ToolError(
            "Cannot create PDF: "
            "- pdf skill not enabled (check .claude/settings.json) "
            "- Google Workspace MCP unavailable (check API key) "
            "Recommendation: Enable pdf skill for comprehensive PDF creation"
        )
```

**Rationale:** Skill is primary (pypdf comprehensive, offline), MCP is fallback (basic PDF export from Docs)

---

### Example 3: Image Generation (Visual Designer)

**Priority:** MCP → Skill → Custom Tool → Error

```python
# Priority 1: GPT-4o via marketing-tools MCP (primary AI image generation)
try:
    image_url = mcp__marketing_tools__generate_gpt4o_image(
        prompt="Modern tech startup office with diverse team",
        size="1024x1024"
    )
    # ✅ Success - AI-generated image
except MCPError as e:
    # Priority 2: canvas-design skill (design-focused alternative)
    try:
        use_skill("canvas-design")
        create_designed_image(
            layout="poster",
            text="Tech Startup",
            fonts=["Helvetica Neue", "Roboto"],
            output="startup_poster.png"
        )
        # ✅ Success - Design-focused (not AI-generated)
    except SkillNotEnabled:
        # Priority 3: Custom tool (direct API fallback)
        try:
            from tools.openai_gpt4o_image import generate_image
            image_url = generate_image(
                prompt="Modern tech startup office",
                size="1024x1024"
            )
            # ✅ Success - Direct API call
        except Exception as e:
            # Priority 4: Raise clear error
            raise ToolError(
                "Cannot generate image: "
                "- marketing-tools MCP unavailable (check MCP server) "
                "- canvas-design skill not enabled (check settings.json) "
                "- openai_gpt4o_image.py failed (check OPENAI_API_KEY) "
                f"Original error: {str(e)}"
            )
```

**Rationale:** MCP is primary (AI generation), skill is alternative (design-focused), custom tool is fallback (direct API)

---

### When NOT to Fallback

**Don't fallback if:**
- ❌ User explicitly requested specific tool/skill (e.g., "use canvas-design skill")
- ❌ Output format incompatible (don't fallback PowerPoint → PDF)
- ❌ Quality/features degrade significantly (e.g., Google Docs PDF export vs pypdf)
- ❌ Fallback would violate user requirements (e.g., "must be offline" → can't use MCP)

---

## 🎨 Special Cases: Skill vs Tool Decision Matrix

### PowerPoint Generation (Presentation Designer)

| Method | Priority | When to Use |
|--------|----------|-------------|
| `pptx` skill | 1 (PRIMARY) | All PowerPoint generation (no MCP alternative) |
| `theme-factory` skill | 2 (ALTERNATIVE) | Themed HTML artifacts (not PowerPoint format) |
| `artifacts-builder` skill | 3 (ALTERNATIVE) | Interactive React presentations (not PowerPoint format) |

**Rule:** pptx skill is ONLY method for actual PowerPoint (.pptx) files

---

### Excel/Spreadsheets (Analyst, Lead Gen, SEO)

| Method | Priority | When to Use |
|--------|----------|-------------|
| Google Sheets MCP | 1 (PRIMARY) | Cloud-based, collaborative, easy sharing |
| `xlsx` skill | 2 (FALLBACK) | Offline, advanced Excel features (macros, pivot tables) |

**Note:** xlsx skill currently NOT enabled in MARKETING_TEAM settings → Use MCP exclusively

---

### Word/Docs (Copywriter)

| Method | Priority | When to Use |
|--------|----------|-------------|
| Google Docs MCP | 1 (PRIMARY) | Cloud-based, collaborative, easy commenting |
| `docx` skill | 2 (FALLBACK) | Offline, local file storage |

**Note:** docx skill currently NOT enabled in MARKETING_TEAM settings → Use MCP exclusively

---

### PDF Creation (PDF Specialist)

| Method | Priority | When to Use |
|--------|----------|-------------|
| `pdf` skill | 1 (PRIMARY) | Whitepapers, reports, eBooks (comprehensive pypdf features) |
| `pdf-filler` skill | 1 (SPECIALIZED) | Fillable forms (form fields, checkboxes, signatures) |
| `canvas-design` skill | 1 (SPECIALIZED) | One-page marketing materials (flyers, brochures, posters) |
| Google Docs MCP → PDF export | 2 (FALLBACK) | Basic PDF export if skills unavailable |

**Rule:** Use `pdf` skill for multi-page documents, `pdf-filler` for forms, `canvas-design` for single-page design-focused materials

---

### Images (Visual Designer)

| Method | Priority | When to Use |
|--------|----------|-------------|
| GPT-4o MCP | 1 (PRIMARY) | AI-generated images (photos, illustrations, realistic scenes) |
| `canvas-design` skill | 2 (DESIGN-FOCUSED) | Design-focused graphics (typography, layout, brand consistency) |
| `algorithmic-art` skill | 3 (GENERATIVE) | Generative art (flow fields, particle systems, abstract) |
| `slack-gif-creator` skill | 4 (SPECIALIZED) | Slack-optimized animated GIFs |
| `openai_gpt4o_image.py` | 5 (FALLBACK) | Direct API call if MCP unavailable |

**Rule:** AI images → MCP, Design work → canvas-design, Generative art → algorithmic-art, Slack GIFs → slack-gif-creator

---

## 📋 Governance Enforcement

### CTO Responsibilities

**Before delegating tool creation:**
1. ☐ Check TOOL_REGISTRY.md for existing tools
2. ☐ Verify skill is enabled in `.claude/settings.json` if declaring
3. ☐ Enforce priority hierarchy (MCP → Skill → Custom → New)
4. ☐ Require written justification for new tools
5. ☐ Ensure tool documented in registry after creation

### Security Auditor Responsibilities

**Quarterly Tool Governance Audit (every 3 months):**
1. ☐ Configuration mismatch detection (skills declared but not enabled)
2. ☐ Priority order documentation audit (agents with dual capabilities)
3. ☐ Orphaned tool detection (tools with zero agent declarations)
4. ☐ Duplication detection (similar names, overlapping functions)
5. ☐ Usage analysis (orphaned tools, multi-agent tools)
6. ☐ Deprecation candidates (MCP replacements, unused tools)
7. ☐ Documentation quality (docstrings, examples, registry entries)

**See:** [TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md) for complete audit workflow

---

## 📊 Success Metrics

**Track quarterly:**
- **MCP Adoption Rate:** % of operations using MCP vs custom tools (target: >60%)
- **Tool Duplication Rate:** # of duplicate tools / total tools (target: <5%)
- **Skill Declaration Accuracy:** % of agents with correct skill declarations (target: 100%)
- **Priority Documentation Coverage:** % of dual-capability agents with documented priority (target: 100%)

**See:** [GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md) for complete metrics

---

## 🔗 Related Documentation

- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Complete tool/MCP/skill inventory
- **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Mandatory checks before tool/skill creation
- **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Agent-specific rules
- **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Quarterly audit workflow
- **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - Deprecation process
- **[GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)** - Success tracking

---

**Last Audit:** Not yet conducted (first audit scheduled for 2025-12-03)
**Next Review:** 2026-02-03

---

**End of Policy**
