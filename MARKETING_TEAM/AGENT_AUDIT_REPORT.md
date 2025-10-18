# MARKETING TEAM Agent Tools & Skills Audit Report

**Generated:** 2025-10-18
**Purpose:** Comprehensive audit of all 16 marketing agents to ensure correct tool/skill configuration

---

## Executive Summary

### Inventory Completed

**Available Resources:**
- ✅ **20 Agent SDK Tools** (with @tool decorators)
- ✅ **13 Claude Skills** (enabled in settings.json)
- ✅ **7 MCP Servers** (configured in .claude.json)
- ✅ **16 Marketing Agents** (agent definitions)

---

## 1. Available Tools (20 Total)

### Email Tools (3)
1. `send_gmail` - Send email via Gmail with optional attachments
2. `create_gmail_draft` - Create email draft in Gmail for review
3. `send_email_campaign` - Send email campaign to multiple recipients (rate limited)

### Image & Visual Tools (1)
4. `generate_gpt4o_image` - Generate high-quality image using GPT-4o (gpt-image-1)

### File Management Tools (1)
5. `upload_to_google_drive` - Upload file to Google Drive and get shareable link

### PDF Tools (2)
6. `generate_pdf` - Generate professional PDF document (whitepaper, lead magnet, report)
7. `create_lead_magnet_pdf` - Create a lead magnet PDF (checklist, template, guide)

### Social Media Tools (5)
8. `format_twitter_post` - Format content for X/Twitter with character limits and hashtag optimization
9. `format_linkedin_post` - Format content for LinkedIn with professional optimization
10. `extract_hashtags` - Extract and suggest hashtags from content
11. `optimize_post_for_engagement` - Analyze and suggest improvements for social media engagement
12. `create_post_variations` - Create multiple variations of a post for A/B testing

### Presentation Tools (2)
13. `generate_powerpoint` - Generate professional PowerPoint presentation
14. `create_pitch_deck` - Create a standard 10-slide pitch deck

### Router/Orchestration Tools (4)
15. `classify_intent` - Classify user intent to determine which marketing agents to invoke
16. `get_agent_capabilities` - Get detailed capabilities of a specific agent
17. `list_available_agents` - List all available marketing agents and their purposes
18. `format_agent_response` - Format agent response for user display

### Video Tools (2)
19. `generate_sora_video` - Generate video using Sora-2 (OpenAI video generation model)
20. `create_video_storyboard` - Create detailed storyboard for video production

---

## 2. Available Skills (13 Total)

### Visual Creation Skills (4)
1. `algorithmic-art` - Generative art with p5.js (flow fields, particle systems)
2. `canvas-design` - Beautiful PNG/PDF visual art (posters, banners)
3. `slack-gif-creator` - Animated GIFs optimized for Slack
4. `theme-factory` - 10 preset themes for consistent branding

### Development & Artifacts Skills (3)
5. `artifacts-builder` - Complex React/Tailwind/shadcn/ui multi-component apps
6. `mcp-builder` - Create MCP servers (Python FastMCP or Node/TypeScript SDK)
7. `skill-creator` - Create custom skills to extend Claude's capabilities

### Content & Document Skills (3)
8. `internal-comms` - Company-standard formats (status reports, newsletters, FAQs)
9. `brand-guidelines` - Anthropic's official brand colors & typography
10. `pdf-filler` - Fill PDF forms, create fillable PDFs with form fields

### Integration Skills (3)
11. `filesystem` - File operations with C:\ and C:\Users access
12. `figma` - Extract designs, components, assets from Figma files
13. `context7` - Enhanced context management (automatic)

---

## 3. Available MCP Servers (7 Total)

### 1. **playwright**
**Purpose:** Browser automation for research
**Key Tools:** navigate, screenshot, click, fill, evaluate, get_visible_text, get_visible_html

### 2. **google-workspace**
**Purpose:** Gmail, Drive, Docs, Sheets, Calendar integration
**Key Tools:** send_gmail_message, upload_to_drive, create_doc, create_sheet, create_event

### 3. **perplexity**
**Purpose:** Web search & research with citations
**Key Tools:** perplexity_ask, perplexity_reason, perplexity_search, perplexity_research

### 4. **google-drive**
**Purpose:** Drive file operations
**Key Tools:** search_drive_files, get_drive_file_content, create_drive_file

### 5. **bright-data**
**Purpose:** Web scraping & lead generation (5,000 free requests/month)
**Key Tools:** search_engine, scrape_as_markdown, search_engine_batch, scrape_batch

### 6. **n8n-mcp**
**Purpose:** Workflow automation (400+ integrations)
**Key Tools:** list_workflows, trigger_workflow, get_execution

### 7. **sequential-thinking**
**Purpose:** Structured step-by-step reasoning
**Key Tools:** sequentialthinking

---

## 4. Agent Audit (16 Agents)

*To be filled in with detailed audit for each agent...*

---

## Next Steps

1. **Audit each agent** - Check their current tool/skill configuration
2. **Identify issues** - Wrong tool names, missing tools, unused tools
3. **Create recommendations** - Which tools/skills each agent should have
4. **Generate matrix** - Cross-reference table of agents × tools/skills
5. **Fix configurations** - Update all agent .md files
6. **Test tools** - Verify functionality and identify redundancies

---

*Report continues with detailed agent-by-agent audit...*
