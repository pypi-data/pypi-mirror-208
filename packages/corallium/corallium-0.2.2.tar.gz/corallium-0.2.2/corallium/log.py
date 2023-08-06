"""Log."""

import logging
from functools import partial
from typing import runtime_checkable

from beartype import beartype
from beartype.typing import Any, Optional, Protocol
from rich.console import Console

from .loggers.rich_printer import rich_printer
from .loggers.styles import STYLES, Styles

DEF_LEVEL = logging.ERROR


@runtime_checkable
class LogCallable(Protocol):
    """Defined the kwargs accepted for a delegated task."""

    @beartype
    def __call__(
        self,
        message: str,
        *,
        is_header: bool,
        _this_level: int,
        _is_text: bool,
    ) -> Any:
        """Type-checked arguments."""


class _LogSingleton:
    """Store pointer to log function."""

    _logger: Optional[LogCallable] = None
    _log_level: int = DEF_LEVEL

    @beartype
    def set_logger(
        self,
        *,
        log_level: int,
        logger: Optional[LogCallable] = None,
        _console: Optional[Console] = None,
        _styles: Optional[Styles] = None,
        **kwargs: Any,
    ) -> LogCallable:
        """Set the internal logger instance."""
        if not (_logger := logger or self._logger):
            _logger = partial(rich_printer, _console=_console or Console(), _styles=_styles or STYLES)
        self._logger = partial(_logger, **kwargs)
        self._log_level = log_level
        return self._logger

    @beartype
    def log(self, *args: Any, _this_level: int, is_header: bool = False, _is_text: bool = False, **kwargs: Any) -> None:
        """Delegate the arguments to the logger if this level above the threshold."""
        if _this_level < self._log_level:
            return
        # Ensure logger is configured
        _logger = self._logger or self.set_logger(log_level=self._log_level)
        _logger(*args, _this_level=_this_level, is_header=is_header, _is_text=_is_text, **kwargs)


_LOG_SINGLETON = _LogSingleton()


class _Logger:

    @beartype
    def text(self, message: str, *, is_header: bool = False, **kwargs: Any) -> None:
        """Print the content without a leading timestamp.

        If writing to a file or not natively supported by the logger, will appear in the logs as level info.

        """
        self.info(message, **{'_is_text': True, 'is_header': is_header, **kwargs})

    @beartype
    def text_debug(self, message: str, *, is_header: bool = False, **kwargs: Any) -> None:
        """Variation on text that will appear as a debug log if not supported."""
        self.debug(message, **{'_is_text': True, 'is_header': is_header, **kwargs})

    @beartype
    def debug(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.DEBUG, **kwargs)

    @beartype
    def info(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.INFO, **kwargs)

    @beartype
    def warning(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.WARNING, **kwargs)

    @beartype
    def error(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.ERROR, **kwargs)

    @beartype
    def exception(self, message: str, **kwargs: Any) -> None:
        _LOG_SINGLETON.log(message, _this_level=logging.CRITICAL, **kwargs)


@beartype
def configure_logger(*, log_level: int = DEF_LEVEL, logger: Optional[LogCallable] = None, **kwargs: Any) -> None:
    """Configure the global log level or replace the logger."""
    _LOG_SINGLETON.set_logger(logger=logger, log_level=log_level, **kwargs)


@beartype
def get_logger() -> _Logger:
    """Retrieve global logger."""
    return _Logger()


logger = get_logger()
