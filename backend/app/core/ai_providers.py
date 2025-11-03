from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx
from loguru import logger

from .config import settings


class OpenAIProvider:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or (settings.openai_api_key.get_secret_value() if settings.openai_api_key else None)
        self.model = model or settings.openai_model
        if not self.api_key:
            logger.warning("OpenAI API key not configured. OpenAI provider will operate in fallback mode.")

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        if not self.api_key:
            return self._fallback_response(prompt)

        payload = {
            "model": self.model,
            "input": prompt,
            **kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post("https://api.openai.com/v1/responses", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if "output" in data and isinstance(data["output"], list):
                return "\n".join(block.get("content", "") for block in data["output"] if isinstance(block, dict))
            return data.get("output_text") or str(data)

    def _fallback_response(self, prompt: str) -> str:
        logger.debug("Using OpenAI fallback response for prompt: {}", prompt)
        return (
            "[OPENAI-FALLBACK]\n"
            "The central AI brain is currently running in simulation mode because no OpenAI API key is configured.\n"
            f"Prompt preview: {prompt[:200]}"
        )


class GeminiProvider:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or (settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None)
        self.model = model or settings.gemini_model
        if not self.api_key:
            logger.warning("Google Gemini API key not configured. Gemini provider will operate in fallback mode.")

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        if not self.api_key:
            return self._fallback_response(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ],
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "\n".join(part.get("text", "") for part in parts)
            return str(data)

    def _fallback_response(self, prompt: str) -> str:
        logger.debug("Using Gemini fallback response for prompt: {}", prompt)
        return (
            "[GEMINI-FALLBACK]\n"
            "Gemini live data retrieval is unavailable because no API key is configured.\n"
            f"Prompt preview: {prompt[:200]}"
        )


class AIIntegrationGateway:
    def __init__(self, openai_provider: Optional[OpenAIProvider] = None, gemini_provider: Optional[GeminiProvider] = None) -> None:
        self.openai_provider = openai_provider or OpenAIProvider()
        self.gemini_provider = gemini_provider or GeminiProvider()

    async def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = self._build_intent_prompt(message, context)

        fast_task = asyncio.create_task(self.gemini_provider.complete(prompt))
        strategic_task = asyncio.create_task(self.openai_provider.complete(prompt))

        done, pending = await asyncio.wait({fast_task, strategic_task}, return_when=asyncio.ALL_COMPLETED)
        for task in pending:
            task.cancel()

        gemini_response = fast_task.result() if fast_task in done else ""
        openai_response = strategic_task.result() if strategic_task in done else ""

        return {
            "gemini": gemini_response,
            "openai": openai_response,
            "intent": self._combine_intents(gemini_response, openai_response),
        }

    async def synthesize_routeros_script(self, network_state: Dict[str, Any], objective: str) -> str:
        prompt = self._build_routeros_prompt(network_state, objective)
        response = await self.openai_provider.complete(prompt, temperature=0.3)
        return response

    async def summarize_event(self, event: Dict[str, Any]) -> str:
        prompt = self._build_summary_prompt(event)
        return await self.gemini_provider.complete(prompt)

    def _combine_intents(self, gemini_resp: str, openai_resp: str) -> Dict[str, Any]:
        fallback = {
            "intent": "analyze",
            "confidence": 0.4,
            "actions": [],
        }
        combined = {
            "intent": fallback["intent"],
            "confidence": fallback["confidence"],
            "actions": fallback["actions"],
        }

        if "intent" in openai_resp:
            combined["intent"] = openai_resp
            combined["confidence"] = 0.9
        elif gemini_resp:
            combined["intent"] = gemini_resp
            combined["confidence"] = 0.6

        combined["raw"] = {"gemini": gemini_resp, "openai": openai_resp}
        return combined

    def _build_intent_prompt(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        context_block = "" if not context else f"Context: {context}\n"
        return (
            "You are the Core AI Brain of a MikroTik RouterOS management platform. "
            "Understand the user's natural language message, infer their intent, "
            "and produce a structured JSON with keys intent, confidence, actions, and reasoning.\n"
            f"{context_block}"
            f"Message: {message}\n"
            "Respond ONLY with JSON."
        )

    def _build_routeros_prompt(self, network_state: Dict[str, Any], objective: str) -> str:
        return (
            "You are an expert MikroTik automation engineer. Generate a safe RouterOS script that achieves the objective.\n"
            "Ensure you validate prerequisites, include comments, and provide rollback procedures if applicable.\n"
            f"Current network telemetry: {network_state}\n"
            f"Objective: {objective}\n"
            "Return ONLY the RouterOS script."
        )

    def _build_summary_prompt(self, event: Dict[str, Any]) -> str:
        return (
            "Summarize the following network event for a human operator in Arabic and English, "
            "highlighting root cause, actions taken, and next steps.\n"
            f"Event Data: {event}"
        )
