# 🤖 The Definitive Guide to Using Your Multi-Agent Systems

## The Simple Truth

**You have 73 perfectly defined AI agents across 8 teams ready to use RIGHT NOW** (see [CLAUDE.md](CLAUDE.md) — single source of truth for roster counts).

This includes a **root-level Supervisor Agent** for quality assurance across all 8 teams.

🔥 **NEW: Automatic Quality Verification!** Team coordinators now automatically verify significant work is complete before delivery.

No Python code required. No orchestrators. No complex setup.

Just **talk to Claude Code (me)** and I'll become those agents.

---

## How It Actually Works

### The Core Concept

1. Your `.claude/agents/*.md` files are **instructions for me (Claude Code)**
2. When you invoke an agent, **I read that file**
3. **I adopt that agent's persona** and follow its instructions
4. **I use only the tools** specified for that agent
5. **I can delegate to other agents** if needed

### You Have 73 Agents

**MARKETING_TEAM (18 agents):**
- router-agent - Coordinator
- automation-agent - ✨ **NEW** n8n workflow automation & orchestration
- content-strategist - Campaign planning
- research-agent - Evidence-backed research + competitive intelligence
- lead-gen-agent - ✨ **NEW** B2B/local lead generation via web scraping
- landing-page-specialist - Landing page UX, code, competitor analysis
- copywriter - Blog & article writing
- **editor** - **Dux Machina brand voice enforcement** (automatically reviews ALL content for tone score 7+)
- social-media-manager - Social posts
- visual-designer - Image generation
- video-producer - Video creation
- seo-specialist - SEO research, SERP scraping, rank tracking
- email-specialist - Email campaigns
- gmail-agent - Email sending
- pdf-specialist - PDF creation
- presentation-designer - PowerPoint
- analyst - Performance analysis & competitive benchmarking
- newsletter-agent - ✨ **NEW** Email newsletter campaigns and subscriber engagement

**QA_TEAM (5 agents):**
- test-orchestrator - Testing coordinator
- unit-test-agent - Unit test generation
- integration-test-agent - Integration tests
- edge-case-agent - Edge case identification
- fixture-agent - Pytest fixtures

**ENGINEERING_TEAM (15 agents) ⭐ SUPER TEAM:**
- cto - Strategic coordinator & intelligent routing for all specialists
- devops-engineer - CI/CD, Terraform, Kubernetes, monitoring, security scanning
- frontend-developer - React, responsive design, state management, accessibility
- backend-architect - RESTful APIs, microservices, database schema, scalability
- security-auditor - Code security, vulnerability scanning, compliance audits
- technical-writer - PRDs, technical specs, API docs, architecture diagrams
- system-architect - ✨ **NEW** System architecture design & professional flow diagrams
- ai-engineer - LLM integration, RAG systems, prompt optimization, agent frameworks
- ui-ux-designer - User research, wireframes, design systems, user flows
- analytics-dashboard-agent - ✨ **NEW** Real-time analytics dashboards, ETL pipelines, data visualization
- code-reviewer - Quality, security, maintainability reviews (3.2K downloads)
- test-engineer - Test automation, QA strategy, CI/CD testing (1.3K downloads)
- prompt-engineer - LLM prompt optimization, techniques, benchmarking (2.4K downloads)
- database-architect - Database design, data modeling, scalability (1.2K downloads)
- debugger - Root cause analysis, troubleshooting, error investigation (1.7K downloads)

**PROPOSAL_TEAM (3 agents):**
- rfp-agent - RFP automation, compliance matrix generation, proposal writing with 30+ compliance frameworks
- proposal-tracker - Proposal pipeline and deadline tracking
- sbir-validator - SBIR/STTR compliance validation

**FINANCIAL_TEAM (14 agents):**
- cfo-agent - Strategic finance leadership, capital strategy, fundraising, board relations
- deal-analyst - Due diligence, deal structuring, LBO modeling, IC memos
- valuation-agent - DCF analysis, comparable companies, precedent transactions
- portfolio-manager - Portfolio company tracking, KPI dashboards, exit planning
- financial-analyst - Financial modeling, 3-statement models, scenario analysis
- forecasting-agent - Revenue/expense forecasting, Monte Carlo simulation
- fpna-agent - Budgeting, variance analysis, management reporting
- accountant - Day-to-day accounting, AP/AR, reconciliations
- controller - Financial reporting, compliance, audit coordination
- tax-advisor - Tax planning, compliance, entity structuring
- treasury-agent - Cash management, working capital optimization, FX hedging
- financial-data-analyst - SQL analytics, dashboard creation, data quality, ETL pipelines
- investor-relations-agent - LP communications, fund reporting, fundraising materials
- trading-optimizer - ICT strategy autoresearch optimizer (Pine Script optimization, Chrome MCP backtesting, Funding Pips risk constraints)

