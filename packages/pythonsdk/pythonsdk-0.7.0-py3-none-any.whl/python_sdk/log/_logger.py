import datetime
import logging

from python_sdk.log import _logging_formatter
from python_sdk.log import _logging_handler

_LOGGER: logging.Logger | None = None
_LAST_CONFIGURED: datetime.datetime | None = None


def logger() -> logging.Logger:
    from python_sdk.log._config import LogConfig

    global _LOGGER
    global _LAST_CONFIGURED

    if not _LOGGER:
        _LOGGER = _configure_logger()
    elif _LAST_CONFIGURED and _LAST_CONFIGURED != LogConfig.last_loaded_at():
        _LAST_CONFIGURED = LogConfig.last_loaded_at()
        _LOGGER = _configure_logger()

    return _LOGGER


def _configure_logger() -> logging.Logger:
    from python_sdk.log._config import LogConfig

    # now that we have a config, set up a logger as dictated by the config
    logger = logging.getLogger()

    logger.setLevel(level=LogConfig.LEVEL)

    for existing_handler in logger.handlers:
        existing_handler.flush()
        existing_handler.close()
        logger.removeHandler(hdlr=existing_handler)

    formatter = _logging_formatter.logging_formatter(
        type=LogConfig.OUTPUT_STYLE,
        include_current_log_filename=LogConfig.INCLUDE_LOG_FILENAME,
        include_function_name=LogConfig.INCLUDE_FUNCTION_NAME,
        include_line_number=LogConfig.INCLUDE_LINE_NUMBER,
        include_module_name=LogConfig.INCLUDE_MODULE_NAME,
        include_module_path=LogConfig.INCLUDE_MODULE_PATH,
        include_process_id=LogConfig.INCLUDE_PROCESS_ID,
        include_process_name=LogConfig.INCLUDE_PROCESS_NAME,
        include_thread_id=LogConfig.INCLUDE_THREAD_ID,
        include_thread_name=LogConfig.INCLUDE_THREAD_NAME,
        include_python_sdk_version=LogConfig.INCLUDE_PYTHON_SDK_VERSION,
    )
    handler = _logging_handler.logging_handler(type=LogConfig.DESTINATION)
    handler.setFormatter(fmt=formatter)
    logger.addHandler(hdlr=handler)
    return logger
