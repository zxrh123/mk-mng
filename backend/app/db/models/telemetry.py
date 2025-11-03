import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TelemetryRecord(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("device.id", ondelete="CASCADE"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    cpu_load: Mapped[float] = mapped_column(Float)
    memory_usage: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    voltage: Mapped[float] = mapped_column(Float, nullable=True)
    interfaces: Mapped[dict] = mapped_column(JSON, default=dict)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)
    packet_loss: Mapped[float] = mapped_column(Float, nullable=True)
    anomalies: Mapped[dict] = mapped_column(JSON, default=dict)

    device = relationship("Device", backref="telemetry")
