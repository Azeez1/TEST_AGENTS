---
globs:
  - "*_TEAM/**"
  - ".claude/agents/**"
description: Enforce workspace isolation between teams
---

# Workspace Boundary Rules

## Team Isolation
- Agents MUST only write files within their own team directory
- MARKETING_TEAM agents write to `MARKETING_TEAM/outputs/`, `MARKETING_TEAM/memory/`
- ENGINEERING_TEAM agents write to `ENGINEERING_TEAM/outputs/`, `ENGINEERING_TEAM/docs/`
- Same pattern for QA_TEAM, PROPOSAL_TEAM, FINANCIAL_TEAM, SALES_TEAM
- **Exception:** supervisor agent has cross-team read/write authority

## Cross-Team Access
- Cross-team memory reads are FORBIDDEN (e.g., MARKETING cannot read FINANCIAL_TEAM/memory/)
- Cross-team output writes are FORBIDDEN
- ENGINEERING_TEAM has limited cross-team write for infrastructure tasks
- QA_TEAM has read-only access to other teams for test generation

## Path Rules
- All file operations MUST use absolute paths (never relative like `./outputs/`)
- Call `validate_workspace()` and `get_absolute_paths()` at task start
- Output files NEVER go to repository root — always to `{TEAM}/outputs/{subfolder}/`
- Read `output_paths.json` from team memory for canonical directory paths

## Root-Level File Protection
- Only supervisor agent may modify root-level files (CLAUDE.md, LLAR_CONFIG.json, TOOL_REGISTRY.md)
- Agent definitions (`.claude/agents/*.md`) require explicit user instruction to modify
