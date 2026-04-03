import logging
import sys


def setup_logging() -> None:
    """
    Configure root logger with sensible defaults for the application.
    INFO level in production, DEBUG in development.
    """
    log_level = logging.DEBUG if _is_development() else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def _is_development() -> bool:
    """Check if running in development environment."""
    try:
        from app.core.config import settings
        return settings.environment == "development"
    except Exception:
        return True
