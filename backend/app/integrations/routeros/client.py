"""RouterOS integration utilities using Paramiko SSH."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import paramiko

from app.core.config import settings
from app.core.logging import logger


class RouterOSExecutionError(RuntimeError):
    pass


@dataclass(slots=True)
class RouterOSCommandResult:
    stdout: str
    stderr: str
    exit_status: int


class RouterOSClient:
    """Facilitate secure communication with MikroTik routers via SSH."""

    def __init__(self, host: str, username: str, password: str | None, use_tls: bool = False) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._use_tls = use_tls

    async def execute_script(self, script: str, dry_run: bool = False) -> RouterOSCommandResult:
        """Run a RouterOS script and return the execution result."""

        if dry_run:
            logger.info("Dry-run requested for RouterOS script")
            return RouterOSCommandResult(stdout=script, stderr="", exit_status=0)

        return await asyncio.to_thread(self._run_command, script)

    def _run_command(self, command: str) -> RouterOSCommandResult:
        logger.info("Executing RouterOS command", command=command)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=self._host,
                username=self._username,
                password=self._password,
                look_for_keys=False,
                allow_agent=False,
                port=8729 if self._use_tls else 22,
            )
            _stdin, stdout, stderr = client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode()
            err = stderr.read().decode()

            if exit_status != 0:
                raise RouterOSExecutionError(err or "Unknown RouterOS error")

            return RouterOSCommandResult(stdout=out, stderr=err, exit_status=exit_status)
        except Exception as exc:  # pragma: no cover - network IO
            logger.exception("RouterOS command failed: %s", exc)
            raise
        finally:
            client.close()

    async def collect_metrics(self) -> dict[str, Any]:
        """Collect metrics from RouterOS. Falls back to synthetic data when unavailable."""

        command = "/system resource print"
        try:
            result = await asyncio.to_thread(self._run_command, command)
            return self._parse_metrics(result.stdout)
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("Falling back to synthetic metrics due to error: %s", exc)
            return {
                "cpu_load": 42.5,
                "memory_usage": 55.1,
                "latency_ms": 3.2,
                "packet_loss": 0.0,
                "interfaces": [],
            }

    def _parse_metrics(self, raw_output: str) -> dict[str, Any]:
        metrics: dict[str, Any] = {
            "cpu_load": 0.0,
            "memory_usage": 0.0,
            "latency_ms": 0.0,
            "packet_loss": 0.0,
            "interfaces": [],
        }

        for line in raw_output.splitlines():
            lower = line.lower()
            if "cpu-load" in lower:
                metrics["cpu_load"] = float(line.split(":")[-1].strip().strip("%"))
            if "memory" in lower and "%" in lower:
                metrics["memory_usage"] = float(line.split(":")[-1].strip().strip("%"))

        return metrics


routeros_client = RouterOSClient(
    host=settings.routeros_host,
    username=settings.routeros_username,
    password=settings.routeros_password.get_secret_value() if settings.routeros_password else None,
    use_tls=settings.routeros_use_tls,
)

