# 🤖 MARKETING_TEAM - Multi-Agent Marketing System

**16 AI marketing agents powered by Claude Agent SDK - ready to use through Claude Code**

Create complete marketing campaigns and generate business leads through natural conversation. Generate blog posts, social content, images, videos, emails, leads, and more by simply talking to your AI marketing team.

---

## 🚀 Quick Start

**No Python code to run. No setup. Just talk to Claude Code:**

```
You: "Use the social-media-manager subagent to create a LinkedIn post about AI trends"

Claude: [Creates professional LinkedIn post with hashtags and formatting]
```

**That's it!** Your 16 agents are ready to use right now.

---

## 📚 **READ THIS FIRST**

### Getting Started
**👉 [docs/getting-started/api-setup.md](docs/getting-started/api-setup.md)** - **START HERE:** API setup for images, videos, emails

### User Guides
**👉 [docs/guides/usage-guide.md](docs/guides/usage-guide.md)** - Complete usage guide with examples

**👉 [docs/guides/campaign-examples.md](docs/guides/campaign-examples.md)** - Real campaign examples and results

**👉 [../MULTI_AGENT_GUIDE.md](../MULTI_AGENT_GUIDE.md)** - Universal guide for all agents

### Technical Documentation
**👉 [docs/architecture/system-architecture.md](docs/architecture/system-architecture.md)** - System architecture and design

These guides explain:
- How to set up APIs (OpenAI, Gmail, Google Drive)
- How to invoke each of the 16 agents
- Real-world examples with actual output
- Common workflows
- Tips & best practices

---

## 🤖 Your 16 Marketing Agents

| Agent | Purpose | Invoke With |
|-------|---------|-------------|
| **router-agent** | Coordinates complex campaigns | `"Use router-agent to plan a campaign"` |
| **content-strategist** | Full campaign orchestration | `"Use content-strategist for campaign"` |
| **research-agent** | Evidence-backed research + competitive intelligence | `"Use research-agent to investigate best practices"` |
| **lead-gen-agent** | ✨ **NEW** B2B & local lead generation via web scraping | `"Use lead-gen-agent to find leads"` |
| **landing-page-specialist** | Designs & codes conversion-focused landing pages | `"Use landing-page-specialist to build a landing page"` |
| **copywriter** | Blog posts, articles (2000+ words) | `"Use copywriter to write a blog"` |
| **editor** | Content review & improvement | `"Use editor to review this content"` |
| **social-media-manager** | X/Twitter, LinkedIn posts | `"Use social-media-manager for LinkedIn post"` |
| **visual-designer** | GPT-4o image generation | `"Use visual-designer to create an image"` |
| **video-producer** | Sora-2 video creation ✅ TESTED | `"Use video-producer for video ad"` |
| **seo-specialist** | SEO research, SERP scraping & rank tracking | `"Use seo-specialist to research keywords"` |
| **email-specialist** | Email copywriting | `"Use email-specialist for email sequence"` |
| **gmail-agent** | Email sending via Gmail | `"Use gmail-agent to send newsletter"` |
| **pdf-specialist** | PDF whitepaper creation | `"Use pdf-specialist for PDF"` |
| **presentation-designer** | PowerPoint decks | `"Use presentation-designer for deck"` |
| **analyst** | Performance analysis + competitive benchmarking | `"Use analyst to analyze data"` |

---

## 🎯 How It Works

### The Truth About Multi-Agent Systems

Your agents are **specialized personas** that I (Claude Code) adopt.

When you say:
```
"Use the copywriter subagent to write a blog about AI"
```

**What happens:**
1. I (Claude) read `.claude/agents/copywriter.md`
2. I adopt that agent's instructions and persona
3. I use the tools specified for that agent
4. I complete the task in that agent's style
5. I return results to you

**No Python orchestrator needed** - I AM the orchestrator.

---

## 🧠 Memory System - Automatic Configuration

**All agents automatically read configuration from memory files** - no hardcoded values!

### How It Works

1. **Each agent has a "⚙️ Configuration Files (READ FIRST)" section** in their definition
2. **Agents read memory files at task start** using the Read tool or filesystem skill
3. **Configuration is applied automatically** - emails, Drive folders, brand voice, visual styles
4. **Update once, affects all agents** - change email config, all 16 agents use it

### Memory Files (MARKETING_TEAM/memory/)

| File | Purpose | Used By |
|------|---------|---------|
| `email_config.json` | Email defaults (`user_google_email`, `default_to`, `default_cc`) | ALL agents sending emails |
| `google_drive_config.json` | Drive folder IDs for organized uploads | ALL agents uploading files |
| `brand_voice.json` | Brand tone, style, writing guidelines | copywriter, social-media-manager, email-specialist |
| `visual_guidelines.json` | Brand colors, fonts, image styles | visual-designer, presentation-designer, pdf-specialist |
| `docs_folder_structure.json` | Documentation organization (AI assistants only) | Claude Code when creating docs |

