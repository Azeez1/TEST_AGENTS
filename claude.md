# TEST_AGENTS - AI Multi-Agent System Repository

## 📋 Repository Overview

This repository contains **4 autonomous AI agent systems** powered by the Claude Agent SDK, featuring **35 specialized agents** for user story generation, marketing automation, test generation, software engineering, quality assurance, and AI/ML development.

**Systems:**
- **USER_STORY_AGENT** - Transform meeting notes into backlog-ready user stories with Excel export
- **MARKETING_TEAM** - **17 marketing agents** for content creation, social media, images, videos, emails, lead generation, landing pages, and workflow automation
- **TEST_AGENT** - 5 testing agents for automated pytest test suite generation
- **ENGINEERING_TEAM** - **12 engineering agents** ⭐ **SUPER TEAM** for DevOps, security, frontend, backend, AI/ML, UX design, quality assurance, testing, optimization, database design, and troubleshooting

All agents work through natural conversation with Claude Code - no Python orchestrators needed.

---

## ⚠️ CRITICAL: Use Existing Tools First

**IMPORTANT INSTRUCTION FOR ALL AI ASSISTANTS:**

When working with this repository, **ALWAYS use existing agents, tools, skills, and MCP servers FIRST**. Do NOT create new implementations when functionality already exists.

**Priority Order:**
1. **Use existing agents** (`.claude/agents/*.md` files) - Invoke them explicitly
2. **Use installed skills** (`.claude/skills/*`) - 13 powerful skills available
3. **Use MCP servers** - 7 external integrations (Playwright, Google Workspace, Perplexity, Bright Data, etc.)
4. **Use existing tools** (`tools/*.py`) - Simpler utilities and API wrappers
5. **Only if none exist** - Then create new implementations

**Examples of What NOT To Do:**
- ❌ Writing new Python code for PowerPoint when pptx skill exists
- ❌ Creating new email scripts when Gmail MCP exists
- ❌ Building new image generation when `tools/openai_gpt4o_image.py` exists
- ❌ Installing new libraries when existing tools already have dependencies

**Examples of What TO Do:**
- ✅ "Use the presentation-designer agent with pptx skill for PowerPoint"
- ✅ "Use gmail-agent with Google Workspace MCP to send emails"
- ✅ "Use the visual-designer agent with GPT-4o image generation"
- ✅ "Use existing tools in tools/ for simple API wrappers"

**How to Check What Exists:**
1. Check `.claude/agents/` for available agents
2. Check `.claude/skills/` for installed skills
3. Check `.claude.json` or `.mcp.json` for MCP servers
4. Check `tools/` for existing Python tools
5. Ask the user if unsure: "Do we have a tool for this already?"

**This saves time, avoids duplication, and uses battle-tested code.**

---

## 🚀 Quick Navigation

| System | Purpose | Quick Start | Docs |
|--------|---------|-------------|------|
| **USER_STORY_AGENT** | Meeting notes → User stories | `cd USER_STORY_AGENT && streamlit run app_ui.py` | [README](USER_STORY_AGENT/README.md) |
| **MARKETING_TEAM** | Marketing content automation | Talk to Claude Code agents | [README](MARKETING_TEAM/README.md) |
| **TEST_AGENT** | Automated test generation | Talk to Claude Code agents | [README](TEST_AGENT/README.md) |
| **ENGINEERING_TEAM** | Software engineering & infrastructure | Talk to Claude Code agents | [README](ENGINEERING_TEAM/README.md) |

**Key Documentation:**
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - Complete guide to using all 28 agents
- [MCP_SETUP.md](MCP_SETUP.md) - MCP server configuration
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation details

---

## 📁 Project Structure

```
TEST_AGENTS/
├── claude.md                        ← YOU ARE HERE - Repository navigation guide
├── .claude.json                     ← Claude Code MCP configuration
├── .gitignore                       ← Excludes outputs, configs, artifacts
├── MULTI_AGENT_GUIDE.md             ← Complete guide for all 20 agents
├── MCP_SETUP.md                     ← MCP server setup instructions
├── IMPLEMENTATION_SUMMARY.md        ← Technical implementation overview
│
├── USER_STORY_AGENT/                ← Streamlit app for user story generation
│   ├── README.md                    ← Quick start guide
│   ├── app_ui.py                    ← Main Streamlit UI (6 tabs)
│   ├── autonomous_mode.py           ← Browser automation with MCP
│   ├── story_generator.py           ← Story generation prompts
│   ├── formatters.py                ← JSON parsing with fallback strategies
│   ├── excel_handler.py             ← Excel read/write operations
│   ├── note_parser.py               ← Multi-format file parsing (PDF, DOCX, etc.)
│   ├── file_handlers.py             ← Extended file format support
│   ├── multi_file_processor.py      ← Multi-file processing
│   ├── ocr_handler.py               ← OCR for images with pytesseract
│   ├── mcp_client.py                ← MCP stdio client with tool execution
│   ├── research_prompts.py          ← Autonomous research prompts
│   ├── feedback_handler.py          ← Feedback learning system
│   ├── conversation_memory.py       ← Persistent preferences storage
│   ├── ui_helpers.py                ← UI utilities
│   ├── mcp_config.json              ← MCP configuration
│   ├── requirements.txt             ← Python dependencies
│   ├── start_ui.bat                 ← Windows launcher
│   └── [Documentation]              ← CLEAN_CODEBASE.md, EXCEL_FIGMA_WORKFLOW.md, etc.
│
├── MARKETING_TEAM/                  ← 17 marketing automation agents
│   ├── README.md                    ← Quick start guide
│   ├── examples/                    ← Curated examples (tracked in git)
│   │   └── skills/                  ← Examples by skill
│   │       ├── algorithmic-art/     ← Generative art examples
│   │       ├── blog-posts/
│   │       ├── landing-pages/
│   │       └── [other skills]/
│   ├── templates/                   ← Reusable templates (tracked in git)
│   │   └── reusable/
│   │       ├── blog_post_template.md
│   │       ├── social_media_template.md
│   │       ├── landing_page_template.html
│   │       └── email_template.md
│   ├── outputs/                     ← Real deliverables (GITIGNORED)
│   │   ├── blog_posts/
│   │   ├── social_media/
│   │   ├── images/
│   │   ├── videos/
│   │   ├── automation/              ← n8n workflow specs and artifacts
│   │   └── [other content]/
│   ├── voice_interface/             ← ✨ NEW: Voice interface modules
│   │   ├── config.py                ← Voice configuration loader
│   │   ├── websocket_client.py      ← ElevenLabs WebSocket connection
│   │   ├── audio_handler.py         ← Microphone & speaker I/O
│   │   ├── voice_agent_router.py    ← Natural language agent routing
│   │   ├── context_manager.py       ← Multi-context lifecycle
│   │   └── conversation_memory.py   ← Session persistence
│   ├── voice_cli_simple.py          ← ✅ WORKING: Text-based conversation with audio
│   ├── voice_cli.py                 ← ⚠️ Has threading issues (real-time audio)
│   ├── voice_app.py                 ← Streamlit UI (session viewer only)
│   ├── start_voice_cli.bat          ← Launcher for working voice CLI
│   ├── requirements_voice.txt       ← Voice dependencies
│   ├── .claude/
│   │   └── agents/                  ← 17 agent definitions
│   │       ├── router-agent.md      ← Campaign coordinator
│   │       ├── copywriter.md        ← Blog posts & articles
│   │       ├── social-media-manager.md  ← X/Twitter, LinkedIn posts
│   │       ├── visual-designer.md   ← GPT-4o image generation
│   │       ├── video-producer.md    ← Sora video creation
│   │       ├── seo-specialist.md    ← SEO research, SERP scraping, rank tracking
│   │       ├── email-specialist.md  ← Email copywriting
│   │       ├── gmail-agent.md       ← Email sending via Gmail API
│   │       ├── pdf-specialist.md    ← PDF whitepaper creation
│   │       ├── presentation-designer.md  ← PowerPoint decks
│   │       ├── landing-page-specialist.md  ← Landing page UX, code, competitor analysis
│   │       ├── analyst.md           ← Performance analysis & competitive benchmarking
│   │       ├── content-strategist.md     ← Campaign orchestration
│   │       ├── editor.md            ← Content review
│   │       ├── research-agent.md    ← Web research, competitive intelligence
│   │       ├── lead-gen-agent.md    ← B2B/local lead generation via web scraping
│   │       └── automation-agent.md  ← ✨ NEW: n8n workflow automation & orchestration
│   ├── tools/                       ← Marketing tools
│   │   ├── openai_gpt4o_image.py    ← GPT-4o image generation
│   │   ├── gmail_api.py             ← Gmail integration
│   │   ├── upload_to_drive.py       ← Google Drive binary file uploads (fills MCP gap)
│   │   ├── pdf_generator.py         ← PDF generation
│   │   ├── sora_video.py            ← Sora video API
│   │   ├── platform_formatters.py   ← Social media formatters
│   │   ├── router_tools.py          ← Agent coordination tools
│   │   ├── send_email_with_attachment.py  ← Email attachments via Gmail API
│   │   ├── send_deliverables_email.py     ← Automated deliverables sender
│   │   └── send_marketing_team_doc.py     ← Email marketing team documentation
│   ├── scripts/                     ← Utility scripts
│   │   ├── create_word_documents.py     ← Convert markdown to Word docs
│   │   ├── generate_linkedin_image.py   ← Generate LinkedIn images
│   │   ├── test_openai_connection.py    ← Test OpenAI API setup
│   │   ├── create_ai_video.py           ← Sora video generation testing
│   │   └── upload_video_to_drive.py     ← Manual Drive upload utility
│   ├── docs/                        ← Comprehensive documentation
│   │   ├── getting-started/
│   │   │   ├── api-setup.md         ← API configuration guide
│   │   │   └── voice-setup.md       ← ✨ NEW: Voice interface setup (60-second guide)
│   │   ├── guides/
│   │   │   ├── usage-guide.md       ← Complete usage examples
│   │   │   ├── campaign-examples.md ← Real campaign examples
│   │   │   └── voice/               ← ✨ NEW: Voice interface documentation
│   │   │       ├── user-guide.md    ← What works and why
│   │   │       └── technical.md     ← Technical documentation
│   │   └── architecture/
│   │       ├── system-architecture.md   ← Technical architecture
│   │       ├── mcp-config.md        ← MCP configuration details
│   │       └── build-notes.md       ← Build process notes
│   ├── requirements.txt             ← Python dependencies
│   └── .env.example                 ← Environment variables template
│
└── TEST_AGENT/                      ← 5 automated testing agents
    ├── README.md                    ← Quick start guide
    ├── HOW_TO_USE.md                ← Detailed usage guide
    ├── BUILD_SUMMARY.md             ← Build and architecture summary
    ├── .claude/
    │   └── agents/                  ← 5 agent definitions
    │       ├── test-orchestrator.md ← Testing coordinator
    │       ├── unit-test-agent.md   ← Unit test generation
    │       ├── integration-test-agent.md  ← Integration tests
    │       ├── edge-case-agent.md   ← Edge case identification
    │       └── fixture-agent.md     ← Pytest fixtures & mocks
    ├── tools/                       ← Testing tools
    │   ├── code_scanner.py          ← Code analysis & scanning
    │   ├── test_generator.py        ← Test case generation
    │   ├── coverage_analyzer.py     ← Coverage analysis
    │   └── router_tools.py          ← Agent coordination
    └── requirements.txt             ← Python dependencies (pytest, pytest-cov, etc.)
```

