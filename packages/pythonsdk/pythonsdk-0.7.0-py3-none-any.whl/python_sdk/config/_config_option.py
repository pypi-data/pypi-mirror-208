import copy
import functools
import typing

from python_sdk import sentinel
from python_sdk.config import _optional_type
from python_sdk.config import _string_decoder

if typing.TYPE_CHECKING:
    from python_sdk.config import _config_value_types
    from python_sdk.config import _config_value_validators

Unset: sentinel.Sentinel = sentinel.Sentinel("Unset")


# TODO?: Rename to Option
class ConfigOption:
    name: str
    prefix: str
    description: str
    datatype: type["_config_value_types.ConfigValueType"]
    default: typing.Union["_config_value_types.ConfigValueType", sentinel.Sentinel, None]
    validators: list["_config_value_validators.ConfigValueValidator"]
    hardcoded: bool
    is_sensitive: bool
    reload_compatible: bool
    _value: typing.Union["_config_value_types.ConfigValueType", sentinel.Sentinel, None]
    _encoded_value: str | sentinel.Sentinel

    SECRET_REFERENCE_TOKEN: str = "secret:"

    def __init__(
        self,
        name: str,
        prefix: str,
        datatype: type["_config_value_types.ConfigValueType"],
        description: str = "",
        default: typing.Union[
            "_config_value_types.ConfigValueType",
            typing.Callable[[], "_config_value_types.ConfigValueType"],
            sentinel.Sentinel,
        ] = Unset,
        validators: list["_config_value_validators.ConfigValueValidator"] | None = None,
        is_sensitive: bool = False,
        reload_compatible: bool = False,
    ) -> None:
        self.name = name
        self.prefix = prefix
        self.description = description
        self.datatype = datatype
        self.default = default() if callable(default) else default
        self.validators = validators or []
        self.hardcoded = False
        self.is_sensitive = is_sensitive
        self.reload_compatbile = reload_compatible
        self._value = Unset
        self._encoded_value = Unset

        if not _string_decoder.type_is_supported(data_type=self._real_datatype):
            raise ValueError(f"{self.datatype} not supported.")

        if self.has_default and self.default is not None:
            self._run_validators(config_value=self.default)

    @property
    def fully_qualified_name(self) -> str:
        return f"{self.prefix}{self.name}"

    @property
    def is_optional(self) -> bool:
        return _optional_type.is_optional_type(data_type=self.datatype)

    @property
    def has_default(self) -> bool:
        return self.default is not Unset

    @property
    def _real_datatype(self) -> type:
        return (
            _optional_type.get_type_in_optional_type(data_type=self.datatype)
            if _optional_type.is_optional_type(data_type=self.datatype)
            else self.datatype
        )

    @property
    def value(self) -> "_config_value_types.ConfigValueType":
        if self._value is not Unset:
            return self._value
        if self.default is not Unset:
            return self.default
        raise RuntimeError(
            "Value not set at access time. This indicates a bug in python-sdk. Please raise a bug report."
        )

    @value.setter
    def value(self, maybe_encoded_value: typing.Union["_config_value_types.ConfigValueType", str, None]) -> None:
        if self.hardcoded:
            return

        if maybe_encoded_value is None:
            # Value is being set to None. This is valid so long as this option is optional.
            if not self.is_optional:
                raise ValueError(f"{self.fully_qualified_name} is not optional.")
            self._value = None
            self._encoded_value = Unset
            return
        elif isinstance(maybe_encoded_value, str):
            # Value may be encoded, let's decode it
            value = _string_decoder.decode_string(string=maybe_encoded_value, data_type=self._real_datatype)
        else:
            # Caller provided a decoded value, lets make a copy
            # Note that we do not validate that the decoded value is of correct type. This is intentional.
            # Only the client may be setting this to a decoded value. We choose to trust the client won't shoot
            # themselves in the foot, and in turn, we avoid the significant complexity of validating data types.
            value = copy.deepcopy(maybe_encoded_value)

        self._run_validators(config_value=value)

        self._value = value
        self._encoded_value = maybe_encoded_value

    def hardcode_value(self, value: "_config_value_types.ConfigValueType") -> None:
        self.hardcoded = False
        self.value = value
        self.hardcoded = True

    def _run_validators(self, config_value: "_config_value_types.ConfigValueType") -> None:
        for validator in self.validators:
            validator(config_option_name=self.name, config_option=self, config_value=config_value)


class PartialConfigOption(functools.partial[ConfigOption]):
    ...


# To satisfy type checkers, we type that we return typing.Any in this function.
# That way, type checkers are happy with a class that looks like the following:
#
# class AppConfig(Config):
#     LOGLEVEL: str = Option(default="INFO", description="Logs below this level will not be emitted.")
def Option(
    default: typing.Union[
        "_config_value_types.ConfigValueType",
        typing.Callable[[], typing.Union["_config_value_types.ConfigValueType"]],
        sentinel.Sentinel,
    ] = Unset,
    description: str = "",
    is_sensitive: bool = False,
    validators: list["_config_value_validators.ConfigValueValidator"] | None = None,
    reload_compatible: bool = True,
) -> typing.Any:
    return PartialConfigOption(
        ConfigOption,
        default=default,
        description=description,
        is_sensitive=is_sensitive,
        validators=validators,
        reload_compatible=reload_compatible,
    )
