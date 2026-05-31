# L1-L13 Coverage Targets For Codex

This is the first working target matrix for bringing Codex up to the same
agentic engineering standard described in `LEARNING/agentic-engineering-self-study.md`.

## L1-L6 Leverage Points

1. Instructions: `AGENTS.md`, `.codex/AGENTS.md`, and team agent files define
   Codex behavior and boundaries.
2. Agent definitions: `CODEX_TEAM/.codex/agents/*.md` defines Codex-native
   specialists; `.codex/agents/**` contains generated runtime instructions.
3. Slash commands: `.codex/commands/*.md` provides sync and validation entry
   points.
4. Skills: `.codex/skills-export/**` and `C:/Users/sabaa/.codex/skills/**`
   provide reusable behavior.
5. Subagents: Codex task subagents are available when the user explicitly asks
   for delegation or parallel agents.
6. MCP servers: Codex MCP config is generated from `.mcp.json` into local
   Codex config files without modifying Claude.

## L7-L13 Lessons

7. ZTE: use scheduled tasks, hooks, validators, and notification hooks for
   low-risk recurring workflows.
8. Agentic layer: log runs, trace decisions, track failures, and summarize
   cost/status where available.
9. Context engineering: load only the relevant agent, skill, memory, and files
   needed for the task.
10. Prompt levels: prefer structured prompts, templates, chains, and meta-skills
    where they reduce repeated work.
11. Domain-specific agents: keep narrow specialists with non-overlapping
    ownership.
12. Multi-agent orchestration: split broad work into bounded Codex subagents
    only when explicitly authorized by the user.
13. Skills as learned behavior: capture proven repeatable workflows as Codex
    skills after the user asks to remember or codify them.

## Next Audit Output

The Codex leverage auditor should produce:

- status: `done`, `partial`, `missing`, or `blocked`
- evidence: exact file paths
- gap: one sentence
- next action: one concrete implementation step
