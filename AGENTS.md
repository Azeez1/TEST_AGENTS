# TEST_AGENTS - Multi-Agent AI System

> Codex context file for OpenAI Codex CLI operating within this repository.
> Claude Code has its own parallel system via `CLAUDE.md` and `.claude/agents/*.md`.

## Project Overview

This is a **62-agent multi-team AI system** built on the Claude Agent SDK, organized into 6 autonomous teams plus a root supervisor. The system is orchestrated through Claude Code — no Python orchestrators.

**Owner:** Dux Machina (duxmachina.com) — Hybrid AI consultancy
**Primary operator:** Azeez (@EZdaArchitect)

## Repository Structure

```
TEST_AGENTS/
├── CLAUDE.md                    ← Claude Code instructions (parallel to this file)
├── AGENTS.md                    ← YOU ARE HERE (Codex instructions)
├── .claude/agents/              ← 1 root supervisor agent
│
├── MARKETING_TEAM/              ← 18 agents (content, social, images, video, email, lead gen)
│   ├── .claude/agents/          ← Agent definitions (YAML frontmatter + markdown)
│   ├── tools/                   ← GPT-4o images, Sora videos, Gmail, Drive utilities
│   ├── memory/                  ← Brand voice, email config, Drive config, visual guidelines
│   ├── outputs/                 ← Generated content (gitignored)
│   ├── examples/                ← Curated reference materials (git-tracked)
│   └── templates/               ← Reusable starting templates (git-tracked)
│
├── ENGINEERING_TEAM/            ← 15 agents (CTO + 14 specialists)
│   ├── .claude/agents/          ← DevOps, security, frontend, backend, AI/ML, UX, etc.
│   └── docs/                    ← PRDs, technical specs, deployment guides
│
├── QA_TEAM/                     ← 5 agents (test orchestrator + 4 specialists)
│   ├── .claude/agents/          ← Unit test, integration, edge case, fixture agents
│   └── tools/                   ← Test generation, coverage analysis
│
├── PROPOSAL_TEAM/               ← 1 agent (RFP automation)
│   ├── .claude/agents/          ← rfp-agent (7-stage pipeline, 30+ compliance frameworks)
│   ├── dux_rfp_agent/           ← Core Python package
│   └── kb/                      ← Pinecone knowledge base
│
├── FINANCIAL_TEAM/              ← 13 agents (PE/M&A + general finance)
│   ├── .claude/agents/          ← Deal analyst, valuation, FP&A, CFO, tax, treasury, etc.
│   └── memory/                  ← Financial assumptions, historical data
│
├── SALES_TEAM/                  ← 9 agents (full sales lifecycle)
│   ├── .claude/agents/          ← SDR, AE, sales ops, proposals, CSM, analytics, outreach
│   └── memory/                  ← CRM configs, templates, target lists
│
├── tools/                       ← Shared production tools (Python)
├── scripts/                     ← One-off utilities and test scripts
├── tests/                       ← Pytest test suites
└── outputs/                     ← Root-level outputs (gitignored)
```

## Agent Definition Format

All agents use `.claude/agents/*.md` files with this structure:

```yaml
---
name: Agent Name
description: What this agent does
model: claude-sonnet-4-6
tools:
  - tool_name               # Custom Python tools
  - mcp__server__tool_name   # MCP server tools (Claude Code runtime only)
skills:
  - skill-name               # Claude Code skills (Claude Code runtime only)
---

# Agent Name

## Role and instructions
[Markdown body with persona, responsibilities, output format]
```

**Important:** The `tools:` and `skills:` in YAML frontmatter are **Claude Code runtime bindings**. When Codex reads these files, treat them as documentation of what the agent can do — not as executable tool declarations.

## Team Roster (62 Agents)

### ROOT (1)
- **supervisor** — Cross-team quality assurance, conflict resolution

### MARKETING_TEAM (18)
- **router-agent** — Campaign orchestrator, delegates to specialists
- **content-strategist** — Editorial planning, content calendars
- **copywriter** — Blog posts, articles, web copy, internal comms
- **editor** — Proofreading, style consistency, quality control
- **social-media-manager** — Platform-specific social content
- **visual-designer** — Image generation (GPT-4o, Nano Banana)
- **video-producer** — Video generation (Sora, Veo)
- **email-specialist** — Email campaigns, drip sequences
- **gmail-agent** — Gmail operations (send, search, read)
- **seo-specialist** — SEO optimization, keyword strategy
- **analyst** — Data analysis, spreadsheets, reporting
- **research-agent** — Market research, competitive intelligence
- **lead-gen-agent** — Lead generation and prospecting
- **landing-page-specialist** — Landing page creation
- **presentation-designer** — PowerPoint/slide decks
- **pdf-specialist** — PDF document generation
- **automation-agent** — n8n workflow automation
- **newsletter-agent** — Email newsletter campaigns

