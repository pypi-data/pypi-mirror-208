import dataclasses
import datetime
import logging
import pathlib
import typing

import python_sdk
from python_sdk import sentinel
from python_sdk.config import _config_option
from python_sdk.config import _config_sources
from python_sdk.config import _config_value_types
from python_sdk.config import _config_value_validators
from python_sdk.config import _flags

if typing.TYPE_CHECKING:
    from python_sdk.config import _config_validators

Unset: sentinel.Sentinel = sentinel.Sentinel("Unset")


# TODO: get_documentation function at module level which pulls out docs from all configuration objects
# TODO: registry of tuples of all Config classes and all of their config options, so we can fetch documentation for it
# and also append to it manually options which are only available through plain environment variables, e.g., in this
# module


class _ConfigMetaclass(type):
    def __str__(cls) -> str:
        # TODO
        return super().__str__()

    def __repr__(cls) -> str:
        # TODO
        return super().__repr__()

    def __getattribute__(cls, item: str) -> typing.Any:
        attribute = super().__getattribute__(item)
        if not isinstance(attribute, _config_option.ConfigOption):
            return attribute

        if cls.meta.lazy_load_config and not cls.meta.loaded:
            cls._load_config()
            attribute = super().__getattribute__(item)

        if _flags.ENABLE_ON_ACCESS_CONFIG_RELOADING:
            cls.reload_config()
            attribute = super().__getattribute__(item)

        return attribute.value


@dataclasses.dataclass
class _ConfigMeta:
    name: str
    description: str
    option_prefix: str
    config_sources: list["_config_sources.ConfigSource"]
    lazy_load_config: bool
    validators: list["_config_validators.ConfigValidator"]
    last_loaded_at: datetime.datetime | None = None
    _loaded: bool = False

    def __init__(
        self,
        name: str,
        description: str,
        option_prefix: str,
        config_sources: list["_config_sources.ConfigSource"],
        lazy_load_config: bool,
        validators: list["_config_validators.ConfigValidator"],
    ) -> None:
        self.name = name
        self.description = description
        self.option_prefix = option_prefix
        self.config_sources = config_sources
        self.lazy_load_config = lazy_load_config
        self.validators = validators
        self.last_loaded_at = None
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded

    @loaded.setter
    def loaded(self, value: bool) -> None:
        self.last_loaded_at = datetime.datetime.now(tz=datetime.timezone.utc)
        self._loaded = value


