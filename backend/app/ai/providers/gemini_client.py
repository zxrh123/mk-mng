"""Google Gemini provider integration for fast knowledge retrieval."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.ai.providers.base import AIProvider
from app.core.logging import logger


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str | None, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=20.0)

    async def complete(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        if not self._api_key:
            logger.warning("Gemini API key missing, using heuristic fallback response")
            return {
                "provider": self.name,
                "model": "heuristic",
                "candidates": [
                    {
                        "output": "Simulated Gemini insight because no API key is configured.",
                        "safety_ratings": [],
                    }
                ],
            }

        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.1),
                "topK": kwargs.get("top_k", 32),
                "topP": kwargs.get("top_p", 0.95),
                "maxOutputTokens": kwargs.get("max_tokens", 1024),
            },
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }

        response = await self._client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent",
            headers=headers,
            content=json.dumps(body),
        )
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        await self._client.aclose()

