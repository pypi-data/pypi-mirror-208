import copy
from dependency_injector.wiring import Provide, inject
import io
import json
import logging
from logging import Handler, StreamHandler
import os
from pendulum.tz import UTC
from pythonjsonlogger.jsonlogger import JsonFormatter
from tarvis.common import environ, secrets
from tarvis.common.environ import PlatformType, DeploymentType
from tarvis.common.time import datetime

# WARNING: Logging *should* be as simple and robust as possible so that when something
# unexpected happens, the path through logging should guarantee that at least the
# problem will get logged. Unfortunately, too many independent thinkers have their own
# interpretation of how to implement Python logging, so in order to get reasonably
# consistent logging across all platforms, many workarounds have been employed.


# noinspection PyUnusedLocal
def _empty_function(*args, **kwargs):
    pass


_GCP_CLIENT_CREDENTIALS_FILE = "gcp-client-logging.json"

_root_logger = logging.getLogger()
_original_logger_log = _empty_function
_gcp_extra = {}


# Class to undo a workaround for GCP's structured logging when also logging elsewhere
class CleanedStreamHandler(StreamHandler):
    def emit(self, record):
        record = copy.copy(record)
        json_fields = record.__dict__.pop("json_fields", None)
        if json_fields is not None:
            for key, value in json_fields.items():
                if key != "logging_client":
                    record.__dict__[key] = value
        super().emit(record)


class Iso8601JsonFormatter(JsonFormatter):
    def __init__(self):
        super().__init__(fmt="%(asctime)s %(levelname)s %(name)s %(message)s")

    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created, UTC)
        return ct.to_iso8601_string()


# Workaround for GCP's structured logging throwing away the extra dictionary
def _gcp_log(
    self,
    level,
    msg,
    args,
    exc_info=None,
    extra=None,
    stack_info=False,
    stacklevel=1,
):
    if _gcp_extra:
        if extra is not None:
            extra = _gcp_extra | extra
        else:
            extra = _gcp_extra
    # GCP library will log a text-only message and discard the extra structured
    # logging if the extra is not packaged in their special format
    if extra is not None:
        extra = {"json_fields": extra}
    _original_logger_log(
        self,
        level,
        msg,
        args,
        exc_info=exc_info,
        extra=extra,
        stack_info=stack_info,
        stacklevel=stacklevel,
    )


def _set_log_handler(handler: Handler) -> None:
    while _root_logger.hasHandlers():
        _root_logger.removeHandler(_root_logger.handlers[0])
    _root_logger.addHandler(handler)


def _setup_azure_logging() -> None:
    # noinspection PyPackageRequirements
    from opencensus.ext.azure.log_exporter import AzureLogHandler

    azure_instrumentation_key = secrets.get_secret("azure_instrumentation_key")
    azure_connection_string = "InstrumentationKey=" + azure_instrumentation_key
    azure_handler = AzureLogHandler(connection_string=azure_connection_string)
    _set_log_handler(azure_handler)


def _setup_gcp_logging() -> None:
    global _original_logger_log

    # noinspection PyProtectedMember
    _original_logger_log = logging.Logger._log
    logging.Logger._log = _gcp_log

    # noinspection PyPackageRequirements
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()


def _setup_json_logging() -> None:
    json_handler = StreamHandler()
    json_formatter = Iso8601JsonFormatter()
    json_handler.setFormatter(json_formatter)
    _set_log_handler(json_handler)


def _setup_client_logging() -> None:
    global _original_logger_log
    global _gcp_extra

    json_handler = CleanedStreamHandler()
    json_formatter = Iso8601JsonFormatter()
    json_handler.setFormatter(json_formatter)
    _root_logger.addHandler(json_handler)

    # noinspection PyProtectedMember
    _original_logger_log = logging.Logger._log
    logging.Logger._log = _gcp_log

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _GCP_CLIENT_CREDENTIALS_FILE

    try:
        with io.open(_GCP_CLIENT_CREDENTIALS_FILE, "r") as credentials_file:
            credentials = json.load(credentials_file)
            client_email = credentials["client_email"]
            logging_client = client_email.split("@")[0]
            _gcp_extra = {"logging_client": logging_client}
    except:
        logging.critical(f'Missing or invalid "{_GCP_CLIENT_CREDENTIALS_FILE}"')
        raise

    # noinspection PyPackageRequirements
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()


@inject
def load_config(config: dict = Provide["config"]) -> None:
    if environ.deployment in (DeploymentType.DEVELOPMENT, DeploymentType.TESTING):
        logging_config = config.get("logging")
        if logging_config is not None:
            logging_level = logging_config.get("level")
            if logging_level is not None:
                _root_logger.setLevel(logging_level)


match environ.platform:
    case PlatformType.LOCAL | PlatformType.AWS:
        _setup_json_logging()
    case PlatformType.CLIENT:
        _setup_client_logging()
    case PlatformType.AZURE:
        _setup_azure_logging()
    case PlatformType.GCP:
        _setup_gcp_logging()
    case _:
        raise Exception("Unknown platform")

match environ.deployment:
    case DeploymentType.DEVELOPMENT:
        _root_logger.setLevel(logging.NOTSET)
    case DeploymentType.TESTING:
        _root_logger.setLevel(logging.DEBUG)
    case DeploymentType.STAGING | DeploymentType.PRODUCTION:
        _root_logger.setLevel(logging.INFO)
    case _:
        raise Exception("Unknown deployment")
