# Changelog

All notable changes to the TEST_AGENTS multi-agent system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added - LLAR Governance Framework (2025-12-14)

**LLAR (Layered Language Agent Reasoning) 1-12** - Meta-governance framework for the 58-agent multi-team system.

#### New Files Created

1. **[LLAR_CONFIG.json](LLAR_CONFIG.json)** - Central LLAR configuration
   - Routing rules (direct_llm, single_tool, multi_tool_chain, ask_user)
   - Reflection checks (count, atomicity, groundedness, hallucination)
   - Memory discipline (what to store vs ignore)
   - Governance hierarchy and conflict resolution

2. **[LLAR_GOVERNANCE.md](LLAR_GOVERNANCE.md)** - Human-readable LLAR documentation
   - Complete LLAR 1-12 framework explanation
   - Architecture diagram showing supervisor + 6 team orchestrators
   - Implementation guide for orchestrators
   - Routing decision tree and examples

3. **6 Team llar_memory.json Files:**
   - `MARKETING_TEAM/memory/llar_memory.json`
   - `QA_TEAM/memory/llar_memory.json`
   - `ENGINEERING_TEAM/memory/llar_memory.json`
   - `PROPOSAL_TEAM/memory/llar_memory.json`
   - `FINANCIAL_TEAM/memory/llar_memory.json`
   - `SALES_TEAM/memory/llar_memory.json`

#### Enhanced Orchestrators (7 total)

1. **supervisor.md** - Added LLAR-12 conflict resolution authority
   - Full 6-tier conflict resolution hierarchy
   - Cross-team mediation rules
   - Escalation handling protocol
   - LLAR verification checklist

2. **6 Team Orchestrators** (LLAR 6-11):
   - `router-agent.md` (MARKETING_TEAM) - 18 agents
   - `cto.md` (ENGINEERING_TEAM) - 15 agents
   - `test-orchestrator.md` (QA_TEAM) - 5 agents
   - `rfp-agent.md` (PROPOSAL_TEAM) - 1 agent
   - `cfo-agent.md` (FINANCIAL_TEAM) - 10 agents
   - `sales-manager.md` (SALES_TEAM) - 8 agents

#### LLAR Components Implemented

| Component | Description |
|-----------|-------------|
| LLAR-6 | Task Routing Protocol (4 modes) |
| LLAR-7 | Agent Decomposition (one-agent-one-role) |
| LLAR-8 | Reflection Protocol (6 checks) |
| LLAR-9 | Memory System (store/ignore rules) |
| LLAR-10 | Evaluation Metrics (groundedness, accuracy) |
| LLAR-11 | Tool Governance (circuit breaker, rate limits) |
| LLAR-12 | Conflict Resolution (6-tier hierarchy) |

#### Documentation Updates

- **CLAUDE.md** - Added LLAR Governance section with architecture diagram
- **MEMORY_SYSTEM.md** - Added llar_memory.json documentation
- **CHANGELOG.md** - This entry

---

### Added - Tool Governance Framework (2025-11-03)

**Comprehensive governance system to prevent tool duplication and ensure consistent tool/MCP/skill usage across all 37 agents.**

#### 7 New Governance Documents

1. **[TOOL_REGISTRY.md](TOOL_REGISTRY.md)** - Complete inventory of 19 custom tools + 7 MCP servers + 18 skills
   - Priority order for every capability (e.g., PDF creation: 1. pdf skill → 2. Google Docs MCP)
   - Status tracking (Active, Deprecated, MCP Gap Filler)
   - Agent usage mapping

2. **[TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)** - Canonical priority hierarchy
   - Priority order: MCP → Skill → Custom Tool → New (LAST RESORT)
   - Fallback logic templates
   - Decision matrices for when to create new tools

3. **[PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)** - Mandatory workflow before creating/using tools
   - 3-part checklist: Before Declaring Skill, Before Creating Tool, Before Using Tool
   - Verification steps to prevent configuration mismatches
   - Skill enablement validation

4. **[AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md)** - Agent-specific rules
   - Skill declaration accuracy rule (verify enabled in settings.json before declaring in YAML)
   - Priority documentation templates for dual-capability agents
   - Deprecation marker requirements

