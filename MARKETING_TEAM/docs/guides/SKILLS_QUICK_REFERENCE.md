# Skills & MCP Quick Reference

Quick lookup table for all available skills and MCP servers.

---

## Skills Quick Reference (13 total)

| Skill | Category | Description | Best Agent | Example Usage |
|-------|----------|-------------|------------|---------------|
| **algorithmic-art** | Visual | Generative art with p5.js (flow fields, particles) | visual-designer | `"Use visual-designer with algorithmic-art to create flow field art"` |
| **canvas-design** | Visual | Beautiful PNG/PDF posters, banners, designs | visual-designer | `"Use visual-designer with canvas-design to create a conference poster"` |
| **slack-gif-creator** | Visual | Animated GIFs optimized for Slack | social-media-manager | `"Use social-media-manager with slack-gif-creator to make a launch GIF"` |
| **theme-factory** | Visual | 10 preset themes for artifacts (modern, vibrant, minimal, etc.) | presentation-designer | `"Use presentation-designer with theme-factory 'professional' theme"` |
| **artifacts-builder** | Development | React/Tailwind/shadcn/ui multi-component apps | landing-page-specialist | `"Use landing-page-specialist with artifacts-builder to build landing page"` |
| **mcp-builder** | Development | Create MCP servers (Python FastMCP or Node SDK) | Any agent | `"Use mcp-builder to create an MCP server for our CRM API"` |
| **skill-creator** | Development | Create custom skills for Claude | Any agent | `"Use skill-creator to design a legal marketing compliance skill"` |
| **internal-comms** | Content | Company-standard formats (status reports, newsletters, FAQs) | copywriter | `"Use copywriter with internal-comms to write Q1 status report"` |
| **brand-guidelines** | Content | Anthropic's official brand colors & typography | visual-designer | `"Use presentation-designer with brand-guidelines for Anthropic deck"` |
| **pdf-filler** | Content | Fill PDF forms, create fillable PDFs | pdf-specialist | `"Use pdf-specialist with pdf-filler to create registration form PDF"` |
| **filesystem** | Integration | File operations (C:\ and C:\Users access) | Any agent | `"Use research-agent with filesystem to read competitor PDFs"` |
| **figma** | Integration | Extract designs, components, assets from Figma | visual-designer | `"Use visual-designer with figma to extract brand assets from [URL]"` |
| **context7** | Integration | Enhanced context management | All agents | Automatic - no invocation needed |

---

## MCP Servers Quick Reference (7 total)

| MCP Server | Category | Description | Key Tools | Best Agent |
|------------|----------|-------------|-----------|------------|
| **playwright** | Browser | Browser automation for research & testing | navigate, screenshot, click, fill, evaluate | research-agent, seo-specialist |
| **google-workspace** | Integration | Gmail, Drive, Docs, Sheets, Calendar, Forms, Tasks | send_gmail_message, upload_to_drive, create_doc, create_event | gmail-agent, all agents |
| **perplexity** | Research | Web search & research with citations | perplexity_ask, perplexity_reason, perplexity_search, perplexity_research | research-agent, seo-specialist, analyst |
| **google-drive** | Integration | Drive file operations (search, upload, manage) | search_drive_files, get_drive_file_content, create_drive_file | All agents |
| **bright-data** | Scraping | Web scraping, lead generation, SERP analysis | search_engine, scrape_as_markdown, search_engine_batch, scrape_batch | lead-gen-agent, seo-specialist, research-agent, analyst |
| **n8n-mcp** | Automation | Workflow automation, 400+ integrations | list_workflows, trigger_workflow, get_execution | router-agent, content-strategist |
| **sequential-thinking** | Reasoning | Structured step-by-step problem-solving | sequentialthinking | router-agent, content-strategist, analyst |

---

## Skills by Agent

### visual-designer
- algorithmic-art
- canvas-design
- theme-factory
- figma

### presentation-designer
- theme-factory
- artifacts-builder

### social-media-manager
- algorithmic-art
- slack-gif-creator

### landing-page-specialist
- artifacts-builder
- theme-factory

### copywriter
- internal-comms

### pdf-specialist
- pdf-filler
- canvas-design

### All other agents
Can use any skill when appropriate, plus:
- filesystem (all agents)
- context7 (automatic for all agents)

---

## Common Combinations

### Visual Content Creation
```
algorithmic-art + canvas-design + slack-gif-creator + theme-factory
= Complete visual asset library
```

### Interactive Landing Page
```
artifacts-builder + theme-factory + figma
= Modern React landing page from Figma design
```

### Research & Analysis
```
perplexity + playwright + bright-data + sequential-thinking
= Comprehensive market research report
```

