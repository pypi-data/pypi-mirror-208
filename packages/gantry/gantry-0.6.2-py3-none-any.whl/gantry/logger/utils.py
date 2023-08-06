import ast
import concurrent
import datetime
import functools
import hashlib
import json
import logging
import os
import subprocess
import urllib
import warnings
from dataclasses import dataclass, field
from itertools import islice
from typing import Any, Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd
import requests
from typeguard import typechecked

from gantry.exceptions import GantryBatchCreationException, GantryLoggingException
from gantry.logger.constants import BatchType, UploadFileType
from gantry.logger.stores import APILogStore, BaseLogStore
from gantry.logger.types import DataLink, DataLinkElement
from gantry.serializers import EventEncoder

logger = logging.getLogger(__name__)


def _log_exception(func):
    """Handles all exceptions thrown by func, and logs them to prevent the
    func call from crashing.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GantryLoggingException as le:
            # this is caused by a user error
            # log the error without the stacktrace
            logger.error("Error logging data to Gantry: %s", le)
        except GantryBatchCreationException as e:
            # Blocking exception for batch creation failure
            raise e
        except Exception as e:
            # make sure our logging errors don't cause exceptions in main program
            logger.exception("Internal exception in Gantry client: %s", e)

    return wrapper


def _is_empty(data: Union[List[Any], pd.DataFrame, Any] = None) -> bool:
    """
    Check whether input data is empty or not
    Returns True if data is None or empty, False if data size >= 1
    """
    if isinstance(data, pd.DataFrame):
        return data.empty
    elif isinstance(data, np.ndarray):
        return data.size == 0
    return True if not data else False


def _is_not_empty(data: Union[List[Any], pd.DataFrame, Any] = None) -> bool:
    return not _is_empty(data)


def _batch_fail_msg(batch_id):
    if batch_id:
        logger.info(f"Batch with id: {batch_id} FAILED")


def _check_sample_rate(sample_rate):
    assert sample_rate <= 1 and sample_rate >= 0


def _build_success_msg(host: str, application: str) -> str:
    return "Track your batch at {}applications/{}/jobs".format(
        host if host.endswith("/") else f"{host}/", urllib.parse.quote(application)
    )


def _batch_success_msg(batch_id, application, log_store: Union[APILogStore, BaseLogStore]):
    if batch_id:
        if isinstance(log_store, APILogStore):
            host = log_store._api_client._host
        else:
            host = "[YOUR_GANTRY_DASHBOARD]"

        logger.info(_build_success_msg(host, application))
        logger.info("Look for batch id: {}".format(batch_id))


def get_file_linecount(filepath):
    """
    'wc -l' will count the number of \n characters, but if the last line is missing the
    \n then it will miss it. So we add one if the last line is missing \n but is not empty.

    This needs to be a high performance function that works even for larger files.
    - https://stackoverflow.com/questions/845058
    - https://stackoverflow.com/questions/46258499
    """
    with open(filepath, "rb") as f:
        try:  # catch OSError in case of a one line file
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()

    line_count = int(subprocess.check_output(["wc", "-l", filepath]).split()[0])
    if len(last_line) > 0 and not last_line.endswith("\n"):
        line_count += 1
    return line_count


def _build_batch_iterator(iterable, batch_size):
    iterator = iter(iterable)
    batch = islice(iterator, batch_size)
    while batch:
        lines = "\n".join(map(lambda e: json.dumps(e, cls=EventEncoder), batch))
        batch = list(islice(iterator, batch_size))
        if batch:
            lines += "\n"
        yield lines.encode("utf-8")


def _put_block(url: str, part_num: int, block: bytes) -> dict:
    response = requests.put(url, data=block)
    etag = str(response.headers["ETag"])
    return {"ETag": etag, "PartNumber": part_num}


def _concurrent_upload_multipart_batch(
    data_batch_iterator: Iterable[bytes], signed_urls: List[str]
) -> List[dict]:
    """Uploads batches to presigned URLs concurrently using threads"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        logger.info("Starting multipart upload")
        futures = [
            executor.submit(_put_block, signed_urls[i], i + 1, block)
            for i, block in enumerate(data_batch_iterator)
        ]
        parts = [f.result() for f in concurrent.futures.as_completed(futures)]
        logger.info("Multipart upload complete")
        return sorted(parts, key=lambda d: d["PartNumber"])  # type: ignore


class JoinKey(str):
    @classmethod
    @typechecked
    def from_dict(cls, dict_: Dict) -> str:
        return hashlib.md5(
            json.dumps(dict_, sort_keys=True, cls=EventEncoder).encode("utf-8")
        ).hexdigest()


def _get_csv_columns(filepath: str, sep: str) -> List[str]:
    ret = []
    columns = pd.read_csv(filepath, sep=sep, nrows=0).columns.tolist()
    for c in columns:
        try:
            # Safe alternative to 'eval'
            # converts quoted header into unquoted header
            # Raise ValueError in case value is not
            # quoted string
            ret.append(ast.literal_eval(c.strip()))
        except ValueError:
            ret.append(c.strip())
    return ret


def _validate_columns(targets: List[str], columns: List[str]) -> None:
    for t in targets:
        _validate_column(t, columns)


def _validate_column(target: str, columns: List[str]) -> None:
    if target not in columns:
        raise ValueError(f"Column '{target}' not in available columns: {columns}")


