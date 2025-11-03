# TOOL REGISTRY - Single Source of Truth

**Last Updated:** 2025-11-03
**Total Inventory:** 19 custom tools + 7 MCP servers + 18 skills
**Maintained by:** Engineering Team (security-auditor + technical-writer)

---

## 📋 Overview

This registry documents ALL tools, MCP servers, and skills available to the 37 agents across 4 teams. Before creating a new tool, **CHECK THIS REGISTRY FIRST**.

**Priority Hierarchy:** MCP Servers → Skills → Custom Tools → Create New Tool (last resort)

---

## 🎨 Visual & Design Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **AI Image Generation** | N/A | `mcp__marketing-tools__generate_gpt4o_image` | `openai_gpt4o_image.py` | 1. MCP → 2. Custom Tool | visual-designer | ✅ Active |
| **Design-Focused Graphics** | `canvas-design` (50+ fonts, PNG/PDF) | N/A | N/A | 1. Skill only | visual-designer (PRIMARY), pdf-specialist, social-media-manager, presentation-designer | ✅ Active |
| **Algorithmic Art** | `algorithmic-art` (p5.js, generative) | N/A | N/A | 1. Skill only | visual-designer, social-media-manager | ✅ Active |
| **Video Generation** | N/A | `mcp__marketing-tools__generate_sora_video` | `sora_video.py` | 1. MCP → 2. Custom Tool (multi-clip stitching) | video-producer | ✅ Active |
| **Slack GIFs** | `slack-gif-creator` (animated GIFs) | N/A | N/A | 1. Skill only | social-media-manager | ✅ Active |
| **System Diagrams** | `flow-diagram` (Mermaid, interactive HTML) | N/A | N/A | 1. Skill only | system-architect, technical-writer | ✅ Active |
| **Themed Artifacts** | `theme-factory` (10 pre-set themes) | N/A | N/A | 1. Skill only | presentation-designer, landing-page-specialist | ✅ Active |

**Usage Notes:**
- **canvas-design ownership:** visual-designer is PRIMARY owner; others use for specialized cases only
- **Video stitching:** sora_video.py custom tool handles multi-clip workflows MCP can't do

---

## 📄 Document Generation Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **PDF Creation** | `pdf` (pypdf, comprehensive) | `mcp__google-workspace__create_doc` → export | ~~pdf_generator.py~~ | 1. Skill → 2. MCP fallback | pdf-specialist | ✅ Active (skill), 🚫 Deprecated (tool) |
| **PDF Form Filling** | `pdf-filler` (fillable forms) | N/A | N/A | 1. Skill only | pdf-specialist | ✅ Active |
| **PowerPoint** | `pptx` (html2pptx, PptxGenJS) | N/A | N/A | 1. Skill only | presentation-designer | ✅ Active |
| **Excel/Spreadsheets** | `xlsx` | `mcp__google-workspace__create_spreadsheet`, `modify_sheet_values`, `read_sheet_values` | N/A | 1. MCP → 2. Skill fallback | analyst, lead-gen-agent, seo-specialist | 🔧 MCP Active, Skill NOT enabled |
| **Word/Docs** | `docx` | `mcp__google-workspace__create_doc`, `update_doc` | N/A | 1. MCP → 2. Skill fallback | copywriter, analyst | 🔧 MCP Active, Skill NOT enabled |

**Rationale for Priority:**
- **PDF:** Skill is PRIMARY (pypdf more comprehensive, offline capable) → MCP fallback for cloud collaboration
- **PowerPoint:** Skill ONLY (no MCP alternative, html2pptx workflow superior)
- **Excel:** MCP PRIMARY (cloud-based, collaborative, Google Sheets) → Skill fallback for offline/advanced features
- **Word:** MCP PRIMARY (cloud-based, collaborative, Google Docs) → Skill fallback for offline

**Configuration Status:**
- ✅ `pdf` skill: ENABLED in MARKETING_TEAM/.claude/settings.json
- ✅ `pptx` skill: ENABLED in MARKETING_TEAM/.claude/settings.json
- 🔧 `xlsx` skill: NOT enabled (use MCP exclusively unless advanced Excel features needed)
- 🔧 `docx` skill: NOT enabled (use MCP exclusively unless offline required)

