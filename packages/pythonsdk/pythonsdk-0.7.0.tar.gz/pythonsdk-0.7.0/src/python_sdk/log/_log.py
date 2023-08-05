import logging
import sys
import types
import typing

from python_sdk.log import _context
from python_sdk.log import _log_levels
from python_sdk.log import _logger


def _log(
    level: int,
    message: typing.Any,
    exception: BaseException
    | tuple[type[BaseException], BaseException, types.TracebackType]
    | tuple[None, None, None]
    | None = None,
    _stack_level: int = 2,
    **kwargs: typing.Any,
) -> None:
    logger = _logger.logger()

    # root_logger.log does this check itself.
    # However, just below this, we're doing a potentially expensive dictionary merge.
    # So, as a simple performance optimization, we run this check before we do the dictionary merge.
    if not logger.isEnabledFor(level=level):
        return

    data = _context.get_context() | kwargs
    logger.log(level=level, msg=message, exc_info=exception, stacklevel=_stack_level, extra={"context": data})


def critical(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=logging.CRITICAL, message=message, _stack_level=3, **kwargs)


def error(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=logging.ERROR, message=message, _stack_level=3, **kwargs)


def warning(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=logging.WARNING, message=message, _stack_level=3, **kwargs)


def info(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=logging.INFO, message=message, _stack_level=3, **kwargs)


def debug(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=logging.DEBUG, message=message, _stack_level=3, **kwargs)


def security(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=_log_levels.SECURITY, message=message, _stack_level=3, **kwargs)


def audit(message: typing.Any, **kwargs: typing.Any) -> None:
    _log(level=_log_levels.AUDIT, message=message, _stack_level=3, **kwargs)


def exception(message: typing.Any, exception: BaseException | None = None, **kwargs: typing.Any) -> None:
    _log(level=logging.ERROR, message=message, exception=exception or sys.exc_info(), _stack_level=3, **kwargs)
