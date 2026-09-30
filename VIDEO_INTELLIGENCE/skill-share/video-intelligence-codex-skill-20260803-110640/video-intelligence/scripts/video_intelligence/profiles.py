"""Analysis profile definitions and prompt construction."""

from __future__ import annotations

from pathlib import Path


PROFILE_INSTRUCTIONS: dict[str, str] = {
    "general": (
        "Create a balanced multimodal analysis: concise summary, semantic chapters, "
        "important visual/audio/dialogue events, notable on-screen text, claims, and uncertainties."
    ),
    "timeline": (
        "Reconstruct the chronology densely. Prioritize scene changes, actions, state changes, "
        "causal order, and precise timestamps over thematic prose."
    ),
    "transcript": (
        "Prioritize dialogue segments with timestamps and visual context. Use generic speaker labels "
        "unless identity is established by the source. Record transcript provenance as model_audio_interpretation."
    ),
    "tutorial-sop": (
        "Extract an executable SOP: prerequisites, inputs, tools, ordered steps, decisions, exceptions, "
        "checks, outputs, and failure recovery. Anchor each step to evidence."
    ),
    "meeting-interview": (
        "Extract speakers as source-supported labels, topics, questions, answers, decisions, disagreements, "
        "commitments, owners, and action items. Do not infer identity from appearance."
    ),
    "education": (
        "Extract concepts, definitions, explanations, examples, misconceptions, dependencies, and useful "
        "knowledge-check questions. Distinguish what is taught from what is visually demonstrated."
    ),
    "product-demo": (
        "Analyze features, user flow, UI states, claimed value, friction, missing steps, proof, and unresolved "
        "questions. Do not treat marketing claims as verified facts."
    ),
    "software-qa": (
        "Reconstruct user actions, application state, expected versus observed behavior, errors, reproduction "
        "steps, severity evidence, and uncertain transitions."
    ),
    "creative-marketing": (
        "Analyze hook, target audience, problem, angle, visual language, pacing, pattern interrupts, proof, "
        "offer, CTA, and risks. Never infer actual conversions or profitability from the creative alone."
    ),
    "compliance-review": (
        "Inventory spoken and displayed claims, disclosures, omissions, risky wording or visuals, and evidence. "
        "Flag uncertainty and require qualified human review; do not give legal advice."
    ),
    "comparison": (
        "Apply a shared evidence structure across sources. Identify repeated patterns, material differences, "
        "strengths, limitations, and source-specific evidence."
    ),
    "custom": "Apply the supplied custom rubric while preserving all canonical evidence and quality fields.",
}


def available_profiles() -> tuple[str, ...]:
    """Return valid profile names."""

    return tuple(PROFILE_INSTRUCTIONS)


def load_rubric(path: str | None) -> str:
    """Load an optional rubric without interpreting its format."""

    if not path:
        return ""
    rubric_path = Path(path).expanduser().resolve()
    if not rubric_path.is_file():
        raise FileNotFoundError(f"Rubric file not found: {rubric_path}")
    return rubric_path.read_text(encoding="utf-8")


def build_prompt(
    *,
    profile: str,
    question: str,
    source_label: str,
    duration_seconds: float = 0.0,
    caption_timeline: str = "",
    rubric: str = "",
) -> str:
    """Build the canonical analysis prompt."""

    if profile not in PROFILE_INSTRUCTIONS:
        raise ValueError(f"Unknown profile: {profile}")
    user_goal = question.strip() or "Understand the important content and evidence in this video."
    rubric_block = f"\nCUSTOM RUBRIC:\n{rubric.strip()}\n" if rubric.strip() else ""
    duration_rule = (
        f"SOURCE DURATION: {duration_seconds:.3f} seconds. Every timestamp MUST be between 0 and "
        f"{duration_seconds:.3f}; never infer a longer runtime."
        if duration_seconds > 0
        else "SOURCE DURATION: unavailable; do not invent a runtime."
    )
    caption_block = (
        "\nAUTHORITATIVE CAPTION TIMELINE:\n"
        "Use these caption timestamps as the source clock for chapters, dialogue, claims, and section boundaries. "
        "Caption wording may contain recognition errors, but its clock overrides any model-estimated clock.\n"
        f"{caption_timeline.strip()}\n"
        if caption_timeline.strip()
        else ""
    )
    return f"""
Analyze the supplied video as multimodal evidence, not merely as a transcript.

SOURCE LABEL: {source_label}
{duration_rule}
PROFILE: {profile}
USER GOAL: {user_goal}

PROFILE INSTRUCTIONS:
{PROFILE_INSTRUCTIONS[profile]}
{rubric_block}
{caption_block}
EVIDENCE RULES:
- Inspect both visual frames and audio.
- Give start_seconds and end_seconds for material events and claims.
- Treat SOURCE DURATION as a hard boundary for chapters, events, dialogue, text, and claims.
- Separate visual, audio, dialogue, on-screen text, metadata, and inference evidence.
- Do not identify unknown people or infer sensitive traits.
- Use confidence from 0 to 1 and state limitations explicitly.
- Request a high-detail pass only for a specific segment where rapid cuts, fleeting text, or ambiguity matters.
- Do not fabricate details that are not perceptible.
- Populate every required JSON field. Use empty arrays rather than omitting fields.
- Keep profile_analysis structured as findings with evidence IDs.
- Be concise: avoid repeating the same observation across fields and use short descriptions.
""".strip()
