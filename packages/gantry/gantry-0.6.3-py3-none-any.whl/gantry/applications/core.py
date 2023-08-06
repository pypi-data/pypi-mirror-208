import datetime
import json
import logging
import uuid
from functools import wraps
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from gantry import dataset
from gantry.api_client import APIClient
from gantry.automations.automations import Automation
from gantry.exceptions import ClientNotInitialized, GantryRequestException
from gantry.logger.constants import BatchType
from gantry.logger.main import _upload_data_as_batch, log, log_file
from gantry.query.core.dataframe import GantryDataFrame
from gantry.query.core.utils import get_application_node_id
from gantry.query.time_window import RelativeTimeWindow, TimeWindow

logger = logging.getLogger(__name__)


class Run:
    """
    Context manager for logging.
    """

    # Class variable to store the current run instance
    _current_instance = None

    def __init__(self, application, tags: Optional[Dict], name: str):
        if not isinstance(application, Application):
            raise TypeError("Your input must be an Application.")
        self.run_id = str(uuid.uuid4())

        self.name: str = name
        self.application: Application = application
        self.tags: Dict = tags or {}
        self.prediction_and_feedback_events: List[Dict] = []
        self.prediction_events: List[Dict] = []
        self.feedback_events: List[Dict] = []
        self.join_keys: List[str] = []

    def __enter__(self):
        logger.info("Starting run...")
        logger.info("Run ID: " + str(self.run_id))
        Run._current_instance = self
        return self

    def add_prediction_and_feedback_events(self, events: List[Dict]):
        self.prediction_and_feedback_events.extend(events)

    def add_prediction_events(self, events: List[Dict]):
        self.prediction_events.extend(events)

    def add_feedback_events(self, events: List[Dict]):
        self.feedback_events.extend(events)

    def prepare_join_key_list(self):
        for event in self.prediction_and_feedback_events:
            if event["feedback_id"] not in self.join_keys:
                self.join_keys.append(event["feedback_id"])
        for event in self.feedback_events:
            if event["feedback_id"] not in self.join_keys:
                self.join_keys.append(event["feedback_id"])

    def merge_events(self):
        """
        Merge prediction and feedback events into a single list of events.
        """
        merge_join_keys = {}
        for event in self.prediction_events:
            if event["feedback_id"] not in merge_join_keys:
                merge_join_keys[event["feedback_id"]] = {}
            merge_join_keys[event["feedback_id"]]["prediction"] = event

        for event in self.feedback_events:
            if event["feedback_id"] in merge_join_keys:
                merge_join_keys[event["feedback_id"]]["feedback"] = event

        for key, value in merge_join_keys.items():
            if key not in self.join_keys:
                self.join_keys.append(key)
            event = {}
            if "feedback" not in value:
                event.update(value["prediction"])
                event.update({"feedback": {"ground_truth_label": None}})
            elif "prediction" not in value:
                continue
            else:
                event.update(value["prediction"])
                event["metadata"].update(value["feedback"].pop("metadata"))
                event.update(value["feedback"])
            self.prediction_and_feedback_events.append(event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Ending run...")
        self.prepare_join_key_list()
        self.merge_events()

        if len(self.prediction_and_feedback_events) - len(self.prediction_events) > 0:
            _upload_data_as_batch(
                self.application._name,
                version=None,
                events=self.prediction_and_feedback_events,
                batch_type=BatchType.RECORD,
                run_id=self.run_id,
                run_name=self.name,
                run_tags=self.tags,
            )
        elif len(self.prediction_events) > 0:
            _upload_data_as_batch(
                self.application._name,
                version=None,
                events=self.prediction_events,
                batch_type=BatchType.PREDICTION,
                run_id=self.run_id,
                run_name=self.name,
                run_tags=self.tags,
            )
        elif len(self.feedback_events) > 0:
            _upload_data_as_batch(
                self.application._name,
                version=None,
                events=self.feedback_events,
                batch_type=BatchType.FEEDBACK,
                run_id=self.run_id,
                run_name=self.name,
                run_tags=self.tags,
            )
        Run._current_instance = None

    def end(self):
        self.__exit__()


def run_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if Run._current_instance:
            if "inputs" in result[0] and "feedback" in result[0]:
                Run._current_instance.add_prediction_and_feedback_events(result)
            elif "inputs" in result[0]:
                Run._current_instance.add_prediction_events(result)
            elif "feedback" in result[0]:
                Run._current_instance.add_feedback_events(result)
        return result

    return wrapper


class Application:
    """
    A class to represent a single application. This class is not directly initialized,
    but is instead initialized by calling `gantry.create_application("my-app")`, or
    `gantry.get_application("my-app")`.
    """

    def __init__(
        self,
        name: str,
        api_client: APIClient,
        id: Optional[uuid.UUID] = None,
        organization_id: Optional[uuid.UUID] = None,
    ):
        """
        Note: Please use gantry.create_application() to create an application instead
        of defining an application directly by calling this method.
        """
        self._api_client = api_client
        if self._api_client is None:
            raise ClientNotInitialized()
        self._id = id or uuid.uuid4()
        self._name = name
        self._organization_id = organization_id
        self._version = 1

    def log_file(
        self,
        filepath: str,
        version: Optional[Union[int, str]] = None,
        timestamp: Optional[str] = None,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        feedbacks: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        feedback_id: Optional[str] = None,
        feedback_keys: Optional[List[str]] = None,
        sep: str = ",",
        join_key: Optional[str] = None,
    ):
        """
        Ingest a file containing records into Gantry. File MUST contain a header
        line with column names.

        This method provides parameters to customize column name
        mappings to inputs/outputs/feedback/timestamps/etc.

        All specifications are specifications of file column names

        IMPORTANT: SDK validation will be done only at the header level
        (validating inputs/outputs/feedback parametrization is valid).
        Data itself won't be validated due to potential limitations with
        file size.

        Args:
            filepath (str): path to the file.
            version (optional, Union[int, str]): Version of the function schema to use
                for validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            timestamp (optional, str): by default, timestamp values will be fetched
                from a 'timestamp' named column. Set this parameter to reference a
                different column.
            inputs (optional, list[str]): by default, all columns that start with 'input'
                will be considered inputs. Alternatively, you can provide a list of
                column names using this parameter to be considered inputs.
            outputs (optional, list[str]): by default, all columns that start with 'output'
                will be considered outputs. Alternatively, you can provide a list of
                column names using this parameter to be considered outputs.
            feedbacks (optional, list[str]): by default, all columns that start with 'feedback'
                will be considered feedbacks. Alternatively, you can provide a list of
                column names using this parameter to be considered feedbacks.
            tags (optional, list[str]): by default, all columns that start with 'tags'
                will be considered tags. Alternatively, you can provide a list of
                column names using this parameter to be considered tags.
            feedback_id (optional, str): by default, feedback_id values will be fetched
                from a 'feedback_id' named column. Set this parameter to reference
                another column.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_key' instead.
            feedback_keys (optional, list[str]): provide a list of column names to be used
                as feedback_keys.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_key' instead.
            sep (str, defaults to ','): Character separator, defaults to ',' (for CSV files).
            join_key (optional, str): by default, feedback_id values will be fetched
                from a 'join_key' named column. Set this parameter to reference
                another column.
        """
        log_file(
            self._name,
            filepath,
            version=version,
            timestamp=timestamp,
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            tags=tags,
            feedback_id=feedback_id,
            feedback_keys=feedback_keys,
            sep=sep,
            join_key=join_key,
        )

    @run_decorator
    def log(
        self,
        inputs: Optional[Union[dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        outputs: Optional[
            Union[Any, List[Any], dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]
        ] = None,
        feedbacks: Optional[Union[dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[
            Union[datetime.datetime, List[datetime.datetime], pd.DatetimeIndex, np.ndarray]
        ] = None,
        sort_on_timestamp: bool = True,
        sample_rate: float = 1.0,
        as_batch: Optional[bool] = False,
        version: Optional[Union[int, str]] = None,
        tags: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        row_tags: Optional[
            Union[Dict[str, str], List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]
        ] = None,
        global_tags: Optional[Dict[str, str]] = None,
        join_keys: Optional[Union[str, List[str], pd.Series]] = None,
    ):
        """
        Ingests an event or a batch of events containing predictions (inputs and outputs), feedback, or both simultaneously.

        Example:

        .. code-block:: python

            app.log(
                inputs=[{'A': 100}, {'A': 101}],
                outputs=[{'B': 'foo'}, {'B': 'bar'}],
                version=1,
                feedbacks=[{'B': 'bar'}, {'B': 'foo'}],
                global_tags={"env": "environment1"},
                join_keys=["12345", "67890"]
            )

        Args:
            inputs (optional, Union[dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]) : A list of prediction inputs. `inputs[i]`
                is a dict of the features for the i-th prediction to be logged.
            outputs (optional, Union[Any, List[Any], dict, List[dict], pd.DataFrame, pd.Series, np.ndarray): A list of prediction outputs. `outputs[i]`
                should be the application output for the prediction with features `inputs[i]`.
            feedbacks (optional, Union[dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]): A list of feedbacks. `feedbacks[i]`
                is a dict of the features for the i-th prediction to be logged.
            ignore_inputs (optional, List[str]): A list of names of input features that should not
                be monitored.
            timestamps (optional, Union[List[datetime.datetime], pd.DatetimeIndex, np.array[datetime.datetime]):  # noqa: E501
                A list of prediction timestamps.
                If specified, `timestamps[i]` should be the timestamps for the i-th prediction.
                If timestamps = None (default), then the prediction
                timestamp defaults to the time when `log_records` is called.
            sort_on_timestamp (bool, defaults to True): Works when timestamps are provided.
                Sort using the given timestamp. Default to True.
            sample_rate: Used for down-sampling. The probability as a float that each record
                will be sent to Gantry.
            as_batch (bool, defaults to False): Whether to add batch metadata and tracking
                in the 'batch' section of the dashboard
            version (optional, Union[int, str]): Version of the function schema to use for
                validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            tags (optional, Optional[Union[Dict[str, str], List[Dict[str, str]]]): A tag is a
                label that you assign to your data. E.g. you can specify which environment
                the data belongs to by setting "env" tag like this tags = {"env": "environment1"}
                if not assigned we will use Gantry client's environment value as the defaults
                environment. If this parameter is a dict, tags will apply to all records.
                Alternatively, you can pass a list of dicts to apply tags to each record
                independantly.
                IMPORTANT: this parameter is in deprecation mode and it will be removed soon.
                Use row_tags and global_tags instead.
            row_tags (optional, Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]]): Specify row level tags.
                If provided, this parameter should be a list of tags to be applied to each of the records.
                row_tags[i] will contain a dictionary of strings containing the tags to attach to the
                i-th record. Alternatively, tags may be specified by passing in a DataFrame, Series,
                or Array, like inputs.

                For batch global tags, use the 'global_tags' parameter instead.
            global_tags (optional, Dict[str, str]): Specify a set of tags that will be attached to
                all ingested records from this batch. For record specific tags, you can use
                'row_tags' param. Only used when log is not called within a run.
            join_keys  (optional, Union[List[str], pd.Series[str]]): provide keys to identify
                each record. These keys can be used later to provide feedback. If not provided,
                a random record key will be generated for each record.
        """
        run_id = None
        run_tags = None
        if Run._current_instance:
            run_id = Run._current_instance.run_id
            run_tags = Run._current_instance.tags
        return log(
            application=self._name,
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            ignore_inputs=ignore_inputs,
            tags=tags,
            timestamps=timestamps,
            sort_on_timestamp=sort_on_timestamp,
            sample_rate=sample_rate,
            row_tags=row_tags,
            global_tags=global_tags,
            join_keys=join_keys,
            as_batch=as_batch,
            run_id=run_id,
            run_tags=run_tags,
            version=version,
        )

    def query(
        self,
        time_window: Optional[Union[TimeWindow, RelativeTimeWindow]] = None,
        version: Optional[Union[int, str]] = None,
        env: Optional[str] = None,
        filters: Optional[List[dict]] = None,
        tags: Optional[dict] = None,
    ):
        """
        Query for a window of data for this application, with given parameters.

        Example:

        .. code-block:: python

            time_window = RelativeTimeWindow(window_length = datetime.timedelta(days=1),
                offset = datetime.timedelta(minutes=1))
            query = app.query(
                time_window,
                tags = {"champion": "messi"},
                filters=[
                    {
                        "feature_name": "inputs.speed",
                        "lower_bound": 0,
                        "upper_bound": 3
                    }
                ]
            )

        Args:
            time_window (optional, Union[TimeWindow, RelativeTimeWindow]): A time window object.
            version (optional, Union[int, str]): The version of the application to query.
            env (optional, str) : The environment of the application to query.
            filters (optional, list[dict]) : A list of filters to apply to the query.
            tags (optional, dict) : A dictionary of tags to apply to the query.

        Returns:
            Gantry Dataframe with all the query information to fetch data.
        """
        start_time: Union[str, datetime.datetime] = "-24H"
        end_time: Union[str, datetime.datetime] = "now"
        if time_window:
            start_time = time_window.start_time
            end_time = time_window.end_time

        return GantryDataFrame(
            api_client=self._api_client,
            application=self._name,
            start_time=start_time,
            end_time=end_time,
            version=version,
            env=env,
            filters=filters,
            tags=tags,
        )

    def save_query(self, name: str, query: GantryDataFrame):
        """
        Save a query to the Gantry database.

        Example:

        .. code-block:: python

            query = app.query(....)
            app.save_query("demo_query", query)

        Args:
            name (str): The name of the query.
            query (GantryDataFrame): The query to save.
        """
        data = {
            "name": name,
            "env": query.env,
            "tags": query.tags or {},
            "filters": query.filters or [],
            "details": {"color": "default"},
        }
        if query.start_time or query.end_time:
            if not (query.start_time and query.end_time):
                raise ValueError("Both start_time and end_time must be specified.")
            data["start_time"] = query.start_time  # type: ignore
            data["end_time"] = query.end_time  # type: ignore

        try:
            model_node_id = get_application_node_id(
                self._api_client, self._name, version=query.version
            )
            data["model_node_id"] = model_node_id
        except GantryRequestException:
            raise ValueError(
                f"Application {self._name}[{query.version if query.version else 'latest'}]"
                + "does not exist."
            )
        if name in [query["name"] for query in self.list_queries()]:
            self._api_client.request("PATCH", "/api/v1/queries", json=data, raise_for_status=True)
            logger.info("Query updated successfully.")
        else:
            self._api_client.request("POST", "/api/v1/queries", json=data, raise_for_status=True)
            logger.info("Query saved successfully.")

    def get_query(self, name: str) -> GantryDataFrame:
        """
        Get a saved query from the Gantry database.

        Example:

        .. code-block:: python

            query = app.get_query("demo_query")

        Args:
            name (str) : The name of the query.
        Returns:
            Gantry Dataframe with all the query information to fetch data.
        """
        try:
            model_node_id = get_application_node_id(self._api_client, self._name)
            query = self._api_client.request(
                "GET", f"/api/v1/applications/{model_node_id}/queries/{name}"
            )
            query = query["data"]
            deserialized_tags = {}
            for tag in query["tags"]:
                deserialized_tags[tag["tag_name"]] = tag["tag_value"]

            return GantryDataFrame(
                api_client=self._api_client,
                application=self._name,
                start_time=query["start_time"],
                end_time=query["end_time"],
                filters=query["filters"],
                tags=deserialized_tags,
            )
        except GantryRequestException:
            raise ValueError("Application does not exist.")

    def list_queries(self):
        """
        List all saved queries for this application.
        Example:

        .. code-block:: python

            queries = app.list_queries()
            for query in queries:
                print(query["name"])

        Returns:
            A list of queries (in Python dict).
        """
        query = self._api_client.request("GET", f"/api/v1/applications/{self._id}/queries")
        return query["data"]

    def start_run(self, name: str, tags: Optional[dict] = None):
        """
        Start a run for this application.

        Example:

        .. code-block:: python

            with app.start_run(name="Demo_run", tags = {"champion": "messi"}) as run:
                app.log(inputs=inputs, outputs=outputs, feedbacks=feedback, join_keys=join_keys)
                app.log(inputs={...}, outputs={...}, join_keys='12345')
                app.log(....)

        Args:
            name (str): Name of the run.
            tags (optional, dict): A dictionary of tags to apply to the run.

        Returns:
            A Run object.
        """
        return Run(self, name=name, tags=tags)

    def get_run(self, name: Optional[str] = None, tags: Optional[dict] = None):
        """
        Get a run in this application, filtered by tags or name.

        Example:

        .. code-block:: python

            job_info = app.get_run(name="Demo_run_prediction")

        .. code-block:: python

            jobs_info = app.get_run(tags={"champion": "argentina"})

        Args:
            name (optional, str): Name of the run.
            tags (optional, dict): Tags of the run.

        Returns:
            An ingestion job object associated with the requested run.
        """
        if name:
            response = self._api_client.request(
                "GET",
                f"/api/v1/applications/{self._id}/jobs",
                params={"run_name": name},
                raise_for_status=True,
            )
            return response["data"]["jobs"]
        if tags:
            response = self._api_client.request(
                "GET",
                f"/api/v1/applications/{self._id}/jobs",
                params={"run_tags": json.dumps(tags)},
                raise_for_status=True,
            )
            return response["data"]["jobs"]

    def add_automation(self, automation: Automation):
        """
        Add an automation to this application.

        Example:

        .. code-block:: python

            automation = Automation(...)
            app.add_automation(automation)

        Args:
            automation (Automation): An Automation object.

        Returns:
            None
        """
        automation.add_to_application(self._name)

    def get_automation(self, automation_name: Optional[str] = None):
        """
        Get an automation by name

        Example:

        .. code-block:: python

            automation = app.get_automation(automation_name="demo_automation")

        Args:
            automation_name (optional, str): Name of the automation.
        Returns:
            An Automation object.
        """
        resp = self._api_client.request(
            "GET", f"/api/v1/automations/{automation_name}", params={"application_name": self._name}
        )
        data = resp["data"]
        data["application"] = self.get_schema()["func_name"]
        return Automation.from_dict(data)

    def list_automations(self):
        """
        List all automations for this application.

        Example:

        .. code-block:: python

            automations = app.list_automations()
            for automation in automations:
                print(automation["name"])

        Returns:
            A list of Automation objects.
        """
        resp = self._api_client.request(
            "GET", "/api/v1/automations", params={"application_name": self._name}
        )
        return resp["data"]

    def list_workspaces(self):
        """
        Get all workspaces for this application.

        Example:

        .. code-block:: python

            workspaces = app.list_workspaces()
            for workspace in workspaces:
                print(workspace["name"])

        Returns:
            A list of Workspace objects.
        """
        res = self._api_client.request(
            "GET", "/api/v1/workspaces", params={"application_id": self._id}
        )
        if "workspaces" in res["data"]:
            return res["data"]["workspaces"]
        return res["data"]

    def get_schema(self):
        """
        Get the schema for this application.

        Example:

        .. code-block:: python

            schema = app.get_schema()
            print(schema["func_name"]) -> application name

        Returns:
            The application schema (in Python dict).
        """
        # GET /api/v1/applications/<model_name>/schemas
        res = self._api_client.request("GET", f"/api/v1/applications/{self._name}/schemas")
        return res["data"]

    def create_dataset(self, name: str, bucket_name: Optional[str] = None):
        """
        Create a dataset for this application.

        Example:

        .. code-block:: python

            dataset = app.create_dataset(name="demo_dataset", bucket_name="demo_bucket")

        Args:
            name (str): The name of the dataset.
            bucket_name (optional, str): The bucket name of the dataset.

        Return:
            :class:`gantry.dataset.GantryDataset`: an object representing the created dataset.
        """
        return dataset.create_dataset(name=name, bucket_name=bucket_name, app_name=self._name)

    def list_datasets(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        List all datasets for this application.

        Example:

        .. code-block:: python

            datasets = app.list_datasets()
            for dataset in datasets:
                print(dataset["name"])

        Args:
            include_deleted (optional, bool): Will include deleted datasets if set to `true`
                and will omit them otherwise.
        Returns:
            ``List[Dict[str, Any]]``: List of dictionaries, each representing one
            dataset and associated metadata.
        """
        return dataset.list_datasets(include_deleted=include_deleted, model_node_id=self._id)

    # NotImplemented: chat/completion functions

    def create_version(self, *args, **kwargs):
        """
        :meta private:
        """
        raise NotImplementedError(
            "Versions are not supported for this application.\n"
            "Versions are only supported for completion applications."
        )

    def get_version(self, *args, **kwargs):
        """
        :meta private:
        """
        raise NotImplementedError(
            "Versions are not supported for this application.\n"
            "Versions are only supported for completion applications."
        )

    def log_completion(self, *args, **kwargs):
        """
        :meta private:
        """
        raise NotImplementedError("Completions cannot be logged for a non-completion application.")
