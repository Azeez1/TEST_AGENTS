# Frequently Asked Questions (FAQ)

Common questions about TEST_AGENTS multi-agent system.

## General Questions

### What is TEST_AGENTS?

TEST_AGENTS is a multi-agent system with **59 specialized AI agents** across 7 teams (MARKETING, ENGINEERING, QA, PROPOSAL, FINANCIAL, SALES, USER_STORY_AGENT, and ROOT supervisor). Each agent has specific capabilities and coordinates with other agents to complete complex tasks.

**See:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

### How many agents are there?

**Total: 59 agents**
- MARKETING_TEAM: 18 agents
- ENGINEERING_TEAM: 15 agents
- QA_TEAM: 5 agents
- PROPOSAL_TEAM: 1 agent
- FINANCIAL_TEAM: 10 agents (NEW)
- SALES_TEAM: 8 agents (NEW)
- USER_STORY_AGENT: 1 system
- ROOT: 1 supervisor

**See:** [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) for complete list

---

### Do I need to configure all agents?

No. Configure only the agents you plan to use.

**Minimum setup:**
- No API keys required for basic functionality
- Some agents work without external APIs

**Full setup:**
- OpenAI API (MARKETING, ENGINEERING content generation)
- Google Workspace (MARKETING email, drive, docs)
- Perplexity (MARKETING research)

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)

---

## Agent Invocation

### How do I invoke an agent?

Use the simple pattern:
```
Task(agent-name): Do X
```

**Examples:**
```
Task(copywriter): Write a blog post about AI automation
Task(research-agent): Find top 10 SaaS companies
Task(visual-designer): Create a hero image for landing page
```

**See:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)

---

### Can I use JSON to invoke agents?

**No.** Never use JSON or script-like syntax.

**❌ Don't do this:**
```
Task(copywriter): {
  "task_type": "blog_post",
  "topic": "AI",
  "length": 500
}
```

**✅ Do this:**
```
Task(copywriter): Write a 500-word blog post about AI
```

**Why?** Agents are designed for natural language, not structured data formats.

**See:** [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)

---

### Which agent should I use for X?

**Content Creation:**
- Blog posts, articles → `copywriter`
- Social media → `social-media-manager`
- Email campaigns → `email-specialist`
- Landing pages → `landing-page-specialist`
- PDFs, whitepapers → `pdf-specialist`
- Presentations → `presentation-designer`

**Research & Analysis:**
- Web research → `research-agent`
- Competitor analysis → `analyst`
- SEO, keywords → `seo-specialist`
- Lead generation → `lead-gen-agent`

**Visual Content:**
- Images, graphics → `visual-designer`
- Videos, UGC ads → `video-producer`

**Development:**
- Architecture → `system-architect` or `backend-architect`
- Frontend → `frontend-developer`
- Testing → `test-engineer`
- Code review → `code-reviewer`
- Debugging → `debugger`
- Security → `security-auditor`

**Quality Assurance:**
- Unit tests → `unit-test-agent`
- Integration tests → `integration-test-agent`
- Edge cases → `edge-case-agent`
- Test fixtures → `fixture-agent`

**Coordination:**
- Marketing campaigns → `content-strategist`
- Engineering projects → `cto`
- Request routing → `router-agent`
- Quality verification → `supervisor` (ROOT)

**See:** [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) for complete descriptions

---

### Can agents work together?

Yes! Agents coordinate automatically.

**Example:**
```
Task(content-strategist): Create email campaign for product launch

[content-strategist automatically coordinates:]
→ copywriter (drafts email)
→ editor (reviews brand voice)
→ email-specialist (finalizes campaign)
→ gmail-agent (sends emails)
```

You don't need to micromanage the coordination.

---

### Do I need to specify which tools agents should use?

No. Agents already know their tools from their definitions.

**Don't do this:**
```
Task(copywriter): Use GPT-4 to write a blog post
```

**Do this:**
```
Task(copywriter): Write a blog post about remote work
```

The agent knows to use its configured tools (GPT-4, brand voice config, etc.)

---

## Configuration & Setup

