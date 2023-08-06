import functools
from datetime import datetime
from inspect import getcallargs, getfullargspec
from typing import Dict, List, Optional, Tuple, Union, cast

import dateparser
import isodate
import pandas as pd

from gantry.api_client import APIClient


def same_size(*params: str, allow_empty: bool = False):
    """
    Use this decorator to prevent running methods over iterables that are different sizes.
    For example, if 'some_method(s1, s2, s3)' need s1/s2/s3 to be same size then
    it can be decorated with '@same_size("s1", "s2", "s3")'.

    Args:
        *params (List[str]): Name of parameters that will be passed to the decorated
            method
        allow_empty (bool, defaults to False): In case False, empty Parameters
            (with length of 0) will fail the check.

    """

    def decorator(method):
        fullargs = getfullargspec(method).args
        if not all(map(lambda x: x in fullargs, params)):
            raise ValueError(
                f"Decorator on {method} was badly parametrized {params}. This shouldn't happen. "
                "Parameters for this decorator should be a subset "
                "of the methods allowed parameters."
            )

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            provided_params = getcallargs(method, *args, **kwargs)
            sizes = {}
            for param in params:
                size = len(provided_params[param])
                if not allow_empty and len(provided_params[param]) == 0:
                    raise ValueError(f"Parameter '{param}' has size 0. This is not allowed.")
                sizes[param] = size
            if len(set(sizes.values())) != 1:
                raise ValueError(
                    f"Size mismatch on inputs: {sizes}. "
                    f"All GantrySeries passed need to be same size."
                )
            return method(*args, **kwargs)

        return wrapper

    return decorator


def runs_on(*types):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.dtype not in types:
                raise ValueError(
                    f"'{self.name}' has type '{self.datatype}'. "
                    f"'{method.__name__}' support {types} only"
                )
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


def get_application_views(
    api_client: APIClient,
    application: str,
    version=Optional[Union[str, int]],
    environment=Optional[str],
) -> list:
    version_param = version or get_last_application_version(
        api_client=api_client, application=application
    )

    response = api_client.request(
        "GET",
        "/api/v1/applications/" + application + "/views",
        params={"version": version_param},
        raise_for_status=True,
    )

    views = response["data"]

    if environment:
        views = list(filter(lambda view: view["tag_filters"].get("env") == environment, views))

    return views


def get_last_application_version(
    api_client: APIClient,
    application: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> str:
    query_params: dict[str, Union[int, str, datetime]] = {}
    if start_time:
        query_params["start_time"] = start_time
    if end_time:
        query_params["end_time"] = end_time
    metadata_response = api_client.request(
        "GET", "/api/v1/models/" + application + "/schemas", query_params, raise_for_status=True
    )
    if metadata_response.get("data", {}).get("version") is None:
        raise RuntimeError("Unkown error: couldn't fetch last application version from API.")

    return metadata_response["data"]["version"]


def get_application_node_id(
    api_client: APIClient,
    application: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    version: Optional[Union[str, int]] = None,
) -> str:
    query_params: dict[str, Union[int, str, datetime]] = {}
    if start_time:
        query_params["start_time"] = start_time
    if end_time:
        query_params["end_time"] = end_time
    if version:
        query_params["version"] = version

    metadata_response = api_client.request(
        "GET", "/api/v1/models/" + application + "/schemas", query_params, raise_for_status=True
    )
    if metadata_response.get("data", {}).get("id") is None:
        raise RuntimeError("Unkown error: couldn't fetch node id from API.")

    return metadata_response["data"]["id"]


def get_start_end_time_from_view(view: dict) -> Tuple[datetime, datetime]:
    if view.get("start_time"):
        start_time = cast(datetime, dateparser.parse(view["start_time"]))
        end_time = cast(datetime, dateparser.parse(view["end_time"]))
    elif view.get("duration"):
        start_time = datetime.utcnow()
        end_time = start_time - isodate.parse_duration(view["duration"])
    else:
        raise ValueError(
            "View has invalid time configuration. Either start_time/end_time"
            " or duration need to be set"
        )

    return start_time, end_time


def _build_empty_df_with_schema(schema: Dict[str, str]) -> pd.DataFrame:
    cols = [item[0] for item in schema.items()]
    ret = pd.DataFrame(columns=cols)
    for col, dtype in schema.items():
        try:
            ret[col] = ret[col].astype(dtype)
        except TypeError:
            ret[col] = ret[col].astype("str")
    return ret


def _build_batch_id_filter(batch_id: str) -> dict:
    return {
        "feature_name": "batch_id",
        "string_query": batch_id,
        "dtype": "reserved_field",
    }


def _get_application_batches(
    api_client: APIClient,
    application: str,
    version: Optional[Union[str, int]] = None,
) -> List[dict]:
    version_param = version or get_last_application_version(
        api_client=api_client, application=application
    )
    node_id = get_application_node_id(api_client, application, version=version_param)
    response = api_client.request(
        "GET",
        "/api/v1/applications/" + node_id + "/batches",
        raise_for_status=True,
    )

    return response["data"]["batches"]