---

## 🤖 Complete Agent Directory

### USER_STORY_AGENT (1 System)

**Streamlit Application:**
- Converts meeting notes, PDFs, images to backlog-ready user stories
- Supports Gherkin and Explicit/Detailed acceptance criteria formats
- Optional browser research mode with Playwright MCP
- Automatic Figma prototype navigation and design extraction
- Excel export with formatting

**Invoke:** Launch Streamlit app via `streamlit run app_ui.py`

---

### MARKETING_TEAM (17 Agents)

| Agent | Capability | Invoke With |
|-------|-----------|-------------|
| **router-agent** | Coordinates complex multi-agent campaigns | `"Use router-agent to plan a product launch campaign"` |
| **content-strategist** | Full campaign orchestration | `"Use content-strategist to plan Q1 content"` |
| **research-agent** | 🔥 **HYBRID:** Custom Perplexity research tools + MCP for comprehensive market research, competitive intelligence, web scraping | `"Use research-agent to research AI marketing trends"` |
| **lead-gen-agent** | B2B/local lead generation via Bright Data web scraping | `"Use lead-gen-agent to find 50 SaaS leads in SF"` |
| **automation-agent** | ✨ **NEW** n8n workflow automation & orchestration for marketing processes | `"Use automation-agent to create a lead nurture workflow"` |
| **copywriter** | Blog posts, articles, web copy (2000+ words) | `"Use copywriter to write a blog about AI trends"` |
| **editor** | Content review, grammar, brand voice alignment | `"Use editor to review this blog post"` |
| **social-media-manager** | X/Twitter, LinkedIn posts with hashtags | `"Use social-media-manager to create a LinkedIn post"` |
| **visual-designer** | GPT-4o image generation | `"Use visual-designer to create a header image"` |
| **video-producer** | Sora video creation | `"Use video-producer to create a 15s product video"` |
| **seo-specialist** | Keyword research, SERP scraping, rank tracking, Playwright web research | `"Use seo-specialist to research AI marketing keywords"` |
| **email-specialist** | Email sequences, newsletters, campaigns | `"Use email-specialist to write a welcome email"` |
| **gmail-agent** | Email sending via Gmail API | `"Use gmail-agent to send this newsletter"` |
| **landing-page-specialist** | Conversion-focused landing pages with UX, code, competitor analysis | `"Use landing-page-specialist to build a landing page"` |
| **pdf-specialist** | PDF whitepaper/report creation | `"Use pdf-specialist to create a PDF guide"` |
| **presentation-designer** | PowerPoint deck creation | `"Use presentation-designer to create a pitch deck"` |
| **analyst** | Campaign performance analysis & competitive benchmarking | `"Use analyst to analyze campaign metrics"` |

**APIs Required:**
- OpenAI API (images via GPT-4o, videos via Sora)
- Gmail API (email sending)
- Google Drive API (file uploads, optional)
- Bright Data MCP (lead generation - 5,000 free requests/month)
- ElevenLabs API (voice interface - text-to-speech)

**Voice Interface (COMING SOON):**

**Status:** Custom voice implementation archived, switching to ElevenLabs Conversational AI for true real-time voice.

**What's changing:**
- Custom voice infrastructure archived to `MARKETING_TEAM/archive/voice_custom_implementation/`
- Switching to ElevenLabs platform for real-time microphone → speaker conversation
- Implementation coming soon

**Current Options:**
1. Wait for ElevenLabs integration (recommended - full real-time voice)
2. Use archived text-based CLI (see `archive/voice_custom_implementation/` - type messages, get audio files)

📖 **Documentation:**
- [MARKETING_TEAM/docs/guides/voice/REALTIME_VOICE_OPTIONS.md](MARKETING_TEAM/docs/guides/voice/REALTIME_VOICE_OPTIONS.md) - Why switching to ElevenLabs
- [MARKETING_TEAM/archive/voice_custom_implementation/VOICE_IMPLEMENTATION_SUMMARY.md](MARKETING_TEAM/archive/voice_custom_implementation/VOICE_IMPLEMENTATION_SUMMARY.md) - Previous custom implementation

---

### TEST_AGENT (5 Agents)

