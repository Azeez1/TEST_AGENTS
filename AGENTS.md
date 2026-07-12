# TEST_AGENTS - Multi-Agent AI System

> Codex context file for OpenAI Codex CLI operating within this repository.
> Claude Code has its own parallel system via `CLAUDE.md` and `.claude/agents/*.md`.

## Codex Agent Routing

When a user request maps to a specialist agent, Codex should route through the
Codex sidecar layer instead of reading `.claude/agents/` directly.

Default workflow:
1. Inspect `.codex/manifest.json` to find candidate agents by team, name,
   description, tools, skills, and capabilities.
2. Load the best matching `.codex/agents/<TEAM>/<agent>.md` instruction file
   before doing the work.
3. If multiple agents match, pick the narrowest specialist. Use team
   orchestrators only for broad or ambiguous requests.
4. Read team memory/config files referenced by that agent before creating
   deliverables.
5. Save outputs to that team's `outputs/` folder, following
   `MARKETING_TEAM/memory/output_paths.json` when working on marketing tasks.

Use `$test-agents-router` when the right specialist is unclear.

For Codex infrastructure work, route through `CODEX_TEAM`. Its source agents
live under `CODEX_TEAM/.codex/agents/` and export to
`.codex/agents/CODEX_TEAM/`. This team may edit Codex-facing files such as
`.codex/`, `CODEX_TEAM/`, and `scripts/export_codex_layer.py`, but must not
modify `.claude/`, Claude agent definitions, or `.mcp.json` unless explicitly
asked.

## Project Overview

This is a **73-agent multi-team AI system** built on the Claude Agent SDK, organized into 8 autonomous teams plus 5 root-level agents (see [CLAUDE.md](CLAUDE.md) — single source of truth for roster counts). Codex also has a Codex-native `CODEX_TEAM` for maintaining the local Codex sidecar. The Claude system is orchestrated through Claude Code — no Python orchestrators.

**Owner:** Dux Machina (duxmachina.com) — Hybrid AI consultancy
**Primary operator:** Azeez (@EZdaArchitect)

## Repository Structure

```
TEST_AGENTS/
├── CLAUDE.md                    ← Claude Code instructions (parallel to this file)
├── AGENTS.md                    ← YOU ARE HERE (Codex instructions)
├── .claude/agents/              ← 5 root-level agents (supervisor, oracle, reviewers, validator)
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
├── PROPOSAL_TEAM/               ← 3 agents (RFP automation)
│   ├── .claude/agents/          ← rfp-agent (7-stage pipeline, 30+ compliance frameworks)
│   ├── dux_rfp_agent/           ← Core Python package
│   └── kb/                      ← Pinecone knowledge base
│
├── FINANCIAL_TEAM/              ← 14 agents (PE/M&A + general finance)
│   ├── .claude/agents/          ← Deal analyst, valuation, FP&A, CFO, tax, treasury, etc.
│   └── memory/                  ← Financial assumptions, historical data
│
├── SALES_TEAM/                  ← 9 agents (full sales lifecycle)
│   ├── .claude/agents/          ← SDR, AE, sales ops, proposals, CSM, analytics, outreach
│   └── memory/                  ← CRM configs, templates, target lists
│
├── VOICE_TEAM/                  ← 3 agents (voice agent deployment + onboarding)
├── HEDGE_FUND/                  ← 1 agent (ICT trading)
│
├── tools/                       ← Shared production tools (Python)
├── scripts/                     ← One-off utilities and test scripts
├── tests/                       ← Pytest test suites
├── CODEX_TEAM/                  ← Codex-native sidecar maintenance team
│   ├── .codex/agents/           ← Source definitions for Codex-only agents
│   ├── docs/                    ← Codex coverage plans and architecture notes
│   └── outputs/                 ← Codex audits and implementation reports
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

## Team Roster (73 Claude Agents + 6 Codex-Native Agents)

### ROOT (5)
- **supervisor** — Cross-team quality assurance, conflict resolution
- **oracle** — Personal knowledge base (Obsidian wiki) manager
- **linkedin-brand-reviewer** — Scores LinkedIn drafts against brand voice rules
- **pe-diagnosis-validator** — Validates PE diagnosis PDFs before send
- **pe-diagnosis-visual-reviewer** — Scores PE diagnoses against visual quality bar

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

### PROPOSAL_TEAM (3)
- **rfp-agent** — 7-stage RFP pipeline, 30+ compliance frameworks
- **proposal-tracker** — Proposal pipeline and deadline tracking
- **sbir-validator** — SBIR/STTR compliance validation

### FINANCIAL_TEAM (14)
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
- **trading-optimizer** — ICT strategy optimization, Pine Script, backtesting

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

### VOICE_TEAM (3)
- **voice-deployer** — Voice agent deployment
- **voice-onboarder** — Voice agent onboarding flows
- **voice-email-validator** — Email validation for voice workflows

### HEDGE_FUND (1)
- **ict-trader** — ICT trading strategy execution and journaling

### CODEX_TEAM (6, Codex-native)
- **codex-team-manager** — Codex sidecar orchestrator and L1-L13 roadmap owner
- **codex-layer-architect** — Exporter, manifest, commands, and sidecar architecture
- **codex-agent-editor** — Codex agent scope, instructions, and routing quality
- **codex-skill-engineer** — Codex skills, skill mirroring, and learned behavior capture
- **codex-mcp-hooks-engineer** — Codex MCP setup, hooks, automation, and runtime validation
- **codex-leverage-auditor** — Evidence-backed L1-L13 Codex coverage audits

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

### Source Reading Completeness
- When asked to read, summarize, analyze, extract, or transform an article, X post/article/thread, newsletter, PDF, webpage, or other long-form source, do not rely on search snippets, link previews, cards, SERP excerpts, or partial preview text.
- Use the most complete source available: X MCP/API, authenticated browser, canonical publisher page, PDF/text extractor, or user-provided full text.
- Before presenting analysis, verify full-body access by checking the source URL/access method, title, author/date when available, first paragraph, last paragraph, visible headings, and approximate paragraph or word count.
- If only preview/snippet content is available, explicitly say: "I only have preview text, not the full article."
- Do not claim to have read the full article unless the body text was available beyond the preview and passed the completeness check.
- Respect copyright limits: summarize, outline, or quote only short excerpts unless the user provided the text or the content is otherwise safe to reproduce.

### Testing
- Run `pytest tests/ --cov` for test validation
- QA_TEAM agents generate pytest test suites
- Test files go in `tests/` directories

### Key Config Files (in MARKETING_TEAM/memory/)
- `brand_voice.json` — Dux Machina tone and messaging guidelines
- `email_config.json` — Email addresses for Gmail operations
- `google_drive_config.json` — Drive folder IDs for uploads
- `visual_guidelines.json` — Brand colors and design standards
- `output_paths.json` — Canonical output directory paths (all 8 teams)

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
