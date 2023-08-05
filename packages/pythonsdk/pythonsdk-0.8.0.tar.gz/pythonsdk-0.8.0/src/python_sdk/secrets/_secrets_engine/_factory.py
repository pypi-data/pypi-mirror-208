from python_sdk.secrets._secrets_engine import _aws_s3
from python_sdk.secrets._secrets_engine import _aws_secrets_manager
from python_sdk.secrets._secrets_engine import _aws_systems_manager_parameter_store
from python_sdk.secrets._secrets_engine import _protocol

_IMPLEMENTATIONS: dict[str, type[_protocol.SecretsEngine]] = {
    _aws_systems_manager_parameter_store.AWSSystemsManagerParameterStore.TYPE: _aws_systems_manager_parameter_store.AWSSystemsManagerParameterStore,
    _aws_secrets_manager.AWSSecretsManager.TYPE: _aws_secrets_manager.AWSSecretsManager,
    _aws_s3.AWSS3.TYPE: _aws_s3.AWSS3,
}


def register_implementation(type: str, implementation: type[_protocol.SecretsEngine]) -> None:
    _IMPLEMENTATIONS[type] = implementation


def secrets_engine(type: str) -> _protocol.SecretsEngine:
    if type not in _IMPLEMENTATIONS:
        raise NotImplementedError(type)
    implementation = _IMPLEMENTATIONS[type]
    return implementation()
