# MARKETING_TEAM — Audit v3 (verified + grounded)

**Date:** 2026-05-12
**Status:** v3 — supersedes v1 (inferred) and v2 (theoretical fixes). Now grounded in actual file inventory + empirical verification.

This audit is **shorter than v1/v2 on purpose.** Most of v1/v2's "problems" turned out to be misreads of an intentional architecture. v3 lists only what's genuinely actionable.

---

## What's actually working (don't touch)

- **All 18 agents are active, production-ready, well-structured.** No drafts, no `*_v1.md`, no abandoned variants. Clean.
- **MCP-first architecture is intentional.** Specialists work via Google Workspace, marketing-tools, perplexity, bright-data MCPs — not local file I/O. Tools lists are correctly scoped to MCP capabilities. Earlier "broken tools" framing was wrong.
- **Workspace-scoped agent discovery works as designed** (cd into team folder, then invoke).
- **Memory configs (`brand_voice.json`, `visual_guidelines.json`, `email_config.json`, `google_drive_config.json`, `output_paths.json`) are critical, current, well-maintained.**
- **Documentation structure is well-organized** (24 files across getting-started/, guides/, architecture/, reference/) with maintained READMEs.
- **`templates/` directory is well-curated** with 6 reusable templates + README.
- **Security:** `credentials.json` and `.env` are properly gitignored. Not tracked.

---

## What's genuinely broken (3 items)

### B1. `editor` agent has Write tools while framed as a reviewer
- Tools include `mcp__google-workspace__modify_doc_text` and `create_doc`
- Prompt frames the agent as review/QA only
- Same agent can modify the content it's reviewing → biased loop
- **Fix:** split into `content-reviewer` (Read-only) and `content-editor` (Write-capable for explicit edit passes), OR drop the modify tools from current editor

### B2. Only `router-agent` has `Task` in its tools list (1 of 18)
- `content-strategist` uses `Task(...)` syntax extensively in its prompt but lacks the tool grant — same gap pattern fixed on router-agent today
- **Fix:** add `Task` to `content-strategist.md` tools

### B3. Only `/comment-leads` (1 of 14) MARKETING slash commands has Step 0 / plan-first
- The other 13 execute-blind: brand-check, comment-engine, competitor-intel, content-suite, launch-campaign, lead-gen-blast, lead-gen-cleaning, lead-gen-fractional, lead-gen-leasing, product-launch, seo-audit, social-boost, video-campaign
- **Fix:** port `/comment-leads` Step 0 template to the others (mechanical)

---

## What's stale or wasteful (cleanup, not architecture)

### C1. `outputs/presentations/node_modules/` — 500+ MB of npm packages
- Build artifact bloat. Already in `.gitignore` (good), but still on disk.
- **Fix:** delete the directory.

### C2. 9 stale `test_*.py` scripts in tools/ + scripts/
- test_reliability.py, test_openai_connection.py, test_google_workspace_mcp.py, test_perplexity_research.py, test_mcp_tools.py, test_enhanced_tools_simple.py, test_list_mcp_tools.py, test_automatic_analysis.py (+1)
- One-off verification scripts. Real testing should use pytest.
- **Fix:** delete all 9.

### C3. `mcp_server.py.backup`
- Duplicate of `mcp_server.py`. Git already handles version history.
- **Fix:** delete.

### C4. `__pycache__/` directories in tools/
- Auto-regenerated Python bytecode. Already gitignored. Just disk bloat.
- **Fix:** delete.

### C5. `tribev2_calibrator.py` — unknown purpose
- 2 KB script with unclear function.
- **Fix:** review with you before deleting. Could be active utility or orphaned experiment.

### C6. 8 outputs/ subdirectories with 90+ day old work
- blog_posts/, landing_pages/, videos/, campaigns/, research/, social_media/, emails/, images/ — all last touched 2025-03-18
- These are historical campaign deliverables. Not infrastructure.
- **Decision needed from you:** archive elsewhere, delete, or keep as portfolio? *Not a default-delete decision.*

### C7. `llar_memory.json` is empty scaffolding
- 1.2 KB file with all learning arrays empty. Never been written to. Last touched Dec 2025.
- **Fix:** either wire `capture-as-skill` to populate it, or remove if not part of intended flow.

### C8. `email_templates.json` is missing from memory/
- Referenced but not present. Likely superseded by `templates/email_templates/` directory.
- **Fix:** confirm intentional, update any references that point to the old file.

### C9. `docs/reference/` folder is empty
- Documented in folder structure but contains no files.
- **Fix:** either populate (with API references, command listings) or remove.

---

## Verified findings that did NOT survive grounded inspection

Listed for honesty / future reference:

- ❌ "Scope overlap between copywriter / content-strategist / editor" — REFUTED. Clean pipeline: strategist plans, copywriter writes, editor reviews.
- ❌ "Scope overlap between social-media-manager and copywriter" — REFUTED. Clean split by surface (long-form vs platform-native).
- ❌ "Scope overlap between visual-designer / presentation-designer / video-producer" — REFUTED. Clean by file extension.
- ❌ "MARKETING agents have broken tools blocks (no Read/Write)" — REFUTED. MCP-first architecture by design.
- ❌ "Team agents aren't discoverable" — REFUTED. Workspace-scoped discovery is intentional and works when invoked from within team cwd.
- ❌ "llar_memory.json is bloated" — REFUTED. It's empty, not bloated. Different problem entirely.

The systematic error in v1 and v2: I was auditing against a default architecture assumption (single-pool agents, local file I/O) that doesn't match the team's actual design.

---

## Prioritized action list (v3 — only verified items)

### Tier A — Safe automatic cleanup (no risk, execute immediately on approval)
1. Delete `outputs/presentations/node_modules/` (500+ MB reclaim)
2. Delete `__pycache__/` directories in tools/
3. Delete `mcp_server.py.backup`
4. Delete 9 `test_*.py` files (~12 KB but mostly conceptual cleanup)

### Tier B — Verify before removing (one-question-per-item)
5. `tribev2_calibrator.py` — is this active or orphaned?
6. `email_templates.json` — confirm intentional removal?
7. `docs/reference/` — populate or remove?
8. `llar_memory.json` — wire to capture-as-skill or remove?

### Tier C — Your deliverable archive decision (not a default)
9. 8 stale outputs/ subdirectories (90+ day old campaign work) — archive externally / delete / keep as portfolio?

### Tier D — Architecture fixes (real but small)
10. Split `editor` → `content-reviewer` (Read-only) + `content-editor` (Write-capable)
11. Add `Task` to `content-strategist.md` tools list
12. Port Step 0 plan-pattern to 13 remaining MARKETING slash commands

---

## Total impact estimate

If Tier A + Tier D execute (high confidence, low risk):
- ~500 MB disk space reclaimed
- 10+ stale files removed
- Editor L6 violation fixed
- Second orchestrator (content-strategist) unlocked
- Plan-first pattern across all 14 MARKETING commands (vs 1 today)

Tier B + C are decisions only you can make. Surface them, you decide.

---

## How v3 differs from v1/v2

**v1** — produced from a single-pass scan, inferred overlaps from agent names, recommended ~14 fixes most of which were wrong.

**v2** — added a "CRITICAL broken tools" framing that was also wrong (missed the MCP-first design).

**v3** — produced from grounded inventory + verified architectural intent. **12 actionable items, 3-4 of which are real architecture fixes; the rest is cleanup of stale artifacts.**

*The lesson, captured for future audits:* don't infer from defaults; inventory the actual repo state first.
