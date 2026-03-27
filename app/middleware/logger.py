import sys

from loguru import logger


def setup_logger() -> None:
    """Configure loguru to write colored INFO+ logs to stderr."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO",
        colorize=True,
    )
