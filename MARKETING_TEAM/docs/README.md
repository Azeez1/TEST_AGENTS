# MARKETING_TEAM Documentation

## 📁 Folder Structure

All documentation is organized into subfolders by type:

```
docs/
├── getting-started/     # Setup and configuration guides
├── guides/              # How-to guides, usage instructions, workflows
├── architecture/        # Technical architecture and build docs
└── reference/           # API references and quick lookups
```

---

## 📚 Documentation Index

### Getting Started
- **[api-setup.md](getting-started/api-setup.md)** - API configuration (OpenAI, Gmail, Drive, Perplexity)

### Guides
- **[usage-guide.md](guides/usage-guide.md)** - Complete usage examples for all agents
- **[campaign-examples.md](guides/campaign-examples.md)** - Real campaign examples
- **[skills-and-mcp-guide.md](guides/skills-and-mcp-guide.md)** - Complete skills & MCP reference (50+ pages)
- **[SKILLS_QUICK_REFERENCE.md](guides/SKILLS_QUICK_REFERENCE.md)** - Quick lookup tables
- **[PERPLEXITY_RESEARCH_TOOLS.md](guides/PERPLEXITY_RESEARCH_TOOLS.md)** - Hybrid research system guide
- **[HYBRID_RESEARCH_SUMMARY.md](guides/HYBRID_RESEARCH_SUMMARY.md)** - Executive summary
- **[DECISION_LOGIC_UPDATE.md](guides/DECISION_LOGIC_UPDATE.md)** - Agent decision logic explanation
- **[HYBRID_OUTPUT_STRATEGY.md](guides/HYBRID_OUTPUT_STRATEGY.md)** - Output folder organization

### Architecture
- **[system-architecture.md](architecture/system-architecture.md)** - System design overview
- **[mcp-config.md](architecture/mcp-config.md)** - MCP configuration details
- **[BUILD_NOTES.md](architecture/BUILD_NOTES.md)** - Perplexity research build summary

### Reference
- (No files yet - for API docs and quick lookups)

---

## 🎯 Where to Put New Documentation

### Decision Matrix

| Type of Document | Folder | Examples |
|------------------|--------|----------|
| Setup/Configuration guide | `getting-started/` | API setup, environment config |
| Usage guide or how-to | `guides/` | Feature guides, workflows, examples |
| Technical architecture | `architecture/` | System design, build notes |
| API reference or lookup | `reference/` | API docs, parameter lists |

### Quick Rules

1. **Setting up APIs or environment?** → `getting-started/`
2. **How to use a feature or tool?** → `guides/`
3. **Technical architecture or build notes?** → `architecture/`
4. **API reference or lookup table?** → `reference/`
5. **When in doubt?** → Put in `guides/` (most common)

---

## 📝 Documentation Guidelines

### File Naming
- Use descriptive names in kebab-case: `perplexity-research-tools.md`
- OR use UPPERCASE for important docs: `SKILLS_QUICK_REFERENCE.md`
- Be consistent within each folder

### Structure
- Start with a clear title (H1: `#`)
- Add a table of contents for long docs
- Use sections (H2: `##`) to organize content
- Include examples and code blocks
- Link to related documentation

### Content
- Write for the intended audience (developers, marketers, or agents)
- Include "Quick Start" sections for complex topics
- Add decision matrices and flowcharts where helpful
- Keep it up-to-date when features change

---

## 🔍 Finding Documentation

**For agents:** Check `guides/` for feature-specific documentation
**For setup:** Check `getting-started/` for configuration guides
**For architecture:** Check `architecture/` for technical details
**For quick lookups:** Check `reference/` for API docs

---

## ✨ Recent Updates

**2025-01-19:**
- Reorganized all docs into proper subfolders
- Moved research guides to `guides/`
- Moved BUILD_NOTES to `architecture/`
- Added decision logic documentation
- Created this README

---

**Maintained by:** MARKETING_TEAM
**Last Updated:** 2025-01-19
