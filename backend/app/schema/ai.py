"""Pydantic models for AI interactions."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AICommandRequest(BaseModel):
    conversation_id: str | None = None
    actor: str = Field(default="operator", description="Origin of the request")
    message: str = Field(min_length=1, description="Natural language instruction")
    context: dict[str, Any] | None = None


class AIPlanStep(BaseModel):
    description: str
    order: int
    command_preview: str | None = None


class AIExecutionPlan(BaseModel):
    intent: str
    confidence: float
    steps: list[AIPlanStep]
    requires_approval: bool = False


class AIScript(BaseModel):
    language: str = "routeros"
    contents: str
    safe: bool = True


class AICommandResponse(BaseModel):
    plan: AIExecutionPlan
    script: AIScript | None = None
    auto_execute: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIExecutionResult(BaseModel):
    decision_id: str
    executed: bool
    started_at: datetime
    completed_at: datetime
    result: dict[str, Any]

