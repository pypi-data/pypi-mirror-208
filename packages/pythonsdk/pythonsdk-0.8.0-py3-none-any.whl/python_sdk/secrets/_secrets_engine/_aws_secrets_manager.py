import io
import logging
import typing

from python_sdk.secrets._config import AWSSecretsEngineConfig
from python_sdk.secrets._secrets_engine import _protocol


class AWSSecretsManager:
    TYPE: str = "AWS_SECRETS_MANAGER"

    def __init__(self) -> None:
        import boto3  # type: ignore
        import botocore.client  # type: ignore

        self.client: botocore.client.BaseClient = boto3.Session().client(
            service_name="secretsmanager",
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
        return key.removeprefix("/")

    def autocomplete_key(self, key: str) -> list[str]:
        filters = []
        if self._processed_key(key=key):
            filters.append({"Key": "name", "Values": [self._processed_key(key=key)]})
        secrets = self.client.list_secrets(
            IncludePlannedDeletion=False, MaxResults=100, Filters=filters, SortOrder="desc"
        )
        return [secret["Name"] for secret in secrets["SecretList"]]

    def get_secret_value(self, key: str) -> typing.IO[bytes]:
        import botocore.exceptions

        logging.debug(f"Getting secret. {key=}")
        try:
            response = self.client.get_secret_value(SecretId=self._processed_key(key=key))
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise _protocol.DoesNotExist(e.response["Error"]["Message"]) from e
            elif e.response["Error"]["Code"] == "NotAuthorizedException":
                raise _protocol.Unauthorized(e.response["Error"]["Message"]) from e
            raise

        value: typing.IO[bytes] = io.BytesIO()
        if "SecretBinary" in response:
            value.write(response["SecretBinary"])
        else:
            value.write(response["SecretString"].encode("utf-8"))
        value.seek(0)
        return value

    def set_secret_value(self, key: str, value: typing.IO[bytes]) -> None:
        import botocore.exceptions

        try:
            try:
                self.client.put_secret_value(
                    SecretId=self._processed_key(key=key), SecretString=value.read().decode("utf-8")
                )
            except UnicodeDecodeError:
                self.client.put_secret_value(SecretId=self._processed_key(key=key), SecretBinary=value.read())
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise _protocol.DoesNotExist(e.response["Error"]["Message"]) from e
            elif e.response["Error"]["Code"] == "NotAuthorizedException":
                raise _protocol.Unauthorized(e.response["Error"]["Message"]) from e
            raise
