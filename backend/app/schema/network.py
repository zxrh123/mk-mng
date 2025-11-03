"""Pydantic models for network monitoring data."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class InterfaceMetric(BaseModel):
    name: str
    rx_rate: float
    tx_rate: float
    rx_packets: int
    tx_packets: int
    status: str


class NetworkMetrics(BaseModel):
    cpu_load: float
    memory_usage: float
    latency_ms: float
    packet_loss: float
    interfaces: list[InterfaceMetric]
    updated_at: datetime


class RouterSnapshot(BaseModel):
    router_identifier: str
    metrics: NetworkMetrics


class Alert(BaseModel):
    severity: str
    title: str
    description: str
    created_at: datetime
    metadata: dict[str, Any]