**Deprecated Tools:**
- 🚫 `pdf_generator.py` - Orphaned (zero agent declarations), replaced by `pdf` skill. Archived 2025-11-03.

---

## 🔗 Integration & Communication Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **Gmail (Text Only)** | N/A | `mcp__google-workspace__send_email`, `search_emails`, `get_email` | N/A | 1. MCP only | gmail-agent, email-specialist | ✅ Active |
| **Gmail (With Attachments)** | N/A | N/A (MCP limitation) | `send_email_with_attachment.py` | 1. Custom Tool only | gmail-agent | ✅ Active (MCP gap-filler) |
| **HTML Email Templates** | N/A | N/A | `email_template_renderer.py` (4 branded themes) | 1. Custom Tool only | email-specialist | ✅ Active |
| **Google Drive (Text Files)** | N/A | `mcp__google-workspace__create_drive_file`, `list_drive_files`, `get_drive_file` | N/A | 1. MCP only | All agents | ✅ Active |
| **Google Drive (Binary Files)** | N/A | N/A (MCP limitation) | `upload_to_drive.py` | 1. Custom Tool only | pdf-specialist, presentation-designer, visual-designer, video-producer | ✅ Active (MCP gap-filler) |
| **File Operations** | `filesystem` (read, write, list, delete) | N/A | N/A | 1. Skill only | lead-gen-agent, seo-specialist, analyst | ✅ Active |
| **Figma Design Extraction** | `figma` (Figma API integration) | N/A | N/A | 1. Skill only | USER_STORY_AGENT (via Playwright MCP) | ✅ Active |

**MCP Gap-Fillers (Justified Duplication):**
- **Binary Uploads:** Google Workspace MCP can't upload binary files (PDFs, images, videos) → `upload_to_drive.py` required
- **Email Attachments:** Google Workspace MCP can't send attachments → `send_email_with_attachment.py` required

---

## 🔍 Research & Data Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **Comprehensive Research** | N/A | `mcp__perplexity__perplexity_ask`, `perplexity_reason`, `perplexity_search` | `conduct_research()` | 1. Custom Tool (PRIMARY) → 2. MCP (fallback) | research-agent | ✅ Active (HYBRID strategy) |
| **Quick Research** | N/A | `mcp__perplexity__perplexity_ask` | `quick_research()` | 1. Custom Tool → 2. MCP fallback | research-agent | ✅ Active (HYBRID) |
| **Strategic Analysis** | N/A | `mcp__perplexity__perplexity_reason` | `strategic_analysis()` | 1. Custom Tool → 2. MCP fallback | research-agent | ✅ Active (HYBRID) |
| **SERP Scraping** | N/A | `mcp__bright-data__search_engine` (Google, Bing, Yandex) | N/A | 1. MCP only | seo-specialist, lead-gen-agent, analyst | ✅ Active (5K free/month) |
| **Web Scraping** | N/A | `mcp__bright-data__scrape_as_markdown`, `scrape_batch` | N/A | 1. MCP only | research-agent, lead-gen-agent, seo-specialist | ✅ Active |
| **Browser Automation** | N/A | `mcp__playwright__playwright_navigate`, `screenshot`, `click`, `fill`, `evaluate` | N/A | 1. MCP only | USER_STORY_AGENT, seo-specialist, research-agent | ✅ Active |

**HYBRID Strategy Rationale (Perplexity):**
- **Custom tools** provide comprehensive research workflows with multi-step logic
- **MCP fallback** provides redundancy if custom tools fail
- **Documented in:** research-agent.md (lines 50-75)

---

## 📱 Content & Social Media Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **Platform Formatting** | N/A | N/A | `router_tools.py` (Twitter, LinkedIn formatters) | 1. Custom Tool only | router-agent, social-media-manager | ✅ Active |
| **Social Media Formatting** | N/A | N/A | `platform_formatters.py` | 1. Custom Tool only | social-media-manager | ⚠️ Audit needed (potential overlap with router_tools) |
| **Internal Communications** | `internal-comms` (status reports, FAQs, newsletters) | N/A | N/A | 1. Skill only | copywriter, analyst | ✅ Active |
| **Brand Guidelines** | `brand-guidelines` (Anthropic brand colors/typography) | N/A | N/A | 1. Skill only | All MARKETING_TEAM agents | ✅ Active |

