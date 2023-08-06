import os
from typing import Optional

from gantry.api_client import APIClient
from gantry.automations import globals
from gantry.const import PROD_API_URL


def _init(
    api_key: Optional[str] = None,
):
    backend = os.environ.get("GANTRY_LOGS_LOCATION", PROD_API_URL)

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
