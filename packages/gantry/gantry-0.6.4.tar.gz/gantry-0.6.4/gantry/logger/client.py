import copy
import datetime
import json
import logging
import math
import os
import random
import sys
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import IO, Any, Dict, Iterable, List, Optional, Tuple, Union, cast
from warnings import warn

import numpy as np
import pandas as pd
from typeguard import check_type, typechecked

from gantry.exceptions import GantryBatchCreationException, GantryLoggingException
from gantry.logger.constants import CHUNK_SIZE, BatchType, UploadFileType
from gantry.logger.event_builder import (
    _build_feedback_event,
    _build_prediction_and_feedback_events,
    _build_prediction_event,
    _build_prediction_events,
    _create_timestamp_idx,
)
from gantry.logger.stores import APILogStore
from gantry.logger.types import (
    DataLink,
    IngestFromDataConnectorRequest,
    IngestFromDataConnectorResponse,
    Schedule,
)
from gantry.logger.utils import (
    _batch_fail_msg,
    _batch_success_msg,
    _build_batch_iterator,
    _build_data_link_from_file,
    _check_sample_rate,
    _concurrent_upload_multipart_batch,
    _is_not_empty,
    _log_exception,
)
from gantry.serializers import EventEncoder, serializable_value
from gantry.utils import compute_feedback_id

logger = logging.getLogger(__name__)


def _update_tags_with_env(environment: str, tags: Dict[str, str]) -> None:
    if "env" not in tags:
        tags["env"] = environment


def _default_join_key_gen() -> str:
    return str(uuid.uuid4())


def _resolve_join_key(inputs, feedback_id, feedback_keys, join_key: Optional[str]) -> Optional[str]:
    """To keep backwards compatibility"""
    if feedback_id or feedback_keys:
        warn(
            "Deprecated: feedback_id and feedback_keys are going to be removed soon. "
            "Use 'join_key' instead. See https://docs.gantry.io/docs/logging-feedback-actuals"
            " for more information"
        )
        if join_key:
            raise ValueError("Cannot use 'join_key' with 'feedback_keys' or 'feedback_id'")

        if feedback_id:
            if feedback_keys:
                raise GantryLoggingException(
                    "Cannot specify feedback_id and feedback_keys at same time."
                )

            if isinstance(feedback_id, str):
                # Set the feedback_id directly from the given string.
                return feedback_id
            else:
                # Compute feedback_id just from provided feedback_id dictionary
                return compute_feedback_id(feedback_id, list(feedback_id.keys()))
        else:
            return compute_feedback_id(inputs, feedback_keys)

    return join_key


def _resolve_join_keys(
    size: int, inputs, feedback_ids, feedback_keys, join_keys: Optional[List[str]]
) -> Optional[List[str]]:
    """To keep backwards compatibility
    It can assume sizes match.
    """
    if feedback_ids is None and feedback_keys is None and join_keys is None:
        return None

    if feedback_ids or feedback_keys:
        warn(
            "Deprecated: feedback_ids and feedback_keys are going to be removed soon. "
            "Use 'join_keys' instead. See https://docs.gantry.io/docs/logging-feedback-actuals"
            " for more information"
        )
        if join_keys:
            raise ValueError("Cannot use 'join_keys' with 'feedback_keys' or 'feedback_ids'")

        if feedback_ids:
            if feedback_keys:
                raise GantryLoggingException(
                    "Cannot specify feedback_id and feedback_keys at same time."
                )

    join_keys = join_keys or ([None] * size)  # type: ignore
    feedback_ids = feedback_ids or ([None] * size)  # type: ignore
    inputs = inputs or ([None] * size)  # type: ignore
    return [
        _resolve_join_key(inputs[i], feedback_ids[i], feedback_keys, join_keys[i])  # type: ignore
        for i in range(size)
    ]


def _sample_records(size, sample_rate, inputs, outputs, feedbacks, join_keys, timestamps, tags):
    _check_sample_rate(sample_rate)
    if sample_rate < 1:
        idxs = random.sample(range(size), int(sample_rate * size))
        inputs = [x for idx, x in enumerate(inputs) if idx in idxs] if inputs else None
        outputs = [x for idx, x in enumerate(outputs) if idx in idxs] if outputs else None
        feedbacks = [x for idx, x in enumerate(feedbacks) if idx in idxs] if feedbacks else None
        join_keys = [x for idx, x in enumerate(join_keys) if idx in idxs] if join_keys else None
        timestamps = [x for idx, x in enumerate(timestamps) if idx in idxs] if timestamps else None
        tags = [x for idx, x in enumerate(tags) if idx in idxs] if tags else None

    return inputs, outputs, feedbacks, join_keys, timestamps, tags


