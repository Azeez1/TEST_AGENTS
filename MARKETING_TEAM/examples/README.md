# Marketing Team Examples

This folder contains **curated examples** of what the marketing agents can produce. These are reference materials, not production deliverables.

## Purpose

- **Demonstrate capabilities** - Show what each skill and agent can create
- **Learning resource** - Help users understand agent outputs
- **Testing artifacts** - Verify skills are working correctly
- **Portfolio pieces** - Showcase system capabilities

## Structure

```
examples/
├── README.md (this file)
└── skills/               ← Examples organized by skill
    ├── algorithmic-art/  ← Generative p5.js art
    ├── canvas-design/    ← PNG/PDF design outputs
    ├── slack-gif-creator/ ← Animated GIFs
    ├── theme-factory/    ← Themed artifacts
    ├── artifacts-builder/ ← React components
    ├── internal-comms/   ← Newsletters, status reports
    ├── blog-posts/       ← Sample blog content
    ├── social-media/     ← Sample social posts
    ├── landing-pages/    ← Sample landing pages
    └── presentations/    ← Sample pitch decks
```

## What Goes Here

### ✅ Include
- Skill demonstrations (one example per skill)
- High-quality reference outputs
- Test artifacts that verify functionality
- Non-sensitive, shareable content
- Small-to-medium file sizes (< 5 MB ideal)

### ❌ Exclude
- Real client work (use `outputs/` instead)
- Sensitive/proprietary content
- Large files (videos > 10 MB, high-res images)
- Work-in-progress drafts
- Personal/private deliverables

## Examples vs Outputs vs Templates

| Folder | Purpose | Git Tracked | Use Case |
|--------|---------|-------------|----------|
| **examples/** | Reference & demos | ✅ Yes | "Show me what algorithmic-art can do" |
| **outputs/** | Real deliverables | ❌ No | "Generate a blog post for my campaign" |
| **templates/** | Starting points | ✅ Yes | "Use the blog template as a foundation" |

## Adding New Examples

When you create something worth preserving as a reference:

1. **Generate in outputs/ first** - Let agents work in their normal folder
2. **Review quality** - Is it a good example? Does it showcase the skill well?
3. **Copy to examples/** - Move it to the appropriate skill folder
4. **Update this README** - Add a note about what the example demonstrates
5. **Commit to git** - Track it in version control

## Current Examples

### algorithmic-art
- **data_flow_dynamics.html** - Flow field generative art with 3,000 particles, demonstrates seed navigation, parameter controls, and Anthropic brand colors

### Coming Soon
- canvas-design examples (conference posters, social media graphics)
- slack-gif-creator examples (animated GIFs)
- theme-factory examples (themed artifacts)
- blog-posts examples (long-form content)
- landing-pages examples (conversion-focused pages)

## Usage

Reference examples when:
- Testing that skills are working
- Learning what each skill can produce
- Showing stakeholders system capabilities
- Debugging agent output issues
- Creating new similar content

## Notes

- **File sizes**: Keep examples under 5 MB when possible for git efficiency
- **Updates**: Examples can be updated/improved over time
- **Organization**: One subfolder per skill or content type
- **Naming**: Use descriptive names (not "test1.html", but "data_flow_dynamics.html")

---

**Last Updated:** 2025-10-18
**Total Examples:** 1 (algorithmic-art)
