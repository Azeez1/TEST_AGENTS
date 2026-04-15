# Claude Reference Guide

Detailed reference material for the TEST_AGENTS repository. This file is NOT loaded every turn — read it on demand when you need specifics about agents, skills, project structure, development guidelines, or governance.

---

## Project Structure

```
TEST_AGENTS/
├── claude.md                          ← Lean behavioral directives (loaded every turn)
├── CLAUDE_REFERENCE.md                ← THIS FILE (read on demand)
├── MULTI_AGENT_GUIDE.md               ← Master guide for all 64 agents
├── AGENT_INVOCATION_BEST_PRACTICES.md
├── MEMORY_SYSTEM.md
├── MCP_SETUP.md
├── .claude/agents/                    ← 2 root agents (supervisor, oracle)
├── MARKETING_TEAM/                    ← 18 agents + tools + docs
├── QA_TEAM/                           ← 5 testing agents
├── ENGINEERING_TEAM/                  ← 15 agents: CTO + 14 specialists
├── PROPOSAL_TEAM/                     ← 1 agent: RFP automation
├── FINANCIAL_TEAM/                    ← 14 agents: PE/M&A + Finance
└── SALES_TEAM/                        ← 9 agents: Full sales lifecycle
```

---

## Complete Agent Directory

**Orchestrators:** router-agent (MARKETING), cto (ENGINEERING), test-orchestrator (QA), cfo-agent (FINANCIAL), sales-manager (SALES), supervisor (ROOT)

**Knowledge:** oracle (ROOT) — Karpathy LLM Wiki: YouTube/articles → Obsidian wiki, cross-references, Q&A

**Content & Creative:** copywriter, editor, social-media-manager, visual-designer, video-producer, newsletter-agent (MARKETING)

**Technical:** devops-engineer, frontend-developer, backend-architect, security-auditor, system-architect, ai-engineer, prompt-engineer (ENGINEERING)

**Research:** research-agent, lead-gen-agent, seo-specialist, analyst (MARKETING)

**Testing:** unit-test-agent, integration-test-agent, edge-case-agent, fixture-agent (QA)

**Finance:** deal-analyst, valuation-agent, portfolio-manager, financial-analyst, forecasting-agent, fpna-agent, accountant, controller, tax-advisor, treasury-agent, financial-data-analyst, investor-relations-agent, trading-optimizer (FINANCIAL)

**Sales:** pe-outreach-agent, sdr-agent, account-executive, sales-operations, sales-analyst, proposal-specialist, customer-success-manager, outbound-specialist (SALES)

**RFP:** rfp-agent (PROPOSAL) — 7-stage pipeline, 30+ compliance frameworks

---

## Skills (28 total)

**Visual:** algorithmic-art, canvas-design, slack-gif-creator, theme-factory, flow-diagram, infographic-creator
**Development:** artifacts-builder, mcp-builder, skill-creator
**Content:** internal-comms, brand-guidelines
**Documents:** pptx, pdf, xlsx, docx (in `.claude/skills/document-skills/`)
**n8n Automation:** n8n-code-javascript, n8n-code-python, n8n-expression-syntax, n8n-mcp-tools-expert, n8n-node-configuration, n8n-validation-expert, n8n-workflow-patterns
**Frontend:** frontend-design
**Video:** remotion-video
**Research:** last30days (Reddit + X trend research, keys in `~/.config/last30days/.env`)

## MCP Servers (7)

- **marketing-tools** — GPT-4o images, Sora videos
- **google-workspace** — Gmail, Drive, Docs, Sheets
- **perplexity** — Web research with citations
- **bright-data** — Web scraping, leads
- **playwright** — Browser automation (use Chrome MCP by default instead)
- **n8n-mcp** — Workflow automation
- **sequential-thinking** — Structured reasoning

---

## Development Guidelines

### How the Multi-Agent System Works

1. Agent definitions live in `.claude/agents/*.md` with YAML frontmatter
2. Claude Code reads definition → adopts persona → validates workspace → executes
3. Agents auto-use absolute paths, auto-read memory configs
4. No Python orchestrator — Claude Code IS the orchestrator

### Adding New Agents

Create `.md` in appropriate `.claude/agents/` folder with YAML frontmatter (name, description, tools) + instructions. See `.claude/rules/agent-definition-standards.md`.

### tools/ vs scripts/

- **tools/** — Production components called by agents (reusable, @tool decorated, robust)
- **scripts/** — One-off utilities and test tools (standalone, less robust)

### Output Management

| Folder | Git Tracked | Use |
|--------|-------------|-----|
| `{TEAM}/outputs/` | No | Real deliverables |
| `{TEAM}/examples/` | Yes | Curated reference materials |
| `{TEAM}/templates/` | Yes | Reusable starting frameworks |

---

## LLAR Governance Framework

Supervisor → Team Orchestrators → Specialists

| Component | Purpose |
|-----------|---------|
| LLAR-6 | Task routing (direct_llm, single_tool, multi_tool_chain, ask_user) |
| LLAR-7 | Decomposition (one-agent-one-role, parallel vs sequential) |
| LLAR-8 | Reflection (pre-output validation) |
| LLAR-9 | Memory (preferences, goals, strategies) |
| LLAR-10 | Evaluation (groundedness, accuracy thresholds) |
| LLAR-11 | Tool Governance (schema enforcement, circuit breaker) |
| LLAR-12 | Conflict Resolution hierarchy |

Full docs: [LLAR_GOVERNANCE.md](LLAR_GOVERNANCE.md) | [LLAR_CONFIG.json](LLAR_CONFIG.json)

---

## Configuration & Setup

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_key    # Required
OPENAI_API_KEY=your_key       # For GPT-4o images, Sora videos
```

### MCP Setup
1. `cp .mcp.json.example .mcp.json`
2. Add API keys to `.mcp.json`
3. Never commit (gitignored)

Full setup: [MCP_SETUP.md](MCP_SETUP.md)

---

## Documentation Map

- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) — Master guide for all 64 agents
- [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) — Invocation patterns
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) — Memory config, Drive/email strategies
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) — Complete tool inventory
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) — MCP → Skill → Custom → New hierarchy
- Team READMEs: MARKETING_TEAM, QA_TEAM, ENGINEERING_TEAM, PROPOSAL_TEAM, FINANCIAL_TEAM, SALES_TEAM
