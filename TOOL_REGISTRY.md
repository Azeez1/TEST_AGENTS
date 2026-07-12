# TOOL REGISTRY - Single Source of Truth

**Last Updated:** 2026-07-12
**Total Inventory:** 35 custom tools + 10 MCP servers + 54 skills (see CLAUDE.md — single source of truth for counts)
**Maintained by:** Engineering Team (security-auditor + technical-writer)

---

## 📋 Overview

This registry documents ALL tools, MCP servers, and skills available to the 73 agents across 8 teams. Before creating a new tool, **CHECK THIS REGISTRY FIRST**.

**Priority Hierarchy:** MCP Servers → Skills → Custom Tools → Create New Tool (last resort)

---

## 🎨 Visual & Design Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **AI Image Generation (General)** | N/A | `mcp__marketing-tools__generate_gpt4o_image` | ~~openai_gpt4o_image.py~~ (retired) | 1. MCP only | visual-designer | ✅ Active |
| **AI Image Generation (UGC)** | N/A | `mcp__marketing-tools__generate_nano_banana_image` | N/A | 1. MCP only (Gemini 2.5 Flash Image) | visual-designer (PRIMARY for UGC) | ✅ Active |
| **Image Analysis (UGC Consistency)** ⭐ **NEW** | N/A | `mcp__marketing-tools__analyze_ugc_image` | N/A | 1. MCP only (GPT-4o Vision) | visual-designer, video-producer | ✅ Active |
| **Design-Focused Graphics** | `canvas-design` (50+ fonts, PNG/PDF) | N/A | N/A | 1. Skill only | visual-designer (PRIMARY), pdf-specialist, social-media-manager, presentation-designer | ✅ Active |
| **Algorithmic Art** | `algorithmic-art` (p5.js, generative) | N/A | N/A | 1. Skill only | visual-designer, social-media-manager | ✅ Active |
| **Video Generation (General + UGC)** | `consistent-video-ads` (multi-clip) | `mcp__marketing-tools__generate_sora_video` | ~~sora_video.py~~ (retired) | 1. MCP → 2. Skill (multi-clip) | video-producer (PRIMARY for UGC + general) | ✅ Active |
| **Video Generation (Text-to-Video)** | N/A | `mcp__marketing-tools__generate_veo_text_to_video` | N/A | 1. MCP only (Veo 3.1) | video-producer | ✅ Active |
| **Video Generation (Image-to-Video UGC Backup)** | N/A | `mcp__marketing-tools__generate_veo_ugc_from_image` | N/A | 1. MCP only (Veo 3.1 + reference image) | video-producer (BACKUP for UGC) | ✅ Active |
| **Slack GIFs** | `slack-gif-creator` (animated GIFs) | N/A | N/A | 1. Skill only | social-media-manager | ✅ Active |
| **System Diagrams** | `flow-diagram` (Mermaid, interactive HTML) | N/A | N/A | 1. Skill only | system-architect, technical-writer | ✅ Active |
| **Themed Artifacts** | `theme-factory` (10 pre-set themes) | N/A | N/A | 1. Skill only | presentation-designer, landing-page-specialist | ✅ Active |

**Usage Notes:**
- **canvas-design ownership:** visual-designer is PRIMARY owner; others use for specialized cases only
- **Video stitching:** `consistent-video-ads` skill (MARKETING_TEAM) handles multi-clip workflows MCP can't do
- ⭐ **UGC Workflow:** Sora 2 is PRIMARY for UGC video generation (50 styles, $0.10/sec). Veo 3.1 is BACKUP (use when Sora fails or native audio is required)

**UGC Workflow Options:**

| Workflow | Steps | Cost | Use Case | Success Rate |
|----------|-------|------|----------|--------------|
| **Standard** | Nano Banana → Veo UGC | $6.04/video | Quick testing, prototyping | 60% first-attempt |
| **Enhanced** | Nano Banana → Image Analysis → Veo UGC (with enhanced params) | $6.05/video | Production quality, targeted messaging | 90% first-attempt |
| **Expert-Optimized** ⭐ **NEW** | Nano Banana → video-producer builds N8n prompt → **prompt-engineer optimizes** → Veo UGC | $6.04/video (+$0 for optimization) | Maximum quality, first UGC for new product, high-value campaigns | 95% first-attempt |

