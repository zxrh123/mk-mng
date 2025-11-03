"""Safely execute RouterOS scripts with guard rails and auditing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import insert, update

from app.core.config import settings
from app.core.logging import logger
from app.integrations.routeros.client import routeros_client
from app.models.router_event import AIDecision
from app.schema.ai import AIExecutionResult, AIScript
from app.storage.database import db


class ExecutorEngine:
    """Manage dry-runs, execution, and audit logging for RouterOS scripts."""

    async def dry_run(self, script: AIScript) -> dict[str, Any]:
        logger.info("Performing dry-run for script")
        result = await routeros_client.execute_script(script.contents, dry_run=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_status": result.exit_status,
        }

    async def execute(self, decision_id: UUID, script: AIScript, metadata: dict[str, Any]) -> AIExecutionResult:
        if not settings.allow_auto_execute:
            raise PermissionError("Auto-execution disabled; manual approval required")

        started = datetime.now(tz=timezone.utc)
        result = await routeros_client.execute_script(script.contents, dry_run=False)
        completed = datetime.now(tz=timezone.utc)

        async with db.session() as session:
            await session.execute(
                update(AIDecision)
                .where(AIDecision.id == decision_id)
                .values(
                    executed=True,
                    execution_result={
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "exit_status": result.exit_status,
                        "metadata": metadata,
                    },
                )
            )

        logger.info("RouterOS script executed", decision_id=str(decision_id))

        return AIExecutionResult(
            decision_id=str(decision_id),
            executed=True,
            started_at=started,
            completed_at=completed,
            result={
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_status": result.exit_status,
                "metadata": metadata,
            },
        )

    async def log_decision(
        self,
        intent: str,
        plan: dict[str, Any],
        script: AIScript | None,
        metadata: dict[str, Any],
    ) -> UUID:
        async with db.session() as session:
            result = await session.execute(
                insert(AIDecision).values(
                    intent=intent,
                    plan=plan,
                    script=script.contents if script else None,
                    executed=False,
                    execution_result={"metadata": metadata},
                ).returning(AIDecision.id)
            )
            decision_id: UUID = result.scalar_one()
        logger.info("AI decision logged", decision_id=str(decision_id))
        return decision_id


executor_engine = ExecutorEngine()

