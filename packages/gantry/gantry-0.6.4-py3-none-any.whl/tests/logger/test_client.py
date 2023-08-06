import datetime
import io
import logging
import uuid
from typing import Dict, List, Union

import mock
import numpy as np
import pandas as pd
import pytest
from freezegun import freeze_time

from gantry.exceptions import GantryLoggingException
from gantry.logger import client
from gantry.logger.constants import (
    BatchType,
    ScheduleFrequency,
    ScheduleType,
    UploadFileType,
)
from gantry.logger.stores import BaseLogStore
from gantry.logger.types import (
    DataLink,
    IngestFromDataConnectorRequest,
    Schedule,
    ScheduleOptions,
)

from .conftest import (
    ANOTHER_TIME,
    ANOTHER_TIME_STR,
    CURRENT_TIME,
    CURRENT_TIME_STR,
    ONE_TO_TEN,
    SOME_TIME,
    SOME_TIME_STR,
)


class TestLogStore(BaseLogStore):
    def __init__(self):
        self.logs = []
        self.status = False

    def log_batch(self, application, events) -> None:
        self.logs.append({"application": application, "events": events})

    def ping(self) -> bool:
        return self.status


@pytest.fixture(scope="function")
def log_store():
    return TestLogStore()


@pytest.fixture(scope="function")
def cli_obj(log_store):
    return client.Gantry(log_store=log_store, environment="test", logging_level="DEBUG")


@pytest.mark.parametrize(
    "env, tags, expected",
    [
        ("test", {}, {"env": "test"}),
        ("test", {"foo": "bar"}, {"foo": "bar", "env": "test"}),
        ("test", {"env": "local"}, {"env": "local"}),
        ("test", {"foo": "bar", "env": "local"}, {"foo": "bar", "env": "local"}),
    ],
)
def test_update_tags_with_env(env, tags, expected):
    client._update_tags_with_env(env, tags)
    assert tags == expected


@mock.patch("gantry.logger.client.uuid.uuid4")
def test_default_join_key_gen(mock_uuid):
    mock_uuid.return_value = "12345"
    assert client._default_join_key_gen() == "12345"


@pytest.mark.parametrize("sample_rate", [-1, 10, 1.1])
def test_sample_records_error(sample_rate):
    with pytest.raises(AssertionError):
        client._sample_records(10, sample_rate, None, None, None, None, None, None)


@pytest.mark.parametrize(
    ["sample", "kwargs", "expected"],
    [
        (
            [2, 3, 4, 5],
            {
                "inputs": ONE_TO_TEN,
                "outputs": ONE_TO_TEN,
                "feedbacks": ONE_TO_TEN,
                "join_keys": ONE_TO_TEN,
                "timestamps": ONE_TO_TEN,
                "tags": ONE_TO_TEN,
            },
            (
                [3, 4, 5, 6],
                [3, 4, 5, 6],
                [3, 4, 5, 6],
                [3, 4, 5, 6],
                [3, 4, 5, 6],
                [3, 4, 5, 6],
            ),
        ),
        (
            [7],
            {
                "inputs": ONE_TO_TEN,
                "outputs": ONE_TO_TEN,
                "feedbacks": None,
                "join_keys": ONE_TO_TEN,
                "timestamps": None,
                "tags": None,
            },
            (
                [8],
                [8],
                None,
                [8],
                None,
                None,
            ),
        ),
        (
            [6, 2],
            {
                "inputs": None,
                "outputs": None,
                "feedbacks": None,
                "join_keys": ONE_TO_TEN,
                "timestamps": None,
                "tags": ONE_TO_TEN,
            },
            (
                None,
                None,
                None,
                [3, 7],
                None,
                [3, 7],
            ),
        ),
    ],
)
@mock.patch("gantry.logger.client.random.sample")
def test_sample_records(mock_sample, sample, kwargs, expected):
    mock_sample.return_value = sample
    assert client._sample_records(10, 0.5, **kwargs) == expected
    mock_sample.assert_called_once_with(range(0, 10), 5)


@pytest.mark.parametrize(
    ["inputs", "feedback_id", "feedback_keys", "join_key", "expected"],
    [
        ({"foo": "bar"}, {"id": "12345"}, None, None, "80ef66be81dbaba30db25d1336217d0d"),
        ({"foo": "bar"}, None, ["foo"], None, "42a5b7b99b3717d1eaeb72a6948dabc9"),
        ({"foo": "bar"}, None, None, None, None),
        ({"foo": "bar"}, None, None, "barbaz", "barbaz"),
    ],
)
def test_resolve_join_key(inputs, feedback_id, feedback_keys, join_key, expected):
    assert (
        client._resolve_join_key(
            inputs,
            feedback_id,
            feedback_keys,
            join_key,
        )
        == expected
    )


@pytest.mark.parametrize(
    ["inputs", "feedback_id", "feedback_keys", "join_key", "error_t"],
    [
        ({"foo": "bar"}, {"id": "12345"}, ["foo"], None, GantryLoggingException),
        ({"foo": "bar"}, None, ["foo"], "barbaz", ValueError),
        ({"foo": "bar"}, {"id": "12345"}, None, "barbaz", ValueError),
        ({"foo": "bar"}, {"id": "12345"}, ["foo"], "barbaz", ValueError),
    ],
)
def test_resolve_join_key_error(inputs, feedback_id, feedback_keys, join_key, error_t):
    with pytest.raises(error_t):
        _ = client._resolve_join_key(
            inputs,
            feedback_id,
            feedback_keys,
            join_key,
        )


@pytest.mark.parametrize(
    ["size", "inputs", "feedback_id", "feedback_keys", "join_key", "expected"],
    [
        (
            2,
            [{"foo": "bar"}, {"foo": "baz"}],
            [{"id": "12345"}, {"id": "67890"}],
            None,
            None,
            ["80ef66be81dbaba30db25d1336217d0d", "4ce58e185be87947375e296071b59a93"],
        ),
        (
            2,
            [{"foo": "bar"}, {"foo": "baz"}],
            None,
            ["foo"],
            None,
            ["42a5b7b99b3717d1eaeb72a6948dabc9", "143654a5f0a059a178924baf9b815ea6"],
        ),
        (2, [{"foo": "bar"}, {"foo": "baz"}], None, None, None, None),
        (
            2,
            [{"foo": "bar"}, {"foo": "baz"}],
            None,
            None,
            ["foobar", "barbaz"],
            ["foobar", "barbaz"],
        ),
    ],
)
def test_resolve_join_keys(size, inputs, feedback_id, feedback_keys, join_key, expected):
    assert (
        client._resolve_join_keys(
            size,
            inputs,
            feedback_id,
            feedback_keys,
            join_key,
        )
        == expected
    )


@pytest.mark.parametrize(
    ["inputs", "feedback_ids", "feedback_keys", "join_keys", "error_t"],
    [
        ([{"foo": "bar"}], [{"id": "12345"}], ["foo"], None, GantryLoggingException),
        ([{"foo": "bar"}], None, ["foo"], ["barbaz"], ValueError),
        ([{"foo": "bar"}], [{"id": "12345"}], None, ["barbaz"], ValueError),
        ([{"foo": "bar"}], [{"id": "12345"}], ["foo"], ["barbaz"], ValueError),
    ],
)
def test_resolve_join_keys_error(inputs, feedback_ids, feedback_keys, join_keys, error_t):
    with pytest.raises(error_t):
        _ = client._resolve_join_keys(
            10,
            inputs,
            feedback_ids,
            feedback_keys,
            join_keys,
        )


def test_ping_fail(cli_obj):
    cli_obj.log_store.status = False
    assert not cli_obj.ping()


def test_ping_success(cli_obj):
    cli_obj.log_store.status = True
    assert cli_obj.ping()


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("tags", [{"env": "overwrite_env"}, {}, None])
@pytest.mark.parametrize("timestamp", [None, SOME_TIME])
@pytest.mark.parametrize("feedback_version", [None, "1.2.3", 10])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_feedback_event(mock_uuid, feedback_version, timestamp, tags, cli_obj):
    mock_uuid.return_value = "12345"
    assert (
        cli_obj._log_feedback_event(
            application="foobar",
            join_key="1234567890",
            feedback={"value": "bar"},
            feedback_version=feedback_version,
            timestamp=timestamp,
            tags=tags,
        )
        == "1234567890"
    )
    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "feedback": {"value": "bar"},
                    "feedback_id": "1234567890",
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "feedback_version": feedback_version,
                        "func_name": "foobar",
                    },
                    "timestamp": SOME_TIME_STR if timestamp else CURRENT_TIME_STR,
                }
            ],
            "application": "foobar",
        },
    ]


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("tags", [{"env": "overwrite_env"}, {}, None])
@pytest.mark.parametrize("timestamp", [None, SOME_TIME])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_prediction_event(mock_uuid, timestamp, tags, cli_obj):
    mock_uuid.return_value = "12345"
    assert (
        cli_obj._log_prediction_event(
            application="foobar",
            inputs={"A": 100},
            outputs={"value": "bar"},
            join_key="1234567890",
            version="a.b.c",
            ignore_inputs=["A"],
            timestamp=timestamp,
            tags=tags,
        )
        == "1234567890"
    )
    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "feedback_id": "1234567890",
                    "inputs": {},
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "feedback_keys": None,
                        "func_name": "foobar",
                        "ignore_inputs": ["A"],
                        "version": "a.b.c",
                    },
                    "outputs": {"value": "bar"},
                    "tags": tags if tags is not None else None,
                    "timestamp": CURRENT_TIME_STR if not timestamp else SOME_TIME_STR,
                }
            ],
            "application": "foobar",
        },
    ]