### Why This Matters

✅ **No hardcoding** - Email addresses and folder IDs never hardcoded in agent definitions
✅ **Consistency** - All agents use same email addresses, same Drive folders, same brand voice
✅ **Easy updates** - Change one memory file, all agents benefit immediately
✅ **Single source of truth** - Configuration lives in one place, not scattered across 16 files

**Example:** Change `default_to` in `email_config.json` from `user1@example.com` to `user2@example.com` → all 16 agents now send emails to `user2@example.com` by default.

---

## 🎨 Skills & Advanced Capabilities

Your marketing agents now have access to **13 powerful skills** and **7 MCP servers**!

### Available Skills

**Visual Creation (4 skills):**
- **algorithmic-art** - Generative art with p5.js (flow fields, particle systems, unique social art)
- **canvas-design** - Beautiful PNG/PDF posters and banners
- **slack-gif-creator** - Animated GIFs optimized for Slack and social media
- **theme-factory** - 10 preset themes (modern, vibrant, minimal, professional, elegant, bold, calm, energetic, corporate, creative)

**Development (3 skills):**
- **artifacts-builder** - Complex React/Tailwind/shadcn/ui apps (interactive landing pages)
- **mcp-builder** - Create custom MCP servers (Python FastMCP or Node SDK)
- **skill-creator** - Create custom skills to extend Claude's capabilities

**Content & Documents (3 skills):**
- **internal-comms** - Company-standard formats (status reports, newsletters, FAQs)
- **brand-guidelines** - Anthropic's official brand colors & typography
- **pdf-filler** - Fill PDF forms, create fillable PDFs

**Integrations (3 skills):**
- **filesystem** - File operations (C:\ and C:\Users access)
- **figma** - Extract designs from Figma files
- **context7** - Enhanced context management (automatic)

### Available MCP Servers

- **playwright** - Browser automation for research & testing
- **google-workspace** - Gmail, Drive, Docs, Sheets, Calendar, Forms, Tasks (40+ tools)
- **perplexity** - Web search & research with citations
- **google-drive** - Drive file operations
- **bright-data** - Web scraping & lead generation (5,000 free requests/month)
- **n8n-mcp** - Workflow automation (400+ integrations)
- **sequential-thinking** - Structured step-by-step reasoning

### Quick Skill Examples

**Generate Unique Art:**
```
"Use visual-designer with algorithmic-art to create flow field art for Instagram"
```

**Build Interactive Landing Page:**
```
"Use landing-page-specialist with artifacts-builder to build a React landing page
with hero, features, and contact form. Apply theme-factory 'modern' theme."
```

**Create Animated GIF:**
```
"Use social-media-manager with slack-gif-creator to make a launch GIF"
```

**Find B2B Leads:**
```
"Use lead-gen-agent with bright-data to find 50 SaaS companies in SF"
```

**Research with Citations:**
```
"Use research-agent with perplexity to research AI marketing trends"
```

**Fillable PDF Form:**
```
"Use pdf-specialist with pdf-filler to create a registration form PDF"
```

### Complete Skills Documentation

📖 **[docs/guides/skills-and-mcp-guide.md](docs/guides/skills-and-mcp-guide.md)** - 50+ page comprehensive guide with detailed examples

📋 **[docs/SKILLS_QUICK_REFERENCE.md](docs/SKILLS_QUICK_REFERENCE.md)** - Quick lookup tables and cheat sheets

---

## 📂 Examples & Templates

### Examples Folder
**[examples/](examples/)** - Curated examples showing what agents can produce

- **Purpose:** Reference materials, testing artifacts, portfolio pieces
- **Tracked in git:** Yes - permanent examples for learning
- **Organization:** By skill and content type
- **Current examples:** algorithmic-art (Data Flow Dynamics)

📖 **[examples/README.md](examples/README.md)** - Complete examples guide

### Templates Folder
**[templates/reusable/](templates/reusable/)** - Starting points for common deliverables

Available templates:
- **[blog_post_template.md](templates/reusable/blog_post_template.md)** - SEO-optimized blog structure (1500-3000 words)
- **[social_media_template.md](templates/reusable/social_media_template.md)** - Platform-specific formats (X/Twitter, LinkedIn, Instagram, Facebook)
- **[landing_page_template.html](templates/reusable/landing_page_template.html)** - Conversion-focused landing page with hero, features, testimonials, pricing, FAQ
- **[email_template.md](templates/reusable/email_template.md)** - Subject line formulas, welcome emails, newsletters, product launches, cart abandonment

