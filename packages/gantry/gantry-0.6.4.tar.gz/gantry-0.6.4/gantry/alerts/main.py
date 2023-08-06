"""
Exposes top-level aliases for using the alerts client.
"""

import os
from typing import Optional
from urllib.parse import urlparse

from gantry.alerts import globals
from gantry.alerts.client import GantryAlerts
from gantry.alerts.globals import _alerts_alias, validate_init
from gantry.api_client import APIClient
from gantry.const import PROD_API_URL


def _init(api_key: Optional[str] = None):
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
    globals._Alerts = GantryAlerts(api_client)  # type: ignore[union-attr]


@_alerts_alias
def get_alerts(*args, **kwargs):
    validate_init()
    return globals._Alerts.get_alerts(*args, **kwargs)  # type: ignore[union-attr]


@_alerts_alias
def create_alert(*args, **kwargs):
    validate_init()
    return globals._Alerts.create_alert(*args, **kwargs)  # type: ignore[union-attr, return-value]


@_alerts_alias
def update_alert(*args, **kwargs):
    validate_init()
    return globals._Alerts.update_alert(*args, **kwargs)  # type: ignore[union-attr, return-value]


@_alerts_alias
def create_slack_notification(*args, **kwargs):
    validate_init()
    return globals._Alerts.create_slack_notification(  # type: ignore[union-attr, return-value]
        *args, **kwargs
    )


@_alerts_alias
def get_slack_notifications(*args, **kwargs):
    validate_init()
    return globals._Alerts.get_slack_notifications(*args, **kwargs)  # type: ignore[union-attr]


@_alerts_alias
def delete_alert(*args, **kwargs):
    validate_init()
    return globals._Alerts.delete_alert(*args, **kwargs)  # type: ignore[union-attr, return-value]


@_alerts_alias
def delete_slack_notification(*args, **kwargs):
    validate_init()
    return globals._Alerts.delete_slack_notification(  # type: ignore[union-attr, return-value]
        *args, **kwargs
    )
