---
globs:
  - "**/.claude/agents/*.md"
description: Standards for agent definition files
---

# Agent Definition Standards

## Required YAML Frontmatter
Every agent .md file MUST include:
- `name:` — agent identifier (kebab-case, e.g., `visual-designer`)
- `description:` — clear one-line summary of what the agent does
- `tools:` — explicit list of tools this agent uses

## Tool Declaration Rules
- Only declare tools that actually exist (check MCP server, skills, and tools/ folder)
- Only declare skills verified as enabled in the team's `.claude/settings.json`
- Use correct naming: `snake_case` for Python tools, `mcp__server__action` for MCP tools, `kebab-case` for skills
- If a tool is deprecated or removed, delete it from the tools list entirely — do not comment it out

## Prompt Quality Standards
- Use explicit, measurable criteria — not vague instructions like "be thorough" or "ensure quality"
- Include validation gates with concrete pass/fail conditions
- Include 2-3 few-shot examples covering ambiguous cases where possible
- End with actionable instructions, not motivational statements

## Multi-Agent Skill Sharing
- When multiple agents declare the same skill, document a PRIMARY OWNER
- Primary owner has full skill capabilities; others use for specialized cases only
- Example: `canvas-design` PRIMARY = visual-designer; others use for specific visual needs

## Configuration Files Section
- Every agent SHOULD include a "Configuration Files (READ FIRST)" section
- List which memory files to read at task start (brand_voice.json, output_paths.json, etc.)
- This ensures consistent behavior across all agents in the team
