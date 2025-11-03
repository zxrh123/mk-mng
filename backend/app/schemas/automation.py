from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AutomationRequest(BaseModel):
    host: str = Field(..., description="RouterOS host or IP address")
    objective: str = Field(..., description="High-level description of the desired outcome")
    auto_execute: Optional[bool] = Field(default=None, description="Override global auto execute policy")


class AutomationResponse(BaseModel):
    message: str
    executed: bool
    result: Dict[str, Any]
