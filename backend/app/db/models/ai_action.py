import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActionStatus(str, Enum):
    PLANNED = "planned"
    DRY_RUN = "dry_run"
    EXECUTED = "executed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class AIAction(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("device.id", ondelete="SET NULL"), nullable=True)
    intent: Mapped[str] = mapped_column(String(255))
    script: Mapped[str] = mapped_column(String)
    reasoning: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(32), default=ActionStatus.PLANNED.value)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)

    device = relationship("Device", backref="actions")
