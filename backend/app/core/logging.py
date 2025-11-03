from loguru import logger

from .config import settings


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        serialize=False,
        colorize=True,
    )


configure_logging()
