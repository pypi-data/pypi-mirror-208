import base64
import pathlib
import typing


class Base64EncodedString(str):
    """
    Uses UTF-8 encoding.
    """

    encoding: str = "utf-8"

    def __new__(cls, string: str) -> "Base64EncodedString":
        if not string:
            raise ValueError()
        base64.b64decode(string, validate=True).decode(cls.encoding)  # check it can be decoded
        return super().__new__(cls, string)

    @property
    def decoded(self) -> str:
        return base64.b64decode(self, validate=True).decode(self.encoding)


# TODO: base64encodedpemcert
# TODO: base64encodeddercert


# TODO: This does not include literals
ConfigValueType: typing.TypeAlias = (
    str
    | int
    | float
    | bool
    | dict[str, typing.Any]
    | Base64EncodedString
    | pathlib.Path
    | list[str]
    | list[int]
    | list[float]
    | list[Base64EncodedString]
    | list[pathlib.Path]
    | None
)
