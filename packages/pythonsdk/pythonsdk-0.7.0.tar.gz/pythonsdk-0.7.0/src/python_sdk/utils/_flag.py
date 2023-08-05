class BoolFlag:
    def __init__(self, value: bool = False) -> None:
        self._value = value

    def set(self) -> None:
        self._value = True

    def unset(self) -> None:
        self._value = False

    def __bool__(self) -> bool:
        return self._value

    def __repr__(self) -> str:
        return repr(self._value)

    def __str__(self) -> str:
        return str(self._value)
