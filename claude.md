# TEST_AGENTS - AI Multi-Agent System Repository

## 📋 Repository Overview

This repository contains **3 autonomous AI agent systems** powered by the Claude Agent SDK, featuring **20 specialized agents** for user story generation, marketing automation, and test generation.

**Systems:**
- **USER_STORY_AGENT** - Transform meeting notes into backlog-ready user stories with Excel export
- **MARKETING_TEAM** - 15 marketing agents for content creation, social media, images, videos, emails, and landing pages
- **TEST_AGENT** - 5 testing agents for automated pytest test suite generation

All agents work through natural conversation with Claude Code - no Python orchestrators needed.

---

## 🚀 Quick Navigation

| System | Purpose | Quick Start | Docs |
|--------|---------|-------------|------|
| **USER_STORY_AGENT** | Meeting notes → User stories | `cd USER_STORY_AGENT && streamlit run app_ui.py` | [README](USER_STORY_AGENT/README.md) |
| **MARKETING_TEAM** | Marketing content automation | Talk to Claude Code agents | [README](MARKETING_TEAM/README.md) |
| **TEST_AGENT** | Automated test generation | Talk to Claude Code agents | [README](TEST_AGENT/README.md) |

**Key Documentation:**
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - Complete guide to using all 20 agents
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
├── MARKETING_TEAM/                  ← 15 marketing automation agents
│   ├── README.md                    ← Quick start guide
│   ├── .claude/
│   │   └── agents/                  ← 15 agent definitions
│   │       ├── router-agent.md      ← Campaign coordinator
│   │       ├── copywriter.md        ← Blog posts & articles
│   │       ├── social-media-manager.md  ← X/Twitter, LinkedIn posts
│   │       ├── visual-designer.md   ← GPT-4o image generation
│   │       ├── video-producer.md    ← Sora video creation
│   │       ├── seo-specialist.md    ← SEO research & keywords
│   │       ├── email-specialist.md  ← Email copywriting
│   │       ├── gmail-agent.md       ← Email sending via Gmail API
│   │       ├── pdf-specialist.md    ← PDF whitepaper creation
│   │       ├── presentation-designer.md  ← PowerPoint decks
│   │       ├── landing-page-specialist.md  ← Landing page UX & code
│   │       ├── analyst.md           ← Performance analysis
│   │       ├── content-strategist.md     ← Campaign orchestration
│   │       ├── editor.md            ← Content review
│   │       └── research-agent.md    ← Web research
│   ├── tools/                       ← Marketing tools
│   │   ├── openai_gpt4o_image.py    ← GPT-4o image generation
│   │   ├── gmail_api.py             ← Gmail integration
│   │   ├── google_drive.py          ← Google Drive uploads
│   │   ├── powerpoint_generator.py  ← PowerPoint creation
│   │   ├── pdf_generator.py         ← PDF generation
│   │   ├── sora_video.py            ← Sora video API
│   │   ├── platform_formatters.py   ← Social media formatters
│   │   ├── router_tools.py          ← Agent coordination tools
│   │   └── create_presentation.py   ← Presentation creation
│   ├── scripts/                     ← Utility scripts
│   │   ├── create_word_documents.py
│   │   ├── generate_linkedin_image.py
│   │   └── test_openai_connection.py
│   ├── docs/                        ← Comprehensive documentation
│   │   ├── getting-started/
│   │   │   └── api-setup.md         ← API configuration guide
│   │   ├── guides/
│   │   │   ├── usage-guide.md       ← Complete usage examples
│   │   │   └── campaign-examples.md ← Real campaign examples
│   │   └── architecture/
│   │       ├── system-architecture.md   ← Technical architecture
│   │       ├── mcp-config.md        ← MCP configuration details
│   │       └── build-notes.md       ← Build process notes
│   ├── requirements.txt             ← Python dependencies
│   ├── .env.example                 ← Environment variables template
│   ├── create_ai_email_presentation.py    ← AI presentation generator
│   ├── enhance_presentation.py      ← Presentation enhancement
│   └── generate_presentation_images.py    ← Image generation for slides
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

### MARKETING_TEAM (15 Agents)

