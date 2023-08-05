import contextvars
import copy
import types
import typing

_DEFAULT_CONTEXT_VALUE_FACTORY: typing.Callable[[], dict[str, typing.Any]] = dict
_CONTEXT: contextvars.ContextVar[dict[str, typing.Any]] = contextvars.ContextVar(
    "_PYTHON_SDK_LOGGING_CONTEXT", default=_DEFAULT_CONTEXT_VALUE_FACTORY()
)


def get_context() -> dict[str, typing.Any]:
    return copy.copy(_CONTEXT.get())


def set_context(value: dict[str, typing.Any]) -> None:
    _CONTEXT.set(value)


class bind:
    local_context: dict[str, typing.Any]

    def __init__(self, **kwargs: typing.Any) -> None:
        self.local_context = kwargs
        set_context(get_context() | kwargs)

    def __enter__(self) -> None:
        return

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        unbind(*self.local_context.keys())


def unbind(*args: str) -> None:
    set_context({key: val for key, val in _CONTEXT.get().items() if key not in args})


def unbind_all() -> None:
    set_context(_DEFAULT_CONTEXT_VALUE_FACTORY())