@pytest.mark.parametrize("application", [10, None, 10.5, b"some binary string"])
def test_log_record_invalid_name(application, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application=application,
        feedback_id={"A": 100},
        feedback={"value": "bar"},
        feedback_version=10,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("application", [10, None, 10.5, b"some binary string"])
def test_single_log_record_invalid_name(application, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.single_log_record(
        application=application,
        feedback_id={"A": 100},
        feedback={"value": "bar"},
        feedback_version=10,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("feedback_id", [10, None, 10.5, ["a", "list"], b"something"])
def test_log_record_invalid_feedback_id(feedback_id, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="foobar",
        feedback_id=feedback_id,
        feedback={"value": "bar"},
        feedback_version=10,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("feedback_id", [10, None, 10.5, ["a", "list"], b"something"])
def test_single_log_record_invalid_feedback_id(feedback_id, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.single_log_record(
        application="foobar",
        feedback_id=feedback_id,
        feedback={"value": "bar"},
        feedback_version=10,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("feedback", [10, None, 10.5, ["a", "list"], b"something"])
def test_log_record_invalid_feedback(feedback, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="foobar",
        feedback_id={"value": "bar"},
        feedback=feedback,
        feedback_version=10,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("feedback", [10, None, 10.5, ["a", "list"], b"something"])
def test_single_log_record_invalid_feedback(feedback, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.single_log_record(
        application="foobar",
        feedback_id={"value": "bar"},
        feedback=feedback,
        feedback_version=10,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize(
    "feedback_version", ["some-version", b"a-version", 10.5, {"version": "yes"}, [10]]
)
def test_log_record_invalid_feedback_version(feedback_version, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="foobar",
        feedback_id={"value": "bar"},
        feedback={"value": "foo"},
        feedback_version=feedback_version,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("timestamp", ["some-timestamp", 10, "2020-10-10"])
def test_log_record_invalid_timestamp(timestamp, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="foobar",
        feedback_id={"value": "bar"},
        feedback={"value": "foo"},
        feedback_version=10,
        timestamp=timestamp,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("inputs", [[10, 20], 10, 10.5, ("A", 100)])
def test_log_record_invalid_inputs(inputs, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="some-name",
        inputs=inputs,
        outputs={"value": "bar"},
        version=10,
        ignore_inputs=["A"],
        feedback_id={"A": 100},
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("version", [[10, 20], 10.5, {"version": 10}])
def test_log_record_invalid_version(version, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version=version,
        ignore_inputs=["A"],
        feedback_id={"A": 100},
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("feedback_keys", [[10, 20], 10.5, ("a", "b", "c")])
def test_log_record_invalid_feedback_keys(feedback_keys, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version="a.b.c",
        feedback_keys=feedback_keys,
        ignore_inputs=["A"],
        feedback_id={"A": 100},
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize(
    "ignore_inputs", [[10, 20], [b"something", "binary"], ["bar", 10.5], [10, "foo"], 10, 10.5]
)
def test_log_record_invalid_ignore_inputs(ignore_inputs, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version="a.b.c",
        ignore_inputs=ignore_inputs,
        feedback_id={"A": 100},
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize("feedback_id", [[10, 20], ["foo"], 10, 10.5])
def test_log_record_invalid_feedback_id_for_prediction(feedback_id, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version="a.b.c",
        feedback_keys=["A"],
        ignore_inputs=["A"],
        feedback_id=feedback_id,
        timestamp=SOME_TIME,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("feedback_id", ["foo", {"foo": "bar"}])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_record_valid_feedback_id_for_prediction(mock_uuid, feedback_id, cli_obj):
    mock_uuid.return_value = "12345"
    cli_obj.log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version="a.b.c",
        ignore_inputs=["B"],
        feedback_id=feedback_id,
        timestamp=SOME_TIME,
    )
    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "inputs": {"A": 100},
                    "outputs": {"value": "bar"},
                    "tags": {"env": "test"},
                    "feedback_id": "42a5b7b99b3717d1eaeb72a6948dabc9"
                    if isinstance(feedback_id, dict)
                    else feedback_id,
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "func_name": "some-name",
                        "version": "a.b.c",
                        "ignore_inputs": ["B"],
                        "feedback_keys": None,
                    },
                    "timestamp": SOME_TIME_STR,
                }
            ],
            "application": "some-name",
        },
    ]


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("feedback_id", ["foo", {"foo": "bar"}])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_single_log_record_valid_feedback_id_for_prediction(mock_uuid, feedback_id, cli_obj):
    mock_uuid.return_value = "12345"
    cli_obj.single_log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version="a.b.c",
        ignore_inputs=["B"],
        feedback_id=feedback_id,
        timestamp=SOME_TIME,
    )
    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "inputs": {"A": 100},
                    "outputs": {"value": "bar"},
                    "tags": {"env": "test"},
                    "feedback_id": "42a5b7b99b3717d1eaeb72a6948dabc9"
                    if isinstance(feedback_id, dict)
                    else feedback_id,
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "func_name": "some-name",
                        "version": "a.b.c",
                        "ignore_inputs": ["B"],
                        "feedback_keys": None,
                    },
                    "timestamp": SOME_TIME_STR,
                }
            ],
            "application": "some-name",
        },
    ]


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("feedback_id", ["foo", {"foo": "bar"}])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_record_valid_feedback_id_for_feedback(mock_uuid, feedback_id, cli_obj):
    mock_uuid.return_value = "12345"
    cli_obj.log_record(
        application="some-name",
        feedback={"A": 100},
        version="a.b.c",
        feedback_id=feedback_id,
        timestamp=SOME_TIME,
    )
    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "feedback": {"A": 100},
                    "feedback_id": "42a5b7b99b3717d1eaeb72a6948dabc9"
                    if isinstance(feedback_id, dict)
                    else feedback_id,
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "func_name": "some-name",
                        "feedback_version": "a.b.c",
                    },
                    "timestamp": SOME_TIME_STR,
                }
            ],
            "application": "some-name",
        },
    ]


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("feedback_id", ["foo", {"foo": "bar"}])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_single_log_record_valid_feedback_id_for_feedback(mock_uuid, feedback_id, cli_obj):
    mock_uuid.return_value = "12345"
    cli_obj.single_log_record(
        application="some-name",
        feedback={"A": 100},
        version="a.b.c",
        feedback_id=feedback_id,
        timestamp=SOME_TIME,
    )
    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "feedback": {"A": 100},
                    "feedback_id": "42a5b7b99b3717d1eaeb72a6948dabc9"
                    if isinstance(feedback_id, dict)
                    else feedback_id,
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "func_name": "some-name",
                        "feedback_version": "a.b.c",
                    },
                    "timestamp": SOME_TIME_STR,
                }
            ],
            "application": "some-name",
        },
    ]


@pytest.mark.parametrize("timestamp", [[], "some-timestamp", 10, "2020-10-10"])
def test_log_record_invalid_timestamp_for_prediction(timestamp, cli_obj, caplog):
    caplog.set_level(logging.ERROR, logger="gantry.client")
    cli_obj.log_record(
        application="some-name",
        inputs={"A": 100},
        outputs={"value": "bar"},
        version="a.b.c",
        feedback_keys=["A"],
        ignore_inputs=["A"],
        feedback_id={"A": 100},
        timestamp=timestamp,
    )
    assert "Internal exception in Gantry client" in caplog.text
    assert "TypeError:" in caplog.text


@pytest.mark.parametrize(
    ["sample_rate", "sample", "expected"],
    [
        (1, 0.9, 1),
        (0, 0.9, 0),
        (0.5, 0.4, 1),
        (0.5, 0.5, 1),
        (0.5, 0.51, 0),
    ],
)
def test_log_record_sample_rate(sample_rate, sample, expected, cli_obj):
    with mock.patch("random.random", return_value=sample):
        cli_obj.log_record(
            application="foobar",
            inputs={"A": 100},
            outputs={"B": 100},
            sample_rate=sample_rate,
        )

    assert len(cli_obj.log_store.logs) == expected


