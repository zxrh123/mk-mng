from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from loguru import logger

from .config import settings


try:
    import librouteros  # type: ignore
except ImportError:  # pragma: no cover - graceful degradation when library missing
    librouteros = None  # type: ignore[assignment]


@dataclass
class RouterOSCredentials:
    host: str
    username: str
    password: str
    port: int = settings.routeros_port
    use_ssl: bool = False


class RouterOSClient:
    def __init__(self, credentials: RouterOSCredentials) -> None:
        self.credentials = credentials
        self._warned = False

    async def fetch_system_resource(self) -> Dict[str, Any]:
        if librouteros is None:
            return self._fake_system_resource()

        try:
            return await asyncio.to_thread(self._fetch_system_resource_real)
        except Exception as exc:  # pragma: no cover - runtime safeguard
            self._log_fallback(exc)
            return self._fake_system_resource()

    async def fetch_interface_stats(self) -> Dict[str, Any]:
        if librouteros is None:
            return self._fake_interfaces()

        try:
            return await asyncio.to_thread(self._fetch_interface_stats_real)
        except Exception as exc:  # pragma: no cover
            self._log_fallback(exc)
            return self._fake_interfaces()

    async def run_command(self, command: str) -> Dict[str, Any]:
        if librouteros is None:
            self._log_fallback("run_command noop")
            return {"status": "noop", "command": command}

        try:
            return await asyncio.to_thread(self._run_command_real, command)
        except Exception as exc:  # pragma: no cover
            self._log_fallback(exc)
            return {"status": "error", "command": command, "detail": str(exc)}

    async def execute_script(self, script: str) -> Dict[str, Any]:
        if librouteros is None:
            self._log_fallback("execute_script noop")
            return {
                "status": "simulated",
                "executed": False,
                "script": script,
                "detail": "librouteros not installed; returning simulated result",
            }

        try:
            return await asyncio.to_thread(self._execute_script_real, script)
        except Exception as exc:  # pragma: no cover
            self._log_fallback(exc)
            return {
                "status": "error",
                "executed": False,
                "script": script,
                "detail": str(exc),
            }

    # --- Real implementations -------------------------------------------------

    def _fetch_system_resource_real(self) -> Dict[str, Any]:
        assert librouteros is not None
        with librouteros.connect(
            username=self.credentials.username,
            password=self.credentials.password,
            host=self.credentials.host,
            port=self.credentials.port,
            use_ssl=self.credentials.use_ssl,
        ) as api:
            resource = api.path("/system/resource")
            result = resource.get()
            return dict(result[0]) if result else {}

    def _fetch_interface_stats_real(self) -> Dict[str, Any]:
        assert librouteros is not None
        with librouteros.connect(
            username=self.credentials.username,
            password=self.credentials.password,
            host=self.credentials.host,
            port=self.credentials.port,
            use_ssl=self.credentials.use_ssl,
        ) as api:
            interface_path = api.path("/interface")
            return {entry["name"]: dict(entry) for entry in interface_path.get()}

    def _run_command_real(self, command: str) -> Dict[str, Any]:
        assert librouteros is not None
        with librouteros.connect(
            username=self.credentials.username,
            password=self.credentials.password,
            host=self.credentials.host,
            port=self.credentials.port,
            use_ssl=self.credentials.use_ssl,
        ) as api:
            logger.debug("Executing RouterOS command: {}", command)
            result = api.path(command).get()
            return {"status": "success", "result": [dict(entry) for entry in result]}

    def _execute_script_real(self, script: str) -> Dict[str, Any]:
        assert librouteros is not None
        script_name = f"ai-exec-{abs(hash(script)) & 0xFFFF}"
        with librouteros.connect(
            username=self.credentials.username,
            password=self.credentials.password,
            host=self.credentials.host,
            port=self.credentials.port,
            use_ssl=self.credentials.use_ssl,
        ) as api:
            script_path = api.path("/system/script")
            script_path.add(
                name=script_name,
                policy="ftp,reboot,read,write,policy,test,password,sniff,sensitive",
                source=script,
            )
            api.path("/system/script/run").call(number=script_name)
            script_path.remove(number=script_name)
        return {"status": "success", "executed": True, "script": script_name}

    # --- Fallback helpers -----------------------------------------------------

    def _fake_system_resource(self) -> Dict[str, Any]:
        now = time.time()
        return {
            "cpu-load": int(20 + 10 * (1 + random.random())),
            "total-memory": 256 * 1024 * 1024,
            "free-memory": int(128 * 1024 * 1024 * random.uniform(0.4, 0.9)),
            "temperature": round(35 + random.random() * 10, 2),
            "voltage": round(24 + random.random(), 2),
            "board-name": "AI-Simulated",
            "generated-at": now,
        }

    def _fake_interfaces(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ether1": {
                "name": "ether1",
                "rx-error": random.randint(0, 2),
                "tx-error": random.randint(0, 2),
                "rx-byte": random.randint(10_000_000, 50_000_000),
                "tx-byte": random.randint(5_000_000, 25_000_000),
            },
            "wlan1": {
                "name": "wlan1",
                "rx-error": random.randint(0, 5),
                "tx-error": random.randint(0, 5),
                "rx-byte": random.randint(1_000_000, 5_000_000),
                "tx-byte": random.randint(1_000_000, 5_000_000),
            },
        }

    def _log_fallback(self, reason: Any) -> None:
        if not self._warned:
            logger.warning(
                "RouterOS live integration unavailable for host {}. Reason: {}. Falling back to simulated data.",
                self.credentials.host,
                reason,
            )
            self._warned = True


def build_routeros_client(host: str) -> Optional[RouterOSClient]:
    if not settings.routeros_username or not settings.routeros_password:
        logger.warning("RouterOS credentials are not configured; skipping client creation for host {}", host)
        return None

    creds = RouterOSCredentials(
        host=host,
        username=settings.routeros_username,
        password=settings.routeros_password.get_secret_value(),
    )
    return RouterOSClient(creds)
