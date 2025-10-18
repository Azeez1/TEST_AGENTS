# Complete Skills & MCP Server Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Skills Reference](#skills-reference)
3. [MCP Servers Reference](#mcp-servers-reference)
4. [Real-World Marketing Scenarios](#real-world-marketing-scenarios)
5. [Advanced Multi-Skill Workflows](#advanced-multi-skill-workflows)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

### What Are Skills?

**Skills** are specialized capabilities that extend Claude's functionality with domain-specific knowledge, workflows, and tool integrations. Think of them as "expert modes" that Claude can activate for specific tasks.

Your MARKETING_TEAM agents now have access to **13 powerful skills**:
- **Visual Creation:** algorithmic-art, canvas-design, slack-gif-creator, theme-factory
- **Development:** artifacts-builder, mcp-builder, skill-creator
- **Content:** internal-comms, brand-guidelines, pdf-filler
- **Integrations:** filesystem, figma, context7

### What Are MCP Servers?

**MCP (Model Context Protocol) servers** provide tools that Claude can use to interact with external services and APIs. Your agents inherit **7 MCP servers**:
- playwright (browser automation)
- google-workspace (Gmail, Drive, Docs, Sheets, Calendar)
- perplexity (web search & research)
- google-drive (Drive file operations)
- bright-data (web scraping & lead generation)
- n8n-mcp (workflow automation)
- sequential-thinking (structured reasoning)

### How Skills & MCPs Work with Agents

**Configuration inheritance:**
1. Skills are enabled in `MARKETING_TEAM/.claude/settings.json`
2. MCPs are inherited from root `.claude.json` via `"mcpServers": "inherit"`
3. All 16 marketing agents automatically get access to both skills and MCPs
4. Agent definitions can specify which skills they emphasize in their `skills:` frontmatter

**Example agent invocation:**
```
"Use visual-designer with algorithmic-art to create a generative art piece for Instagram"
```

Claude will:
1. Read the visual-designer agent definition
2. See that algorithmic-art is listed as a skill
3. Activate the algorithmic-art skill
4. Generate unique code-based art
5. Return the result

---

## Skills Reference

### Visual Creation Skills

#### 1. algorithmic-art

**Description:** Create generative art using p5.js with seeded randomness and interactive parameter exploration.

**Best for:**
- Unique, non-stock social media visuals
- Abstract or geometric patterns
- Flow fields and particle systems
- Distinctive brand art
- Reproducible, parametric designs

**Key features:**
- Seeded randomness (reproducible results)
- Interactive parameter exploration
- Code-based art generation
- Customizable colors, sizes, patterns

**Example use cases:**
- Instagram post backgrounds
- Twitter header art
- LinkedIn visual content
- Website hero section art
- Brand pattern libraries

**Which agents use it:**
- visual-designer (primary)
- social-media-manager (for unique posts)

**Example invocation:**
```
"Use visual-designer with algorithmic-art to create a flow field design
with our brand colors (#FF5733, #3498DB) for a Twitter post.
Canvas size: 1200x675px (16:9 ratio)."
```

---

#### 2. canvas-design

**Description:** Create beautiful visual art in PNG and PDF formats using design philosophy principles.

**Best for:**
- Posters and banners
- Conference materials
- Static design pieces
- Professional certificates
- Print-ready materials
- One-page marketing collateral

**Key features:**
- PNG and PDF output formats
- Design philosophy focused on aesthetics
- High-quality professional layouts
- Print-ready resolution

**Example use cases:**
- Conference posters
- Event banners
- PDF one-pagers
- Professional certificates
- Print advertisements
- Infographic designs

**Which agents use it:**
- visual-designer (primary)
- pdf-specialist (for beautiful PDFs)

**Example invocation:**
```
"Use visual-designer with canvas-design to create a conference poster
for our AI Summit in PDF format. Include event details, date, and
a modern abstract design."
```

---

#### 3. slack-gif-creator

**Description:** Create animated GIFs optimized for Slack with size validators and composable animation primitives.

**Best for:**
- Product launch announcements
- Milestone celebrations
- Eye-catching promotions
- Animated reactions
- Looping brand animations
- Attention-grabbing social media content

**Key features:**
- Slack size optimization (automatic validators)
- Composable animation primitives
- Small file sizes
- Professional quality output
- Works great on Twitter, LinkedIn too

**Example use cases:**
- Product launch GIFs
- Announcement animations
- Celebration animations
- Branded emoji/reactions
- Social media eye-catchers

**Which agents use it:**
- social-media-manager (primary)
- visual-designer

**Example invocation:**
```
"Use social-media-manager with slack-gif-creator to make a 3-second
looping GIF announcing 'NEW PRODUCT LAUNCH' with our brand colors,
optimized for Slack and Twitter."
```

---

#### 4. theme-factory

**Description:** Apply one of 10 preset professional themes to artifacts for consistent branding.

**Best for:**
- Consistent branded materials
- Presentation styling
- Landing page themes
- Document formatting
- Rapid professional styling
- Cohesive multi-artifact campaigns

**Available themes:**
- modern
- vibrant
- minimal
- professional
- elegant
- bold
- calm
- energetic
- corporate
- creative

**Key features:**
- 10 preset professional themes
- Consistent colors and typography
- Artifact styling (slides, docs, landing pages)
- Custom overrides available

**Example use cases:**
- Themed presentation decks
- Branded landing pages
- Consistent report styling
- Multi-page branded documents
- Campaign material cohesion

**Which agents use it:**
- presentation-designer (primary)
- landing-page-specialist
- visual-designer

**Example invocation:**
```
"Use presentation-designer with theme-factory to create a sales deck
with the 'professional' theme. Apply consistent styling to all 15 slides."
```

---

### Development & Artifact Skills

#### 5. artifacts-builder

**Description:** Suite of tools for creating elaborate, multi-component artifacts using React, Tailwind CSS, and shadcn/ui.

**Best for:**
- Complex interactive landing pages
- Multi-component web applications
- State-managed interfaces
- Modern frontend development
- Component-based architecture
- Interactive presentations

**Key features:**
- React with TypeScript support
- Tailwind CSS for styling
- shadcn/ui component library
- State management capabilities
- Routing and navigation
- Multi-component architecture

**Tech stack:**
- React (modern hooks, functional components)
- Tailwind CSS (utility-first styling)
- shadcn/ui (accessible component library)
- TypeScript (type safety)
- Modern ES6+ JavaScript

**Example use cases:**
- Interactive landing pages
- Multi-section marketing sites
- Form-heavy pages with validation
- Interactive product showcases
- Complex presentation interfaces
- Dashboard-style marketing tools

**Which agents use it:**
- landing-page-specialist (primary)
- presentation-designer (for interactive decks)

**Example invocation:**
```
"Use landing-page-specialist with artifacts-builder to build an
interactive landing page with:
- Hero section with animations
- Interactive product showcase with tabs
- Contact form with validation
- Responsive Tailwind design
- shadcn/ui components"
```

---

#### 6. mcp-builder

**Description:** Guide for creating high-quality MCP (Model Context Protocol) servers using FastMCP (Python) or MCP SDK (Node/TypeScript).

**Best for:**
- Integrating external APIs
- Building custom tools for Claude
- Creating service connectors
- Custom workflow automation
- Extending Claude's capabilities

**Supports:**
- Python (FastMCP framework)
- Node.js / TypeScript (MCP SDK)

**Key features:**
- Step-by-step MCP creation guide
- Best practices for tool design
- Authentication patterns
- Error handling strategies
- Testing and deployment

**Example use cases:**
- Custom API integrations
- Proprietary service connectors
- Internal tool integrations
- Specialized workflow automation
- Custom data source connections

**Which agents use it:**
- Any agent (when custom integration needed)
- Typically invoked for special projects

**Example invocation:**
```
"Use mcp-builder to help me create an MCP server that integrates
with our internal CRM API. I need tools for fetching leads,
updating contacts, and creating opportunities."
```

---

#### 7. skill-creator

**Description:** Guide for creating effective skills that extend Claude's capabilities with specialized knowledge and workflows.

**Best for:**
- Creating domain-specific skills
- Building custom expert modes
- Documenting specialized workflows
- Knowledge base integration
- Creating reusable templates

**Key features:**
- Skill design best practices
- YAML frontmatter guidance
- Prompt engineering patterns
- Tool integration advice
- Testing and iteration strategies

**Example use cases:**
- Industry-specific skills (legal, medical, finance)
- Company-specific workflow skills
- Specialized knowledge domains
- Custom template libraries
- Proprietary methodology skills

**Which agents use it:**
- Any agent (when creating new capabilities)
- Typically invoked for extending the system

**Example invocation:**
```
"Use skill-creator to help me design a custom skill for creating
legal marketing content that follows law firm advertising compliance
rules and bar association guidelines."
```

---

### Content & Document Skills

#### 8. internal-comms

**Description:** Resources for writing internal communications using company-standard formats (status reports, updates, newsletters, FAQs).

**Best for:**
- Status reports
- Leadership updates
- Company newsletters
- Project updates
- Incident reports
- FAQs
- Team communications

**Communication types supported:**
- Status reports (project tracking)
- Leadership updates (executive summaries)
- 3P updates (third-party communications)
- Company newsletters (internal news)
- FAQs (documentation)
- Incident reports (postmortems)
- Project updates (sprint reviews)

**Key features:**
- Company-standard formats
- Professional tone and structure
- Clear hierarchies
- Action item highlighting
- Audience-appropriate language

**Example use cases:**
- Quarterly status reports
- Monthly team updates
- Incident postmortems
- Project milestone communications
- Internal documentation
- Leadership briefings

**Which agents use it:**
- copywriter (primary)
- Any agent writing internal docs

**Example invocation:**
```
"Use copywriter with internal-comms to write a Q1 status report
for the marketing team including:
- Campaign performance metrics
- Budget status and forecasts
- Key wins and challenges
- Q2 planning preview"
```

---

#### 9. brand-guidelines

**Description:** Applies Anthropic's official brand colors and typography to artifacts.

**Best for:**
- Anthropic-branded materials
- Official company artifacts
- Consistent visual identity
- Style guide compliance

**Key features:**
- Anthropic brand colors
- Official typography
- Design standards
- Visual formatting rules

**Example use cases:**
- Anthropic internal materials
- Partner-facing documents
- Official presentations
- Brand-compliant artifacts

**Which agents use it:**
- visual-designer (when appropriate)
- presentation-designer (for Anthropic materials)

**Example invocation:**
```
"Use presentation-designer with brand-guidelines to create
an Anthropic-branded presentation using official colors and fonts."
```

---

#### 10. pdf-filler

**Description:** Fill PDF form fields and create fillable PDF forms.

**Best for:**
- Registration forms
- Survey PDFs
- Application forms
- Contract templates
- Form-based data collection

**Key features:**
- Fill existing PDF forms
- Create fillable form fields
- Text fields, checkboxes, radio buttons
- Signature field support

**Example use cases:**
- Event registration forms
- Survey PDFs
- Lead capture forms
- Application templates
- Contract forms

**Which agents use it:**
- pdf-specialist (primary)

**Example invocation:**
```
"Use pdf-specialist with pdf-filler to create a fillable registration
form PDF with fields for name, email, company, title, and signature."
```

---

### Integration Skills

#### 11. filesystem

**Description:** File operations with access to C:\ and C:\Users directories.

**Best for:**
- Reading local files
- Writing output files
- Managing assets
- Local file organization
- Batch file processing

**Allowed directories:**
- C:\ (full drive access)
- C:\Users (user directories)

**Key features:**
- Read files from disk
- Write files to disk
- Directory navigation
- File management
- Asset organization

**Example use cases:**
- Reading competitor PDFs for analysis
- Writing campaign output files
- Managing local asset libraries
- Batch processing marketing materials
- Organizing deliverable files

**Which agents use it:**
- Any agent (when file access needed)
- Particularly useful for file-heavy workflows

**Example invocation:**
```
"Use research-agent with filesystem to read and analyze
competitor whitepapers stored in C:\Users\Documents\Research\"
```

---

#### 12. figma

**Description:** Figma design integration for extracting designs, components, and assets.

**Best for:**
- Design handoff
- Extracting brand assets
- Implementing Figma designs
- Design token extraction
- Component library access

**Key features:**
- Extract designs from Figma files
- Access design tokens
- Component extraction
- Asset downloads
- Design system integration

**Example use cases:**
- Implementing landing page from Figma
- Extracting brand colors and fonts
- Converting designs to code
- Accessing component libraries
- Design-to-development handoff

**Which agents use it:**
- visual-designer (primary)
- landing-page-specialist (for design implementation)

**Example invocation:**
```
"Use visual-designer with figma to extract our brand's design system
from [Figma URL] and implement the color palette and typography
in our landing page."
```

---

#### 13. context7

**Description:** Enhanced context management for maintaining conversation state and knowledge.

**Best for:**
- Long conversations
- Complex multi-step tasks
- Context preservation
- Knowledge retention

**Key features:**
- Enhanced context handling
- Knowledge persistence
- Conversation state management
- Improved context window utilization

**Example use cases:**
- Long campaign planning sessions
- Multi-day project work
- Complex research tasks
- Iterative design processes

**Which agents use it:**
- All agents (automatic enhancement)
- Particularly helpful for long conversations

**Usage:**
Context7 works automatically in the background to enhance context management. No special invocation needed.

---

## MCP Servers Reference

### 1. playwright - Browser Automation

**Description:** Automate browser interactions for research, testing, and data collection.

**Available tools:**
- `playwright_navigate` - Navigate to URLs
- `playwright_screenshot` - Capture screenshots
- `playwright_click` - Click elements
- `playwright_fill` - Fill form fields
- `playwright_evaluate` - Execute JavaScript
- `playwright_get_visible_text` - Extract page text
- `playwright_get_visible_html` - Extract page HTML
- And more (iframe interactions, file uploads, etc.)

**Best for:**
- Competitive research
- Website analysis
- Screenshot capture
- Form automation
- Web scraping
- Content extraction

**Example use cases:**
- Capture competitor landing pages
- Analyze website structures
- Extract web content
- Automate repetitive web tasks
- Test landing pages

**Which agents use it:**
- research-agent (primary)
- seo-specialist (for website analysis)
- analyst (for competitive research)

**Example invocation:**
```
"Use research-agent with playwright to navigate to
competitor-site.com, capture a screenshot, and extract
their headline and CTA copy."
```

---

### 2. google-workspace - Gmail, Drive, Docs, Sheets, Calendar

**Description:** Comprehensive Google Workspace integration (Gmail, Drive, Docs, Sheets, Calendar, Forms, Tasks).

**Available tool categories:**
- **Gmail:** Search, read, send emails (with attachments)
- **Drive:** Search, upload, download, manage files
- **Docs:** Create, read, modify Google Docs
- **Sheets:** Read, write, create spreadsheets
- **Calendar:** List, create, modify events
- **Forms:** Create, get forms
- **Tasks:** List, create, update tasks

**Best for:**
- Email automation
- Document management
- File storage and sharing
- Calendar scheduling
- Task management
- Form creation

**Example use cases:**
- Send campaign deliverables via email
- Upload assets to Google Drive
- Create shared Google Docs
- Schedule campaign launch events
- Manage marketing task lists

**Which agents use it:**
- gmail-agent (email sending)
- All agents (for Drive uploads, doc creation)

**Example invocation:**
```
"Use gmail-agent to send this campaign brief via email with
the PDF attachment, then upload the PDF to Google Drive and
share the Drive link."
```

---

### 3. perplexity - Web Search & Research

**Description:** Web search and research with citations using Perplexity AI.

**Available tools:**
- `perplexity_ask` - Conversational search with citations
- `perplexity_reason` - Deep reasoning and analysis
- `perplexity_search` - Ranked web search results (requires specific API key)
- `perplexity_research` - Comprehensive research reports (may require specific plan)

**Best for:**
- Market research
- Competitive intelligence
- Industry trends
- Best practices research
- Citation-backed insights
- Comparative analysis

**Example use cases:**
- Research industry best practices
- Analyze competitor strategies
- Find market trends
- Gather evidence-backed insights
- Comparative product analysis

**Which agents use it:**
- research-agent (primary)
- seo-specialist (for keyword research)
- analyst (for market analysis)
- copywriter (for topic research)

**Example invocation:**
```
"Use research-agent with perplexity to research current AI marketing
trends and provide citation-backed insights on what's working in 2025."
```

---

### 4. google-drive - Drive File Operations

**Description:** Google Drive file operations (search, upload, download, manage).

**Available tools:**
- `search_drive_files` - Search for files
- `get_drive_file_content` - Read file contents
- `create_drive_file` - Upload new files

**Best for:**
- File storage
- Asset management
- File sharing
- Content delivery

**Example use cases:**
- Upload campaign deliverables
- Search for brand assets
- Share files with team
- Organize marketing materials

**Which agents use it:**
- All agents (for file operations)
- Particularly gmail-agent (for attachments)

**Example invocation:**
```
"Upload this presentation to Google Drive in the 'Marketing Campaigns'
folder and share the link."
```

---

### 5. bright-data - Web Scraping & Lead Generation

**Description:** 60+ web scrapers for lead generation, SERP scraping, and competitive intelligence.

**Available tools:**
- `search_engine` - Scrape Google/Bing/Yandex search results
- `scrape_as_markdown` - Scrape webpages as markdown
- `search_engine_batch` - Batch search queries
- `scrape_batch` - Batch webpage scraping

**Best for:**
- B2B lead generation
- Local business leads
- SERP analysis
- Competitor analysis
- Web content extraction
- Market intelligence

**Example use cases:**
- Find 50 SaaS companies in San Francisco
- Scrape competitor landing pages
- Extract SERP features for SEO
- Gather local business leads
- Competitive intelligence gathering

**Which agents use it:**
- lead-gen-agent (primary - for lead generation)
- seo-specialist (for SERP analysis)
- research-agent (for competitive intelligence)
- analyst (for market research)
- landing-page-specialist (for competitor analysis)

**Example invocation:**
```
"Use lead-gen-agent with bright-data to find 50 B2B SaaS companies
in San Francisco with 50-200 employees. Include company name, website,
industry, and estimated employee count."
```

---

### 6. n8n-mcp - Workflow Automation

**Description:** Trigger n8n workflows and connect to 400+ integrations.

**Available tools:**
- Workflow management (list, get, create, update, delete)
- Execution management (trigger, monitor, manage)
- Validation and testing tools

**Best for:**
- Workflow automation
- Integration orchestration
- Complex multi-step processes
- API integrations
- Scheduled tasks

**Example use cases:**
- Trigger campaign workflows
- Automate social media posting
- Schedule email sequences
- Integrate with marketing tools
- Orchestrate complex processes

**Which agents use it:**
- router-agent (for campaign orchestration)
- Any agent (for workflow triggers)

**Example invocation:**
```
"Use router-agent with n8n to trigger our 'Product Launch Campaign'
workflow which sends emails, posts to social media, and updates our CRM."
```

---

### 7. sequential-thinking - Structured Reasoning

**Description:** Structured step-by-step reasoning for complex problem-solving.

**Available tools:**
- `sequentialthinking` - Break down problems into logical steps

**Best for:**
- Complex problem-solving
- Multi-step planning
- Logical reasoning
- Decision analysis
- Strategy development

**Key features:**
- Step-by-step thought process
- Revisions and backtracking
- Hypothesis generation and verification
- Branch exploration
- Structured output

**Example use cases:**
- Campaign strategy development
- Complex problem analysis
- Multi-step planning
- Decision-making processes
- Strategic thinking

**Which agents use it:**
- router-agent (for campaign planning)
- content-strategist (for strategy development)
- analyst (for analysis)

**Example invocation:**
```
"Use content-strategist with sequential-thinking to develop a
comprehensive Q2 content strategy. Break down the problem into
logical steps and explore different approaches."
```

---

## Real-World Marketing Scenarios

### Scenario 1: Complete Product Launch Campaign

**Goal:** Launch a new SaaS product with full marketing campaign

**Workflow:**
```
1. Use router-agent to plan campaign structure
   - Identify deliverables needed
   - Create timeline
   - Assign sub-agents

2. Use research-agent with perplexity
   - Research SaaS launch best practices
   - Analyze competitor launches
   - Gather evidence-backed insights

3. Use lead-gen-agent with bright-data
   - Find 100 target companies
   - Extract contact information
   - Build prospect list

4. Use copywriter to create content
   - Blog post announcing launch
   - Email sequence (5 emails)
   - Website copy

5. Use visual-designer with algorithmic-art
   - Generate unique launch visuals
   - Create social media art
   - Design email headers

6. Use social-media-manager with slack-gif-creator
   - Create animated launch GIF
   - Write social media posts
   - Schedule content

7. Use landing-page-specialist with artifacts-builder
   - Build interactive landing page
   - Apply theme-factory "modern" theme
   - Implement conversion tracking

8. Use presentation-designer
   - Create sales deck
   - Apply theme-factory styling
   - Generate visual assets

9. Use email-specialist + gmail-agent
   - Write email campaign
   - Send to prospect list
   - Track responses

10. Use analyst
    - Track campaign metrics
    - Generate performance report
    - Provide recommendations
```

**Estimated Timeline:** 2-3 days with agent automation

---

### Scenario 2: Visual Content Creation Blitz

**Goal:** Create 20 unique social media visuals in one session

**Workflow:**
```
1. Use visual-designer with algorithmic-art
   - Generate 10 flow field designs
   - Vary colors and parameters
   - Export at 1200x675px (Twitter/LinkedIn)

2. Use visual-designer with canvas-design
   - Create 5 professional posters
   - Apply brand colors
   - Export as PNG

3. Use social-media-manager with slack-gif-creator
   - Create 5 animated GIFs
   - Product features, launches, celebrations
   - Optimize for Slack/social media

4. Upload all to Google Drive
   - Organize in folders by type
   - Share folder link with team
```

**Estimated Time:** 1-2 hours

---

### Scenario 3: Competitive Intelligence Report

**Goal:** Analyze 5 competitors and create comprehensive report

**Workflow:**
```
1. Use research-agent with perplexity
   - Research competitor companies
   - Find recent news and updates
   - Gather market positioning

2. Use research-agent with playwright
   - Navigate to competitor sites
   - Capture screenshots
   - Extract key messaging

3. Use landing-page-specialist with bright-data
   - Scrape competitor landing pages
   - Extract layout patterns
   - Analyze conversion elements

4. Use analyst with sequential-thinking
   - Compare competitor strategies
   - Identify gaps and opportunities
   - Develop recommendations

5. Use copywriter with internal-comms
   - Write executive summary
   - Create detailed report
   - Include citations and evidence

6. Use pdf-specialist with canvas-design
   - Create beautiful PDF report
   - Professional layout
   - Include screenshots and data

7. Upload to Google Drive
   - Share with leadership
   - Present findings
```

**Estimated Time:** Half day

---

### Scenario 4: Interactive Landing Page from Figma

**Goal:** Implement a Figma design as an interactive React landing page

**Workflow:**
```
1. Use visual-designer with figma
   - Extract design from Figma file
   - Get color palette and typography
   - Download assets

2. Use landing-page-specialist with artifacts-builder
   - Build React landing page
   - Use Tailwind CSS for styling
   - Implement with shadcn/ui components
   - Match Figma design exactly

3. Use landing-page-specialist with theme-factory
   - Apply "professional" theme
   - Ensure consistent branding
   - Adjust to match brand guidelines

4. Test and refine
   - Check responsive behavior
   - Validate forms
   - Test interactions

5. Export and deploy
   - Generate HTML/CSS/JS bundle
   - Deploy to hosting
   - Share with team
```

**Estimated Time:** 2-4 hours

---

### Scenario 5: Email Campaign with Attachments

**Goal:** Send personalized email campaign with PDF whitepaper to 50 leads

**Workflow:**
```
1. Use pdf-specialist
   - Create whitepaper PDF
   - Professional layout
   - Include branding

2. Use email-specialist
   - Write email copy
   - Personalization tokens
   - Clear CTA

3. Use gmail-agent with google-workspace MCP
   - Send emails with PDF attachment
   - Track opens (if using email platform)
   - Follow up sequences

4. Use analyst
   - Track response rates
   - Measure engagement
   - Report on performance
```

**Estimated Time:** Half day

---

### Scenario 6: Internal Status Report

**Goal:** Create Q1 marketing status report for leadership

**Workflow:**
```
1. Use analyst
   - Gather campaign metrics
   - Calculate ROI
   - Identify trends

2. Use copywriter with internal-comms
   - Write status report
   - Use company format
   - Include executive summary
   - Highlight key wins and challenges

3. Use presentation-designer with theme-factory
   - Create visual presentation
   - Apply "corporate" theme
   - Include charts and data

4. Share with leadership
   - Upload to Google Drive
   - Send via gmail-agent
   - Schedule review meeting
```

**Estimated Time:** 2-3 hours

---

### Scenario 7: SEO Content Cluster

**Goal:** Create a content cluster on "AI Marketing" with 1 pillar post and 5 supporting articles

**Workflow:**
```
1. Use seo-specialist with perplexity
   - Research "AI marketing" keywords
   - Find related topics
   - Analyze SERP features

2. Use research-agent with bright-data
   - Scrape top 10 search results
   - Analyze content structure
   - Identify content gaps

3. Use copywriter
   - Write pillar post (3000 words)
   - Write 5 supporting articles (1500 words each)
   - Interlink strategically
   - Include SEO keywords naturally

4. Use visual-designer with canvas-design
   - Create featured images for each post
   - Design infographics
   - Create shareable graphics

5. Use social-media-manager
   - Create social posts for each article
   - Schedule promotion
   - Use algorithmic-art for unique visuals

6. Upload to Google Drive
   - Organize by topic
   - Share with content team
```

**Estimated Time:** 1-2 days

---

## Advanced Multi-Skill Workflows

### Workflow 1: "The Complete Campaign"

**Combines:** 8+ skills and 5+ MCPs

```
Goal: Launch new product with full campaign

Steps:
1. router-agent + sequential-thinking
   → Develop campaign strategy with structured reasoning

2. research-agent + perplexity + bright-data + playwright
   → Market research, competitor analysis, lead generation

3. copywriter + internal-comms
   → Blog posts, emails, internal status updates

4. visual-designer + algorithmic-art + canvas-design
   → Unique social art, professional posters

5. social-media-manager + slack-gif-creator
   → Social posts, animated GIFs

6. landing-page-specialist + artifacts-builder + theme-factory
   → Interactive React landing page with professional theme

7. presentation-designer + theme-factory
   → Sales deck with consistent branding

8. pdf-specialist + canvas-design + pdf-filler
   → Whitepaper PDF with beautiful design and fillable forms

9. email-specialist + gmail-agent + google-workspace
   → Email campaign with attachments sent via Gmail

10. analyst + sequential-thinking
    → Performance analysis with structured reasoning

11. All content uploaded via google-workspace to Drive
    → Organized, shared, delivered
```

**Result:** Complete multi-channel campaign delivered in days instead of weeks

---

### Workflow 2: "The Visual Content Factory"

**Combines:** 4 visual skills

```
Goal: Create 50+ visual assets in one session

Tools used:
- algorithmic-art (20 unique generative art pieces)
- canvas-design (15 professional posters/banners)
- slack-gif-creator (10 animated GIFs)
- theme-factory (5 themed artifact sets)

Process:
1. Define brand colors and themes
2. Generate algorithmic art variations
3. Create canvas-design posters
4. Produce animated GIFs
5. Apply theme-factory to artifact sets
6. Upload all to Drive with filesystem organization

Result: Complete visual asset library ready for use
```

---

### Workflow 3: "The Research & Report Pipeline"

**Combines:** Research MCPs + document skills

```
Goal: Comprehensive market analysis report

Tools used:
- perplexity (market research)
- playwright (website analysis)
- bright-data (competitor scraping)
- sequential-thinking (analysis)
- internal-comms (report writing)
- canvas-design (PDF creation)
- google-workspace (delivery)

Process:
1. Research with perplexity (trends, insights)
2. Scrape competitors with bright-data
3. Analyze websites with playwright
4. Structure analysis with sequential-thinking
5. Write report with internal-comms format
6. Design PDF with canvas-design
7. Deliver via google-workspace

Result: Professional research report with citations
```

---

### Workflow 4: "The Interactive Experience Builder"

**Combines:** Development skills + themes

```
Goal: Build complex interactive marketing experience

Tools used:
- artifacts-builder (React development)
- theme-factory (consistent theming)
- figma (design extraction)
- filesystem (asset management)

Process:
1. Extract design from Figma
2. Build with artifacts-builder (React + Tailwind + shadcn/ui)
3. Apply theme-factory for consistent styling
4. Manage assets with filesystem
5. Deploy interactive experience

Result: Modern, interactive web experience
```

---

## Troubleshooting

### Skills Not Available

**Problem:** Agent says skill is not available

**Solutions:**
1. Check `MARKETING_TEAM/.claude/settings.json` - is the skill enabled?
2. Verify the skill name is spelled correctly
3. Check if the skill is listed in the agent's frontmatter
4. Try invoking with explicit skill mention: "Use X agent with Y skill"

---

### MCP Tools Not Working

**Problem:** MCP tool returns error or not found

**Solutions:**
1. Verify `.claude.json` has the MCP server configured
2. Check `"mcpServers": "inherit"` is set in MARKETING_TEAM/.claude/settings.json
3. Ensure MCP server is running (test in Claude Desktop first)
4. Verify API keys are set correctly in .claude.json
5. Check server logs for error messages

---

### Skill Conflicts

**Problem:** Multiple skills trying to do the same thing

**Solutions:**
1. Be explicit about which skill to use: "Use X skill (not Y)"
2. Specify in agent frontmatter which skill is preferred
3. Guide the agent with clear instructions

---

### Performance Issues

**Problem:** Agent is slow or times out

**Solutions:**
1. Break complex tasks into smaller steps
2. Use sequential-thinking for complex problems
3. Reduce number of parallel skill uses
4. Simplify prompts

---

### Output Quality Issues

**Problem:** Skills produce unexpected results

**Solutions:**
1. Provide more detailed instructions
2. Specify output requirements clearly
3. Use examples in your prompts
4. Iterate with feedback

---

### Integration Errors

**Problem:** Skills not working with MCPs

**Solutions:**
1. Test skill and MCP separately first
2. Verify API permissions and credentials
3. Check rate limits on external services
4. Review error messages carefully

---

## Summary

You now have **13 powerful skills** and **7 MCP servers** available to all your marketing agents. This creates endless possibilities for marketing automation, content creation, and campaign management.

**Key takeaways:**
- Skills and MCPs work automatically when agents need them
- Be explicit when you want specific skills used
- Combine multiple skills for complex workflows
- All 16 marketing agents have access to everything
- Experiment and iterate to find optimal workflows

**Next steps:**
1. Try simple single-skill tasks first
2. Experiment with combining 2-3 skills
3. Build complex multi-agent workflows
4. Create custom skills with skill-creator
5. Integrate external services with mcp-builder

Happy creating!
