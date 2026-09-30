"""Gemini Developer API adapter for provider-neutral video intelligence."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .media import MediaSource
from .schema import ANALYSIS_SCHEMA, HIGH_DETAIL_SCHEMA
from .security import redact


@dataclass
class ProviderResult:
    data: dict[str, Any]
    usage: dict[str, Any]
    interaction_id: str
    cleanup_status: str


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _usage(interaction: Any) -> dict[str, Any]:
    usage = _field(interaction, "usage", {}) or {}
    by_modality = []
    for item in _field(usage, "input_tokens_by_modality", []) or []:
        by_modality.append(
            {
                "modality": str(_field(item, "modality", "unknown")),
                "tokens": int(_field(item, "tokens", 0) or 0),
            }
        )
    return {
        "input_tokens": int(_field(usage, "total_input_tokens", 0) or 0),
        "output_tokens": int(_field(usage, "total_output_tokens", 0) or 0),
        "thought_tokens": int(_field(usage, "total_thought_tokens", 0) or 0),
        "total_tokens": int(_field(usage, "total_tokens", 0) or 0),
        "input_tokens_by_modality": by_modality,
    }


class GeminiProvider:
    """Small adapter around the Gemini Interactions and Files APIs."""

    def __init__(self, api_key: str, *, keep_remote_file: bool = False, poll_timeout: int = 600):
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("Install google-genai>=2,<3 to use Gemini video analysis") from exc
        self.client = genai.Client(api_key=api_key)
        self.keep_remote_file = keep_remote_file
        self.poll_timeout = poll_timeout

    def _upload(self, path: str):
        uploaded = self.client.files.upload(file=path)
        deadline = time.monotonic() + self.poll_timeout
        while True:
            state = _field(_field(uploaded, "state"), "name", "")
            if state == "ACTIVE":
                return uploaded
            if state in {"FAILED", "ERROR", "CANCELLED"}:
                raise RuntimeError(f"Gemini file processing ended in state {state}")
            if time.monotonic() >= deadline:
                raise TimeoutError("Gemini file processing timed out")
            time.sleep(2)
            uploaded = self.client.files.get(name=_field(uploaded, "name"))

    def _call(
        self,
        *,
        source: MediaSource,
        prompt: str,
        model: str,
        schema: dict[str, Any],
        max_output_tokens: int,
        thinking_level: str,
    ) -> ProviderResult:
        uploaded = None
        cleanup = "not_applicable"
        data: dict[str, Any] | None = None
        usage: dict[str, Any] = {}
        interaction_id = ""
        try:
            if source.local_path:
                uploaded = self._upload(source.local_path)
                video = {
                    "type": "video",
                    "uri": _field(uploaded, "uri"),
                    "mime_type": _field(uploaded, "mime_type", source.mime_type),
                }
            elif source.direct_uri:
                video = {"type": "video", "uri": source.direct_uri}
            else:
                raise ValueError("media source has neither a local file nor a direct URI")
            interaction = self.client.interactions.create(
                model=model,
                input=[video, {"type": "text", "text": prompt}],
                response_format={"type": "text", "mime_type": "application/json", "schema": schema},
                store=False,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": max_output_tokens,
                    "thinking_level": thinking_level,
                    "thinking_summaries": "none",
                },
            )
            raw = _field(interaction, "output_text", "")
            if not raw:
                raise RuntimeError("Gemini returned no text output")
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()
            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError as exc:
                status = _field(interaction, "status", "unknown")
                complete_object = cleaned.endswith("}")
                observed_usage = _usage(interaction)
                raise RuntimeError(
                    f"Gemini returned malformed structured JSON (status={status}, "
                    f"characters={len(cleaned)}, output_tokens={observed_usage['output_tokens']}, "
                    f"complete_object={complete_object})"
                ) from exc
            if not isinstance(data, dict):
                raise RuntimeError("Gemini structured output was not a JSON object")
            usage = _usage(interaction)
            interaction_id = str(_field(interaction, "id", ""))
        except Exception as exc:
            raise RuntimeError(redact(exc)) from exc
        finally:
            if uploaded is not None:
                if self.keep_remote_file:
                    cleanup = "retained_by_request"
                else:
                    try:
                        self.client.files.delete(name=_field(uploaded, "name"))
                        cleanup = "deleted"
                    except Exception:
                        cleanup = "delete_failed"
        if data is None:
            raise RuntimeError("Gemini analysis ended without structured output")
        return ProviderResult(
            data=data,
            usage=usage,
            interaction_id=interaction_id,
            cleanup_status=cleanup,
        )

    def analyze(self, source: MediaSource, prompt: str, model: str, max_output_tokens: int) -> ProviderResult:
        return self._call(
            source=source,
            prompt=prompt,
            model=model,
            schema=ANALYSIS_SCHEMA,
            max_output_tokens=max_output_tokens,
            thinking_level="low",
        )

    def analyze_clip(
        self,
        clip_path: Path,
        prompt: str,
        model: str,
        max_output_tokens: int = 3000,
    ) -> ProviderResult:
        from .media import resolve_source

        return self._call(
            source=resolve_source(str(clip_path)),
            prompt=prompt,
            model=model,
            schema=HIGH_DETAIL_SCHEMA,
            max_output_tokens=max_output_tokens,
            thinking_level="minimal",
        )
