# Sync Paperclip Agent Instructions

Regenerate all Paperclip agent instruction files (AGENTS.md) from the real TEST_AGENTS agent definitions.

## What This Does

Reads every agent definition from `{TEAM}/.claude/agents/*.md` and updates the corresponding Paperclip instruction file at `~/.paperclip/instances/default/companies/{companyId}/agents/{agentId}/instructions/AGENTS.md`.

This ensures Paperclip agents stay in sync with your Claude Code agent definitions after you make changes.

## Usage

```
/sync-paperclip              # Sync all 63 agents
/sync-paperclip marketing    # Sync MARKETING_TEAM only
/sync-paperclip engineering  # Sync ENGINEERING_TEAM only
/sync-paperclip financial    # Sync FINANCIAL_TEAM only
/sync-paperclip sales        # Sync SALES_TEAM only
/sync-paperclip qa           # Sync QA_TEAM only
/sync-paperclip proposal     # Sync PROPOSAL_TEAM only
/sync-paperclip root         # Sync ROOT (supervisor) only
```

## How It Works

1. Queries Paperclip API at `http://localhost:3100` to get all agent IDs and names
2. Maps each Paperclip agent to its TEST_AGENTS definition file using the agent name mapping
3. Reads the real agent definition (YAML frontmatter + instructions)
4. Generates a Paperclip-formatted AGENTS.md that includes:
   - Agent identity and role at Dux Machina OS
   - Working directory (`C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS`)
   - Persona definition path to the real `.claude/agents/{name}.md` file
   - Real capabilities, tools, skills, MCP servers from the definition
   - Team memory/config files section
   - Claude Memory System reference
   - Brand voice context
   - Output routing rules
   - Standard rules footer
5. Writes the updated instruction file

## Prerequisites

- Paperclip server must be running at `http://localhost:3100`
- Run `python INFRASTRUCTURE/scripts/sync_paperclip.py` directly if Paperclip is not running (uses cached agent mapping)

## When to Run

- After adding or modifying agent definitions in `.claude/agents/`
- After adding new skills or MCP servers
- After changing team structure or agent capabilities
- After any significant update to CLAUDE.md or memory files

## Instructions

Run the sync script:

```bash
python INFRASTRUCTURE/scripts/sync_paperclip.py $ARGUMENTS
```

If the script doesn't exist yet or fails, perform the sync manually:

1. For each team (MARKETING, ENGINEERING, FINANCIAL, SALES, QA, PROPOSAL):
   - Read every `.claude/agents/*.md` file in the team directory
   - Find the matching Paperclip agent by name
   - Read the Paperclip agent's current `instructions/AGENTS.md`
   - Rewrite it following the Copywriter template pattern (agent at `~/.paperclip/.../agents/e2764a41-.../instructions/AGENTS.md`)
   - Include: identity, working directory, persona path, capabilities from definition, tools/skills/MCP from YAML, team config files, Claude Memory System block, brand voice, output rules, standard footer
2. Report what was updated and any agents that couldn't be matched