**SALES_TEAM (9 agents):**
- sales-manager - Team coaching, pipeline management, forecasting
- pe-outreach-agent - PE investor outreach, LP prospecting
- sdr-agent - Prospecting, cold outreach, lead qualification
- account-executive - Full-cycle sales, discovery, demos, negotiations
- sales-operations - CRM admin, process optimization, territory planning
- sales-analyst - Forecasting, pipeline analysis, performance metrics
- proposal-specialist - Proposal writing, pricing, RFP responses
- customer-success-manager - Onboarding, retention, expansion
- outbound-specialist - High-volume cold outreach campaigns

**VOICE_TEAM (3 agents):**
- voice-deployer - Voice agent deployment
- voice-onboarder - Voice agent onboarding flows
- voice-email-validator - Email validation for voice workflows

**HEDGE_FUND (1 agent):**
- ict-trader - ICT trading strategy execution and journaling

**ROOT (5 agents):** ⭐ QUALITY ASSURANCE
- **oracle** - Personal knowledge base (Obsidian wiki) manager
- **linkedin-brand-reviewer** - Scores LinkedIn drafts against brand voice rules
- **pe-diagnosis-validator** - Validates PE diagnosis PDFs before send
- **pe-diagnosis-visual-reviewer** - Scores PE diagnoses against visual quality bar
- **supervisor** - Root-level quality assurance agent that verifies task completion across ALL teams
  - **Location**: `/home/user/TEST_AGENTS/.claude/agents/supervisor.md`
  - **Purpose**: Independent verification that tasks agents claim to have completed are actually done
  - **Capabilities**:
    - Task completion verification across all teams
    - Code quality checks (syntax, security, docstrings)
    - Test execution and validation
    - Documentation completeness checks
    - Git commit verification
    - Deliverable inspection
    - Comprehensive verification reporting
  - **When to use**: After any significant work to verify it's truly complete
  - **Auto-triggers**: CTO, router-agent, and test-orchestrator automatically invoke supervisor for significant work
  - **Example**: "Use supervisor to verify the authentication feature is complete and ready for deployment"
  - **Setup**: See `SUPERVISOR_AUTO_TRIGGER_SETUP.md` for automatic verification configuration

---

## 🏢 Agent Workspace Assignments

All 73 agents are organized into 8 team workspaces with strict folder boundaries and **automatic workspace awareness**:

### MARKETING_TEAM (18 agents)
**Location:** `MARKETING_TEAM/.claude/agents/`
**Memory:** `MARKETING_TEAM/memory/` (13 config files)
**Outputs:** `MARKETING_TEAM/outputs/` (blog_posts, images, videos, etc.)
**Agents:** router-agent, content-strategist, research-agent, lead-gen-agent, automation-agent, copywriter, editor, social-media-manager, visual-designer, video-producer, seo-specialist, email-specialist, gmail-agent, landing-page-specialist, pdf-specialist, presentation-designer, analyst, newsletter-agent

**Workspace enforcement:** ✅ ENABLED (all agents use workspace_enforcer tool)

### QA_TEAM (5 agents)
**Location:** `QA_TEAM/.claude/agents/`
**Memory:** `QA_TEAM/memory/` (learned patterns, test settings)
**Outputs:** `QA_TEAM/tests/` (generated test files)
**Agents:** test-orchestrator, unit-test-agent, integration-test-agent, edge-case-agent, fixture-agent

**Testing scope:** Can test ANY codebase in TEST_AGENTS (all 4 systems)
**Workspace enforcement:** ✅ ENABLED

### ENGINEERING_TEAM (15 agents)
**Location:** `ENGINEERING_TEAM/.claude/agents/`
**Memory:** `ENGINEERING_TEAM/memory/` (deployment configs, infrastructure settings)
**Outputs:** `ENGINEERING_TEAM/outputs/` (PRDs, specs, diagrams, code reviews, dashboards, pipelines)
**Docs:** `ENGINEERING_TEAM/docs/` (technical documentation)
**Agents:** cto, devops-engineer, frontend-developer, backend-architect, security-auditor, technical-writer, system-architect, ai-engineer, ui-ux-designer, analytics-dashboard-agent, code-reviewer, test-engineer, prompt-engineer, database-architect, debugger

