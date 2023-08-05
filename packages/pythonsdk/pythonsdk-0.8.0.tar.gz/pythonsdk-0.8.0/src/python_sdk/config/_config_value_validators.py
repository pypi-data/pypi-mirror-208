import os
import pathlib
import re
import typing

if typing.TYPE_CHECKING:
    from python_sdk.config import _config_option


class ConfigValueValidationError(Exception):
    """Config Value does not pass validation."""

    ...


class ConfigValueValidator(typing.Protocol):
    name: str
    description: str

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: typing.Any,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Config value does not pass validation.
        """
        ...


class ValidateFileExists:
    name: str = "Validate File Exists"
    description: str = "Validates that the file at a given path exists."

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: pathlib.Path,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Path does not exist or is not a directory.
        """
        if not config_value.exists():
            raise ConfigValueValidationError(f"File at {config_value} does not exist.")
        if not config_value.is_file():
            raise ConfigValueValidationError(f"{config_value} not a file.")


class ValidateDirectoryExists:
    name: str = "Validate Directory Exists"
    description: str = "Validates that the directory at a given path exists."

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: pathlib.Path,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Path does not exist or is not a directory.
        """
        if not config_value.exists():
            raise ConfigValueValidationError(f"Directory at {config_value} does not exist.")
        if not config_value.is_dir():
            raise ConfigValueValidationError(f"{config_value} not a directory.")


class ValidatePathIsReadable:
    name: str = "Validate Path is Readable"
    description: str = "Validates that a given path is readable."

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: pathlib.Path,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Path is not readable.
        """
        path_to_evaluate = config_value if config_value.exists() else config_value.parent
        if not os.access(path_to_evaluate, os.R_OK):
            raise ConfigValueValidationError(f"{config_value} is not readable.")


class ValidatePathIsWritable:
    name: str = "Validate Path is Writable"
    description: str = "Validates that a given path is writeable."

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: pathlib.Path,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Path is not writeable.
        """
        path_to_evaluate = config_value if config_value.exists() else config_value.parent
        if not os.access(path_to_evaluate, os.W_OK):
            raise ConfigValueValidationError(f"{config_value} is not writeable")


class ValidatePathIsExecutable:
    name: str = "Validate Path is Executable"
    description: str = "Validates that a given path is executable."

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: pathlib.Path,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Path is not executable.
        """
        path_to_evaluate = config_value if config_value.exists() else config_value.parent
        if not os.access(path_to_evaluate, os.EX_OK):
            raise ConfigValueValidationError(f"{config_value} is not executable")


class ValidateFileType:
    name: str = "Validate File Type"
    description: str = "Validates that the file at a given path is of set file type."

    file_type: str

    def __init__(self, file_type: str) -> None:
        self.file_type = file_type if file_type[0] == "." else f".{file_type}"

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: pathlib.Path,
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Path is not of correct file type.
        """
        if "".join(config_value.suffixes) != self.file_type:
            raise ConfigValueValidationError(f"{config_value} is not {self.file_type}")


class ValidateRegexMatch:
    name: str = "Validate Regex Match"
    description: str = """
    Validates that the passed value(s) match a regex pattern.
    This can be used with strings and lists of strings.
    """

    pattern: re.Pattern

    def __init__(self, pattern: str) -> None:
        self.pattern = re.compile(pattern=pattern)

    def __call__(
        self,
        config_option_name: str,
        config_option: "_config_option.ConfigOption",
        config_value: str | list[str],
    ) -> None:
        """
        Raises:
            ConfigValueValidationError: Value does not match regex pattern.
        """
        values_to_validate = config_value if isinstance(config_value, list) else [config_value]
        for value in values_to_validate:
            if not self.pattern.match(value):
                raise ConfigValueValidationError(f"Value does not match regex pattern {self.pattern.pattern}")
