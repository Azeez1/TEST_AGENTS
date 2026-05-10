# Phase 3b — Adapters & Utility Selective-Restore Log

**Date:** 2026-05-10
**OLD snapshot:** `INFRASTRUCTURE/paperclip.OLD-2026-05-10/`
**NEW (current):** `INFRASTRUCTURE/paperclip/`

## Headline finding

After exhaustive investigation, **the OLD snapshot contains zero EZ-specific custom logic** in any of the 10 Tier 1/2 files. Searches for unique markers (`dux`, `DuxMachina`, `sabaa`, `azeez`, `// Custom:`, `EZ_*`, custom `CEO_BOOTSTRAP`, custom auth/telemetry) returned **no hits** across all OLD adapter and utility files. The OLD snapshot appears to be a clean earlier upstream version, NOT a customized fork.

All differences fall cleanly into two categories:
1. **Pure refactor** — upstream renamed/consolidated helpers (e.g. `runChildProcess` → `runAdapterExecutionTargetProcess`, individual `env.PAPERCLIP_WORKSPACE_*` setters → `applyPaperclipWorkspaceEnv()`)
2. **Upstream improvements** — new features (skills-dir, prompt-cache, Bedrock support, ACPx adapter, Security agent kind, plugin issue origins, issue threading interactions, stream-handling refactor in backup-lib, remote execution targets, etc.)

Therefore: **no ports were performed.** Upstream is taken wholesale for all 10 files. This matches the user's stated bias of "minimize fork tax."

---

## packages/adapters/claude-local/src/server/execute.ts

**Diff scope**: ~715 diff lines (629 OLD vs 942 NEW). Major upstream rewrite.

**Categorization**:
- Pure refactor: `runChildProcess` → `runAdapterExecutionTargetProcess`; inline env-setter block → `applyPaperclipWorkspaceEnv` helper; `ensureCommandResolvable`/`resolveCommandForLogs` → `ensureAdapterExecutionTargetCommandResolvable`/`resolveAdapterExecutionTargetCommandForLogs`; default agent prompt → `DEFAULT_PAPERCLIP_AGENT_PROMPT_TEMPLATE`; bootstrap session resume retry logic moved into upstream
- Upstream improvement: remote-execution target abstraction; `prepareClaudeConfigSeed`; new transient/upstream-error retry handling (`isClaudeTransientUpstreamError`, `extractClaudeRetryNotBefore`); `readPaperclipIssueWorkModeFromContext` env flag; `shapePaperclipWorkspaceEnvForExecution` for remote cwd rewriting; `terminalResultCleanupGraceMs`; sandbox install command wiring
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapters/codex-local/src/server/execute.ts

**Diff scope**: ~579 diff lines.

**Categorization**:
- Pure refactor: same helper-renaming pattern as claude-local; `bootstrapPromptTemplate` rendering still present (pre-existing upstream feature, not EZ custom)
- Upstream improvement: remote-execution target plumbing; new env shaping helpers
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapters/cursor-local/src/server/execute.ts

**Diff scope**: ~484 diff lines.

**Categorization**:
- Pure refactor: same helper-renaming pattern
- Upstream improvement: same remote-execution target plumbing
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapters/gemini-local/src/server/execute.ts

**Diff scope**: ~445 diff lines.

**Categorization**:
- Pure refactor: same helper-renaming pattern
- Upstream improvement: same remote-execution target plumbing
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapters/opencode-local/src/server/execute.ts

**Diff scope**: ~495 diff lines.

**Categorization**:
- Pure refactor: same helper-renaming pattern
- Upstream improvement: same remote-execution target plumbing
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapters/pi-local/src/server/execute.ts

**Diff scope**: ~666 diff lines.

**Categorization**:
- Pure refactor: same helper-renaming pattern; `canResumeSession` logic preserved by upstream
- Upstream improvement: remote-execution target plumbing; pi-specific session/runtime improvements
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapter-utils/src/server-utils.ts

**Diff scope**: ~1310 diff lines.

**Categorization**:
- Pure refactor: large consolidation — many small helpers merged into broader ones; `applyPaperclipWorkspaceEnv` introduced; `DEFAULT_PAPERCLIP_AGENT_PROMPT_TEMPLATE` added; `shapePaperclipWorkspaceEnvForExecution` and `rewriteWorkspaceCwdEnvVarsForExecution` added for remote-execution support; `refreshPaperclipWorkspaceEnvForExecution` added
- Upstream improvement: `readPaperclipIssueWorkModeFromContext`; `readPaperclipRuntimeSkillEntries` improvements
- EZ custom logic: **none found**