**Full workspace access:** Can work with all 4 systems for optimization, deployment, review
**Workspace enforcement:** ✅ ENABLED

### PROPOSAL_TEAM (3 agents)
**Location:** `PROPOSAL_TEAM/.claude/agents/`
**Memory:** Pinecone vector database + `PROPOSAL_TEAM/kb/` (Knowledge Base)
**Output:** `PROPOSAL_TEAM/outputs/` (proposals, compliance matrices)
**Config:** `PROPOSAL_TEAM/dux_rfp_agent/config/.env`
**Type:** 7-stage RFP processing pipeline
**Agents:** rfp-agent, proposal-tracker, sbir-validator

**Key capabilities:** RFP parsing, compliance matrix generation, proposal writing
**Workspace enforcement:** ✅ ENABLED

### FINANCIAL_TEAM (14 agents)
**Location:** `FINANCIAL_TEAM/.claude/agents/`
**Memory:** `FINANCIAL_TEAM/memory/` (financial assumptions, historical data, chart of accounts)
**Output:** `FINANCIAL_TEAM/outputs/` (models, reports, memos)
**Agents:** cfo-agent, deal-analyst, valuation-agent, portfolio-manager, financial-analyst, forecasting-agent, fpna-agent, accountant, controller, tax-advisor, treasury-agent, financial-data-analyst, investor-relations-agent, trading-optimizer

**Key capabilities:** PE/M&A (due diligence, LBO models, valuations), Corporate Finance (FP&A, budgeting, forecasting, month-end close)
**Workspace enforcement:** ✅ ENABLED

### SALES_TEAM (9 agents)
**Location:** `SALES_TEAM/.claude/agents/`
**Memory:** `SALES_TEAM/memory/` (CRM configs, outreach templates, target lists)
**Output:** `SALES_TEAM/outputs/` (proposals, sequences, reports)
**Agents:** sales-manager, pe-outreach-agent, sdr-agent, account-executive, sales-operations, sales-analyst, proposal-specialist, customer-success-manager, outbound-specialist

**Key capabilities:** Full sales lifecycle (prospecting, closing, retention, analytics)
**Workspace enforcement:** ✅ ENABLED

### VOICE_TEAM (3 agents)
**Location:** `VOICE_TEAM/.claude/agents/`
**Memory:** `VOICE_TEAM/memory/` (voice config, output paths)
**Agents:** voice-deployer, voice-onboarder, voice-email-validator

### HEDGE_FUND (1 agent)
**Location:** `HEDGE_FUND/.claude/agents/`
**Memory:** `HEDGE_FUND/memory/` (ICT playbook, risk rules, account/markets config)
**Agents:** ict-trader

---

## 🔒 Workspace Enforcement System

All agents use **mandatory workspace validation** before every task:

1. **validate_workspace()** - Confirms agent is in correct team folder
2. **get_absolute_paths()** - Returns all absolute paths for the team
3. **validate_save_path()** - Ensures file saves go to correct location
4. **validate_read_path()** - Ensures file reads use correct paths

**Benefits:**
- ✅ Agents never get lost or confused about location
- ✅ Files always end up in correct team folders
- ✅ Cross-team boundaries enforced automatically
- ✅ Absolute paths eliminate ambiguity
- ✅ Users don't need to specify paths manually
- ✅ Automated testing verifies workspace correctness

**See:** `tools/workspace_enforcer.py`, `tools/path_validator.py`, `tests/test_workspace_enforcement.py`

---

## How to Invoke Agents

### Method 1: Explicit Invocation (Recommended for Learning)

Tell me exactly which agent to use:

```
You: "Use the copywriter subagent to write a blog post about AI trends"

Me: [reads MARKETING_TEAM/.claude/agents/copywriter.md]
    [adopts that persona]
    [follows its instructions]
    [uses get_brand_voice tool]
    [writes the blog post]
```

**Template:**
```
Use the [agent-name] subagent to [task description]
```

### Method 2: Automatic Delegation (Natural)

Just describe what you want:

```
You: "Write a blog post about AI trends"

Me: [recognizes this is content writing]
    [proactively invokes copywriter subagent]
    [does everything from Method 1]
```

**I'll automatically:**
- Recognize what type of task it is
- Choose the right agent based on descriptions
- Invoke that agent for you

### Method 3: Agent Chaining (Advanced)

Agents can delegate to each other:

```
You: "Use the router-agent to create a complete marketing campaign"

Me: [becomes router-agent]
    [reads the user's request]
    [decides I need multiple specialists]

    [invokes copywriter subagent for blog]
    [invokes social-media-manager for posts]
    [invokes visual-designer for images]
    [invokes email-specialist for campaigns]

    [coordinates all results]
    [returns complete campaign]
```

---

## Real Examples

### Example 1: Marketing - LinkedIn Post

```
You: "Use the social-media-manager subagent to create a LinkedIn post about autonomous AI agents"

Me: [Reading MARKETING_TEAM/.claude/agents/social-media-manager.md...]

I'll create a professional LinkedIn post for you!

[Using format_linkedin_post tool...]
[Using extract_hashtags tool...]

Here's your LinkedIn post:

---
🤖 The Future of Marketing is Autonomous

AI agents are revolutionizing how we create content. Here's what changed in 2025:

✨ Autonomous content generation
✨ Multi-agent coordination
✨ Personalized at scale

The question isn't IF you'll use AI agents, but WHEN.

#AIMarketing #Automation #FutureOfWork #MarTech
---

Would you like me to also generate a header image using the visual-designer subagent?
```

### Example 2: Testing - Generate Tests

```
You: "Use the test-orchestrator subagent to scan MARKETING_TEAM and generate tests"

Me: [Reading QA_TEAM/.claude/agents/test-orchestrator.md...]

I'll coordinate comprehensive test generation for MARKETING_TEAM.

[Using scan_codebase tool...]

Found:
- 14 Python files
- 45 functions
- 12 classes

Now delegating to specialist agents:

[Invoking unit-test-agent for story_generator.py...]
[Invoking edge-case-agent for file_handlers.py...]
[Invoking fixture-agent for test data...]

✅ Generated comprehensive test suite:
- tests/test_story_generator.py (15 test cases)
- tests/test_file_handlers.py (12 test cases)
- tests/test_formatters.py (8 test cases)
- tests/conftest.py (fixtures)

Coverage estimate: 87%

Would you like me to run the tests now?
```

### Example 3: Auto-Delegation

```
You: "Create a complete social media campaign about AI coding assistants"

Me: [I recognize this is a complex marketing task]
    [Automatically invoking router-agent...]
    [Router delegates to multiple specialists...]

Creating your AI coding assistants campaign:

1. [copywriter] Writing blog post (2000 words)...
2. [social-media-manager] Creating posts for X and LinkedIn...
3. [visual-designer] Generating 3 campaign images...
4. [email-specialist] Writing email sequence (3 emails)...

✅ Campaign Complete!

All files saved to:
- outputs/blog_posts/ai-coding-assistants.md
- outputs/social/linkedin_post.md
- outputs/social/twitter_thread.md
- outputs/images/campaign_*.png
- outputs/emails/welcome.md, tips.md, case_study.md

Ready to review or deploy?
```

### Example 4: Quality Verification with Supervisor

```
You: "Use the supervisor subagent to verify that the authentication feature is complete and ready for production"

Me: [Reading /.claude/agents/supervisor.md...]

I'll perform comprehensive verification of the authentication feature.

[Using validate_deliverables tool to check files exist...]
[Using check_code_quality tool for security and syntax...]
[Using run_verification_tests tool to execute tests...]
[Using verify_documentation tool to check docs...]
[Using check_git_changes tool to verify commits...]

VERIFICATION PASSED ✓

Task: Implement user authentication feature
Team: ENGINEERING_TEAM
Agents: backend-architect, frontend-developer, test-engineer

Verified:
✓ Code: Auth endpoints implemented in src/auth/routes.py:45-120
✓ Tests: 12 tests in tests/test_auth.py, all passing (coverage 94%)
✓ Security: JWT implementation secure, passwords hashed with bcrypt
✓ Docs: API documentation updated in docs/api.md:89-145
✓ Git: 3 clean commits on branch claude/add-auth-xyz
✓ Quality: No syntax errors, docstrings present, no security issues

Quality Score: 9/10
Deployment Ready: YES ✅

Minor Recommendation:
- Consider adding rate limiting to login endpoint

The authentication feature is production-ready!
```