@pytest.mark.parametrize(
    ["sample_rate", "sample", "expected"],
    [
        (1, 0.9, 1),
        (0, 0.9, 0),
        (0.5, 0.4, 1),
        (0.5, 0.5, 1),
        (0.5, 0.51, 0),
    ],
)
def test_single_log_record_sample_rate(sample_rate, sample, expected, cli_obj):
    with mock.patch("random.random", return_value=sample):
        cli_obj.single_log_record(
            application="foobar",
            inputs={"A": 100},
            outputs={"B": 100},
            sample_rate=sample_rate,
        )

    assert len(cli_obj.log_store.logs) == expected


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("tags", [{"env": "overwrite_env"}, {}, None])
@pytest.mark.parametrize("timestamp", [None, SOME_TIME])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_prediction_and_feedback_event(mock_uuid, timestamp, tags, cli_obj):
    mock_uuid.return_value = "12345"
    assert (
        cli_obj._log_prediction_and_feedback_event(
            application="foobar",
            version="a.b.c",
            inputs={"A": 100},
            outputs={"value": "bar"},
            feedback={"value": "potato"},
            join_key="1234567890",
            timestamp=timestamp,
            tags=tags,
        )
        == "1234567890"
    )

    assert cli_obj.log_store.logs == [
        {
            "events": [
                {
                    "batch_id": None,
                    "event_id": "12345",
                    "feedback": {"value": "potato"},
                    "inputs": {"A": 100},
                    "outputs": {"value": "bar"},
                    "tags": tags if tags is not None else None,
                    "feedback_id": "1234567890",
                    "log_timestamp": CURRENT_TIME_STR,
                    "metadata": {
                        "feedback_version": "a.b.c",
                        "func_name": "foobar",
                        "version": "a.b.c",
                        "ignore_inputs": None,
                        "feedback_keys": None,
                    },
                    "timestamp": SOME_TIME_STR if timestamp else CURRENT_TIME_STR,
                }
            ],
            "application": "foobar",
        },
    ]


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"feedback_keys": ["A"]}, [{"A": 100}, None, ["A"], None]),
        ({"feedback_id": "12345"}, [{"A": 100}, "12345", None, None]),
        ({"join_key": "54321"}, [{"A": 100}, None, None, "54321"]),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_event", return_value="foobar12345"
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_log_record_pred_and_feedback(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    assert (
        cli_obj.log_record(
            application="foobar",
            version="2.0.1",
            inputs={"A": 100},
            outputs={"B": 300},
            feedback={"A": 200},
            timestamp=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_called_once_with(
        application="foobar",
        version="2.0.1",
        inputs={"A": 100},
        outputs={"B": 300},
        feedback={"A": 200},
        join_key="1234567890",
        ignore_inputs=None,
        timestamp=None,
        tags={"env": "test"},
    )
    mock_pred.assert_not_called()
    mock_feedback.assert_not_called()

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"join_keys": "54321"}, [{"A": 100}, None, None, "54321"]),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_event", return_value="foobar12345"
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_single_log_pred_and_feedback(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    assert (
        cli_obj.log(
            application="foobar",
            version="2.0.1",
            inputs={"A": 100},
            outputs={"B": 300},
            feedbacks={"A": 200},
            timestamps=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_called_once_with(
        application="foobar",
        version="2.0.1",
        inputs={"A": 100},
        outputs={"B": 300},
        feedback={"A": 200},
        join_key="1234567890",
        ignore_inputs=None,
        timestamp=None,
        tags={"env": "test"},
    )
    mock_pred.assert_not_called()
    mock_feedback.assert_not_called()

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"feedback_keys": ["A"]}, [{"A": 100}, None, ["A"], None]),
        ({"feedback_id": "12345"}, [{"A": 100}, "12345", None, None]),
        ({"join_key": "54321"}, [{"A": 100}, None, None, "54321"]),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_event", return_value="foobar12345"
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_single_log_record_pred_and_feedback(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    assert (
        cli_obj.single_log_record(
            application="foobar",
            version="2.0.1",
            inputs={"A": 100},
            outputs={"B": 300},
            feedback={"A": 200},
            timestamp=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_called_once_with(
        application="foobar",
        version="2.0.1",
        inputs={"A": 100},
        outputs={"B": 300},
        feedback={"A": 200},
        join_key="1234567890",
        ignore_inputs=None,
        timestamp=None,
        tags={"env": "test"},
    )
    mock_pred.assert_not_called()
    mock_feedback.assert_not_called()

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"feedback_keys": ["A"]}, [{"A": 100}, None, ["A"], None]),
        ({"feedback_id": "12345"}, [{"A": 100}, "12345", None, None]),
        ({"join_key": "54321"}, [{"A": 100}, None, None, "54321"]),
    ],
)
@pytest.mark.parametrize(
    "test_feedback",
    [None, {}],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event", return_value="foobar12345")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_log_record_pred_only(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    test_feedback,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    assert (
        cli_obj.log_record(
            application="foobar",
            version="2.0.1",
            inputs={"A": 100},
            outputs={"B": 300},
            feedback=test_feedback,
            timestamp=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_called_once_with(
        application="foobar",
        inputs={"A": 100},
        outputs={"B": 300},
        version="2.0.1",
        join_key="1234567890",
        ignore_inputs=None,
        timestamp=None,
        tags={"env": "test"},
    )
    mock_feedback.assert_not_called()

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"feedback_keys": ["A"]}, [{"A": 100}, None, ["A"], None]),
        ({"feedback_id": "12345"}, [{"A": 100}, "12345", None, None]),
        ({"join_key": "54321"}, [{"A": 100}, None, None, "54321"]),
    ],
)
@pytest.mark.parametrize(
    "test_feedback",
    [None, {}],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event", return_value="foobar12345")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_single_log_record_pred_only(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    test_feedback,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    assert (
        cli_obj.single_log_record(
            application="foobar",
            version="2.0.1",
            inputs={"A": 100},
            outputs={"B": 300},
            feedback=test_feedback,
            timestamp=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_called_once_with(
        application="foobar",
        inputs={"A": 100},
        outputs={"B": 300},
        version="2.0.1",
        join_key="1234567890",
        ignore_inputs=None,
        timestamp=None,
        tags={"env": "test"},
    )
    mock_feedback.assert_not_called()

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"feedback_keys": ["A"]}, [None, None, ["A"], None]),
        ({"feedback_id": "12345"}, [None, "12345", None, None]),
        ({"join_key": "54321"}, [None, None, None, "54321"]),
    ],
)
@pytest.mark.parametrize(
    "test_output",
    [None, {}],
)
@pytest.mark.parametrize(
    "test_input",
    [None, {}],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event", return_value="foobar12345")
def test_log_record_feedback_only(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    test_input,
    test_output,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    # Hack the parametrized value with the other parametrized fixture
    expected_compat_call[0] = test_input

    assert (
        cli_obj.log_record(
            application="foobar",
            version="2.0.1",
            inputs=test_input,
            outputs=test_output,
            feedback={"A": 200},
            timestamp=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_not_called()
    mock_feedback.assert_called_once_with(
        application="foobar",
        join_key="1234567890",
        feedback={"A": 200},
        feedback_version="2.0.1",
        timestamp=None,
        tags={"env": "test"},
    )

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    ["kwargs", "expected_compat_call"],
    [
        ({"feedback_keys": ["A"]}, [None, None, ["A"], None]),
        ({"feedback_id": "12345"}, [None, "12345", None, None]),
        ({"join_key": "54321"}, [None, None, None, "54321"]),
    ],
)
@pytest.mark.parametrize(
    "test_output",
    [None, {}],
)
@pytest.mark.parametrize(
    "test_input",
    [None, {}],
)
@mock.patch("gantry.logger.client._resolve_join_key", return_value="1234567890")
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event", return_value="foobar12345")
def test_single_log_record_feedback_only(
    mock_feedback,
    mock_pred,
    mock_pred_and_feedback,
    mock_get_record,
    test_input,
    test_output,
    kwargs,
    expected_compat_call,
    cli_obj,
):
    # Hack the parametrized value with the other parametrized fixture
    expected_compat_call[0] = test_input

    assert (
        cli_obj.single_log_record(
            application="foobar",
            version="2.0.1",
            inputs=test_input,
            outputs=test_output,
            feedback={"A": 200},
            timestamp=None,
            **kwargs,
        )
        == "foobar12345"
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_not_called()
    mock_feedback.assert_called_once_with(
        application="foobar",
        join_key="1234567890",
        feedback={"A": 200},
        feedback_version="2.0.1",
        timestamp=None,
        tags={"env": "test"},
    )

    mock_get_record.assert_called_once_with(*expected_compat_call)


@pytest.mark.parametrize(
    "test_output",
    [None, {}],
)
@pytest.mark.parametrize(
    "test_input",
    [None, {}],
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_log_record_feedback_no_key_error(
    mock_feedback, mock_pred, mock_pred_and_feedback, test_input, test_output, cli_obj
):
    cli_obj.log_record(
        application="foobar",
        version="2.0.1",
        inputs=test_input,
        outputs=test_output,
        feedback={"A": 200},
        timestamp=None,
        feedback_keys=None,
        feedback_id=None,
        join_key=None,
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_id": "12345"},
        {"join_key": "54321"},
    ],
)
@pytest.mark.parametrize(
    "test_input",
    [None, {}],
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_log_record_no_data(
    mock_feedback, mock_pred, mock_pred_and_feedback, test_input, kwargs, cli_obj
):
    cli_obj.log_record(
        application="foobar",
        version="2.0.1",
        inputs=test_input,
        outputs={"B": 100},
        feedback=None,
        timestamp=None,
        **kwargs,
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_id": "12345"},
        {"join_key": "54321"},
    ],
)
@pytest.mark.parametrize("feedback", [None, {}, {"B": 200}])
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_event")
@mock.patch("gantry.logger.client.Gantry._log_prediction_event")
@mock.patch("gantry.logger.client.Gantry._log_feedback_event")
def test_log_record_incomplete_preds(
    mock_feedback, mock_pred, mock_pred_and_feedback, feedback, kwargs, cli_obj
):
    cli_obj.log_record(
        application="foobar",
        version="2.0.1",
        inputs={},
        outputs={"B": 100},
        feedback=feedback,
        timestamp=None,
        **kwargs,
    )

    mock_pred_and_feedback.assert_not_called()
    mock_pred.assert_not_called()
    mock_feedback.assert_not_called()


# TODO -> add np.ndarrays as possible feedbacks values
@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize(
    "tags", [[{"env": "overwrite_env"}, {"env": "overwrite_env_2"}], [{}] * 2, None]
)
@pytest.mark.parametrize("sort", [False, True])
@pytest.mark.parametrize(
    "timestamps", [pd.DatetimeIndex([ANOTHER_TIME, SOME_TIME]), [ANOTHER_TIME, SOME_TIME], None]
)
@pytest.mark.parametrize(
    "feedbacks",
    [
        [{100: "some-value"}, {100: "some-other-value"}],
    ],
)
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_feedback_events(mock_uuid, feedbacks, timestamps, sort, tags, cli_obj):
    mock_uuid.return_value = "ABCD1234"

    assert cli_obj._log_feedback_events(
        application="foobar",
        feedbacks=feedbacks,
        join_keys=["12345", "67890"],
        feedback_version=10,
        timestamps=timestamps,
        sort_on_timestamp=sort,
        as_batch=False,
        tags=tags,
    ) == (None, ["12345", "67890"])
    events = [
        {
            "batch_id": None,
            "event_id": "ABCD1234",
            "feedback": {100: "some-other-value"},
            "feedback_id": "67890",
            "log_timestamp": CURRENT_TIME_STR,
            "metadata": {
                "feedback_version": 10,
                "func_name": "foobar",
            },
            "timestamp": SOME_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        },
        {
            "batch_id": None,
            "event_id": "ABCD1234",
            "feedback": {100: "some-value"},
            "feedback_id": "12345",
            "log_timestamp": CURRENT_TIME_STR,
            "metadata": {
                "feedback_version": 10,
                "func_name": "foobar",
            },
            "timestamp": ANOTHER_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        },
    ]

    if timestamps is not None:
        expected_events = [events[1], events[0]] if not sort else [events[0], events[1]]
    else:
        expected_events = [events[1], events[0]]

    assert cli_obj.log_store.logs == [
        {
            "events": expected_events,
            "application": "foobar",
        }
    ]


# TODO -> add np.ndarrays as possible inputs/outputs values
@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize(
    "tags", [[{"env": "overwrite_env"}, {"env": "overwrite_env_2"}], [{}] * 2, None]
)
@pytest.mark.parametrize("sort", [False, True])
@pytest.mark.parametrize(
    "timestamps", [pd.DatetimeIndex([ANOTHER_TIME, SOME_TIME]), [ANOTHER_TIME, SOME_TIME], None]
)
@pytest.mark.parametrize(
    "outputs",
    [
        [{"C": 300}, {"C": 303}],
    ],
)
@pytest.mark.parametrize(
    "inputs",
    [
        [{"A": 100, "B": 200}, {"A": 101, "B": 202}],
    ],
)
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
def test_log_prediction_events(mock_uuid, inputs, outputs, timestamps, sort, tags, cli_obj):
    mock_uuid.return_value = "ABCD1234"
    assert cli_obj._log_prediction_events(
        application="foobar",
        inputs=inputs,
        outputs=outputs,
        join_keys=["12345", "67890"],
        ignore_inputs=["B"],
        version=10,
        timestamps=timestamps,
        sort_on_timestamp=sort,
        as_batch=False,
        tags=tags,
    ) == (None, ["12345", "67890"])

    events = [
        {
            "batch_id": None,
            "event_id": "ABCD1234",
            "feedback_id": "67890",
            "inputs": {"A": 101},
            "log_timestamp": CURRENT_TIME_STR,
            "metadata": {
                "feedback_keys": None,
                "func_name": "foobar",
                "ignore_inputs": ["B"],
                "version": 10,
            },
            "outputs": {"C": 303},
            "tags": tags[1] if tags else None,
            "timestamp": SOME_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        },
        {
            "batch_id": None,
            "event_id": "ABCD1234",
            "feedback_id": "12345",
            "inputs": {"A": 100},
            "log_timestamp": CURRENT_TIME_STR,
            "metadata": {
                "feedback_keys": None,
                "func_name": "foobar",
                "ignore_inputs": ["B"],
                "version": 10,
            },
            "outputs": {"C": 300},
            "tags": tags[0] if tags else None,
            "timestamp": ANOTHER_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        },
    ]

    if timestamps is not None:
        expected_events = [events[1], events[0]] if not sort else [events[0], events[1]]
    else:
        expected_events = [events[1], events[0]]

    assert cli_obj.log_store.logs == [
        {
            "events": expected_events,
            "application": "foobar",
        }
    ]


# TODO -> readd the as_batch=True tests


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize(
    "tags", [[{"env": "overwrite_env"}, {"env": "overwrite_env_2"}], [{}] * 2, None]
)
@pytest.mark.parametrize(
    "timestamps", [None, pd.DatetimeIndex([ANOTHER_TIME, SOME_TIME]), [ANOTHER_TIME, SOME_TIME]]
)
@pytest.mark.parametrize("sort", [False, True])
@pytest.mark.parametrize("version", ["0", 0, None])
@pytest.mark.parametrize("as_batch", [False, True])
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
    ],
)
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
@mock.patch("gantry.logger.client.Gantry._upload_data_as_batch")
def test_log_prediction_and_feedback_events(
    mock_upload_data_as_batch,
    mock_uuid,
    test_inputs,
    test_outputs,
    test_feedbacks,
    as_batch,
    version,
    sort,
    timestamps,
    tags,
    cli_obj,
    log_store,
):
    mock_upload_data_as_batch.return_value = None
    mock_uuid.side_effect = ["ABCD1", "ABCD2", "ABCD3", "ABCD4"]
    cli_obj._log_prediction_and_feedback_events(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        join_keys=["12345", "67890"],
        feedbacks=test_feedbacks,
        timestamps=timestamps,
        sort_on_timestamp=sort,
        as_batch=as_batch,
        tags=tags,
    )

    event_1 = {
        "event_id": "ABCD2" if not (sort and timestamps is not None) else "ABCD4",
        "log_timestamp": CURRENT_TIME_STR,
        "timestamp": ANOTHER_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        "metadata": {
            "func_name": "foobar",
            "version": version,
            "feedback_keys": None,
            "ignore_inputs": None,
            "feedback_version": version,
        },
        "inputs": {"A": 100},
        "outputs": {"B": 300},
        "feedback_id": "12345",
        "tags": tags[0] if tags else None,
        "batch_id": None,
        "feedback": {"A": 200},
    }

    event_2 = {
        "event_id": "ABCD4" if not (sort and timestamps is not None) else "ABCD2",
        "log_timestamp": CURRENT_TIME_STR,
        "timestamp": SOME_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        "metadata": {
            "func_name": "foobar",
            "version": version,
            "feedback_keys": None,
            "ignore_inputs": None,
            "feedback_version": version,
        },
        "inputs": {"A": 101},
        "outputs": {"B": 301},
        "feedback_id": "67890",
        "tags": tags[1] if tags else None,
        "batch_id": None,
        "feedback": {"A": 201},
    }

    if as_batch:
        mock_upload_data_as_batch.assert_called_once_with(
            "foobar",
            version,
            [event_1, event_2] if not (sort and timestamps is not None) else [event_2, event_1],
            BatchType.RECORD,
        )
    else:
        assert log_store.logs == [
            {
                "events": [event_1, event_2]
                if not (sort and timestamps is not None)
                else [event_2, event_1],
                "application": "foobar",
            },
        ]
        mock_upload_data_as_batch.assert_not_called()


@freeze_time(CURRENT_TIME)
@pytest.mark.parametrize("tags", [{"env": "overwrite_env"}, {}, None])
@pytest.mark.parametrize(
    "timestamps", [None, pd.DatetimeIndex([ANOTHER_TIME, SOME_TIME]), [ANOTHER_TIME, SOME_TIME]]
)
@pytest.mark.parametrize("sort", [False, True])
@pytest.mark.parametrize("version", ["0", 0, None])
@mock.patch("gantry.logger.event_builder.uuid.uuid4")
@mock.patch("gantry.logger.client.Gantry._handle_upload")
def test__upload_data_as_batch(
    mock_handle_upload,
    mock_uuid,
    version,
    sort,
    timestamps,
    tags,
    cli_obj,
):
    mock_uuid.side_effect = ["1"]
    expected_tags = tags if tags else {"env": "test"}
    event_1 = {
        "event_id": "ABCD2" if not (sort and timestamps is not None) else "ABCD4",
        "log_timestamp": CURRENT_TIME_STR,
        "timestamp": ANOTHER_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        "metadata": {
            "func_name": "foobar",
            "version": version,
            "feedback_keys": ["A"],
            "ignore_inputs": None,
            "provided_feedback_id": None,
            "feedback_version": version,
        },
        "inputs": {"A": 100},
        "outputs": {"B": 300},
        "feedback_id": "5dd14615efeb2d086e519ed35efd3f73",
        "tags": expected_tags,
        "batch_id": None,
        "feedback_id_inputs": {"A": 100},
        "feedback": {"A": 200},
    }
    event_2 = {
        "event_id": "ABCD4" if not (sort and timestamps is not None) else "ABCD2",
        "log_timestamp": CURRENT_TIME_STR,
        "timestamp": SOME_TIME_STR if timestamps is not None else CURRENT_TIME_STR,
        "metadata": {
            "func_name": "foobar",
            "version": version,
            "feedback_keys": ["A"],
            "ignore_inputs": None,
            "provided_feedback_id": None,
            "feedback_version": version,
        },
        "inputs": {"A": 101},
        "outputs": {"B": 301},
        "feedback_id": "9e329293e022d6cdaafdec49b5f4fedc",
        "tags": expected_tags,
        "batch_id": None,
        "feedback_id_inputs": {"A": 101},
        "feedback": {"A": 201},
    }
    events = [event_1, event_2]

    cli_obj._upload_data_as_batch("test_app", version, events, BatchType.RECORD)

    mock_handle_upload.assert_called_once_with(
        mock.ANY,
        DataLink(
            application="test_app",
            version=str(version) if version is not None else version,
            file_type=UploadFileType.EVENTS,
            batch_type=BatchType.RECORD,
            log_timestamp=CURRENT_TIME.isoformat(),
            num_events=2,
        ),
        mock.ANY,
        "test_app_1",
    )


@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
def test_generate_records_preds_and_feedback_series_coerced(
    mock_generate_preds_and_feedback,
    cli_obj,
):
    expected_inputs = pd.Series([200, 201])
    expected_outputs = pd.Series([300, 301])
    expected_feedbacks = pd.Series([100, 101])
    application = "test_app"

    cli_obj.generate_records(
        application=application,
        inputs=expected_inputs,
        outputs=expected_outputs,
        feedbacks=expected_feedbacks,
    )

    downstream_kwargs = mock_generate_preds_and_feedback.call_args.kwargs
    actual_inputs = downstream_kwargs["inputs"]
    actual_outputs = downstream_kwargs["outputs"]
    actual_feedbacks = downstream_kwargs["feedbacks"]
    assert actual_inputs == [{0: 200}, {0: 201}]
    assert actual_outputs == [{0: 300}, {0: 301}]
    assert actual_feedbacks == [{0: 100}, {0: 101}]


@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
def test_log_records_preds_and_feedback_series_coerced(
    mock_preds_and_feedback,
    cli_obj,
):
    expected_inputs = pd.Series([200, 201])
    expected_outputs = pd.Series([300, 301])
    expected_feedbacks = pd.Series([100, 101])
    application = "test_app"

    cli_obj.log_records(
        application=application,
        inputs=expected_inputs,
        outputs=expected_outputs,
        feedbacks=expected_feedbacks,
    )

    downstream_kwargs = mock_preds_and_feedback.call_args.kwargs
    actual_inputs = downstream_kwargs["inputs"]
    actual_outputs = downstream_kwargs["outputs"]
    actual_feedbacks = downstream_kwargs["feedbacks"]
    assert actual_inputs == [{0: 200}, {0: 201}]
    assert actual_outputs == [{0: 300}, {0: 301}]
    assert actual_feedbacks == [{0: 100}, {0: 101}]


@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
def test_single_log_records_preds_and_feedback_series_coerced(
    mock_preds_and_feedback,
    cli_obj,
):
    expected_inputs = pd.Series([200, 201])
    expected_outputs = pd.Series([300, 301])
    expected_feedbacks = pd.Series([100, 101])
    application = "test_app"

    cli_obj.single_log_records(
        application=application,
        inputs=expected_inputs,
        outputs=expected_outputs,
        feedbacks=expected_feedbacks,
    )

    downstream_kwargs = mock_preds_and_feedback.call_args.kwargs
    actual_inputs = downstream_kwargs["inputs"]
    actual_outputs = downstream_kwargs["outputs"]
    actual_feedbacks = downstream_kwargs["feedbacks"]
    assert actual_inputs == [{0: 200}, {0: 201}]
    assert actual_outputs == [{0: 300}, {0: 301}]
    assert actual_feedbacks == [{0: 100}, {0: 101}]


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_ids": ["12345", "67890"]},
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_events",
    return_value=(None, ["12345", "67890"]),
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_single_log_records_preds_and_feedback(
    mock_join_key_gen,
    mock_sample_records,
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    mock_resolve_join_keys,
    kwargs,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    test_feedbacks,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    assert cli_obj.single_log_records(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        sample_rate=1,
        tags=tags,
        row_tags=row_tags,
        global_tags=global_tags,
        **kwargs,
    ) == (None, ["12345", "67890"])

    mock_preds_and_feedback.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        feedbacks=[{"A": 200}, {"A": 201}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        as_batch=False,
        tags=expected_tags_param,
    )
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_ids": ["12345", "67890"]},
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_events",
    return_value=(None, ["12345", "67890"]),
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_log_records_preds_and_feedback(
    mock_join_key_gen,
    mock_sample_records,
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    mock_resolve_join_keys,
    kwargs,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    test_feedbacks,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    assert cli_obj.log_records(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        sample_rate=1,
        tags=tags,
        row_tags=row_tags,
        global_tags=global_tags,
        **kwargs,
    ) == (None, ["12345", "67890"])

    mock_preds_and_feedback.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        feedbacks=[{"A": 200}, {"A": 201}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        as_batch=False,
        tags=expected_tags_param,
    )
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch(
    "gantry.logger.client.Gantry._generate_prediction_and_feedback_events",
    return_value=([{"event": "place_holder"}], ["12345", "67890"]),
)
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_generate_records_preds_and_feedback(
    mock_join_key_gen,
    mock_sample_records,
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    mock_resolve_join_keys,
    kwargs,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    test_feedbacks,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    run_id = str(uuid.uuid4())
    run_tags = None
    if tags and global_tags:
        run_tags = {**tags, **global_tags}
    elif tags:
        run_tags = tags
    elif global_tags:
        run_tags = global_tags
    assert cli_obj.log(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        sample_rate=1,
        run_tags=run_tags,
        row_tags=row_tags,
        run_id=run_id,
        **kwargs,
    ) == [{"event": "place_holder"}]

    mock_generate_preds_and_feedback.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        feedbacks=[{"A": 200}, {"A": 201}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        run_id=run_id,
        tags=expected_tags_param,
    )
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_events",
    return_value=(None, ["12345", "67890"]),
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_single_log_preds_and_feedback(
    mock_join_key_gen,
    mock_sample_records,
    mock_log_feedback,
    mock_log_preds,
    mock_log_preds_and_feedback,
    mock_resolve_join_keys,
    kwargs,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    test_feedbacks,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    cli_obj.log(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        sample_rate=1,
        global_tags=global_tags,
        tags=tags,
        row_tags=row_tags,
        **kwargs,
    )

    mock_log_preds_and_feedback.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        feedbacks=[{"A": 200}, {"A": 201}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        tags=expected_tags_param,
        as_batch=False,
    )
    mock_log_preds.assert_not_called()
    mock_log_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "inputs, outputs, feedbacks",
    [
        (
            np.array([200, 201]),
            [{"B": 200}, {"B": 201}],
            [{"A": 200}, {"A": 201}],
        ),
        (
            np.array([200, 201]),
            [{"B": 200}, {"B": 201}],
            None,
        ),
        (
            np.array([200, 201]),
            np.array([200, 201]),
            None,
        ),
        (
            [{"B": 200}, {"B": 201}],
            np.array([200, 201]),
            [{"A": 200}, {"A": 201}],
        ),
        (
            [{"B": 200}, {"B": 201}],
            [{"A": 200}, {"A": 201}],
            np.array([200, 201]),
        ),
        (
            None,
            None,
            np.array([200, 201]),
        ),
    ],
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
def test_log_records_preds_and_feedback_wrong_np_array(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    inputs,
    outputs,
    feedbacks,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version="1.2.3",
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            timestamps=None,
            sort_on_timestamp=True,
            sample_rate=1,
            join_keys=["foobar", "barbaz"],
        )
        is None
    )
    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "inputs, outputs, feedbacks",
    [
        (
            np.array([200, 201]),
            [{"B": 200}, {"B": 201}],
            [{"A": 200}, {"A": 201}],
        ),
        (
            np.array([200, 201]),
            [{"B": 200}, {"B": 201}],
            None,
        ),
        (
            np.array([200, 201]),
            np.array([200, 201]),
            None,
        ),
        (
            [{"B": 200}, {"B": 201}],
            np.array([200, 201]),
            [{"A": 200}, {"A": 201}],
        ),
        (
            [{"B": 200}, {"B": 201}],
            [{"A": 200}, {"A": 201}],
            np.array([200, 201]),
        ),
        (
            None,
            None,
            np.array([200, 201]),
        ),
    ],
)
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
def test_generate_records_preds_and_feedback_wrong_np_array(
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    inputs,
    outputs,
    feedbacks,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version="1.2.3",
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            timestamps=None,
            sort_on_timestamp=True,
            sample_rate=1,
            join_keys=["foobar", "barbaz"],
        )
        is None
    )
    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_not_called()


@pytest.mark.parametrize(
    "timestamps",
    [
        np.array([200, 201]),
        np.array([200, CURRENT_TIME]),
    ],
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
def test_log_records_preds_and_feedback_wrong_timestamps(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    timestamps,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version="1.2.3",
            inputs=[{"foo": "bar"}, {"foo": "baz"}],
            outputs=[{"foo": "bar"}, {"foo": "baz"}],
            feedbacks=None,
            timestamps=timestamps,
            sort_on_timestamp=True,
            sample_rate=1,
            join_keys=["foobar", "barbaz"],
        )
        is None
    )
    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "timestamps",
    [
        np.array([200, 201]),
        np.array([200, CURRENT_TIME]),
    ],
)
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
def test_generate_records_preds_and_feedback_wrong_timestamps(
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    timestamps,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version="1.2.3",
            inputs=[{"foo": "bar"}, {"foo": "baz"}],
            outputs=[{"foo": "bar"}, {"foo": "baz"}],
            feedbacks=None,
            timestamps=timestamps,
            sort_on_timestamp=True,
            sample_rate=1,
            join_keys=["foobar", "barbaz"],
        )
        is None
    )
    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_not_called()


@pytest.mark.parametrize("join_keys", [[1, 2, 3], pd.Series([1, 2, 3])])
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
def test_log_records_preds_and_feedback_wrong_join_keys(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    join_keys,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version="1.2.3",
            inputs=[{"A": 200}, {"A": 201}],
            outputs=[{"B": 200}, {"B": 201}],
            feedbacks=[{"C": 200}, {"C": 201}],
            timestamps=None,
            sort_on_timestamp=True,
            sample_rate=1,
            join_keys=join_keys,
        )
        is None
    )
    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize("join_keys", [[1, 2, 3], pd.Series([1, 2, 3])])
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
def test_generate_records_preds_and_feedback_wrong_join_keys(
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    join_keys,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version="1.2.3",
            inputs=[{"A": 200}, {"A": 201}],
            outputs=[{"B": 200}, {"B": 201}],
            feedbacks=[{"C": 200}, {"C": 201}],
            timestamps=None,
            sort_on_timestamp=True,
            sample_rate=1,
            join_keys=join_keys,
        )
        is None
    )
    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_ids": ["12345", "67890"]},
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_events", return_value=(None, ["12345", "67890"])
)
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_log_records_preds_only(
    mock_join_key_gen,
    mock_sample_records,
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    mock_resolve_join_keys,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    kwargs,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    assert cli_obj.log_records(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=None,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        tags=tags,
        row_tags=row_tags,
        global_tags=global_tags,
        **kwargs,
    ) == (None, ["12345", "67890"])

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        as_batch=False,
        tags=expected_tags_param,
    )
    mock_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        None,
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_ids": ["12345", "67890"]},
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_events", return_value=(None, ["12345", "67890"])
)
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_single_log_records_preds_only(
    mock_join_key_gen,
    mock_sample_records,
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    mock_resolve_join_keys,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    kwargs,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    assert cli_obj.single_log_records(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=None,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        tags=tags,
        row_tags=row_tags,
        global_tags=global_tags,
        **kwargs,
    ) == (None, ["12345", "67890"])

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        as_batch=False,
        tags=expected_tags_param,
    )
    mock_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        None,
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
        {},
    ],
)
@pytest.mark.parametrize(
    "test_outputs",
    [
        [{"B": 300}, {"B": 301}],
        pd.DataFrame.from_dict({"B": [300, 301]}),
        pd.Series(name="B", data=[300, 301]),
        np.array([{"B": 300}, {"B": 301}]),
    ],
)
@pytest.mark.parametrize(
    "test_inputs",
    [
        [{"A": 100}, {"A": 101}],
        pd.DataFrame.from_dict({"A": [100, 101]}),
        pd.Series(name="A", data=[100, 101]),
        np.array([{"A": 100}, {"A": 101}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch(
    "gantry.logger.client.Gantry._generate_prediction_events",
    return_value=([{"event": "place_holder"}], ["12345", "67890"]),
)
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
@mock.patch("gantry.logger.client._default_join_key_gen")
def test_generate_records_preds_only(
    mock_join_key_gen,
    mock_sample_records,
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    mock_resolve_join_keys,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_timestamps,
    test_timestamps_list,
    test_inputs,
    test_outputs,
    kwargs,
    cli_obj,
):
    mock_join_key_gen.side_effect = ["67890", "12345"]
    mock_resolve_join_keys.return_value = ["12345", "67890"] if kwargs else None
    run_id = str(uuid.uuid4())
    run_tags = None
    if tags and global_tags:
        run_tags = {**tags, **global_tags}
    elif tags:
        run_tags = tags
    elif global_tags:
        run_tags = global_tags
    assert cli_obj.log(
        application="foobar",
        version=version,
        inputs=test_inputs,
        outputs=test_outputs,
        feedbacks=None,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        run_tags=run_tags,
        row_tags=row_tags,
        run_id=run_id,
        **kwargs,
    ) == [{"event": "place_holder"}]

    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_called_once_with(
        application="foobar",
        inputs=[{"A": 100}, {"A": 101}],
        outputs=[{"B": 300}, {"B": 301}],
        join_keys=["12345", "67890"] if kwargs else ["67890", "12345"],
        version=version,
        ignore_inputs=None,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        run_id=run_id,
        tags=expected_tags_param,
    )
    mock_generate_feedback.assert_not_called()

    mock_sample_records.assert_called_once_with(
        2,
        1,
        [{"A": 100}, {"A": 101}],
        [{"B": 300}, {"B": 301}],
        None,
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )

    if kwargs:
        mock_join_key_gen.assert_not_called()
    else:
        mock_join_key_gen.assert_called()


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_ids": ["12345", "67890"]},
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys", return_value=["12345", "54321"])
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch(
    "gantry.logger.client.Gantry._log_feedback_events", return_value=(None, ["12345", "67890"])
)
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
def test_log_records_feedback_only(
    mock_sample_records,
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    mock_resolve_join_keys,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_feedbacks,
    test_timestamps,
    test_timestamps_list,
    kwargs,
    cli_obj,
):
    assert cli_obj.log_records(
        application="foobar",
        version=version,
        inputs=None,
        outputs=None,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        tags=tags,
        row_tags=row_tags,
        global_tags=global_tags,
        **kwargs,
    ) == (None, ["12345", "67890"])

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_called_once_with(
        "foobar",
        [{"A": 200}, {"A": 201}],
        ["12345", "54321"],
        version,
        test_timestamps_list,
        True,
        False,
        expected_tags_param,
    )

    mock_sample_records.assert_called_once_with(
        2,
        1,
        None,
        None,
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"feedback_keys": ["A"]},
        {"feedback_ids": ["12345", "67890"]},
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys", return_value=["12345", "54321"])
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch(
    "gantry.logger.client.Gantry._log_feedback_events", return_value=(None, ["12345", "67890"])
)
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
def test_single_log_records_feedback_only(
    mock_sample_records,
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    mock_resolve_join_keys,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_feedbacks,
    test_timestamps,
    test_timestamps_list,
    kwargs,
    cli_obj,
):
    assert cli_obj.single_log_records(
        application="foobar",
        version=version,
        inputs=None,
        outputs=None,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        tags=tags,
        row_tags=row_tags,
        global_tags=global_tags,
        **kwargs,
    ) == (None, ["12345", "67890"])

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_called_once_with(
        application="foobar",
        feedbacks=[{"A": 200}, {"A": 201}],
        join_keys=["12345", "54321"],
        feedback_version=version,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        as_batch=False,
        tags=expected_tags_param,
    )

    mock_sample_records.assert_called_once_with(
        2,
        1,
        None,
        None,
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )


@pytest.mark.parametrize(
    "test_timestamps, test_timestamps_list",
    [
        (None, None),
        ([CURRENT_TIME] * 2, [CURRENT_TIME] * 2),
        (np.array([CURRENT_TIME] * 2), [CURRENT_TIME] * 2),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        {"join_keys": ["54321", "67890"]},
        {"join_keys": pd.Series(["54321", "67890"])},
    ],
)
@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
        np.array([{"A": 200}, {"A": 201}]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@pytest.mark.parametrize(
    "tags, row_tags, global_tags, expected_tags_param",
    [
        (None, None, None, [{"env": "test"}, {"env": "test"}]),
        (
            {"bar": "bar"},
            None,
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "bar", "env": "test"}],
        ),
        (
            {"bar": "bar"},
            None,
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "bar", "env": "test", "foo": "foo"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [{"bar": "bar", "env": "test"}, {"bar": "baz", "env": "test"}],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            {"foo": "foo"},
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"foo": "foo"},
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test", "foo": "foo"},
                {"bar": "baz", "env": "test", "foo": "foo"},
            ],
        ),
        (
            {"bar": "bar"},
            [{"foo": "foo"}, {"baz": "baz"}],
            {"env": "foobar"},
            [
                {"bar": "bar", "env": "foobar", "foo": "foo"},
                {"bar": "bar", "env": "foobar", "baz": "baz"},
            ],
        ),
        (
            None,
            [{"bar": "bar"}, {"bar": "baz"}],
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            np.array([{"bar": "bar"}, {"bar": "baz"}]),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.Series(["bar", "baz"], name="bar"),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
        (
            None,
            pd.DataFrame({"bar": ["bar", "baz"]}),
            None,
            [
                {"bar": "bar", "env": "test"},
                {"bar": "baz", "env": "test"},
            ],
        ),
    ],
)
@mock.patch("gantry.logger.client._resolve_join_keys", return_value=["12345", "54321"])
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch(
    "gantry.logger.client.Gantry._generate_feedback_events",
    return_value=([{"event": "place_holder"}], ["12345", "67890"]),
)
@mock.patch("gantry.logger.client._sample_records", side_effect=client._sample_records)
def test_generate_records_feedback_only(
    mock_sample_records,
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    mock_resolve_join_keys,
    version,
    tags,
    row_tags,
    global_tags,
    expected_tags_param,
    test_feedbacks,
    test_timestamps,
    test_timestamps_list,
    kwargs,
    cli_obj,
):
    run_id = str(uuid.uuid4())
    run_tags = None
    if tags and global_tags:
        run_tags = {**tags, **global_tags}
    elif tags:
        run_tags = tags
    elif global_tags:
        run_tags = global_tags
    assert cli_obj.log(
        application="foobar",
        version=version,
        inputs=None,
        outputs=None,
        feedbacks=test_feedbacks,
        timestamps=test_timestamps,
        sort_on_timestamp=True,
        row_tags=row_tags,
        run_tags=run_tags,
        run_id=run_id,
        **kwargs,
    ) == [{"event": "place_holder"}]

    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_called_once_with(
        application="foobar",
        feedbacks=[{"A": 200}, {"A": 201}],
        join_keys=["12345", "54321"],
        feedback_version=version,
        timestamps=test_timestamps_list,
        sort_on_timestamp=True,
        run_id=run_id,
        tags=expected_tags_param,
    )

    mock_sample_records.assert_called_once_with(
        2,
        1,
        None,
        None,
        [{"A": 200}, {"A": 201}],
        client._resolve_join_keys(**kwargs),
        test_timestamps_list,
        expected_tags_param,
    )


@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch(
    "gantry.logger.client.Gantry._log_feedback_events", return_value=(None, ["12345", "67890"])
)
def test_log_records_feedback_only_no_join_keys(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    version,
    test_feedbacks,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version=version,
            inputs=None,
            outputs=None,
            feedbacks=test_feedbacks,
            timestamps=None,
            sort_on_timestamp=True,
        )
        is None
    )

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_feedbacks",
    [
        [{"A": 200}, {"A": 201}],
        pd.DataFrame.from_dict({"A": [200, 201]}),
        pd.Series(name="A", data=[200, 201]),
    ],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch(
    "gantry.logger.client.Gantry._generate_feedback_events", return_value=(None, ["12345", "67890"])
)
def test_generate_records_feedback_only_no_join_keys(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    version,
    test_feedbacks,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version=version,
            inputs=None,
            outputs=None,
            feedbacks=test_feedbacks,
            timestamps=None,
            sort_on_timestamp=True,
        )
        is None
    )

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_feedbacks",
    [None, pd.DataFrame(), [], pd.Series(), np.array([])],
)
@pytest.mark.parametrize(
    "test_outputs",
    [None, pd.DataFrame(), [], pd.Series(), np.array([])],
)
@pytest.mark.parametrize(
    "test_inputs",
    [None, pd.DataFrame(), [], pd.Series(), np.array([])],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
def test_log_records_no_data(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    version,
    test_inputs,
    test_outputs,
    test_feedbacks,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version=version,
            inputs=test_inputs,
            outputs=test_outputs,
            feedbacks=test_feedbacks,
            timestamps=None,
            sort_on_timestamp=True,
        )
        is None
    )

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_feedbacks",
    [None, pd.DataFrame(), [], pd.Series(), np.array([])],
)
@pytest.mark.parametrize(
    "test_outputs",
    [None, pd.DataFrame(), [], pd.Series(), np.array([])],
)
@pytest.mark.parametrize(
    "test_inputs",
    [None, pd.DataFrame(), [], pd.Series(), np.array([])],
)
@pytest.mark.parametrize("version", [None, 10, "1.2.3"])
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
def test_generate_records_no_data(
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    version,
    test_inputs,
    test_outputs,
    test_feedbacks,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version=version,
            inputs=test_inputs,
            outputs=test_outputs,
            feedbacks=test_feedbacks,
            timestamps=None,
            sort_on_timestamp=True,
        )
        is None
    )

    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_feedbacks",
    [None, pd.DataFrame(), [{"A": 3}, {"A": 3}], pd.Series()],
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
def test_log_records_incomplete_preds(
    mock_feedback,
    mock_preds,
    mock_preds_and_feedback,
    test_feedbacks,
    cli_obj,
):
    rv = cli_obj.log_records(
        application="foobar",
        version="2.0.1",
        inputs=[],
        outputs=[{"A": 1}, {"A": 2}],
        feedbacks=test_feedbacks,
        timestamps=None,
        sort_on_timestamp=True,
    )
    assert rv is None

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_feedbacks",
    [None, pd.DataFrame(), [{"A": 3}, {"A": 3}], pd.Series()],
)
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
def test_generate_records_incomplete_preds(
    mock_generate_feedback,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    test_feedbacks,
    cli_obj,
):
    rv = cli_obj.generate_records(
        application="foobar",
        version="2.0.1",
        inputs=[],
        outputs=[{"A": 1}, {"A": 2}],
        feedbacks=test_feedbacks,
        timestamps=None,
        sort_on_timestamp=True,
    )
    assert rv is None

    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedback.assert_not_called()


