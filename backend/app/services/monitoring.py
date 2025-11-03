from __future__ import annotations

import asyncio
import contextlib
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.routeros import RouterOSClient, build_routeros_client
from app.db.models import Device, DeviceStatus, TelemetryRecord


class MonitoringEngine:
    def __init__(self, session_factory, interval_seconds: Optional[int] = None) -> None:
        self._session_factory = session_factory
        self._interval = interval_seconds or settings.telemetry_interval_seconds
        self._clients: Dict[str, RouterOSClient] = {}
        self._task: Optional[asyncio.Task] = None
        self._running = asyncio.Event()

    async def start(self) -> None:
        logger.info("Starting monitoring engine")
        self._running.set()
        self._prepare_clients()
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        logger.info("Stopping monitoring engine")
        self._running.clear()
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    def _prepare_clients(self) -> None:
        for host in settings.routeros_hosts:
            client = build_routeros_client(host)
            if client:
                self._clients[host] = client

    async def _run_loop(self) -> None:
        while self._running.is_set():
            try:
                await self.poll_all()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Monitoring loop encountered an error: {}", exc)
            await asyncio.sleep(self._interval)

    async def poll_all(self) -> None:
        for host, client in self._clients.items():
            await self._poll_device(host, client)

    async def _poll_device(self, host: str, client: RouterOSClient) -> None:
        async with self._session_factory() as session:  # type: AsyncSession
            device = await self._ensure_device(session, host)
            resource = await client.fetch_system_resource()
            interfaces = await client.fetch_interface_stats()
            latency_ms, packet_loss = await self._measure_connectivity(host)

            telemetry = TelemetryRecord(
                device_id=device.id,
                cpu_load=float(resource.get("cpu-load", 0)) / 100,
                memory_usage=self._calculate_memory_usage(resource),
                temperature=float(resource.get("temperature", 0) or 0),
                voltage=float(resource.get("voltage", 0) or 0),
                latency_ms=latency_ms,
                packet_loss=packet_loss,
                interfaces=interfaces,
                anomalies=self._detect_anomalies(resource, interfaces),
            )

            device.status = DeviceStatus.ONLINE.value
            device.last_seen = datetime.utcnow()

            session.add(telemetry)
            await session.commit()
            logger.debug("Telemetry recorded for host {}", host)

    async def _ensure_device(self, session: AsyncSession, host: str) -> Device:
        result = await session.execute(select(Device).where(Device.host == host))
        device = result.scalar_one_or_none()
        if not device:
            device = Device(host=host, status=DeviceStatus.DEGRADED.value)
            session.add(device)
            await session.commit()
            await session.refresh(device)
        return device

    def _detect_anomalies(self, resource: Dict[str, str], interfaces: Dict[str, Dict[str, str]]) -> Dict[str, float]:
        anomalies: Dict[str, float] = {}
        cpu_load = float(resource.get("cpu-load", 0)) / 100
        memory_free = float(resource.get("free-memory", 0))
        memory_total = float(resource.get("total-memory", 1))
        memory_usage = 1 - (memory_free / memory_total if memory_total else 0)

        if cpu_load > settings.anomaly_threshold_cpu:
            anomalies["cpu_load"] = cpu_load
        if memory_usage > settings.anomaly_threshold_memory:
            anomalies["memory_usage"] = memory_usage

        error_interfaces = {
            name: iface
            for name, iface in interfaces.items()
            if int(iface.get("rx-error", 0)) + int(iface.get("tx-error", 0)) > settings.anomaly_threshold_interface_errors
        }
        if error_interfaces:
            anomalies["interfaces"] = len(error_interfaces)

        return anomalies

    def _calculate_memory_usage(self, resource: Dict[str, str]) -> float:
        memory_free = float(resource.get("free-memory", 0))
        memory_total = float(resource.get("total-memory", 1))
        if memory_total <= 0:
            return 0.0
        return 1 - (memory_free / memory_total)

    async def _measure_connectivity(self, host: str) -> Tuple[float, float]:
        try:
            process = await asyncio.create_subprocess_exec(
                "ping",
                "-c",
                "5",
                host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            logger.warning("ping binary not found; skipping latency measurement")
            return 0.0, 0.0

        stdout, _ = await process.communicate()
        output = stdout.decode()

        latency_match = re.search(r"= [\d\.]+/([\d\.]+)/", output)
        packet_match = re.search(r"(\d+)% packet loss", output)

        latency = float(latency_match.group(1)) if latency_match else 0.0
        packet_loss = float(packet_match.group(1)) / 100 if packet_match else 0.0
        return latency, packet_loss
