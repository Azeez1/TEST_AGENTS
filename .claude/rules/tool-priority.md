---
globs:
  - "**"
description: Enforce tool/MCP/skill priority hierarchy for all operations
---

# Tool Priority Rules

## Priority Hierarchy (ALWAYS follow this order)
1. **MCP Servers** — Use first (google-workspace, perplexity, bright-data, playwright, n8n-mcp, marketing-tools, sequential-thinking)
2. **Skills** — Use second (23 skills: document-skills, visual, n8n, frontend, video, research)
3. **Custom Python Tools** — Use third (tools/ folder: upload_to_drive, send_email_with_attachment, etc.)
4. **Create New** — LAST RESORT only after confirming nothing above exists

## Before Creating Anything New
- Check TOOL_REGISTRY.md for existing capabilities
- Check .mcp.json for MCP server tools
- Check .claude/skills/ for installed skills
- Check team tools/ folder for existing Python tools
- Ask the user if unsure: "Do we have a tool for this already?"

## What NOT To Do
- NEVER write new Python scripts for functionality an MCP server already provides
- NEVER create new image generation code when marketing-tools MCP has 5 image tools
- NEVER create new email scripts when google-workspace MCP handles Gmail
- NEVER install new libraries when existing tools already have the dependencies

## Skill Declaration Rules
- NEVER declare a skill in agent YAML tools unless it is enabled in the team's .claude/settings.json
- Verify skill exists at .claude/skills/{name}/SKILL.md before declaring
- If a skill is not enabled, either enable it in settings.json or remove from agent YAML
