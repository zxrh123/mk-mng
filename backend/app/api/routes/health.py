"""Health and readiness probes."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@router.get("/readyz")
async def ready() -> dict[str, str]:
    return {"status": "ready"}

