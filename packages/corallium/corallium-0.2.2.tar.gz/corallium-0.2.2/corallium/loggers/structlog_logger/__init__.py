"""Only importable when `structlog` is installed."""

try:
    from ._structlog_logger import structlog_logger
except ModuleNotFoundError as exc:  # pragma: no cover
    msg = 'Install "structlog" in order to use the "structlog_logger"'
    raise RuntimeError(msg) from exc
