"""
LLM client wrapper supporting multiple providers.
Handles API calls with retries, logging, and error handling.
"""

import json
import time
from typing import Any, Dict, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from .config import config
from .logger import logger


class LLMClient:
    """Unified LLM client for OpenAI and Anthropic."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ('openai' or 'anthropic'). Defaults to config.
        """
        self.provider = provider or config.llm.provider

        if self.provider == "openai":
            import openai

            self.client = openai.OpenAI(api_key=config.llm.api_key)
        elif self.provider == "anthropic":
            import anthropic

            self.client = anthropic.Anthropic(api_key=config.llm.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        logger.info(f"Initialized LLM client with provider: {self.provider}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=16),
        reraise=True,
    )
    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        json_mode: bool = False,
    ) -> str:
        """
        Get completion from LLM.

        Args:
            prompt: Input prompt
            model: Model ID (defaults to config)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Whether to enforce JSON output

        Returns:
            Generated text
        """
        model = model or config.llm.model_small
        start_time = time.time()

        logger.debug(f"LLM request: model={model}, temp={temperature}, tokens={max_tokens}")

        try:
            if self.provider == "openai":
                response = self._openai_complete(prompt, model, temperature, max_tokens, json_mode)
            elif self.provider == "anthropic":
                response = self._anthropic_complete(
                    prompt, model, temperature, max_tokens, json_mode
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            elapsed = time.time() - start_time
            logger.info(
                f"LLM completion successful in {elapsed:.2f}s "
                f"(~{len(response)} chars, model={model})"
            )

            return response

        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            raise

    def _openai_complete(
        self, prompt: str, model: str, temperature: float, max_tokens: int, json_mode: bool
    ) -> str:
        """OpenAI completion."""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _anthropic_complete(
        self, prompt: str, model: str, temperature: float, max_tokens: int, json_mode: bool
    ) -> str:
        """Anthropic completion."""
        # Map OpenAI model names to Anthropic if needed
        model_map = {
            "gpt-4o": "claude-sonnet-4",
            "gpt-4o-mini": "claude-haiku-4",
        }
        model = model_map.get(model, model)

        if json_mode:
            prompt += "\n\nReturn ONLY a valid JSON object with no additional text."

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    def complete_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """
        Get JSON completion from LLM.

        Args:
            prompt: Input prompt
            model: Model ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Parsed JSON dictionary
        """
        response = self.complete(prompt, model, temperature, max_tokens, json_mode=True)

        # Try to parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON, attempting cleanup: {e}")

            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
