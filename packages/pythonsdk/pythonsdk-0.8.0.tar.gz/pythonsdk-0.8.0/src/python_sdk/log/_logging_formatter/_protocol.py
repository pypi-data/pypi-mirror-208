import logging
import typing


class Formatter(typing.Protocol):
    TYPE: str

    include_current_log_filename: bool
    include_function_name: bool
    include_line_number: bool
    include_module_name: bool
    include_module_path: bool
    include_process_id: bool
    include_process_name: bool
    include_thread_id: bool
    include_thread_name: bool
    include_python_sdk_version: bool

    def __init__(
        self,
        include_current_log_filename: bool,
        include_function_name: bool,
        include_line_number: bool,
        include_module_name: bool,
        include_module_path: bool,
        include_process_id: bool,
        include_process_name: bool,
        include_thread_id: bool,
        include_thread_name: bool,
        include_python_sdk_version: bool,
    ) -> None:
        ...

    def format(self, record: logging.LogRecord) -> str:
        ...
