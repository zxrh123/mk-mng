"""Core AI brain that orchestrates decision-making across providers."""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Any

from app.ai.providers.gemini_client import GeminiProvider
from app.ai.providers.openai_client import OpenAIProvider
from app.core.config import settings
from app.core.logging import logger
from app.knowledge.crawler import knowledge_base_crawler
from app.schema.ai import AICommandRequest, AICommandResponse, AIExecutionPlan, AIPlanStep, AIScript
from app.services.executor_engine import executor_engine
from app.services.monitoring_engine import monitoring_engine

INTENT_PATTERNS: dict[str, re.Pattern[str]] = {
    "restart_interface": re.compile(r"(?:reset|restart|bounce)\s+(?:the\s+)?interface\s+(?P<iface>\S+)", re.I),
    "optimize_bandwidth": re.compile(r"(?:optimi[sz]e|limit|shape)\s+bandwidth", re.I),
    "inspect_hotspot": re.compile(r"hot\s*spot|hotspot", re.I),
    "check_security": re.compile(r"attack|intrusion|security", re.I),
}


class AIBrainOrchestrator:
    """Entrypoint that coordinates AI providers, monitoring data, and execution."""

    def __init__(self) -> None:
        self._openai = OpenAIProvider(
            api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None,
            model=settings.openai_model,
        )
        self._gemini = GeminiProvider(
            api_key=settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None,
            model=settings.gemini_model,
        )

    async def handle_command(self, request: AICommandRequest) -> AICommandResponse:
        logger.info("AI brain received request", actor=request.actor)

        snapshot = await monitoring_engine.collect_snapshot()
        anomalies = await monitoring_engine.detect_anomalies(snapshot)

        intent = self._infer_intent(request.message)
        logger.info("Intent inferred", intent=intent)

        knowledge_context = self._aggregate_knowledge(intent)
        ai_meta = await self._consult_models(request.message, intent, snapshot.metrics.model_dump())

        plan = self._build_plan(intent, request.message, snapshot.metrics.model_dump(), anomalies, ai_meta)
        script = self._build_script(intent, plan, ai_meta)

        metadata = {
            "snapshot": snapshot.model_dump(),
            "anomalies": anomalies,
            "ai_meta": ai_meta,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }

        decision_id = await executor_engine.log_decision(intent=intent, plan=plan.model_dump(), script=script, metadata=metadata)

        requires_approval = plan.requires_approval or not settings.allow_auto_execute

        response = AICommandResponse(
            plan=plan,
            script=script,
            auto_execute=not requires_approval,
            metadata={
                "decision_id": str(decision_id),
                "knowledge": knowledge_context,
                "anomalies": anomalies,
            },
        )

        return response

    async def aclose(self) -> None:
        await asyncio.gather(self._openai.aclose(), self._gemini.aclose())

    async def _consult_models(
        self,
        message: str,
        intent: str,
        snapshot_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Query OpenAI and Gemini for complementary reasoning."""

        system_prompt = (
            "You are an expert MikroTik network engineer AI. "
            "Analyse the instruction, outline remediation steps, and produce safety considerations."
        )

        prompt = (
            f"Instruction: {message}\n"
            f"Detected intent: {intent}\n"
            f"Current metrics: {snapshot_metrics}\n"
            "Respond with JSON containing keys: steps (array of strings) and risks (array)."
        )

        openai_payload = await self._openai.complete(
            prompt,
            system_prompt=system_prompt,
            json_mode=True,
        )

        gemini_payload = await self._gemini.complete(
            f"Summarise recent MikroTik best practices related to: {intent}",
            temperature=0.2,
        )

        return {
            "openai": openai_payload,
            "gemini": gemini_payload,
        }

    def _infer_intent(self, message: str) -> str:
        for intent, pattern in INTENT_PATTERNS.items():
            if pattern.search(message):
                return intent
        if "balance" in message.lower():
            return "adjust_load_balance"
        if "log" in message.lower():
            return "inspect_logs"
        return "general_diagnostics"

    def _build_plan(
        self,
        intent: str,
        message: str,
        metrics: dict[str, Any],
        anomalies: list[dict[str, Any]],
        ai_meta: dict[str, Any],
    ) -> AIExecutionPlan:
        steps: list[AIPlanStep] = []
        requires_approval = False

        if intent == "restart_interface":
            iface_match = INTENT_PATTERNS[intent].search(message)
            iface = iface_match.group("iface") if iface_match else "ether1"
            steps = [
                AIPlanStep(description=f"Verify health metrics for {iface}", order=1),
                AIPlanStep(description=f"Disable interface {iface}", order=2),
                AIPlanStep(description=f"Enable interface {iface}", order=3),
                AIPlanStep(description=f"Monitor interface {iface} for 60 seconds", order=4),
            ]
        elif intent == "optimize_bandwidth":
            steps = [
                AIPlanStep(description="Analyse current throughput and queues", order=1),
                AIPlanStep(description="Apply smart queue for fair usage", order=2),
                AIPlanStep(description="Notify hotspot users about adjustments", order=3),
            ]
            requires_approval = True
        elif intent == "inspect_hotspot":
            steps = [
                AIPlanStep(description="Review hotspot session load", order=1),
                AIPlanStep(description="Generate customer impact summary", order=2),
            ]
        else:
            steps = [
                AIPlanStep(description="Perform diagnostic health check", order=1),
                AIPlanStep(description="Recommend remediation options", order=2),
            ]

        confidence = 0.7 + (0.1 if not anomalies else -0.1)
        return AIExecutionPlan(intent=intent, confidence=min(confidence, 0.95), steps=steps, requires_approval=requires_approval)

    def _build_script(self, intent: str, plan: AIExecutionPlan, ai_meta: dict[str, Any]) -> AIScript:
        if intent == "restart_interface":
            iface = "ether1"
            for step in plan.steps:
                if "interface" in step.description and "disable" in step.description.lower():
                    iface = step.description.split()[-1]
            contents = (
                f"/interface disable [find name={iface}]\n"
                f"/delay 2\n"
                f"/interface enable [find name={iface}]\n"
                f"/log info \"AI restarted interface {iface}\""
            )
        elif intent == "optimize_bandwidth":
            contents = (
                "/queue simple add name=\"AI-AutoQoS\" target=0.0.0.0/0 max-limit=50M/50M burst-limit=60M/60M "
                "burst-threshold=40M/40M burst-time=30s"
            )
        elif intent == "inspect_hotspot":
            contents = "/ip hotspot active print detail"
        elif intent == "check_security":
            contents = "/log print where topics~\"security\""
        else:
            contents = "/system resource print"

        return AIScript(contents=contents)

    def _aggregate_knowledge(self, intent: str) -> list[str]:
        snippets: list[str] = []
        for document in knowledge_base_crawler.iter_documents():
            if intent.replace("_", " ") in document.lower():
                snippets.append(document[:300])
            if len(snippets) >= 3:
                break
        return snippets


ai_brain = AIBrainOrchestrator()

