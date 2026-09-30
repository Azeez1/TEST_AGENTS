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
python scripts\export_codex_layer.py --write-local-secrets --write-codex-mcp-config
```

## Portable core validation

Install the locked environment outside the synced repository:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA/TEST_AGENTS/core-venv"
uv sync --locked --group voice-tests
uv run --no-sync python tools/project_health.py --tests
```

On Linux/macOS, use `UV_PROJECT_ENVIRONMENT="$HOME/.cache/test-agents/core-venv"`.
The `voice-tests` group enables the voice regression suites; without it those
suites skip explicitly. Live connectors and account credentials are not needed.
The lock targets Python 3.11+; CI exercises Python 3.12 on Windows and Linux.

`config/workspaces.json` owns team paths and access policy. Team `config/`
contains portable output defaults; private `memory/` stays local. Integrations
in `config/integrations.json` are declarations, not a live capability inventory.

```powershell
python scripts/export_codex_layer.py --agents-only
python scripts/export_codex_layer.py --agents-only --check
python tools/project_health.py
```

The full exporter stages agents and skill assets, validates, and publishes with
rollback on ordinary publication errors. An exclusive export lock prevents two
exporters from publishing concurrently. This is not an atomic multi-file
snapshot for readers or a guarantee against power loss. `--check` never
publishes. `--agents-only` updates routing and generated workflow instructions.
Native hooks, local secrets, MCP settings and globally installed skills are
preserved unless their corresponding explicit flags are supplied. Hook mirroring
requires `--sync-hooks`; global skill replacement requires `--install-global-skills`.
An unavailable cloud source asset aborts a full export rather than publishing a
partial skill. Hydrate the source asset or use `--agents-only`.

Both runtime source definitions remain available. Generated agent headers use
`codex_model: inherit`; the shared runtime contract replaces the known repeated
workspace section only in generated mirrors. Domain procedures remain in the
canonical source and generated role. Long domain prompts still need outcome-based
review before further trimming.

## Workflow pilots and task records

`CODEX_TEAM/config/workflows.json` defines one owner for 12 workflows. Email,
QA-suite and FP&A are consolidation pilots; related specialist roles remain
available. `python tools/evaluate_workflows.py` runs 15 deterministic contract
cases, including missing capability and unauthorized send cases. These are not
LLM quality or cost benchmarks. For model comparisons, run the same sanitized
real task through each workflow and record correctness, evidence, unwanted
actions, handoffs, elapsed time and cost before retiring an alias.

`python tools/task_record.py record input.json` saves an explicit task record
outside OneDrive. Fields: objective, team, role, runtime, status, artifacts,
checks (name/status), and next_step for active work. Status `validated` requires
existing artifacts and exclusively passing checks. Checks are caller-reported,
not independently executed by this recorder. `python tools/task_record.py resume
TASK_ID` verifies the saved artifact fingerprints. `TEST_AGENTS_STATE_DIR` can
set another state directory; unknown cost and duration stay null.

## Remaining integration work

`python tools/project_health.py --local` includes the legacy Claude diagnostics.
Their encoding and static Task-declaration findings are not suppressed. Actual
MCP authentication and native hook dispatch need separate runtime verification.
Proposal retrieval is explicitly unavailable until a real adapter is connected;
demo documents cannot establish compliance. QA templates are scaffolds and skip
until a developer supplies meaningful inputs and assertions.
