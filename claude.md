# TEST_AGENTS - AI Multi-Agent System Repository

## 📋 Repository Overview

This repository contains **4 autonomous AI agent systems** powered by the Claude Agent SDK, featuring **37 specialized agents** for user story generation, marketing automation, test generation, software engineering, quality assurance, and AI/ML development.

**Systems:**
- **USER_STORY_AGENT** (1) - Transform meeting notes into backlog-ready user stories with Excel export
- **MARKETING_TEAM** (17) - Content creation, social media, images, videos, emails, lead generation, landing pages, workflow automation
- **QA_TEAM** (5) - Automated pytest test suite generation
- **ENGINEERING_TEAM** (14) ⭐ **SUPER TEAM** - CTO coordinator + 13 specialists (DevOps, security, frontend, backend, AI/ML, UX, architecture, QA, testing, optimization, database, troubleshooting)

All agents work through natural conversation with Claude Code - no Python orchestrators needed.

**⚡ Key Facts:**
- 37 autonomous agents across 4 systems
- 18 powerful skills (visual, development, documents, integration)
- 7 MCP servers (Google Workspace, Perplexity, Playwright, Bright Data, n8n, etc.)
- Memory system with automatic configuration loading
- No Python orchestrators - pure Claude Code conversation

### 🔍 Quick Navigation

