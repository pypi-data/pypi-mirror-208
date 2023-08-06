import inspect
from typing import Optional

from gantry.alerts.client import GantryAlerts
from gantry.exceptions import GantryException

# Singleton instance for alerts functionality within the scope of some backend and api key
_Alerts: Optional[GantryAlerts] = None


def _alerts_alias(func):
    """Decorator for GantryAlerts functions, exposed in main.py"""
    doc: str = ""
    signature = inspect.signature(func)
    orig_doc: Optional[str] = None
    if hasattr(GantryAlerts, func.__name__):
        doc = "Alias for :meth:`gantry.alerts.client.GantryAlerts.{}`".format(func.__name__)
        orig_doc = inspect.getdoc(getattr(GantryAlerts, func.__name__))
        signature = inspect.signature(getattr(GantryAlerts, func.__name__))

    if orig_doc:
        doc += "\n\n{}".format(orig_doc)
    signature = signature.replace(parameters=tuple(signature.parameters.values())[1:])
    func.__doc__ = doc
    func.__signature__ = signature

    return func


def validate_init():
    if _Alerts is None:
        raise GantryException("Alerts functionality has not been initialized.")
