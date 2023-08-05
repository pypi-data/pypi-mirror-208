import io
import logging
import typing

from python_sdk.secrets._config import AWSSecretsEngineConfig
from python_sdk.secrets._secrets_engine import _protocol


class AWSSystemsManagerParameterStore:
    TYPE: str = "AWS_SYSTEMS_MANAGER_PARAMETER_STORE"

    def __init__(self) -> None:
        import boto3  # type: ignore
        import botocore.client  # type: ignore

        self.client: botocore.client.BaseClient = boto3.Session().client(
            service_name="ssm",
            aws_access_key_id=AWSSecretsEngineConfig.ACCESS_KEY_ID,
            aws_secret_access_key=AWSSecretsEngineConfig.SECRET_ACCESS_KEY,
            aws_session_token=AWSSecretsEngineConfig.SESSION_TOKEN,
            region_name=AWSSecretsEngineConfig.REGION_NAME,
            api_version=AWSSecretsEngineConfig.API_VERSION,
            use_ssl=AWSSecretsEngineConfig.USE_SSL,
            verify=AWSSecretsEngineConfig.VERIFY,
            endpoint_url=AWSSecretsEngineConfig.ENDPOINT_URL,
            config=AWSSecretsEngineConfig.BOTOCORE_CONFIG,
        )

    def _processed_key(self, key: str) -> str:
        return "/" + key.removeprefix("/")  # ensure prefixed with /

    def autocomplete_key(self, key: str) -> list[str]:
        return [
            parameter["Name"]
            for parameter in self.client.get_paginator("describe_parameters")
            .paginate()
            .build_full_result()["Parameters"]
            if parameter["Name"].startswith(self._processed_key(key=key))
        ]

    def get_secret_value(self, key: str) -> typing.IO[bytes]:
        import botocore.exceptions

        logging.debug(f"Getting secret. {key=}")
        try:
            response = self.client.get_parameter(Name=self._processed_key(key=key), WithDecryption=True)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                raise _protocol.DoesNotExist(e.response["Error"]["Message"]) from e
            elif e.response["Error"]["Code"] == "NotAuthorizedException":
                raise _protocol.Unauthorized(e.response["Error"]["Message"]) from e
            raise

        value: typing.IO[bytes] = io.BytesIO()
        value.write(response["Parameter"]["Value"].encode("utf-8"))
        value.seek(0)
        return value

    def set_secret_value(self, key: str, value: typing.IO[bytes]) -> None:
        self.client.put_parameter(Name=self._processed_key(key=key), Value=value.read().decode("utf-8"), Overwrite=True)
