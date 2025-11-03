"""OpenAI provider integration for natural language reasoning and script generation."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.ai.providers.base import AIProvider
from app.core.logging import logger


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str | None, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=30.0)

    async def complete(self, prompt: str, **kwargs: Any) -> dict[str, Any]:  # noqa: D401
        """Send a completion request. Falls back to rule-based stub when API key is absent."""

        if not self._api_key:
            logger.warning("OpenAI API key missing, using heuristic fallback response")
            return {
                "provider": self.name,
                "model": "heuristic",
                "prompt": prompt,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Simulated response due to missing OpenAI credentials.",
                        },
                        "finish_reason": "stub",
                    }
                ],
            }

        body = {
            "model": self._model,
            "messages": kwargs.get("messages")
            or [
                {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful AI.")},
                {"role": "user", "content": prompt},
            ],
            "temperature": kwargs.get("temperature", 0.2),
            "response_format": {"type": "json_object"} if kwargs.get("json_mode") else None,
        }

        # Remove None entries for clean payload
        body = {k: v for k, v in body.items() if v is not None}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        response = await self._client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            content=json.dumps(body),
        )
        response.raise_for_status()
        payload = response.json()
        return payload

    async def aclose(self) -> None:
        await self._client.aclose()