**🚀 Getting Started:**
- [Use Existing Tools First](#️-critical-use-existing-tools-first) - Priority order for AI assistants
- [Agent Invocation Guidelines](#-agent-invocation-guidelines-for-ai-assistants) - How to invoke agents properly
- [Complete Agent Directory](#-complete-agent-directory) - All 37 agents at a glance
- [Quick Start Examples](#-quick-start-examples) - Common workflows

**📚 Key Resources:**
- [Project Structure](#-project-structure) - Repository layout
- [Skills & MCP Capabilities](#-skills--advanced-capabilities) - 18 skills + 7 MCP servers
- [Configuration & Setup](#️-configuration--setup) - API keys, MCP servers
- [Memory System](#-memory-system---how-it-works) - Automatic configuration loading
- [Documentation Map](#-documentation-map) - All guides and references

**🛠️ For Developers:**
- [Development Guidelines](#️-development-guidelines) - Multi-agent system, coding standards
- [Tools vs Scripts](#tools-vs-scripts-organization) - Organization patterns
- [Git Workflow](#git-workflow) - What's tracked, what's ignored

---

## ⚠️ CRITICAL: Use Existing Tools First

**IMPORTANT INSTRUCTION FOR ALL AI ASSISTANTS:**

When working with this repository, **ALWAYS use existing agents, tools, skills, and MCP servers FIRST**. Do NOT create new implementations when functionality already exists.

**Priority Order:**
1. **Use existing agents** (`.claude/agents/*.md` files) - Invoke them explicitly
2. **Use installed skills** (`.claude/skills/*`) - 18 powerful skills available
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

**See "🤖 Agent Invocation Guidelines" below for how to properly invoke agents without over-specification.**

---

## 🤖 Agent Invocation Guidelines

**Pattern:** `"Use [agent-name] to [goal] with [context]"` - Agents are autonomous and know which tools to use.

📖 **Complete Guide:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - Proper invocation patterns, troubleshooting, and anti-patterns

---

## 🚀 System Quick Start

| System | Launch | Documentation |
|--------|--------|---------------|
| **USER_STORY_AGENT** | `streamlit run app_ui.py` | [README](USER_STORY_AGENT/README.md) |
| **MARKETING_TEAM** | Talk to agents via Claude Code | [README](MARKETING_TEAM/README.md) |
| **QA_TEAM** | Talk to agents via Claude Code | [README](QA_TEAM/README.md) |
| **ENGINEERING_TEAM** | Talk to agents via Claude Code | [README](ENGINEERING_TEAM/README.md) |

**📚 Master Guides:** [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) • [MCP_SETUP.md](MCP_SETUP.md) • [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 📁 Project Structure

```
TEST_AGENTS/
├── claude.md                        ← YOU ARE HERE
├── MULTI_AGENT_GUIDE.md             ← Master guide for all 37 agents
├── AGENT_INVOCATION_BEST_PRACTICES.md  ← Agent invocation patterns
├── MEMORY_SYSTEM.md                 ← Memory/Drive/Email strategies
├── MCP_SETUP.md, IMPLEMENTATION_SUMMARY.md
│
│
├── MARKETING_TEAM/                  ← 17 agents + tools + docs (see README.md)
│   ├── .claude/agents/              ← 17 marketing agent definitions
│   ├── tools/                       ← GPT-4o images, Sora videos, Gmail, Drive
│   ├── outputs/                     ← Generated content (gitignored)
│   ├── examples/, templates/        ← Reference materials (git-tracked)
│   └── docs/                        ← Complete documentation
│
├── QA_TEAM/                         ← 5 testing agents (see README.md)
│   ├── .claude/agents/              ← test-orchestrator + 4 specialists
│   └── tools/                       ← Test generation, coverage analysis
│
└── ENGINEERING_TEAM/                ← 14 agents: CTO + 13 specialists (see README.md)
    ├── .claude/agents/              ← DevOps, security, frontend, backend, AI, etc.
    └── docs/                        ← PRDs, technical specs, deployment guides
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
| **editor** | **Dux Machina brand voice enforcement** - Automatically reviews ALL content (blogs, posts, emails, landing pages, presentations, PDFs) for tone score 7+, checks 5 voice principles, flags anti-patterns | **Automatic** - content agents invoke editor themselves (or manual: `"Use editor to review this content"`) |
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

### QA_TEAM (5 Agents)

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

### ENGINEERING_TEAM (14 Agents) ⭐ **SUPER TEAM**

**CTO Coordinator (1 Agent):**

| Agent | Capability | Invoke With |
|-------|-----------|-------------|
| **cto** ⭐ | **Strategic coordinator** for all 13 specialists - Intelligent routing, multi-agent orchestration, workflow planning with sequential-thinking, quality gates, dependency tracking | `"Use cto to build an AI-powered analytics dashboard"` `"Use cto to deploy all systems to AWS"` `"Use cto to optimize all 37 agents"` |

**Core 8 Specialists (Custom Built):**

| Agent | Capability | Invoke With |
|-------|-----------|-------------|
| **devops-engineer** ⭐ | **Production-ready** CI/CD (GitHub Actions), Terraform (AWS/GCP), Kubernetes (Helm), monitoring (Prometheus/Grafana), security scanning (886 lines of code) | `"Use devops-engineer to create complete deployment pipeline"` |
| **frontend-developer** | React components, responsive design (Tailwind), state management, performance optimization, accessibility (WCAG) | `"Use frontend-developer to build agent dashboard in Next.js"` |
| **backend-architect** | RESTful API design, microservices architecture, database schema, caching strategies, scalability planning | `"Use backend-architect to design API for 37 agents"` |
| **security-auditor** ⭐ | **Unique comprehensive security** - Code security analysis, vulnerability scanning (OWASP Top 10), compliance (GDPR/HIPAA) | `"Use security-auditor to scan for hardcoded API keys"` |
| **technical-writer** ⭐ | **Broader scope** - PRDs, technical specs, API docs (OpenAPI), architecture diagrams, user guides | `"Use technical-writer to write PRD for agent scheduling"` |
| **system-architect** ⭐ **NEW** | **Professional flow diagrams** - System architecture design, Mermaid diagrams (flowcharts, sequence, ER, state, CI/CD), interactive HTML visualizations with pan/zoom | `"Use system-architect to create microservices architecture diagram"` `"Use system-architect to visualize CI/CD pipeline"` |
| **ai-engineer** ⭐ | **Perfect for 37 agents** - LLM integration, RAG systems, prompt optimization, agent frameworks (LangChain/LangGraph) | `"Use ai-engineer to optimize prompts for all 37 agents"` |
| **ui-ux-designer** | User research, wireframes, design systems, accessibility, user flows, usability testing | `"Use ui-ux-designer to create wireframes for dashboard"` |

**Specialist 5 Agents (From aitmpl.com - Community Validated):**

| Agent | Capability | Downloads | Invoke With |
|-------|-----------|-----------|-------------|
| **code-reviewer** | Quality, security, maintainability reviews - automatic git diff analysis | 3.2K | `"Use code-reviewer to review MARKETING_TEAM email tool"` |
| **test-engineer** | Test automation (Jest, Playwright, pytest), QA strategy, CI/CD testing | 1.3K | `"Use test-engineer to create test strategy for 37 agents"` |
| **prompt-engineer** | LLM prompt optimization, techniques (few-shot, chain-of-thought), benchmarking | 2.4K | `"Use prompt-engineer to optimize copywriter prompt"` |
| **database-architect** | Database design, data modeling, scalability (sharding, replication), polyglot persistence | 1.2K | `"Use database-architect to design analytics DB for 37 agents"` |
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
- ✅ **CTO Coordinator** - Single command orchestration for complex multi-agent workflows
- ✅ **Intelligent routing** - CTO classifies requests and delegates to the right specialists
- ✅ **Full workspace access** - All 14 agents can work with all 37 agents across 4 systems
- ✅ **Production-ready code** - devops-engineer provides 886 lines of battle-tested CI/CD, Terraform, Helm
- ✅ **Professional diagrams** - system-architect creates interactive Mermaid flow diagrams with pan/zoom
- ✅ **Community validated** - 5 specialist agents with thousands of downloads (proven in production)
- ✅ **AI optimization powerhouse** - ai-engineer + prompt-engineer can optimize all 37 agent prompts
- ✅ **Quality layer** - code-reviewer + security-auditor ensure comprehensive code quality
- ✅ **Complete testing** - test-engineer builds strategies, QA_TEAM generates tests
- ✅ **Design → Develop → Test → Deploy** - Complete SDLC from UX to production
- ✅ **Cross-team collaboration** - DevOps deploys all systems, AI/Prompt engineers optimize all agents, Security/Code reviewers audit everything
- ✅ **End-to-end workflows** - CTO coordinates: PRD (technical-writer) → Architecture Diagrams (system-architect) → Database (database-architect) → Wireframes (ui-ux-designer) → API (backend-architect) → UI (frontend-developer) → Review (code-reviewer) → Test (test-engineer) → Deploy (devops-engineer) → Audit (security-auditor) → Optimize (ai-engineer + prompt-engineer) → Debug (debugger)

---

## 📖 Documentation Map

### Getting Started
- [USER_STORY_AGENT/README.md](USER_STORY_AGENT/README.md) - User story generation quick start
- [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md) - Marketing agents overview
- [MARKETING_TEAM/docs/getting-started/api-setup.md](MARKETING_TEAM/docs/getting-started/api-setup.md) - API configuration (OpenAI, Gmail, Drive)
- [QA_TEAM/README.md](QA_TEAM/README.md) - Testing agents overview
- [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) - Engineering agents overview
- [MCP_SETUP.md](MCP_SETUP.md) - MCP server configuration

### Usage Guides
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - **MASTER GUIDE** for all 37 agents
- [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - **CRITICAL** - Proper agent invocation patterns
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - Memory configuration, Drive/email strategies, formatting rules
- [MARKETING_TEAM/docs/guides/usage-guide.md](MARKETING_TEAM/docs/guides/usage-guide.md) - Marketing agent usage with examples
- [MARKETING_TEAM/docs/guides/campaign-examples.md](MARKETING_TEAM/docs/guides/campaign-examples.md) - Real campaign examples
- [QA_TEAM/HOW_TO_USE.md](QA_TEAM/HOW_TO_USE.md) - Testing agent usage with examples
- [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) - Engineering workflows and examples

### Technical Documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation overview
- [MARKETING_TEAM/docs/architecture/system-architecture.md](MARKETING_TEAM/docs/architecture/system-architecture.md) - Marketing system architecture
- [MARKETING_TEAM/docs/architecture/mcp-config.md](MARKETING_TEAM/docs/architecture/mcp-config.md) - MCP configuration details
- [QA_TEAM/BUILD_SUMMARY.md](QA_TEAM/BUILD_SUMMARY.md) - Testing system build notes
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

All **17 MARKETING_TEAM agents** have access to **18 powerful skills** and **7 MCP servers** for visual creation, development, document processing, and external integrations.

### Quick Reference

**📦 18 Skills Available:**

| Category | Skills | Primary Use |
|----------|--------|-------------|
| **Visual** (5) | algorithmic-art, canvas-design, slack-gif-creator, theme-factory, flow-diagram | Social media art, presentations, diagrams |
| **Development** (3) | artifacts-builder, mcp-builder, skill-creator | React apps, custom integrations |
| **Content** (3) | internal-comms, brand-guidelines, pdf-filler | Reports, branded docs, forms |
| **Documents** (4) | pptx, pdf, xlsx, docx | Office documents (built-in) |
| **Integration** (3) | filesystem, figma, context7 | File ops, design extraction |

**🔌 7 MCP Servers Available:**

| Server | Purpose | Key Capabilities |
|--------|---------|------------------|
| **marketing-tools** | OpenAI APIs | GPT-4o images, Sora videos |
| **google-workspace** | G Suite automation | Gmail, Drive, Docs, Sheets, Calendar |
| **perplexity** | Web research | Search with citations, reasoning |
| **bright-data** | Web scraping | SERP, leads (5K free/month) |
| **playwright** | Browser automation | Navigate, screenshot, extract |
| **n8n-mcp** | Workflow automation | 400+ integrations |
| **sequential-thinking** | Structured reasoning | Step-by-step problem solving |

### Usage Examples

**Visual Content:**
- `"Use visual-designer with algorithmic-art to create flow field Instagram post"`
- `"Use social-media-manager with slack-gif-creator for product launch GIF"`

**Development:**
- `"Use landing-page-specialist with artifacts-builder for React landing page"`
- `"Use presentation-designer with theme-factory 'vibrant' theme"`

**Research & Analysis:**
- `"Use research-agent to conduct comprehensive research on AI marketing trends"` (uses custom Perplexity tools)
- `"Use lead-gen-agent with bright-data to find 50 B2B SaaS companies in SF"`
- `"Use seo-specialist with playwright to analyze competitor sites"`

**Documents:**
- `"Use copywriter with internal-comms for Q1 status report"`
- `"Use pdf-specialist with pdf-filler to create registration form"`

### Agent-Skill Mapping

**By Agent Type:**
- **Visual/Creative:** visual-designer, social-media-manager, presentation-designer, video-producer
- **Content/Strategy:** copywriter, landing-page-specialist, pdf-specialist, email-specialist, editor, gmail-agent
- **Research/Analysis:** research-agent, seo-specialist, lead-gen-agent, analyst
- **Orchestration:** router-agent, content-strategist, automation-agent

**All agents inherit all 18 skills** via `MARKETING_TEAM/.claude/settings.json`

### Complete Documentation

For detailed guides with 50+ examples:
- **[skills-and-mcp-guide.md](MARKETING_TEAM/docs/guides/skills-and-mcp-guide.md)** - Complete reference
- **[SKILLS_QUICK_REFERENCE.md](MARKETING_TEAM/docs/SKILLS_QUICK_REFERENCE.md)** - Cheat sheets

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
- **Template:** `.mcp.json.example` (tracked in git)
- **Your Config:** `.mcp.json` (gitignored - contains real API keys)

**Setup Steps:**
1. Copy: `cp .mcp.json.example .mcp.json`
2. Edit `.mcp.json` and add your API keys
3. File stays local (never committed)

**7 MCP Servers Available** (see [Skills & MCP Capabilities](#-skills--advanced-capabilities) for details):
- marketing-tools, google-workspace, perplexity, bright-data, playwright, n8n-mcp, sequential-thinking

**Installation:**
```bash
npx playwright install chromium          # Playwright
pip install workspace-mcp                # Google Workspace
# Others auto-install via npx on first use
```

**Security:** `.mcp.json` and `.claude.json` contain real API keys → gitignored → never commit

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

---

## 🧠 Memory System

**Agents auto-read memory configuration files** at task start:
- `email_config.json` - Email addresses for Gmail operations
- `google_drive_config.json` - Drive folder IDs for uploads
- `brand_voice.json` - Dux Machina tone and messaging
- `visual_guidelines.json` - Brand colors and design standards

**Key Rules:**
- ✅ Use `tools/upload_to_drive.py` for Drive uploads (MCP broken for binary files)
- ✅ Use `tools/send_email_with_attachment.py` for emails with attachments
- ✅ All agents read configs automatically (no hardcoding)

📖 **Complete Guide:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - JSON examples, Drive/email strategies, formatting rules

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
**System:** QA_TEAM
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
- `learned_patterns.json` - Test generation patterns (QA_TEAM)
- `preferences_store.json` - User preferences (USER_STORY_AGENT)

**How it works:** Each agent's `.claude/agents/*.md` file includes a "⚙️ Configuration Files (READ FIRST)" section with explicit instructions to read relevant memory files at task start. This ensures consistency across all agents without hardcoding configuration.

**These files are gitignored and local-only** (never committed to version control).

---

---

## 📝 Recent Updates

**Last Updated:** 2025-10-26

**Latest Major Changes:**
- ✨ **system-architect agent** - 14th Engineering agent for professional Mermaid diagrams with interactive HTML (37 agents total)
- ✨ **flow-diagram skill** - 18th skill for system architecture, flowcharts, sequence diagrams, ER diagrams
- ✨ **CTO coordinator** - Strategic orchestration for all 13 Engineering specialists with intelligent routing
- ✨ **Engineering Super Team** - 14 agents (CTO + 13 specialists: 8 custom built + 5 community validated from aitmpl.com)
- ✨ **automation-agent** - 17th Marketing agent for n8n workflow automation (400+ integrations)
- 🧠 **Memory system standardization** - All agents auto-read config files (email, Drive, brand voice)
- 🔥 **Hybrid Perplexity research** - Custom tools + MCP fallback for maximum reliability

**See [CHANGELOG.md](CHANGELOG.md) for complete version history**

**Repository:** https://github.com/Azeez1/TEST_AGENTS
**License:** Uses Anthropic Claude API - see Anthropic's terms of service
