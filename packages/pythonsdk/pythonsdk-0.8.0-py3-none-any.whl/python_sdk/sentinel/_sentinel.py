# Implementation of PEP 661
# https://www.python.org/dev/peps/pep-0661/

import inspect
import sys
import threading
import typing

_registry: dict[str, "Sentinel"] = {}
_lock = threading.Lock()


class Sentinel:
    _name: str
    _repr: str
    _module_name: str

    def __new__(cls, name: str, repr: str | None = None, module_name: str | None = None) -> "Sentinel":
        """Implements the singleton pattern."""
        final_name: str = name
        final_repr: str = repr or f"<{name}>"
        final_module_name: str = module_name or cls._get_caller_module_name()

        # Include the class's module and fully qualified name in the registry key to support sub-classing.
        registry_key = sys.intern(f"{cls.__module__}-{cls.__qualname__}-{final_module_name}-{final_name}")

        with _lock:
            sentinel: Sentinel | None = _registry.get(registry_key, None)
            if sentinel is not None:
                # For hot code reload, if the Sentinel class was re-defined, we switch it to the new class, and continue
                # using the old instance.
                if sentinel.__class__ is not cls:
                    sentinel.__class__ = cls

                return sentinel

            # No existing qualified sentinel found in registry, so let's create one.
            sentinel = super().__new__(cls)
            sentinel._name = final_name
            sentinel._repr = final_repr
            sentinel._module_name = final_module_name

            return _registry.setdefault(registry_key, sentinel)

    def __repr__(self) -> str:
        return self._repr

    def __bool__(self) -> bool:
        # As per PEP 661, Sentinel instances are truthy by default
        return True

    def __getnewargs__(self) -> typing.Tuple[str, str, str]:
        # Get arguments for the __new__ method, for pickle serialization.
        # In combination with magic in the overriden __new__() method,
        # that allows to avoid constructing duplicates when un-pickling the object.
        return self._name, self._repr, self._module_name

    def __reduce__(self) -> typing.Tuple[typing.Type["Sentinel"], typing.Tuple[str, str, str]]:
        return self.__class__, (self._name, self._repr, self._module_name)

    @classmethod
    def _get_caller_module_name(cls) -> str:
        # Walk over the call stack, and stop as soon as we leave this (_sentinel) module.
        frame = inspect.currentframe()
        while frame:
            module_name: str = frame.f_globals["__name__"]

            if module_name != __name__:
                return module_name

            frame = frame.f_back

        # Normally the code should never reach this point.
        # It may be only the case when stack inspection is not available (Jython, IronPython)
        # See alternative implementation:
        # https://github.com/taleinat/python-stdlib-sentinels/blob/9fdf9628d7bf010f0a66c72b717802c715c7d564/sentinels/sentinels.py#L104
        raise RuntimeError("Could not find caller module name.")
