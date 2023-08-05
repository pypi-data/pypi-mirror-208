import os
import pathlib
import typing
import urllib.error
import urllib.request

import python_sdk

# TODO: support custom CA's and proxies


class ConfigSource(typing.Protocol):
    """
    Config source protocol.
    Implementing classes must only concern themselves with reading in the configuration and presenting it as a plain,
    flat, dictionary. Implementing classes should not attempt any config value manipulation or even normalization
    (e.g. stripping blank characters), unless said manipulation is to remove artifacts specific to the configuration
    source. Implementing classes should be casing-agnostic.
    """

    name: str
    description: str

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            PermissionError: Could not read from config source.
            ConnectionError: Could not connect to a networked config source.
            ValueError: Could not parse the config file, which may be malformed.
        """
        ...


class StaticDictionary:
    name: str = "Static Dictionary"
    description: str = "Sources configuration from a static dictionary."
    dictionary: dict[str, str]

    def __init__(self, dictionary: dict[str, str]) -> None:
        self.dictionary = dictionary

    def __call__(self, prefix: str) -> dict[str, str]:
        return {key: val for key, val in self.dictionary.items() if key.lower().startswith(prefix.lower())}


class EnvironmentVariables:
    name: str = "Environment Variables"
    description: str = "Sources configuration from the environment variables."

    def __call__(self, prefix: str) -> dict[str, str]:
        return StaticDictionary(dictionary=dict(os.environ))(prefix=prefix)


class FileObject:
    name: str = "File Object"
    description: str = """
    Sources configuration from a given file object.
    The file object is interpreted as a plain text document.
    The document must use `=` as a key value separator and `\n` as a new line separator.

    Example valid document:
    ```
    DB_USER=admin
    DB_PORT=5432
    ```
    """
    key_value_separator: str = "="
    line_separator: str = "\n"
    file: typing.TextIO

    def __init__(self, file: typing.TextIO) -> None:
        self.file = file

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            ValueError: Could not parse the config file, which may be malformed.
        """
        configuration = {}

        for line in self.file.read().split(self.line_separator):
            if self.key_value_separator not in line:
                raise ValueError(f"No key value separator `{self.key_value_separator}` in config line: {line}")
            key, val = line.split(self.key_value_separator, 1)
            configuration[key] = val

        return StaticDictionary(dictionary=dict(os.environ))(prefix=prefix)


class LocalFile:
    name: str = "Local File"
    description: str = """
    Sources configuration from a given local file.
    The file is interpreted as a plain text document.
    The document must use `=` as a key value separator and `\n` as a new line separator.

    Example valid document:
    ```
    DB_USER=admin
    DB_PORT=5432
    ```
    """
    key_value_separator: str = "="
    line_separator: str = "\n"
    filepath: pathlib.Path

    def __init__(self, filepath: pathlib.Path) -> None:
        self.filepath: pathlib.Path = filepath

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            PermissionError: Could not read from config source.
            ValueError: Could not parse the config file, which may be malformed.
        """
        with self.filepath.open(mode="r", encoding="utf-8") as f:
            return FileObject(file=f)(prefix=prefix)


class S3File:
    name: str = "S3 File"
    description: str = """
    Sources configuration from an S3 (Simple Storage Service) compatible API.
    The file is interpreted as a plain text document.
    The document must use `=` as a key value separator and `\n` as a new line separator.

    Example valid document:
    ```
    DB_USER=admin
    DB_PORT=5432
    ```
    """

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            PermissionError: Could not read from config source.
            ConnectionError: Could not connect to a networked config source.
            ValueError: Could not parse the config file, which may be malformed.
        """
        return {}


class AWSSecretsManagerSecret:
    name: str = "AWS Secrets Manager secret"
    description: str = """
    Sources configuration from an AWS Secrets Manager secret.
    The secret is interpreted as a plain text document.
    The secret must use `=` as a key value separator and `\n` as a new line separator.

    Example valid document:
    ```
    DB_USER=admin
    DB_PORT=5432
    ```
    """

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            PermissionError: Could not read from config source.
            ConnectionError: Could not connect to a networked config source.
            ValueError: Could not parse the config file, which may be malformed.
        """
        return {}


class AWSParameterStoreDocument:
    name: str = "AWS Parameter Store document"
    description: str = """
    Sources configuration from an AWS Parameter Store document.
    The file is interpreted as a plain text document.
    The document must use `=` as a key value separator and `\n` as a new line separator.

    Example valid document:
    ```
    DB_USER=admin
    DB_PORT=5432
    ```
    """

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            PermissionError: Could not read from config source.
            ConnectionError: Could not connect to a networked config source.
            ValueError: Could not parse the config file, which may be malformed.
        """
        return {}


class RemoteHTTPFile:
    name: str = "Remote HTTP File"
    description: str = """
    Sources configuration from a remote HTTP server at a given URL.
    The contents are interpreted as a plain text document.
    The document must use `=` as a key value separator and `\n` as a new line separator.

    Example valid document:
    ```
    DB_USER=admin
    DB_PORT=5432
    ```
    """
    url: str
    timeout: int
    authorization_header: str | None
    user_agent_string: str

    def __init__(
        self,
        url: str,
        timeout: int = 10,
        authorization_header: str | None = None,
        user_agent_string: str = f"python-sdk-{python_sdk.__version__}",
    ) -> None:
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("RemoteHTTPFile only supports http and https endpoints.")
        self.url = url
        self.timeout = timeout
        self.authorization_header = authorization_header
        self.user_agent_string = user_agent_string

    def __call__(self, prefix: str) -> dict[str, str]:
        """
        Raises:
            PermissionError: Could not read from config source.
            ConnectionError: Could not connect to a networked config source.
            ValueError: Could not parse the config file, which may be malformed.
        """
        try:
            request = urllib.request.urlopen(url=self.url, timeout=self.timeout)
        except urllib.error.HTTPError as e:
            if 400 <= e.code <= 500:
                raise PermissionError(f"Received status code {e.code} {e.reason} when connecting to {self.url}.") from e
            raise ConnectionError(f"Received status code {e.code} {e.reason} when connecting to {self.url}.") from e
        except urllib.error.URLError as e:
            raise ConnectionError(f"Could not connect to {self.url}. Malformed URL?") from e

        return FileObject(file=request)(prefix=prefix)
