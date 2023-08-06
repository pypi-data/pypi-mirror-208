import datetime
import logging
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from gantry.exceptions import GantryLoggingException
from gantry.utils import check_event_time_in_future
from gantry.validators import validate_logged_field_datatype

logger = logging.getLogger(__name__)


def _build_prediction_and_feedback_events(
    application: str,
    timestamp_idx: Iterable,
    inputs: List[dict],
    outputs: Union[List[dict], List[Any]],
    feedbacks: List[dict],
    join_keys: List[str],
    version: Optional[Union[str, int]] = None,
    ignore_inputs: Optional[List[str]] = None,
    tags: Optional[List[Dict[str, str]]] = None,
    run_id: Optional[str] = None,
):
    """Build prediction and feedback events for log_records"""
    events = []
    for idx, timestamp in timestamp_idx:
        event = {}

        event.update(
            _build_prediction_event(
                inputs[idx],
                outputs[idx],
                application,
                join_keys[idx],
                version,
                ignore_inputs,
                custom_timestamp=timestamp,
                tags=tags[idx] if tags else None,
                batch_id=run_id,
            )
        )

        feedback_event = _build_feedback_event(
            application,
            join_keys[idx],
            feedbacks[idx],
            version,  # type: ignore
            timestamp,
            tags=tags[idx] if tags else None,
            batch_id=run_id,
        )

        # Build an event with prediction data
        # and feedback data, now that backend
        # supports it.
        event["metadata"].update(feedback_event.pop("metadata"))
        event.update(feedback_event)

        events.append(event)

    return events


def _create_timestamp_idx(
    sort_on_timestamp: bool,
    timestamps: Optional[Iterable[Any]],
    record_count: int,
) -> Iterable:
    """
    This function is used to take an index of timestamps, possibly None, and a length,
    and turn it into a mapping from the current timestamp to the original index of the
    corresponding value. The goal is to send all data to Gantry in timestamp order to
    minimize summarization window computing overhead by packing events of a single
    window into a single task.
    """
    if timestamps is not None:
        timestamp_idx: Iterable[Tuple[int, Any]] = enumerate(timestamps)
        if sort_on_timestamp:
            timestamp_idx = sorted(timestamp_idx, key=lambda el: el[1])
    else:
        timestamp = datetime.datetime.utcnow()
        timestamp_idx = ((i, timestamp) for i in range(record_count))

    return timestamp_idx


def _enrich_events_with_batch_id(events, batch_id):
    for event in events:
        event["batch_id"] = batch_id


def _build_feedback_event(
    application: str,
    join_key: str,
    feedback: dict,
    feedback_version: Optional[Union[str, int]] = None,
    timestamp: Optional[datetime.datetime] = None,
    batch_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> dict:
    """
    Create a feedback event record for logging.
    """
    metadata: Dict[str, Any] = {}
    metadata.update({"func_name": application, "feedback_version": feedback_version})

    log_time = datetime.datetime.utcnow()
    event_time = timestamp if timestamp else log_time
    if check_event_time_in_future(event_time):
        raise GantryLoggingException(
            "Cannot log events from the future. "
            f"Event timestep is {event_time}, but current time is {log_time}. "
            "Please check your event times and re-submit all."
        )
    log_time_str, event_time_str = log_time.isoformat(), event_time.isoformat()

    validate_logged_field_datatype(feedback, paths=["feedback"])
    validate_logged_field_datatype(event_time_str, paths=["timestamp"])

    return {
        "event_id": uuid.uuid4(),
        "timestamp": event_time_str,
        "log_timestamp": log_time_str,
        "metadata": metadata,
        "feedback": feedback,
        "feedback_id": join_key,
        "batch_id": batch_id,
    }


def _build_prediction_events(
    application: str,
    inputs: List[dict],
    outputs: Union[List[dict], List[Any]],
    timestamp_idx: Iterable,
    version: Optional[Union[str, int]],
    join_keys: List[str],
    ignore_inputs: Optional[List[str]] = None,
    batch_id: Optional[str] = None,
    tags: Optional[List[Dict[str, str]]] = None,
):
    events = []
    for idx, timestamp in timestamp_idx:

        events.append(
            _build_prediction_event(
                inputs[idx],
                outputs[idx],
                application,
                join_keys[idx],
                version,
                ignore_inputs,
                batch_id=batch_id,
                custom_timestamp=timestamp,
                tags=tags[idx] if tags else None,
            )
        )

    return events


def _build_prediction_event(
    inputs: Dict,
    outputs: Any,
    application: str,
    join_key: str,
    version: Optional[Union[int, str]],
    ignore_inputs: Optional[List[str]],
    batch_id: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    custom_timestamp: Optional[datetime.datetime] = None,
):
    metadata = {}
    metadata.update(
        {
            "func_name": application,
            "version": version,
            "feedback_keys": None,  # TODO -> see if this can be removed
            "ignore_inputs": ignore_inputs,
        }
    )
    inputs = dict(inputs)  # make a copy so we can pop keys safely

    if ignore_inputs:
        for ignore in ignore_inputs:
            inputs.pop(ignore, None)

    log_time = datetime.datetime.utcnow()
    event_time = custom_timestamp if custom_timestamp else log_time
    if check_event_time_in_future(event_time):
        raise GantryLoggingException(
            "Cannot log events from the future. "
            f"Event timestep is {event_time}, but current time is {log_time}. "
            "Please check your event times and re-submit all."
        )
    log_time_str, event_time_str = log_time.isoformat(), event_time.isoformat()

    validate_logged_field_datatype(inputs, paths=["inputs"])
    validate_logged_field_datatype(outputs, paths=["outputs"])

    return {
        "event_id": uuid.uuid4(),
        "log_timestamp": log_time_str,
        "timestamp": event_time_str,
        "metadata": metadata,
        "inputs": inputs,
        "outputs": outputs,
        "feedback_id": join_key,
        "tags": tags,
        "batch_id": batch_id,
    }