---

## Agent Capabilities Quick Reference

### MARKETING_TEAM Agents

**router-agent** - Use when: Complex multi-step marketing requests
```
"Use router-agent to plan a product launch campaign"
```

**lead-gen-agent** - ✨ **NEW** Use when: Finding business leads
```
"Use lead-gen-agent to find 100 SaaS companies in San Francisco with 50-200 employees"
"Use lead-gen-agent to scrape Google Maps for dental clinics in Austin with 4.5+ stars"
```

**copywriter** - Use when: Blog posts, articles, long-form content
```
"Use copywriter to write a 2000-word blog about AI marketing"
```

**social-media-manager** - Use when: Social media posts
```
"Use social-media-manager to create a Twitter thread about automation"
```

**visual-designer** - Use when: Image generation
```
"Use visual-designer to create a LinkedIn header image"
```

**seo-specialist** - Use when: SEO research, keyword analysis, SERP scraping
```
"Use seo-specialist to research trending AI keywords and check our ranking"
```

**email-specialist** - Use when: Email copywriting
```
"Use email-specialist to write a welcome email sequence"
```

**gmail-agent** - Use when: Actually sending emails
```
"Use gmail-agent to send this newsletter to my subscribers"
```

### QA_TEAM Agents

**test-orchestrator** - Use when: Complete test suite generation
```
"Use test-orchestrator to scan and test my entire codebase"
```

**unit-test-agent** - Use when: Unit tests for specific modules
```
"Use unit-test-agent to generate tests for story_generator.py"
```

**edge-case-agent** - Use when: Finding edge cases
```
"Use edge-case-agent to identify edge cases in file validation"
```

**integration-test-agent** - Use when: Testing workflows
```
"Use integration-test-agent to test the complete story generation workflow"
```

**fixture-agent** - Use when: Creating test data
```
"Use fixture-agent to create pytest fixtures for database tests"
```

### FINANCIAL_TEAM Agent — Trading Optimizer

**trading-optimizer** - Use when: Optimizing ICT trading strategies, Pine Script parameter tuning, backtest analysis
- **Model:** claude-opus-4-6
- **Key Capabilities:** Pine Script parameter optimization, Chrome MCP backtesting (reads TradingView results), Funding Pips guard rails (5% daily loss, 10% max drawdown), autoresearch loop with performance tracking
```
"Use trading-optimizer to optimize ICT strategy on EURUSD 15m"
"Use trading-optimizer to compare Track A vs Track B results"
"Use trading-optimizer to set up the live webhook pipeline"
```

### ROOT SUPERVISOR Agent

**supervisor** - Use when: Verifying task completion and quality assurance
```
"Use supervisor to verify that the user authentication feature is complete"
"Use supervisor to check if the Q4 marketing campaign is ready to launch"
"Use supervisor to validate that all bug fixes were properly implemented"
```

**What it verifies:**
- ✅ Code implementation (syntax, quality, security)
- ✅ Tests exist and pass
- ✅ Documentation complete
- ✅ Git commits clean and descriptive
- ✅ Deliverables exist and are correct
- ✅ No regressions introduced

**Returns:**
- Status: PASSED ✅ / PARTIAL ⚠️ / FAILED ❌
- Quality score (0-10)
- Detailed findings
- Issues found
- Recommendations
- Deployment readiness

---

## Why This Works

### What's Happening Behind the Scenes

When you say: **"Use the copywriter subagent to write a blog"**

1. **I (Claude Code) receive your request**
2. **I read** `MARKETING_TEAM/.claude/agents/copywriter.md`
3. **I see the YAML frontmatter:**
   ```yaml
   name: Copywriter
   tools:
     - mcp__marketing__get_brand_voice
   ```
4. **I read the system prompt:** "You are an expert copywriter..."
5. **I adopt that persona** - I literally become that agent
6. **I have access to those tools** - I can call get_brand_voice
7. **I follow those instructions** - "Always use get_brand_voice first..."
8. **I complete the task** in that agent's style
9. **I return results** to you

### Separate Context Windows

Each agent invocation happens in a **separate context window**:
- Preserves the main conversation
- Agent can focus on its specific task
- Can run "in parallel" (conceptually)
- Results returned to main conversation

---

