# 🚀 MARKETING_TEAM Usage Guide

## Your 13 Marketing Agents Are Ready!

No Python code to run. No setup. Just talk to Claude Code.

---

## Quick Start

```
You: "Use the social-media-manager subagent to create a LinkedIn post about AI trends"

Claude: [becomes social-media-manager]
        [creates your post]
        [returns formatted content]
```

**That's it!**

---

## All 13 Agents

### 1. router-agent (The Coordinator)
**When to use:** Complex multi-step marketing requests

```
"Use router-agent to create a complete product launch campaign"
```

**It will:**
- Classify your intent
- Delegate to specialist agents (copywriter, designer, social manager)
- Coordinate all work
- Return complete campaign

### 2. copywriter (Long-Form Content)
**When to use:** Blog posts, articles, white papers

```
"Use copywriter to write a 2000-word blog about AI in marketing"
```

**It will:**
- Get brand voice guidelines
- Research keywords
- Write engaging content
- Include CTAs
- Return Markdown format

### 3. editor (Quality Assurance)
**When to use:** Review and improve content

```
"Use editor to review this blog post for clarity and grammar"
```

**It will:**
- Check grammar and style
- Improve clarity
- Ensure brand voice
- Suggest improvements

### 4. social-media-manager (Social Posts)
**When to use:** X/Twitter, LinkedIn posts

```
"Use social-media-manager to create a Twitter thread about automation"
```

**It will:**
- Format for platform (280 chars for X, etc.)
- Add hashtags
- Optimize for engagement
- Create multiple versions

### 5. visual-designer (Images)
**When to use:** Image generation with GPT-4o

```
"Use visual-designer to create a LinkedIn header image about AI agents"
```

**It will:**
- Generate image with GPT-4o
- Follow visual guidelines
- Upload to Google Drive
- Return shareable link

### 6. video-producer (Videos)
**When to use:** Video generation with Sora

```
"Use video-producer to create a 10-second product demo video"
```

**It will:**
- Generate video with Sora
- Follow brand guidelines
- Upload to Google Drive
- Return shareable link

### 7. seo-specialist (SEO & Research)
**When to use:** Keyword research, trend analysis

```
"Use seo-specialist to research trending AI marketing keywords"
```

**It will:**
- Research with Playwright
- Analyze competitors
- Find keywords
- Provide insights

### 8. email-specialist (Email Copywriting)
**When to use:** Email campaign writing

```
"Use email-specialist to write a 3-email welcome sequence"
```

**It will:**
- Write compelling emails
- Follow email best practices
- Include CTAs
- Suggest send schedule

### 9. gmail-agent (Email Sending)
**When to use:** Actually send emails via Gmail

```
"Use gmail-agent to send this newsletter to my subscribers"
```

**It will:**
- Connect to Gmail API
- Send emails
- Track sends
- Report status

### 10. pdf-specialist (PDF Creation)
**When to use:** Whitepapers, lead magnets

```
"Use pdf-specialist to create a whitepaper PDF about AI ROI"
```

**It will:**
- Generate professional PDF
- Include branding
- Upload to Google Drive
- Return shareable link

### 11. presentation-designer (PowerPoint)
**When to use:** Presentation decks

```
"Use presentation-designer to create a 10-slide pitch deck"
```

**It will:**
- Create PowerPoint
- Professional design
- Upload to Google Drive
- Return shareable link

### 12. analyst (Performance Analysis)
**When to use:** Data analysis, insights

```
"Use analyst to analyze last month's campaign performance"
```

**It will:**
- Analyze data
- Provide insights
- Create reports
- Recommend improvements

### 13. content-strategist (Campaign Planning)
**When to use:** Full campaign orchestration

```
"Use content-strategist to plan a Q1 marketing campaign"
```

**It will:**
- Plan strategy
- Coordinate all content types
- Delegate to specialists
- Create complete campaign

---

## Real-World Examples

### Example 1: Create a Blog Post

```
You: "Use copywriter to write a blog post about autonomous AI agents in marketing, 2000 words, SEO-optimized for 'AI marketing automation'"

Claude (as copywriter):
  [Using get_brand_voice tool...]

  I'll write an engaging blog post for you!

  # The Rise of Autonomous AI Agents in Marketing

  In 2025, marketing teams discovered something revolutionary...

  [2000 words of content...]

  ## Call to Action
  Ready to transform your marketing with AI agents? [CTA here]

  ---
  SEO Keywords included:
  - AI marketing automation (8x)
  - Autonomous agents (12x)
  - Marketing AI (15x)

  Saved to: outputs/blog_posts/ai-agents-marketing.md
```

### Example 2: Complete Social Campaign

```
You: "Use router-agent to create a social media campaign for our new AI product launch"

Claude (as router-agent):
  Analyzing request... This requires multiple specialists.

  [Delegating to seo-specialist for research...]
  Found trending keywords: #AIProductivity, #AutomationTools

  [Delegating to copywriter for blog...]
  ✅ Blog post created (2000 words)

  [Delegating to social-media-manager for posts...]
  ✅ LinkedIn post created
  ✅ Twitter thread created (7 tweets)

  [Delegating to visual-designer for images...]
  ✅ 3 campaign images generated

  [Delegating to email-specialist for campaign...]
  ✅ 3-email sequence created

  Campaign Complete!

  All files uploaded to Google Drive:
  - Blog: [link]
  - Social posts: [link]
  - Images: [link]
  - Emails: [link]

  Ready to review or launch?
```