### Where do I put API keys?

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
PERPLEXITY_API_KEY=pplx-your-key-here
```

**Never commit API keys to git:**
```bash
echo ".env" >> .gitignore
```

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)

---

### What are memory files?

Memory files store configuration that agents read:

**MARKETING_TEAM/memory/**
- `brand_voice.json` - Brand voice guidelines
- `email_config.json` - Email defaults
- `google_drive_config.json` - Drive folder structure
- `visual_guidelines.json` - Design standards

Agents read these files to maintain consistency.

**See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

---

### Do I need to create memory files?

Yes, for MARKETING agents that need brand consistency.

**Minimum required:**
- `brand_voice.json` - For any content creation
- `email_config.json` - For gmail-agent, email-specialist
- `google_drive_config.json` - For file uploads

**See:** [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) for templates

---

### Can I customize brand voice?

Yes! Edit `MARKETING_TEAM/memory/brand_voice.json`:

```json
{
  "company_name": "Your Company",
  "voice_principles": [
    "Your principle 1",
    "Your principle 2"
  ],
  "tone": "professional yet conversational",
  "what_not_to_do": [
    "Don't use jargon",
    "Don't be overly formal"
  ]
}
```

All content agents will read this file.

---

## Governance & Tools

### Can I create custom tools?

Yes, but follow the governance process:

1. Check [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - tool might exist
2. Follow priority: **MCP → Skill → Custom Tool → Create New**
3. Complete [PRE_FLIGHT_CHECKS.md](PRE_FLIGHT_CHECKS.md)
4. Register new tool in TOOL_REGISTRY.md

**See:** [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md)

---

### What's the difference between MCP, Skill, and Custom Tool?

**MCP Servers (Highest Priority):**
- Pre-integrated external services
- Examples: `mcp__google-drive`, `mcp__gmail`
- Use these first

**Skills (Second Priority):**
- Official Claude skills in `.claude/skills/`
- Examples: `pdf`, `pptx`, `docx`, `algorithmic-art`
- Use if no MCP exists

**Custom Tools (Third Priority):**
- Team-created tools for specific needs
- Examples: `identify_edge_cases`, `analyze_function`
- Use if no MCP or skill exists

**Create New (Last Resort):**
- Only when nothing else works
- Requires governance approval

**See:** [TOOL_USAGE_POLICY.md](TOOL_USAGE_POLICY.md)

---

### Why isn't xlsx skill enabled?

The `xlsx` skill is not enabled because Google Sheets MCP is better:
- Real-time collaboration
- Cloud storage
- API integration
- No local file management

**Use instead:**
```
mcp__google-sheets__create_spreadsheet
mcp__google-sheets__read_sheet
```

**See:** [TOOL_REGISTRY.md](TOOL_REGISTRY.md) - Document Generation section

---

## Workflows & Best Practices

### How does the editor review workflow work?

For brand-facing content (blogs, emails, social media, landing pages):

1. Agent creates content
2. Agent invokes editor: `Task(editor): Review [content]`
3. Editor checks brand voice compliance (target: 7+ out of 10)
4. If approved → deliver to user
5. If revisions needed → agent revises and returns to step 2

**This is mandatory for:**
- copywriter (external content)
- email-specialist (marketing emails)
- landing-page-specialist (all pages)
- pdf-specialist (marketing PDFs)
- presentation-designer (client-facing)
- social-media-manager (all posts)

---

### What is the supervisor agent?

The `supervisor` agent performs cross-team quality verification:

```
Task(supervisor): Verify [deliverable] meets quality standards