| Agent | Capability | Invoke With |
|-------|-----------|-------------|
| **test-orchestrator** | Coordinates test generation across modules | `"Use test-orchestrator to scan my codebase"` |
| **unit-test-agent** | Unit tests with AAA pattern, mocking, parametrization | `"Use unit-test-agent to test story_generator.py"` |
| **integration-test-agent** | End-to-end workflow and module interaction tests | `"Use integration-test-agent to test the workflow"` |
| **edge-case-agent** | Identifies boundary values, empty inputs, security cases | `"Use edge-case-agent to find edge cases"` |
| **fixture-agent** | Pytest fixtures, mock objects, factory fixtures | `"Use fixture-agent to create test fixtures"` |

**Testing Stack:**
- pytest, pytest-cov, pytest-asyncio, pytest-mock
- 80%+ coverage goals
- AAA pattern (Arrange-Act-Assert)

---

### ENGINEERING_TEAM (12 Agents) ⭐ **SUPER TEAM**

**Core 7 Agents (Custom Built):**

| Agent | Capability | Invoke With |
|-------|-----------|-------------|
| **devops-engineer** ⭐ | **Production-ready** CI/CD (GitHub Actions), Terraform (AWS/GCP), Kubernetes (Helm), monitoring (Prometheus/Grafana), security scanning (886 lines of code) | `"Use devops-engineer to create complete deployment pipeline"` |
| **frontend-developer** | React components, responsive design (Tailwind), state management, performance optimization, accessibility (WCAG) | `"Use frontend-developer to build agent dashboard in Next.js"` |
| **backend-architect** | RESTful API design, microservices architecture, database schema, caching strategies, scalability planning | `"Use backend-architect to design API for 35 agents"` |
| **security-auditor** ⭐ | **Unique comprehensive security** - Code security analysis, vulnerability scanning (OWASP Top 10), compliance (GDPR/HIPAA) | `"Use security-auditor to scan for hardcoded API keys"` |
| **technical-writer** ⭐ | **Broader scope** - PRDs, technical specs, API docs (OpenAPI), architecture diagrams, user guides | `"Use technical-writer to write PRD for agent scheduling"` |
| **ai-engineer** ⭐ | **Perfect for 35 agents** - LLM integration, RAG systems, prompt optimization, agent frameworks (LangChain/LangGraph) | `"Use ai-engineer to optimize prompts for all 35 agents"` |
| **ui-ux-designer** | User research, wireframes, design systems, accessibility, user flows, usability testing | `"Use ui-ux-designer to create wireframes for dashboard"` |

**Specialist 5 Agents (From aitmpl.com - Community Validated):**

| Agent | Capability | Downloads | Invoke With |
|-------|-----------|-----------|-------------|
| **code-reviewer** | Quality, security, maintainability reviews - automatic git diff analysis | 3.2K | `"Use code-reviewer to review MARKETING_TEAM email tool"` |
| **test-engineer** | Test automation (Jest, Playwright, pytest), QA strategy, CI/CD testing | 1.3K | `"Use test-engineer to create test strategy for 35 agents"` |
| **prompt-engineer** | LLM prompt optimization, techniques (few-shot, chain-of-thought), benchmarking | 2.4K | `"Use prompt-engineer to optimize copywriter prompt"` |
| **database-architect** | Database design, data modeling, scalability (sharding, replication), polyglot persistence | 1.2K | `"Use database-architect to design analytics DB for 35 agents"` |
| **debugger** | Root cause analysis, troubleshooting, error investigation, hypothesis testing | 1.7K | `"Use debugger to fix MARKETING_TEAM timeout issues"` |

**Engineering Stack:**
- **DevOps:** Docker, Kubernetes, Terraform, Helm, GitHub Actions, Prometheus, Grafana
- **Backend:** Python, FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL
- **Frontend:** React, Next.js, TypeScript, Tailwind CSS, shadcn/ui
- **AI/ML:** LangChain, LangGraph, OpenAI, Anthropic Claude, vector databases
- **Design:** Wireframes, design systems, Figma integration, accessibility (WCAG)
- **Security:** Trivy, kube-bench, gitleaks, Bandit, Safety, pip-audit
- **Quality:** Code review, test automation, performance testing
- **Database:** PostgreSQL, MongoDB, Redis, Elasticsearch, InfluxDB
- **Docs:** Markdown, Mermaid diagrams, OpenAPI/Swagger, PlantUML

**Special Features:**
- ✅ **Full workspace access** - All 12 agents can work with all 35 agents across 4 systems
- ✅ **Production-ready code** - devops-engineer provides 886 lines of battle-tested CI/CD, Terraform, Helm
- ✅ **Community validated** - 5 specialist agents with thousands of downloads (proven in production)
- ✅ **AI optimization powerhouse** - ai-engineer + prompt-engineer can optimize all 35 agent prompts
- ✅ **Quality layer** - code-reviewer + security-auditor ensure comprehensive code quality
- ✅ **Complete testing** - test-engineer builds strategies, TEST_AGENT generates tests
- ✅ **Design → Develop → Test → Deploy** - Complete SDLC from UX to production
- ✅ **Cross-team collaboration** - DevOps deploys all systems, AI/Prompt engineers optimize all agents, Security/Code reviewers audit everything
- ✅ **End-to-end workflows** - PRD (technical-writer) → Database (database-architect) → Wireframes (ui-ux-designer) → API (backend-architect) → UI (frontend-developer) → Review (code-reviewer) → Test (test-engineer) → Deploy (devops-engineer) → Audit (security-auditor) → Optimize (ai-engineer + prompt-engineer) → Debug (debugger)

---

## 📖 Documentation Map

### Getting Started
- [USER_STORY_AGENT/README.md](USER_STORY_AGENT/README.md) - User story generation quick start
- [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md) - Marketing agents overview
- [MARKETING_TEAM/docs/getting-started/api-setup.md](MARKETING_TEAM/docs/getting-started/api-setup.md) - API configuration (OpenAI, Gmail, Drive)
- [TEST_AGENT/README.md](TEST_AGENT/README.md) - Testing agents overview
- [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) - Engineering agents overview
- [MCP_SETUP.md](MCP_SETUP.md) - MCP server configuration

### Usage Guides
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - **MASTER GUIDE** for all 35 agents
- [MARKETING_TEAM/docs/guides/usage-guide.md](MARKETING_TEAM/docs/guides/usage-guide.md) - Marketing agent usage with examples
- [MARKETING_TEAM/docs/guides/campaign-examples.md](MARKETING_TEAM/docs/guides/campaign-examples.md) - Real campaign examples
- [TEST_AGENT/HOW_TO_USE.md](TEST_AGENT/HOW_TO_USE.md) - Testing agent usage with examples
- [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) - Engineering workflows and examples

### Technical Documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation overview
- [MARKETING_TEAM/docs/architecture/system-architecture.md](MARKETING_TEAM/docs/architecture/system-architecture.md) - Marketing system architecture
- [MARKETING_TEAM/docs/architecture/mcp-config.md](MARKETING_TEAM/docs/architecture/mcp-config.md) - MCP configuration details
- [TEST_AGENT/BUILD_SUMMARY.md](TEST_AGENT/BUILD_SUMMARY.md) - Testing system build notes
- [ENGINEERING_TEAM/docs/](ENGINEERING_TEAM/docs/) - PRDs, technical specs, API docs, deployment guides

### Workflow Guides
- [USER_STORY_AGENT/EXCEL_FIGMA_WORKFLOW.md](USER_STORY_AGENT/EXCEL_FIGMA_WORKFLOW.md) - Excel + Figma integration workflow
- [USER_STORY_AGENT/CLEAN_CODEBASE.md](USER_STORY_AGENT/CLEAN_CODEBASE.md) - Codebase structure reference

---

## 🛠️ Development Guidelines

### How the Multi-Agent System Works

**Core Concept:**
1. Agent definitions live in `.claude/agents/*.md` files
2. Each agent has YAML frontmatter defining its tools and capabilities
3. When you invoke an agent, Claude Code reads that definition and adopts the persona
4. No Python orchestrator needed - Claude Code IS the orchestrator