@dataclass
class _FeatureToColumnMapping:
    timestamp: Dict[str, DataLinkElement] = field(default_factory=dict)
    inputs: Dict[str, DataLinkElement] = field(default_factory=dict)
    outputs: Dict[str, DataLinkElement] = field(default_factory=dict)
    feedback: Dict[str, DataLinkElement] = field(default_factory=dict)
    tags: Dict[str, DataLinkElement] = field(default_factory=dict)
    feedback_id: Dict[str, DataLinkElement] = field(default_factory=dict)
    feedback_keys: List[str] = field(default_factory=list)

    _join_key: Dict[str, DataLinkElement] = field(default_factory=dict)

    @classmethod
    def from_columns(  # noqa: C901
        cls,
        columns: List[str],
        inputs: Optional[List[str]],
        outputs: Optional[List[str]],
        feedback: Optional[List[str]],
        tags: Optional[List[str]],
        timestamp: Optional[str],
        feedback_id: Optional[str],
        feedback_keys: Optional[List[str]],
        join_key: Optional[str],
    ):
        # Validate custom columns exist
        for feature in [inputs, outputs, feedback, tags, feedback_keys]:
            _validate_columns(feature or [], columns)

        if timestamp is not None:
            _validate_column(timestamp, columns)
        if feedback_id is not None:
            _validate_column(feedback_id, columns)

        ret = cls()
        for col_index, col in enumerate(columns):
            if (inputs is None and col.startswith("input")) or (
                inputs is not None and col in inputs
            ):
                ret.inputs[col] = DataLinkElement(ref=col_index)
            elif (outputs is None and col.startswith("output")) or (
                outputs is not None and col in outputs
            ):
                ret.outputs[col] = DataLinkElement(ref=col_index)
            elif (feedback is None and col.startswith("feedback")) or (
                feedback is not None and col in feedback
            ):
                ret.feedback[col] = DataLinkElement(ref=col_index)
            elif (tags is None and col.startswith("tags")) or (tags is not None and col in tags):
                ret.tags[col] = DataLinkElement(ref=col_index)
            elif col == timestamp or (timestamp is None and col == "timestamp"):
                ret.timestamp[col] = DataLinkElement(ref=col_index)
            elif col == feedback_id or (feedback_id is None and col == "feedback_id"):
                ret.feedback_id[col] = DataLinkElement(ref=col_index)
            elif col == join_key or (join_key is None and col == "join_key"):
                ret._join_key[col] = DataLinkElement(ref=col_index)
            elif feedback_keys is not None and col in feedback_keys:
                ret.feedback_keys.append(col)

        if ret._join_key:
            if ret.feedback_id or ret.feedback_keys:
                raise ValueError(
                    "Cannot provide 'join_key' with 'feedback_id/feedback_keys' "
                    "'feedback_id/feedback_keys' are in deprecation mode. Use "
                    "'join_key' instead"
                )

            ret.feedback_id = ret._join_key
        elif ret.feedback_id:
            warnings.warn("'feedback_id/feedback_keys' will be deprecated in favor" "of join_key")

        return ret

    def validate(self) -> None:
        if not self.inputs and not self.outputs and not self.feedback:
            raise ValueError(
                "No referenced data found after mapping column names to features. "
                "Are column names correctly mapped? See the documentation for further information"
            )

        if (self.inputs and not self.outputs) or (not self.inputs and self.outputs):
            raise ValueError(
                "Providing inputs and no outputs (or the other way around) is not valid."
            )

        # TODO -> verify this is actually an error
        if self.feedback and not self.feedback_id:
            raise ValueError(
                "In order to provide feedback you need to reference feedback_id as well"
            )

    def get_batch_type(self) -> BatchType:
        if not self.inputs and not self.outputs and self.feedback:
            return BatchType.FEEDBACK

        if self.inputs and self.outputs and self.feedback:
            return BatchType.RECORD

        return BatchType.PREDICTION


def _build_data_link_from_file(  # noqa: C901
    application: str,
    filepath: str,
    sep: str,
    version: Optional[str],
    timestamp: Optional[str],
    inputs: Optional[List[str]],
    outputs: Optional[List[str]],
    feedback: Optional[List[str]],
    tags: Optional[List[str]],
    feedback_id: Optional[str],
    feedback_keys: Optional[List[str]],
    join_key: Optional[str],
) -> DataLink:
    columns = _get_csv_columns(filepath, sep)
    feature_to_columns = _FeatureToColumnMapping.from_columns(
        columns, inputs, outputs, feedback, tags, timestamp, feedback_id, feedback_keys, join_key
    )
    feature_to_columns.validate()

    return DataLink(
        file_type=UploadFileType.CSV_WITH_HEADERS,
        batch_type=feature_to_columns.get_batch_type(),
        num_events=get_file_linecount(filepath) - 1,  # Subtract the header line.
        application=application,
        version=version,
        log_timestamp=datetime.datetime.utcnow().isoformat(),
        inputs=feature_to_columns.inputs,
        outputs=feature_to_columns.outputs,
        feedback=feature_to_columns.feedback,
        timestamp=feature_to_columns.timestamp,
        feedback_id=feature_to_columns.feedback_id,
        feedback_keys=feature_to_columns.feedback_keys,
        tags=feature_to_columns.tags,
    )
