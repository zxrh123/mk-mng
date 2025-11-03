from datetime import datetime
from typing import List

from pydantic import BaseModel


class TelemetryResponse(BaseModel):
    device: str
    cpu_load: float
    memory_usage: float
    latency_ms: float
    packet_loss: float
    anomalies: dict
    recorded_at: datetime


class TelemetrySeriesPoint(BaseModel):
    recorded_at: datetime
    cpu_load: float
    memory_usage: float
    latency_ms: float
    packet_loss: float


class TelemetrySeriesResponse(BaseModel):
    device: str
    points: List[TelemetrySeriesPoint]
