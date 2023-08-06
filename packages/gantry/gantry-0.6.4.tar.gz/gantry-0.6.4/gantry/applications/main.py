import functools
import inspect
import os
from typing import Optional

from gantry.api_client import APIClient
from gantry.applications.client import ApplicationClient
from gantry.const import PROD_API_URL
from gantry.exceptions import ClientNotInitialized

_APPLICATION_CLIENT: Optional[ApplicationClient] = None


def _application_client_alias(f):
    doc = "Alias for :meth:`gantry.applications.client.ApplicationClient.{}`".format(f.__name__)
    signature = inspect.signature(getattr(ApplicationClient, f.__name__))
    orig_doc = inspect.getdoc(getattr(ApplicationClient, f.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)
    signature = signature.replace(parameters=tuple(signature.parameters.values())[1:])

    f.__doc__ = doc
    f.__signature__ = signature

    # This decorator also checks that the _CLIENT
    # has been initialized
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _APPLICATION_CLIENT is None:
            raise ClientNotInitialized()

        return f(*args, **kwargs)

    return wrapper


def _init(api_key: Optional[str] = None):
    global _APPLICATION_CLIENT
    backend = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)
    api_client = APIClient(backend, api_key)
    _APPLICATION_CLIENT = ApplicationClient(api_client)  # type: ignore


@_application_client_alias
def create_application(*args, **kwargs):
    return _APPLICATION_CLIENT.create_application(*args, **kwargs)


@_application_client_alias
def get_application(*args, **kwargs):
    return _APPLICATION_CLIENT.get_application(*args, **kwargs)


@_application_client_alias
def archive_application(*args, **kwargs):
    return _APPLICATION_CLIENT.archive_application(*args, **kwargs)


@_application_client_alias
def delete_application(*args, **kwargs):
    return _APPLICATION_CLIENT.delete_application(*args, **kwargs)
