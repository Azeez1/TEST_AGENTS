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

**Quick Overview:**

| System | Agents | Primary Use |
|--------|--------|-------------|
| **USER_STORY_AGENT** | 1 | Meeting notes → Excel user stories (Streamlit app) |
| **MARKETING_TEAM** | 17 | Content creation, campaigns, social media, images, videos, emails, lead gen |
| **QA_TEAM** | 5 | Automated pytest test suite generation |
| **ENGINEERING_TEAM** | 14 | CTO coordinator + 13 specialists (DevOps, security, frontend, backend, AI, UX, etc.) |

**Key Agents by Function:**

**Orchestrators:** router-agent, content-strategist (MARKETING), test-orchestrator (QA), cto (ENGINEERING)

**Content & Creative:** copywriter, editor, social-media-manager, visual-designer, video-producer (MARKETING)

**Technical/Engineering:** devops-engineer, frontend-developer, backend-architect, security-auditor, system-architect (ENGINEERING)

**AI/Optimization:** ai-engineer, prompt-engineer (ENGINEERING)

**Research & Analysis:** research-agent, lead-gen-agent, seo-specialist, analyst (MARKETING)

**Testing:** unit-test-agent, integration-test-agent, edge-case-agent, fixture-agent (QA)

📖 **Complete Agent Details:** [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)
- Detailed capabilities for all 37 agents
- Invocation examples and patterns
- API requirements and technology stacks
- Workflow orchestration strategies
- Special features and cross-team collaboration

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
1. Agent definitions live in `.claude/agents/*.md` files with YAML frontmatter
2. Each agent has workspace context (team folder, memory, outputs)
3. Claude Code reads definition → adopts persona → validates workspace → executes
4. Agents automatically use absolute paths (no manual path specification needed)
5. No Python orchestrator - Claude Code IS the orchestrator

**Example Flow:**
`"Use copywriter to write a blog"` → Claude reads copywriter.md → validates MARKETING_TEAM workspace → reads brand_voice.json → generates content → saves to outputs/blog_posts/

**Key Benefits:** Agents never get lost, files end up in correct folders, cross-team boundaries enforced, absolute paths eliminate ambiguity

📖 **Complete Multi-Agent Documentation:** [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - Detailed workflows, orchestration patterns, examples

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

## 📋 Tool Governance

**Comprehensive governance framework** ensures consistent tool/MCP/skill usage across all 37 agents and prevents redundant tool creation.

**Priority Hierarchy:** MCP Servers → Skills → Custom Tools → Create New

**Quick Reference:**
- 19 custom tools (GPT-4o images, Sora videos, Drive uploads, email attachments)
- 7 MCP servers (google-workspace, perplexity, bright-data, playwright, n8n, marketing-tools, sequential-thinking)
- 18 skills (visual, development, content, documents, integration)

📖 **Complete Governance Documentation:**
- **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Complete inventory with priority order for every capability
- **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - Hierarchy of authority (MCP → Skill → Custom → New)
- **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Mandatory workflow before creating tools/skills
- **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Skill declaration rules, priority documentation
- **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Quarterly audit workflow
- **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - Deprecation process
- **[GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)** - Success tracking (16 metrics)

---

## 🎨 Skills & Advanced Capabilities

All **17 MARKETING_TEAM agents** have access to **18 powerful skills** and **7 MCP servers** for visual creation, development, document processing, and external integrations.

**Quick Reference:**

**18 Skills:** algorithmic-art, canvas-design, slack-gif-creator, theme-factory, flow-diagram (visual) • artifacts-builder, mcp-builder, skill-creator (development) • internal-comms, brand-guidelines, pdf-filler (content) • pptx, pdf, xlsx, docx (documents) • filesystem, figma, context7 (integration)

**7 MCP Servers:** marketing-tools (GPT-4o images, Sora videos) • google-workspace (Gmail, Drive, Docs, Sheets) • perplexity (web research with citations) • bright-data (web scraping, leads) • playwright (browser automation) • n8n-mcp (workflow automation) • sequential-thinking (structured reasoning)

📖 **Complete Skills & MCP Documentation:**
- **[skills-and-mcp-guide.md](MARKETING_TEAM/docs/guides/skills-and-mcp-guide.md)** - 50+ usage examples, agent-skill mapping, complete reference
- **[SKILLS_QUICK_REFERENCE.md](MARKETING_TEAM/docs/SKILLS_QUICK_REFERENCE.md)** - Cheat sheets and quick lookups

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

### About Workspace Awareness

**All 37 agents automatically know their workspace** - team folder, memory location, output paths, and cross-team boundaries via workspace_enforcer tool.

**Quick Troubleshooting:**
- If "Workspace validation failed" → Check `pwd` (should be TEST_AGENTS or team folder) → Navigate to correct directory
- Marketing agents cannot access QA_TEAM memory (by design - each team has isolated memory)
- Verify: `pytest tests/test_workspace_enforcement.py -v`

📖 **Complete Workspace Documentation:** [WORKSPACE_ENFORCEMENT_SUMMARY.md](WORKSPACE_ENFORCEMENT_SUMMARY.md)
- 665-line comprehensive guide
- Implementation details, troubleshooting, test results
- Tools: workspace_enforcer.py, path_validator.py
- Standards: WORKSPACE_CONTEXT_STANDARD.md

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
