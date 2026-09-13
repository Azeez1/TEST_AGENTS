---
name: eli5
description: Create beautiful visual HTML lessons with simple explanations and meaningful interactive diagrams. Use for $eli5, explain-like-I-am-five requests, or beginner-friendly visual explanations of concepts, code, and systems.
---

# ELI5 — a small museum of one idea

Make the reader understand something they could not explain a minute ago.
Default to an illustrated, interactive HTML lesson: big visuals, few words,
one memorable insight. Treat the reader as an intelligent newcomer.

## Plan the insight before the page

Resolve the topic and audience from the conversation. Ask only when the topic
is missing. Read referenced source/code fully enough to explain it accurately;
verify uncertain or changing facts. Do not invent benchmarks or call a diagram
an execution trace unless you actually ran the code.

Privately choose: the central question, one useful analogy, the likely
misconception, and the observable change that would make the answer click.
Translate the analogy back to the real terms. State where the analogy breaks.
Adapt the scope: a single concept may need one scene; a broad system may need
several. Respect requests for text-only, a specific format, or a literal age.

## Art-direct the explanation

Read [visual direction](references/visual-direction.md) when making HTML.
Choose a visual metaphor and palette that belong to the subject. Make a
bespoke explanatory scene the focal point. Avoid treating a row of text cards
as a visual explanation. Delight should come from seeing the mechanism work.

Use [interaction patterns](references/interaction-patterns.md) to choose a
meaningful control: step a process, compare alternatives, or change an input.
Offer a prediction and reveal when there is a real misconception to test.
Do not add a quiz, animation, or dashboard just to satisfy a template.
Use calm static diagrams when interaction would add no understanding.

A useful story rhythm is: a concrete question → visible mechanism → the
surprising consequence → one takeaway. Optional depth belongs in <details>.
Aim for one or two short sentences per scene, not arbitrary word-count padding.
Introduce jargon after the reader has seen what it means.

## Build with the bundled materials

- `assets/lesson.css`: reusable typography, controls, responsive layout, and
  paper/ink/garden theme tokens. Change these to suit the topic.
- `assets/lesson.js`: accessible prediction/reveal enhancement. It uses
  native buttons and leaves the answer readable without JavaScript.
- `assets/cache-lab.html`: a working causal simulation and visual quality
  reference. Read it only for stateful demos or examples; do not copy its
  caching content, palette, or layout into every lesson.
- `scripts/build.py`: embeds the CSS/JS markers in a trusted authored HTML
  source to produce one portable file. No package installation is needed.

Example (resolve paths relative to this skill directory):
`python scripts/build.py assets/cache-lab.html --output <output>/cache-lab.html`
For a custom lesson, author its own HTML using `<!-- ELI5:STYLE -->` in
the head and `<!-- ELI5:SCRIPT -->` before its custom script. Both markers
are required by the builder. Standalone hand-authored HTML is also fine.
The builder refuses overwrites unless `--force` is explicitly supplied.

Inline CSS/SVG/JavaScript; no remote fonts, CDNs, tracking, or dependencies.
Use real labels, visible focus, large touch targets, non-color-only state,
and reduced-motion support. Prefer native details/range/button controls.
Escape user text; never insert untrusted content with innerHTML.
Label illustrative numbers and animation timing as such.

## Test the idea and the artifact

Read [quality checks](references/quality-checks.md) before delivery.
Preview desktop and narrow mobile layouts. Test every control, keyboard
navigation, reset, and at least one boundary or counterexample. Check the
console and ensure results match the mechanism. A successful build or valid
skill header is not a rendered UI test. Fix observed defects before handoff;
report any test you could not perform.

## Codex delivery

Take the topic from the message; do not rely on Claude's $ARGUMENTS variable.
Save to the requested or appropriate workspace outputs directory. Open the
artifact in the Codex file/browser panel when available and return an absolute
clickable file link. Keep the chat handoff brief; the artifact carries the lesson.

Independent Codex adaptation of:
https://github.com/anthropics/claude-plugins-community/tree/main/eli5