@pytest.mark.parametrize(
    "test_inputs",
    [[{"A": 100}, {"A": 101}]],
)
@mock.patch("gantry.logger.utils.get_file_linecount")
def test_log_file(mock_line_count, test_inputs):
    log_store = mock.MagicMock()
    gantry = client.Gantry(log_store=log_store, environment="test")
    mock_line_count.return_value = 5

    gantry.log_file(
        "foobar",
        "dir/csv_with_headers.csv",
        version="2.0.1",
    )

    log_store.log_batch.assert_not_called()


@mock.patch("gantry.logger.client.uuid.uuid4", return_value="ABC")
@mock.patch("gantry.logger.client.Gantry._handle_upload")
def test_smart_fileread(mock_handle_upload, mock_uuid, cli_obj):
    data_link = mock.Mock()
    cli_obj._smart_file_read(
        data_link=data_link,
        object_size=10,
        path_name="foobar",
        file=io.StringIO("😎😎"),
        chunk_size=200,
    )

    args, kwargs = mock_handle_upload.call_args

    assert list(args[0]) == [b"\xf0\x9f\x98\x8e\xf0\x9f\x98\x8e"]  # test UTF-8 support
    assert args[1] == data_link
    assert args[2] == 10
    assert args[3] == "ABC_foobar"


