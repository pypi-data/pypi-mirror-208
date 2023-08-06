import datetime
import logging
import random
from collections import defaultdict
from typing import Dict, List, Optional, Union

import isodate
from halo import Halo
from tabulate import tabulate

from gantry.api_client import APIClient
from gantry.exceptions import GantryRequestException
from gantry.query.core.dataframe import GantryDataFrame
from gantry.query.core.distance import GantryDistance
from gantry.query.core.metric import GantryMetric
from gantry.query.core.utils import (
    _build_batch_id_filter,
    _get_application_batches,
    get_application_node_id,
    get_application_views,
)

logger = logging.getLogger(__name__)

COLOR_OPTIONS_FOR_VIEW = [
    "#32D3EC",
    "#3998D9",
    "#126196",
    "#B184FE",
    "#7C3AED",
    "#4E16AD",
    "#FDC17D",
    "#FF8900",
    "#FFE47A",
    "#FACC15",
    "#6EE7B7",
    "#CDDC39",
    "#389D3C",
    "#8BC34A",
    "#D2AFC5",
    "#904C77",
    "#642F50",
    "#607D8B",
]


class GantryQuery:
    def __init__(self, api_client: APIClient) -> None:
        self._api_client = api_client
        self.distance = GantryDistance(self._api_client)
        self.metric = GantryMetric(self._api_client)

    def list_applications(self) -> List[str]:
        """
        List all applications in Gantry.

        Returns:
            List of application names that are stored in gantry.
        """
        query_params = {"limit": 10}
        response = self._api_client.request(
            "GET", "/api/v1/models", params=query_params, raise_for_status=True
        )
        return list(response["data"].keys())

    def list_application_versions(self, application: str) -> List[str]:
        """
        List the stored versions integer and version names for a given application.

        The version integer is used in conjunction with the application name to uniquely identify
        the application and its events in Gantry.

        Args:
            application (str): application name string.
        Returns:
            List of versions for |application| that are stored in gantry.
        """
        version_response = self._api_client.request(
            "GET",
            "/api/v1/models/" + application,
            params={"include_names": True},
            raise_for_status=True,
        )
        data = version_response["data"]
        return [version_dict["version"] for version_dict in data["versions"]]

    def list_application_environments(self, application: str) -> List[str]:
        """
        List the available environments for a given application.

        Args:
            application (str): application name string.
        Returns:
            List of environments
        """
        response = self._api_client.request(
            "GET", "/api/v1/models/" + application, raise_for_status=True
        )
        return response["data"]["environments"]

    def query(
        self,
        application: str,
        start_time: Optional[Union[str, datetime.datetime]] = None,
        end_time: Optional[Union[str, datetime.datetime]] = None,
        version: Optional[Union[int, str]] = None,
        environment: Optional[str] = None,
        filters: Optional[List[Dict]] = None,
        view: Optional[str] = None,
        tags: Optional[dict] = None,
        batch_id: Optional[str] = None,
    ) -> GantryDataFrame:
        """
        Query for a window of data for an application and version with a given start, end
        time.

        Args:
            application (str): application name string.
            start_time (str or datetime): datetime object for start time of the window.
                If not provided, defaults to previous 24 hours
            end_time (str or datetime): datetime object for the end time of the window.
                If not provided, defaults to now
            version (optional, int or str): application version.
            environment: (optional, str) - environment string to pull application for.
                This parameter takes precedence over a tags["env"] value in case
                tags are passed.
            filters: (optional, list[dict]) - optional filters for the query. Use this
                parameter only if you are familiar with the dict representation of
                the filters.
            view: (optional, str) - The view name to query data from. A view is a saved
                configuration of filters/start_time/end_time, so this parameter cannot
                be used with start_time, end_time, filters or batch_id parameters.
            tags: (optional, dict) - Optional tags to filter data. Each record has tags
                associated that were provided at ingestion time. The environment parameter
                overrides an "env" tag.
            batch_id: (optional, str) - The batch_id to query data from. Only data ingested
                in the given batch will be retrieved. This parameter cannot be used with
                'view' parameter.

        Returns:
            Gantry Dataframe with the data.
        """
        if view is not None:
            if not (
                start_time is None and end_time is None and filters is None and batch_id is None
            ):
                raise ValueError(
                    "Cannot provide 'view' parameter with "
                    "start_time/end_time/filters/batch_id at the same time"
                )

            views = self.list_application_views(
                application, version=version, environment=environment
            )
            if view not in views:
                raise ValueError(
                    f"View '{view}' not found. Available views for this version/env: {views}"
                )

            return GantryDataFrame.from_view(
                self._api_client, application, view, version, environment, tags=tags
            )

        if batch_id:
            batches = _get_application_batches(self._api_client, application, version=version)
            batch_ids = [b["id"] for b in batches]
            if batch_id not in batch_ids:
                raise ValueError(
                    f"Batch '{batch_id}' not found. Available batches for this version: {batch_ids}"
                )

            filters = filters or []
            filters.append(_build_batch_id_filter(batch_id))

        start_time = start_time or "-24H"
        end_time = end_time or "now"

        return GantryDataFrame(
            self._api_client,
            application,
            version=version,
            env=environment,
            start_time=start_time,
            end_time=end_time,
            filters=filters,
            tags=tags,
        )

    def get_current_feedback_schema(self, application: str):
        """Returns current feedback schema for the provided application."""
        raise NotImplementedError()

    def update_feedback_schema(
        self, application, feedback_fields: List[Dict[str, str]], create: bool = True
    ):
        """Update feedback schema with feedback_fields for the provided application

        This function updates the feedback schema to *only* have the feedback fields specified in
        the `feedback_fields` argument. If you want to add new feedback fields to an existing
        feedback schema, use the `add_feedback_field` function.

        Args:
            application: The name of the relevant application to apply this update for.
            feedback_fields: A list of dicts with keys 'name' and 'type'. For example:

                .. code-block:: python

                    [{'name': 'label', 'type': 'int'}, {'name': 'label2', 'type': 'str'}]

            create: If create=True, then if a feedback schema doesn't exist for the application
                then this function will create a new schema. If create=False, then if a feedback
                schema doesn't already exist, will raise an error.
        """
        raise NotImplementedError()

    def add_feedback_field(self, application: str, feedback_field: Dict[str, str]) -> int:
        """Adds a feedback field to current feedback schema.

        A current feedback schema must exist to use this method, otherwise it will raise an error.
        If it doesn't, use the `update_feedback_schema` method to generate a new one.

        Args:
            application: The name of the application apply this update to.
            feedback_field: A dict with keys 'name' and 'type' specifying the `name` and `type` of
                the feedback field. For example:

                .. code-block:: python

                    {'name': 'label', 'type': 'int'}

        """
        raise NotImplementedError()

    def get_current_metric_schema(self, application: str):
        """Returns current metrics schema for application with name=application."""
        raise NotImplementedError()

    def update_metric_schema(self, application: str, metrics: List[dict], create: bool = True):
        """Update metrics schema with metrics for application.

        This function updates the metrics schema to *only* have the metrics specified in
        the `metrics` argument. If you want to add new metrics to an existing
        feedback schema, use the `add_metric` function. Must already have schemas for
        prediction events and feedback events in place before created a metric schema.

        Args:
            application: The name of the relevant application to apply this update for.
            metrics: A list of dicts, where each dict specifies a metric. For example a metric
                dict looks like:

                .. code-block:: python

                    {
                        'name': 'my_metric',
                        'output_features': 'outputs',
                        'feedback_fields': 'feedback.label',
                        'metric_fn': 'mse'
                    }

            create: If create=True, then if a metric schema doesn't exist for the func_name
                then this function will create a new schema. If create=False, then if a metric
                schema doesn't already exist, will raise an error.
        """
        raise NotImplementedError()

    def add_metric(self, application: str, metric: dict) -> int:
        """Adds a metric to current metric schema.

        A current metric schema must exist to use this method, otherwise it will raise an error.
        If it doesn't, use the `update_metric_schema` method to generate a new one.

        Args:
            application (str): The name of the relevant application to apply this update for.
            metric: A dict that specifs a metric. For example:

                .. code-block:: python

                    {
                        'name': 'my_metric',
                        'output_features': 'outputs',
                        'feedback_fields': 'feedback.label',
                        'metric_fn': 'mse'
                    }

        """
        raise NotImplementedError()

    def create_view(
        self,
        name: str,
        application: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        duration: Optional[datetime.timedelta] = None,
        version: Optional[str] = None,
        tag_filters: Optional[Dict[str, str]] = None,
        data_filters: Optional[List[Dict]] = None,
    ) -> None:
        """Create a view for an application.

        Args:
            name (str): The name of the view.
            application (str): The application in which the view will be created.
            start_time (optional, datetime): Start time of the view. If you pass start_time,
                you need to specify end_time and cannot set duration.
            end_time (optional, datetime): End time of the view. If you pass end_time, you need to
                specify start_time also and cannot set duration.
            duration (optional, timedelta): Time window of the view. End time will be present time.
                For example, timedelta(days=1) will look 24hs back.
                IMPORTANT: if exact datetimes want to be provided, use start_time/end_time instead.
            version (optional, str): The version of the app that the view should use.
            tag_filters (optional, dict): A dictionary with tags to filter the data of the view.
            data_filters (optional, list[dict]): A list of Gantry-formatted filters. For example:

                .. code-block:: python

                    [
                        {
                            'feature_name': 'inputs.loan_amount',
                            'lower_bound': '100',
                            'upper_bound': '200',
                        }
                    ]

        """
        data = {
            "name": name,
            "tag_filters": tag_filters or {},
            "data_filters": data_filters or [],
            "details": {"color": random.choice(COLOR_OPTIONS_FOR_VIEW)},
        }

        if duration:
            if start_time or end_time:
                raise ValueError("Cannot provide duration and start_time/end_time at the same time")

            data["duration"] = isodate.duration_isoformat(duration)

        if start_time or end_time:
            if not (start_time and end_time):
                raise ValueError("Need to provide both start_time and end_time")

            data["start_time"] = start_time  # type: ignore
            data["end_time"] = end_time  # type: ignore

        if not (duration or start_time or end_time):
            raise ValueError("Need to provide duration or start_time/end_time")

        try:
            model_node_id = get_application_node_id(self._api_client, application, version=version)
            data["model_node_id"] = model_node_id
        except GantryRequestException:
            raise ValueError(
                f"Application {application}[{version if version else 'latest'}] does not exist."
            )

        self._api_client.request("POST", "/api/v1/views", json=data, raise_for_status=True)
        return None

    def list_application_views(
        self,
        application: str,
        version: Optional[Union[str, int]] = None,
        environment: Optional[str] = None,
    ) -> List[str]:
        """
        List saved views for given application, version and enviroment.

        Args:
            application (str): The name of the application.
            version (str): The version of the application to show the views
                from. If not provided, it will use the latest version.
            environment (str): The environment of the application to filter
                the views. If not provided, views from all environments will
                be shown.

        Returns:
            List of saved views names.
        """

        views = get_application_views(self._api_client, application, version, environment)
        return [view["name"] for view in views]

    def list_application_batches(
        self,
        application: str,
        version: Optional[Union[str, int]] = None,
    ) -> List[dict]:
        """
        List data batches for given application and version.

        Args:
            application (str): The name of the application.
            version (str): The version of the application to show the views
                from. If not provided, it will use the latest version.

        Returns:
            List of batches
        """
        return _get_application_batches(self._api_client, application, version)

    def print_application_info(self, application: str) -> None:
        """
        Prints a high-level report of an application.

        Args:
            application (str): The name of the application.

        """
        versions = self.list_application_versions(application)
        envs = self.list_application_environments(application)

        print("Available versions:")
        print("-------------------")
        print(versions)
        print()
        print("Available environments:")
        print("-----------------------")
        print(sorted(envs))
        print()
        print("Available views:")
        print("----------------")

        with Halo(text="Fetching views...", spinner="dots"):
            content = defaultdict(list)
            for version in versions:
                if self.list_application_views(application, version):
                    for env in envs:
                        views = get_application_views(self._api_client, application, version, env)
                        for view in views:
                            content["name"].append(view["name"])
                            if view.get("duration"):
                                content["duration"].append(isodate.parse_duration(view["duration"]))
                                content["from"].append("null")
                                content["to"].append("null")
                            else:
                                content["duration"].append("null")
                                content["from"].append(
                                    datetime.datetime.fromisoformat(view["start_time"])
                                )
                                content["to"].append(
                                    datetime.datetime.fromisoformat(view["end_time"])
                                )
                            content["version"].append(version)
                            content["env"].append(env)
        print(tabulate(content, headers="keys"))
