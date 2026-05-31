# CODEX_TEAM

Codex-native operators for maintaining the Codex sidecar layer in this repo.

This team is intentionally separate from Claude source-of-truth files. Its
source agents live in `CODEX_TEAM/.codex/agents/` and are exported into
`.codex/agents/CODEX_TEAM/` by `scripts/export_codex_layer.py`.

## Scope

- Maintain `.codex/` routing, generated agent mirrors, skills, hooks, and MCP
  handoff files.
- Audit Codex coverage against the L1-L13 agentic engineering lessons in
  `LEARNING/`.
- Create Codex-only improvements that do not modify `.claude/`, `.mcp.json`, or
  Claude agent definitions unless the user explicitly asks.

## Source Of Truth

- Claude runtime: `.claude/`, team `.claude/agents/`, and `.mcp.json`
- Codex runtime: `CODEX_TEAM/.codex/agents/`, `.codex/`, and
  `C:/Users/sabaa/.codex/`

## Export

Run from the repo root:

```powershell
python scripts\export_codex_layer.py
```

For full local refresh:

```powershell
python scripts\export_codex_layer.py --write-local-secrets --install-global-skills --write-codex-mcp-config
```
