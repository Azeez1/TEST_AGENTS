# Marketing Templates

This folder contains **reusable templates** that serve as starting points for common marketing deliverables. Agents can use these as foundations and customize them for specific campaigns.

## Purpose

- **Consistency** - Maintain brand voice and structure across content
- **Efficiency** - Start from proven frameworks instead of blank pages
- **Best practices** - Embed marketing principles into templates
- **Flexibility** - Templates are suggestions, not rigid requirements

## Structure

```
templates/
├── README.md (this file)
└── reusable/
    ├── blog_post_template.md
    ├── social_media_template.md
    ├── landing_page_template.html
    ├── email_template.md
    ├── presentation_outline.md
    └── campaign_brief_template.md
```

## Available Templates

### 1. Blog Post Template
**File:** `reusable/blog_post_template.md`
**Use when:** Writing long-form content (1500-3000 words)
**Agent:** copywriter
**Structure:** SEO-optimized with hook, body sections, CTA, metadata

### 2. Social Media Template
**File:** `reusable/social_media_template.md`
**Use when:** Creating platform-specific posts
**Agent:** social-media-manager
**Includes:** X/Twitter, LinkedIn, Facebook formats with hashtag strategies

### 3. Landing Page Template
**File:** `reusable/landing_page_template.html`
**Use when:** Building conversion-focused pages
**Agent:** landing-page-specialist
**Features:** Hero, features, testimonials, CTA sections

### 4. Email Template
**File:** `reusable/email_template.md`
**Use when:** Writing marketing emails or newsletters
**Agent:** email-specialist
**Structure:** Subject line formulas, body framework, CTA best practices

### 5. Presentation Outline
**File:** `reusable/presentation_outline.md`
**Use when:** Creating pitch decks or presentations
**Agent:** presentation-designer
**Framework:** Problem-solution-proof structure with slide breakdowns

### 6. Campaign Brief Template
**File:** `reusable/campaign_brief_template.md`
**Use when:** Planning multi-channel campaigns
**Agent:** router-agent or content-strategist
**Includes:** Goals, audience, channels, timeline, deliverables

## How Agents Use Templates

### Method 1: Direct Reference
```
"Use the blog post template to write about AI automation"
```
Agent reads the template and adapts it to the topic.

### Method 2: Structural Guidance
```
"Follow the landing page template structure for our SaaS product"
```
Agent uses the template's sections but creates custom content.

### Method 3: Hybrid Approach
```
"Start with the email template but make it more conversational"
```
Agent combines template guidance with specific customization.

## Customization

Templates are **starting points**, not rigid rules. Agents should:

✅ **Do adapt** - Modify structure for specific use cases
✅ **Do iterate** - Improve templates based on performance data
✅ **Do personalize** - Adjust tone/voice for different audiences
✅ **Do experiment** - Try variations to see what works best

❌ **Don't blindly copy** - Every piece should be unique
❌ **Don't ignore context** - Templates may not fit all situations
❌ **Don't skip research** - Templates don't replace audience analysis

## Adding New Templates

When you create a template worth preserving:

1. **Identify the pattern** - What makes this reusable?
2. **Generalize the structure** - Remove campaign-specific details
3. **Add placeholders** - Use [BRACKET NOTATION] for variables
4. **Document usage** - Explain when and how to use it
5. **Test with agents** - Verify agents can use it effectively
6. **Update this README** - Add it to the list above

## Template Variables

Use consistent notation for placeholders:

- `[COMPANY_NAME]` - Business name
- `[PRODUCT_NAME]` - Product/service name
- `[TARGET_AUDIENCE]` - Audience description
- `[KEY_BENEFIT]` - Primary value proposition
- `[CTA]` - Call-to-action
- `[BRAND_VOICE]` - Tone descriptor (professional, casual, etc.)
- `[DATE]` - Publication date
- `[AUTHOR]` - Content creator

## Examples vs Templates vs Outputs

| Folder | Purpose | Content Type |
|--------|---------|--------------|
| **templates/** | Starting frameworks | Blank/placeholder content |
| **examples/** | Reference samples | Complete finished pieces |
| **outputs/** | Real deliverables | Campaign-specific content |

**Example:**
- **Template:** Blog post structure with [TOPIC] placeholders
- **Example:** Finished "AI Marketing Trends 2024" blog post
- **Output:** Your actual blog post about your product

## Best Practices

### For Template Creators
- Keep templates simple and clear
- Include inline comments explaining sections
- Provide 2-3 variations when appropriate
- Test templates with different content types
- Update based on performance metrics

### For Template Users (Agents)
- Read the entire template before starting
- Understand the purpose of each section
- Adapt freely to match the specific need
- Don't force content into template structure if it doesn't fit
- Suggest improvements when you find better approaches

## Maintenance

Templates should be reviewed and updated:
- **Quarterly** - Check if structures still reflect best practices
- **After campaigns** - Incorporate learnings from successful content
- **When metrics change** - Adapt to new platform requirements (e.g., Twitter → X character limits)
- **On feedback** - Update based on team/audience feedback

## Version Control

Because templates are tracked in git:
- Review changes before committing updates
- Use descriptive commit messages ("Update blog template with SEO improvements")
- Consider keeping old versions in `templates/archived/` if major changes
- Document breaking changes in commit messages

---

**Last Updated:** 2025-10-18
**Total Templates:** 6
**Next Review:** 2026-01-18
