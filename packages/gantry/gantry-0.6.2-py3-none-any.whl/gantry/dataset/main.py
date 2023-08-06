import functools
import inspect
import logging
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from gantry.api_client import APIClient
from gantry.const import PROD_API_URL
from gantry.dataset.client import GantryDatasetClient
from gantry.exceptions import ClientNotInitialized

_DATASET: Optional[GantryDatasetClient] = None
logger_obj = logging.getLogger(__name__)


def _dataset_client_alias(f):
    doc = "Alias for :meth:`gantry.dataset.client.GantryDatasetClient.{}`".format(f.__name__)
    signature = inspect.signature(getattr(GantryDatasetClient, f.__name__))
    orig_doc = inspect.getdoc(getattr(GantryDatasetClient, f.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)
    signature = signature.replace(parameters=tuple(signature.parameters.values())[1:])

    f.__doc__ = doc
    f.__signature__ = signature

    # This decorator also checks that the _CLIENT
    # has been initialized
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _DATASET is None:
            raise ClientNotInitialized()

        return f(*args, **kwargs)

    return wrapper


def _init(
    api_key: Optional[str] = None,
):
    """
    Initialize the dataset functionality. Initialization should happen before any dataset operation.

    Example:

    .. code-block:: python

       import gantry.dataset as gdataset

       gdataset.init(api_key="foobar")

    Args:
        api_key (str): The API key. Users can fetch the API key from the dashboard.
    """
    backend = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)
    working_directory = os.environ.get("GANTRY_DATASET_WORKING_DIR", str(Path().absolute()))
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

    global _DATASET

    api_client = APIClient(backend, api_key)
    _DATASET = GantryDatasetClient(
        api_client=api_client,
        working_directory=working_directory,
    )  # type: ignore[union-attr]

    if not _DATASET.ping():
        logger_obj.warning(
            "Gantry services not reachable. Check provided URL "
            f"[{backend}] is pointing to the correct address"
        )
        return

    if not _DATASET.ready():
        logger_obj.warning("Gantry services won't receive traffic. Check if API Key is valid")

    # TODO:// only show this warning when customer use dataset sdk
    # if not os.environ.get("GANTRY_DATASET_WORKING_DIR"):
    #     logger_obj.warning(
    #         "You haven't set dataset working directory yet, by default Gantry will "
    #         + f"use {str(Path().absolute())}. You can overwrite the default setting"
    #         + "using set_working_directory method."
    #     )


@_dataset_client_alias
def set_working_directory(*args, **kwargs):
    _DATASET.set_working_directory(*args, **kwargs)


@_dataset_client_alias
def create_dataset(*args, **kwargs):
    return _DATASET.create_dataset(*args, **kwargs)


@_dataset_client_alias
def get_dataset(*args, **kwargs):
    return _DATASET.get_dataset(*args, **kwargs)


@_dataset_client_alias
def list_dataset_versions(*args, **kwargs):
    return _DATASET.list_dataset_versions(*args, **kwargs)


@_dataset_client_alias
def list_datasets(*args, **kwargs):
    return _DATASET.list_datasets(*args, **kwargs)


@_dataset_client_alias
def delete_dataset(*args, **kwargs):
    return _DATASET.delete_dataset(*args, **kwargs)