**Audit Action Required:**
- ⚠️ `platform_formatters.py` vs `router_tools.py` - Verify no duplicate functionality (MEDIUM priority)

---

## 🧪 Testing & QA Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **Test Generation** | N/A | N/A | `test_generator.py` (pytest) | 1. Custom Tool only | unit-test-agent, integration-test-agent | ✅ Active |
| **Code Scanning** | N/A | N/A | `code_scanner.py` (AST analysis) | 1. Custom Tool only | test-orchestrator, edge-case-agent | ✅ Active |
| **Coverage Analysis** | N/A | N/A | `coverage_analyzer.py` (pytest-cov) | 1. Custom Tool only | test-orchestrator | ✅ Active |
| **QA Routing** | N/A | N/A | ~~router_tools.py~~ → `qa_router_tools.py` | 1. Custom Tool only | test-orchestrator | 🔧 Renamed (naming conflict) |

**Naming Conflict Resolved:**
- ❌ OLD: `QA_TEAM/tools/router_tools.py` (conflicted with MARKETING_TEAM)
- ✅ NEW: `QA_TEAM/tools/qa_router_tools.py` (unique name)

---

## 🏗️ Engineering & Orchestration Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **CTO Coordination** | N/A | `mcp__sequential-thinking__sequentialthinking` | `engineering_coordinator_tools.py` (658 lines: classify_request, create_execution_plan, get_capabilities) | 1. Custom Tool + MCP (sequential-thinking) | cto | ✅ Active (critical) |
| **Agent Validation** | N/A | N/A | `validate_agents.py` (YAML schema validation) | 1. Custom Tool only | security-auditor, technical-writer | ✅ Active |
| **MCP Server Bridge** | N/A | N/A | `mcp_server.py` (bridges Python tools to MCP) | 1. Custom Tool only | Infrastructure | ✅ Active |
| **Agent Config Update** | N/A | N/A | `update_agent_tools.py` (bulk YAML updates) | 1. Custom Tool only | technical-writer | ✅ Active |
| **Workflow Automation** | N/A | `mcp__n8n-mcp__*` (400+ integrations) | N/A | 1. MCP only | automation-agent | ✅ Active |
| **React Artifacts** | `artifacts-builder` (React + shadcn/ui) | N/A | N/A | 1. Skill only | landing-page-specialist | ✅ Active |
| **MCP Server Creation** | `mcp-builder` (create MCP servers) | N/A | N/A | 1. Skill only | Engineering team | ✅ Active |
| **Skill Creation** | `skill-creator` (create new skills) | N/A | N/A | 1. Skill only | Engineering team | ✅ Active |

---

## 📊 Complete MCP Server Inventory

| Server | Purpose | Key Tools | Agents Using | Status |
|--------|---------|-----------|--------------|--------|
| **marketing-tools** | OpenAI APIs (GPT-4o, Sora) | `generate_gpt4o_image`, `generate_sora_video` | visual-designer, video-producer | ✅ Active |
| **google-workspace** | G Suite automation | `send_email`, `create_doc`, `create_spreadsheet`, `create_drive_file`, `search_emails` | gmail-agent, copywriter, analyst, pdf-specialist, presentation-designer | ✅ Active |
| **perplexity** | Web research with citations | `perplexity_ask`, `perplexity_reason`, `perplexity_search` | research-agent (HYBRID fallback) | ✅ Active |
| **bright-data** | Web scraping (5K free/month) | `search_engine` (Google/Bing/Yandex), `scrape_as_markdown`, `scrape_batch` | seo-specialist, lead-gen-agent, research-agent, analyst | ✅ Active |
| **playwright** | Browser automation | `navigate`, `screenshot`, `click`, `fill`, `evaluate`, `get_visible_html` | USER_STORY_AGENT, seo-specialist, research-agent | ✅ Active |
| **n8n-mcp** | Workflow automation (400+ integrations) | n8n workflow execution | automation-agent | ✅ Active |
| **sequential-thinking** | Structured reasoning | `sequentialthinking` (step-by-step problem solving) | cto, system-architect | ✅ Active |

