from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Device, TelemetryRecord
from app.db.session import get_db
from app.schemas.monitoring import TelemetryResponse, TelemetrySeriesPoint, TelemetrySeriesResponse


router = APIRouter()


@router.get("/latest", response_model=TelemetryResponse)
async def latest_telemetry(
    host: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_db),
) -> TelemetryResponse:
    query = (
        select(TelemetryRecord, Device)
        .join(Device, Device.id == TelemetryRecord.device_id)
        .order_by(TelemetryRecord.recorded_at.desc())
        .limit(1)
    )
    if host:
        query = query.where(Device.host == host)

    result = await session.execute(query)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="No telemetry available")

    telemetry, device = row
    return TelemetryResponse(
        device=device.host,
        cpu_load=telemetry.cpu_load,
        memory_usage=telemetry.memory_usage,
        latency_ms=telemetry.latency_ms,
        packet_loss=telemetry.packet_loss,
        anomalies=telemetry.anomalies,
        recorded_at=telemetry.recorded_at,
    )


@router.get("/history", response_model=TelemetrySeriesResponse)
async def telemetry_history(
    host: str = Query(..., description="RouterOS host"),
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
) -> TelemetrySeriesResponse:
    query = (
        select(TelemetryRecord)
        .join(Device, Device.id == TelemetryRecord.device_id)
        .where(Device.host == host)
        .order_by(TelemetryRecord.recorded_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    records = result.scalars().all()
    if not records:
        raise HTTPException(status_code=404, detail="No telemetry for host")

    points = [
        TelemetrySeriesPoint(
            recorded_at=item.recorded_at,
            cpu_load=item.cpu_load,
            memory_usage=item.memory_usage,
            latency_ms=item.latency_ms,
            packet_loss=item.packet_loss,
        )
        for item in records
    ]

    return TelemetrySeriesResponse(device=host, points=list(reversed(points)))