5. **[TOOL_AUDITOR_CHECKLIST.md](TOOL_AUDITOR_CHECKLIST.md)** - Quarterly audit workflow
   - 8 audit sections (orphaned tools, skill accuracy, conflicts, duplicates, etc.)
   - Automated detection scripts
   - Assigned to security-auditor agent (runs every 3 months)

6. **[TOOL_CLEANUP_WORKFLOW.md](TOOL_CLEANUP_WORKFLOW.md)** - 5-step deprecation process
   - 30-day deprecation timeline
   - Archive location: `archive/tools/deprecated/`
   - Notification requirements

7. **[GOVERNANCE_METRICS.md](GOVERNANCE_METRICS.md)** - Success tracking
   - 16 metrics across 4 categories (tool health, skill health, governance processes, conflict resolution)
   - Baseline values and targets (e.g., orphaned tools: 1 → 0, skill accuracy: 60% → 100%)
   - Quarterly tracking

#### Configuration Fixes

- ✅ **Enabled all document skills** in `MARKETING_TEAM/.claude/settings.json` and `.claude/settings.json`:
  - `pdf` skill: enabled (pypdf-based, comprehensive features)
  - `pptx` skill: enabled (html2pptx, no MCP alternative)
  - `docx` skill: enabled (local Word, Google Docs MCP primary)
  - `xlsx` skill: enabled (local Excel, Google Sheets MCP primary)

- ✅ **Deprecated orphaned tool**: `MARKETING_TEAM/tools/pdf_generator.py` → `archive/tools/deprecated/`
  - Zero agent declarations in YAML frontmatter
  - Replaced by `pdf` skill (more comprehensive)

- ✅ **Resolved naming collision**: Renamed `QA_TEAM/tools/router_tools.py` → `qa_router_tools.py`
  - Prevented conflict with `MARKETING_TEAM/tools/router_tools.py`

#### Agent Updates

- ✅ **All 37 agents now have governance reminders** (concise "Check TOOL_REGISTRY.md first" section)
  - 17 MARKETING_TEAM agents
  - 5 QA_TEAM agents
  - 14 ENGINEERING_TEAM agents
  - 1 Supervisor agent

- ✅ **3 agents updated with dual-capability priority documentation**:
  - `analyst.md` - Google Sheets MCP (PRIMARY) → xlsx skill (FALLBACK)
  - `copywriter.md` - Google Docs MCP (PRIMARY) → docx skill (FALLBACK)
  - `lead-gen-agent.md` - Google Sheets MCP (PRIMARY) → xlsx skill (FALLBACK)
  - Clear fallback logic: Try MCP → If fails, use skill → If fails, offer alternatives

- ✅ **CTO agent** - Added governance enforcement workflow
  - Pre-delegation checklist for tool creation tasks
  - Enforcement examples (PDF generation, email automation, video stitching)
  - Quarterly audit coordination with security-auditor

- ✅ **security-auditor agent** - Added quarterly governance audit responsibilities
  - 4-step audit workflow (Run checklist → Generate report → Coordinate with CTO → Update metrics)
  - Automated detection scripts
  - Report template with violation tracking

#### Documentation Updates

- ✅ **CLAUDE.md** - Added comprehensive Tool Governance section
  - Links to all 7 governance documents
  - Critical rules (skill declaration, priority documentation, orphaned tools)
  - Quick reference for AI assistants

- ✅ **AGENT_INVOCATION_BEST_PRACTICES.md** - Updated with governance references
  - Proper agent invocation patterns to avoid over-specification
  - Tool governance integration

#### Impact & Expected Results

**Problem Solved:** Agents were creating random/duplicate tools instead of using existing MCPs, skills, or custom tools.

**Solution:** 7-file governance framework + configuration fixes + agent reminders

**Expected Reduction in Tool Duplication:** 85-90%
- Before: No registry, no pre-flight checks, agents create duplicate tools freely
- After: Mandatory TOOL_REGISTRY.md check + priority hierarchy + quarterly audits