### ENGINEERING_TEAM (15)
- **cto** — Strategic orchestrator for all 14 specialists
- **devops-engineer** — CI/CD, infrastructure, deployment
- **frontend-developer** — React, Next.js, UI components
- **backend-architect** — APIs, databases, system design
- **security-auditor** — Vulnerability scanning, compliance
- **system-architect** — Architecture diagrams, system design
- **ai-engineer** — ML models, AI integrations
- **prompt-engineer** — Prompt optimization, LLM tuning
- **ui-ux-designer** — User experience, wireframes
- **test-engineer** — Quality assurance automation
- **code-reviewer** — Code review and quality analysis
- **database-architect** — Schema design, query optimization
- **debugger** — Debugging, root cause analysis
- **analytics-dashboard-agent** — Data visualization, dashboards
- **technical-writer** — Technical documentation

### QA_TEAM (5)
- **test-orchestrator** — Scans codebases, coordinates test generation
- **unit-test-agent** — Pytest unit test generation
- **integration-test-agent** — Integration and API test generation
- **edge-case-agent** — Edge case identification and testing
- **fixture-agent** — Test fixtures and mock data

### PROPOSAL_TEAM (1)
- **rfp-agent** — 7-stage RFP pipeline, 30+ compliance frameworks

### FINANCIAL_TEAM (13)
- **cfo-agent** — Financial strategy orchestrator
- **deal-analyst** — PE/M&A deal analysis
- **valuation-agent** — Business valuations, DCF models
- **portfolio-manager** — Portfolio analysis and optimization
- **financial-analyst** — Financial modeling, analysis
- **forecasting-agent** — Revenue/expense forecasting
- **fpna-agent** — FP&A, budgeting, variance analysis
- **accountant** — Bookkeeping, financial statements
- **controller** — Financial controls, reporting
- **tax-advisor** — Tax strategy, compliance
- **treasury-agent** — Cash management, liquidity
- **financial-data-analyst** — Data analysis, visualization
- **investor-relations-agent** — IR communications, reporting

### SALES_TEAM (9)
- **sales-manager** — Sales team orchestrator
- **sdr-agent** — Sales development, outbound prospecting
- **account-executive** — Deal management, negotiations
- **sales-operations** — CRM, pipeline management
- **sales-analyst** — Sales metrics, forecasting
- **proposal-specialist** — Sales proposals, pricing
- **customer-success-manager** — Client retention, upsells
- **outbound-specialist** — Cold outreach, sequences
- **pe-outreach-agent** — PE investor outreach campaigns

## Working Agreements

### Code Conventions
- Python: PEP 8, type hints, docstrings for functions/classes
- Agent definitions: Clear YAML frontmatter, specific tool lists, detailed instructions
- Prefer editing existing files over creating new ones
- Never commit secrets (.env, credentials.json, API keys)

### File Boundaries
- Each team has isolated `memory/`, `outputs/`, and `tools/`
- Cross-team access is restricted by design (exception: CTO, test-orchestrator, and supervisor have intentional cross-team read access for coordination and quality assurance)
- `outputs/` folders are gitignored — real deliverables stay local
- `examples/` and `templates/` are git-tracked reference materials

### When Reviewing or Analyzing
- Respect team boundaries — each team has isolated memory/outputs
- Agent `.md` files contain role definitions with YAML frontmatter
- `tools:` and `skills:` in agent files are Claude Code runtime bindings
- Custom Python tools are in `tools/` folders
- Check `memory/` folders for configuration context (brand voice, email settings, etc.)

### Testing
- Run `pytest tests/ --cov` for test validation
- QA_TEAM agents generate pytest test suites
- Test files go in `tests/` directories

### Key Config Files (in MARKETING_TEAM/memory/)
- `brand_voice.json` — Dux Machina tone and messaging guidelines
- `email_config.json` — Email addresses for Gmail operations
- `google_drive_config.json` — Drive folder IDs for uploads
- `visual_guidelines.json` — Brand colors and design standards
- `output_paths.json` — Canonical output directory paths (all 6 teams)

## External Integrations

### MCP Servers (Claude Code runtime)
These are available to Claude Code agents, not directly to Codex:
- **google-workspace** — Gmail, Drive, Docs, Sheets, Calendar, Chat, Tasks, Forms
- **marketing-tools** — GPT-4o images, Sora videos
- **perplexity** — Web research with citations
- **bright-data** — Web scraping, lead data
- **playwright** — Browser automation (testing)
- **n8n-mcp** — Workflow automation (400+ integrations)
- **sequential-thinking** — Structured reasoning chains

### Custom Python Tools (in tools/)
- `openai_gpt4o_image.py` — GPT-4o image generation
- `sora_video.py` — Sora video generation
- `upload_to_drive.py` — Binary file uploads to Google Drive
- `send_email_with_attachment.py` — Emails with attachments via Gmail
- `mcp_server.py` — Marketing tools MCP server

## How Codex Fits In

Codex operates as a **sub-agent** called via MCP from Claude Code. Typical delegation patterns:

1. **Code review** — Claude delegates diff analysis to Codex
2. **Codebase research** — Codex reads files and reports findings
3. **Debugging** — Codex investigates, Claude applies fixes
4. **Second opinion** — Cross-model validation on architecture decisions
5. **Bulk audits** — Codex scans many files, returns summary

Codex should NOT attempt to:
- Invoke Claude Code MCP tools (mcp__google-workspace__*, etc.)
- Execute Claude Code skills
- Modify agent definition files without explicit instruction
- Override Claude Code's orchestration decisions
