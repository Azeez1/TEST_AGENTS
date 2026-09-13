# Install ELI5

This package contains separate Claude and Codex skills, all local visual assets,
and standard-library Python helpers. No API keys or private code are included.

## Install

Use Python 3.10+ in your chosen environment. From the root
of this checkout or extracted ELI5 bundle:

```sh
python CODEX_TEAM/skills/install_eli5.py --runtime both
```

Use `--runtime claude` or `--runtime codex` to install only one.
The installer copies to the current user's `.claude/skills/eli5` and
`.codex/skills/eli5`. It makes no network calls and refuses to replace an
existing installation. If you configured a nonstandard Codex home, copy the
Codex folder to that installation's skills directory manually instead.

Without Python, manually copy the complete source folders:

| Source in bundle | Destination under your home folder |
|---|---|
| `.claude/skills/eli5` | `.claude/skills/eli5` |
| `CODEX_TEAM/skills/eli5` | `.codex/skills/eli5` |

The instructions and assets work without Python; only the optional builder and
source-evidence helpers require it. Restart or refresh your AI client's skill
discovery after installing.

## Use it inside the repository you want to understand

Claude: `/eli5 Trace login from the UI action to the database. Cite the real files.`

Codex: `$eli5 Give me an orientation to this repo, then trace one representative request. Separate observed code from inferences and unknowns.`

Useful follow-ups:
- Show me exactly where this decision happens.
- What changes if this request fails?
- Explain this at the level of a backend developer new to this framework.
- Which three functions should I read next, and why?
- Use text only; no HTML for this answer.

Evidence is based on the files actually inspected. Use a focused subsystem for
deep traces; a broad initial map is explicitly partial.

## Source privacy

The helpers operate locally and the generated HTML needs no remote assets.
The skill does not browse/search using private code or publish it by default.
This does not make the Claude/Codex model itself offline: source text read by
the agent may enter its provider's context under the selected client's privacy
settings and applicable data policies. Use a client/account permitted for that
source. Keep generated HTML and evidence JSON local unless sharing is authorized;
they can contain confidential code snippets.