**Key Metrics (Baseline → Target):**
- Orphaned tool count: 1 → 0
- Skill declaration accuracy: 60% → 100%
- Tool/MCP/skill conflicts: 8 → 0
- Pre-flight compliance: 0% → 95%
- Duplicate functionality cases: 3 → 0

**Quarterly Governance Audit Schedule:**
- Q1 2025: February 1
- Q2 2025: May 1
- Q3 2025: August 1
- Q4 2025: November 1

---

## [Previous Versions]

### [2025-10-26] - System Architecture Agent

#### Added
- ✨ **system-architect agent** (14th ENGINEERING_TEAM agent, 37 agents total)
  - Professional Mermaid diagram creation (flowcharts, sequence, ER, state, CI/CD)
  - Interactive HTML visualizations with pan/zoom
  - System architecture design

- ✨ **flow-diagram skill** (18th skill)
  - Multiple visual styles (glassmorphism, neon, hand-drawn, animated)
  - Social media optimized (LinkedIn, Twitter)
  - Exports: HTML, PNG, GIF, MP4, LinkedIn carousels

### [2025-10-25] - CTO Coordinator & Engineering Super Team

#### Added
- ✨ **CTO coordinator agent** - Strategic orchestration for all 13 ENGINEERING specialists
  - Intelligent routing with sequential-thinking MCP
  - Multi-agent workflow planning
  - Quality gates and dependency tracking

- ✨ **8 Custom-built ENGINEERING agents:**
  - devops-engineer (production-ready CI/CD, Terraform, Kubernetes - 886 lines)
  - frontend-developer (React, Next.js, Tailwind, accessibility)
  - backend-architect (API design, microservices, scalability)
  - security-auditor (comprehensive security analysis, OWASP Top 10)
  - technical-writer (PRDs, specs, API docs, architecture diagrams)
  - system-architect (flow diagrams, Mermaid visualizations)
  - ai-engineer (LLM integration, RAG, prompt optimization, agent frameworks)
  - ui-ux-designer (user research, wireframes, design systems)

- ✨ **5 Community-validated agents (from aitmpl.com):**
  - code-reviewer (3.2K downloads)
  - test-engineer (1.3K downloads)
  - prompt-engineer (2.4K downloads)
  - database-architect (1.2K downloads)
  - debugger (1.7K downloads)

### [2025-10-20] - Automation Agent

#### Added
- ✨ **automation-agent** (17th MARKETING_TEAM agent)
  - n8n workflow automation (400+ integrations)
  - n8n-mcp integration for workflow creation

### [2025-10-15] - Memory System Standardization

#### Added
- 🧠 **Memory system** - All agents auto-read configuration files
  - `email_config.json` - Email addresses for Gmail operations
  - `google_drive_config.json` - Drive folder IDs for uploads
  - `brand_voice.json` - Dux Machina tone and messaging
  - `visual_guidelines.json` - Brand colors and design standards

### [2025-10-10] - Hybrid Perplexity Research

#### Added
- 🔥 **Hybrid Perplexity research** - Custom tools + MCP fallback
  - research-agent uses custom Perplexity tools for reliability
  - MCP fallback for comprehensive research

### [Earlier Releases]

See git history for earlier changes including:
- Initial MARKETING_TEAM (17 agents)
- QA_TEAM (5 testing agents)
- USER_STORY_AGENT (Streamlit application)
- MCP server integrations (Google Workspace, Playwright, Bright Data, etc.)
- 18 skills implementation

---

## Governance Change Log

### [2025-11-03] - Tool Governance Framework

**Changes:**
- Created 7 governance documents
- Enabled all document skills (pdf, pptx, docx, xlsx)
- Deprecated 1 orphaned tool (pdf_generator.py)
- Renamed 1 tool (qa_router_tools.py)
- Added governance reminders to 37 agents
- Updated 3 agents with priority documentation
- Updated CTO and security-auditor with governance workflows

**Next Audit:** 2025-02-01 (Q1 2025)

---

**Legend:**
- ✨ New feature
- 🧠 Enhancement
- 🔥 Performance improvement
- ✅ Configuration fix
- 🔧 Tool/governance update
- 📋 Documentation update