class Config(metaclass=_ConfigMetaclass):
    meta: _ConfigMeta

    # TODO: config cache
    # TODO: how do we allow ops to configure some of these options?
    # TODO?: remove `config` prefixes and suffixes
    def __init_subclass__(
        cls,
        name: str = "Application Configuration",
        description: str = "",
        option_prefix: str = "",
        config_sources: list["_config_sources.ConfigSource"] | None = None,
        lazy_load_config: bool = False,
        validators: list["_config_validators.ConfigValidator"] | None = None,  # TODO: this or function
    ) -> None:
        super().__init_subclass__()

        # Ensure user is not trying to use a configuration option with the name of "meta".
        # We will be overriding it below to store the configuration of this class in.
        if "meta" in cls.__dict__ or ("meta" in cls.__annotations__ and cls.__annotations__["meta"] != _ConfigMeta):
            raise ValueError("`meta` is a reserved keyword and cannot be used as a configuration option.")

        options: dict[str, _config_option.PartialConfigOption] = {
            k: v for k, v in cls.__dict__.items() if isinstance(v, _config_option.PartialConfigOption)
        }

        # Raise if we find any untyped _config_option.ConfigOptions.
        for option_name in options:
            if option_name not in cls.__annotations__:
                raise TypeError(f"{option_name} is untyped. Please add a type hint.")

        # Finish instantiation of _config_option.ConfigOptions instances with attributes that the user cannot supply,
        # but are now known.
        for option_name, option in options.items():
            # We can assume here that the annotation is available, because of the typing checks we did earlier.
            complete_option: _config_option.ConfigOption = option(
                name=option_name,
                prefix=option_prefix,
                datatype=cls.__annotations__[option_name],
            )
            setattr(cls, option_name, complete_option)

        # We store this data in a container rather than on the Config itself to prevent name collisions.
        cls.meta = _ConfigMeta(
            name=name,
            description=description,
            option_prefix=option_prefix,
            config_sources=config_sources or _get_config_sources(),
            lazy_load_config=lazy_load_config,
            validators=validators or [],
        )

        if not cls.meta.lazy_load_config:
            cls._load_config()

    def __init__(self) -> None:
        # TODO: can we make this work with instantiation?
        raise TypeError("Config classes cannot be instantiated.")

    @classmethod
    def _load_config(cls) -> None:
        config_data: dict[str, str] = {}
        for config_source in reversed(cls.meta.config_sources):
            # Start sourcing config data from provided config sources, backwards.
            # Top of the list in cls.meta.config_sources takes precedence.
            config_data |= {key.lower(): value for key, value in config_source(prefix=cls.meta.option_prefix).items()}

        config_options = [val for val in cls.__dict__.values() if isinstance(val, _config_option.ConfigOption)]

        for config_option in config_options:
            if config_option.fully_qualified_name.lower() in config_data:
                encoded_config_value: str = config_data.pop(config_option.fully_qualified_name.lower())
                config_option.value = encoded_config_value
            elif config_option.has_default:
                continue
            elif config_option.is_optional:
                config_option.value = None
            else:
                raise ValueError(
                    f"Required config option {config_option.fully_qualified_name} with no default was not set."
                )

        # TODO: Temporarily commented out 'cause can be very disruptive. Need to think of a way to toggle this.
        # if (
        #     cls.meta.option_prefix
        # ):  # If no option_prefix, all env vars would be pulled in, and we would warn for each one.
        #     for unused_config_option in config_data:
        #         logging.warning(f"Config option {unused_config_option} not supported by {cls.meta.name}.")

        cls.meta.loaded = True
        cls.validate()
        cls.post_load_hook()

    @classmethod
    def validate(cls) -> None:
        for validator in cls.meta.validators:
            validator(config=cls)

    @classmethod
    def post_load_hook(cls) -> None:
        pass

    @classmethod
    def reload_config(cls) -> None:
        cls._load_config()

    @classmethod
    def save_to_file(cls, file: pathlib.Path) -> None:
        # TODO
        raise NotImplementedError()

    @classmethod
    def get_documentation(cls) -> str:
        # TODO
        raise NotImplementedError()

    @classmethod
    def get_config_option(cls, option: str) -> _config_option.ConfigOption:
        config_option: _config_option.ConfigOption = object.__getattribute__(cls, option)
        return config_option

    @classmethod
    def set_config_value(cls, option: str, value: _config_value_types.ConfigValueType) -> None:
        config_option = cls.get_config_option(option=option)
        config_option.value = value
        cls.validate()
        cls.post_load_hook()

    @classmethod
    def hardcode_config_value(cls, option: str, value: _config_value_types.ConfigValueType) -> None:
        config_option = cls.get_config_option(option=option)
        config_option.hardcode_value(value=value)
        cls.validate()
        cls.post_load_hook()

    @classmethod
    def last_loaded_at(cls) -> datetime.datetime | None:
        return cls.meta.last_loaded_at

    @classmethod
    def last_load_contained_changes(cls) -> bool:
        # TODO: Implement this
        return False