@pytest.mark.parametrize(
    ["inputs", "outputs", "feedbacks", "join_keys", "timestamps"],
    [
        ([{"A": 10}] * 10, [{"A": 10}] * 9, None, None, None),
        ([{"A": 10}] * 10, [{"A": 10}] * 9, [{"A": 11}] * 10, ["foobar"] * 10, None),
        ([{"A": 10}] * 9, [{"A": 10}] * 8, [{"A": 11}] * 10, ["foobar"] * 10, None),
        ([{"A": 10}] * 9, None, [{"A": 11}] * 10, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 11, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 11, ["foobar"] * 10, [CURRENT_TIME] * 10),
        (None, None, [{"A": 11}] * 11, ["foobar"] * 10, np.array([CURRENT_TIME] * 10)),
    ],
)
@mock.patch("gantry.logger.client.Gantry._log_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._log_prediction_events")
@mock.patch("gantry.logger.client.Gantry._log_feedback_events")
def test_log_records_size_mismatch(
    mock_feedbacks,
    mock_preds,
    mock_preds_and_feedback,
    inputs,
    outputs,
    feedbacks,
    timestamps,
    join_keys,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version="2.0.1",
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            timestamps=timestamps,
            sort_on_timestamp=True,
            join_keys=join_keys,
        )
        is None
    )

    mock_preds_and_feedback.assert_not_called()
    mock_preds.assert_not_called()
    mock_feedbacks.assert_not_called()