**UGC Specifications:**
  - **Enhanced Parameters (Optional):** icp, product_features, video_setting, reference_image_description - For targeted messaging and better quality
  - **50+ UGC Styles:** demo (recommended), tutorial, how_to, before_after, first_time, morning_routine, product_showcase, problem_solving, hack, haul, honest_review, asmr, pov, satisfying, luxury, budget_friendly, and 34+ more - See [ugc_prompt_templates.json](MARKETING_TEAM/memory/ugc_prompt_templates.json) for complete list
  - **3 Platforms:** TikTok (9:16, 6-8s), Instagram (9:16, 8s), Facebook (16:9, 8s)
  - **Sora 2 is PRIMARY:** Use Sora 2 first for all UGC (50 styles, 7.5x cheaper). Veo 3.1 is backup when Sora fails or native audio is needed

**Expert-Optimized Workflow (Agent Handoff):**
  1. **visual-designer** creates product image via Nano Banana ($0.039)
  2. **video-producer** builds comprehensive N8n prompt with user parameters (ICP, features, setting)
  3. **video-producer** displays complete prompt to user
  4. **User** passes complete N8n prompt to **prompt-engineer** for expert optimization
  5. **prompt-engineer** applies advanced techniques (few-shot, Constitutional AI, safety filter avoidance, Veo 3.1 model-specific)
  6. **prompt-engineer** returns optimized prompt preserving all 6 N8n sections
  7. **video-producer** generates video with optimized custom_prompt parameter ($6.00)
  8. **Benefits:** Zero extra cost, 95% success rate, expert techniques, cross-team synergy (ENGINEERING helps MARKETING)

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
| **Figma Design Extraction** | `figma` (Figma API integration) | N/A | N/A | 1. Skill only | visual-designer, research-agent | ✅ Active |

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
| **Browser Automation** | N/A | `mcp__playwright__playwright_navigate`, `screenshot`, `click`, `fill`, `evaluate` | N/A | 1. MCP only | seo-specialist, research-agent | ✅ Active |

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
| **Workflow Automation** | `n8n-expression-syntax`, `n8n-mcp-tools-expert`, `n8n-workflow-patterns`, `n8n-validation-expert`, `n8n-node-configuration`, `n8n-code-javascript`, `n8n-code-python` (7 auto-activating skills) | `mcp__n8n-mcp__*` (400+ integrations) | N/A | 1. Skills auto-activate with MCP tools | automation-agent | ✅ Active |
| **React Artifacts** | `artifacts-builder` (React + shadcn/ui) | N/A | N/A | 1. Skill only | landing-page-specialist | ✅ Active |
| **MCP Server Creation** | `mcp-builder` (create MCP servers) | N/A | N/A | 1. Skill only | Engineering team | ✅ Active |
| **Skill Creation** | `skill-creator` (create new skills) | N/A | N/A | 1. Skill only | Engineering team | ✅ Active |
| **Workspace Validation** ⭐ **NEW** | N/A | N/A | `workspace_enforcer.py` (validate_workspace, get_absolute_paths, ensure_team_context) | 1. Custom Tool only (MANDATORY for all agents) | ALL 73 agents | ✅ Active (critical) |
| **Path Validation** ⭐ **NEW** | N/A | N/A | `path_validator.py` (validate_save_path, validate_read_path, validate_cross_team_path) | 1. Custom Tool only (MANDATORY for all agents) | ALL 73 agents | ✅ Active (critical) |

**Workspace Management Priority:**

⚠️ **CRITICAL:** These tools have HIGHEST priority:

1. **workspace_enforcer** - FIRST tool agents must use (before any task execution)
2. **path_validator** - REQUIRED for all file operations (read/write)
3. Then other tools (MCP servers, skills, custom tools)

**Rationale:** Workspace context is foundational - agents must know WHERE they are before WHAT they do.

**Usage Notes:**
- **workspace_enforcer:** Validates agent is in correct team workspace (MARKETING_TEAM, QA_TEAM, ENGINEERING_TEAM)
- **path_validator:** Converts relative paths to absolute paths, enforces cross-team boundaries
- **Declaring agents:** ALL 73 agents MUST include in YAML frontmatter (automatically added to all agents)