**Configuration:** All MCP servers defined in `.mcp.json` (gitignored - contains real API keys)

---

## 🎨 Complete Skills Inventory

### Visual Skills (5)
- ✅ `algorithmic-art` - p5.js generative art with seeded randomness
- ✅ `canvas-design` - PNG/PDF visual design with 50+ fonts, professional layouts
- ✅ `slack-gif-creator` - Animated GIFs optimized for Slack (size constraints)
- ✅ `theme-factory` - 10 pre-set themes for artifacts (vibrant, professional, minimal, etc.)
- ✅ `flow-diagram` - Mermaid diagrams (flowcharts, sequence, ER, state, CI/CD) with interactive HTML

### Development Skills (3)
- ✅ `artifacts-builder` - React + Tailwind CSS + shadcn/ui components for elaborate artifacts
- ✅ `mcp-builder` - Create MCP servers (Python FastMCP or Node/TypeScript SDK)
- ✅ `skill-creator` - Create new skills extending Claude's capabilities

### Content Skills (3)
- ✅ `internal-comms` - Internal communications (status reports, leadership updates, FAQs, newsletters)
- ✅ `brand-guidelines` - Anthropic's official brand colors and typography
- ✅ `pdf-filler` - PDF form filling and generation

### Document Skills (4 - Built-in)
- 🔧 `pdf` - PDF creation using pypdf library (ENABLED in MARKETING_TEAM settings)
- 🔧 `pptx` - PowerPoint generation via html2pptx + PptxGenJS (ENABLED in MARKETING_TEAM settings)
- ❌ `docx` - Word document generation (NOT enabled - use Google Docs MCP instead)
- ❌ `xlsx` - Excel operations (NOT enabled - use Google Sheets MCP instead)

### Integration Skills (3)
- ✅ `filesystem` - File operations (read, write, list, delete, path validation)
- ✅ `figma` - Figma design extraction via Figma API
- ✅ `context7` - Context management

**Skills Location:** `.claude/skills/` (team-level inheritance from `.claude/settings.json`)

---

## 📈 Usage Statistics

**Most Used Tools:**
- `upload_to_drive.py` - Used by 4+ agents (pdf-specialist, presentation-designer, visual-designer, video-producer)
- Google Workspace MCP - Used by 10+ agents (gmail-agent, copywriter, analyst, etc.)
- `filesystem` skill - Used by 3+ agents (lead-gen, seo-specialist, analyst)

**Orphaned Tools (Zero Agent Declarations):**
- 🚫 `pdf_generator.py` - DEPRECATED 2025-11-03, archived to `archive/tools/deprecated/`

**Naming Conflicts Resolved:**
- ✅ `QA_TEAM/tools/router_tools.py` → `qa_router_tools.py` (unique name)

---

## ⚠️ Governance Reminders

**Before Creating a New Tool:**
1. ✅ Check this registry for existing tools
2. ✅ Check `.mcp.json` for MCP servers
3. ✅ Check `.claude/skills/` for skills
4. ✅ Read PRE_FLIGHT_CHECKS.md
5. ✅ Follow TOOL_USAGE_POLICY.md priority hierarchy

**Before Declaring a Skill:**
1. ✅ Verify skill exists in `.claude/skills/` folder
2. ✅ Verify skill enabled in team `.claude/settings.json`
3. ✅ Test skill actually works before adding to agent YAML
4. ⚠️ Document skills (pdf/pptx/docx/xlsx) require explicit enablement

**After Creating a Tool:**
1. ✅ Update this registry with tool details
2. ✅ Add to appropriate category
3. ✅ Document which agents use it
4. ✅ Specify priority order (vs MCP/skills)

---

## 🔄 Maintenance

**Quarterly Audit:** Security-auditor runs TOOL_AUDITOR_CHECKLIST.md every 3 months

**Update Frequency:** Real-time (update immediately after tool creation/deprecation)

**Last Audit:** Not yet conducted (first audit scheduled for 2025-12-03)

---

**End of Registry**
