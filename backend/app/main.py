"""FastAPI application factory for the MikroTik AI platform."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.brain.orchestrator import ai_brain
from app.api.routes import register_routes
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.knowledge.crawler import knowledge_base_crawler
from app.storage.cache import ensure_redis_connected, redis_pool
from app.storage.database import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    db.configure()
    logger.info("Database configured")

    await ensure_redis_connected()
    logger.info("Redis connected")

    await knowledge_base_crawler.refresh()

    async def refresh_knowledge() -> None:
        while True:
            await knowledge_base_crawler.refresh()
            await asyncio.sleep(3600)

    kb_task = asyncio.create_task(refresh_knowledge())

    try:
        yield
    finally:
        kb_task.cancel()
        with contextlib.suppress(Exception):
            await kb_task
        await redis_pool.close()
        await ai_brain.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    if settings.client_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(settings.client_origin)],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(register_routes(), prefix=settings.api_prefix)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"service": settings.app_name}

    return app


app = create_app()