📖 **[templates/README.md](templates/README.md)** - Template usage guide

### Outputs Folder (Gitignored)
**outputs/** - Your actual work and deliverables

- **Purpose:** Real client work, campaign content, production files
- **Tracked in git:** No - stays private on your machine
- **Organization:** By content type (blog_posts, social_media, images, videos, etc.)

**The Difference:**
- **examples/** = Reference materials (tracked in git for learning)
- **templates/** = Starting frameworks (tracked in git for reuse)
- **outputs/** = Your actual deliverables (gitignored - stays private)

---

## 💡 Usage Examples

### Example 1: Create LinkedIn Post

```
You: "Use social-media-manager to create a LinkedIn post about autonomous AI agents"

Claude (as social-media-manager):
  🤖 The Future of Marketing is Autonomous

  AI agents are revolutionizing content creation in 2025:

  ✨ Autonomous content generation
  ✨ Multi-agent coordination
  ✨ Personalized at scale

  The question isn't IF you'll use AI agents, but WHEN.

  #AIMarketing #Automation #FutureOfWork #MarTech
```

### Example 2: Complete Campaign

```
You: "Use router-agent to create a social media campaign for our AI product launch"

Claude (as router-agent):
  [Coordinates multiple specialist agents]

  ✅ Blog post (2000 words) - copywriter
  ✅ LinkedIn + Twitter posts - social-media-manager
  ✅ 3 campaign images - visual-designer
  ✅ 3-email sequence - email-specialist

  All uploaded to Google Drive:
  - Blog: [link]
  - Social: [link]
  - Images: [link]
  - Emails: [link]
```

### Example 3: Automatic Delegation

```
You: "Write a blog post about AI coding assistants"

Claude: [Automatically invokes copywriter agent]
        [Writes 2000-word SEO-optimized blog]
        [Returns Markdown format]
```

---

## ⚙️ Setup (One-Time)

### 1. Install Dependencies

```bash
cd MARKETING_TEAM
pip install -r requirements.txt
```

### 2. Configure APIs

**OpenAI API (CONFIGURED):**
- Image generation with GPT-4o - Ready!
- Video generation with Sora - Ready!
- See [docs/getting-started/api-setup.md](docs/getting-started/api-setup.md) for testing

**Gmail API (Optional):**
- Required for: email-specialist, gmail-agent
- See [docs/getting-started/api-setup.md](docs/getting-started/api-setup.md) for setup

**Google Drive API (Optional):**
- Required for: file uploads and sharing
- See [docs/getting-started/api-setup.md](docs/getting-started/api-setup.md) for setup

**Bright Data MCP (CONFIGURED):** ✨ **NEW**
- Web scraping and lead generation - Ready!
- 5,000 free requests/month
- See usage examples below

**Playwright (Auto-configured):**
- Used for web research by seo-specialist
- First run: `npx playwright install`

**Full setup guide:** [docs/getting-started/api-setup.md](docs/getting-started/api-setup.md)

### 3. Configure Brand (Recommended)

Create `memory/brand_voice.json`:
```json
{
  "tone": "professional yet approachable",
  "style": "data-driven storytelling",
  "key_phrases": ["AI-powered marketing"],
  "audience": "Marketing professionals"
}
```

See [docs/guides/usage-guide.md](docs/guides/usage-guide.md) for more memory configuration options.

---

## 🛠️ Agent Capabilities

### Content Creation
- **copywriter** - Blog posts, articles, web copy
- **editor** - Grammar, clarity, brand voice
- **social-media-manager** - X/Twitter, LinkedIn posts

### Visual Content
- **visual-designer** - GPT-4o image generation
- **video-producer** - Sora video creation
- **presentation-designer** - PowerPoint decks
- **pdf-specialist** - PDF documents

### Research & Strategy
- **research-agent** - Market, UX, and competitor research with citations + web scraping
- **seo-specialist** - Keyword research, SERP scraping, rank tracking
- **analyst** - Performance analysis, competitive benchmarking
- **content-strategist** - Campaign planning

### Lead Generation ✨ NEW
- **lead-gen-agent** - B2B lead generation (LinkedIn companies, Google Maps, directories)
  - 5,000 free Bright Data requests/month = 2,000-5,000 leads
  - Business contact enrichment
  - CRM-ready export (CSV, Google Sheets)

### Conversion Experiences
- **landing-page-specialist** - UX, copy, code + competitor analysis

### Distribution
- **email-specialist** - Email copywriting
- **gmail-agent** - Email sending automation

### Coordination
- **router-agent** - Multi-agent coordination

---

## 📖 Documentation Structure

```
MARKETING_TEAM/
├── README.md                         ← You are here
├── docs/                             ← All documentation
│   ├── getting-started/              ← Setup guides
│   │   └── api-setup.md
│   ├── guides/                       ← Usage guides
│   │   ├── usage-guide.md
│   │   └── campaign-examples.md
│   ├── reference/                    ← API references
│   └── architecture/                 ← Technical docs
│       ├── system-architecture.md
│       ├── mcp-config.md
│       └── build-notes.md
├── .claude/
│   └── agents/                       ← 16 agent definitions
│       ├── router-agent.md
│       ├── lead-gen-agent.md         ← NEW!
│       ├── copywriter.md
│       ├── social-media-manager.md
│       └── ... (11 more)
├── tools/                            ← Custom tools
│   ├── openai_gpt4o_image.py
│   └── ... (more tools)
├── scripts/                          ← Utility scripts
│   ├── create_word_documents.py
│   ├── generate_linkedin_image.py
│   └── test_openai_connection.py
├── memory/                           ← Brand & preferences
│   ├── brand_voice.json
│   └── visual_guidelines.json
├── outputs/                          ← Generated content
│   ├── blog_posts/
│   ├── campaigns/
│   ├── emails/
│   └── ... (more outputs)
└── archive/
    └── orchestrator.py               ← Old approach (archived)
```

---

## 🎓 Learn More

**[docs/guides/usage-guide.md](docs/guides/usage-guide.md)** - Detailed guide with examples for each agent

**[docs/guides/campaign-examples.md](docs/guides/campaign-examples.md)** - Real campaign examples and results

**[../MULTI_AGENT_GUIDE.md](../MULTI_AGENT_GUIDE.md)** - Understanding multi-agent systems

**[docs/architecture/system-architecture.md](docs/architecture/system-architecture.md)** - Technical architecture documentation

**Agent Definitions:** Check `.claude/agents/` to see each agent's:
- Specialized instructions
- Available tools
- Capabilities

---

## 🔧 Troubleshooting

### "Agent isn't working"
- Verify agent `.md` file exists in `.claude/agents/`
- Be more specific in your request
- Check [docs/guides/usage-guide.md](docs/guides/usage-guide.md) for examples

### "Images not generating"
- Need OpenAI API key in `.env` file
- Verify `OPENAI_API_KEY` is correct
- Check billing is set up

### "Can't upload to Drive"
- Need `credentials.json` from Google Cloud Console
- Enable Google Drive API
- First run opens browser for authentication

### "Gmail not sending"
- Need `gmail_credentials.json` from Google Cloud Console
- Enable Gmail API
- Check OAuth scopes include `gmail.send`

---

## 🚀 Quick Examples to Try

**Create your first content:**
```
"Use copywriter to write a short blog intro about AI in marketing"
```

**Generate an image:**
```
"Use visual-designer to create a LinkedIn header image about productivity"
```

**Create social posts:**
```
"Use social-media-manager to create posts about our new feature"
```

**Generate leads:** ✨ NEW
```
"Use lead-gen-agent to find 50 SaaS companies in San Francisco with 50-200 employees"
```

**Full campaign:**
```
"Use router-agent to plan a mini marketing campaign"
```

---

## 📝 Notes

### About the Archived Orchestrator

You'll find `orchestrator.py` in the `archive/` folder. This was an earlier attempt to create a Python program that would invoke agents. **It's not needed anymore** because:

- Agent definitions are used directly by Claude Code
- No Python orchestrator required
- Simpler and more powerful to just talk to Claude

**The agent definitions (`.claude/agents/*.md`) are what matter** - they're perfectly formatted and ready to use.

---

## 🎯 What's Next?

1. **Read [docs/guides/usage-guide.md](docs/guides/usage-guide.md)** - Complete guide with examples
2. **Check out [docs/guides/campaign-examples.md](docs/guides/campaign-examples.md)** - See real examples
3. **Try invoking an agent** - Start with something simple
4. **Explore agent definitions** - See what each can do in `.claude/agents/`
5. **Experiment** - Try automatic delegation by just describing tasks

---

## 📚 Additional Resources

- **Claude Code Documentation:** https://docs.claude.com/claude-code
- **Agent Definitions:** `.claude/agents/`
- **Tools Source Code:** `tools/`
- **Memory Configuration:** `memory/`

---

**Your 16 marketing agents are ready!** Just start talking to Claude Code.

**✨ NEW: Lead generation with Bright Data MCP - 5,000 free requests/month for business lead discovery!**

See [docs/guides/usage-guide.md](docs/guides/usage-guide.md) for detailed instructions and examples. 🚀