---

## 📝 Proposal & RFP Capabilities

| Capability | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------------|----------------|--------------|--------|
| **RFP Parsing** | `rfp_parser.py` (extract sections, requirements) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **PDF Extraction** | `pdf_extractor.py` (text + structure from PDFs) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Compliance Engine** | `compliance_engine.py` (30+ frameworks) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Adaptive Proposal Writing** | `adaptive_proposal_writer.py` (7-stage pipeline) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Knowledge Base** | `pinecone_knowledge_base.py` (vector search) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Hybrid Search** | `hybrid_search.py` (semantic + keyword) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Query Expansion** | `query_expander.py` (search optimization) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Embeddings** | `embeddings_generator.py` (vector embeddings) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **Priority Frameworks** | `user_priority_frameworks.py` (scoring) | 1. Custom Tool only | rfp-agent | ✅ Active |
| **RFP MCP Server** | `rfp_mcp_server.py` (MCP bridge) | 1. Custom Tool only | rfp-agent | ✅ Active |

---

## 🔧 Additional Marketing Tools (Not in Main Tables)

| Capability | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------------|----------------|--------------|--------|
| **Deliverables Email** | `send_deliverables_email.py` | 1. Custom Tool only | email-specialist | ✅ Active |
| **HTML Newsletter** | `send_html_newsletter.py` | 1. Custom Tool only | newsletter-agent | ✅ Active |
| **Fillable Workbook** | `create_fillable_workbook.py` | 1. Custom Tool only | analyst | ✅ Active |
| **Capability PDF** | `generate_capability_pdf_final.py` | 1. Custom Tool only | pdf-specialist | ✅ Active |
| **Capability Statement** | `generate_capability_statement.py` | 1. Custom Tool only | copywriter | ✅ Active |
| **Workflow Template PDF** | `generate_workflow_template_pdf.py` | 1. Custom Tool only | pdf-specialist | ✅ Active |

---

## 🏠 Root-Level Tools

| Capability | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------------|----------------|--------------|--------|
| **Supervisor MCP Server** | `supervisor_mcp_server.py` | 1. Custom Tool only | supervisor | ✅ Active |
| **Supervisor Tools** | `supervisor_tools.py` | 1. Custom Tool only | supervisor | ✅ Active |

---

## 📊 Analytics & Dashboard Capabilities

| Capability | Skill | MCP Tool | Custom Tool | Priority Order | Agents Using | Status |
|------------|-------|----------|-------------|----------------|--------------|--------|
| **Real-Time Dashboards** | `flow-diagram`, `infographic-creator`, `frontend-design` | N/A | Analytics dashboard implementation (React + Chart.js + WebSocket) | 1. Skills + Custom Implementation | analytics-dashboard-agent | ✅ Active |
| **Data Integration** | N/A | `mcp__google-workspace__create_spreadsheet`, `read_sheet_values` | ETL pipeline (pandas + asyncio) | 1. Custom Tool + MCP | analytics-dashboard-agent | ✅ Active |
| **Real-Time Data Streams** | N/A | N/A | WebSocket/SSE implementation (FastAPI) | 1. Custom Implementation only | analytics-dashboard-agent | ✅ Active |
| **Multi-Source ETL** | N/A | N/A | Data integration pipeline (API + DB + Files) | 1. Custom Tool only | analytics-dashboard-agent | ✅ Active |

**Usage Notes:**
- **analytics-dashboard-agent**: Primary agent for creating client analytics dashboards with real-time data visualization
- **Collaboration**: Works with frontend-developer (UI), backend-architect (API), database-architect (data modeling), devops-engineer (deployment)
- **Tech Stack**: React, Chart.js, D3.js, FastAPI, WebSocket, Redis, PostgreSQL
- **Use Cases**: Client analytics, KPI tracking, real-time metrics, data visualization, multi-source data integration

---

## 📊 Complete MCP Server Inventory