@pytest.mark.parametrize(
    ["inputs", "outputs", "feedbacks", "join_keys", "timestamps"],
    [
        ([{"A": 10}] * 10, [{"A": 10}] * 9, None, None, None),
        ([{"A": 10}] * 10, [{"A": 10}] * 9, [{"A": 11}] * 10, ["foobar"] * 10, None),
        ([{"A": 10}] * 9, [{"A": 10}] * 8, [{"A": 11}] * 10, ["foobar"] * 10, None),
        ([{"A": 10}] * 9, None, [{"A": 11}] * 10, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 11, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 11, ["foobar"] * 10, [CURRENT_TIME] * 10),
        (None, None, [{"A": 11}] * 11, ["foobar"] * 10, np.array([CURRENT_TIME] * 10)),
    ],
)
@mock.patch("gantry.logger.client.Gantry._generate_prediction_and_feedback_events")
@mock.patch("gantry.logger.client.Gantry._generate_prediction_events")
@mock.patch("gantry.logger.client.Gantry._generate_feedback_events")
def test_generate_records_size_mismatch(
    mock_generate_feedbacks,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    inputs,
    outputs,
    feedbacks,
    timestamps,
    join_keys,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version="2.0.1",
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            timestamps=timestamps,
            sort_on_timestamp=True,
            join_keys=join_keys,
        )
        is None
    )

    mock_generate_preds_and_feedback.assert_not_called()
    mock_generate_preds.assert_not_called()
    mock_generate_feedbacks.assert_not_called()