**Example:**
```
You: "Use the copywriter subagent to write a blog post"

What happens:
1. Claude reads MARKETING_TEAM/.claude/agents/copywriter.md
2. Claude adopts the copywriter persona and instructions
3. Claude uses the tools specified (get_brand_voice, etc.)
4. Claude generates the blog post in the copywriter's style
5. Claude returns results to you
```

### Adding New Agents

Create a new `.md` file in the appropriate `.claude/agents/` folder:

```markdown
---
name: Agent Name
description: What this agent does
tools:
  - tool_name_1
  - tool_name_2
---

# Agent Name

You are an expert in [domain].

Your responsibilities:
- [Task 1]
- [Task 2]

Instructions:
1. Always [instruction]
2. Never [anti-pattern]

Output format:
[Specify expected output]
```

### Coding Standards

**Python:**
- PEP 8 style guide
- Type hints where applicable
- Docstrings for functions/classes
- Modular design - separate files for distinct functionality

**Agent Definitions:**
- Clear YAML frontmatter
- Specific tool lists
- Detailed instructions
- Example outputs when helpful

**Documentation:**
- README.md for each system
- Inline code comments for complex logic
- Workflow guides for multi-step processes

### Tools vs Scripts Organization

**tools/** - Production Agent Components
- Reusable libraries called by multiple agents
- SDK integration with @tool decorators
- Unique tools not available in MCP servers (GPT-4o images, Sora videos, PDF generation, PowerPoint)
- **MCP gap fillers** - Functions that MCP servers can't handle (e.g., upload_to_drive.py for local binary files)
- Robust error handling, rate limiting, authentication
- Production-ready code with logging and validation
- Examples: openai_gpt4o_image.py, sora_video.py, send_email_with_attachment.py, upload_to_drive.py
- **Note:** Google Drive/Gmail text operations handled by google-workspace MCP server

**scripts/** - One-Off Utilities & Test Tools
- Standalone executables for specific tasks
- Testing and debugging tools (test_mcp_connection.py, test_mcp_imports.py)
- Manual workflows and one-time conversions
- Less robust, can have hardcoded values
- Simple output, minimal error handling
- Examples: test_openai_connection.py, create_word_documents.py

**Decision Matrix:**

| Question | tools/ | scripts/ |
|----------|--------|----------|
| Will agents call this repeatedly? | ✅ Yes | ❌ No |
| Needs @tool decorator? | ✅ Yes | ❌ No |
| Part of production workflow? | ✅ Yes | ❌ No |
| One-time testing/debugging? | ❌ No | ✅ Yes |
| Manual utility/conversion? | ❌ No | ✅ Yes |
| Should be imported as module? | ✅ Yes | ❌ No |

### Hybrid Output Management Strategy

The repository uses a **hybrid approach** for managing agent outputs:

| Folder | Purpose | Git Tracked | Use Case |
|--------|---------|-------------|----------|
| **examples/** | Reference materials | ✅ Yes | Curated demos, portfolio pieces, test artifacts |
| **templates/** | Starting frameworks | ✅ Yes | Reusable templates for common deliverables |
| **outputs/** | Real deliverables | ❌ No | Client work, campaigns, production content |

**Why this approach?**
- **Real work stays private** - Your actual deliverables in `outputs/` are never committed
- **Examples preserved** - Reference materials in `examples/` are version controlled
- **Templates shared** - Reusable starting points in `templates/` are tracked
- **Clean separation** - Test vs production vs templates
- **Flexible** - Can adjust later if needs change

**How agents work with this:**
- By default, agents output to `outputs/` (gitignored)
- High-quality reference pieces can be copied to `examples/` for preservation
- Agents can use templates from `templates/` as starting points

📖 See [MARKETING_TEAM/examples/README.md](MARKETING_TEAM/examples/README.md) and [MARKETING_TEAM/templates/README.md](MARKETING_TEAM/templates/README.md) for complete guides.

### Git Workflow

**What's Excluded (`.gitignore`):**
- `outputs/` and `output/` folders (generated content)
- `*.xlsx`, `*.pdf`, `*.docx`, `*.pptx` (artifacts)
- `__pycache__/`, `*.pyc` (Python cache)
- `memory/`, `archive/` (runtime data)
- `.env`, `credentials.json`, `*.key` (secrets)
- `.claude.json`, `.mcp.json` (contain real API keys - stay local)
- `.claude/settings.local.json` (local config)
- `*.backup`, `.mcp.test-*.json` (backups and test configs)

**What's Included:**
- Source code (`.py` files)
- Agent definitions (`.claude/agents/*.md`)
- Documentation (`.md` files)
- Configuration templates (`.env.example`, `.claude.json.example`, `.mcp.json.example`)
- Requirements files
- **`examples/` folder** - Curated examples and reference materials (EXCEPTION to outputs/ rule)
- **`templates/` folder** - Reusable starting templates for common deliverables

---

## 🎨 Skills & Advanced Capabilities

### Overview

All **17 MARKETING_TEAM agents** now have access to **17 powerful skills** (13 user-installed + 4 document-skills) and **7 MCP servers**, dramatically expanding their capabilities for visual creation, interactive development, document processing, and external integrations.

**Skills Configuration:** Enabled in `MARKETING_TEAM/.claude/settings.json`
**MCPs:** Inherited from root `.claude.json` via `"mcpServers": "inherit"`

---

### Available Skills (17 total)

#### Visual Creation Skills (4)

| Skill | Description | Best For | Example |
|-------|-------------|----------|---------|
| **algorithmic-art** | Generative art with p5.js (flow fields, particle systems, geometric patterns) | Unique social media visuals, abstract art, distinctive brand art | `"Use visual-designer with algorithmic-art to create flow field art"` |
| **canvas-design** | Beautiful PNG/PDF visual art (posters, banners, designs) | Conference posters, print materials, professional designs | `"Use visual-designer with canvas-design to create a conference poster"` |
| **slack-gif-creator** | Animated GIFs optimized for Slack with size validators | Product launches, animated content, eye-catching posts | `"Use social-media-manager with slack-gif-creator to make launch GIF"` |
| **theme-factory** | 11 preset themes for consistent branding (vibrant, modern-minimalist, midnight-galaxy, golden-hour, tech-innovation, botanical-garden, arctic-frost, forest-canopy, ocean-depths, desert-rose, sunset-boulevard) | Themed presentations, branded landing pages, consistent artifacts | `"Use presentation-designer with theme-factory 'vibrant' theme"` |

#### Development & Artifacts Skills (3)

| Skill | Description | Best For | Example |
|-------|-------------|----------|---------|
| **artifacts-builder** | Complex React/Tailwind/shadcn/ui multi-component apps | Interactive landing pages, state-managed interfaces, modern web apps | `"Use landing-page-specialist with artifacts-builder to build landing page"` |
| **mcp-builder** | Create MCP servers (Python FastMCP or Node/TypeScript SDK) | Custom API integrations, tool creation, service connectors | `"Use mcp-builder to create MCP server for our CRM API"` |
| **skill-creator** | Create custom skills to extend Claude's capabilities | Domain-specific skills, specialized workflows, knowledge integration | `"Use skill-creator to design a legal marketing compliance skill"` |

#### Content & Document Skills (3)

| Skill | Description | Best For | Example |
|-------|-------------|----------|---------|
| **internal-comms** | Company-standard formats (status reports, newsletters, FAQs, incident reports) | Internal communications, structured reports, team updates | `"Use copywriter with internal-comms to write Q1 status report"` |
| **brand-guidelines** | Anthropic's official brand colors & typography | Anthropic-branded materials, official documents | `"Use presentation-designer with brand-guidelines for Anthropic deck"` |
| **pdf-filler** | Fill PDF forms, create fillable PDFs with form fields | Registration forms, surveys, applications, contracts | `"Use pdf-specialist with pdf-filler to create registration form PDF"` |

#### Document Creation Skills (4) - Claude Code Built-in

| Skill | Description | Best For | Example |
|-------|-------------|----------|---------|
| **pptx** | PowerPoint creation with html2pptx & PptxGenJS workflows | Professional presentations, pitch decks, marketing slides | `"Use presentation-designer with pptx skill for PowerPoint"` |
| **pdf** | PDF generation with forms, layouts, and styling | Whitepapers, reports, fillable forms | `"Use pdf-specialist with pdf skill to create report"` |
| **xlsx** | Excel spreadsheet creation with formulas & formatting | Data reports, financial models, dashboards | `"Create Excel report with xlsx skill"` |
| **docx** | Word document creation with styles & formatting | Documentation, contracts, proposals | `"Create Word document with docx skill"` |

**Note:** These are built-in Claude Code skills (always available). The pdf-filler skill listed above is a separate user-installed skill for form filling.

#### Integration Skills (3)

| Skill | Description | Best For | Example |
|-------|-------------|----------|---------|
| **filesystem** | File operations with C:\ and C:\Users access | Local file management, reading assets, batch processing | `"Use research-agent with filesystem to read competitor PDFs"` |
| **figma** | Extract designs, components, assets from Figma files | Design handoff, brand asset extraction, Figma-to-code | `"Use visual-designer with figma to extract brand assets from [URL]"` |
| **context7** | Enhanced context management (automatic) | Long conversations, complex tasks, context preservation | Automatic - works in background |

---

### Available MCP Servers (7 total)

| MCP Server | Purpose | Key Tools | Best For |
|------------|---------|-----------|----------|
| **playwright** | Browser automation | navigate, screenshot, click, fill, evaluate, get_visible_text | Competitive research, website analysis, web scraping |
| **google-workspace** | Gmail, Drive, Docs, Sheets, Calendar, Forms, Tasks | send_gmail_message, create_drive_file, upload_to_drive, create_doc, create_event, search_drive_files | Email automation, Drive uploads, document management, calendar scheduling |
| **perplexity** | Web search & research with citations | perplexity_ask, perplexity_reason, perplexity_search, perplexity_research | Market research, competitive intelligence, citation-backed insights |
| **bright-data** | Web scraping & lead generation (5,000 free requests/month) | search_engine, scrape_as_markdown, search_engine_batch, scrape_batch | B2B lead gen, SERP scraping, competitor analysis |
| **n8n-mcp** | Workflow automation (400+ integrations) | list_workflows, trigger_workflow, get_execution | Campaign orchestration, automated workflows |
| **sequential-thinking** | Structured step-by-step reasoning | sequentialthinking | Complex problem-solving, strategic planning |
| **marketing-tools** | Custom MCP for OpenAI APIs | generate_gpt4o_image, generate_sora_video | GPT-4o image generation, Sora video creation |

---

### Skills by Agent

**Which agents use which skills:**

#### Visual & Creative Agents
- **visual-designer:** algorithmic-art, canvas-design, theme-factory, figma
- **social-media-manager:** algorithmic-art, slack-gif-creator, canvas-design
- **presentation-designer:** pptx, theme-factory, artifacts-builder, canvas-design
- **video-producer:** *(No skills - uses marketing-tools MCP directly)*

#### Content & Strategy Agents
- **copywriter:** internal-comms, docx
- **landing-page-specialist:** artifacts-builder, theme-factory
- **pdf-specialist:** pdf-filler, canvas-design, pdf
- **email-specialist:** *(No skills)*
- **editor:** *(No skills)*
- **gmail-agent:** *(No skills)*

#### Research & Analysis Agents
- **research-agent:** filesystem
- **seo-specialist:** filesystem, xlsx
- **lead-gen-agent:** filesystem, xlsx
- **analyst:** filesystem, xlsx

#### Orchestration Agents
- **router-agent:** context7
- **content-strategist:** context7
- **automation-agent:** context7

**Note:** All agents inherit access to all 17 skills via MARKETING_TEAM/.claude/settings.json, but the above lists show which skills each agent is designed to use based on their agent definitions.

---

### Agent MCP Tools Reference

**Which agents use which MCP servers:**

#### marketing-tools MCP (OpenAI APIs)
- **visual-designer** - generate_gpt4o_image
- **social-media-manager** - generate_gpt4o_image
- **video-producer** - generate_sora_video
- **presentation-designer** - generate_gpt4o_image

#### google-workspace MCP (Gmail, Drive, Docs, Sheets, Calendar)
- **All agents** can use google-workspace tools when needed
- **Primary users:**
  - **gmail-agent** - send_gmail_message, search_gmail_messages, get_gmail_message_content
  - **email-specialist** - send_gmail_message, create_doc
  - **copywriter** - create_doc, update_doc
  - **visual-designer** - create_drive_file (file uploads)
  - **presentation-designer** - create_drive_file (file uploads)
  - **pdf-specialist** - create_doc, create_drive_file
  - **landing-page-specialist** - create_doc, upload_to_drive
  - **seo-specialist** - Spreadsheet operations
  - **research-agent** - create_doc
  - **lead-gen-agent** - Spreadsheet operations, create_drive_file
  - **analyst** - Spreadsheet operations, create_doc
  - **editor** - get_doc_content, modify_doc_text, create_doc
  - **content-strategist** - create_event, create_spreadsheet, create_doc

#### perplexity MCP (Web Search & Research) + Custom Research Tools

**🔥 HYBRID APPROACH:** research-agent uses BOTH custom Python tools AND MCP tools

**Custom Perplexity Tools (Primary):**
- **research-agent** - `conduct_research()`, `quick_research()`, `strategic_analysis()` (marketing-optimized)
- **seo-specialist** - Can use custom tools via import
- **copywriter** - Can use custom tools for research
- **content-strategist** - Can use custom tools for strategic planning

**Working MCP Tools (Backup & Specialized):**
- ✅ **mcp__perplexity__perplexity_ask** - Conversational search (all agents)
- ✅ **mcp__perplexity__perplexity_reason** - Reasoning analysis (all agents)
- ✅ **mcp__perplexity__perplexity_search** - Web search/SERP results (all agents)
- ❌ **mcp__perplexity__perplexity_research** - BROKEN (replaced by `conduct_research`)

**Strategy:** Use custom tools for comprehensive research, MCP tools for lightweight queries and backup

#### bright-data MCP (Web Scraping & Lead Generation)
- **research-agent** - search_engine, scrape_as_markdown
- **seo-specialist** - search_engine, scrape_as_markdown
- **lead-gen-agent** - All bright-data tools (60+ scrapers)
- **landing-page-specialist** - All bright-data tools
- **analyst** - search_engine, scrape_as_markdown

#### playwright MCP (Browser Automation)
- **seo-specialist** - navigate, screenshot, click, fill, get_visible_text
- **research-agent** - navigate, screenshot, evaluate, get_visible_html

#### sequential-thinking MCP (Structured Reasoning)
- **router-agent** - sequentialthinking
- **content-strategist** - sequentialthinking
- **automation-agent** - sequentialthinking

#### n8n-mcp (Workflow Automation)
- **automation-agent** - All n8n-mcp tools (list_workflows, create_workflow, update_workflow, trigger_workflow, get_execution, list_credentials)
- Available to all agents but primarily used by automation-agent for marketing workflow orchestration

---

### Quick Examples

#### Generate Unique Social Media Art
```
"Use visual-designer with algorithmic-art to create a flow field design
with brand colors (#FF5733, #3498DB) for Instagram. 1080x1080px."
```

#### Build Interactive React Landing Page
```
"Use landing-page-specialist with artifacts-builder to build a responsive
landing page with hero section, features, testimonials, and contact form.
Apply theme-factory 'modern' theme."
```

#### Create Themed Presentation
```
"Use presentation-designer with theme-factory to create a 15-slide sales
deck with the 'professional' theme."
```

#### Generate Animated GIF
```
"Use social-media-manager with slack-gif-creator to make a 3-second
'NEW FEATURE' announcement GIF with our brand colors."
```

#### Extract Figma Designs
```
"Use visual-designer with figma to extract designs from [Figma URL] and
implement the landing page with artifacts-builder."
```

#### Create Fillable PDF Form
```
"Use pdf-specialist with pdf-filler to create a fillable registration form
PDF with fields for name, email, company, title, and signature."
```

#### Write Internal Status Report
```
"Use copywriter with internal-comms to write a Q1 marketing status report
including metrics, wins, challenges, and Q2 preview."
```

#### Find B2B Leads
```
"Use lead-gen-agent with bright-data to find 50 B2B SaaS companies in
San Francisco with 50-200 employees."
```

#### Comprehensive Research (Custom Tool)
```
"Use research-agent to conduct comprehensive research on AI marketing automation
trends in 2025. Include adoption rates, ROI data, and top tools."

# Uses conduct_research() - returns 2000-4000 word formatted report with citations
```

#### Quick Stat Lookup (MCP Tool)
```
"Use research-agent to get the average email open rate for B2B SaaS"

# Uses mcp__perplexity__perplexity_ask - fast, lightweight
```

#### Strategic Analysis (Custom Tool)
```
"Use research-agent to analyze whether we should invest in multi-agent AI
vs traditional marketing automation. Include strategic comparison."

# Uses strategic_analysis() - deep reasoning with visible thinking
```

#### Automate Browser Tasks
```
"Use research-agent with playwright to navigate to competitor-site.com,
screenshot the homepage, and extract their headline and CTA copy."
```

---

### Complete Documentation

For comprehensive guides, examples, and workflows:

- **[MARKETING_TEAM/docs/guides/skills-and-mcp-guide.md](MARKETING_TEAM/docs/guides/skills-and-mcp-guide.md)** - 50+ page complete reference with detailed examples
- **[MARKETING_TEAM/docs/SKILLS_QUICK_REFERENCE.md](MARKETING_TEAM/docs/SKILLS_QUICK_REFERENCE.md)** - Quick lookup tables and cheat sheets
- **[MARKETING_TEAM/README.md](MARKETING_TEAM/README.md)** - Marketing team overview with skills

---

## ⚙️ Configuration & Setup

### Environment Variables

**USER_STORY_AGENT:**
```bash
# USER_STORY_AGENT/.env
ANTHROPIC_API_KEY=your_anthropic_key_here
```

**MARKETING_TEAM:**
```bash
# MARKETING_TEAM/.env
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here          # For GPT-4o images and Sora videos

# Optional (for email/drive features)
# Gmail and Google Drive credentials are OAuth-based
# See MARKETING_TEAM/docs/getting-started/api-setup.md
```

### MCP Server Configuration

**Configuration Files:**
- **Template:** `.claude.json.example` or `.mcp.json.example` (tracked in git)
- **Your Config:** `.claude.json` or `.mcp.json` (gitignored - contains your real API keys)

**Setup Steps:**
1. Copy the template: `cp .mcp.json.example .mcp.json`
2. Edit `.mcp.json` and add your real API keys
3. The config file stays local (never committed to git)

**Available MCP Servers:**

| Server | Purpose | Tools Provided |
|--------|---------|----------------|
| **playwright** | Browser automation for research | Navigate, screenshot, click, fill forms, evaluate JS |
| **perplexity** | Web search and research | `perplexity_ask`, `perplexity_reason`, `perplexity_search`, `perplexity_research` |
| **google-workspace** | Gmail, Drive, Docs, Sheets, Calendar | Send emails, upload files, create docs/sheets, schedule events, manage Drive |
| **bright-data** | ✨ **NEW** Web scraping & lead generation | 60+ scrapers (LinkedIn, Google Maps, directories, SERP) |
| **n8n-mcp** | Workflow automation | Trigger n8n workflows, connect to 400+ integrations |
| **sequential-thinking** | ✨ **NEW** Structured reasoning | Step-by-step problem decomposition, logical reasoning |
| **fetch** | ✨ **NEW** HTTP requests | Web content retrieval, API calls, file downloads |

**Configuration Example (`.mcp.json`):**
See `.mcp.json.example` for the full template with placeholder values.

**Install MCP Servers:**
```bash
# Playwright (browser automation)
npx playwright install chromium

# Google Workspace (Gmail, Drive, Calendar, Docs, Sheets, etc.)
pip install workspace-mcp

# Perplexity, Bright Data, n8n, Sequential Thinking, and Fetch are auto-installed via npx when first used
```

**Security Note:**
- `.mcp.json` and `.claude.json` contain real API keys and are gitignored
- Never commit these files to version control
- Use `.example` templates to share configuration structure without exposing secrets

---

## 🔒 Security Best Practices

### API Key Management
- **Never commit real API keys** to git repositories
- Store keys in local config files (`.env`, `.mcp.json`, `.claude.json`)
- All sensitive config files are gitignored automatically
- Use `.example` templates to document configuration structure

### Configuration File Security
**Local-only files (gitignored):**
- `.mcp.json` - MCP server configurations with real API keys
- `.claude.json` - Claude Code settings with credentials
- `.env` - Environment variables with API keys
- `credentials.json`, `token.pickle` - OAuth tokens for Google services

**Template files (tracked in git):**
- `.mcp.json.example` - MCP configuration template
- `.claude.json.example` - Claude Code settings template
- `.env.example` - Environment variables template

### If You Accidentally Commit Secrets
1. Remove from git tracking: `git rm --cached .mcp.json`
2. Commit the removal: `git commit -m "Remove secrets from tracking"`
3. Force push to rewrite history: `git push --force-with-lease`
4. **Rotate the exposed API keys immediately**
5. Verify `.gitignore` includes the file

### Perplexity MCP Capabilities
The Perplexity MCP server provides four tools for web research:
- **`perplexity_ask`** ✅ - Conversational search with citations (working)
- **`perplexity_reason`** ✅ - Deep reasoning and comparative analysis (working)
- **`perplexity_search`** - Ranked web search results (requires newer API key)
- **`perplexity_research`** - Comprehensive research reports (may require specific plan)

**Usage:**
```
"Use Perplexity to search for the latest AI trends"
"Use Perplexity reasoning to compare multi-agent vs monolithic systems"
```

## 🧠 Memory System - How It Works

**Automatic Configuration Loading:**

All 17 MARKETING_TEAM agents are instructed in their agent definitions to read memory configuration files at the start of each task. This ensures:
- ✅ Consistent email addresses across all email operations (no hardcoding)
- ✅ Consistent Drive folder structure for uploads (no hardcoded folder IDs)
- ✅ Consistent brand voice and visual guidelines (no style drift)
- ✅ Single source of truth for configuration (update once, affects all agents)

**How Agents Access Memory:**

1. **Agent Definition Includes Configuration Section** - Each agent's `.claude/agents/*.md` file contains a "⚙️ Configuration Files (READ FIRST)" section
2. **Explicit Instructions to Read Files** - Section lists which memory files to read and when to use them
3. **Agent Reads Files at Task Start** - Agent uses Read tool or filesystem skill to load configuration
4. **Agent Uses Configuration Throughout Task** - Configuration values used instead of hardcoded defaults

**Example from gmail-agent.md:**
```markdown
## ⚙️ Configuration Files (READ FIRST)

**ALWAYS read these memory files before starting work:**

1. **memory/email_config.json** - Email defaults (CRITICAL for ALL email operations)
   - Contains: `user_google_email`, `default_to`, `default_cc`
   - Used when: Sending emails, creating drafts, searching messages
   - Required for: ALL Google Workspace MCP email tools
```

---

### Configuration Files in memory/

**Memory files provide centralized configuration for all agents:**

**Email Configuration (MARKETING_TEAM/memory/email_config.json):**
```json
{
  "user_google_email": "sabaazeez12@gmail.com",
  "default_to": "sabaazeez12@gmail.com",
  "default_cc": "aoseni@duxvitaecapital.com"
}
```

**Google Drive Configuration (MARKETING_TEAM/memory/google_drive_config.json):**
```json
{
  "user_google_email": "sabaazeez12@gmail.com",
  "folders": {
    "ai_marketing_team": "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv",
    "videos": "1EMk6waLu87DmLaI4LrxoBvpYSdFzy42q",
    "images": "12DaX0JJ5K6_os1ANj6FgovF72ymdson1",
    "social_media": "1mFHE1aKOIzhxL3BmIC593WfNt5G1GBxi",
    "lead_gen": "1G5AQYEcKv_kKUMfr8QgPVAlkcMjvhEB_"
  },
  "upload_defaults": {
    "presentations": "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv",
    "documents": "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv",
    "images": "12DaX0JJ5K6_os1ANj6FgovF72ymdson1",
    "videos": "1EMk6waLu87DmLaI4LrxoBvpYSdFzy42q",
    "leads": "1G5AQYEcKv_kKUMfr8QgPVAlkcMjvhEB_"
  }
}
```

**Brand Voice (MARKETING_TEAM/memory/brand_voice.json):**
- Tone, style, keywords, avoid-words, writing guidelines
- Read by: copywriter, social-media-manager, email-specialist
- Ensures consistent brand voice across all content

**Visual Guidelines (MARKETING_TEAM/memory/visual_guidelines.json):**
- Brand colors, fonts, image styles, design preferences
- Read by: visual-designer, presentation-designer, pdf-specialist
- Ensures consistent visual identity

**Docs Folder Structure (MARKETING_TEAM/memory/docs_folder_structure.json):**
- Documentation organization rules for AI assistants
- Read by: AI assistants (Claude Code, Cursor, etc.) creating documentation
- NOT for marketing agents - for codebase maintenance only

**IMPORTANT - How Agents Use Memory:**
- ✅ All agents sending emails → Read `email_config.json` for user_google_email, default_to, default_cc
- ✅ All agents uploading to Drive → Read `google_drive_config.json` for folder IDs
- ✅ Content agents → Read `brand_voice.json` for tone and style
- ✅ Visual agents → Read `visual_guidelines.json` for brand colors and fonts
- ✅ AI assistants → Read `docs_folder_structure.json` when creating docs

---

### Google Drive Upload Strategy

**⚠️ CRITICAL: MCP is BROKEN for Binary File Uploads**

Google Workspace MCP's `create_drive_file` has a critical bug: it creates 116-byte placeholder files instead of uploading actual binary content. Test confirmed PPTX file (26 KB) uploaded as only 116 bytes.

**PRIMARY METHOD: Use Python Tool (Reliable)**

✅ **ALL File Types (Recommended):**
- Use `tools/upload_to_drive.py` (Python Drive API) - **PRIMARY METHOD**
- Uses `token_drive.pickle` (separate authentication from Gmail)
- Handles all file uploads: PPTX, PDF, XLSX, PNG, MP4, HTML, DOCX, etc.
- Auto-detects MIME types from file extensions
- **Always read folder IDs from memory/google_drive_config.json**
- Verified working with full file content

**Usage Example:**
```python
from tools.upload_to_drive import upload_to_drive

result = upload_to_drive(
    file_path="outputs/presentations/deck.pptx",
    file_name="My Presentation.pptx",
    folder_id="1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv"  # From google_drive_config.json
)
# Returns: {'file_id': '...', 'file_name': '...', 'web_view_link': '...'}
```

**❌ AVOID: MCP for Binary Files**
- `mcp__google-workspace__create_drive_file` - **DO NOT USE for binary files**
- Creates placeholder files (116 bytes) instead of uploading actual content
- Fails silently - returns "success" but file is unusable
- Only safe for Google Workspace text documents (Docs, Sheets, Forms created from text)

---

### Email Sending Strategy

**Two approaches based on attachment needs:**

**Without Attachments:**
- Use `mcp__google-workspace__send_gmail_message` (Google Workspace MCP tool)
- Fast and simple, already authenticated through MCP
- Perfect for text-only emails
- No file size limitations for body content
- **Always use user_google_email from email_config.json**
- **Set `body_format='html'`** for proper line break rendering
- Convert plaintext to HTML before sending (see gmail-agent.md Workflow 1)

**With Attachments:**
- Use `tools/send_email_with_attachment.py` (Python Gmail API)
- Supports file attachments via MIME multipart messages
- Handles base64 encoding automatically
- Requires full Gmail API scope authentication
- Recommended for files under 25 MB
- **Automatically converts plaintext to HTML** for proper formatting

**Email Formatting Rules (always apply):**
- Clean plaintext body - No markdown symbols (no ##, **, ---, etc.)
- Professional formatting with proper spacing and clear hierarchy
- Use bullet points with • character instead of markdown lists
- Section headers in UPPERCASE for emphasis
- Concise, organized structure with greeting and closing
- Business-appropriate tone

**HTML Email Rendering (ALL EMAILS):**
- Both MCP and Python tools now send HTML emails
- **UPPERCASE headers automatically bolded** (e.g., "DOCUMENT OVERVIEW" → **DOCUMENT OVERVIEW**)
- Line breaks (`\n`) rendered as `<br>` tags
- Double line breaks (`\n\n`) rendered as paragraph breaks (`<br><br>`)
- Professional styling: Arial/Calibri, 11pt, line-height 1.5
- No more "wall of text" formatting issues

**Example Clean Email Body:**
```
Hi,

Here's the landing page we created today.

LANDING PAGE OVERVIEW

Platform: AI InvestIQ
Purpose: Investment intelligence platform

KEY FEATURES

The page includes:

• Hero section with compelling stats
• 6 feature cards explaining benefits
• Social proof with testimonials

File is attached and ready to deploy.

Best regards
```

---

### Dependencies Overview

**USER_STORY_AGENT:**
```bash
cd USER_STORY_AGENT
pip install -r requirements.txt
# streamlit, anthropic, pandas, openpyxl, python-docx, PyPDF2, pytesseract
```

**MARKETING_TEAM:**
```bash
cd MARKETING_TEAM
pip install -r requirements.txt
# anthropic, openai, google-auth, google-api-python-client, python-pptx, fpdf
```

**TEST_AGENT:**
```bash
cd TEST_AGENT
pip install -r requirements.txt
# pytest, pytest-cov, pytest-asyncio, pytest-mock, anthropic
```

---

## 🚀 Quick Start Examples

### Generate User Stories
```bash
cd USER_STORY_AGENT
streamlit run app_ui.py
# Upload notes → Choose format → Generate → Download Excel
```

### Create Marketing Content
```
Talk to Claude Code:

"Use the copywriter subagent to write a 2000-word blog about AI automation"
"Use the social-media-manager to create a LinkedIn post about our product"
"Use the visual-designer to create a header image for LinkedIn"
"Use the router-agent to plan a complete product launch campaign"
```

### Generate Tests
```
Talk to Claude Code:

"Use the test-orchestrator to scan USER_STORY_AGENT and generate comprehensive tests"
"Use the unit-test-agent to generate tests for story_generator.py"
"Use the edge-case-agent to identify edge cases in file validation"
```

---

## 🎯 Common Use Cases

### User Story Generation
**Goal:** Convert meeting notes to Excel user stories
**System:** USER_STORY_AGENT
**Steps:**
1. Launch Streamlit: `streamlit run app_ui.py`
2. Upload notes (PDF, DOCX, TXT, images, etc.)
3. Choose AC format (Gherkin or Explicit/Detailed)
4. Optionally enable browser research mode
5. Generate and download Excel

### Marketing Campaign
**Goal:** Create a complete social media campaign
**System:** MARKETING_TEAM
**Agent:** router-agent or content-strategist
**Steps:**
1. Talk to Claude Code: `"Use router-agent to create a social media campaign for [product]"`
2. Router coordinates: copywriter → social-media-manager → visual-designer → email-specialist
3. All content saved to `outputs/` folders
4. Optionally upload to Google Drive with Google Workspace MCP

### Test Suite Generation
**Goal:** Generate comprehensive pytest test suite
**System:** TEST_AGENT
**Agent:** test-orchestrator
**Steps:**
1. Talk to Claude Code: `"Use test-orchestrator to scan [folder] and generate tests"`
2. Orchestrator scans codebase
3. Delegates to unit-test-agent, edge-case-agent, fixture-agent
4. Generates tests in `tests/` folder
5. Run: `pytest tests/ --cov`

---

## 📞 Support & Resources

- **Claude Code Documentation:** https://docs.claude.com/claude-code
- **Anthropic API Docs:** https://docs.anthropic.com
- **OpenAI API Docs:** https://platform.openai.com/docs
- **Playwright MCP:** https://github.com/executeautomation/playwright-mcp-server

---

## 🔍 Tips for AI Assistants

**When working with this codebase:**

1. **Check this file first** - It's your navigation guide
2. **Read agent definitions** - They contain the specialized instructions
3. **Follow the documentation map** - Links to all key docs
4. **Respect .gitignore** - Don't track outputs, credentials, or artifacts
5. **Use the multi-agent system** - Invoke specialized agents for complex tasks
6. **Refer to MULTI_AGENT_GUIDE.md** - Master guide for all 20 agents

**Common patterns:**
- Each system has a README.md with quick start
- Agent definitions are in `.claude/agents/` folders
- Tools are in `tools/` folders
- Generated content goes to `outputs/` (gitignored)
- Docs are in `docs/` folders or root-level `.md` files

---

## 📝 Notes

### About Archived Files
You'll find `archive/` folders with old `orchestrator.py` files. These were early attempts to create Python orchestrators. **They're not needed anymore** because:
- Claude Code reads agent definitions directly
- No Python orchestrator required
- Simpler and more powerful to just talk to Claude

### About Memory/Preferences

**All agents automatically read memory configuration files** - See "🧠 Memory System - How It Works" section above for complete details.

**Memory files (MARKETING_TEAM/memory/):**
- `email_config.json` - Email defaults (read by ALL agents sending emails)
- `google_drive_config.json` - Drive folder IDs (read by ALL agents uploading files)
- `brand_voice.json` - Brand voice guidelines (read by content agents)
- `visual_guidelines.json` - Design standards (read by visual agents)
- `docs_folder_structure.json` - Docs organization (AI assistants only)
- `learned_patterns.json` - Test generation patterns (TEST_AGENT)
- `preferences_store.json` - User preferences (USER_STORY_AGENT)

**How it works:** Each agent's `.claude/agents/*.md` file includes a "⚙️ Configuration Files (READ FIRST)" section with explicit instructions to read relevant memory files at task start. This ensures consistency across all agents without hardcoding configuration.

**These files are gitignored and local-only** (never committed to version control).

---

**Last Updated:** 2025-10-22
**Recent Changes:**
- ✨ **ENGINEERING SUPER TEAM CREATED** - 12 engineering agents (30 → **35 agents total**)
  - **Core 7 Agents (Custom Built):**
    - ⭐ **devops-engineer:** UPGRADED with official production-ready template - 886 lines of battle-tested CI/CD (GitHub Actions), Terraform (AWS EKS, RDS, Redis, ALB), Kubernetes (Helm charts), monitoring (Prometheus/Grafana), security scanning (Trivy, kube-bench, gitleaks)
    - ⭐ **frontend-developer:** REPLACED with official template - React components, responsive design (Tailwind), state management, performance optimization, accessibility (WCAG)
    - ⭐ **backend-architect:** NEW official template - RESTful API design, microservices architecture, database schema, caching strategies, scalability planning
    - ⭐ **ai-engineer:** NEW - LLM integration (OpenAI/Anthropic), RAG systems (vector DBs), prompt optimization, agent frameworks (LangChain/LangGraph), token management - **PERFECT for optimizing all 35 AI agents!**
    - ⭐ **ui-ux-designer:** NEW - User research, wireframes, design systems, accessibility, user flows, usability testing - **Complements frontend-developer for complete Design → Develop workflow**
    - ✅ **security-auditor:** KEPT custom version - Comprehensive code security analysis, vulnerability scanning (OWASP Top 10), compliance audits (GDPR/HIPAA)
    - ✅ **technical-writer:** KEPT custom version - PRDs, technical specs, API docs (OpenAPI), architecture diagrams, user guides
  - **Specialist 5 Agents (From aitmpl.com - Community Validated):**
    - ⭐ **code-reviewer:** Quality, security, maintainability reviews - automatic git diff analysis (3.2K community downloads)
    - ⭐ **test-engineer:** Test automation (Jest, Playwright, pytest), QA strategy, CI/CD testing (1.3K downloads)
    - ⭐ **prompt-engineer:** LLM prompt optimization, techniques (few-shot, chain-of-thought), benchmarking (2.4K downloads) - **Can optimize all 35 agents!**
    - ⭐ **database-architect:** Database design, data modeling, scalability (sharding, replication), polyglot persistence (1.2K downloads)
    - ⭐ **debugger:** Root cause analysis, troubleshooting, error investigation, hypothesis testing (1.7K downloads)
  - **Full workspace access:** All 12 engineering agents can work with MARKETING_TEAM, TEST_AGENT, USER_STORY_AGENT
  - **Cross-team collaboration:** DevOps deploys all systems, AI Engineer + Prompt Engineer optimize all 35 agents, Security + Code Reviewer audit everything, Database Architect designs unified analytics
  - **End-to-end workflows:** PRD (technical-writer) → Wireframes (ui-ux-designer) → API (backend-architect) → UI (frontend-developer) → Tests (test-engineer) → Review (code-reviewer) → Deploy (devops-engineer) → Audit (security-auditor) → AI Features (ai-engineer) → Prompt Optimization (prompt-engineer) → Debug (debugger)
  - See [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) for complete guide with production-ready code examples
- ✨ **NEW automation-agent** - 17th marketing agent for n8n workflow automation & orchestration
  - Process discovery, workflow architecture, n8n node mapping
  - Automation QA, testing, and iteration
  - Cross-tool orchestration with marketing platforms (CRM, email, ads, analytics)
  - Uses n8n-mcp tools + sequential-thinking for complex workflow planning
  - Memory system integration (reads email_config, google_drive_config, brand_voice)
  - Outputs to `MARKETING_TEAM/outputs/automation/` folder
- 🧠 **MEMORY SYSTEM STANDARDIZATION** - All 17 marketing agents now have standardized memory configuration
  - Added "⚙️ Configuration Files (READ FIRST)" section to ALL agent definitions
  - Ensures automatic reading of email_config.json, google_drive_config.json, brand_voice.json, visual_guidelines.json
  - Eliminates hardcoded email addresses and folder IDs across all agents
  - Single source of truth for configuration - update memory files, all agents benefit
  - See "🧠 Memory System - How It Works" section in CLAUDE.md for complete explanation
- 🔥 **HYBRID Perplexity Research** - Custom Python tools + MCP tools for research-agent (maximum reliability)
  - 3 custom tools: `conduct_research()`, `quick_research()`, `strategic_analysis()`
  - Kept 3 working MCP tools: `perplexity_ask`, `perplexity_reason`, `perplexity_search`
  - Redundancy strategy: if custom fails → fallback to MCP
  - See [PERPLEXITY_RESEARCH_TOOLS.md](MARKETING_TEAM/docs/guides/PERPLEXITY_RESEARCH_TOOLS.md)
- ✨ **lead-gen-agent** - B2B/local lead generation with Bright Data MCP (5,000 free requests/month)
- ✨ **MCP servers** - sequential-thinking and fetch for enhanced capabilities
- **Enhanced agents** - research-agent (hybrid research), seo-specialist, analyst, landing-page-specialist
- **NEW tool** - send_marketing_team_doc.py for documentation email automation
- Updated all documentation to reflect 35 agents (4 systems: MARKETING_TEAM (17), TEST_AGENT (5), USER_STORY_AGENT (1), ENGINEERING_TEAM (12))

**Repository:** https://github.com/Azeez1/TEST_AGENTS
**License:** Uses Anthropic Claude API - see Anthropic's terms of service