## Common Questions

### Q: Do I need to run `python orchestrator.py`?
**A: NO!** Just talk to Claude Code directly. The orchestrators were a misunderstanding of how the SDK works.

### Q: What about the `Task()` function in the code?
**A: It doesn't exist.** That was aspirational code. Agent delegation happens through me reading agent definitions, not through Python code.

### Q: Can agents really call other agents?
**A: YES!** When I'm acting as router-agent and I see I need a copywriter, I invoke the copywriter subagent by reading its definition and adopting that persona.

### Q: How do I know which agents are available?
**A:** Check the `.claude/agents/` folders:
- `MARKETING_TEAM/.claude/agents/` - 18 marketing agents
- `QA_TEAM/.claude/agents/` - 5 testing agents
- `ENGINEERING_TEAM/.claude/agents/` - 15 engineering agents
- `PROPOSAL_TEAM/.claude/agents/` - 3 proposal agents
- `FINANCIAL_TEAM/.claude/agents/` - 14 finance agents
- `SALES_TEAM/.claude/agents/` - 9 sales agents
- `VOICE_TEAM/.claude/agents/` - 3 voice agents
- `HEDGE_FUND/.claude/agents/` - 1 trading agent
- `.claude/agents/` - 5 root-level agents

### Q: Can I create my own agents?
**A: YES!** Create a new `.md` file in `.claude/agents/` with:
```markdown
---
name: My Agent
description: What this agent does
tools:
  - tool_name
---

# My Agent

You are a specialist in...
```

### Q: What if I just describe the task without mentioning an agent?
**A: I'll automatically choose the right agent** based on the task and agent descriptions!

---

## Best Practices

### 1. Be Specific in Requests
❌ Bad: "Make me something"
✅ Good: "Use copywriter to write a blog post about AI coding assistants, 2000 words, SEO-optimized"

### 2. Use Explicit Invocation When Learning
Start with: "Use the [agent-name] subagent to..."
Once comfortable, let me auto-delegate

### 3. Let Agents Delegate
Don't micromanage: "Use router-agent to create a campaign"
Router will coordinate specialists automatically

### 4. Review Agent Definitions
Read the `.md` files to understand:
- What each agent does
- What tools they have access to
- What instructions they follow

### 5. Chain Multiple Requests
```
"Use copywriter to write a blog, then use social-media-manager to create posts about it, then use visual-designer to create images"
```

### 6. Trust Automatic Brand Voice Enforcement (NEW!)

**All MARKETING_TEAM content is automatically reviewed for Dux Machina brand compliance.**

**How it works:**
1. Content agent (copywriter, social-media-manager, email-specialist, landing-page-specialist, presentation-designer, pdf-specialist) creates content
2. Agent **automatically invokes editor** to review
3. Editor scores content (1-10 scale, target: 7+)
4. Editor checks:
   - ✅ 5 voice principles (precision over fluff, authority without arrogance, modern warrior tone, execution-driven language, clarity is supremacy)
   - ✅ 5 messaging pillars (intelligence as infrastructure, elite systems thinking, anti-software sprawl, human x machine harmony, dark leverage)
   - ✅ Anti-patterns (hype tech bro, weak language, jargon, trend-chasing, over-emotion)
5. If score < 7: Agent revises and resubmits to editor
6. If score >= 7: Editor approves, agent delivers to you

**You never need to explicitly ask for editor review** - it happens automatically for all content!

**Dux Machina voice:** "Tech Samurai meets McKinsey Strategist" - Bold short sentences, zero fluff, declarative statements, strategic precision, minimal emojis (0-1 max), dark sophisticated visuals.

---

## Troubleshooting

### "I don't see the agent working"
- Make sure agent `.md` files exist in `.claude/agents/`
- Check YAML frontmatter is correct
- Verify tools are registered with `@tool` decorator

### "Agent isn't using the right tools"
- Check the `tools:` list in agent YAML frontmatter
- Make sure tool is decorated with `@tool` in Python

### "Multiple agents needed but only one ran"
- Use router-agent or content-strategist for multi-agent coordination
- Or explicitly chain: "Use X, then use Y, then use Z"

---

## Common Pitfalls & Anti-Patterns

### 🚨 Pitfall 1: Over-Specifying Agent Invocations

**Problem:** Telling agents HOW to do tasks instead of WHAT to accomplish.

