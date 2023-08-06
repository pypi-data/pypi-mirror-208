import os
from typing import Optional

from gantry.alerts.main import _init as alerts_init
from gantry.applications.main import _init as applications_init
from gantry.applications.core import Application, Run
from gantry.applications.llm import CompletionApplication, VersionDetails
from gantry.applications.main import (
    archive_application,
    create_application,
    delete_application,
    get_application,
)
from gantry.automations.curators.main import _init as curators_init
from gantry.automations.main import _init as automations_init
from gantry.dataset.main import _init as dataset_init
from gantry.logger.main import LOGGING_LEVEL_T
from gantry.logger.main import _init as logger_init
from gantry.logger.main import (
    get_client,
    log,
    log_file,
    log_from_data_connector,
    log_record,
    log_records,
    ping,
    ready,
    setup_logger,
)
from gantry.logger.utils import JoinKey
from gantry.query.main import _init as query_init
from gantry.utils import compute_feedback_id
from gantry.version import __version__ as _version

__all__ = [
    "init",
    "Application",
    "CompletionApplication",
    "VersionDetails",
    "Run",
    "log",
    "log_file",
    "log_from_data_connector",
    "log_record",
    "log_records",
    "ping",
    "ready",
    "get_client",
    "setup_logger",
    "compute_feedback_id",
    "JoinKey",
    "_version",
    "create_application",
    "get_application",
    "delete_application",
    "archive_application",
]


def init(
    api_key: Optional[str] = None,
    logging_level: Optional[LOGGING_LEVEL_T] = None,
    environment: Optional[str] = None,
    send_in_background: Optional[bool] = None,
):
    """
    Initialize gantry services. Initialization should happen before any interaction with Gantry
    (whether is ingesting data or performing queries).

    After initialization, the SDK logging module, query module and alerts module
    will be enabled.

    Example:

    .. code-block:: python

       import gantry
       gantry.init(api_key="foobar")


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
    api_key = _get_api_key(api_key)
    logger_init(api_key, logging_level, environment, send_in_background)
    query_init(api_key)
    alerts_init(api_key)
    curators_init(api_key)
    dataset_init(api_key)
    applications_init(api_key)
    automations_init(api_key)


def _get_api_key(api_key: Optional[str] = None) -> str:
    """
    Get API key from environment if not already supplied. Raise exception if not found.
    """
    api_key = api_key or os.environ.get("GANTRY_API_KEY")
    if api_key is None:
        raise ValueError(
            "Please provide an API key to initialize Gantry SDK. API key can be provided"
            + "as parameter to init methods or by setting env var GANTRY_API_KEY"
        )
    return api_key
