from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_providers import AIIntegrationGateway
from app.db.models import ChatMessage, Device, KnowledgeArticle, TelemetryRecord
from app.services.executor import ExecutorEngine
from app.services.knowledge_base import KnowledgeBaseCrawler
from app.services.monitoring import MonitoringEngine


class AIBrain:
    def __init__(
        self,
        session_factory,
        ai_gateway: AIIntegrationGateway,
        monitoring_engine: MonitoringEngine,
        executor_engine: ExecutorEngine,
        knowledge_crawler: KnowledgeBaseCrawler,
    ) -> None:
        self._session_factory = session_factory
        self._ai_gateway = ai_gateway
        self._monitoring = monitoring_engine
        self._executor = executor_engine
        self._knowledge = knowledge_crawler

    async def startup(self) -> None:
        logger.info("Bootstrapping Core AI Brain")
        await self._monitoring.start()
        await self._knowledge.start()

    async def shutdown(self) -> None:
        logger.info("Tearing down Core AI Brain")
        await self._monitoring.stop()
        await self._knowledge.stop()

    async def handle_chat(self, session_id: str, message: str, host: Optional[str] = None) -> Dict[str, Any]:
        logger.info("Handling chat message for session {}", session_id)
        intent_envelope = await self._ai_gateway.analyze_intent(message)
        intent_payload = self._parse_intent(intent_envelope)

        async with self._session_factory() as session:
            await self._log_chat(session, session_id, "user", message)

        response = await self._route_intent(session_id, intent_payload, host)

        async with self._session_factory() as session:
            await self._log_chat(session, session_id, "assistant", response["message"], response.get("metadata"))

        return response

    async def _route_intent(self, session_id: str, intent_payload: Dict[str, Any], host: Optional[str]) -> Dict[str, Any]:
        intent = intent_payload.get("intent", "diagnose")
        logger.debug("Routing intent {} with payload {}", intent, intent_payload)

        if intent in {"optimize", "execute", "apply_changes"} and host:
            result = await self._executor.plan_and_execute(host, intent_payload.get("objective", intent), intent_payload)
            message = (
                "\u062a\u0645 \u062a\u0646\u0641\u064a\u0630 \u0627\u0644\u062e\u0637\u0648\u0629 \u0627\u0644\u0645\u0637\u0644\u0648\u0628\u0629 \u0628\u0646\u062c\u0627\u062d."
                if result.get("executed")
                else "\u062a\u0645 \u0625\u0639\u062f\u0627\u062f \u0627\u0644\u0633\u0643\u0631\u0628\u062a \u0648\u062c\u0627\u0647\u0632 \u0644\u0644\u0645\u0631\u0627\u062c\u0639\u0629."
            )
            return {
                "message": message,
                "metadata": {"action_result": result},
            }

        if intent in {"monitor", "status", "diagnose"}:
            telemetry = await self._latest_telemetry(host)
            summary = await self._ai_gateway.summarize_event({"telemetry": telemetry, "context": intent_payload})
            return {
                "message": summary,
                "metadata": {"telemetry": telemetry},
            }

        if intent in {"knowledge", "faq"}:
            articles = await self._recent_knowledge()
            return {
                "message": "\u0623\u062d\u062f\u062b \u0627\u0644\u0645\u0642\u0627\u0644\u0627\u062a \u0627\u0644\u062a\u0639\u0644\u064a\u0645\u064a\u0629 \u0645\u062a\u0627\u062d\u0629\u060c \u062a\u0645 \u0625\u0631\u0633\u0627\u0644\u0647\u0627 \u0625\u0644\u0649 \u0644\u0648\u062d\u0629 \u0627\u0644\u062a\u062d\u0643\u0645.",
                "metadata": {"articles": articles},
            }

        return {
            "message": "\u0644\u0645 \u0623\u0641\u0647\u0645 \u0627\u0644\u0637\u0644\u0628 \u0628\u0627\u0644\u0643\u0627\u0645\u0644. \u0627\u0644\u0631\u062c\u0627\u0621 \u062a\u0648\u0636\u064a\u062d \u0627\u0644\u0647\u062f\u0641 \u0623\u0648 \u062a\u062d\u062f\u064a\u062f \u0627\u0644\u062c\u0647\u0627\u0632 \u0627\u0644\u0645\u0637\u0644\u0648\u0628.",
            "metadata": {"intent": intent_payload},
        }

    async def execute_objective(
        self,
        host: str,
        objective: str,
        auto_execute: Optional[bool] = None,
        session_id: str = "system",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "intent": "execute",
            "objective": objective,
            "context": context or {},
        }
        result = await self._executor.plan_and_execute(host, objective, payload, auto_approve=auto_execute)
        async with self._session_factory() as session:
            await self._log_chat(
                session,
                session_id,
                "assistant",
                f"\u062a\u0645 \u062a\u0646\u0641\u064a\u0630 \u0627\u0644\u0647\u062f\u0641: {objective}",
                {"action_result": result},
            )
        return result

    async def _recent_knowledge(self) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(select(KnowledgeArticle).order_by(KnowledgeArticle.last_synced_at.desc()).limit(5))
            articles = result.scalars().all()
            return [
                {
                    "title": article.title,
                    "summary": article.summary,
                    "synced_at": article.last_synced_at.isoformat(),
                    "url": article.source_url,
                }
                for article in articles
            ]

    async def _latest_telemetry(self, host: Optional[str]) -> Dict[str, Any]:
        async with self._session_factory() as session:
            query = (
                select(TelemetryRecord, Device)
                .join(Device, Device.id == TelemetryRecord.device_id)
                .order_by(TelemetryRecord.recorded_at.desc())
            )
            if host:
                query = query.where(Device.host == host)
            query = query.limit(1)
            result = await session.execute(query)
            row = result.first()
            if not row:
                return {}
            telemetry, device = row
            return {
                "device": device.host,
                "cpu_load": telemetry.cpu_load,
                "memory_usage": telemetry.memory_usage,
                "latency_ms": telemetry.latency_ms,
                "packet_loss": telemetry.packet_loss,
                "anomalies": telemetry.anomalies,
                "recorded_at": telemetry.recorded_at.isoformat(),
            }

    async def _log_chat(self, session: AsyncSession, session_id: str, sender: str, content: str, metadata: Optional[dict] = None) -> None:
        message = ChatMessage(session_id=session_id, sender=sender, content=content, meta=metadata or {})
        session.add(message)
        await session.commit()

    def _parse_intent(self, intent_envelope: Dict[str, Any]) -> Dict[str, Any]:
        candidate = intent_envelope.get("intent")
        if isinstance(candidate, dict):
            return candidate
        if isinstance(candidate, str):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return {"intent": candidate, "confidence": intent_envelope.get("confidence", 0.5)}
        return intent_envelope