# TODO: How do we allow custom config sources if SOURCE is a literal?
class ConfigSourcesConfig(
    Config,
    name="Config Sources Config",
    description="""
    Configuration used by config sources to configure their behaviour, particularly around document sourcing.
    """,
    option_prefix="PYTHON_SDK_CONFIG_",
    config_sources=[_config_sources.EnvironmentVariables()],
):
    SOURCE: typing.Literal[
        "ENVIRONMENT_VARIABLES",
        "LOCAL_FILE",
        "S3_FILE",
        "AWS_SECRETS_MANAGER_SECRET",
        "AWS_PARAMETER_STORE_DOCUMENT",
        "REMOTE_HTTP_FILE",
    ] = _config_option.Option(
        default="ENVIRONMENT_VARIABLES",
        description="Where configurations will be sourced from.",
    )
    SOURCE_LOCAL_FILE_FILEPATH: pathlib.Path | None = _config_option.Option(
        description="""
        Filepath for the LOCAL_FILE config source. Required when PYTHON_SDK_CONFIG_SOURCE is set to LOCAL_FILE.
        The file must exist and be readable by the running process.
        """,
        validators=[_config_value_validators.ValidateFileExists(), _config_value_validators.ValidatePathIsReadable()],
    )
    SOURCE_REMOTE_HTTP_FILE_URL: str | None = _config_option.Option(
        description="""
        URL for the REMOTE_HTTP_FILE config source. Required when PYTHON_SDK_CONFIG_SOURCE is set to REMOTE_HTTP_FILE.
        """
    )
    SOURCE_REMOTE_HTTP_FILE_TIMEOUT: int = _config_option.Option(
        default=10, description="Timeout for the REMOTE_HTTP_FILE config source."
    )
    SOURCE_REMOTE_HTTP_FILE_AUTHORIZATION_HEADER: str | None = _config_option.Option(
        description="Authorization header to send along when accessing the REMOTE_HTTP_FILE config source."
    )
    SOURCE_REMOTE_HTTP_FILE_USER_AGENT_STRING: str = _config_option.Option(
        default=f"python-sdk-{python_sdk.__version__}",
        description="User-Agent string to send along when accessing the REMOTE_HTTP_FILE config source.",
    )

    @classmethod
    def validate(cls) -> None:
        if cls.SOURCE == "LOCAL_FILE" and not cls.SOURCE_LOCAL_FILE_FILEPATH:
            raise _config_validators.ConfigValidationError(
                "PYTHON_SDK_CONFIG_SOURCE_LOCAL_FILE_FILEPATH must be set when PYTHON_SDK_CONFIG_SOURCE is LOCAL_FILE."
            )
        if cls.SOURCE == "REMOTE_HTTP_FILE" and not cls.SOURCE_REMOTE_HTTP_FILE_URL:
            raise _config_validators.ConfigValidationError(
                "PYTHON_SDK_CONFIG_SOURCE_REMOTE_HTTP_FILE_URL must be set when PYTHON_SDK_CONFIG_SOURCE is "
                "REMOTE_HTTP_FILE."
            )


def _get_config_sources() -> list["_config_sources.ConfigSource"]:
    if ConfigSourcesConfig.SOURCE == "ENVIRONMENT_VARIABLES":
        return [_config_sources.EnvironmentVariables()]
    elif ConfigSourcesConfig.SOURCE == "LOCAL_FILE":
        assert ConfigSourcesConfig.SOURCE_LOCAL_FILE_FILEPATH is not None
        return [_config_sources.LocalFile(filepath=ConfigSourcesConfig.SOURCE_LOCAL_FILE_FILEPATH)]
    elif ConfigSourcesConfig.SOURCE == "REMOTE_HTTP_FILE":
        assert ConfigSourcesConfig.SOURCE_REMOTE_HTTP_FILE_URL is not None
        return [
            _config_sources.RemoteHTTPFile(
                url=ConfigSourcesConfig.SOURCE_REMOTE_HTTP_FILE_URL,
                timeout=ConfigSourcesConfig.SOURCE_REMOTE_HTTP_FILE_TIMEOUT,
                authorization_header=ConfigSourcesConfig.SOURCE_REMOTE_HTTP_FILE_AUTHORIZATION_HEADER,
                user_agent_string=ConfigSourcesConfig.SOURCE_REMOTE_HTTP_FILE_USER_AGENT_STRING,
            )
        ]
    raise NotImplementedError()
