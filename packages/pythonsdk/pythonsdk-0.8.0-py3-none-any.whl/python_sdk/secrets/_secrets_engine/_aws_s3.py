import io
import logging
import typing

from python_sdk.secrets._config import AWSSecretsEngineConfig
from python_sdk.secrets._secrets_engine import _protocol


class AWSS3:
    TYPE: str = "AWS_S3"

    def __init__(self) -> None:
        import boto3  # type: ignore
        import botocore.client  # type: ignore

        self.client: botocore.client.BaseClient = boto3.Session().client(
            service_name="s3",
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

    def _split_key(self, key: str) -> tuple[str, str]:
        bucket = key.split("/")[0]
        key = key.removeprefix(bucket).removeprefix("/")
        return bucket, key

    def _processed_key(self, key: str) -> str:
        return key.removeprefix("/")

    def autocomplete_key(self, key: str) -> list[str]:
        import botocore.exceptions

        bucket, key = self._split_key(key=self._processed_key(key=key))

        if not bucket:
            return []

        try:
            return [
                f"{bucket}/{content['Key']}"
                for page in self.client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=key)
                for content in page.get("Contents", [])
            ]
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                return []
            raise

    def get_secret_value(self, key: str) -> typing.IO[bytes]:
        value: typing.IO[bytes] = io.BytesIO()
        bucket, key = self._split_key(key=self._processed_key(key=key))
        self.client.download_fileobj(Bucket=bucket, Key=key, Fileobj=value)
        value.seek(0)
        return value

    def set_secret_value(self, key: str, value: typing.IO[bytes]) -> None:
        bucket, key = self._split_key(key=self._processed_key(key=key))
        self.client.upload_fileobj(Bucket=bucket, Key=key, Fileobj=value)
