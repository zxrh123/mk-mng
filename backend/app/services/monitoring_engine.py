"""Continuously collect and analyse network telemetry."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import insert

from app.core.logging import logger
from app.integrations.routeros.client import routeros_client
from app.models.router_event import NetworkSnapshot
from app.schema.network import NetworkMetrics, RouterSnapshot
from app.storage.database import db


class MonitoringEngine:
    """Acquire telemetry data and persist snapshots."""

    def __init__(self) -> None:
        self._router_identifier = "primary-router"

    async def collect_snapshot(self) -> RouterSnapshot:
        metrics_payload = await routeros_client.collect_metrics()
        metrics = NetworkMetrics(
            cpu_load=metrics_payload.get("cpu_load", 0.0),
            memory_usage=metrics_payload.get("memory_usage", 0.0),
            latency_ms=metrics_payload.get("latency_ms", 0.0),
            packet_loss=metrics_payload.get("packet_loss", 0.0),
            interfaces=metrics_payload.get("interfaces", []),
            updated_at=datetime.now(tz=timezone.utc),
        )

        async with db.session() as session:
            await session.execute(
                insert(NetworkSnapshot).values(
                    router_identifier=self._router_identifier,
                    metrics=metrics.model_dump(),
                )
            )

        logger.info(
            "Network snapshot collected",
            router=self._router_identifier,
            cpu=metrics.cpu_load,
            memory=metrics.memory_usage,
        )
        return RouterSnapshot(router_identifier=self._router_identifier, metrics=metrics)

    async def detect_anomalies(self, snapshot: RouterSnapshot) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        if snapshot.metrics.cpu_load > 85:
            anomalies.append(
                {
                    "type": "cpu_spike",
                    "severity": "high",
                    "message": f"CPU load at {snapshot.metrics.cpu_load}%",
                }
            )
        if snapshot.metrics.packet_loss > 5:
            anomalies.append(
                {
                    "type": "packet_loss",
                    "severity": "medium",
                    "message": f"Packet loss at {snapshot.metrics.packet_loss}%",
                }
            )
        return anomalies


monitoring_engine = MonitoringEngine()

