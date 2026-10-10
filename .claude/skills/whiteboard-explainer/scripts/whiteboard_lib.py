"""Shared project schema and path helpers for the whiteboard explainer skill."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ALLOWED_ASPECT_RATIOS = {"16:9", "9:16", "1:1", "4:3", "3:4", "21:9"}
ALLOWED_MODES = {"text_to_video", "first_last_frames", "omni_reference"}
ALLOWED_RESOLUTIONS = {"480p", "720p", "1080p"}
ALLOWED_TASK_TYPES = {
    "seedance-2",
    "seedance-2-fast",
    "seedance-2-mini",
    "seedance-2-less-restriction",
    "seedance-2-fast-less-restriction",
    "seedance-2-mini-less-restriction",
}


def slugify(value: str) -> str:
    """Return a safe lowercase project slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Project name must contain at least one letter or number.")
    return slug[:80]


def find_repo_root(start: Path) -> Path:
    """Find the nearest TEST_AGENTS-style repository root."""
    candidates = [start.resolve(), *start.resolve().parents]
    for candidate in candidates:
        if (candidate / "AGENTS.md").is_file() and (candidate / "MARKETING_TEAM").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not find a repository containing AGENTS.md and MARKETING_TEAM. "
        "Pass --repo-root explicitly."
    )


def project_output_root(repo_root: Path) -> Path:
    """Return the single canonical output root for this skill."""
    return repo_root / "MARKETING_TEAM" / "outputs" / "videos" / "whiteboard-explainer"


def load_storyboard(project_path: Path) -> dict[str, Any]:
    """Read the project's canonical storyboard JSON."""
    path = project_path / "storyboard" / "storyboard.json"
    if not path.is_file():
        raise FileNotFoundError(f"Storyboard not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    """Write stable, human-readable JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_storyboard(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return schema errors and non-blocking warnings."""
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    project = data.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
        project = {}

    title = project.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("project.title is required")

    aspect_ratio = project.get("aspect_ratio")
    if aspect_ratio not in ALLOWED_ASPECT_RATIOS:
        errors.append(f"project.aspect_ratio must be one of {sorted(ALLOWED_ASPECT_RATIOS)}")

    fps = project.get("fps")
    if not isinstance(fps, int) or fps < 12 or fps > 60:
        errors.append("project.fps must be an integer from 12 to 60")

    providers = data.get("providers")
    if not isinstance(providers, dict):
        errors.append("providers must be an object")
        providers = {}

    seedance = providers.get("seedance", {})
    if seedance.get("task_type") not in ALLOWED_TASK_TYPES:
        errors.append(f"providers.seedance.task_type must be one of {sorted(ALLOWED_TASK_TYPES)}")
    if seedance.get("resolution") not in ALLOWED_RESOLUTIONS:
        errors.append(f"providers.seedance.resolution must be one of {sorted(ALLOWED_RESOLUTIONS)}")
    if seedance.get("resolution") == "1080p" and seedance.get("task_type") not in {
        "seedance-2",
        "seedance-2-less-restriction",
    }:
        errors.append("1080p requires seedance-2 or seedance-2-less-restriction")

    elevenlabs = providers.get("elevenlabs", {})
    if not elevenlabs.get("model_id"):
        errors.append("providers.elevenlabs.model_id is required")
    if not (elevenlabs.get("voice_id") or elevenlabs.get("voice_name")):
        warnings.append("Choose an ElevenLabs voice_id or voice_name before narration generation")

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a non-empty array")
        return errors, warnings

    ids: set[str] = set()
    orders: set[int] = set()
    total_duration = 0
    for index, scene in enumerate(scenes, start=1):
        prefix = f"scenes[{index - 1}]"
        if not isinstance(scene, dict):
            errors.append(f"{prefix} must be an object")
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not re.fullmatch(r"scene-\d{3}", scene_id):
            errors.append(f"{prefix}.id must look like scene-001")
        elif scene_id in ids:
            errors.append(f"duplicate scene id: {scene_id}")
        else:
            ids.add(scene_id)

        order = scene.get("order")
        if not isinstance(order, int) or order < 1:
            errors.append(f"{prefix}.order must be a positive integer")
        elif order in orders:
            errors.append(f"duplicate scene order: {order}")
        else:
            orders.add(order)

        duration = scene.get("duration_seconds")
        if not isinstance(duration, int) or duration < 4 or duration > 15:
            errors.append(f"{prefix}.duration_seconds must be an integer from 4 to 15")
        else:
            total_duration += duration

        for field in ("narration", "visual_goal"):
            value = scene.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field} is required")

        scene_seedance = scene.get("seedance")
        if not isinstance(scene_seedance, dict):
            errors.append(f"{prefix}.seedance must be an object")
            continue
        mode = scene_seedance.get("mode")
        if mode not in ALLOWED_MODES:
            errors.append(f"{prefix}.seedance.mode must be one of {sorted(ALLOWED_MODES)}")
        prompt = scene_seedance.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{prefix}.seedance.prompt is required")
        elif _asks_model_to_render_copy(prompt):
            errors.append(
                f"{prefix}.seedance.prompt asks the video model to render readable copy; "
                "move that copy to overlay"
            )

        image_urls = scene_seedance.get("image_urls", [])
        reference_paths = scene_seedance.get("reference_image_paths", [])
        video_urls = scene_seedance.get("video_urls", [])
        audio_urls = scene_seedance.get("audio_urls", [])
        for field_name, value in (
            ("image_urls", image_urls),
            ("reference_image_paths", reference_paths),
            ("video_urls", video_urls),
            ("audio_urls", audio_urls),
        ):
            if not isinstance(value, list):
                errors.append(f"{prefix}.seedance.{field_name} must be an array")

        if mode == "first_last_frames" and not image_urls and not reference_paths:
            errors.append(f"{prefix}.seedance first_last_frames requires image URLs or reference image paths")
        if mode == "text_to_video" and any((image_urls, reference_paths, video_urls, audio_urls)):
            errors.append(f"{prefix}.seedance text_to_video cannot include references")

        overlay = scene.get("overlay", {})
        if not isinstance(overlay, dict):
            errors.append(f"{prefix}.overlay must be an object")
        else:
            headline = overlay.get("headline", "")
            caption = overlay.get("caption", "")
            if len(headline) > 80:
                warnings.append(f"{prefix}.overlay.headline exceeds 80 characters")
            if len(caption) > 180:
                warnings.append(f"{prefix}.overlay.caption exceeds 180 characters")

    expected_orders = set(range(1, len(scenes) + 1))
    if orders and orders != expected_orders:
        errors.append("scene orders must be contiguous starting at 1")

    target = project.get("target_duration_seconds")
    if isinstance(target, int) and abs(target - total_duration) > 3:
        warnings.append(
            f"Storyboard totals {total_duration}s but target_duration_seconds is {target}s"
        )

    return errors, warnings


def _asks_model_to_render_copy(prompt: str) -> bool:
    normalized = " ".join(prompt.lower().split())
    patterns = (
        r"\btext\s+(?:reads|reading|says)\b",
        r"\bwrite\s+(?:the\s+)?(?:word|words|text|label|caption|title)\b",
        r"\bspell\s+(?:the\s+)?(?:word|words|text|label|caption|title)\b",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)

