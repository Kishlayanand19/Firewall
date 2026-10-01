import re
import structlog

logger = structlog.get_logger()

_SECRET_PATTERNS = re.compile(
    r"(sk-[a-zA-Z0-9_-]{10,}|"
    r"Bearer\s+[a-zA-Z0-9._-]+|"
    r"postgresql(\+asyncpg)?://[^\s]+|"
    r"redis://[^\s]+)",
    re.IGNORECASE,
)


def _redact(message: str) -> str:
    return _SECRET_PATTERNS.sub("[REDACTED]", message)


def safe_log_exception(event: str, exc: BaseException, **kwargs) -> None:
    """Log errors without leaking secrets or full stack traces to log consumers."""
    logger.error(
        event,
        error_type=type(exc).__name__,
        error_message=_redact(str(exc)[:200]),
        **kwargs,
    )
