"""Model routing and conservative cost estimates."""

from __future__ import annotations

from dataclasses import asdict, dataclass


MODEL_ALIASES = {
    "auto": "gemini-3.5-flash",
    "standard": "gemini-3.5-flash",
    "budget": "gemini-3.1-flash-lite",
    "deep": "gemini-3.5-flash",
}


@dataclass(frozen=True)
class ModelPricing:
    video_input_per_million: float
    audio_input_per_million: float
    output_per_million: float


PRICING: dict[str, ModelPricing] = {
    # Retained for reproducibility on projects where this legacy model remains available.
    "gemini-2.5-flash": ModelPricing(0.30, 1.00, 2.50),
    "gemini-3.1-flash-lite": ModelPricing(0.25, 0.50, 1.50),
    # Gemini 3.5 Flash publishes a unified standard input price. Treat audio
    # conservatively at the same price until a separate audio rate is exposed.
    "gemini-3.5-flash": ModelPricing(1.50, 1.50, 9.00),
}


@dataclass(frozen=True)
class CostEstimate:
    model: str
    duration_seconds: float
    video_tokens: int
    audio_tokens: int
    output_tokens_allowance: int
    estimated_input_usd: float | None
    estimated_output_usd: float | None
    estimated_total_usd: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def resolve_model(value: str) -> str:
    """Resolve a routing alias while allowing explicit model IDs."""

    return MODEL_ALIASES.get(value, value)


def estimate_cost(
    model: str,
    duration_seconds: float | None,
    output_tokens_allowance: int = 4000,
) -> CostEstimate:
    """Estimate multimodal input and allowed output cost."""

    duration = max(float(duration_seconds or 0.0), 0.0)
    video_tokens = round(duration * 258)
    audio_tokens = round(duration * 32)
    pricing = PRICING.get(model)
    if pricing is None:
        return CostEstimate(
            model,
            duration,
            video_tokens,
            audio_tokens,
            output_tokens_allowance,
            None,
            None,
            None,
        )
    input_cost = (
        video_tokens * pricing.video_input_per_million
        + audio_tokens * pricing.audio_input_per_million
    ) / 1_000_000
    output_cost = output_tokens_allowance * pricing.output_per_million / 1_000_000
    return CostEstimate(
        model,
        duration,
        video_tokens,
        audio_tokens,
        output_tokens_allowance,
        round(input_cost, 6),
        round(output_cost, 6),
        round(input_cost + output_cost, 6),
    )


def estimate_usage_cost(model: str, usage: dict[str, int]) -> float | None:
    """Estimate realized cost from provider token counters."""

    pricing = PRICING.get(model)
    if pricing is None:
        return None
    input_tokens = int(usage.get("input_tokens", 0))
    output_tokens = int(usage.get("output_tokens", 0))
    # Provider usage does not always separate video and audio. Price all input
    # at the higher of the two rates for a conservative realized estimate.
    input_rate = max(pricing.video_input_per_million, pricing.audio_input_per_million)
    return round(
        input_tokens * input_rate / 1_000_000
        + output_tokens * pricing.output_per_million / 1_000_000,
        6,
    )
