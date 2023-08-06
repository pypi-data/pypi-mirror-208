import os
import warnings
from typing import Optional
from urllib.parse import urlparse

from gantry.api_client import APIClient
from gantry.const import PROD_API_URL
from gantry.query import globals
from gantry.query.client import GantryQuery
from gantry.query.globals import _query_alias, validate_init


def init(api_key: Optional[str] = None):
    """
    Initialize the Query functionality. Initialization should happen before any Query call.

    WARNING: this method will be deprecated soon, Use global `init` to intialize query
    functionality, as shown below.

    Example:

    .. code-block:: python

       import gantry.query as gquery

       gquery.init(api_key="foobar")

    Args:
        api_key (str): The API key. Users can fetch the API key from the dashboard.
    """
    warnings.warn(
        "This initialization method will be deprecated soon, use global gantry.init instead"
    )
    _init(api_key)


def _init(api_key: Optional[str] = None):
    backend = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)
    parsed_origin = urlparse(backend)
    if parsed_origin.scheme not in ("http", "https"):
        raise ValueError(
            "Invalid backend. http or https backends " + "supported. Got {}".format(backend)
        )

    # Check environment if api_key is not provided
    api_key = os.environ.get("GANTRY_API_KEY") if api_key is None else api_key

    if not api_key:
        raise ValueError(
            """
            No API key provided. Please pass the api_key parameter or set the GANTRY_API_KEY
            environment variable.
            """
        )

    api_client = APIClient(backend, api_key)
    globals._Query = GantryQuery(api_client)  # type: ignore[union-attr]


@_query_alias
def list_applications(*args, **kwargs):
    validate_init()
    return globals._Query.list_applications(*args, **kwargs)  # type: ignore[union-attr]


@_query_alias
def create_view(*args, **kwargs):
    validate_init()
    return globals._Query.create_view(*args, **kwargs)  # type: ignore[union-attr,return-value]


@_query_alias
def list_application_versions(*args, **kwargs):
    validate_init()
    return globals._Query.list_application_versions(*args, **kwargs)  # type: ignore[union-attr]


@_query_alias
def list_application_environments(*args, **kwargs):
    validate_init()
    return globals._Query.list_application_environments(*args, **kwargs)  # type: ignore[union-attr]


@_query_alias
def query(*args, **kwargs):
    validate_init()
    return globals._Query.query(*args, **kwargs)  # type: ignore[union-attr]


@_query_alias
def list_application_views(*args, **kwargs):
    validate_init()
    return globals._Query.list_application_views(*args, **kwargs)  # type: ignore[union-attr]


@_query_alias
def list_application_batches(*args, **kwargs):
    validate_init()
    return globals._Query.list_application_batches(*args, **kwargs)  # type: ignore[union-attr]


@_query_alias
def print_application_info(*args, **kwargs):
    validate_init()
    return globals._Query.print_application_info(*args, **kwargs)  # type: ignore[union-attr]
