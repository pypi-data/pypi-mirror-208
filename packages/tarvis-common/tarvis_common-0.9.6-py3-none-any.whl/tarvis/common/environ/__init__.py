import asyncio
from enum import Enum
import os
import sys
from threading import Lock


class PlatformType(Enum):
    LOCAL = 0
    CLIENT = 1
    GCP = 2
    AWS = 3
    AZURE = 4


class DeploymentType(Enum):
    DEVELOPMENT = 0
    TESTING = 1
    STAGING = 2
    PRODUCTION = 3


def _get_environ_enum(environ_name: str, enum_class):
    environ_value = os.environ.get(environ_name)
    if environ_value is None:
        # Default is not allowed because an absence might cause a misconfiguration.
        # For example, production could accidentally default down to development.
        raise Exception(
            "The environmental variable '" + environ_name + "' is not defined."
        )
    try:
        result = enum_class[environ_value]
    finally:
        pass
    if result is None:
        raise Exception(
            "The environmental variable '"
            + environ_name
            + "' value of '"
            + environ_value
            + "' is not recognized."
        )
    return result


_lock = Lock()
platform = _get_environ_enum("TARVIS_PLATFORM", PlatformType)
deployment = _get_environ_enum("TARVIS_DEPLOYMENT", DeploymentType)

_GCP_PROJECT_ID_META_URL = (
    "http://metadata.google.internal/computeMetadata/v1/project/project-id"
)
_gcp_project_id = None

# TODO: Remove when https://bugs.python.org/issue39232 is fixed
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_gcp_project_id() -> str:
    global _gcp_project_id
    if _gcp_project_id is not None:
        return _gcp_project_id
    else:
        with _lock:
            if _gcp_project_id is None:
                from urllib import request

                project_id_request = request.Request(_GCP_PROJECT_ID_META_URL)
                project_id_request.add_header("Metadata-Flavor", "Google")
                _gcp_project_id = request.urlopen(project_id_request).read().decode()
            return _gcp_project_id