@pytest.mark.parametrize(
    ["inputs", "outputs", "feedbacks", "join_keys", "timestamps"],
    [
        ([{"A": 10}] * 10, [{"A": 10}] * 10, None, None, None),
        ([{"A": 10}] * 10, [{"A": 10}] * 10, [{"A": 11}] * 10, ["foobar"] * 10, None),
        ([{"A": 10}] * 10, [{"A": 10}] * 10, [{"A": 11}] * 10, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 10, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 10, ["foobar"] * 10, [CURRENT_TIME] * 10),
        (None, None, [{"A": 11}] * 10, ["foobar"] * 10, np.array([CURRENT_TIME] * 10)),
    ],
)
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_and_feedback_events",
    return_value=(None, ["12345", "67890"]),
)
@mock.patch(
    "gantry.logger.client.Gantry._log_prediction_events", return_value=(None, ["12345", "67890"])
)
@mock.patch(
    "gantry.logger.client.Gantry._log_feedback_events", return_value=(None, ["12345", "67890"])
)
def test_log_records_size_match(
    mock_feedbacks,
    mock_preds,
    mock_preds_and_feedback,
    inputs,
    outputs,
    feedbacks,
    timestamps,
    join_keys,
    cli_obj,
):
    assert (
        cli_obj.log_records(
            application="foobar",
            version="2.0.1",
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            timestamps=timestamps,
            sort_on_timestamp=True,
            join_keys=join_keys,
        )
        is not None
    )


