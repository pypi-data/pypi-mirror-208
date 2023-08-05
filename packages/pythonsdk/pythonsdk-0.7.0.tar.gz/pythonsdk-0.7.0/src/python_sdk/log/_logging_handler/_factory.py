from python_sdk.log._logging_handler import _protocol
from python_sdk.log._logging_handler import _rotating_file
from python_sdk.log._logging_handler import _stderr
from python_sdk.log._logging_handler import _stdout

_IMPLEMENTATIONS: dict[str, type[_protocol.Handler]] = {
    _rotating_file.RotatingFile.TYPE: _rotating_file.RotatingFile,
    _stderr.STDErr.TYPE: _stderr.STDErr,
    _stdout.STDOut.TYPE: _stdout.STDOut,
}


def register_implementation(type: str, implementation: type[_protocol.Handler]) -> None:
    _IMPLEMENTATIONS[type] = implementation


def logging_handler(type: str) -> _protocol.Handler:
    if type not in _IMPLEMENTATIONS:
        raise NotImplementedError(type)
    implementation = _IMPLEMENTATIONS[type]
    return implementation()
