import typing

import boto3  # type: ignore


class DoesNotExist(Exception):
    """Secret does not exist."""


class Unauthorized(Exception):
    """Not authorized to access secret."""


class SecretsEngine(typing.Protocol):
    TYPE: str

    def autocomplete_key(self, key: str) -> list[str]:
        ...

    def get_secret_value(self, key: str) -> typing.IO[bytes]:
        """
        Raises:
            DoesNotExist: Secret does not exist.
            Unauthorized: Not authorized to access secret.
        """
        ...

    def set_secret_value(self, key: str, value: typing.IO[bytes]) -> None:
        """
        Raises:
            DoesNotExist: Secret does not exist.
            Unauthorized: Not authorized to access secret.
        """
        ...
