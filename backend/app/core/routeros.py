from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Optional

import routeros_api
from loguru import logger

from .config import settings


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
        self._pool: Optional[routeros_api.RouterOsApiPool] = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[routeros_api.RouterOsApi]:
        if self._pool is None:
            self._pool = routeros_api.RouterOsApiPool(
                host=self.credentials.host,
                username=self.credentials.username,
                password=self.credentials.password,
                port=self.credentials.port,
                use_ssl=self.credentials.use_ssl,
            )
        api = await asyncio.to_thread(self._pool.get_api)
        try:
            yield api
        finally:
            await asyncio.to_thread(api.disconnect)

    async def fetch_system_resource(self) -> Dict[str, Any]:
        async with self.connect() as api:
            resource = await asyncio.to_thread(self._call_resource, api, "/system/resource/getall")
            return resource[0] if resource else {}

    async def fetch_interface_stats(self) -> Dict[str, Any]:
        async with self.connect() as api:
            interfaces = await asyncio.to_thread(self._call_resource, api, "/interface/print")
            return {iface.get("name"): iface for iface in interfaces}

    async def run_command(self, command: str) -> Any:
        async with self.connect() as api:
            logger.debug("Executing RouterOS command: {}", command)
            return await asyncio.to_thread(self._call_resource, api, command)

    async def execute_script(self, script: str) -> Dict[str, Any]:
        async with self.connect() as api:
            logger.info("Executing RouterOS script via /system/script/run")
            script_resource = api.get_resource("/system/script")
            script_name = f"ai-exec-{hash(script) & 0xffff}"
            await asyncio.to_thread(
                script_resource.add,
                name=script_name,
                policy="ftp,reboot,read,write,policy,test,password,sniff,sensitive",
                source=script,
            )
            await asyncio.to_thread(script_resource.call, "run", {"number": script_name})
            await asyncio.to_thread(script_resource.remove, {"numbers": script_name})
            return {"status": "success", "script": script_name}

    def _call_resource(self, api: routeros_api.RouterOsApi, command: str) -> Any:
        resource = api.get_resource(command)
        return resource.get()


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
