# Memory Routing Convention

**Status:** v1 — 2026-05-12
**Scope:** All agents and human contributors writing or updating memory in the TEST_AGENTS repo
**Rule:** Every new memory entry must be routable to exactly ONE tier in ONE location. Ambiguity = re-classify before writing.

---

## Why this exists

Without a routing convention, memory accumulates ad-hoc:
- MEMORY.md bloats (every prompt pays for stale entries)
- Team configs scatter across multiple files with overlapping concerns
- Topic knowledge gets duplicated in multiple memory layers
- Archived material gets lost or re-archived

This spec defines **where each kind of memory belongs** and **when an agent should write vs. propose**.

---

## The 5 Tiers (plus governance-level artifacts)

| Tier | Location | Auto-load | Lifetime | Use case |
|---|---|---|---|---|
| **HOT** | `~/.claude/projects/.../memory/MEMORY.md` | Every prompt | Daily reference, ≤30 days dormant | Frequently-referenced personal context — frameworks, current pipelines, brand, key relationships |
| **WARM** | `~/.claude/projects/.../memory/<topic>.md` | On-demand (linked from MEMORY.md) | Active reference, ≤90 days dormant | Detailed reference info — playbooks, runbooks, framework details, conventions |
| **COLD** | `~/.claude/projects/.../memory/MEMORY-archive.md` | Grep-only | Forever (never deleted) | Historical, completed, retired-but-preserved |
| **TEAM-HOT** | `{TEAM}/memory/*.json` | When team CLAUDE.md auto-loads | Team-lifecycle | Team-specific config — brand_voice, output_paths, llar_memory |
| **TEAM-STATE** | `{TEAM}/memory/active_workflows/*.json` | Loaded by specific workflow agent | Workflow-lifecycle (ephemeral) | Current work-in-progress state — RFP-in-progress, campaign-in-flight |

### Governance-level artifacts (not memory per se, but related)

These live in the repo (not user-memory) and document the system itself rather than personal context:

| Artifact | Location | Lifetime | Use case |
|---|---|---|---|
| **ADR** (Architecture Decision Record) | `docs/adr/ADR-NNNN-kebab-case.md` | Immutable once accepted | Captures one non-obvious architectural decision. Pattern enforced by `output_routing_gate.ps1`. Index at `docs/adr/README.md`. |
| **Operator runbook** | `.claude/OPERATOR_CHEATSHEET.md` | Updated as system evolves | Single-page reference for daily operation. Should stay one page — growth signals automation gap. |
| **CHANGELOG** (future) | `CHANGELOG.md` (repo root) | Append-only | Per-release human-readable summary of what changed. |

**Key distinction:** memory captures personal/project context (changes often, lives in user-memory dir). Governance artifacts capture *the system's design* (changes rarely, lives in the repo, version-controlled).

---

## Decision Matrix — Where does X go?

Apply these questions in order. The first YES routes the memory.

### Q1. Is this a current work-in-progress state file?
- YES → **TEAM-STATE** at `{TEAM}/memory/active_workflows/<workflow-name>_state.json`
- Examples: RFP-26-04 response draft state, current PE outreach batch progress

### Q2. Does this only matter inside ONE team's workflow?
- YES → **TEAM-HOT** at `{TEAM}/memory/<purpose>.json`
- Examples: MARKETING brand_voice.json, PROPOSAL output_paths.json, SALES default_recipients.json

### Q3. Is this completed / retired / historical context?
- YES → **COLD** appended to `MEMORY-archive.md`
- Examples: Closed projects, resolved bugs, deprecated frameworks, completed training summaries

### Q4. Is this detailed reference info (>3 lines) that's referenced occasionally but not daily?
- YES → **WARM** as `<topic-kebab>.md` in user memory dir, linked from MEMORY.md with one summary line
- Examples: Full playbook docs, framework deep-dives, runbooks, character/relationship details