| Agent | Capability | Invoke With |
|-------|-----------|-------------|
| **router-agent** | Coordinates complex multi-agent campaigns | `"Use router-agent to plan a product launch campaign"` |
| **content-strategist** | Full campaign orchestration | `"Use content-strategist to plan Q1 content"` |
| **research-agent** | Evidence-backed market research with citations | `"Use research-agent to investigate best practices"` |
| **copywriter** | Blog posts, articles, web copy (2000+ words) | `"Use copywriter to write a blog about AI trends"` |
| **editor** | Content review, grammar, brand voice alignment | `"Use editor to review this blog post"` |
| **social-media-manager** | X/Twitter, LinkedIn posts with hashtags | `"Use social-media-manager to create a LinkedIn post"` |
| **visual-designer** | GPT-4o image generation | `"Use visual-designer to create a header image"` |
| **video-producer** | Sora video creation | `"Use video-producer to create a 15s product video"` |
| **seo-specialist** | Keyword research, trend analysis, Playwright web research | `"Use seo-specialist to research AI marketing keywords"` |
| **email-specialist** | Email sequences, newsletters, campaigns | `"Use email-specialist to write a welcome email"` |
| **gmail-agent** | Email sending via Gmail API | `"Use gmail-agent to send this newsletter"` |
| **landing-page-specialist** | Conversion-focused landing pages with UX & code | `"Use landing-page-specialist to build a landing page"` |
| **pdf-specialist** | PDF whitepaper/report creation | `"Use pdf-specialist to create a PDF guide"` |
| **presentation-designer** | PowerPoint deck creation | `"Use presentation-designer to create a pitch deck"` |
| **analyst** | Campaign performance analysis | `"Use analyst to analyze campaign metrics"` |

**APIs Required:**
- OpenAI API (images via GPT-4o, videos via Sora)
- Gmail API (email sending)
- Google Drive API (file uploads, optional)

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

## 📖 Documentation Map

### Getting Started
- [USER_STORY_AGENT/README.md](USER_STORY_AGENT/README.md) - User story generation quick start
- [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md) - Marketing agents overview
- [MARKETING_TEAM/docs/getting-started/api-setup.md](MARKETING_TEAM/docs/getting-started/api-setup.md) - API configuration (OpenAI, Gmail, Drive)
- [TEST_AGENT/README.md](TEST_AGENT/README.md) - Testing agents overview
- [MCP_SETUP.md](MCP_SETUP.md) - MCP server configuration

### Usage Guides
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - **MASTER GUIDE** for all 20 agents
- [MARKETING_TEAM/docs/guides/usage-guide.md](MARKETING_TEAM/docs/guides/usage-guide.md) - Marketing agent usage with examples
- [MARKETING_TEAM/docs/guides/campaign-examples.md](MARKETING_TEAM/docs/guides/campaign-examples.md) - Real campaign examples
- [TEST_AGENT/HOW_TO_USE.md](TEST_AGENT/HOW_TO_USE.md) - Testing agent usage with examples

### Technical Documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation overview
- [MARKETING_TEAM/docs/architecture/system-architecture.md](MARKETING_TEAM/docs/architecture/system-architecture.md) - Marketing system architecture
- [MARKETING_TEAM/docs/architecture/mcp-config.md](MARKETING_TEAM/docs/architecture/mcp-config.md) - MCP configuration details
- [TEST_AGENT/BUILD_SUMMARY.md](TEST_AGENT/BUILD_SUMMARY.md) - Testing system build notes

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

### Git Workflow

**What's Excluded (`.gitignore`):**
- `outputs/` and `output/` folders (generated content)
- `*.xlsx`, `*.pdf`, `*.docx`, `*.pptx` (artifacts)
- `__pycache__/`, `*.pyc` (Python cache)
- `memory/`, `archive/` (runtime data)
- `.env`, `credentials.json`, `*.key` (secrets)
- `.claude/settings.local.json` (local config)
- `*.backup`, `.mcp.test-*.json` (backups and test configs)

**What's Included:**
- Source code (`.py` files)
- Agent definitions (`.claude/agents/*.md`)
- Documentation (`.md` files)
- Configuration templates (`.env.example`)
- Requirements files

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

**Root-level MCP config (`.claude.json`):**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    },
    "google-workspace": {
      "command": "workspace-mcp.exe",
      "args": ["--tool-tier", "core"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your_google_client_id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your_google_client_secret"
      }
    },
    "perplexity": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "your_perplexity_api_key",
        "PERPLEXITY_TIMEOUT_MS": "600000"
      }
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GDRIVE_CLIENT_ID": "your_google_client_id",
        "GDRIVE_CLIENT_SECRET": "your_google_client_secret"
      }
    }
  }
}
```

**Install MCP Servers:**
```bash
# Playwright (browser automation)
npx playwright install chromium

# Google Workspace (Gmail, Drive, Calendar, Docs, Sheets, etc.)
pip install workspace-mcp

# Perplexity and Google Drive are auto-installed via npx
```

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
4. Optionally upload to Google Drive with google-drive tool

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
Some agents store learned preferences:
- `memory/brand_voice.json` - Marketing brand voice
- `memory/learned_patterns.json` - Test generation patterns
- `preferences_store.json` - User preferences

These are gitignored and local-only.

---

**Last Updated:** 2025-10-16
**Repository:** https://github.com/Azeez1/TEST_AGENTS
**License:** Uses Anthropic Claude API - see Anthropic's terms of service