| Server | Purpose | Key Tools | Agents Using | Status |
|--------|---------|-----------|--------------|--------|
| **marketing-tools** ⭐ **UPDATED** | OpenAI APIs (GPT-4o, Sora) + Google Gemini APIs (Veo 3.1, Nano Banana) | `generate_gpt4o_image`, `generate_sora_video`, `generate_nano_banana_image` ⭐, `generate_veo_text_to_video` ⭐, `generate_veo_ugc_from_image` ⭐ | visual-designer, video-producer | ✅ Active |
| **google-workspace** | G Suite automation | `send_email`, `create_doc`, `create_spreadsheet`, `create_drive_file`, `search_emails` | gmail-agent, copywriter, analyst, pdf-specialist, presentation-designer | ✅ Active |
| **perplexity** | Web research with citations | `perplexity_ask`, `perplexity_reason`, `perplexity_search` | research-agent (HYBRID fallback) | ✅ Active |
| **bright-data** | Web scraping (5K free/month) | `search_engine` (Google/Bing/Yandex), `scrape_as_markdown`, `scrape_batch` | seo-specialist, lead-gen-agent, research-agent, analyst | ✅ Active |
| **playwright** | Browser automation | `navigate`, `screenshot`, `click`, `fill`, `evaluate`, `get_visible_html` | seo-specialist, research-agent | ✅ Active |
| **n8n-mcp** | Workflow automation (400+ integrations) | n8n workflow execution | automation-agent | ✅ Active |
| **sequential-thinking** | Structured reasoning | `sequentialthinking` (step-by-step problem solving) | cto, system-architect | ✅ Active |

**Configuration:** All MCP servers defined in `.mcp.json` (gitignored - contains real API keys)

---

## 🎬 UGC Video Ad Workflow (NEW - 2025-11-04)

**Complete two-agent pipeline for creating User Generated Content (UGC) video ads:**

### Architecture
```
visual-designer (Nano Banana) → video-producer (Veo 3.1)
   Product Image                  UGC Video Ad
```

### Tools Involved
1. **`mcp__marketing-tools__generate_nano_banana_image`** (visual-designer)
   - Model: Gemini 2.5 Flash Image
   - Cost: $0.039 per image
   - Purpose: Product images optimized for Veo 3.1 video conversion
   - Capabilities: Character consistency, lifestyle photography, natural settings

2. **`mcp__marketing-tools__generate_veo_ugc_from_image`** (video-producer) ✨ **AUTOMATIC ANALYSIS**
   - Model: Veo 3.1 (image-to-video) + GPT-4o Vision (automatic analysis)
   - Cost: $4.51-$6.01 per video (6-8 seconds + automatic image analysis)
   - Purpose: Convert product images to UGC-style video ads with maximum visual consistency
   - Capabilities: 4 UGC styles (testimonial, demo, unboxing, lifestyle), native audio, **automatic image analysis by default**
   - **NEW:** Image analysis is automatic (+$0.01, 588x ROI, opt-out available with `auto_analyze_image: false`)

3. **`mcp__marketing-tools__generate_veo_text_to_video`** (video-producer)
   - Model: Veo 3.1 (text-to-video)
   - Cost: $0.75 per second ($4.50-$6.00 for 6-8s)
   - Purpose: Generate videos from text prompts (no image input)
   - Alternative workflow for non-product UGC

### Cost Comparison
- **AI-Generated UGC (Default):** $4.55-$6.05 per ad (image $0.039 + video $4.50-$6.00 + automatic analysis $0.01)
- **AI-Generated UGC (Opt-Out):** $4.54-$6.04 per ad (image + video, no analysis - NOT recommended for production)
- **Human UGC Creators:** $100-$500 per ad
- **Savings:** 93-98% cost reduction
- **ROI of Automatic Analysis:** 588x (100% quality improvement for 0.17% cost increase)

### Platform Optimization
- **TikTok:** 9:16 portrait, 6-8 seconds, fast-paced
- **Instagram:** 9:16 portrait, 8 seconds, aesthetic focus
- **Facebook:** 16:9 landscape, 8 seconds, testimonial-heavy

### UGC Styles
1. **Testimonial** - Person talking about product benefits
2. **Demo** - Showing product features in action
3. **Unboxing** - First impression and packaging reveal
4. **Lifestyle** - Product integrated into daily routine

