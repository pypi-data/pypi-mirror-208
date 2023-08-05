import typing

from python_sdk.secrets._config import AWSSecretsEngineConfig as AWSSecretsEngineConfig
from python_sdk.secrets._config import SecretsConfig as SecretsConfig
from python_sdk.secrets._secrets_engine import DoesNotExist as DoesNotExist
from python_sdk.secrets._secrets_engine import Unauthorized as Unauthorized
from python_sdk.secrets._secrets_engine import register_implementation as register_implementation
from python_sdk.secrets._secrets_engine import secrets_engine as secrets_engine


def autocomplete_key(key: str) -> list[str]:
    return secrets_engine(type=SecretsConfig.ENGINE).autocomplete_key(key=key)


def get_secret_value(key: str) -> typing.IO[bytes]:
    return secrets_engine(type=SecretsConfig.ENGINE).get_secret_value(key=key)


def set_secret_value(key: str, value: typing.IO[bytes]) -> None:
    return secrets_engine(type=SecretsConfig.ENGINE).set_secret_value(key=key, value=value)
