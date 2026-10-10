# Cost and approval gates

No provider call occurs during initialization, validation, planning, or composition scaffolding.

## Gate 1: script

Show the full spoken script, target duration, and intended platform. Record approval in `manifest.json`.

## Gate 2: storyboard

Show every scene's narration, visual goal, start/end keyframe plan, duration, and overlay copy. Lock scene IDs before generating assets.

## Gate 3: voice

Confirm ElevenLabs voice identity, model, sample, pronunciation, and delivery. Voice cloning requires explicit authorization.

## Gate 4: cost

Run both planners. The SeedDance estimate uses the repository wrapper's pricing snapshot and excludes ElevenLabs, retries, alternate takes, and reference-video surcharges. Reconfirm live pricing at execution time because provider prices can change.

State:

- number of scenes;
- generated seconds;
- model/task type;
- resolution;
- estimated first-pass SeedDance cost;
- expected alternates/retry allowance;
- ElevenLabs usage or current provider quote when available.

## Gate 5: preview

Assemble a low-risk preview before the final render. Obtain approval for pacing, captions, voice, visual continuity, and CTA.

Approval for one gate does not imply approval for later paid calls. If the script or storyboard changes materially, recompute both the voice request and video cost plan.

