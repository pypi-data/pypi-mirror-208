import mock
import pytest
from freezegun import freeze_time

from gantry.exceptions import GantryLoggingDataTypeError
from gantry.logger import event_builder

from .conftest import CURRENT_TIME, CURRENT_TIME_STR, SOME_TIME, SOME_TIME_STR


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize(
    ["sort", "timestamps", "record_count", "expected"],
    [
        (False, [3, 4, 5, 1, 2], 10, [(0, 3), (1, 4), (2, 5), (3, 1), (4, 2)]),
        (True, [3, 4, 5, 1, 2], 10, [(3, 1), (4, 2), (0, 3), (1, 4), (2, 5)]),
        (False, ["b", "a", "c"], 100, [(0, "b"), (1, "a"), (2, "c")]),
        (True, ["b", "a", "c"], 100, [(1, "a"), (0, "b"), (2, "c")]),
        (
            True,
            None,
            4,
            [
                (0, CURRENT_TIME),
                (1, CURRENT_TIME),
                (2, CURRENT_TIME),
                (3, CURRENT_TIME),
            ],
        ),
        (
            False,
            None,
            4,
            [
                (0, CURRENT_TIME),
                (1, CURRENT_TIME),
                (2, CURRENT_TIME),
                (3, CURRENT_TIME),
            ],
        ),
    ],
)
def test_create_timestamp_idx(sort, timestamps, record_count, expected):
    assert list(event_builder._create_timestamp_idx(sort, timestamps, record_count)) == expected


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("timestamp", [None, SOME_TIME])
@pytest.mark.parametrize("feedback_version", [None, 5, "1.2.3"])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_build_feedback_event(mock_uuid, feedback_version, timestamp):
    mock_uuid.return_value = "123abc"
    assert event_builder._build_feedback_event(
        application="barbaz",
        join_key="1234567890",
        feedback={"b": 20},
        feedback_version=feedback_version,
        timestamp=timestamp,
        batch_id="ABCD1234",
    ) == {
        "batch_id": "ABCD1234",
        "event_id": "123abc",
        "feedback": {"b": 20},
        "feedback_id": "1234567890",
        "log_timestamp": CURRENT_TIME_STR,
        "metadata": {
            "feedback_version": feedback_version,
            "func_name": "barbaz",
        },
        "timestamp": SOME_TIME_STR if timestamp else CURRENT_TIME_STR,
    }


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("timestamp", [None, SOME_TIME])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_build_prediction_event(mock_uuid, timestamp):
    mock_uuid.return_value = "123abc"
    assert event_builder._build_prediction_event(
        inputs={"some-input": "a-input"},
        outputs={"some-output": "a-output"},
        application="barbaz",
        join_key="1234567890",
        version="1.2.3",
        ignore_inputs=["some-other-input"],
        batch_id="ABCD1234",
        tags={"this-is": "a-tag"},
        custom_timestamp=timestamp,
    ) == {
        "batch_id": "ABCD1234",
        "event_id": "123abc",
        "feedback_id": "1234567890",
        "inputs": {"some-input": "a-input"},
        "log_timestamp": CURRENT_TIME_STR,
        "metadata": {
            "feedback_keys": None,
            "version": "1.2.3",
            "ignore_inputs": ["some-other-input"],
            "func_name": "barbaz",
        },
        "timestamp": SOME_TIME_STR if timestamp else CURRENT_TIME_STR,
        "outputs": {"some-output": "a-output"},
        "tags": {"this-is": "a-tag"},
    }


def test_build_prediction_event_invalid_input():
    with pytest.raises(GantryLoggingDataTypeError):
        event_builder._build_prediction_event(
            inputs={"some-invalid-input": ["invalid", {"invalid": True}]},
            outputs={"some-output": "a-output"},
            application="barbaz",
            join_key="1234567890",
            version="1.2.3",
            ignore_inputs=[],
            batch_id="ABCD1234",
            tags={"this-is": "a-tag"},
            custom_timestamp=SOME_TIME,
        )
