# Scene schema

`storyboard/storyboard.json` is the source of truth. Schema version 1 has four top-level keys: `schema_version`, `project`, `providers`, and `scenes`.

## Project

- `slug`, `title`
- `aspect_ratio`: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, or `21:9`
- `width`, `height`, `fps`
- `target_duration_seconds`

## Providers

`providers.seedance` sets `task_type`, `resolution`, and `stability_mode`. The normal default is `seedance-2-fast-less-restriction` at `720p`; move to the pro tier only when a scene genuinely needs it.

`providers.elevenlabs` sets `model_id`, `voice_id` or `voice_name`, `output_format`, and `speed`. A voice warning is allowed during planning but must be resolved before the narration call.

## Scene

Every scene contains:

- `id`: stable `scene-###`
- `order`: contiguous integer starting at 1
- `duration_seconds`: SeedDance-compatible integer from 4 through 15
- `narration`: locked spoken copy for the scene
- `visual_goal`: what the viewer should understand by the final frame
- `transition`: editorial intent such as `cut`, `match-cut`, or `continuation`
- `seedance`: motion-generation specification
- `overlay`: deterministic copy and styling rendered by HyperFrames

## SeedDance block

- `mode`: `text_to_video`, `first_last_frames`, or `omni_reference`
- `prompt`: physical action, composition, style, camera, consistency, and explicit exclusions
- `image_urls`, `video_urls`, `audio_urls`: provider-ready references
- `reference_image_paths`: local keyframes that still need upload

`text_to_video` has no references. `first_last_frames` requires one or two image URLs or local reference paths. `omni_reference` requires at least one uploaded reference before execution.

## Overlay block

- `headline`: short hook or section marker, ideally under 80 characters
- `caption`: spoken caption or supporting point, ideally under 180 characters
- `labels`: optional structured labels for deterministic placement
- `accent_color`: valid CSS color

Never move important overlay copy into a SeedDance prompt.