**Note on `renderPaperclipWakePrompt`**: the task hinted this helper might have been lost. Confirmed it is present in upstream `server-utils.ts` AND consumed by all 7 adapter `execute.ts` files (claude/codex/cursor/gemini/opencode/pi/openclaw + acpx + the test file). No restore needed — it was never lost.

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/adapter-utils/src/types.ts

**Diff scope**: ~158 diff lines, **additive only** (no `^-` removal lines). Upstream added new fields/types, removed nothing.

**Categorization**:
- Upstream improvement: new fields on `AdapterExecutionContext` (e.g. `executionTarget`, `runtimeCommandSpec`, etc.) to support remote execution
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/db/src/backup-lib.ts

**Diff scope**: ~617 diff lines.

**Categorization**:
- Pure refactor: stream-handling rewritten (drain/error retry logic replaced with cleaner abstraction); drizzle migration table constants no longer hardcoded inline
- Upstream improvement: improved error propagation and resource cleanup
- EZ custom logic: **none found**

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

## packages/shared/src/constants.ts

**Diff scope**: ~491 diff lines, **additive only** in the regions sampled.

**Categorization**:
- Upstream improvement: new constants (`DEFAULT_COMPANY_ATTACHMENT_MAX_BYTES`, `acpx_local` adapter type, `security` agent kind, `MODEL_PROFILE_KEYS`, `ISSUE_WORK_MODES`, `MAX_ISSUE_REQUEST_DEPTH`, `ISSUE_COMMENT_*`, `ISSUE_THREAD_INTERACTION_*`, expanded `ISSUE_ORIGIN_KINDS` with `harness_liveness_escalation`, `stranded_issue_recovery`, etc., plus plugin origin kind support)
- EZ custom logic: **none found** — `ceo`/`cfo` enum values are pre-existing upstream, NOT EZ customizations (confirmed in OLD also)

**Restored**: nothing
**Dropped (was custom)**: nothing
**Confidence**: HIGH

---

# Global Summary

| Metric | Count |
|---|---|
| Files investigated | 10 / 10 |
| Custom EZ logic restored | **0** |
| Custom EZ logic dropped (experimental) | **0** |
| Files where upstream was taken wholesale | **10 / 10** |

**Files needing manual user review**: NONE — but the user should be aware that this OLD snapshot did not contain a customized fork. If the user has an even older snapshot somewhere with genuine `dux`/`DuxMachina`/`CEO_BOOTSTRAP` customizations, those would need a separate investigation pass.

**Reasoning for zero restores**: every diff was a clean pure-refactor or upstream feature addition. No comments, helpers, env vars, prompt templates, auth flows, telemetry calls, or hardcoded values were unique to OLD. The conservative-bias rule from the task ("when uncertain, drop") therefore reduces to "take upstream" universally.

**Phase 4 build risks**:
1. `claude-local/execute.ts` introduces a new `prompt-cache.ts` module call site (`prepareClaudePromptBundle`). API-key shape unchanged from upstream's perspective (uses `authToken` → `PAPERCLIP_API_KEY`), so no migration needed unless EZ has bespoke key wiring elsewhere.
2. New `executionTarget` field on `AdapterExecutionContext` is required reading in every adapter — if any non-vendored caller (e.g. EZ's CLI / cli/src/) constructs this context manually, it may need updating. Worth a grep for `AdapterExecutionContext` outside `packages/`.
3. `acpx_local` adapter type added to `AGENT_ADAPTER_TYPES` — any DB rows or config files referencing the old narrower union should still parse fine since it's an *additive* widening.
4. `security` agent kind added — same additive widening, safe.
5. `ISSUE_ORIGIN_KINDS` widened with several new variants and `plugin:*` template literal — anything switch-exhaustive on this union will need updating, but that's an upstream-driven change EZ would have hit regardless.

**Compile confidence**: HIGH for all 10 vendored files in isolation (we made zero edits — they are pure upstream). The only build risk is in **non-vendored consumer code** that imports from these packages and may not have been updated to the new API surface (e.g. `runtimeCommandSpec`, `executionTarget`, removed `runChildProcess` export). That is out of scope here but should be checked in Phase 4.

**Open questions for user**:
- Do you have a different/older snapshot that contains the genuine Dux Machina customizations? The 2026-04-25 snapshot under `paperclip.OLD-2026-05-10/` reads as plain upstream.
- If you remember specific custom features (e.g. a custom CEO bootstrap routine, a custom telemetry shim, a custom auth flow) that should have been in these files, name them and I can do a targeted search across the broader tree.

**Log file path**: `C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\INFRASTRUCTURE\paperclip\.backups\phase3b-adapters-log.md`
