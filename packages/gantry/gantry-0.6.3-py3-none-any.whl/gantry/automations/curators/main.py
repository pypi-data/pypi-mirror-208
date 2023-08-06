import functools
import inspect
import logging
import os
from typing import Optional
from urllib.parse import urlparse

from gantry.api_client import APIClient
from gantry.automations.curators import globals
from gantry.automations.curators.curators import CuratorClient
from gantry.const import PROD_API_URL
from gantry.exceptions import ClientNotInitialized

logger_obj = logging.getLogger(__name__)


def _curators_alias(func):
    """Decorator for CuratorClient functions, exposed in main.py"""
    doc = "Alias for :meth:`gantry.automations.curators.curators.CuratorClient.{}`".format(
        func.__name__
    )
    signature = inspect.signature(getattr(CuratorClient, func.__name__))
    orig_doc = inspect.getdoc(getattr(CuratorClient, func.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)
    signature = signature.replace(parameters=tuple(signature.parameters.values())[1:])

    func.__doc__ = doc
    func.__signature__ = signature

    # This decorator also checks that the _CURATOR_CLIENT
    # has been initialized
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if globals._CURATOR_CLIENT is None:
            raise ClientNotInitialized()

        return func(*args, **kwargs)

    return wrapper


def _init(
    api_key: Optional[str] = None,
):
    backend = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)
    parsed_origin = urlparse(backend)
    if parsed_origin.scheme not in ("http", "https"):
        raise ValueError(
            "Invalid backend. http or https backends " + "supported. Got {}".format(backend)
        )

    api_key = os.environ.get("GANTRY_API_KEY") if api_key is None else api_key

    if not api_key:
        raise ValueError(
            """
            No API key provided. Please pass the api_key parameter or set the GANTRY_API_KEY
            environment variable.
            """
        )

    api_client = APIClient(backend, api_key)
    # instantiated curators need a client, too
    globals._API_CLIENT = api_client  # type: ignore
    # this client has special methods for querying all curators
    globals._CURATOR_CLIENT = CuratorClient(api_client)  # type: ignore

    if not globals._CURATOR_CLIENT.ping():  # type: ignore
        logger_obj.warning(
            "Gantry services not reachable. Check provided URL "
            f"[{backend}] is pointing to the correct address"
        )
        return

    if not globals._CURATOR_CLIENT.ready():  # type: ignore
        logger_obj.warning("Gantry services won't receive traffic. Check if API Key is valid")


@_curators_alias
def get_all_curators(*args, **kwargs):
    return globals._CURATOR_CLIENT.get_all_curators(*args, **kwargs)  # type: ignore


@_curators_alias
def get_curator(*args, **kwargs):
    return globals._CURATOR_CLIENT.get_curator(*args, **kwargs)  # type: ignore


@_curators_alias
def list_curators(*args, **kwargs):
    return globals._CURATOR_CLIENT.list_curators(*args, **kwargs)  # type: ignore
