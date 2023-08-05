from python_sdk.log._logging_formatter import _protocol
from python_sdk.log._logging_formatter import _structured_human_readable
from python_sdk.log._logging_formatter import _structured_machine_readable

_IMPLEMENTATIONS: dict[str, type[_protocol.Formatter]] = {
    _structured_human_readable.StructuredHumanReadable.TYPE: _structured_human_readable.StructuredHumanReadable,
    _structured_machine_readable.StructuredMachineReadable.TYPE: _structured_machine_readable.StructuredMachineReadable,
}


def register_implementation(type: str, implementation: type[_protocol.Formatter]) -> None:
    _IMPLEMENTATIONS[type] = implementation


def logging_formatter(
    type: str,
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
) -> _protocol.Formatter:
    if type not in _IMPLEMENTATIONS:
        raise NotImplementedError(type)
    implementation = _IMPLEMENTATIONS[type]
    return implementation(
        include_current_log_filename=include_current_log_filename,
        include_function_name=include_function_name,
        include_line_number=include_line_number,
        include_module_name=include_module_name,
        include_module_path=include_module_path,
        include_process_id=include_process_id,
        include_process_name=include_process_name,
        include_thread_id=include_thread_id,
        include_thread_name=include_thread_name,
        include_python_sdk_version=include_python_sdk_version,
    )
