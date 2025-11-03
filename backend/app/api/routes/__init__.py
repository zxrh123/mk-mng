"""API router registration."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import ai, health, network


def register_routes() -> APIRouter:
    router = APIRouter()
    router.include_router(health.router, tags=["health"])
    router.include_router(ai.router, prefix="/ai", tags=["ai"])
    router.include_router(network.router, prefix="/network", tags=["network"])
    return router


__all__ = ["register_routes"]

