import logging
import sys

from python_sdk.log import _log_levels
from python_sdk.log import _logging_formatter

logging.addLevelName(level=_log_levels.SECURITY, levelName="SECURITY")
logging.addLevelName(level=_log_levels.AUDIT, levelName="AUDIT")

# Set up a default logger, which can be used while the whole of python_sdk initializes.
_logger: logging.Logger = logging.getLogger()
_logger.setLevel("INFO")
for _existing_handler in _logger.handlers:
    _existing_handler.flush()
    _existing_handler.close()
    _logger.removeHandler(hdlr=_existing_handler)

_default_handler: logging.StreamHandler = logging.StreamHandler(stream=sys.stderr)
_formatter = _logging_formatter.logging_formatter(
    type="STRUCTURED_MACHINE_READABLE",
    include_current_log_filename=True,
    include_function_name=True,
    include_line_number=True,
    include_module_name=True,
    include_module_path=True,
    include_process_id=True,
    include_process_name=True,
    include_thread_id=True,
    include_thread_name=True,
    include_python_sdk_version=True,
)
_default_handler.setFormatter(fmt=_formatter)
_logger.addHandler(hdlr=_default_handler)