### Example 3: Quick Social Post

```
You: "Use social-media-manager to create a LinkedIn post celebrating our 10k users milestone"

Claude (as social-media-manager):
  [Using format_linkedin_post tool...]

  Here's your LinkedIn post:

  ---
  🎉 10,000 Users and Counting!

  We're thrilled to announce we've reached 10,000 amazing users!

  What started as an idea 2 years ago is now:
  ✨ 10K+ active users
  ✨ 50K+ AI agents deployed
  ✨ 95% customer satisfaction

  Thank you for being part of this journey! 🚀

  The best is yet to come.

  #Milestone #Growth #AITools #ThankYou #Community
  ---

  Would you like me to also create:
  1. A Twitter version?
  2. A header image (visual-designer)?
  3. An email to send to users (email-specialist)?
```

---

## Common Workflows

### Workflow 1: Blog Post → Social Posts → Images

```
You: "Use copywriter to write a blog about AI productivity tips"

[Wait for blog completion]

You: "Use social-media-manager to create social posts promoting this blog"

[Wait for posts]

You: "Use visual-designer to create 3 images for these social posts"

Done! Complete content package ready.
```

### Workflow 2: Full Campaign (Automated)

```
You: "Use content-strategist to create a complete campaign for our new feature release"

Claude (as content-strategist):
  [Automatically delegates to all necessary agents]
  [Coordinates everything]
  [Returns complete campaign package]
```

### Workflow 3: Research → Write → Review

```
You: "Use seo-specialist to research AI coding assistant keywords"

[Get keyword list]

You: "Use copywriter to write a blog optimized for these keywords"

[Get blog draft]

You: "Use editor to review and improve this blog"

[Get final polished blog]
```

---

## Tips & Best Practices

### 1. Start with router-agent for Complex Tasks
Let it coordinate specialists automatically:
```
"Use router-agent to plan my February social media calendar"
```

### 2. Be Specific About Requirements
Include details:
- Word count: "2000 words"
- Platform: "LinkedIn"
- Tone: "professional"
- Keywords: "AI automation, marketing"

### 3. Chain Agents for Multi-Step Tasks
```
"Use copywriter to write X, then use editor to review it, then use social-media-manager to create posts about it"
```

### 4. Use Automatic Delegation When Comfortable
Instead of: "Use copywriter to write a blog"
Just say: "Write a blog about AI trends"
I'll automatically invoke copywriter!

### 5. Review Agent Definitions
Check `.claude/agents/` to see:
- Each agent's capabilities
- Available tools
- Specific instructions

---

## Available Tools (Per Agent)

**copywriter:**
- get_brand_voice

**social-media-manager:**
- format_twitter_post
- format_linkedin_post
- extract_hashtags
- optimize_post_for_engagement

**visual-designer:**
- generate_gpt4o_image
- upload_file_to_drive

**video-producer:**
- generate_sora_video
- upload_file_to_drive

**gmail-agent:**
- send_gmail
- create_gmail_draft
- send_email_campaign

**seo-specialist:**
- Playwright MCP (web browsing)
- WebSearch

---

## Troubleshooting

### "Agent didn't respond correctly"
- Check if agent .md file exists
- Verify tools are working
- Be more specific in your request

### "Tools not working"
- Check .env file has API keys (OpenAI for images/videos)
- Verify Google credentials for Drive/Gmail
- Run `pip install -r requirements.txt`

### "Can't upload to Drive"
- Need credentials.json in MARKETING_TEAM folder
- First run opens browser for auth
- See README for setup

---

## Next Steps

1. **Try your first agent:**
   ```
   "Use social-media-manager to create a LinkedIn post about your favorite topic"
   ```

2. **Try automatic delegation:**
   ```
   "Create a blog post about AI trends"
   ```

3. **Try multi-agent coordination:**
   ```
   "Use router-agent to create a mini campaign for a product launch"
   ```

4. **Explore agent definitions:**
   ```bash
   ls .claude/agents/  # See all 13 agents
   cat .claude/agents/copywriter.md  # Read agent instructions
   ```

---

## Quick Reference

| Need | Use This Agent | Example |
|------|----------------|---------|
| Blog post | copywriter | "Use copywriter to write about X" |
| Social post | social-media-manager | "Use social-media-manager for LinkedIn post" |
| Image | visual-designer | "Use visual-designer to create image" |
| Video | video-producer | "Use video-producer for demo video" |
| Email campaign | email-specialist | "Use email-specialist for welcome emails" |
| Send email | gmail-agent | "Use gmail-agent to send newsletter" |
| SEO research | seo-specialist | "Use seo-specialist to find keywords" |
| PDF | pdf-specialist | "Use pdf-specialist for whitepaper" |
| PowerPoint | presentation-designer | "Use presentation-designer for pitch deck" |
| Campaign | content-strategist or router-agent | "Use router-agent for full campaign" |

---

**Your marketing team is ready! Just start talking to Claude Code.** 🚀

See [../../MULTI_AGENT_GUIDE.md](../../MULTI_AGENT_GUIDE.md) for more details on how the system works.
