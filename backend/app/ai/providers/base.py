"""Interfaces and utilities for AI model providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Standardised contract for AI model interactions."""

    name: str

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a completion call and return provider-specific payload."""

