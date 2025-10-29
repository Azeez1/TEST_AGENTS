# 🤖 The Definitive Guide to Using Your Multi-Agent Systems

## The Simple Truth

**You have 38 perfectly defined AI agents ready to use RIGHT NOW.**

This includes a **root-level Supervisor Agent** for quality assurance across all teams.

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

### You Have 37 Agents

**MARKETING_TEAM (17 agents):**
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

**QA_TEAM (5 agents):**
- test-orchestrator - Testing coordinator
- unit-test-agent - Unit test generation
- integration-test-agent - Integration tests
- edge-case-agent - Edge case identification
- fixture-agent - Pytest fixtures

**ENGINEERING_TEAM (14 agents) ⭐ SUPER TEAM:**
- cto - Strategic coordinator & intelligent routing for all specialists
- devops-engineer - CI/CD, Terraform, Kubernetes, monitoring, security scanning
- frontend-developer - React, responsive design, state management, accessibility
- backend-architect - RESTful APIs, microservices, database schema, scalability
- security-auditor - Code security, vulnerability scanning, compliance audits
- technical-writer - PRDs, technical specs, API docs, architecture diagrams
- system-architect - ✨ **NEW** System architecture design & professional flow diagrams
- ai-engineer - LLM integration, RAG systems, prompt optimization, agent frameworks
- ui-ux-designer - User research, wireframes, design systems, user flows
- code-reviewer - Quality, security, maintainability reviews (3.2K downloads)
- test-engineer - Test automation, QA strategy, CI/CD testing (1.3K downloads)
- prompt-engineer - LLM prompt optimization, techniques, benchmarking (2.4K downloads)
- database-architect - Database design, data modeling, scalability (1.2K downloads)
- debugger - Root cause analysis, troubleshooting, error investigation (1.7K downloads)

**USER_STORY_AGENT (1 system):**
- Streamlit application for converting meeting notes to user stories with Excel export

**ROOT SUPERVISOR (1 agent):** ⭐ QUALITY ASSURANCE
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
  - **Example**: "Use supervisor to verify the authentication feature is complete and ready for deployment"

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
You: "Use the test-orchestrator subagent to scan USER_STORY_AGENT and generate tests"

Me: [Reading QA_TEAM/.claude/agents/test-orchestrator.md...]

I'll coordinate comprehensive test generation for USER_STORY_AGENT.

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
- `MARKETING_TEAM/.claude/agents/` - 16 marketing agents (including new lead-gen-agent)
- `QA_TEAM/.claude/agents/` - 5 testing agents
- Plus USER_STORY_AGENT Streamlit system

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

## Quick Start Checklist

✅ **Verify agents exist:**
```bash
ls .claude/agents/                   # Should show 1 .md file (supervisor)
ls MARKETING_TEAM/.claude/agents/    # Should show 17 .md files
ls QA_TEAM/.claude/agents/           # Should show 5 .md files
ls ENGINEERING_TEAM/.claude/agents/  # Should show 14 .md files
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

- ✅ 38 agents perfectly defined (17 marketing + 5 testing + 14 engineering + 1 user story system + 1 root supervisor)
- ✅ Tools properly registered
- ✅ No setup required
- ✅ No Python code to run
- ✅ Just talk to Claude Code
- ✨ NEW: **Supervisor Agent** - Root-level quality assurance for verifying task completion
- ✨ NEW: System architect with professional flow diagrams
- ✨ NEW: Flow-diagram skill for Mermaid visualizations
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
