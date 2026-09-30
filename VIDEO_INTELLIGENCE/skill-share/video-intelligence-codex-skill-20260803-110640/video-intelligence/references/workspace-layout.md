# Workspace Layout

When the active repository contains `VIDEO_INTELLIGENCE/workspace.json`, use it
as the canonical workspace for this skill:

- Place user-supplied local videos in `VIDEO_INTELLIGENCE/inbox/` only when the
  user asks Codex to copy or organize them.
- Write real analysis runs to `VIDEO_INTELLIGENCE/outputs/analyses/`.
- Write generated fixtures and smoke tests to `VIDEO_INTELLIGENCE/outputs/tests/`.
- Load reusable custom rubrics from `VIDEO_INTELLIGENCE/rubrics/`.
- Put only reviewed, intentionally curated artifacts in
  `VIDEO_INTELLIGENCE/examples/`.

Treat `inbox/` and `outputs/` as local runtime data. Do not stage or publish
them. If the workspace file is absent, use the owning team's approved output
folder instead.
