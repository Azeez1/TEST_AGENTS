# ELI5 visual lessons

Create a beginner-friendly HTML lesson with a visible mechanism, a meaningful
interaction when useful, and optional depth. This is an expanded adaptation of
[Anthropic's community ELI5 skill](https://github.com/anthropics/claude-plugins-community/tree/main/eli5).

## Two independently maintained entrypoints

| Runtime | Source | Invocation |
|---|---|---|
| Claude Code | `.claude/skills/eli5/` | `/eli5 <topic>` |
| Codex | `CODEX_TEAM/skills/eli5/` | `$eli5 <topic>` |

Claude Code can discover the project skill in this checkout. To use it globally,
copy the complete folder into your user `.claude/skills/eli5` directory.
For Codex, copy the complete Codex folder into your user `.codex/skills/eli5`
directory. Preserve existing customizations before replacing an installation.
Use the Codex source for Codex rather than replacing it with a generated mirror
of the Claude entrypoint. Restart or refresh skill discovery if needed.

The entrypoints have runtime-specific delivery guidance. Each package contains
the same CSS/JavaScript toolkit, example, builder, tests, and teaching references
so either installation is self-contained. Keep shared resources in sync when
editing them; neither package depends on the other being installed.

## What is included

- Three configurable color palettes and responsive typography/controls.
- Accessible prediction/reveal enhancement with a readable no-script fallback.
- A working cache simulation covering hits, misses, stale copies, and refresh.
- A standard-library Python builder that embeds assets into one HTML file.
- Packaging regression tests and visual/teaching verification guidance.

Build and test from the repository root:

```sh
python CODEX_TEAM/skills/eli5/scripts/test_build.py
python .claude/skills/eli5/scripts/test_build.py
python CODEX_TEAM/skills/eli5/scripts/build.py CODEX_TEAM/skills/eli5/assets/cache-lab.html --output CODEX_TEAM/outputs/eli5/cache-lab.html
```

Open the generated HTML in a browser. Rebuilding an existing output requires
`--force`. The source is never overwritten, even with that flag. The builder
accepts trusted authored lesson HTML containing its two documented asset markers;
it is not an HTML sanitizer.

## Codebase exploration

Use this as an explanation layer over inspected source. Focused prompts work best:

- Trace one request from a UI action to the backend and back.
- Explain how three modules cooperate, citing the real files and functions.
- Show a bug's state changes and the condition that triggers it.

The agent should inspect the code first, distinguish observed behavior from
inference, and retain navigable source references. A simplified diagram does not
replace an exhaustive architecture review, dependency audit, or execution test.
The bundled example is about caching; it should not dictate every lesson's
subject, aesthetic, or interaction pattern.

## Verification scope

Both packages pass skill schema checks and five builder tests each. The built
example was exercised in a browser for hits/misses, stale data, refresh, bypass,
prediction feedback, reset during animation, expanded details, and keyboard
focus. Desktop, 390px, and 320px layouts were inspected; mobile page overflow
checks passed and no console errors or warnings were observed.

Reduced-motion and no-JavaScript fallbacks are implemented but were not separately
exercised in that browser session. These checks establish the bundled example's
behavior, not the quality of every future generated lesson.
