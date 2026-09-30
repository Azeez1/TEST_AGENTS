# Provider-Neutral Output Contract

`analysis.json` is the stable contract. Provider adapters must populate the
same fields so downstream workflows do not depend on Gemini-specific objects.

## Top-level fields

- `schema_version`: contract version.
- `profile`: selected profile.
- `source`: source label and kind.
- `summary`: concise multimodal synthesis.
- `chapters`: timestamped semantic sections.
- `events`: timestamped visual, audio, dialogue, text, or transition events.
- `transcript_segments`: dialogue excerpts with speaker and provenance.
- `on_screen_text`: timestamped OCR-like observations.
- `entities`: people-as-labeled, products, interfaces, locations, and objects.
- `claims`: spoken or displayed claims with evidence and verification status.
- `profile_analysis`: profile-specific structured findings.
- `quality`: confidence, limitations, and high-detail escalation requests.
- `high_detail_findings`: results of bounded targeted re-analysis.
- `open_questions`: questions the evidence cannot answer.

## Evidence rules

Every event or claim must include `start_seconds`, `end_seconds`, an evidence
type, and confidence from 0 to 1. Use `null` only where the schema permits it.
Material conclusions should cite at least one event or claim ID.

Transcript provenance values:

- `manual_caption`
- `embedded_subtitle`
- `platform_auto_caption`
- `model_audio_interpretation`
- `speech_to_text`
- `unknown`

Evidence types:

- `visual`
- `audio`
- `dialogue`
- `on_screen_text`
- `metadata`
- `inference`

## Quality and escalation

Set `requires_high_detail_pass=true` only when a targeted pass could resolve a
specific uncertainty. Supply no more than five segments, each with start/end
seconds and a reason. Do not request a second pass merely to improve prose.

The executable schema lives in `scripts/video_intelligence/schema.py` and is
the source of truth for validation.
