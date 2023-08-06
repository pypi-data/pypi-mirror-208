import functools
import inspect
import logging
import os
from distutils.util import strtobool
from typing import Optional, Tuple, cast

import colorama
from typeguard import typechecked
from typing_extensions import Literal

from gantry.const import DEFAULT_ENV, PROD_API_URL
from gantry.exceptions import ClientNotInitialized
from gantry.logger.client import Gantry
from gantry.logger.stores import APILogStore

colorama.init(autoreset=True)
logger_obj = logging.getLogger(__name__)
logger_obj.addHandler(logging.NullHandler())

_CLIENT: Optional[Gantry] = None


def _client_alias(f):
    doc = "Alias for :meth:`gantry.logger.client.Gantry.{}`".format(f.__name__)
    signature = inspect.signature(getattr(Gantry, f.__name__))
    orig_doc = inspect.getdoc(getattr(Gantry, f.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)
    signature = signature.replace(parameters=tuple(signature.parameters.values())[1:])

    f.__doc__ = doc
    f.__signature__ = signature

    # This decorator also checks that the _CLIENT
    # has been initialized
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _CLIENT is None:
            raise ClientNotInitialized()

        return f(*args, **kwargs)

    return wrapper


LOGGING_LEVEL_T = Literal["DEBUG", "INFO", "WARNING", "CRITICAL", "ERROR"]


@typechecked
def _resolve_params(
    api_key: Optional[str] = None,
    logging_level: Optional[LOGGING_LEVEL_T] = None,
    environment: Optional[str] = None,
    send_in_background: Optional[bool] = None,
) -> Tuple[str, str, LOGGING_LEVEL_T, str, bool, bool]:
    api_key = api_key or os.environ.get("GANTRY_API_KEY")
    if api_key is None:
        raise ValueError("logger was not initialized with API Key")

    logs_location = cast(str, os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL))
    logging_level = cast(
        LOGGING_LEVEL_T, logging_level or os.environ.get("GANTRY_LOGGING_LEVEL", "INFO")
    )
    environment = cast(str, environment or os.environ.get("GANTRY_ENVIRONMENT", DEFAULT_ENV))

    # TODO: use urlparse to grab the scheme instead
    if not (logs_location.startswith("http://") or logs_location.startswith("https://")):
        logger_obj.error("Currently only HTTP logs location supported")
        raise ValueError(
            "logger was not initialized with http endpoint. Only HTTP logs locations supported."
        )

    bypass_firehose = bool(strtobool(os.environ.get("GANTRY_BYPASS_FIREHOSE", "false")))

    if send_in_background is None:
        if "GANTRY_SEND_IN_BACKGROUND" in os.environ:
            send_in_background = bool(strtobool(os.environ["GANTRY_SEND_IN_BACKGROUND"]))
        else:
            # Set sync behavior in case app is running in a lambda (scenario in which
            # we can't start a thread).
            # https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
            send_in_background = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None

    return api_key, logs_location, logging_level, environment, bypass_firehose, send_in_background


def _init(
    api_key: Optional[str] = None,
    logging_level: Optional[LOGGING_LEVEL_T] = None,
    environment: Optional[str] = None,
    send_in_background: Optional[bool] = None,
):
    """
    Initialize the logger. Initialization should happen before submitting any data to Gantry.

    Args:
        api_key (optional, str): The Gantry API Key. You can also set this parameter by setting
            the env variable GANTRY_API_KEY.
        logging_level (optional, str): Set logging level for Gantry system logging.
            You can also set this parameter by setting the env variable GANTRY_LOGGING_LEVEL.
            Options are: DEBUG, INFO, WARNING, CRITICAL or ERROR.
            If not specified, it defaults to INFO.
        environment (optional, str): Set the value for the environment label attached
            to data instrumented. You can also set this parameter by setting the env
            variable GANTRY_ENVIRONMENT. If not provided, it defaults to "dev".
            The environment is essentially a tag attached to data. To override
            this value later, you can set an 'env' tag in the tags parameters
            in the ingestion methods.
        send_in_background (optional, bool): set whether Gantry logging methods should
            run synchronously or not. You can also set this value by setting
            the env variable GANTRY_SEND_IN_BACKGROUND.
            If not provided, it defaults to True unless running in an AWS lambda.
    """
    (
        api_key,
        logs_location,
        logging_level,
        environment,
        bypass_firehose,
        send_in_background,
    ) = _resolve_params(api_key, logging_level, environment, send_in_background)

    global _CLIENT

    log_store = APILogStore(
        location=logs_location,
        api_key=api_key,
        bypass_firehose=bypass_firehose,
        send_in_background=send_in_background,
    )
    _CLIENT = Gantry(log_store, environment, logging_level)

    logger_obj.debug("Gantry logger initialized")

    if not _CLIENT.ping():
        logger_obj.warning(
            "Gantry services not reachable. Check provided URL "
            f"[{logs_location}] is pointing to the correct address"
        )
        return

    if not _CLIENT.ready():
        logger_obj.warning("Gantry services won't receive traffic. Check if API Key is valid")


@_client_alias
def ping():
    return _CLIENT.ping()


@_client_alias
def ready():
    return _CLIENT.ready()


@_client_alias
def log_file(*args, **kwargs):
    return _CLIENT.log_file(*args, **kwargs)  # type: ignore[union-attr]


@_client_alias
def log_from_data_connector(*args, **kwargs):
    return _CLIENT.log_from_data_connector(*args, **kwargs)  # type: ignore[union-attr]


@_client_alias
def log_record(*args, **kwargs):
    return _CLIENT.log_record(*args, **kwargs)  # type: ignore[union-attr]


@_client_alias
def log_records(*args, **kwargs):
    return _CLIENT.log_records(*args, **kwargs)  # type: ignore[union-attr]


def get_client():
    return _CLIENT


def setup_logger(level: str = "INFO"):
    return Gantry.setup_logger(level)


@_client_alias
def log(*args, **kwargs):
    return _CLIENT.log(*args, **kwargs)  # type: ignore[union-attr]


@_client_alias
def generate_records(*args, **kwargs):
    return _CLIENT.generate_records(*args, **kwargs)  # type: ignore[union-attr]


@_client_alias
def _upload_data_as_batch(*args, **kwargs):
    return _CLIENT._upload_data_as_batch(*args, **kwargs)  # type: ignore[union-attr]
