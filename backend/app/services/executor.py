from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_providers import AIIntegrationGateway
from app.core.config import settings
from app.core.routeros import RouterOSClient, build_routeros_client
from app.db.models import AIAction, ActionStatus, Device


class ExecutorEngine:
    def __init__(self, session_factory, ai_gateway: AIIntegrationGateway) -> None:
        self._session_factory = session_factory
        self._ai_gateway = ai_gateway
        self._clients: Dict[str, RouterOSClient] = {}

    async def plan_and_execute(
        self,
        host: str,
        objective: str,
        intent_payload: Dict[str, Any],
        auto_approve: Optional[bool] = None,
    ) -> Dict[str, Any]:
        client = self._get_client(host)
        if not client:
            raise ValueError(f"RouterOS host {host} is not configured or credentials missing")

        network_state = await self._collect_state(client)
        script = await self._ai_gateway.synthesize_routeros_script(network_state, objective)

        async with self._session_factory() as session:
            device = await self._ensure_device(session, host)
            action = AIAction(
                device_id=device.id,
                intent=intent_payload.get("intent", objective),
                script=script,
                reasoning=intent_payload,
                dry_run=settings.dry_run_default,
            )
            session.add(action)
            await session.commit()
            await session.refresh(action)

            if auto_approve is None:
                auto_approve = settings.auto_execute

            result = await self._maybe_execute(client, action, auto_approve)
            action.result = result
            action.status = result.get("status", ActionStatus.DRY_RUN.value)
            action.executed_at = datetime.utcnow()
            action.dry_run = not result.get("executed", False)
            await session.commit()

        return result

    async def _maybe_execute(self, client: RouterOSClient, action: AIAction, auto_approve: bool) -> Dict[str, Any]:
        if not auto_approve:
            logger.info("Dry-run only for action {}", action.id)
            return {
                "status": ActionStatus.DRY_RUN.value,
                "executed": False,
                "script": action.script,
            }

        if settings.snapshot_before_execute:
            await self._create_snapshot(client)

        result = await client.execute_script(action.script)
        logger.success("Action {} executed with result {}", action.id, result)
        return {
            "status": ActionStatus.EXECUTED.value,
            "executed": True,
            "script": action.script,
            "result": result,
        }

    async def _collect_state(self, client: RouterOSClient) -> Dict[str, Any]:
        resource, interfaces = await asyncio.gather(
            client.fetch_system_resource(),
            client.fetch_interface_stats(),
        )
        return {
            "resource": resource,
            "interfaces": interfaces,
        }

    async def _ensure_device(self, session: AsyncSession, host: str) -> Device:
        result = await session.execute(select(Device).where(Device.host == host))
        device = result.scalar_one_or_none()
        if not device:
            device = Device(host=host)
            session.add(device)
            await session.commit()
            await session.refresh(device)
        return device

    def _get_client(self, host: str) -> Optional[RouterOSClient]:
        if host not in self._clients:
            self._clients[host] = build_routeros_client(host)
        return self._clients.get(host)

    async def _create_snapshot(self, client: RouterOSClient) -> None:
        logger.info("Creating pre-execution snapshot")
        snapshot_name = f"ai-snapshot-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        try:
            await client.run_command("/system/backup/save")
            logger.info("Snapshot {} created", snapshot_name)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to create snapshot: {}", exc)
