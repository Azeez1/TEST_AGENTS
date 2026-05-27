# TEST_AGENTS - AI Multi-Agent System

67 agents across 8 teams + 28 skills + 7 MCP servers. Pure Claude Code conversation — no Python orchestrators.

| Team | Agents | Orchestrator |
|------|--------|-------------|
| MARKETING_TEAM | 18 | router-agent |
| ENGINEERING_TEAM | 15 | cto |
| FINANCIAL_TEAM | 14 | cfo-agent |
| SALES_TEAM | 9 | sales-manager |
| QA_TEAM | 5 | test-orchestrator |
| VOICE_TEAM | 2 | voice-deployer + voice-onboarder |
| PROPOSAL_TEAM | 1 | rfp-agent |
| HEDGE_FUND | 1 | ict-trader |
| ROOT | 2 | supervisor + oracle |

Reference docs: [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) | [CLAUDE_REFERENCE.md](CLAUDE_REFERENCE.md) | [MCP_SETUP.md](MCP_SETUP.md)

---

## Use Existing Tools First

**ALWAYS use existing agents, tools, skills, and MCP servers BEFORE creating new implementations.**

**Priority:** Agents → Skills → MCP servers → Custom tools (`tools/`) → Create new (last resort)

Check: `.claude/agents/` → `.claude/skills/` → `.mcp.json` → `tools/` → Ask user

---

## Document Generation: Skill-First Mandate

When a deliverable format maps to a document skill, invoke the skill BEFORE writing custom code. Skills handle formatting, tables, brand consistency, and pitfalls that raw libraries miss.

| Format | Skill | Path |
|--------|-------|------|
| Word `.docx` | `docx` | `.claude/skills/document-skills/docx/SKILL.md` |
| PowerPoint `.pptx` | `pptx` | `.claude/skills/document-skills/pptx/SKILL.md` |
| Excel `.xlsx` | `xlsx` | `.claude/skills/document-skills/xlsx/SKILL.md` |
| PDF | `pdf` | `.claude/skills/document-skills/pdf/SKILL.md` |
| Poster / graphic | `canvas-design` | `.claude/skills/canvas-design/SKILL.md` |
| Infographic | `infographic-creator` | `.claude/skills/infographic-creator/SKILL.md` |
| Flow / architecture diagram | `flow-diagram` | `.claude/skills/flow-diagram/SKILL.md` |
| Editable diagram | `excalidraw-diagrams` | `.claude/skills/excalidraw-diagrams/SKILL.md` |
| Video / motion graphics | `remotion-video` | `.claude/skills/remotion-video/SKILL.md` |
| React artifact (claude.ai) | `artifacts-builder` | `.claude/skills/artifacts-builder/SKILL.md` |
| Web page / dashboard | `frontend-design` | `.claude/skills/frontend-design/SKILL.md` |
| Slack GIF | `slack-gif-creator` | `.claude/skills/slack-gif-creator/SKILL.md` |

Document skills are instruction bundles (read `SKILL.md` and follow its workflow), NOT slash commands. Only bypass when: user explicitly asks for custom code, no skill matches, or skill demonstrably failed.

---

## Browser Policy: Chrome MCP ONLY

Use `mcp__claude-in-chrome__*` for ALL browser tasks. This controls Azeez's real Chrome with logged-in sessions.

**DO NOT use Playwright** unless Azeez explicitly says so. Playwright = sandboxed, no sessions.

Workflow: `tabs_context_mcp` → `tabs_create_mcp` → `navigate` → `read_page`/`screenshot`

If Chrome MCP isn't connected: tell user to run `/chrome`. Do NOT fall back to Playwright.

---

## Agent Invocation

**Pattern:** `"Use [agent-name] to [goal] with [context]"` — agents are autonomous and know their tools.

Full guide: [AGENT_INVOCATION_BEST_PRACTICES.md](AGENT_INVOCATION_BEST_PRACTICES.md)

---

## Memory System

Agents auto-read config files at task start: `email_config.json`, `google_drive_config.json`, `brand_voice.json`, `visual_guidelines.json`, `output_paths.json`

Key rules:
- Use `tools/upload_to_drive.py` for Drive uploads (MCP broken for binary files)
- Use `tools/send_email_with_attachment.py` for emails with attachments
- Full guide: [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)

---

## MCP Error Quick Reference

**On ANY MCP error, READ `.claude/memory/mcp_lessons_learned.json` FIRST.**

| Error | Fix |
|-------|-----|
| MCP tools missing from list | Delete creds → kill port 8000 → RESTART Claude Code. **DO NOT script around it.** |
| `invalid_scope` / Error 400 | Delete `~/.google_workspace_mcp/credentials/EMAIL.json`, kill port 8000, retry |
| GSheet "... and X more rows" | Use browser Ctrl+F first, then read specific rows |
| Wrong sheet tab data | Include sheet name: `'SheetName!A1:Z100'` |

If google-workspace MCP tools are NOT in available tools list, DO NOT attempt Python scripts. Follow the 2-minute restart fix above.
