from dependency_injector.wiring import Provide, inject
import json
from tarvis.common import environ
from tarvis.common.environ import PlatformType
from threading import Lock

_lock = Lock()
_secret_cache = {}
_gcp_secret_manager_client = None


@inject
def get_secret_remap(secret_name: str, config: dict = Provide["config"]) -> str:
    remaps = config.get("secret_remaps")
    if remaps:
        secret_name = remaps.get(secret_name, secret_name)
    return secret_name


@inject
def get_config_secret(secret_name: str, config: dict = Provide["config"]) -> any:
    secrets = config.get("secrets")
    if secrets is None:
        raise Exception("No secrets defined in the configuration.")
    return secrets.get(secret_name)


def _get_gcp_secret(secret_name: str) -> str:
    global _gcp_secret_manager_client
    if _gcp_secret_manager_client is None:
        # noinspection PyPackageRequirements
        from google.cloud import secretmanager

        _gcp_secret_manager_client = secretmanager.SecretManagerServiceClient()

    secret_path = _gcp_secret_manager_client.secret_version_path(
        environ.get_gcp_project_id(), secret_name, "latest"
    )
    response = _gcp_secret_manager_client.access_secret_version(name=secret_path)
    secret = response.payload.data.decode("UTF-8")
    return secret


def get_secret(secret_name: str, cache: bool = True, decode_json: bool = False) -> any:
    with _lock:
        if cache:
            secret = _secret_cache.get(secret_name)
            if secret is not None:
                return secret

        remapped_secret_name = get_secret_remap(secret_name)
        match environ.platform:
            # Secrets cannot be retrieved from configuration when running on a cloud
            # platform. They must be properly secured on the cloud platforms.
            case PlatformType.LOCAL | PlatformType.CLIENT:
                secret = get_config_secret(remapped_secret_name)
            case PlatformType.AWS:
                secret = NotImplementedError()
            case PlatformType.AZURE:
                secret = NotImplementedError()
            case PlatformType.GCP:
                secret = _get_gcp_secret(remapped_secret_name)
            case _:
                raise Exception("Unknown platform")

        if secret is None:
            raise Exception(f'Secret not found: "{secret_name}".')

        if decode_json and isinstance(secret, str):
            secret = json.loads(secret)

        if cache:
            _secret_cache[secret_name] = secret

        return secret
