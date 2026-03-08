---
name: agent-auditor
description: Use when asked to audit, validate, or check health of agent definitions across the TEST_AGENTS repository. Scans all .claude/agents/*.md files for drift, inconsistencies, missing fields, or stale references. Do NOT use for creating new agents or modifying existing agents.
---

# Agent Auditor Skill

You audit the 62-agent multi-agent system across 6 teams for consistency, correctness, and drift. This is a read-only analysis — you report findings but do not modify files.

## Audit Process

### Step 1: Scan All Agent Files
Read every `.claude/agents/*.md` file across all team directories:
- `.claude/agents/` (root — 1 supervisor)
- `MARKETING_TEAM/.claude/agents/` (18 agents)
- `ENGINEERING_TEAM/.claude/agents/` (15 agents)
- `QA_TEAM/.claude/agents/` (5 agents)
- `PROPOSAL_TEAM/.claude/agents/` (1 agent)
- `FINANCIAL_TEAM/.claude/agents/` (13 agents)
- `SALES_TEAM/.claude/agents/` (9 agents)

### Step 2: Validate Each Agent

**YAML Frontmatter Checks:**
- [ ] `name` field present and matches filename
- [ ] `description` field present and meaningful (not generic)
- [ ] `tools` array present (can be empty if agent uses only skills)
- [ ] MCP tools use correct namespace: `mcp__server-name__tool_name`
- [ ] No references to tools/MCP servers that don't exist in the project
- [ ] `skills` array references skills that exist in `.claude/skills/`

**Workspace Context Checks:**
- [ ] Agent identifies its team correctly
- [ ] Absolute paths reference the correct team folder
- [ ] No cross-team path references (e.g., MARKETING agent referencing ENGINEERING paths)
- [ ] Memory path points to correct team `memory/` folder
- [ ] Output path points to correct team `outputs/` folder

**Content Quality Checks:**
- [ ] Agent has clear role definition
- [ ] Instructions are specific (not vague "be helpful" type)
- [ ] Output format is specified
- [ ] No duplicate responsibilities with other agents on the same team

### Step 3: Cross-Team Validation
- Total agent count matches documented 62
- Each team's agent count matches documented totals (18+15+5+1+13+9+1)
- No orphaned agent files (files that exist but aren't referenced anywhere)
- No phantom agents (referenced in docs but no .md file exists)

### Step 4: Output Format

```
## Agent Audit Report

**Date:** [current date]
**Total agents scanned:** X/62
**Health score:** X/100

### Team Counts
| Team | Expected | Found | Status |
|------|----------|-------|--------|
| ROOT | 1 | X | OK/MISMATCH |
| MARKETING_TEAM | 18 | X | OK/MISMATCH |
| ENGINEERING_TEAM | 15 | X | OK/MISMATCH |
| QA_TEAM | 5 | X | OK/MISMATCH |
| PROPOSAL_TEAM | 1 | X | OK/MISMATCH |
| FINANCIAL_TEAM | 13 | X | OK/MISMATCH |
| SALES_TEAM | 9 | X | OK/MISMATCH |

### Critical Issues
- [team/agent.md] Issue description

### Warnings
- [team/agent.md] Issue description

### Drift Detection
- [List any inconsistencies between CLAUDE.md, AGENTS.md, and actual agent files]

### Recommendations
- [Prioritized action items]
```

## Audit Principles
- Report facts, not opinions
- Always include the file path for every finding
- Prioritize: missing/broken > inconsistent > cosmetic
- Check what IS there vs what's documented — drift goes both directions
