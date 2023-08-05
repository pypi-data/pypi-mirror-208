import typing

from python_sdk import config


# TODO(lijok): something to prevent this from being configured using secrets
class SecretsConfig(config.Config, option_prefix="PYTHON_SDK_SECRETS_"):
    ENGINE: str = config.Option(default="AWS_SECRETS_MANAGER")


# TODO(lijok): extract BOTOCORE_CONFIG to top level so users dont have to supply a dict
class AWSSecretsEngineConfig(
    config.Config,
    name="AWS Secrets Engine Config",
    description="""Configuration for the AWS Secrets Engines such as AWS Secrets Manager and
    AWS Systems Manager Parameter Store.
    """,
    option_prefix="PYTHON_SDK_SECRETS_ENGINE_AWS_",
):
    ACCESS_KEY_ID: str | None = config.Option()
    SECRET_ACCESS_KEY: str | None = config.Option()
    SESSION_TOKEN: str | None = config.Option()
    REGION_NAME: str | None = config.Option()
    API_VERSION: str | None = config.Option()
    USE_SSL: bool = config.Option(default=True)
    VERIFY: bool = config.Option(default=True)
    ENDPOINT_URL: str | None = config.Option()
    BOTOCORE_CONFIG: dict[str, typing.Any] | None = config.Option(
        description="See https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html"
    )
