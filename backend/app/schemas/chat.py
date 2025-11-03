from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Unique chat session identifier")
    message: str = Field(..., description="User message in natural language")
    host: Optional[str] = Field(default=None, description="Target RouterOS host")


class ChatMessageResponse(BaseModel):
    message: str
    metadata: Dict[str, Any]