class Gantry:
    def __init__(
        self,
        log_store: APILogStore,
        environment: str,
        logging_level: str = "INFO",
    ):
        """
        Initializes a new Gantry client to log predictions and feedback.
        Full list of arguments is defined by :class:`gantry.config.ConfigSchema`.

        Args:
            logs_store (BaseLogStore): The log store to use.
            environment (optional, str): Set the value for the 'env' label attached to data
                instrumented by this client. This value can be overridden for each record using
                the 'env' tag (ie `log_record(..., tag={"env": "prod"})` will override the
                environment tag for that specific record).
                WARNING: this parameter has no effect when using `log_file` functionality,
                it only applies to `log_record`/`log_records`.
            logging_level (options: str): Configure logging level for Gantry system.
        """
        self.log_store = log_store
        self.environment = environment
        self.setup_logger(level=logging_level)

    @_log_exception
    @typechecked
    def log_file(
        self,
        application: str,
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
    ) -> None:
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
            application (str): Name of the application to ingest the file into.
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
        data_link = _build_data_link_from_file(
            application=application,
            filepath=filepath,
            sep=sep,
            version=str(version) if isinstance(version, int) else version,
            timestamp=timestamp,
            inputs=inputs,
            outputs=outputs,
            feedback=feedbacks,
            tags=tags,
            feedback_id=feedback_id,
            feedback_keys=feedback_keys,
            join_key=join_key,
        )
        object_size = os.path.getsize(filepath)  # in bytes
        with open(filepath, "r") as f_in:
            self._smart_file_read(data_link, object_size, Path(filepath).name, f_in, CHUNK_SIZE)

    def _smart_file_read(
        self, data_link, object_size, path_name: str, file: IO[str], chunk_size
    ) -> None:
        block_read = lambda: file.read(chunk_size).encode("utf-8")  # noqa: E731
        # Reference on how sentinel parameter works
        # https://docs.python.org/3/library/functions.html#iter
        block_iterator = iter(block_read, b"")
        self._handle_upload(block_iterator, data_link, object_size, f"{uuid.uuid4()}_{path_name}")

    def _handle_upload(
        self, data_batch_iterator: Iterable, data_link: DataLink, object_size: int, filename: str
    ) -> str:
        # Calculate part counts and generate presigned s3 urls.
        total_num_parts = math.ceil(object_size / CHUNK_SIZE)

        logger.info("Initializing upload to Gantry")
        preupload_res = self.log_store._api_client.request(
            "GET",
            "/api/v1/ingest/file-preupload",
            params={
                "filename": filename,
                "num_parts": total_num_parts,
                "filetype": data_link.file_type,
            },
        )
        if "upload_urls" not in preupload_res:
            raise GantryBatchCreationException(
                "Failed to start batch upload. Please check your API key."
            )
        signed_urls = preupload_res["upload_urls"]
        upload_id = preupload_res["upload_id"]
        file_key = preupload_res["key"]

        parts = _concurrent_upload_multipart_batch(data_batch_iterator, signed_urls)

        logger.info("Starting Gantry Ingestion")
        # Submit file completion to gantry API.
        complete_res = self.log_store._api_client.request(
            "POST",
            "/api/v1/ingest/file",
            json={
                "upload_id": upload_id,
                "key": file_key,
                "parts": parts,
                "data_link": asdict(data_link),
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if "batch_id" not in complete_res:
            raise GantryBatchCreationException(
                "Failed to complete upload. Please contact Gantry support."
            )
        batch_id = complete_res["batch_id"]
        _batch_success_msg(batch_id, data_link.application, self.log_store)

        return batch_id

    @_log_exception
    @typechecked
    def log_from_data_connector(
        self,
        application: str,
        source_data_connector_name: str,
        timestamp: Optional[str] = None,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        feedbacks: Optional[List[str]] = None,
        join_key: Optional[str] = None,
        row_tags: Optional[List[str]] = None,
        global_tags: Optional[Dict[str, str]] = None,
        schedule: Optional[Schedule] = None,
        pipeline_name: Optional[str] = None,
    ) -> IngestFromDataConnectorResponse:
        """
        Function to ingest source tabular records from a registered source data
        connector into Gantry.

        To log predictions using this function, both column names of inputs and outputs
        must be passed.
        To log feedback using this function, both column names of join_key and feedback
        must be passed.

        Example:

        .. code-block:: python

            # Record an application's predictions.
            gantry.log_from_data_connector(
                application="foobar",
                source_data_connector_name="my_snowflake_connector",
                inputs=["column_A", "column_B"],
                outputs=["column_C"],
                timestamp="column_T",
                global_tags = {"env":"dev", "version": "1.0.0"},
                row_tags=["column_D"],
                join_key="column_E",
            )

            # Record an application's feedbacks.
            # to a previously ingested prediction.
            gantry.log_from_data_connector(
                application="foobar",
                source_data_connector_name="my_snowflake_connector",
                feedbacks=["column_E", "column_F"],
                timestamp="column_T",
                global_tags = {"env":"dev", "version": "1.0.0"},
                row_tags=["column_D"],
                join_key="column_E",
            )

            # Trigger scheduled ingestion every 8 hours from a data connector incrementally.
            from gantry.logger.types import (
                Schedule,
                ScheduleFrequency,
                ScheduleType,
                ScheduleOptions,
            )

            gantry.log_from_data_connector(
                application="foobar",
                source_data_connector_name="my_snowflake_connector",
                inputs=["column_A", "column_B"],
                outputs=["column_C"],
                timestamp="column_T",
                global_tags = {"env":"dev", "version": "1.0.0"},
                row_tags=["column_D"],
                join_key="column_E",
                schedule=Schedule(
                    start_on="2023-01-14T17:00:00.000000",
                    frequency=ScheduleFrequency.EVERY_8_HOURS,
                    type=ScheduleType.INCREMENTAL_APPEND,
                    options=ScheduleOptions(watermark_key="column_T"),
                )
            )

            # If the data are expected to arrive late in your source table/view, use delay_time
            # to specify how long to wait before triggering the scheduled ingestion.
            gantry.log_from_data_connector(
                application="foobar",
                source_data_connector_name="my_snowflake_connector",
                inputs=["column_A", "column_B"],
                outputs=["column_C"],
                timestamp="column_T",
                global_tags = {"env":"dev", "version": "1.0.0"},
                row_tags=["column_D"],
                join_key="column_E",
                schedule=Schedule(
                    start_on="2023-01-14T17:00:00.000000",
                    frequency=ScheduleFrequency.EVERY_8_HOURS,
                    type=ScheduleType.INCREMENTAL_APPEND,
                    options=ScheduleOptions(
                        delay_time=300, # Delay 5 minutes before triggering ingestion.
                        watermark_key="column_T"
                    ),
                )
            )

        Args:
            application (str): Name of the application to ingest data into
            source_data_connector_name (str): Name of the registered source data connector
                to ingest data from.
            timestamp (optional, str): by default, the timestamp values will be filled
                with the timestamp at ingestion. Set this parameter to reference a
                different column.
            inputs (optional, list[str]): A list of column names for inputs.
            outputs (optional, list[str]): A list ofcolumn names for outputs.
            feedbacks (optional, list[str]): A list of column names for feedbacks.
            join_key (optional, str): A column name to use as the join key to identify each
                record.
            row_tags (optional, list[str]): A list of column names to use the values of
                as tags for each row.
            global_tags (optional, list[dict[str, str]]): A list of dictionaries of string
                key and value pairs to tag the entire ingestion from this data connector
            schedule (optional, Schedule): An optional parameter to schedule the ingestion.
            pipeline_name (optional, str): An optional parameter to specify the ingestion
                pipeline's name
        """
        if schedule and schedule.start_on and isinstance(schedule.start_on, datetime.datetime):
            schedule.start_on = schedule.start_on.isoformat()

        request = IngestFromDataConnectorRequest(
            application=application,
            source_data_connector_name=source_data_connector_name,
            timestamp=timestamp,
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            row_tags=row_tags,
            global_tags=global_tags,
            join_key=join_key,
            schedule=schedule,
            pipeline_name=pipeline_name,
        )

        response = self.log_store.log_from_data_connector_async(request=request)
        logger.info("Successfully submitted ingestion request to Gantry.")

        return response

    @_log_exception
    @typechecked
    def log(
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[Union[dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        outputs: Optional[
            Union[Any, List[Any], dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]
        ] = None,
        feedbacks: Optional[Union[dict, List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        ignore_inputs: Optional[List[str]] = None,
        tags: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        timestamps: Optional[
            Union[datetime.datetime, List[datetime.datetime], pd.DatetimeIndex, np.ndarray]
        ] = None,
        sort_on_timestamp: bool = True,
        sample_rate: float = 1.0,
        row_tags: Optional[
            Union[Dict[str, str], List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]
        ] = None,
        global_tags: Optional[Dict[str, str]] = None,
        join_keys: Optional[Union[str, List[str], pd.Series]] = None,
        as_batch: Optional[bool] = False,
        run_id: Optional[str] = None,
        run_tags: Optional[dict] = None,
    ):
        """
        A general log function to log inputs, outputs, and feedbacks regardless of
        single or multiple records that is not attached to a specific application.
        This is intended for use primarily in contexts production where contexts
        where avoiding initializing an instance of the application is preferable.

        Args:
            application (str): Name of the application. Gantry validates and monitors data
                by function.
            version (optional, Union[int, str]): Version of the function schema to use for
                validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            inputs (Union[List[dict], pd.Dataframe]): A list of prediction inputs. `inputs[i]`
                is a dict of the features for the i-th prediction to be logged.
            outputs (Union[List[dict], pd.Dataframe]): A list of prediction outputs. `outputs[i]`
                should be the application output for the prediction with features `inputs[i]`.
            feedbacks (Union[List[dict], pd.DataFrame]): A list of feedbacks. `feedbacks[i]`
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
            tags (optional, Optional[Union[Dict[str, str], List[Dict[str, str]]]): A tag is a
                label that you assign to your data. E.g. you can specify which environment
                the data belongs to by setting "env" tag like this tags = {"env": "environment1"}
                if not assigned we will use Gantry client's environment value as the defaults
                environment. If this parameter is a dict, tags will apply to all records.
                Alternatively, you can pass a list of dicts to apply tags to each record
                independantly.
                IMPORTANT: this parameter is in deprecation mode and it will be removed soon.
                Use row_tags and global_tags instead.
            join_keys  (optional, Union[List[str], pd.Series[str]]): provide keys to identify
                each record. These keys can be used later to provide feedback. If not provided,
                a random record key will be generated for each record.
            row_tags (optional, Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]]): Specify row level tags.
                If provided, this parameter should be a list of tags to be applied to each of the records.
                row_tags[i] will contain a dictionary of strings containing the tags to attach to the
                i-th record. Alternatively, tags may be specified by passing in a DataFrame, Series,
                or Array, like inputs.

                For batch global tags, use the 'global_tags' parameter instead.
            global_tags (optional, Dict[str, str]): Specify a set of tags that will be attached to
                all ingested records from this batch. For record specific tags, you can use
                'row_tags' param. Only used when log is not called within a run.
            run_id (optional, str): This should never be provided by user. It will be populated automatically when logging within a run to group records together.
            run_tags (optional, Dict[str, str]): This should never be provided by user. It will be populated automatically when logging within a run to provide global tags for all records in the run.
        """
        if run_id:
            # Generate records/events to be logged as part of the Run.

            # Check if inputs, outputs, feedbacks, timestamps, and join keys are singular.
            # If so, convert to list with one element.
            if isinstance(inputs, dict):
                inputs = [inputs]
            if isinstance(outputs, dict):
                outputs = [outputs]
            if isinstance(feedbacks, dict):
                feedbacks = [feedbacks]
            if isinstance(timestamps, datetime.datetime):
                timestamps = [timestamps]
            if isinstance(join_keys, str):
                join_keys = [join_keys]
            return self.generate_records(
                application=application,
                inputs=inputs,
                outputs=outputs,
                feedbacks=feedbacks,
                global_tags=run_tags,
                row_tags=row_tags,
                timestamps=timestamps,
                join_keys=join_keys,
                run_id=run_id,
                version=version,
                sample_rate=sample_rate,
                sort_on_timestamp=sort_on_timestamp,
                ignore_inputs=ignore_inputs,
            )[0]
        else:
            # Log as a single call.
            if (
                isinstance(inputs, dict)
                and isinstance(outputs, dict)
                and isinstance(feedbacks, dict)
            ):
                return self.single_log_record(
                    application=application,
                    version=version,
                    inputs=inputs,
                    outputs=outputs,
                    feedback=feedbacks,
                    tags=tags,
                    timestamp=timestamps,
                    join_key=join_keys,
                    sample_rate=sample_rate,
                )
            else:
                return self.single_log_records(
                    application=application,
                    version=version,
                    inputs=inputs,
                    outputs=outputs,
                    feedbacks=feedbacks,
                    tags=tags,
                    row_tags=row_tags,
                    global_tags=global_tags,
                    timestamps=timestamps,
                    join_keys=join_keys,
                    as_batch=as_batch,
                    sort_on_timestamp=sort_on_timestamp,
                    sample_rate=sample_rate,
                )

    @_log_exception
    @typechecked
    def generate_records(  # noqa: C901
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[Union[List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        outputs: Optional[Union[List[Any], List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        feedbacks: Optional[Union[List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        sample_rate: float = 1.0,
        run_id: Optional[str] = None,
        tags: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        join_keys: Optional[Union[List[str], pd.Series]] = None,
        row_tags: Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]] = None,
        global_tags: Optional[Dict[str, str]] = None,
        feedback_keys: Optional[List[str]] = None,
        feedback_ids: Optional[Union[List[str], List[dict]]] = None,
    ):
        """
        Function to generate a batch of events containing predictions (inputs and outputs),
        feedback, or both simultaneously.
        To generate predictions using this method, both inputs and outputs must be passed.
        To generate feedbacks using this method, both join_keys and feedbacks must be passed.

        Args:
            application (str): Name of the application. Gantry validates and monitors data
                by function.
            version (optional, Union[int, str]): Version of the function schema to use for
                validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            inputs (Union[List[dict], pd.Dataframe]): A list of prediction inputs. `inputs[i]`
                is a dict of the features for the i-th prediction to be logged.
            outputs (Union[List[dict], pd.Dataframe]): A list of prediction outputs. `outputs[i]`
                should be the application output for the prediction with features `inputs[i]`.
            feedback_keys (optional, List[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for
                performance metric calculation, you will provide the values of the features
                in this list for Gantry to look up the corresponding prediction.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_keys' instead.
            feedback_ids (optional, List[str] or List[dict]): A list of prediction feedback ids.
                The i-th entry corresponds to the argument `feedback_ids` in
                :meth:`gantry.client.Gantry.log_predictions` for the i-th prediction event.
                If the feedback_id is a List[str], then the exact value of the i-th element in the
                list is used as the feedback join id for the i-th event.
                If the feedback_id is a Dict[str], then the values of the dictionary will be hashed
                to create a feedback join id for the i-th event.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_keys' instead.
            feedbacks (Union[List[dict], pd.DataFrame]): A list of feedbacks. `feedbacks[i]`
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
            tags (optional, Optional[Union[Dict[str, str], List[Dict[str, str]]]): A tag is a
                label that you assign to your data. E.g. you can specify which environment
                the data belongs to by setting "env" tag like this tags = {"env": "environment1"}
                if not assigned we will use Gantry client's environment value as the defaults
                environment. If this parameter is a dict, tags will apply to all records.
                Alternatively, you can pass a list of dicts to apply tags to each record
                independantly.
                IMPORTANT: this parameter is in deprecation mode and it will be removed soon.
                Use row_tags and global_tags instead.
            join_keys  (optional, Union[List[str], pd.Series[str]]): provide keys to identify
                each record. These keys can be used later to provide feedback. If not provided,
                a random record key will be generated for each record.
            row_tags (optional, Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]]): Specify row level tags.
                If provided, this parameter should be a list of tags to be applied to each of the records.
                row_tags[i] will contain a dictionary of strings containing the tags to attach to the
                i-th record. Alternatively, tags may be specified by passing in a DataFrame, Series,
                or Array, like inputs.
                For batch global tags, use the 'global_tags' parameter instead.
            global_tags (optional, Dict[str, str]): Specify a set of tags that will be attached to
                all ingested records from this batch. For record specific tags, you can use
                'row_tags' param.
        Returns:
            Tuple[batch_id, list[join_keys]]: The batch_id will be None if records are not
            logged as batch. The list of join_keys will be the records keys.
        """
        if tags:
            warn(
                "Deprecated: tags parameter is going to be removed soon. "
                "Use row_tags/global_tags instead."
            )

        if inputs is not None and isinstance(inputs, pd.Series):
            inputs = inputs.to_frame()
        if outputs is not None and isinstance(outputs, pd.Series):
            outputs = outputs.to_frame()
        if row_tags is not None and isinstance(row_tags, pd.Series):
            row_tags = row_tags.to_frame()
        if feedbacks is not None and isinstance(feedbacks, pd.Series):
            feedbacks = feedbacks.to_frame()
        if join_keys is not None and isinstance(join_keys, pd.Series):
            join_keys = join_keys.to_list()
            check_type("join_keys", join_keys, List[str])

        if timestamps is not None and isinstance(timestamps, np.ndarray):
            timestamps = timestamps.tolist()
            check_type("timestamps", timestamps, List[datetime.datetime])

        some_preds_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        preds_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedbacks_exist = _is_not_empty(feedbacks)

        if not preds_exist and some_preds_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        sizes = {}
        if row_tags is not None:
            row_tags = serializable_value(row_tags)
            check_type("row_tags", row_tags, List[Dict[str, str]])

        if feedbacks_exist:
            feedbacks = serializable_value(feedbacks)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("feedbacks", feedbacks, List[dict])
            sizes["feedback"] = len(feedbacks)  # type: ignore
        if preds_exist:
            inputs = serializable_value(inputs)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("inputs", inputs, List[dict])
            sizes["inputs"] = len(inputs)  # type: ignore

            outputs = serializable_value(outputs)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("outputs", outputs, List[dict])
            sizes["outputs"] = len(outputs)  # type: ignore

        if timestamps:
            sizes["timestamps"] = len(timestamps)  # type: ignore
        if join_keys:
            sizes["join_keys"] = len(join_keys)  # type: ignore
        if row_tags:
            sizes["row_tags"] = len(row_tags)  # type: ignore
        if tags and isinstance(tags, List):
            sizes["tags"] = len(tags)  # type: ignore

        unique_sizes = set(sizes.values())
        if len(unique_sizes) != 1:
            raise ValueError(f"Data sizes should match. Got {sizes}")

        size = list(unique_sizes)[0]

        if tags is None or isinstance(tags, Dict):
            tags = [copy.deepcopy(tags) if tags else {} for _ in range(size)]
            tags = cast(List[Dict[str, str]], tags)
        if global_tags:
            for t in tags:
                t.update(global_tags)
        if row_tags:
            for t, row_tag in zip(tags, row_tags):
                t.update(row_tag)

        for t in tags:
            _update_tags_with_env(self.environment, t)
        join_keys = _resolve_join_keys(size, inputs, feedback_ids, feedback_keys, join_keys)
        inputs, outputs, feedbacks, join_keys, timestamps, tags = _sample_records(
            size, sample_rate, inputs, outputs, feedbacks, join_keys, timestamps, tags
        )
        if preds_exist and feedbacks_exist:
            return self._generate_prediction_and_feedback_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                feedbacks=feedbacks,
                join_keys=join_keys or [_default_join_key_gen() for _ in range(size)],
                version=version,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                run_id=run_id,
                tags=tags,
            )
        elif preds_exist:
            return self._generate_prediction_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                join_keys=join_keys or [_default_join_key_gen() for _ in range(size)],
                version=version,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                run_id=run_id,
                tags=tags,
            )
        elif feedbacks_exist:
            if join_keys is None:
                raise ValueError(
                    "Can't submit feedback without submitting join_keys "
                    "(or feedback_ids/feedback_keys)"
                )
            return self._generate_feedback_events(
                application=application,
                feedbacks=feedbacks,
                join_keys=join_keys,
                feedback_version=version,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                run_id=run_id,
                tags=tags,
            )
        else:
            raise ValueError("Tried to log_records without prediction and without feedback")

    @_log_exception
    @typechecked
    def single_log_records(  # noqa: C901
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[Union[List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        outputs: Optional[Union[List[Any], List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        feedback_keys: Optional[List[str]] = None,
        feedback_ids: Optional[Union[List[str], List[dict]]] = None,
        feedbacks: Optional[Union[List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        sample_rate: float = 1.0,
        as_batch: bool = False,
        tags: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        join_keys: Optional[Union[List[str], pd.Series]] = None,
        row_tags: Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]] = None,
        global_tags: Optional[Dict[str, str]] = None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Function to record a batch of events containing predictions (inputs and outputs),
        feedback, or both simultaneously.
        To log predictions using this method, both inputs and outputs must be passed.
        To log feedbacks using this method, both join_keys and feedbacks must be passed.

        Args:
            application (str): Name of the application. Gantry validates and monitors data
                by function.
            version (optional, Union[int, str]): Version of the function schema to use for
                validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            inputs (Union[List[dict], pd.Dataframe]): A list of prediction inputs. `inputs[i]`
                is a dict of the features for the i-th prediction to be logged.
            outputs (Union[List[dict], pd.Dataframe]): A list of prediction outputs. `outputs[i]`
                should be the application output for the prediction with features `inputs[i]`.
            feedback_keys (optional, List[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for
                performance metric calculation, you will provide the values of the features
                in this list for Gantry to look up the corresponding prediction.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_keys' instead.
            feedback_ids (optional, List[str] or List[dict]): A list of prediction feedback ids.
                The i-th entry corresponds to the argument `feedback_ids` in
                :meth:`gantry.client.Gantry.log_predictions` for the i-th prediction event.
                If the feedback_id is a List[str], then the exact value of the i-th element in the
                list is used as the feedback join id for the i-th event.
                If the feedback_id is a Dict[str], then the values of the dictionary will be hashed
                to create a feedback join id for the i-th event.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_keys' instead.
            feedbacks (Union[List[dict], pd.DataFrame]): A list of feedbacks. `feedbacks[i]`
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
            tags (optional, Optional[Union[Dict[str, str], List[Dict[str, str]]]): A tag is a
                label that you assign to your data. E.g. you can specify which environment
                the data belongs to by setting "env" tag like this tags = {"env": "environment1"}
                if not assigned we will use Gantry client's environment value as the defaults
                environment. If this parameter is a dict, tags will apply to all records.
                Alternatively, you can pass a list of dicts to apply tags to each record
                independantly.
                IMPORTANT: this parameter is in deprecation mode and it will be removed soon.
                Use row_tags and global_tags instead.
            join_keys  (optional, Union[List[str], pd.Series[str]]): provide keys to identify
                each record. These keys can be used later to provide feedback. If not provided,
                a random record key will be generated for each record.
            row_tags (optional, Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]]): Specify row level tags.
                If provided, this parameter should be a list of tags to be applied to each of the records.
                row_tags[i] will contain a dictionary of strings containing the tags to attach to the
                i-th record. Alternatively, tags may be specified by passing in a DataFrame, Series,
                or Array, like inputs.
                For batch global tags, use the 'global_tags' parameter instead.
            global_tags (optional, Dict[str, str]): Specify a set of tags that will be attached to
                all ingested records from this batch. For record specific tags, you can use
                'row_tags' param.
        Returns:
            Tuple[batch_id, list[join_keys]]: The batch_id will be None if records are not
            logged as batch. The list of join_keys will be the records keys.
        """
        if tags:
            warn(
                "Deprecated: tags parameter is going to be removed soon. "
                "Use row_tags/global_tags instead."
            )

        if inputs is not None and isinstance(inputs, pd.Series):
            inputs = inputs.to_frame()
        if outputs is not None and isinstance(outputs, pd.Series):
            outputs = outputs.to_frame()
        if row_tags is not None and isinstance(row_tags, pd.Series):
            row_tags = row_tags.to_frame()
        if feedbacks is not None and isinstance(feedbacks, pd.Series):
            feedbacks = feedbacks.to_frame()
        if join_keys is not None and isinstance(join_keys, pd.Series):
            join_keys = join_keys.to_list()
            check_type("join_keys", join_keys, List[str])

        if timestamps is not None and isinstance(timestamps, np.ndarray):
            timestamps = timestamps.tolist()
            check_type("timestamps", timestamps, List[datetime.datetime])

        some_preds_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        preds_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedbacks_exist = _is_not_empty(feedbacks)

        if not preds_exist and some_preds_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        sizes = {}
        if row_tags is not None:
            row_tags = serializable_value(row_tags)
            check_type("row_tags", row_tags, List[Dict[str, str]])

        if feedbacks_exist:
            feedbacks = serializable_value(feedbacks)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("feedbacks", feedbacks, List[dict])
            sizes["feedback"] = len(feedbacks)  # type: ignore
        if preds_exist:
            inputs = serializable_value(inputs)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("inputs", inputs, List[dict])
            sizes["inputs"] = len(inputs)  # type: ignore

            outputs = serializable_value(outputs)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("outputs", outputs, List[dict])
            sizes["outputs"] = len(outputs)  # type: ignore

        if timestamps:
            sizes["timestamps"] = len(timestamps)  # type: ignore
        if join_keys:
            sizes["join_keys"] = len(join_keys)  # type: ignore
        if row_tags:
            sizes["row_tags"] = len(row_tags)  # type: ignore
        if tags and isinstance(tags, List):
            sizes["tags"] = len(tags)  # type: ignore

        unique_sizes = set(sizes.values())
        if len(unique_sizes) != 1:
            raise ValueError(f"Data sizes should match. Got {sizes}")

        size = list(unique_sizes)[0]

        if tags is None or isinstance(tags, Dict):
            tags = [copy.deepcopy(tags) if tags else {} for _ in range(size)]
            tags = cast(List[Dict[str, str]], tags)

        if global_tags:
            for t in tags:
                t.update(global_tags)
        if row_tags:
            for t, row_tag in zip(tags, row_tags):
                t.update(row_tag)

        for t in tags:
            _update_tags_with_env(self.environment, t)

        join_keys = _resolve_join_keys(size, inputs, feedback_ids, feedback_keys, join_keys)
        inputs, outputs, feedbacks, join_keys, timestamps, tags = _sample_records(
            size, sample_rate, inputs, outputs, feedbacks, join_keys, timestamps, tags
        )

        if preds_exist and feedbacks_exist:
            return self._log_prediction_and_feedback_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                feedbacks=feedbacks,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                tags=tags,
                join_keys=join_keys or [_default_join_key_gen() for _ in range(size)],
                version=version,
                as_batch=as_batch,
            )
        elif preds_exist:
            return self._log_prediction_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                tags=tags,
                join_keys=join_keys or [_default_join_key_gen() for _ in range(size)],
                version=version,
                as_batch=as_batch,
            )
        elif feedbacks_exist:
            if join_keys is None:
                raise ValueError(
                    "Can't submit feedback without submitting join_keys "
                    "(or feedback_ids/feedback_keys)"
                )
            return self._log_feedback_events(
                application=application,
                feedbacks=feedbacks,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                tags=tags,
                join_keys=join_keys,
                feedback_version=version,
                as_batch=as_batch,
            )
        else:
            raise ValueError("Tried to log_records without prediction and without feedback")

    @_log_exception
    @typechecked
    def single_log_record(
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[dict] = None,
        outputs: Optional[Any] = None,
        feedback_id: Optional[Union[str, dict]] = None,
        feedback: Optional[dict] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamp: Optional[datetime.datetime] = None,
        sample_rate: float = 1.0,
        tags: Optional[Dict[str, str]] = None,
        join_key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Function to record an event, regardless of inputs. Allows client to pass in inputs,
        predictions, and/or feedback for one record.
        Logs error for any individual failures, but does not fail unless method called with
        invalid parameters.
        To log predictions using this method, both inputs and outputs must be passed.
        To log feedback using this method, both join_key and feedback must be passed.

        Args:
            application (str): Name of the application. Gantry validates and monitors data by
                function.
            version (optional, Union[int, str]): Version of the function schema to use
                for validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            inputs (optional, dict): Inputs to the prediction. A dict where the keys are the feature
                names and the values are the feature values.
            outputs (optional, Any): application output on the prediction.
            feedback_id (optional, Dict[str, Any]): A dictionary mapping string keys to values on
                which the feedback id is computed for matching prediction and feedback events.
                Should be the same as the argument `feedback_id` to
                :meth:`gantry.client.Gantry.log_feedback_event` for the matching feedback event.
                DEPRECATION WARNING: this parameter will be removed soon. Use instead 'join_key'.
            feedback (optional, dict): application feedback object.
            feedback_keys (optional, list[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for performance
                metric calculation, you will provide the values of the features in this list for
                Gantry to look up the corresponding prediction.
                DEPRECATION WARNING: this parameter will be removed soon. Use instead 'join_key'.
            ignore_inputs (optional, list[str]): A list of names of input features that should not
                be monitored.
            timestamp (optional, datetime.datetime): Specify a custom timestamp for the when the
                prediction occured. Useful for recording predictions from the past. If not
                specified, then the prediction timestamp defaults to when `log_record` was
                called.
            sample_rate (optional, float): Specify the probability as a float that the event will
                be sent to Gantry.
            tags (optional, Optional[Dict[str, str]]): A tag is a label that you assign to your
                data. E.g. you can specify which environment the data belongs to by setting "env"
                tag like this tags = {"env": "environment1"} if not assigned we will use Gantry
                client's environment value as the default environment.
            join_key  (optional, str): provide a key to identify the record. This key can be used
                later to provide feedback to this record. If not provided, a random record key will
                be generated.
        Returns:
            The record key if record was logged. None in case the sample rate ommited this record.
        """
        # In order to keep backwards compatibility.
        # When feedback_keys and feedback_id get deprecated, this
        # line should just be 'join_key = join_key or _default_join_key_gen()'
        join_key = _resolve_join_key(inputs, feedback_id, feedback_keys, join_key)

        some_pred_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        pred_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedback_exist = _is_not_empty(feedback)

        tags = tags or {}
        _update_tags_with_env(self.environment, tags)

        if (not pred_exist) and some_pred_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        _check_sample_rate(sample_rate)
        if random.random() > sample_rate:
            return None

        if pred_exist and feedback_exist:
            return self._log_prediction_and_feedback_event(
                application=application,
                version=version,
                inputs=inputs,
                outputs=outputs,
                feedback=feedback,
                join_key=join_key or _default_join_key_gen(),
                ignore_inputs=ignore_inputs,
                timestamp=timestamp,
                tags=tags,
            )
        elif pred_exist:
            return self._log_prediction_event(
                application=application,
                inputs=inputs,
                outputs=outputs,
                join_key=join_key or _default_join_key_gen(),
                version=version,
                ignore_inputs=ignore_inputs,
                timestamp=timestamp,
                tags=tags,
            )
        elif feedback_exist:
            if join_key is None:
                raise ValueError(
                    "Can't submit feedback without submitting join_key "
                    "(or feedback_id/feedback_keys)"
                )

            return self._log_feedback_event(
                application=application,
                join_key=join_key,
                feedback=feedback,
                feedback_version=version,
                timestamp=timestamp,
                tags=tags,
            )
        else:
            logger.error("Tried to log record without prediction and without feedback")

        return None

    @_log_exception
    @typechecked
    def log_records(  # noqa: C901
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[Union[List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        outputs: Optional[Union[List[Any], List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        feedback_keys: Optional[List[str]] = None,
        feedback_ids: Optional[Union[List[str], List[dict]]] = None,
        feedbacks: Optional[Union[List[dict], pd.DataFrame, pd.Series, np.ndarray]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        sample_rate: float = 1.0,
        as_batch: bool = False,
        tags: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        join_keys: Optional[Union[List[str], pd.Series]] = None,
        row_tags: Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]] = None,
        global_tags: Optional[Dict[str, str]] = None,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Function to record a batch of events containing predictions (inputs and outputs),
        feedback, or both simultaneously.
        To log predictions using this method, both inputs and outputs must be passed.
        To log feedbacks using this method, both join_keys and feedbacks must be passed.

        Example:

        .. code-block:: python

            gantry.log_records(
                application='foobar',
                inputs=[{'A': 100}, {'A': 101}],
                outputs=[{'B': 'foo'}, {'B': 'bar'}],
                version=1,
                feedbacks=[{'B': 'bar'}, {'B': 'foo'}],
                tags={"env": "environment1"},
                join_keys=["12345", "67890"]
            )


        Args:
            application (str): Name of the application. Gantry validates and monitors data
                by function.
            version (optional, Union[int, str]): Version of the function schema to use for
                validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            inputs (Union[List[dict], pd.Dataframe]): A list of prediction inputs. `inputs[i]`
                is a dict of the features for the i-th prediction to be logged.
            outputs (Union[List[dict], pd.Dataframe]): A list of prediction outputs. `outputs[i]`
                should be the application output for the prediction with features `inputs[i]`.
            feedback_keys (optional, List[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for
                performance metric calculation, you will provide the values of the features
                in this list for Gantry to look up the corresponding prediction.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_keys' instead.
            feedback_ids (optional, List[str] or List[dict]): A list of prediction feedback ids.
                The i-th entry corresponds to the argument `feedback_ids` in
                :meth:`gantry.client.Gantry.log_predictions` for the i-th prediction event.
                If the feedback_id is a List[str], then the exact value of the i-th element in the
                list is used as the feedback join id for the i-th event.
                If the feedback_id is a Dict[str], then the values of the dictionary will be hashed
                to create a feedback join id for the i-th event.
                DEPRECATION WARNING: this parameter will be removed soon. Use 'join_keys' instead.
            feedbacks (Union[List[dict], pd.DataFrame]): A list of feedbacks. `feedbacks[i]`
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
            tags (optional, Optional[Union[Dict[str, str], List[Dict[str, str]]]): A tag is a
                label that you assign to your data. E.g. you can specify which environment
                the data belongs to by setting "env" tag like this tags = {"env": "environment1"}
                if not assigned we will use Gantry client's environment value as the defaults
                environment. If this parameter is a dict, tags will apply to all records.
                Alternatively, you can pass a list of dicts to apply tags to each record
                independantly.
                IMPORTANT: this parameter is in deprecation mode and it will be removed soon.
                Use row_tags and global_tags instead.
            join_keys  (optional, Union[List[str], pd.Series[str]]): provide keys to identify
                each record. These keys can be used later to provide feedback. If not provided,
                a random record key will be generated for each record.
            row_tags (optional, Optional[Union[List[Dict[str, str]], pd.DataFrame, pd.Series, np.ndarray]]): Specify row level tags.
                If provided, this parameter should be a list of tags to be applied to each of the records.
                row_tags[i] will contain a dictionary of strings containing the tags to attach to the
                i-th record. Alternatively, tags may be specified by passing in a DataFrame, Series,
                or Array, like inputs.
                For batch global tags, use the 'global_tags' parameter instead.
            global_tags (optional, Dict[str, str]): Specify a set of tags that will be attached to
                all ingested records from this batch. For record specific tags, you can use
                'row_tags' param.
        Returns:
            Tuple[batch_id, list[join_keys]]: The batch_id will be None if records are not
            logged as batch. The list of join_keys will be the records keys.
        """
        if tags:
            warn(
                "Deprecated: tags parameter is going to be removed soon. "
                "Use row_tags/global_tags instead."
            )

        if inputs is not None and isinstance(inputs, pd.Series):
            inputs = inputs.to_frame()
        if outputs is not None and isinstance(outputs, pd.Series):
            outputs = outputs.to_frame()
        if row_tags is not None and isinstance(row_tags, pd.Series):
            row_tags = row_tags.to_frame()
        if feedbacks is not None and isinstance(feedbacks, pd.Series):
            feedbacks = feedbacks.to_frame()
        if join_keys is not None and isinstance(join_keys, pd.Series):
            join_keys = join_keys.to_list()
            check_type("join_keys", join_keys, List[str])

        if timestamps is not None and isinstance(timestamps, np.ndarray):
            timestamps = timestamps.tolist()
            check_type("timestamps", timestamps, List[datetime.datetime])

        some_preds_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        preds_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedbacks_exist = _is_not_empty(feedbacks)

        if not preds_exist and some_preds_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        sizes = {}
        if row_tags is not None:
            row_tags = serializable_value(row_tags)
            check_type("row_tags", row_tags, List[Dict[str, str]])

        if feedbacks_exist:
            feedbacks = serializable_value(feedbacks)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("feedbacks", feedbacks, List[dict])
            sizes["feedback"] = len(feedbacks)  # type: ignore
        if preds_exist:
            inputs = serializable_value(inputs)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("inputs", inputs, List[dict])
            sizes["inputs"] = len(inputs)  # type: ignore

            outputs = serializable_value(outputs)
            # Check in case this was an np.array
            # Reference https://github.com/gantry-ml/gantry/pull/3341
            check_type("outputs", outputs, List[dict])
            sizes["outputs"] = len(outputs)  # type: ignore

        if timestamps:
            sizes["timestamps"] = len(timestamps)  # type: ignore
        if join_keys:
            sizes["join_keys"] = len(join_keys)  # type: ignore
        if row_tags:
            sizes["row_tags"] = len(row_tags)  # type: ignore
        if tags and isinstance(tags, List):
            sizes["tags"] = len(tags)  # type: ignore

        unique_sizes = set(sizes.values())
        if len(unique_sizes) != 1:
            raise ValueError(f"Data sizes should match. Got {sizes}")

        size = list(unique_sizes)[0]

        if tags is None or isinstance(tags, Dict):
            tags = [copy.deepcopy(tags) if tags else {} for _ in range(size)]
            tags = cast(List[Dict[str, str]], tags)

        if global_tags:
            for t in tags:
                t.update(global_tags)
        if row_tags:
            for t, row_tag in zip(tags, row_tags):
                t.update(row_tag)

        for t in tags:
            _update_tags_with_env(self.environment, t)

        join_keys = _resolve_join_keys(size, inputs, feedback_ids, feedback_keys, join_keys)
        inputs, outputs, feedbacks, join_keys, timestamps, tags = _sample_records(
            size, sample_rate, inputs, outputs, feedbacks, join_keys, timestamps, tags
        )

        if preds_exist and feedbacks_exist:
            return self._log_prediction_and_feedback_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                feedbacks=feedbacks,
                join_keys=join_keys or [_default_join_key_gen() for _ in range(size)],
                version=version,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                as_batch=as_batch,
                tags=tags,
            )
        elif preds_exist:
            return self._log_prediction_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                join_keys=join_keys or [_default_join_key_gen() for _ in range(size)],
                version=version,
                ignore_inputs=ignore_inputs,
                timestamps=timestamps,
                sort_on_timestamp=sort_on_timestamp,
                as_batch=as_batch,
                tags=tags,
            )
        elif feedbacks_exist:
            if join_keys is None:
                raise ValueError(
                    "Can't submit feedback without submitting join_keys "
                    "(or feedback_ids/feedback_keys)"
                )

            return self._log_feedback_events(
                application,
                feedbacks,
                join_keys,
                version,
                timestamps,
                sort_on_timestamp,
                as_batch,
                tags,
            )
        else:
            raise ValueError("Tried to log_records without prediction and without feedback")

    @_log_exception
    @typechecked
    def log_record(
        self,
        application: str,
        version: Optional[Union[int, str]] = None,
        inputs: Optional[dict] = None,
        outputs: Optional[Any] = None,
        feedback_id: Optional[Union[str, dict]] = None,
        feedback: Optional[dict] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamp: Optional[datetime.datetime] = None,
        sample_rate: float = 1.0,
        tags: Optional[Dict[str, str]] = None,
        join_key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Function to record an event, regardless of inputs. Allows client to pass in inputs,
        predictions, and/or feedback for one record.

        Logs error for any individual failures, but does not fail unless method called with
        invalid parameters.

        To log predictions using this method, both inputs and outputs must be passed.
        To log feedback using this method, both join_key and feedback must be passed.

        Example:

        .. code-block:: python

            # Record an application's prediction
            gantry.log_record(
                application='foobar',
                inputs={'A': 100},
                outputs={'prediction': True},
                version=1,
                tags = {"env":"environment1"},
                join_key='12345'
            )

            # Record an application's feedback
            # to a previously ingested prediction.
            gantry.log_record(
                application='foobar',
                feedback={'prediction': False},
                join_key='12345'
            )


        Args:
            application (str): Name of the application. Gantry validates and monitors data by
                function.
            version (optional, Union[int, str]): Version of the function schema to use
                for validation by Gantry.
                If not provided, Gantry will use the latest version. If the version doesn't exist
                yet, Gantry will create it by auto-generating the schema based on data it has seen.
                Providing an int or its value stringified has no difference
                (e.g. version=10 will be the same as version='10').
            inputs (optional, dict): Inputs to the prediction. A dict where the keys are the feature
                names and the values are the feature values.
            outputs (optional, Any): application output on the prediction.
            feedback_id (optional, Dict[str, Any]): A dictionary mapping string keys to values on
                which the feedback id is computed for matching prediction and feedback events.
                Should be the same as the argument `feedback_id` to
                :meth:`gantry.client.Gantry.log_feedback_event` for the matching feedback event.
                DEPRECATION WARNING: this parameter will be removed soon. Use instead 'join_key'.
            feedback (optional, dict): application feedback object.
            feedback_keys (optional, list[str]): A list of names of input features to use for
                feedback lookup. When you later provide a feedback event or label for performance
                metric calculation, you will provide the values of the features in this list for
                Gantry to look up the corresponding prediction.
                DEPRECATION WARNING: this parameter will be removed soon. Use instead 'join_key'.
            ignore_inputs (optional, list[str]): A list of names of input features that should not
                be monitored.
            timestamp (optional, datetime.datetime): Specify a custom timestamp for the when the
                prediction occured. Useful for recording predictions from the past. If not
                specified, then the prediction timestamp defaults to when `log_record` was
                called.
            sample_rate (optional, float): Specify the probability as a float that the event will
                be sent to Gantry.
            tags (optional, Optional[Dict[str, str]]): A tag is a label that you assign to your
                data. E.g. you can specify which environment the data belongs to by setting "env"
                tag like this tags = {"env": "environment1"} if not assigned we will use Gantry
                client's environment value as the default environment.
            join_key  (optional, str): provide a key to identify the record. This key can be used
                later to provide feedback to this record. If not provided, a random record key will
                be generated.

        Returns:
            The record key if record was logged. None in case the sample rate ommited this record.

        """
        warn("Deprecated: log_record is going to be removed soon. " "Use log() instead.")
        # In order to keep backwards compatibility.
        # When feedback_keys and feedback_id get deprecated, this
        # line should just be 'join_key = join_key or _default_join_key_gen()'
        join_key = _resolve_join_key(inputs, feedback_id, feedback_keys, join_key)

        some_pred_exist = _is_not_empty(inputs) or _is_not_empty(outputs)
        pred_exist = _is_not_empty(inputs) and _is_not_empty(outputs)
        feedback_exist = _is_not_empty(feedback)

        tags = tags or {}
        _update_tags_with_env(self.environment, tags)

        if (not pred_exist) and some_pred_exist:
            raise ValueError(
                "Tried to log records with incomplete prediction "
                "(both inputs and outputs should be provided)"
            )

        _check_sample_rate(sample_rate)
        if random.random() > sample_rate:
            return None

        if pred_exist and feedback_exist:
            return self._log_prediction_and_feedback_event(
                application=application,
                version=version,
                inputs=inputs,
                outputs=outputs,
                feedback=feedback,
                join_key=join_key or _default_join_key_gen(),
                ignore_inputs=ignore_inputs,
                timestamp=timestamp,
                tags=tags,
            )
        elif pred_exist:
            return self._log_prediction_event(
                application=application,
                inputs=inputs,
                outputs=outputs,
                join_key=join_key or _default_join_key_gen(),
                version=version,
                ignore_inputs=ignore_inputs,
                timestamp=timestamp,
                tags=tags,
            )
        elif feedback_exist:
            if join_key is None:
                raise ValueError(
                    "Can't submit feedback without submitting join_key "
                    "(or feedback_id/feedback_keys)"
                )

            return self._log_feedback_event(
                application=application,
                join_key=join_key,
                feedback=feedback,
                feedback_version=version,
                timestamp=timestamp,
                tags=tags,
            )
        else:
            logger.error("Tried to log record without prediction and without feedback")

        return None

    @_log_exception
    def ping(self) -> bool:
        """
        Pings the log store API server to check if it is alive.
        Returns True if alive, False if there is an error during ping process.
        """
        return self.log_store.ping()

    @_log_exception
    def ready(self) -> bool:
        """
        Checks if the configured API key authenticates with the API.
        Returns True if ready, False otherwise.
        """
        return self.log_store.ready()

    @_log_exception
    def _log_prediction_and_feedback_events(
        self,
        application: str,
        inputs: List[dict],
        outputs: List[dict],
        feedbacks: List[dict],
        join_keys: List[str],
        version: Optional[Union[int, str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        as_batch: bool = False,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[Optional[str], List[str]]:
        """Internal method to log batch of predictions AND feedbacks
        This method can assume inputs/outputs/feedbacks/timestamps/tags have same size
        """
        size = len(inputs)

        timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, size)

        events = _build_prediction_and_feedback_events(
            application=application,
            timestamp_idx=timestamp_idx,
            tags=tags,
            version=version,
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            join_keys=join_keys,
            ignore_inputs=ignore_inputs,
        )

        if events:
            if as_batch:
                return (
                    self._upload_data_as_batch(application, version, events, BatchType.RECORD),
                    join_keys,
                )
            else:
                self.log_store.log_batch(application, events)
        else:
            logger.info("No events to log")

        return None, join_keys

    @_log_exception
    def _generate_prediction_and_feedback_events(
        self,
        application: str,
        inputs: List[dict],
        outputs: List[dict],
        feedbacks: List[dict],
        join_keys: List[str],
        version: Optional[Union[int, str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        run_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ):
        """Internal method to generate batch of predictions AND feedbacks as list of events.
        This method can assume inputs/outputs/feedbacks/timestamps/tags have same size
        """
        size = len(inputs)

        timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, size)

        events = _build_prediction_and_feedback_events(
            application=application,
            timestamp_idx=timestamp_idx,
            tags=tags,
            version=version,
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            join_keys=join_keys,
            ignore_inputs=ignore_inputs,
            run_id=run_id,
        )

        return events, join_keys

    @_log_exception
    def _log_prediction_and_feedback_event(
        self,
        application: str,
        inputs: dict,
        outputs: Any,
        feedback: Optional[dict],
        join_key: str,
        version: Optional[Union[int, str]] = None,
        feedback_keys: Optional[List[str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamp: Optional[datetime.datetime] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """Internal method to log an event with prediction AND feedback"""
        ev = {}

        ev.update(
            _build_prediction_event(
                inputs,  # type: ignore
                outputs,
                application,
                join_key,
                version,
                ignore_inputs,
                custom_timestamp=timestamp,
                tags=tags,
            )
        )

        fev = _build_feedback_event(
            application,
            join_key,
            feedback,  # type: ignore
            version,
            timestamp,
            tags=tags,
        )

        ev["metadata"].update(fev.pop("metadata"))  # update nested dict separately
        ev.update(fev)
        self.log_store.log(application, ev)
        return join_key

    @_log_exception
    def _log_feedback_event(
        self,
        application: str,
        join_key: str,
        feedback: dict,
        feedback_version: Optional[Union[str, int]] = None,
        timestamp: Optional[datetime.datetime] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """Internal method to log a feedback event"""
        ev = _build_feedback_event(
            application,
            join_key,
            feedback,
            feedback_version,
            timestamp,
            tags=tags,
        )
        self.log_store.log(application, ev)
        return join_key

    @_log_exception
    def _generate_feedback_events(
        self,
        application: str,
        feedbacks: List[dict],
        join_keys: List[str],
        feedback_version: Optional[Union[str, int]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        run_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ):
        """Internal method to generate batch of feedback events
        This method can assume feedbacks/join_keys/timestamps have same size
        """
        timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, len(feedbacks))

        if len(join_keys) == len(feedbacks):
            events = []
            for idx, timestamp in timestamp_idx:
                try:
                    events.append(
                        _build_feedback_event(
                            application,
                            join_keys[idx],
                            feedbacks[idx],
                            feedback_version,
                            timestamp,
                            batch_id=run_id,
                            tags=tags[idx] if tags else None,
                        )
                    )
                except GantryLoggingException as le:
                    # this is caused by a user error
                    # log the error without the stacktrace
                    logger.error("Error generating logging data to Gantry: %s", le)
                except Exception as e:
                    logger.error(
                        "Failed to generate feedback with id {} due to {}".format(join_keys[idx], e)
                    )
        else:
            raise GantryLoggingException("Feedback_ids and feedbacks lists don't have same length.")

        return events, join_keys

    @_log_exception
    def _log_feedback_events(
        self,
        application: str,
        feedbacks: List[dict],
        join_keys: List[str],
        feedback_version: Optional[Union[str, int]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        as_batch: bool = False,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[Optional[str], List[str]]:
        """Internal method to log batch of feedback events
        This method can assume feedbacks/join_keys/timestamps have same size
        """
        batch_id = None
        try:
            timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, len(feedbacks))

            if len(join_keys) == len(feedbacks):
                events = []
                for idx, timestamp in timestamp_idx:
                    try:
                        events.append(
                            _build_feedback_event(
                                application,
                                join_keys[idx],
                                feedbacks[idx],
                                feedback_version,
                                timestamp,
                                batch_id=batch_id,
                                tags=tags[idx] if tags else None,
                            )
                        )
                    except GantryLoggingException as le:
                        # this is caused by a user error
                        # log the error without the stacktrace
                        logger.error("Error logging data to Gantry: %s", le)
                    except Exception as e:
                        logger.error(
                            "Failed to log feedback with id {} due to {}".format(join_keys[idx], e)
                        )

                if events:
                    if as_batch:
                        return (
                            self._upload_data_as_batch(
                                application,
                                feedback_version,
                                events,
                                BatchType.FEEDBACK,
                            ),
                            join_keys,
                        )
                    else:
                        batch_id = None
                        self.log_store.log_batch(application, events)
                        _batch_success_msg(batch_id, application, self.log_store)
                else:
                    raise ValueError("No events to log")
            else:
                raise GantryLoggingException(
                    "Feedback_ids and feedbacks lists don't have same length."
                )
        except Exception as e:
            _batch_fail_msg(batch_id)

            raise e

        return None, join_keys

    @_log_exception
    def _log_prediction_event(
        self,
        application: str,
        inputs: dict,
        outputs: Any,
        join_key: str,
        version: Optional[Union[int, str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamp: Optional[datetime.datetime] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """Internal method to log a prediction event"""
        ev = _build_prediction_event(
            inputs,
            outputs,
            application,
            join_key,
            version,
            ignore_inputs,
            custom_timestamp=timestamp,
            tags=tags,
        )
        self.log_store.log(application, ev)
        return join_key

    @_log_exception
    def _generate_prediction_events(
        self,
        application: str,
        inputs: List[dict],
        outputs: List[dict],
        join_keys: List[str],
        version: Optional[Union[int, str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        run_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Internal method to generate a batch of prediction events.
        Assume inputs/outputs/join_keys/timestamps have same size
        """
        timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, len(inputs))
        events = _build_prediction_events(
            application=application,
            inputs=inputs,
            outputs=outputs,
            timestamp_idx=timestamp_idx,
            tags=tags,
            version=version,
            join_keys=join_keys,
            ignore_inputs=ignore_inputs,
            batch_id=run_id,
        )
        return events, join_keys

    @_log_exception
    def _log_prediction_events(
        self,
        application: str,
        inputs: List[dict],
        outputs: List[dict],
        join_keys: List[str],
        version: Optional[Union[int, str]] = None,
        ignore_inputs: Optional[List[str]] = None,
        timestamps: Optional[Union[List[datetime.datetime], pd.DatetimeIndex, np.ndarray]] = None,
        sort_on_timestamp: bool = True,
        as_batch: bool = False,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[Optional[str], List[str]]:
        """Internal method to log a batch of prediction events
        This method can assume inputs/outputs/join_keys/timestamps have same size
        """
        batch_id = None
        try:
            timestamp_idx = _create_timestamp_idx(sort_on_timestamp, timestamps, len(inputs))

            events = _build_prediction_events(
                application=application,
                inputs=inputs,
                outputs=outputs,
                timestamp_idx=timestamp_idx,
                tags=tags,
                version=version,
                join_keys=join_keys,
                ignore_inputs=ignore_inputs,
                batch_id=batch_id,
            )

            if events:
                if as_batch:
                    return (
                        self._upload_data_as_batch(
                            application, version, events, BatchType.PREDICTION
                        ),
                        join_keys,
                    )
                else:
                    batch_id = None
                    self.log_store.log_batch(application, events)
                    _batch_success_msg(batch_id, application, self.log_store)
            else:
                logger.info("No events to log")
        except Exception as e:
            _batch_fail_msg(batch_id)
            raise e

        return None, join_keys

    def _upload_data_as_batch(
        self,
        application: str,
        version: Optional[Union[str, int]],
        events: List,
        batch_type: BatchType,
        run_id: Optional[str] = None,
        run_name: Optional[str] = None,
        run_tags: Optional[Dict] = None,
    ) -> str:
        data_link = DataLink(
            file_type=UploadFileType.EVENTS,
            batch_type=batch_type,
            num_events=len(events),
            application=application,
            version=str(version) if isinstance(version, int) else version,
            log_timestamp=datetime.datetime.utcnow().isoformat(),
            batch_id=run_id,
            run_name=run_name,
            run_tags=run_tags,
        )
        events_bytesize = sys.getsizeof(json.dumps(events, cls=EventEncoder).encode("utf-8"))
        batch_count = int(
            CHUNK_SIZE / (events_bytesize / data_link.num_events)
        )  # max file chunk size / average event size -> count of batch events to get to chunk.
        return self._handle_upload(
            _build_batch_iterator(events, batch_count),
            data_link,
            events_bytesize,
            f"{application}_{uuid.uuid4()}",
        )

    @staticmethod
    def setup_logger(level="INFO"):
        if not level:
            return

        pkg_logger = logging.getLogger("gantry")
        pkg_logger.setLevel(level)

        existing_handlers = pkg_logger.handlers
        for handler in existing_handlers:
            if isinstance(handler, logging.StreamHandler):
                return
        formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        pkg_logger.addHandler(handler)
