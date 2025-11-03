"""Redis cache connector for low-latency state sharing."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import redis.asyncio as redis

from app.core.config import settings


class RedisPool:
    """Manage a shared Redis connection pool."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._pool: redis.Redis | None = None

    async def connect(self) -> None:
        self._pool = redis.from_url(self._url, decode_responses=True)
        await self._pool.ping()

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()

    @property
    def client(self) -> redis.Redis:
        if self._pool is None:
            raise RuntimeError("Redis pool not initialised")
        return self._pool

    async def lock(self, name: str, timeout: int = 10) -> AsyncGenerator[redis.lock.Lock, None]:
        lock = self.client.lock(name, timeout=timeout)
        await lock.acquire()
        try:
            yield lock
        finally:
            await lock.release()


redis_pool = RedisPool(settings.redis_url)


async def ensure_redis_connected(retries: int = 5, delay: float = 1.0) -> None:
    """Retry Redis connection until success or retries exhausted."""

    for attempt in range(1, retries + 1):
        try:
            await redis_pool.connect()
            return
        except Exception:  # pragma: no cover - best effort connectivity
            if attempt == retries:
                raise
            await asyncio.sleep(delay * attempt)

