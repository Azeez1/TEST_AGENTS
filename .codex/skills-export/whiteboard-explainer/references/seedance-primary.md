# SeedDance primary scene workflow

Use the repository's existing `MARKETING_TEAM/tools/mcp_server.py` tool named `generate_seedance_video`. It is the primary scene generator for this skill.

## Mode selection

- `first_last_frames`: default for whiteboard scenes. It anchors the blank or partial starting board and the exact completed diagram.
- `omni_reference`: use when the same hand, marker, person, object, product, or art direction must persist across scenes.
- `text_to_video`: use for expendable transitions, texture, or shots without continuity requirements.

Create or source start/end keyframes before generating expensive scenes. For a sequence, the prior scene's end frame can become the next scene's start frame.

## Prompt anatomy

Describe, in order:

1. camera and surface;
2. hand/marker or moving subject;
3. visible physical action;
4. line-art and accent-color system;
5. final composition and hold;
6. stability requirements;
7. exclusions.

Always exclude visible writing, labels, captions, logos, watermarks, and generated typography. The model may draw symbols, arrows, shapes, and illustrations. HyperFrames adds exact language later.

## Execution contract

1. Run `plan_seedance.py`.
2. Upload local keyframes and replace `image_urls` in the scene specification.
3. Re-run the planner until every request says `ready_for_execution: true`.
4. Reconfirm current provider price and show the user the total.
5. Set approval in `manifest.json`; do not edit `approved_for_execution` in request files as a substitute for user approval.
6. Generate one scene at a time through the existing tool.
7. Save to the request's nested filename so the clip lands inside the project.
8. Inspect the first, midpoint, and final frames before generating the next scene.

Reject and regenerate clips with warped hands, duplicate fingers, accidental writing, unstable diagrams, flicker, camera drift, continuity breaks, or a weak final-frame hold.