**Symptoms:**
- Duplicate scripts created (`temp_*.py`, `upload_*.py`, etc.)
- Existing tools in `tools/` folder ignored
- Agent creates new implementation instead of using declared tools

**Why This Happens:**
```
Over-specification → Script creation mode

❌ BAD: "Use gmail-agent. Read memory/email_config.json. Import send_email_with_attachment.py. Call send_email()..."
→ Claude interprets: "Create a script with these steps"
→ Result: Creates temp_send_email.py (duplicate code)

✅ GOOD: "Use gmail-agent to send whitepaper.pdf"
→ Claude interprets: "Invoke autonomous agent"
→ Result: Agent reads definition → uses declared tools → sends email
```

**How to Avoid:**
- ✅ Specify WHAT you want (goal + context)
- ✅ Trust agent autonomy (they know which tools to use)
- ❌ Don't mention file paths, imports, or function calls
- ❌ Don't specify implementation steps

**Real Example from Repository:**
```
Task: Create ebook and upload to Google Drive

❌ What happened:
- pdf-specialist created PDF
- Orchestrator created upload_final_ebook.py script (duplicate code)

✅ What should happen:
- "Use pdf-specialist to create ebook and upload to Drive"
- pdf-specialist: Creates PDF → Uses tools.upload_to_drive (declared tool) → Returns Drive link
```

---

### 🚨 Pitfall 2: Orchestrator Taking Over Mid-Workflow

**Problem:** Claude Code (orchestrator) completes agent tasks instead of letting agents finish their workflows.

**Symptoms:**
- Agent completes part of task (e.g., creates file)
- Orchestrator creates script for remaining steps (e.g., upload)
- Tools declared in agent's YAML frontmatter are ignored

**Example:**
```
User: "Create PDF and upload to Drive"

❌ WRONG:
Orchestrator → pdf-specialist
pdf-specialist: Creates PDF ✅
Orchestrator: Creates upload script ❌ (ignores agent's upload_to_drive tool)

✅ RIGHT:
Orchestrator: "Use pdf-specialist to create PDF and upload to Drive"
pdf-specialist:
  1. Creates PDF (pdf skill)
  2. Uploads (upload_to_drive tool - declared in YAML)
  3. Returns Drive link
```

**How to Avoid:**
- ✅ Include full workflow in agent invocation
- ✅ Let agents own entire workflow (create + upload + deliver)
- ✅ Check agent's YAML frontmatter for declared tools
- ❌ Don't split tasks between orchestrator and agent

---

### 🚨 Pitfall 3: Not Checking Agent's Declared Tools

**Problem:** Creating new implementations when agent already has the tool declared.

**Example:**
```yaml
# pdf-specialist.md YAML frontmatter
---
name: PDF Specialist
tools:
  - upload_to_drive  ✅ ALREADY DECLARED
  - generate_pdf
---
```

**What This Means:**
- Agent will use `tools.upload_to_drive` automatically
- Orchestrator should NEVER create upload scripts
- Agent definition shows exact usage (lines 206-215 in pdf-specialist.md)

**How to Avoid:**
1. Before invoking agent, read its YAML frontmatter
2. Check what tools are declared
3. Trust agent will use those tools
4. Don't create duplicate implementations

---

### 🚨 Pitfall 4: Ignoring Agent's Configuration Instructions

**Problem:** Agent definitions specify which memory files to read, but orchestrator tells agent to read them anyway.

**Example:**
```markdown
# gmail-agent.md
## ⚙️ Configuration Files (READ FIRST)
1. **memory/email_config.json** - Email defaults
```

**What This Means:**
- Agent ALREADY KNOWS to read email_config.json
- Orchestrator shouldn't mention it in invocation
- Agent reads config automatically at task start

**Wrong Invocation:**
```
❌ "Use gmail-agent. Read memory/email_config.json. Send email..."
   → Triggers script creation mode
```

**Correct Invocation:**
```
✅ "Use gmail-agent to send whitepaper.pdf"
   → Agent reads config automatically
```

---

### 🚨 Pitfall 5: Not Trusting Skills

**Problem:** Creating Python scripts when agents have skills that already handle the task.

**Example - PDF Skill:**
```yaml
# pdf-specialist.md
skills:
  - pdf        # Includes pypdf, pdfplumber, AND reportlab
  - pdf-filler
  - canvas-design
```