### Campaign Delivery
```
google-workspace + gmail + drive + filesystem
= Complete content delivery system
```

### PDF Creation
```
pdf-filler + canvas-design + filesystem
= Professional fillable PDF forms
```

---

## Theme-Factory Themes

All 10 available themes:
1. **modern** - Clean, contemporary design
2. **vibrant** - Bold, energetic colors
3. **minimal** - Simple, focused layouts
4. **professional** - Business-appropriate styling
5. **elegant** - Sophisticated, refined
6. **bold** - Strong, impactful visuals
7. **calm** - Peaceful, soothing tones
8. **energetic** - Dynamic, exciting
9. **corporate** - Traditional business style
10. **creative** - Artistic, expressive

---

## When to Use What

### Need unique visuals?
→ **algorithmic-art** (generative art) or **canvas-design** (professional posters)

### Need animated content?
→ **slack-gif-creator** (optimized GIFs)

### Need consistent branding?
→ **theme-factory** (preset themes)

### Need interactive website?
→ **artifacts-builder** (React/Tailwind)

### Need to scrape websites?
→ **bright-data** MCP (web scraping)

### Need market research?
→ **perplexity** MCP (research with citations)

### Need browser automation?
→ **playwright** MCP (automate browsers)

### Need to send emails?
→ **google-workspace** MCP (Gmail tools)

### Need fillable PDF forms?
→ **pdf-filler** skill

### Need internal documents?
→ **internal-comms** skill

### Need to implement Figma designs?
→ **figma** skill + **artifacts-builder** or static HTML

### Need structured problem-solving?
→ **sequential-thinking** MCP

### Need workflow automation?
→ **n8n-mcp** (trigger n8n workflows)

---

## Quick Start Examples

### 1. Generate Unique Social Art
```
"Use visual-designer with algorithmic-art to create a flow field design
with brand colors (#FF5733, #3498DB) for Instagram. 1080x1080px."
```

### 2. Create Animated GIF
```
"Use social-media-manager with slack-gif-creator to make a 3-second
'NEW FEATURE' announcement GIF with our brand colors."
```

### 3. Build Interactive Landing Page
```
"Use landing-page-specialist with artifacts-builder to create a React
landing page with hero section, features, and contact form. Apply
theme-factory 'modern' theme."
```

### 4. Create Professional PDF
```
"Use pdf-specialist with canvas-design to create a one-page PDF
product overview with beautiful layout."
```

### 5. Write Status Report
```
"Use copywriter with internal-comms to write a Q1 marketing status
report including metrics, wins, challenges, and Q2 preview."
```

### 6. Find Leads
```
"Use lead-gen-agent with bright-data to find 50 B2B SaaS companies
in San Francisco with 50-200 employees."
```

### 7. Research Market
```
"Use research-agent with perplexity to research AI marketing trends
and provide citation-backed insights."
```

### 8. Scrape Competitor Sites
```
"Use research-agent with bright-data to scrape top 10 competitor
landing pages and extract their headlines and CTAs."
```

### 9. Automate Browser
```
"Use research-agent with playwright to navigate to competitor-site.com,
screenshot the homepage, and extract visible text."
```

### 10. Send Campaign Email
```
"Use gmail-agent with google-workspace to send this email campaign
to 50 leads with the PDF attachment."
```

---

## MCP Tool Count by Server

| MCP Server | Tool Count | Category |
|------------|------------|----------|
| google-workspace | 40+ | Gmail, Drive, Docs, Sheets, Calendar, Forms, Tasks |
| playwright | 25+ | Browser automation |
| n8n-mcp | 15+ | Workflow management |
| bright-data | 4 | Web scraping |
| perplexity | 4 | Research |
| google-drive | 3 | File operations |
| sequential-thinking | 1 | Reasoning |

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Skill not available | Check MARKETING_TEAM/.claude/settings.json has skill enabled |
| MCP tool error | Verify .claude.json has MCP configured and API keys set |
| Wrong output | Be more explicit: "Use X agent with Y skill to..." |
| Slow performance | Break task into smaller steps or simplify prompt |
| Skill conflict | Specify which skill: "Use X skill (not Y)" |

---

## Full Documentation

For comprehensive guides with detailed examples and workflows, see:
- **[skills-and-mcp-guide.md](guides/skills-and-mcp-guide.md)** - Complete reference with 50+ pages
- **[CLAUDE.md](../../CLAUDE.md)** - Repository overview
- **[MULTI_AGENT_GUIDE.md](../../MULTI_AGENT_GUIDE.md)** - Complete multi-agent guide

---

**Last Updated:** 2025-10-18
