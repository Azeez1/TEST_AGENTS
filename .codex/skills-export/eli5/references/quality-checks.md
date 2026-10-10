# Quality checks

The pass condition is a correct explanation with an artifact the user can use.

For codebase lessons, run `scripts/source_evidence.py --root <repo> --verify
<evidence.json>` before delivery. Confirm major diagram edges map to inspected
call sites, inferences are labeled, the scope is stated, and inline evidence
links work without absolute machine paths. Test the helper itself with
`python scripts/test_source_evidence.py` when changing it.

When changing the builder or bundled assets, run `python scripts/test_build.py`
from the skill directory. These checks cover packaging and overwrite behavior;
they do not replace the browser and teaching checks below.

Teaching: Can a newcomer answer the central question after one pass? Does the
diagram show the mechanism instead of only naming its components? Are the
analogy's limits, illustrative quantities, and any uncertainty clear?
Remove decorative work that competes with the explanation.

Behavior: Exercise every visible control, endpoints, repeat clicks, and reset.
Verify the displayed result against the modeled state. A reveal must explain
why, not just say correct. Ensure progress does not erase another active control.

Layout: Inspect a desktop viewport and a 390px-wide viewport, plus 320px if
there are dense controls. No horizontal page overflow, clipped labels,
overlapping controls, or unreadable SVG text. Check long labels and open details.
Inspect the actual rendered image; DOM checks alone cannot establish visual quality.

Accessibility: Use the keyboard through the lesson with visible focus.
Name controls and meaningful SVGs. Communicate states through text as well as
color. Honor prefers-reduced-motion. Content must remain understandable if
scripts are disabled, even if the simulation cannot run. Print should show the
explanation rather than leave a blank stage.

Portability: Open the built HTML offline. Inspect console errors and network
requests; the lesson should not fetch assets. Check source links separately
from self-contained runtime dependencies. No unresolved build markers.

Handoff: State what was actually exercised. Never substitute a linter, fixture
test, file existence check, or self-awarded score for a browser preview.
If browser tools are unavailable, describe the unverified portions precisely.

Future regression prompts (use when altering teaching behavior):
1. Explain caching; show the stale-data tradeoff.
2. Compare merge and rebase using a tiny, explicitly illustrative history.
3. Explain photosynthesis to a ten-year-old without implying plants eat soil.
4. Explain a supplied function without inventing behavior absent from the code.
5. Explain one concept in text only; respect the format and create no HTML.