**What the pdf skill includes:**
- pypdf - Read, merge, split PDFs
- pdfplumber - Extract text and tables
- **reportlab** - Create styled PDFs from scratch ✅

**Wrong Assumption:**
```
❌ "pdf skill only reads PDFs, need to create script for PDF generation"
   → Creates standalone reportlab script
```

**Correct Understanding:**
```
✅ "pdf skill includes reportlab for PDF creation"
   → Agent uses skill's reportlab capabilities
   → Read SKILL.md to verify: .claude/skills/document-skills/pdf/SKILL.md
```

**How to Avoid:**
1. Read skill documentation (`.claude/skills/*/SKILL.md`)
2. Understand skill capabilities before creating scripts
3. Trust agents to use skills properly

---

### 🔧 How to Fix These Pitfalls

**Step 1: Update Your Invocation Pattern**
```
From: "Use [agent]. Read X. Import Y. Call Z..."
To:   "Use [agent] to [goal] with [context]"
```

**Step 2: Check Agent Definitions**
```bash
# Before invoking, check what agent has:
cat .claude/agents/pdf-specialist.md | head -20

# Look for:
# - tools: [...] in YAML frontmatter
# - skills: [...] in YAML frontmatter
# - Configuration Files section
```

**Step 3: Trust Agent Autonomy**
- Agent knows which tools to use
- Agent knows which files to read
- Agent knows how to complete workflow
- Your job: Specify WHAT, not HOW

**Step 4: Let Agents Own Workflows**
- If agent creates file → agent uploads file
- If agent has upload_to_drive tool → agent will use it
- Orchestrator routes, agents execute

---

### 📚 Learn More

For comprehensive guide on proper agent invocation:
- **[AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)** - Complete guide with examples, decision trees, and troubleshooting
- **[claude.md](claude.md)** - Repository navigation with agent invocation guidelines
- **Agent Definitions:** `.claude/agents/*.md` files show declared tools and workflows

---

## Quick Start Checklist

✅ **Verify agents exist:**
```bash
ls .claude/agents/                   # Should show 5 .md files (supervisor, oracle, reviewers)
ls MARKETING_TEAM/.claude/agents/    # Should show 18 .md files
ls QA_TEAM/.claude/agents/           # Should show 5 .md files
ls ENGINEERING_TEAM/.claude/agents/  # Should show 15 .md files
ls PROPOSAL_TEAM/.claude/agents/     # Should show 3 .md files
ls FINANCIAL_TEAM/.claude/agents/    # Should show 14 .md files
ls SALES_TEAM/.claude/agents/        # Should show 9 .md files
ls VOICE_TEAM/.claude/agents/        # Should show 3 .md files
ls HEDGE_FUND/.claude/agents/        # Should show 1 .md file
```

✅ **Try your first agent:**
```
You: "Use the copywriter subagent to write a short blog intro about AI"
```

✅ **Try automatic delegation:**
```
You: "Create a LinkedIn post about productivity"
```

✅ **Try multi-agent:**
```
You: "Use router-agent to create a mini social media campaign"
```

---

## The Bottom Line

**Your agent systems are READY TO USE right now.**

- ✅ 73 agents perfectly defined across 8 teams
  - 18 MARKETING + 5 QA + 15 ENGINEERING + 3 PROPOSAL + 14 FINANCIAL + 9 SALES + 3 VOICE + 1 HEDGE_FUND + 5 ROOT
- ✅ Tools properly registered
- ✅ No setup required
- ✅ No Python code to run
- ✅ Just talk to Claude Code
- ✨ **FINANCIAL_TEAM** (14 agents) - PE/M&A + General Finance + Trading Optimization
- ✨ **SALES_TEAM** (9 agents) - Full sales lifecycle
- ✨ NEW: **Supervisor Agent** - Root-level quality assurance for verifying task completion
- ✨ NEW: System architect with professional flow diagrams
- ✨ NEW: Lead generation with Bright Data (5,000 free requests/month)

**Start using them:**
```
"Use the [agent-name] subagent to [what you want]"
```

That's it! 🚀

---

## Next Steps

1. **Try invoking an agent** from the examples above
2. **Read agent definitions** in `.claude/agents/` to understand capabilities
3. **Experiment with auto-delegation** by just describing tasks
4. **Create your own agents** when needed
5. **Give feedback** so I can improve agent behavior

**Ready to start?** Just tell me which agent you want to use and what you want to accomplish!
