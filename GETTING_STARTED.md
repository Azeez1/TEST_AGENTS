# Getting Started with TEST_AGENTS

Welcome! This guide will get you up and running with the TEST_AGENTS multi-agent system in **5 minutes**.

## What is TEST_AGENTS?

TEST_AGENTS is a sophisticated multi-agent system with **59 specialized AI agents** across 7 teams:
- **MARKETING_TEAM** (18 agents) - Content, campaigns, research, automation, newsletters
- **ENGINEERING_TEAM** (15 agents) - CTO + 14 specialists (DevOps, security, frontend, backend, AI)
- **QA_TEAM** (5 agents) - Test creation, fixtures, edge cases
- **PROPOSAL_TEAM** (1 agent) - RFP parsing and proposal generation
- **FINANCIAL_TEAM** (10 agents) - PE/M&A, valuations, FP&A, accounting, tax
- **SALES_TEAM** (8 agents) - SDR, AE, sales ops, proposals, customer success
- **ROOT** (1 supervisor) - Cross-team quality verification
- **USER_STORY_AGENT** (1 system) - User story management

## Quick Start (5 Minutes)

### Step 1: Clone and Navigate
```bash
git clone <repository-url>
cd TEST_AGENTS
```

### Step 2: Understand the Structure
```
TEST_AGENTS/
├── claude.md                    # Navigation hub (START HERE)
├── MULTI_AGENT_GUIDE.md        # Complete agent reference
├── GOVERNANCE_OVERVIEW.md      # Governance rules map
├── GETTING_STARTED.md          # This file
│
├── MARKETING_TEAM/             # 18 marketing agents
├── ENGINEERING_TEAM/           # 15 engineering agents
├── QA_TEAM/                    # 5 QA agents
├── PROPOSAL_TEAM/              # 1 proposal agent
├── FINANCIAL_TEAM/             # 10 finance agents (NEW)
├── SALES_TEAM/                 # 8 sales agents (NEW)
├── USER_STORY_AGENT/           # User story management
│
├── .claude/
│   ├── agents/                 # Agent definitions
│   ├── commands/               # Slash commands
│   └── skills/                 # Custom skills
│
└── memory/                     # Configuration files
    ├── brand_voice.json
    ├── email_config.json
    └── google_drive_config.json
```

### Step 3: Configure API Keys (Optional)

If you plan to use specific agents, configure API keys:

**For MARKETING_TEAM:**
- OpenAI API key (GPT-4, DALL-E, image generation)
- Google API credentials (Drive, Gmail, Sheets)
- Perplexity API key (research)
- Bright Data API key (web scraping)
- Gemini API key (video generation with Veo)

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) for detailed setup instructions.

### Step 4: Your First Agent Invocation

Use the simple invocation pattern:

```
Task(agent-name): Do X
```

**Example 1: Content Creation**
```
Task(copywriter): Write a blog post about AI automation trends in 2025
```

**Example 2: Code Review**
```
Task(code-reviewer): Review the authentication module for security issues
```

**Example 3: Research**
```
Task(research-agent): Find the top 10 SaaS companies in the project management space
```

### Step 5: Explore Agent Capabilities

**See all agents:**
- Read [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - Complete agent directory
- Or check team-specific READMEs:
  - [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md)
  - [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md)
  - [QA_TEAM/README.md](QA_TEAM/README.md)
  - [PROPOSAL_TEAM/README.md](PROPOSAL_TEAM/README.md)

## Common Use Cases

### Use Case 1: Create Marketing Campaign
```
Task(content-strategist): Plan a product launch campaign for our new AI tool

[Agent coordinates with copywriter, visual-designer, email-specialist]
```

### Use Case 2: Build Feature with Tests
```
Task(cto): Build a user authentication system with comprehensive tests

[Agent coordinates backend-architect, test-engineer, security-auditor]
```

### Use Case 3: Generate Proposal
```
Task(rfp-agent): Parse this RFP and generate a winning proposal
```

### Use Case 4: Quality Verification
```
Task(supervisor): Verify that the marketing campaign meets all quality standards

[Supervisor checks deliverables across all teams]
```

## Key Concepts

### 1. Agent Invocation Pattern
Always use: `Task(agent-name): Clear instruction`

**Good:**
```
Task(copywriter): Write a 500-word blog post about remote work trends
```

**Bad:**
```
Task(copywriter): {
  "type": "blog_post",
  "topic": "remote work",
  "length": 500
}
```

### 2. Multi-Agent Coordination
Agents coordinate automatically:

```
Task(content-strategist): Create email campaign for product launch

[content-strategist coordinates:]
→ copywriter (drafts email)
→ editor (reviews brand voice)
→ email-specialist (finalizes campaign)
→ gmail-agent (sends emails)
```

### 3. Memory System
Agents read configuration from `memory/` directory:
- `brand_voice.json` - Brand voice guidelines (Dux Machina)
- `email_config.json` - Email templates and settings
- `visual_guidelines.json` - Design standards

**See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) for details.

### 4. Quality Verification
Use the `supervisor` agent for cross-team verification:

```
Task(supervisor): Verify [deliverable] meets quality standards

[Supervisor returns:]
- Verification Status: PASS/FAIL
- Quality Score: 0-100
- Issues Found: [list]
- Recommendations: [improvements]
```

## Documentation Navigation

**New Users (Read First):**
1. [claude.md](claude.md) - Repository navigation hub
2. [GETTING_STARTED.md](GETTING_STARTED.md) - This guide
3. [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All 39 agents explained
4. [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - Invocation patterns

**Core Documentation:**
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - Configuration guide
- [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) - Workspace validation
- [SUPERVISOR_ARCHITECTURE.md](SUPERVISOR_ARCHITECTURE.md) - Quality verification

**Governance (For Maintainers):**
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - Governance map
- [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md) - Tool priority hierarchy
- [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Complete tool inventory
- [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md) - Pre-creation checklist

**Reference:**
- [GLOSSARY.md](GLOSSARY.md) - Terms and definitions
- [FAQ.md](FAQ.md) - Common questions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Debugging guide
- [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - API configuration

## Next Steps

**Option 1: Dive Into Marketing**
Read [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md) and try:
```
Task(copywriter): Write a welcome email for new users
```

**Option 2: Explore Engineering**
Read [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) and try:
```
Task(system-architect): Design a microservices architecture for an e-commerce platform
```

**Option 3: Try Quality Assurance**
Read [QA_TEAM/README.md](QA_TEAM/README.md) and try:
```
Task(test-orchestrator): Create comprehensive tests for the user authentication module
```

**Option 4: Generate a Proposal**
Read [PROPOSAL_TEAM/README.md](PROPOSAL_TEAM/README.md) and try:
```
Task(rfp-agent): Parse this RFP and generate a proposal
```

## Need Help?

- **Common Questions:** See [FAQ.md](FAQ.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Agent Invocation Issues:** See [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)
- **Governance Questions:** See [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md)

## Key Reminders

1. **Always use simple invocation:** `Task(agent-name): Do X`
2. **Never create JSON/script prompts** - Use natural language
3. **Agents coordinate automatically** - Don't micromanage
4. **Use supervisor for verification** - Quality assurance built-in
5. **Configure memory files** - Personalize agent behavior

---

**Ready to go?** Start with [claude.md](claude.md) for complete navigation, or dive into a team README!

**Questions?** Check [FAQ.md](FAQ.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
