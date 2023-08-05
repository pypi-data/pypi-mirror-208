import pathlib
import typing

from python_sdk import config


class LogConfig(config.Config, option_prefix="PYTHON_SDK_LOG_"):
    LEVEL: typing.Literal["DEBUG", "INFO", "SECURITY", "AUDIT", "WARNING", "ERROR", "CRITICAL"] = config.Option(
        default="INFO"
    )
    OUTPUT_STYLE: str = config.Option(default="STRUCTURED_MACHINE_READABLE")
    DESTINATION: str = config.Option(default="STDERR")
    DESTINATION_ROTATING_FILE_PATH: pathlib.Path | None = config.Option(validators=[config.ValidatePathIsWritable()])
    DESTINATION_ROTATING_FILE_MAX_SIZE_BYTES: int = config.Option(default=1073741824)
    DESTINATION_ROTATING_FILE_MAX_NUMBER_OF_FILES: int = config.Option(default=10)
    INCLUDE_LOG_FILENAME: bool = config.Option(default=False)
    INCLUDE_FUNCTION_NAME: bool = config.Option(default=True)
    INCLUDE_LINE_NUMBER: bool = config.Option(default=True)
    INCLUDE_MODULE_NAME: bool = config.Option(default=True)
    INCLUDE_MODULE_PATH: bool = config.Option(default=True)
    INCLUDE_PROCESS_ID: bool = config.Option(default=False)
    INCLUDE_PROCESS_NAME: bool = config.Option(default=False)
    INCLUDE_THREAD_ID: bool = config.Option(default=False)
    INCLUDE_THREAD_NAME: bool = config.Option(default=False)
    INCLUDE_PYTHON_SDK_VERSION: bool = config.Option(default=False)

    @classmethod
    def configure_logging(self) -> None:
        # TODO: Temporary hack for the test suite. Remove this.
        from python_sdk.log import _logger

        _logger._LOGGER = None
        _logger.logger()