### Q5. Default — daily-relevant personal context, ≤2 lines summary?
- → **HOT** in MEMORY.md, with optional link to a WARM detail file

---

## Naming Conventions

### HOT entries (MEMORY.md)
- One H2 heading per topic cluster (e.g., `## PE Outreach Pipeline (2026-04-30)`)
- Date in parentheses = entry creation date (helps weekly review)
- Each bullet: 1–2 lines max
- Link to WARM detail file using `[Title](memory/<topic-kebab>.md)` syntax if depth needed

### WARM files
- Kebab-case filename: `pe-outreach-sequence.md`, `dbac-framework.md`, `relationship-cardology.md`
- YAML frontmatter required:
  ```yaml
  ---
  created: 2026-04-30
  last_updated: 2026-05-12
  status: active        # active | dormant | archive-candidate
  hot_link: true        # true if MEMORY.md links to this
  ---
  ```

### COLD entries (MEMORY-archive.md)
- One H2 heading per archived topic
- Original creation date preserved in heading
- Add archive metadata line: `**Archived:** 2026-05-12 | **Reason:** completed / superseded by X / dormant 90 days`

### TEAM-HOT files
- Snake_case: `brand_voice.json`, `output_paths.json`, `email_config.json`, `linkedin_config.json`
- JSON format preferred for machine-readable configs
- Markdown OK for prose conventions (e.g., `README.md` in each team's memory dir)

### TEAM-STATE files
- Snake_case with `_state` suffix: `rfp_26_04_state.json`, `pe_outreach_batch_state.json`
- Location: `{TEAM}/memory/active_workflows/`
- Delete or move to archive when workflow completes

---

## Agent Behavior Rules

When you (an agent) want to write or update memory, follow this protocol:

### Rule 1 — Classify before writing
Always run the Decision Matrix Q1–Q5 mentally before any memory write. If unclear → propose to the user with your classification and reasoning.

### Rule 2 — HOT writes are PROPOSE-ONLY
Never auto-write to MEMORY.md. It's load-bearing on every future prompt. Always propose the addition as a draft, get explicit user approval, then write.

Format: "I'd add this to MEMORY.md HOT tier under section X: `<proposed bullet>`. Approve?"

### Rule 3 — WARM writes are OK to auto-write, but link from HOT
When creating a new WARM topic file, also propose the 1-line HOT entry that links to it. Without the HOT link, the WARM file is invisible to future sessions.

### Rule 4 — COLD writes are curator-only
Only the user (or a delegated archive script) may write to MEMORY-archive.md. Never auto-archive — that's a deliberate retirement decision.

### Rule 5 — TEAM-HOT writes follow team conventions
Read existing `{TEAM}/memory/*.json` to understand the schema before adding new keys. Don't introduce new top-level config files without proposing first.

### Rule 6 — TEAM-STATE writes are workflow-scoped
Only write to TEAM-STATE during active workflow execution. Clean up when workflow completes (move to archive or delete).

### Rule 7 — Update timestamps on every change
WARM and TEAM-STATE files must update `last_updated` on every modification. This drives the dormancy detection (Rule 8).

### Rule 8 — Demotion happens by age and link-count
Weekly (or via scheduled review):
- HOT entries dormant >30 days → propose demotion to WARM
- WARM files dormant >90 days OR not linked from HOT for >60 days → propose COLD archive
- TEAM-STATE workflows completed >7 days → propose deletion or archive

---

## When to Propose vs. Auto-Write

| Action | Mode |
|---|---|
| Add a new HOT entry to MEMORY.md | **Propose** (user approves) |
| Update an existing HOT entry | **Propose** (user approves) |
| Create a new WARM topic file | **Auto-write** (and propose the HOT link) |
| Update an existing WARM topic file | **Auto-write** (user can review via git diff) |
| Archive to COLD | **Propose** (user approves the retirement decision) |
| Create new TEAM-HOT config | **Propose** (user approves the schema) |
| Update existing TEAM-HOT config values | **Auto-write** (user can review via git diff) |
| Create or update TEAM-STATE during workflow | **Auto-write** (workflow scope is explicit) |
| Delete or move TEAM-STATE after workflow completes | **Propose** (user approves cleanup) |

---

## Topic Taxonomy — what belongs where

### USER-level (cross-team or personal)
- Personal frameworks (DBAC, Core 4, 12 Leverage Points, 7 Guardrails)
- Personal positioning (Dux Machina brand, distribution channels)
- Personal commitments and cadences (LinkedIn streak, YouTube schedule)
- Personal relationships (cardology, natal chart, key people)
- Personal collaboration defaults (feedback rules: be-concise, no-sycophancy, etc.)
- Technical environment fixes that apply to user's machine (Chrome MCP, Ralph Loop, etc.)
- Cross-team strategy and roadmaps (Dux Machina pricing tiers, capstone goals)

### MARKETING_TEAM
- Brand voice, writing style, visual guidelines
- LinkedIn config (cadence, format, post archive)
- Email config (templates, recipients, drip sequences)
- Social media config (platforms, schedules)
- Campaign state (in-flight campaigns, content backlog)

### PROPOSAL_TEAM
- Output paths config (canonical directory structure)
- Proposal framework (scoring matrices, evaluation criteria)
- RFP response state (per-RFP working state)
- Compliance matrices (regulatory requirements per opportunity)

### FINANCIAL_TEAM
- Deal evaluation criteria (PE / M&A frameworks)
- Financial model templates
- Active deal state (DD in-progress, valuations under review)

### ENGINEERING_TEAM
- Tech stack preferences
- Architecture patterns
- Active feature branch state
- Code style conventions

### SALES_TEAM
- Pipeline state (active prospects)
- ICP definitions
- Outreach templates and sequences

### QA_TEAM
- Test conventions and standards
- Test artifact paths
- Active test run state

---

## Implementation Roadmap

### Phase 1 — TODAY (manual adherence)
- Convention documented at `MEMORY_ROUTING.md` (this file)
- Agents and user voluntarily route memory per the convention
- No enforcement hook yet — adherence by discipline

### Phase 2 — 30 days out (audit hook)
- Build a weekly audit script that scans memory dirs and flags:
  - HOT entries past 30-day dormancy
  - WARM files past 90-day dormancy or 60-day no-HOT-link
  - TEAM-STATE files for completed workflows
  - Memory writes that violated the routing convention
- Output: `LOGS/memory-routing-audit-{date}.md` report

### Phase 3 — 60 days out (proposal automation)
- Agent capability: weekly auto-proposal of demotions based on audit
- User approves/rejects in batch
- Closed-loop: audit → propose → user-decides → execute

### Phase 4 — 90 days out (PreToolUse hook)
- Hook fires on Write to memory directories
- Validates: target path matches Decision Matrix classification claimed in commit message / prompt context
- WARN mode first, ENFORCE later (same pattern as output_routing_gate.ps1)

---

## How to use this spec

### For the user
- Reference this file when deciding where to file new memory
- Run the weekly review (when audit hook lands) to keep tiers clean
- Push back on agents that write to MEMORY.md without proposing first

### For agents
- Read this file as part of any task that touches memory
- Default to PROPOSE when in doubt about tier classification
- Never archive without explicit user approval
- Update `last_updated` on every WARM/TEAM file modification

### For new contributors / agents being onboarded
- This is the single source of truth for memory placement decisions
- Memory written outside this convention is technical debt
- Migration path: when discovered, propose moving the memory to its correct tier

---

## Versioning

| Version | Date | Change |
|---|---|---|
| v1 | 2026-05-12 | Initial spec — 5 tiers, decision matrix, propose-vs-write rules, 4-phase implementation roadmap |
