"""Network monitoring endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.schema.network import RouterSnapshot
from app.services.monitoring_engine import monitoring_engine

router = APIRouter()


@router.get("/snapshot", response_model=RouterSnapshot)
async def get_snapshot() -> RouterSnapshot:
    return await monitoring_engine.collect_snapshot()


@router.get("/anomalies")
async def get_anomalies() -> dict[str, list[dict[str, Any]]]:
    snapshot = await monitoring_engine.collect_snapshot()
    anomalies = await monitoring_engine.detect_anomalies(snapshot)
    return {"anomalies": anomalies}

