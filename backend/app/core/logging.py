"""Centralized logging configuration using Loguru."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger


def configure_logging(log_dir: Path | None = None) -> None:
    """Configure the Loguru logger for the application."""

    logger.remove()
    sink_kwargs: dict[str, Any] = {"colorize": True, "enqueue": True}
    logger.add(sys.stdout, level="INFO", **sink_kwargs)

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_dir / "app.log",
            rotation="1 week",
            retention="30 days",
            compression="zip",
            level="INFO",
            serialize=False,
            **sink_kwargs,
        )


 __all__ = ["configure_logging", "logger"]
