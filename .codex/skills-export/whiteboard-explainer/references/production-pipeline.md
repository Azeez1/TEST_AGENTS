# Production pipeline

## Ownership

| Layer | Owner | Responsibility |
|---|---|---|
| Research and claims | Codex + source workflow | Evidence, angle, audience, promise |
| Script | Codex + user approval | Hook, beats, payoff, CTA |
| Narration | ElevenLabs | Approved voice performance |
| Keyframes | Image workflow or supplied art | Exact start/end diagrams and continuity anchors |
| Scene motion | SeedDance 2 | Hand motion, marker movement, camera texture, visual transformations |
| Assembly | HyperFrames | Exact timing, captions, labels, logos, transitions, audio mix, export |
| QA | HyperFrames checks + video-intelligence | Technical and frame-aware review |

SeedDance is the primary visual generator. HyperFrames is not a substitute generator; it is the deterministic production and finishing layer.

## Canonical project layout

```text
MARKETING_TEAM/outputs/videos/whiteboard-explainer/<project-slug>/
├── manifest.json
├── brief/
│   ├── brief.json
│   └── source.txt
├── script/
│   └── SCRIPT.md
├── storyboard/
│   ├── STORYBOARD.md
│   └── storyboard.json
├── audio/
│   ├── elevenlabs-request.json
│   ├── narration.json
│   ├── narration.mp3
│   └── sfx/
├── keyframes/
├── seedance/
│   ├── cost-plan.json
│   ├── requests/
│   └── clips/
├── composition/
│   ├── index.html
│   ├── timeline.json
│   ├── public/
│   └── frames/
├── renders/
├── qa/
│   └── video-intelligence/
└── logs/
```

All generated artifacts remain under one ignored project directory. Reusable workflow logic belongs in the global skill, not in MARKETING_TEAM.

## Status progression

`initialized → script-approved → storyboard-approved → cost-approved → generating → preview-ready → preview-approved → rendered → qa-passed`

Update `manifest.json` after each gate. A provider failure returns the project to `generating`; it does not erase approved work or overwrite a good take.