@pytest.mark.parametrize(
    ["inputs", "outputs", "feedbacks", "join_keys", "timestamps"],
    [
        ([{"A": 10}] * 10, [{"A": 10}] * 10, None, None, None),
        ([{"A": 10}] * 10, [{"A": 10}] * 10, [{"A": 11}] * 10, ["foobar"] * 10, None),
        ([{"A": 10}] * 10, [{"A": 10}] * 10, [{"A": 11}] * 10, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 10, ["foobar"] * 10, None),
        (None, None, [{"A": 11}] * 10, ["foobar"] * 10, [CURRENT_TIME] * 10),
        (None, None, [{"A": 11}] * 10, ["foobar"] * 10, np.array([CURRENT_TIME] * 10)),
    ],
)
@mock.patch(
    "gantry.logger.client.Gantry._generate_prediction_and_feedback_events",
    return_value=(None, ["12345", "67890"]),
)
@mock.patch(
    "gantry.logger.client.Gantry._generate_prediction_events",
    return_value=(None, ["12345", "67890"]),
)
@mock.patch(
    "gantry.logger.client.Gantry._generate_feedback_events", return_value=(None, ["12345", "67890"])
)
def test_generate_records_size_match(
    mock_generate_feedbacks,
    mock_generate_preds,
    mock_generate_preds_and_feedback,
    inputs,
    outputs,
    feedbacks,
    timestamps,
    join_keys,
    cli_obj,
):
    assert (
        cli_obj.generate_records(
            application="foobar",
            version="2.0.1",
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            timestamps=timestamps,
            sort_on_timestamp=True,
            join_keys=join_keys,
        )
        is not None
    )


@pytest.mark.parametrize(
    ("timestamp", "inputs", "outputs", "feedbacks", "join_key", "global_tags", "row_tags"),
    [  # Test all combinations of inputs, outputs, feedbacks, and join_key
        ("T", ["A", "B"], ["C", "D"], ["H", "I"], "E", {"version": "test_version"}, ["G"]),
        # Test without feedbacks and row_tags
        ("T", ["A", "B"], ["D"], None, "E", {"version": "test_version"}, None),
        # Test without inputs and timestamp
        (None, None, None, ["H", "I"], "E", {"version": "test_version"}, ["G"]),
        # Test only with feedbacks and join_key
        (None, None, None, ["H", "I"], "E", None, None),
        # Test only with inputs and global tags
        ("T", ["A", "B"], ["C", "D"], None, None, {"version": "test_version"}, None),
    ],
)
def test_log_from_data_connector(
    timestamp: str,
    inputs: List[str],
    outputs: List[str],
    feedbacks: List[str],
    join_key: str,
    row_tags: List[str],
    global_tags: Dict[str, str],
    cli_obj,
):
    """
    Tests that the log_from_data_connector function calls the log_from_data_connector_async
    function with correct parameters
    """
    cli_obj.log_store = mock.Mock()
    cli_obj.log_from_data_connector(
        application="foobar",
        source_data_connector_name="test-connector",
        timestamp=timestamp,
        inputs=inputs,
        outputs=outputs,
        feedbacks=feedbacks,
        join_key=join_key,
        row_tags=row_tags,
        global_tags=global_tags,
    )

    call_args = cli_obj.log_store.log_from_data_connector_async.call_args
    assert call_args.kwargs == {
        "request": IngestFromDataConnectorRequest(
            application="foobar",
            source_data_connector_name="test-connector",
            timestamp=timestamp,
            inputs=inputs,
            outputs=outputs,
            feedbacks=feedbacks,
            join_key=join_key,
            row_tags=row_tags,
            global_tags=global_tags,
            schedule=None,
            pipeline_name=None,
        )
    }


@pytest.mark.parametrize(
    ("start_on", "frequency", "type", "options"),
    [
        (
            "2023-02-01T00:00:00.000000",
            ScheduleFrequency.EVERY_HOUR,
            ScheduleType.INCREMENTAL_APPEND,
            {"watermark_key": "updated_at"},
        ),
        (
            datetime.datetime.utcnow(),
            ScheduleFrequency.EVERY_2_HOURS,
            ScheduleType.INCREMENTAL_APPEND,
            {"watermark_key": None},
        ),
        (
            datetime.datetime.utcnow(),
            ScheduleFrequency.EVERY_4_HOURS,
            ScheduleType.INCREMENTAL_APPEND,
            {"watermark_key": "updated_at"},
        ),
        (
            datetime.datetime.utcnow(),
            ScheduleFrequency.EVERY_4_HOURS,
            ScheduleType.INCREMENTAL_APPEND,
            {"delay_time": 300, "watermark_key": "updated_at"},
        ),
    ],
)
def test_log_from_data_connector_with_schedule(
    start_on: Union[datetime.datetime, str],
    frequency: ScheduleFrequency,
    type: ScheduleType,
    options: Dict[str, str],
    cli_obj,
):
    """
    Tests that the log_from_data_connector function calls the log_from_data_connector_async
    function with correct parameters
    """
    cli_obj.log_store = mock.Mock()
    cli_obj.log_from_data_connector(
        application="foobar",
        source_data_connector_name="test-connector",
        timestamp="T",
        inputs=["A", "B"],
        outputs=["C", "D"],
        feedbacks=["E", "F"],
        join_key="H",
        row_tags=["I", "J"],
        global_tags={"version": "test_version"},
        schedule=Schedule(
            start_on=start_on,
            frequency=frequency,
            type=type,
            options=ScheduleOptions(**options),
        ),
    )

    call_args = cli_obj.log_store.log_from_data_connector_async.call_args
    assert call_args.kwargs == {
        "request": IngestFromDataConnectorRequest(
            application="foobar",
            source_data_connector_name="test-connector",
            timestamp="T",
            inputs=["A", "B"],
            outputs=["C", "D"],
            feedbacks=["E", "F"],
            join_key="H",
            row_tags=["I", "J"],
            global_tags={"version": "test_version"},
            schedule=Schedule(
                start_on=start_on.isoformat()
                if isinstance(start_on, datetime.datetime)
                else start_on,
                frequency=frequency,
                type=type,
                options=ScheduleOptions(**options),
            ),
            pipeline_name=None,
        )
    }