[Returns:]
- Verification Status: PASS/FAIL
- Quality Score: 0-100
- Issues Found: [list]
- Recommendations: [improvements]
```

Use supervisor for:
- Final deliverable QA
- Cross-team coordination verification
- Quality gate before delivery

**See:** [SUPERVISOR_ARCHITECTURE.md](SUPERVISOR_ARCHITECTURE.md)

---

### Can I skip the editor review?

**For internal content:** Yes (emails to teammates, internal docs)

**For external content:** No, editor review is mandatory:
- Blog posts
- Social media
- Landing pages
- Marketing emails
- Client presentations
- PDFs, whitepapers

**Why?** Brand consistency and quality control. Editor catches brand drift before publication.

---

## Workspace & Files

### What are absolute paths and why do I need them?

**Absolute path:** Full path from root
```
/home/user/TEST_AGENTS/MARKETING_TEAM/memory/brand_voice.json
```

**Relative path:** Path from current directory
```
memory/brand_voice.json  # Where is "memory"? Ambiguous!
```

**Why use absolute paths?**
- Prevents "file not found" errors
- Enables multi-agent coordination
- Makes debugging easier
- Required for workspace validation

**See:** [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md)

---

### Why do I keep getting "file not found" errors?

**Common causes:**

1. **Using relative paths**
   ```python
   # BAD
   path = "outputs/report.json"

   # GOOD
   path = "/home/user/TEST_AGENTS/MARKETING_TEAM/outputs/report.json"
   ```

2. **Wrong working directory**
   ```bash
   # Check where you are
   pwd
   # Should be: /home/user/TEST_AGENTS
   ```

3. **File doesn't exist**
   ```bash
   # Find the file
   find . -name "report.json"
   ```

**See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Workspace & File Path Issues

---

### Can agents read files from other teams?

**Team-specific files (memory/):** No
- Each team has its own memory folder
- Don't read from other teams' memory

**Shared resources:** Yes
- TOOL_REGISTRY.md
- MULTI_AGENT_GUIDE.md
- Governance docs
- MCP servers

**Cross-team outputs:** Yes, if explicitly requested
- MARKETING agent can read ENGINEERING output if user requests it
- Use absolute paths

---

## Git & Version Control

### What branch should I push to?

Always push to branches starting with `claude/` and ending with session ID:

**Format:**
```
claude/{feature-name}-{session-id}
```

**Example:**
```
claude/cleanup-docs-01694mTUfmUevsSwYpgbUTQY
```

**Why?** Security and organization. Only `claude/*` branches accepted by remote.

---

### Push fails with 403 error. Why?

**Common causes:**

1. **Branch name doesn't start with `claude/`**
   ```bash
   # Wrong
   git push origin feature-branch  # 403 error

   # Correct
   git push origin claude/feature-branch-sessionid
   ```

2. **Branch doesn't end with session ID**
   - Verify full branch name includes session ID

3. **Network error**
   - Retry with exponential backoff (2s, 4s, 8s, 16s)

**See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Git Issues

---

## Performance & Costs

### How much do the APIs cost?

**Estimated monthly costs** (varies by usage):

**Light usage (testing):** $10-20/month
- OpenAI: ~$5-10
- Google Workspace: Free tier
- Perplexity: ~$5-10

**Medium usage (regular use):** $50-100/month
- OpenAI: ~$20-40
- Google Workspace: Free tier
- Perplexity: ~$20-30
- Bright Data: ~$10-20

**Heavy usage (production):** $200+/month
- OpenAI: ~$100+
- Google Workspace: May need paid tier
- Perplexity: ~$50+
- Bright Data: ~$50+

**Cost controls:**
- Set monthly budget caps in provider dashboards
- Monitor usage regularly
- Use caching for repeated requests

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Cost Considerations sections

---

### Why is the agent slow to respond?

**Common causes:**

1. **External API latency**
   - OpenAI, Perplexity, Gemini can be slow during peak times
   - Check status pages

2. **Complex request**
   - Large tasks take longer
   - Break into smaller chunks

3. **Rate limiting**
   - You hit API rate limit
   - Wait or upgrade tier

4. **Network issues**
   - Check internet connection
   - Try again

**See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Performance Issues

---

## Documentation

### Where do I start?

**New users:**
1. [README.md](README.md) - Project overview
2. [GETTING_STARTED.md](GETTING_STARTED.md) - 5-minute quick start
3. [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All agents explained
4. [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - How to use agents

**For specific teams:**
- [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md)
- [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md)
- [QA_TEAM/README.md](QA_TEAM/README.md)
- [PROPOSAL_TEAM/README.md](PROPOSAL_TEAM/README.md)

**For governance:**
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - Governance map

---

### What's the difference between all these README files?

**Root level:**
- [README.md](README.md) - Project overview
- [claude.md](claude.md) - Repository navigation hub

**Team level:**
- [MARKETING_TEAM/README.md](MARKETING_TEAM/README.md) - MARKETING agents
- [ENGINEERING_TEAM/README.md](ENGINEERING_TEAM/README.md) - ENGINEERING agents
- [QA_TEAM/README.md](QA_TEAM/README.md) - QA agents
- [PROPOSAL_TEAM/README.md](PROPOSAL_TEAM/README.md) - PROPOSAL agents

**Agent level:**
- Each agent has its own definition in `.claude/agents/`

---

### Where is the documentation index?

**Coming soon:** DOCUMENTATION.md

**For now, use:**
- [claude.md](claude.md) - Navigation hub
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - Governance docs
- [GETTING_STARTED.md](GETTING_STARTED.md) - Setup guide

---

## Troubleshooting

### Where do I go if something breaks?

1. **Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Most issues covered
2. **Check [FAQ.md](FAQ.md)** - This document
3. **Check agent-specific docs** - Team READMEs
4. **Check [GLOSSARY.md](GLOSSARY.md)** - Terms and definitions

---

### How do I report a bug?

1. **Document the issue:**
   - What were you trying to do?
   - What error occurred?
   - Steps to reproduce

2. **Check if it's a known issue:**
   - See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - See this FAQ

3. **Create issue in repository:**
   - Include error message
   - Include relevant configuration
   - Include steps to reproduce

---

## Advanced Topics

### Can I create my own agents?

Yes! Follow the agent definition template.

**See:**
- [WORKSPACE_ENFORCEMENT.md](WORKSPACE_ENFORCEMENT.md) - Required sections
- [AGENT_GOVERNANCE_RULES.md](AGENT_GOVERNANCE_RULES.md) - Governance rules
- Existing agents as templates (editor, supervisor are excellent examples)

---

### How do I add a new MCP server?

1. **Install MCP server:**
   ```bash
   npm install -g @modelcontextprotocol/server-{name}
   ```

2. **Configure in Claude desktop:**
   Edit `claude_desktop_config.json`

3. **Register in TOOL_REGISTRY.md:**
   Document the new MCP server

4. **Update agent definitions:**
   Add to relevant agents' `tools:` section

**See:** [MCP_SETUP.md](MCP_SETUP.md)

---

### Can I run this in production?

Yes, but consider:

1. **API costs** - Monitor usage and set budgets
2. **Rate limits** - Upgrade tiers as needed
3. **Security** - Use secret managers, not .env files
4. **Monitoring** - Track agent performance
5. **Error handling** - Implement robust retry logic

**See:** [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - Security Best Practices

---

## Still Have Questions?

**Check these resources:**
- [GETTING_STARTED.md](GETTING_STARTED.md) - Setup guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Debugging guide
- [GLOSSARY.md](GLOSSARY.md) - Terms and definitions
- [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md) - Governance rules
- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - All agents
- [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md) - Invocation patterns

**Or create an issue in the repository with your question.**