### Why Veo 3.1 is Required
- ✅ **Only model** supporting image-to-video UGC (Sora doesn't support reference images)
- ✅ Native audio generation (no separate TTS needed)
- ✅ Character consistency via reference images
- ✅ 4-8 second duration (perfect for social media)
- ✅ Platform-specific aspect ratios (9:16, 16:9)

### Agent Responsibilities
- **visual-designer:** Creates UGC-ready product images (natural settings, lifestyle context)
- **video-producer:** Converts images to video ads using UGC templates

### Invocation Examples
```
"Use visual-designer to create product image for TikTok UGC ad"
→ Nano Banana generates 9:16 lifestyle product shot ($0.039)

"Use video-producer to create testimonial UGC video from this image"
→ Veo 3.1 automatically analyzes image with GPT-4o Vision ($0.01)
→ Generates 6-8s testimonial video with visual consistency ($4.50-$6.00)
→ Total: $4.55-$6.05 (automatic analysis by default)

"Use video-producer for quick UGC test without image analysis"
→ Veo 3.1 generates video without analysis ($4.50-$6.00)
→ Set auto_analyze_image: false to opt-out
→ Total: $4.54-$6.04 (testing only, not recommended for production)
```

**Documentation:**
- [video-producer.md](MARKETING_TEAM/.claude/agents/video-producer.md) - Complete UGC workflow guide (lines 1-200)
- [visual-designer.md](MARKETING_TEAM/.claude/agents/visual-designer.md) - UGC image best practices (lines 37-133)

---

## 🎨 Complete Skills Inventory

### Visual Skills (6)
- ✅ `algorithmic-art` - p5.js generative art with seeded randomness
- ✅ `canvas-design` - PNG/PDF visual design with 50+ fonts, professional layouts
- ✅ `slack-gif-creator` - Animated GIFs optimized for Slack (size constraints)
- ✅ `theme-factory` - 10 pre-set themes for artifacts (vibrant, professional, minimal, etc.)
- ✅ `flow-diagram` - Mermaid diagrams (flowcharts, sequence, ER, state, CI/CD) with interactive HTML
- ✅ `infographic-creator` - Static, animated, and interactive infographics for social media and presentations

### Development Skills (4)
- ✅ `artifacts-builder` - React + Tailwind CSS + shadcn/ui components for elaborate artifacts
- ✅ `mcp-builder` - Create MCP servers (Python FastMCP or Node/TypeScript SDK)
- ✅ `skill-creator` - Create new skills extending Claude's capabilities
- ✅ `frontend-design` - Production-grade frontend interfaces with high design quality

### Content Skills (3)
- ✅ `internal-comms` - Internal communications (status reports, leadership updates, FAQs, newsletters)
- ✅ `brand-guidelines` - Anthropic's official brand colors and typography
- ✅ `pdf-filler` - PDF form filling and generation

### Document Skills (4 - Bundled in `document-skills`)
- 🔧 `pdf` - PDF creation using pypdf library (ENABLED in MARKETING_TEAM settings)
- 🔧 `pptx` - PowerPoint generation via html2pptx + PptxGenJS (ENABLED in MARKETING_TEAM settings)
- ❌ `docx` - Word document generation (NOT enabled - use Google Docs MCP instead)
- ❌ `xlsx` - Excel operations (NOT enabled - use Google Sheets MCP instead)

### Video Skills (1)
- ✅ `remotion-video` - Programmatic video creation with React (motion graphics, captions, data viz)

### Research Skills (1)
- ✅ `last30days` - Real-time Reddit + X trend research with engagement metrics (past 30 days)

### n8n Automation Skills (7)
- ✅ `n8n-code-javascript` - JavaScript in n8n Code nodes ($input/$json syntax)
- ✅ `n8n-code-python` - Python in n8n Code nodes (_input/_json syntax)
- ✅ `n8n-expression-syntax` - n8n expression validation and {{}} syntax
- ✅ `n8n-mcp-tools-expert` - n8n MCP tool selection and usage patterns
- ✅ `n8n-node-configuration` - Operation-aware node config and property dependencies
- ✅ `n8n-validation-expert` - Validation error interpretation and fixing
- ✅ `n8n-workflow-patterns` - Proven workflow architectural patterns

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

**Last Audit:** 2026-02-20 (system-wide audit via 4-agent team)

---

**End of Registry**
