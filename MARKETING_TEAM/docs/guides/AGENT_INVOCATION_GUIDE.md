# Agent Invocation Guide - MARKETING_TEAM

## 📋 Table of Contents

- [Core Principles](#core-principles)
- [Quick Reference](#quick-reference)
- [Agent-by-Agent Examples](#agent-by-agent-examples)
- [Common Mistakes](#common-mistakes)
- [Troubleshooting](#troubleshooting)
- [Decision Trees](#decision-trees)

---

## Core Principles

### The Golden Rule

**Agents are autonomous systems with pre-configured tools, memory, and workflows.**

Your job: Specify **WHAT** you want
Agent's job: Figure out **HOW** to do it

### Three-Part Invocation Pattern

```
"Use [agent-name] to [goal] with [context]"
```

**Parts:**
1. **Agent name** - Which specialized agent to use
2. **Goal** - What deliverable or outcome you want
3. **Context** - Key details (audience, tone, constraints, subject matter)

### What NOT to Include

❌ File paths to read
❌ Function names to call
❌ Implementation steps
❌ Tool import statements
❌ Memory file references
❌ Library installation commands

**Why:** Agents already know this from their definitions.

---

## Quick Reference

| Agent | Use When | Minimal Invocation Example |
|-------|----------|----------------------------|
| **gmail-agent** | Sending emails with/without attachments | `"Use gmail-agent to send whitepaper.pdf"` |
| **copywriter** | Blog posts, articles, web copy | `"Use copywriter to write 2000-word blog about AI automation"` |
| **social-media-manager** | LinkedIn/Twitter posts | `"Use social-media-manager to create LinkedIn post about product launch"` |
| **visual-designer** | Images via GPT-4o | `"Use visual-designer to create LinkedIn header with brand colors"` |
| **video-producer** | Videos via Sora | `"Use video-producer to create 15-second product demo"` |
| **pdf-specialist** | PDFs, whitepapers, lead magnets | `"Use pdf-specialist to create 12-page whitepaper about AI agents"` |
| **presentation-designer** | PowerPoint decks | `"Use presentation-designer to create 10-slide pitch deck"` |
| **email-specialist** | Email sequences, newsletters | `"Use email-specialist to write 3-email welcome sequence"` |
| **landing-page-specialist** | Landing pages with UX/code | `"Use landing-page-specialist to create SaaS signup page"` |
| **seo-specialist** | Keyword research, SERP analysis | `"Use seo-specialist to research AI marketing keywords"` |
| **research-agent** | Market research, competitive intel | `"Use research-agent to research AI automation trends"` |
| **lead-gen-agent** | B2B/local lead generation | `"Use lead-gen-agent to find 50 B2B SaaS companies in SF"` |
| **analyst** | Performance analysis, benchmarking | `"Use analyst to analyze Q4 campaign performance"` |
| **editor** | Content review, brand voice check | `"Use editor to review blog post for brand compliance"` |
| **router-agent** | Multi-agent campaign coordination | `"Use router-agent to plan product launch campaign"` |
| **content-strategist** | Full campaign orchestration | `"Use content-strategist to plan Q1 content calendar"` |
| **automation-agent** | n8n workflow automation | `"Use automation-agent to create lead nurture workflow"` |

---

## Agent-by-Agent Examples

### Gmail Agent

**Agent Definition:** `MARKETING_TEAM/.claude/agents/gmail-agent.md`

**What It Knows:**
- ✅ Reads `memory/email_config.json` automatically for email addresses
- ✅ Has `send_email_with_attachment` tool declared
- ✅ Knows when to use Python tool vs MCP tool
- ✅ Automatically converts plaintext to HTML for proper formatting
- ✅ Supports branded email templates

**✅ CORRECT Invocations:**

```
"Use gmail-agent to send whitepaper.pdf"
→ Agent reads config, uses tool, sends with branded template

"Use gmail-agent to send AI_Marketing_Report.pdf with executive summary"
→ Agent creates professional email body with summary, attaches file

"Use gmail-agent to send campaign_results.xlsx to stakeholders"
→ Agent reads recipients from config, sends with context-appropriate message
```

**❌ INCORRECT Invocations:**

```
"Use gmail-agent. Read memory/email_config.json. Import send_email_with_attachment.py.
Call the function with to_email='sabaazeez12@gmail.com', attachment_path='whitepaper.pdf'..."
→ CREATES DUPLICATE SCRIPT instead of using agent

"Use gmail-agent to send email. First check if token.pickle exists, then authenticate
with Gmail API, then create MIME message..."
→ Over-specification triggers script creation mode
```

**Real Issue from Repository:**
- File created: `send_content_suite_emails.py` (108 lines)
- What happened: Over-specified invocation → Claude created standalone script
- Should have been: `"Use gmail-agent to send content suite deliverables"`

---

### PDF Specialist

**Agent Definition:** `MARKETING_TEAM/.claude/agents/pdf-specialist.md`

**What It Knows:**
- ✅ Has `pdf` skill declared for comprehensive PDF creation
- ✅ Reads `memory/brand_voice.json` and `memory/visual_guidelines.json`
- ✅ Knows when to use pdf skill vs pdf-filler vs canvas-design
- ✅ Uploads to Google Drive using `upload_to_drive` tool
- ✅ Invokes editor for marketing PDFs automatically

**✅ CORRECT Invocations:**

```
"Use pdf-specialist to create 12-page whitepaper about AI agent transformation"
→ Agent chooses pdf skill, reads brand guidelines, creates professional PDF

"Use pdf-specialist to create fillable registration form"
→ Agent recognizes form requirement, uses pdf-filler skill

"Use pdf-specialist to create one-page marketing flyer"
→ Agent uses canvas-design skill for visual quality
```

**❌ INCORRECT Invocations:**

```
"Use pdf-specialist. Install reportlab. Create PDF using reportlab.lib.pagesizes..."
→ CREATES DUPLICATE SCRIPT instead of using pdf skill

"Use pdf-specialist. Read brand_voice.json. Import pdf_generator.py. Call generate_pdf()..."
→ Over-specification triggers script creation
```

**Real Issue from Repository:**
- File created: `create_whitepaper_pdf.py` (254 lines)
- What happened: PDF creation manually scripted with reportlab
- Should have been: `"Use pdf-specialist to create whitepaper"`

---

### Copywriter

**Agent Definition:** `MARKETING_TEAM/.claude/agents/copywriter.md`

**What It Knows:**
- ✅ Reads `memory/brand_voice.json` for tone and style
- ✅ Has Google Workspace MCP tools for Docs creation
- ✅ Invokes editor automatically for brand voice review
- ✅ Knows Dux Machina voice principles (Tech Samurai meets McKinsey)

**✅ CORRECT Invocations:**

```
"Use copywriter to write 2500-word blog about AI agent economics with cost comparison"
→ Agent reads brand voice, writes in Dux style, invokes editor

"Use copywriter to create case study about Shopify AI implementation"
→ Agent researches (if needed), writes with data, maintains voice

"Use copywriter to write product description for AI agent platform"
→ Agent creates concise, benefit-focused copy with brand voice
```

**❌ INCORRECT Invocations:**

```
"Use copywriter. Read brand_voice.json. Write blog with these sections: 1) intro,
2) problem, 3) solution... Use these exact phrases..."
→ Over-specification removes agent creativity

"Use copywriter to write blog. Then save to outputs/blog_posts/. Then invoke editor.
Then revise if needed..."
→ Agent already knows this workflow
```

---

### Visual Designer

**Agent Definition:** `MARKETING_TEAM/.claude/agents/visual-designer.md`

**What It Knows:**
- ✅ Has `openai_gpt4o_image` tool (via marketing-tools MCP)
- ✅ Has algorithmic-art, canvas-design, theme-factory skills
- ✅ Reads `memory/visual_guidelines.json` for brand colors
- ✅ Uploads to Google Drive automatically

**✅ CORRECT Invocations:**

```
"Use visual-designer to create LinkedIn header image about AI automation"
→ Agent reads brand colors, uses GPT-4o, creates 1200x627 image

"Use visual-designer to create Instagram post graphic with algorithmic art"
→ Agent uses algorithmic-art skill, generates unique visual

"Use visual-designer to create presentation theme with brand colors"
→ Agent uses theme-factory skill, applies Dux Machina palette
```

**❌ INCORRECT Invocations:**

```
"Use visual-designer. Import openai_gpt4o_image.py. Call generate_gpt4o_image()
with prompt='...', aspect_ratio='3:2'..."
→ Over-specification triggers script creation

"Use visual-designer. First check if OPENAI_API_KEY exists. Then call API..."
→ Agent handles authentication internally
```

---

### Social Media Manager

**Agent Definition:** `MARKETING_TEAM/.claude/agents/social-media-manager.md`

**What It Knows:**
- ✅ Reads `memory/brand_voice.json` for messaging
- ✅ Has platform formatters for LinkedIn/Twitter character limits
- ✅ Creates hashtags automatically
- ✅ Can generate GIFs with slack-gif-creator skill

**✅ CORRECT Invocations:**

```
"Use social-media-manager to create LinkedIn post about AI cost savings"
→ Agent writes 150-200 words, adds hashtags, professional tone

"Use social-media-manager to create 5-tweet thread about agent economics"
→ Agent breaks into 280-char tweets, maintains narrative flow

"Use social-media-manager to create animated GIF post for product launch"
→ Agent uses slack-gif-creator skill, creates engaging visual
```

---

### Email Specialist

**Agent Definition:** `MARKETING_TEAM/.claude/agents/email-specialist.md`

**What It Knows:**
- ✅ Reads `memory/brand_voice.json`
- ✅ Creates subject lines with A/B test alternatives
- ✅ Invokes editor for brand voice review
- ✅ Outputs clean plaintext (no markdown symbols)

**✅ CORRECT Invocations:**

```
"Use email-specialist to write 3-email welcome sequence for SaaS product"
→ Agent creates emails with proper spacing, CTAs, subject lines

"Use email-specialist to write newsletter about Q4 AI trends"
→ Agent researches (if needed), writes engaging content

"Use email-specialist to create abandoned cart email"
→ Agent writes persuasive recovery email with urgency
```

---

### Landing Page Specialist

**Agent Definition:** `MARKETING_TEAM/.claude/agents/landing-page-specialist.md`

**What It Knows:**
- ✅ Conducts competitor analysis with Bright Data MCP
- ✅ Uses artifacts-builder skill for React landing pages
- ✅ Creates UX wireframes before coding
- ✅ Provides conversion optimization recommendations

**✅ CORRECT Invocations:**

```
"Use landing-page-specialist to create SaaS signup page for AI agent platform"
→ Agent researches competitors, designs UX, builds React artifact

"Use landing-page-specialist to optimize existing landing page for conversions"
→ Agent analyzes current page, provides recommendations

"Use landing-page-specialist to create webinar registration page"
→ Agent designs form-focused layout, clear CTA, social proof
```

---

### Research Agent

**Agent Definition:** `MARKETING_TEAM/.claude/agents/research-agent.md`

**What It Knows:**
- ✅ Has custom Perplexity research tools (perplexity_research.py, perplexity_research_tool.py)
- ✅ Falls back to Perplexity MCP if custom tools unavailable
- ✅ Provides cited sources and data-backed insights
- ✅ Can conduct competitive intelligence

**✅ CORRECT Invocations:**

```
"Use research-agent to research AI marketing automation trends in 2025"
→ Agent uses Perplexity tools, finds 20+ sources, synthesizes findings

"Use research-agent to analyze competitor AI agent platforms"
→ Agent researches pricing, features, positioning

"Use research-agent to find case studies about AI cost savings"
→ Agent searches, verifies credibility, compiles data
```

---

### Router Agent & Content Strategist

**Agent Definition:** `MARKETING_TEAM/.claude/agents/router-agent.md`, `content-strategist.md`

**What They Know:**
- ✅ Coordinate multiple agents for complex campaigns
- ✅ Use sequential-thinking MCP for planning
- ✅ Enforce editor review for all marketing content
- ✅ Create distribution checklists

**✅ CORRECT Invocations:**

```
"Use router-agent to plan complete product launch campaign"
→ Agent coordinates: research → copywriter → social-media → email → pdf

"Use content-strategist to plan Q1 content calendar with 12 blog posts"
→ Agent creates schedule, assigns topics, coordinates agents

"Use router-agent to create webinar promotion campaign"
→ Agent orchestrates landing page, emails, social, ads
```

---

## Common Mistakes

### Mistake 1: Over-Specifying Implementation

**❌ BAD:**
```
"Use gmail-agent. First, check if token.pickle exists in the root directory.
If not, run OAuth flow. Then import send_email_with_attachment from tools/.
Read memory/email_config.json to get user_google_email and default_cc.
Call send_email_with_attachment(to_email=..., attachment_path=..., cc=...).
Use branded_light template."
```

**✅ GOOD:**
```
"Use gmail-agent to send AI_Marketing_Report.pdf"
```

**Why:** Agent definition (lines 38-54) already says "ALWAYS read memory files".
Agent knows OAuth, import paths, template selection.

---

### Mistake 2: Mentioning Tools by Name

**❌ BAD:**
```
"Use pdf-specialist with pdf_generator.py tool to create whitepaper"
```

**✅ GOOD:**
```
"Use pdf-specialist to create 12-page whitepaper about AI agents"
```

**Why:** Agent knows it has pdf skill, pdf_generator.py, and canvas-design. It chooses based on requirements.

---

### Mistake 3: Providing File Paths

**❌ BAD:**
```
"Use copywriter to write blog and save to MARKETING_TEAM/outputs/blog_posts/"
```

**✅ GOOD:**
```
"Use copywriter to write 2500-word blog about AI cost savings"
```

**Why:** Agent knows output directory structure from repository layout.

---

### Mistake 4: Dictating Workflow Steps

**❌ BAD:**
```
"Use copywriter to write blog. Then invoke editor. If editor approves, save.
If not, revise and resubmit."
```

**✅ GOOD:**
```
"Use copywriter to write blog about AI automation economics"
```

**Why:** Agent definition (lines 80-95) already includes editor review workflow.

---

### Mistake 5: Creating Standalone Scripts

**❌ BAD:**
```python
# send_my_email.py
from tools.send_email_with_attachment import send_email_with_attachment
# ... 50 lines of hardcoded email sending ...
```

**✅ GOOD:**
```
"Use gmail-agent to send deliverables with executive summary"
```

**Why:** gmail-agent already wraps the tool with proper configuration, error handling, and branding.

---

## Troubleshooting

### Problem: "Agent claims success but file doesn't exist"

**Possible Causes:**
1. Skill invocation failed silently
2. File created in unexpected location
3. Agent didn't verify file creation

**Solutions:**
1. Check exact file path agent claimed to create
2. Search entire outputs/ directory: `find outputs/ -name "*.pdf"`
3. Re-invoke agent with explicit verification request: `"Use [agent] to create [file] and verify it exists"`

---

### Problem: "Duplicate scripts keep getting created"

**Root Cause:** Over-specification in invocation

**Solution Pattern:**
```
❌ Current invocation: "Use agent. Step 1... Step 2... Step 3..."
✅ Fixed invocation: "Use agent to [goal]"

Remove all implementation details from request.
```

---

### Problem: "Agent doesn't use declared tool"

**Diagnosis:**
1. Check agent's YAML frontmatter: `tools:` list
2. Verify tool file exists in `tools/` directory
3. Check if tool requires installation (MCP servers)

**Solutions:**
1. If tool missing from YAML → Add to agent definition
2. If tool file missing → Create or restore from backup
3. If MCP server down → Check `.mcp.json` configuration

---

### Problem: "Email formatting looks broken (no line breaks)"

**Root Cause:** MCP `send_gmail_message` sent as plaintext without HTML conversion

**Solution:**
- gmail-agent automatically converts plaintext to HTML
- Uses `email_template_renderer.py` for branded templates
- Both MCP and Python tools now send HTML emails

**Prevention:** Always use gmail-agent, never invoke MCP tool directly

---

### Problem: "PDF upload creates 116-byte placeholder file"

**Root Cause:** Google Workspace MCP `create_drive_file` is broken for binary files

**Solution:**
- pdf-specialist uses `upload_to_drive.py` (Python tool) instead of MCP
- This bypasses MCP bug and uploads full file content

**Agent handles this automatically** - no action needed

---

## Decision Trees

### When to Use Which Agent?

```
Need to send communication?
├─ Email?
│   ├─ With attachment? → gmail-agent
│   └─ Without attachment? → email-specialist (writes copy) + gmail-agent (sends)
├─ Social media post?
│   └─ → social-media-manager
└─ Landing page?
    └─ → landing-page-specialist

Need to create content?
├─ Long-form (1000+ words)?
│   ├─ Blog/article? → copywriter
│   ├─ Whitepaper? → pdf-specialist
│   └─ Case study? → copywriter
├─ Visual?
│   ├─ Image? → visual-designer
│   ├─ Video? → video-producer
│   └─ Presentation? → presentation-designer
├─ Email sequence?
│   └─ → email-specialist
└─ Landing page?
    └─ → landing-page-specialist

Need research or analysis?
├─ Market research? → research-agent
├─ Competitor analysis? → research-agent or analyst
├─ Lead generation? → lead-gen-agent
├─ SEO research? → seo-specialist
└─ Performance analysis? → analyst

Need campaign coordination?
├─ Multi-agent workflow? → router-agent
├─ Content calendar? → content-strategist
└─ Workflow automation? → automation-agent

Need content review?
└─ Brand voice check? → editor (invoked automatically by content agents)
```

---

### Should I Create a Script or Invoke an Agent?

```
Task requires:
├─ Single function call with clear parameters?
│   └─ → Use tool directly (no agent needed)
├─ Domain expertise (writing, design, research)?
│   └─ → Invoke agent
├─ Multiple steps with decision-making?
│   └─ → Invoke agent
├─ Content creation with brand compliance?
│   └─ → Invoke agent (includes editor review)
└─ One-time utility or test?
    └─ → Create script in scripts/ directory
```

**Default Rule:** If an agent exists for the task, ALWAYS invoke the agent instead of creating a script.

---

## Examples from Real Repository Issues

### Issue 1: Email Sending

**What Happened:**
- Created `send_content_suite_emails.py` (108 lines)
- Hardcoded email content, recipients, file paths
- Imported tools manually

**Should Have Been:**
```
"Use gmail-agent to send content suite deliverables"
```

**Why It Went Wrong:**
- Over-specified invocation with implementation steps
- Told agent to "import send_email_with_attachment"
- Claude interpreted: "Create a script"

---

### Issue 2: PDF Creation

**What Happened:**
- Created `create_whitepaper_pdf.py` (254 lines)
- Manually imported reportlab, wrote PDF generation code
- Hardcoded whitepaper content and structure

**Should Have Been:**
```
"Use pdf-specialist to create 12-page whitepaper about AI agent transformation"
```

**Why It Went Wrong:**
- pdf-specialist has pdf skill but wasn't invoked
- Over-specification: "Install reportlab, import reportlab.lib.pagesizes..."
- Claude created standalone implementation

---

### Issue 3: Content Suite Campaign

**What Worked:**
- ✅ Invoked research-agent → Comprehensive research
- ✅ Invoked copywriter → Blog post created
- ✅ Invoked editor → Brand voice review
- ✅ Invoked social-media-manager → LinkedIn/Twitter content
- ✅ Invoked email-specialist → Email sequence

**What Broke:**
- ❌ pdf-specialist invocation unclear → PDF not created
- ❌ gmail-agent not invoked → Created script instead
- ❌ Supervisor verification delayed → Missing files not caught early

**Lesson:** Minimal invocation works. Over-specification breaks.

---

## Best Practices Checklist

Before invoking an agent:

- [ ] Check agent exists: `.claude/agents/[agent-name].md`
- [ ] Read agent definition to understand capabilities
- [ ] Formulate minimal invocation: `"Use [agent] to [goal]"`
- [ ] Include only: goal + context (no implementation)
- [ ] Avoid mentioning: tools, files, imports, steps
- [ ] Trust agent autonomy: it knows its workflow
- [ ] Let agent read memory files automatically
- [ ] Let agent choose tools based on requirements
- [ ] Let agent invoke editor if it's a content agent
- [ ] Verify deliverable after completion

---

## Summary: The One Rule

**If you find yourself writing implementation steps, STOP.**

You're about to trigger script creation mode instead of agent invocation.

**Ask:** "What is the goal?" not "How do I implement this?"

**Then:** `"Use [agent-name] to [goal]"`

That's it. Trust the agent.

---

**Last Updated:** 2025-01-29
**Applies To:** MARKETING_TEAM (17 agents)
**See Also:** [claude.md](../../../claude.md) - Repository-wide agent guidelines
