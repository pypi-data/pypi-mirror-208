import json
import tempfile
from contextlib import nullcontext as does_not_raise
from io import StringIO

import mock
import pandas as pd
import pytest
import responses
from freezegun import freeze_time

from gantry.exceptions import (  # noqa
    GantryBatchCreationException,
    GantryLoggingException,
)
from gantry.logger import utils
from gantry.logger.constants import BatchType, UploadFileType
from gantry.logger.stores import APILogStore
from gantry.logger.types import DataLink, DataLinkElement
from gantry.logger.utils import (
    JoinKey,
    _batch_success_msg,
    _build_batch_iterator,
    _build_success_msg,
    _concurrent_upload_multipart_batch,
    _is_empty,
    _is_not_empty,
    _log_exception,
    _put_block,
)


@pytest.mark.parametrize(
    ["test_obj", "expected_result"],
    [
        (pd.DataFrame(), True),
        (pd.DataFrame.from_dict({"A": [200, 201]}), False),
        ([1, 2, 3], False),
        ([], True),
        (None, True),
    ],
)
def test_is_empty(test_obj, expected_result):
    assert _is_empty(test_obj) is expected_result


@pytest.mark.parametrize(
    ["test_obj", "expected_result"],
    [
        (pd.DataFrame(), False),
        (pd.DataFrame.from_dict({"A": [200, 201]}), True),
        ([1, 2, 3], True),
        ([], False),
        (None, False),
    ],
)
def test_is_not_empty(test_obj, expected_result):
    assert _is_not_empty(test_obj) is expected_result


def test_log_exception():
    try:
        _log_exception(lambda: exec("raise(GantryLoggingException())"))()
    except Exception as e:
        pytest.fail(f"_log_exception() failed due to raising {e}")
    with pytest.raises(GantryBatchCreationException):
        _log_exception(lambda: exec("raise(GantryBatchCreationException())"))()
    try:
        _log_exception(lambda: exec("raise(Exception())"))()
    except Exception as e:
        pytest.fail(f"_log_exception() failed due to raising {e}")


def test_build_batch_iterator():
    event_list = [{1: 1}, {2: 2}, {3: 3}, {4: 4}, {5: 5}]
    # We should only have 3 batches created from the list.
    batch_iter = _build_batch_iterator(event_list, 2)
    iters = 0
    for _ in batch_iter:
        iters += 1
    assert iters == 3

    # We should still have all 5 lines in the file
    batch_iter = _build_batch_iterator(event_list, 2)
    result = "".join([part.decode("utf-8") for part in batch_iter])
    file = StringIO(result)

    for line in file.readlines():
        json.loads(line)

    file.seek(0)
    assert len(file.readlines()) == 5


def test_put_block():
    def custom_matcher(req):
        return (
            req.body == b"foobar",
            "Body doesn't match",
        )

    with responses.RequestsMock() as resp:
        resp.add(
            resp.PUT,
            url="http://foo/bar",
            headers={"ETag": "0123456789", "Content-Type": "application/json"},
            match=[custom_matcher],
        )
        res = _put_block("http://foo/bar", 10, b"foobar")
        assert res == {"ETag": "0123456789", "PartNumber": 10}


@mock.patch("gantry.logger.utils._put_block")
def test_concurrent_upload(mock_put_block):
    mock_put_block.side_effect = [
        {"ETag": "123", "PartNumber": 2},
        {"ETag": "456", "PartNumber": 1},
        {"ETag": "789", "PartNumber": 3},
    ]

    data = [{"1": "foo"}, {"2": "bar"}, {"3": "baz"}]
    signed_urls = ["http://foo", "http://bar", "http://baz"]

    ret = _concurrent_upload_multipart_batch(iter(data), signed_urls)
    assert ret == [
        {"ETag": "456", "PartNumber": 1},
        {"ETag": "123", "PartNumber": 2},
        {"ETag": "789", "PartNumber": 3},
    ]


@pytest.mark.parametrize(
    ["host", "application", "expected"],
    [
        (
            "https://staging.com/",
            "app",
            "Track your batch at https://staging.com/applications/app/jobs",
        ),
        (
            "https://staging.com",
            "app",
            "Track your batch at https://staging.com/applications/app/jobs",
        ),
        (
            "https://staging.com",
            "my app",
            "Track your batch at https://staging.com/applications/my%20app/jobs",
        ),
    ],
)
def test_build_success_msg(host, application, expected):
    assert _build_success_msg(host, application) == expected


@mock.patch("gantry.logger.utils._build_success_msg")
def test_batch_success_msg(mock_build_msg):
    log_store = mock.Mock(__class__=APILogStore)
    _batch_success_msg("12345", "app", log_store)
    mock_build_msg.assert_called_with(log_store._api_client._host, "app")


@pytest.mark.parametrize(
    ["dict_", "expected"],
    [
        ({"foo": "bar", "bar": "baz"}, "44258089824ec9db73fd592f418fbea1"),
        ({"bar": "baz", "foo": "bar"}, "44258089824ec9db73fd592f418fbea1"),
        ({"foo": "bar", "bar": 10}, "01debdea5ba523b44164d202fbbe42da"),
        ({"bar": None, "foo": "bar"}, "ade3188c2cfeae4234e0b7b042b74c35"),
        ({"foo": True, "bar": 10.4321}, "294ca280f5485b49fec1247e5b45d644"),
        ({"bar": [1, 2, 3], "foo": {"another": "dict"}}, "152874e4c1db6061d5a45ee38c3eace0"),
    ],
)
def test_join_key_from_dict(dict_, expected):
    assert JoinKey.from_dict(dict_) == expected


@pytest.mark.parametrize("dict_", [None, True, 10, "something"])
def test_join_key_from_dict_error(dict_):
    with pytest.raises(TypeError):
        _ = JoinKey.from_dict(dict_)


@pytest.mark.parametrize(
    "content, sep, expected",
    [
        (
            """a, b, c
            10, 20, 30""",
            ",",
            ["a", "b", "c"],
        ),
        (
            """a,        b,       c
            10, 20, 30""",
            ",",
            ["a", "b", "c"],
        ),
        (
            """a\tb\tc
            10\t20\t30""",
            "\t",
            ["a", "b", "c"],
        ),
        (
            '''"a",        "b",       "c"
            "foo", "bar", "baz"''',
            ",",
            ["a", "b", "c"],
        ),
    ],
)
def test_csv_columns(content, sep, expected):
    with tempfile.NamedTemporaryFile("w") as tmp:
        tmp.write(content)
        tmp.flush()
        assert utils._get_csv_columns(tmp.name, sep) == expected


@pytest.mark.parametrize(
    "target, columns, expectation",
    [
        ("foo", ["foo", "bar"], does_not_raise()),
        ("foo", ["bar", "baz"], pytest.raises(ValueError)),
    ],
)
def test_validate_column(target, columns, expectation):
    with expectation:
        utils._validate_column(target, columns)


@pytest.mark.parametrize(
    "targets, columns, expectation",
    [
        (["foo"], ["foo", "bar"], does_not_raise()),
        (["foo", "bar"], ["foo", "bar"], does_not_raise()),
        (["foo", "bar"], ["bar", "baz"], pytest.raises(ValueError)),
        (["foo"], ["bar", "baz"], pytest.raises(ValueError)),
    ],
)
def test_validate_columns(targets, columns, expectation):
    with expectation:
        utils._validate_columns(targets, columns)


@pytest.mark.parametrize(
    "inputs, outputs, feedback, expected",
    [
        ({"foo": "bar"}, {"bar": "baz"}, None, BatchType.PREDICTION),
        ({"foo": "bar"}, {"bar": "baz"}, {"baz": "bax"}, BatchType.RECORD),
        ({}, {}, {"baz": "bax"}, BatchType.FEEDBACK),
    ],
)
def test_feature_to_column_mapping_get_batch_type(inputs, outputs, feedback, expected):
    assert (
        utils._FeatureToColumnMapping(
            inputs=inputs,
            outputs=outputs,
            feedback=feedback,
        ).get_batch_type()
        == expected
    )


@pytest.mark.parametrize(
    "inputs, outputs, feedback, feedback_id, expectation",
    [
        ({}, {"foo": "bar"}, {}, {}, pytest.raises(ValueError)),
        ({"bar": "baz"}, {"foo": "bar"}, {}, {}, does_not_raise()),
        ({"bar": "baz"}, {"foo": "bar"}, {"baz": "bax"}, {"foo": "bar"}, does_not_raise()),
        ({"bar": "baz"}, {"foo": "bar"}, {"baz": "bax"}, {}, pytest.raises(ValueError)),
        (None, None, None, {}, pytest.raises(ValueError)),
        ({}, {}, {}, {}, pytest.raises(ValueError)),
    ],
)
def test_feature_to_column_mapping_validate(inputs, outputs, feedback, feedback_id, expectation):
    with expectation:
        utils._FeatureToColumnMapping(
            inputs=inputs, outputs=outputs, feedback=feedback, feedback_id=feedback_id
        ).validate()


@pytest.mark.parametrize(
    "columns, inputs, outputs, feedback, tags, timestamp, feedback_id,"
    "feedback_keys, join_key, expected",
    [
        (
            ["a", "b", "c", "f", "f.id", "foo", "bar"],
            ["a", "b"],
            ["c"],
            ["f"],
            None,
            None,
            "f.id",
            ["foo", "bar"],
            None,
            utils._FeatureToColumnMapping(
                timestamp={},
                inputs={"a": DataLinkElement(ref=0), "b": DataLinkElement(ref=1)},
                outputs={"c": DataLinkElement(ref=2)},
                feedback={"f": DataLinkElement(ref=3)},
                tags={},
                feedback_id={"f.id": DataLinkElement(ref=4)},
                feedback_keys=["foo", "bar"],
            ),
        ),
        (
            ["a", "b", "output_c", "timestamp", "tags.A"],
            ["a", "b"],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            utils._FeatureToColumnMapping(
                timestamp={"timestamp": DataLinkElement(ref=3)},
                inputs={"a": DataLinkElement(ref=0), "b": DataLinkElement(ref=1)},
                outputs={"output_c": DataLinkElement(ref=2)},
                feedback={},
                tags={"tags.A": DataLinkElement(ref=4)},
                feedback_id={},
                feedback_keys=[],
            ),
        ),
        (
            ["inputs.a", "inputs.b", "c", "other_timestamp", "some_tag"],
            None,
            ["c"],
            None,
            ["some_tag"],
            "other_timestamp",
            None,
            None,
            None,
            utils._FeatureToColumnMapping(
                timestamp={"other_timestamp": DataLinkElement(ref=3)},
                inputs={"inputs.a": DataLinkElement(ref=0), "inputs.b": DataLinkElement(ref=1)},
                outputs={"c": DataLinkElement(ref=2)},
                feedback={},
                tags={"some_tag": DataLinkElement(ref=4)},
                feedback_id={},
                feedback_keys=[],
            ),
        ),
        (
            ["a", "b", "c", "f", "join_key", "foo", "bar"],
            ["a", "b"],
            ["c"],
            ["f"],
            None,
            None,
            None,
            None,
            None,
            utils._FeatureToColumnMapping(
                timestamp={},
                inputs={"a": DataLinkElement(ref=0), "b": DataLinkElement(ref=1)},
                outputs={"c": DataLinkElement(ref=2)},
                feedback={"f": DataLinkElement(ref=3)},
                tags={},
                feedback_id={"join_key": DataLinkElement(ref=4)},
                feedback_keys=[],
                _join_key={"join_key": DataLinkElement(ref=4)},
            ),
        ),
        (
            ["a", "b", "c", "f", "other_join_key", "foo", "bar"],
            ["a", "b"],
            ["c"],
            ["f"],
            None,
            None,
            None,
            None,
            "other_join_key",
            utils._FeatureToColumnMapping(
                timestamp={},
                inputs={"a": DataLinkElement(ref=0), "b": DataLinkElement(ref=1)},
                outputs={"c": DataLinkElement(ref=2)},
                feedback={"f": DataLinkElement(ref=3)},
                tags={},
                feedback_id={"other_join_key": DataLinkElement(ref=4)},
                feedback_keys=[],
                _join_key={"other_join_key": DataLinkElement(ref=4)},
            ),
        ),
    ],
)
@mock.patch("gantry.logger.utils._validate_column")
@mock.patch("gantry.logger.utils._validate_columns")
def test_feature_to_column_mapping_from_columns(
    mock_validate_columns,
    mock_validate_column,
    columns,
    inputs,
    outputs,
    feedback,
    tags,
    timestamp,
    feedback_id,
    feedback_keys,
    join_key,
    expected,
):
    assert (
        utils._FeatureToColumnMapping.from_columns(
            columns,
            inputs,
            outputs,
            feedback,
            tags,
            timestamp,
            feedback_id,
            feedback_keys,
            join_key,
        )
        == expected
    )
    mock_validate_columns.assert_called()
    if timestamp or feedback_id:
        mock_validate_column.assert_called()
    else:
        mock_validate_column.assert_not_called()


@pytest.mark.parametrize(
    "columns, inputs, outputs, feedback, tags, timestamp, feedback_id," "feedback_keys, join_key",
    [
        (
            ["a", "b", "c", "f", "other_join_key", "foo", "bar", "feedback_id"],
            ["a", "b"],
            ["c"],
            ["f"],
            None,
            None,
            None,
            None,
            "other_join_key",
        ),
        (
            ["a", "b", "c", "f", "other_join_key", "foo", "bar", "feedback_id"],
            ["a", "b"],
            ["c"],
            ["f"],
            None,
            None,
            "feedback_id",
            None,
            "other_join_key",
        ),
        (
            ["a", "b", "c", "f", "other_join_key", "foo", "bar", "feedback_id"],
            ["a", "b"],
            ["c"],
            ["f"],
            None,
            None,
            "feedback_id",
            ["a", "b"],
            "other_join_key",
        ),
    ],
)
@mock.patch("gantry.logger.utils._validate_column")
@mock.patch("gantry.logger.utils._validate_columns")
def test_feature_to_column_mapping_from_columns_deprecation_error(
    mock_validate_columns,
    mock_validate_column,
    columns,
    inputs,
    outputs,
    feedback,
    tags,
    timestamp,
    feedback_id,
    feedback_keys,
    join_key,
):
    with pytest.raises(ValueError):
        utils._FeatureToColumnMapping.from_columns(
            columns,
            inputs,
            outputs,
            feedback,
            tags,
            timestamp,
            feedback_id,
            feedback_keys,
            join_key,
        )


@freeze_time("2012-01-14")
@mock.patch("gantry.logger.utils.get_file_linecount")
@mock.patch("gantry.logger.utils._get_csv_columns")
@mock.patch("gantry.logger.utils._FeatureToColumnMapping.from_columns")
def test_build_data_link_from_file_deprecated(
    mock_from_cols, mock_get_csv_columns, mock_get_file_linecount
):
    mock_get_file_linecount.return_value = 1001
    mock_get_csv_columns.return_value = ["foo", "bar"]
    validate_mock = mock.Mock()
    mock_from_cols.return_value = mock.Mock(
        inputs="parsed_inputs",
        outputs="parsed_outputs",
        feedback="parsed_feedback",
        timestamp="parsed_ts",
        feedback_id="parsed_fid",
        feedback_keys="parsed_fkeys",
        tags="parsed_tags",
        get_batch_type=mock.Mock(return_value=BatchType.PREDICTION),
        validate=validate_mock,
    )

    assert utils._build_data_link_from_file(
        application="my-app",
        filepath="/some/file/to/upload",
        sep="\t",
        version="1.2.3",
        timestamp="some-timestamp",
        inputs=["a", "b"],
        outputs=["c"],
        feedback=["f"],
        tags=["foo", "bar"],
        feedback_id="baz",
        feedback_keys=["c"],
        join_key=None,
    ) == DataLink(
        file_type=UploadFileType.CSV_WITH_HEADERS,
        batch_type=BatchType.PREDICTION,
        num_events=1000,
        application="my-app",
        version="1.2.3",
        log_timestamp="2012-01-14T00:00:00",
        inputs="parsed_inputs",
        outputs="parsed_outputs",
        feedback="parsed_feedback",
        timestamp="parsed_ts",
        feedback_id="parsed_fid",
        feedback_keys="parsed_fkeys",
        tags="parsed_tags",
    )

    mock_get_csv_columns.assert_called_with("/some/file/to/upload", "\t")
    mock_from_cols.assert_called_with(
        ["foo", "bar"],
        ["a", "b"],
        ["c"],
        ["f"],
        ["foo", "bar"],
        "some-timestamp",
        "baz",
        ["c"],
        None,
    )
    validate_mock.assert_called_once()


@freeze_time("2012-01-14")
@mock.patch("gantry.logger.utils.get_file_linecount")
@mock.patch("gantry.logger.utils._get_csv_columns")
@mock.patch("gantry.logger.utils._FeatureToColumnMapping.from_columns")
def test_build_data_link_from_file(mock_from_cols, mock_get_csv_columns, mock_get_file_linecount):
    mock_get_file_linecount.return_value = 1001
    mock_get_csv_columns.return_value = ["foo", "bar"]
    validate_mock = mock.Mock()
    mock_from_cols.return_value = mock.Mock(
        inputs="parsed_inputs",
        outputs="parsed_outputs",
        feedback="parsed_feedback",
        timestamp="parsed_ts",
        feedback_id="some_join_key",
        feedback_keys=None,
        tags="parsed_tags",
        get_batch_type=mock.Mock(return_value=BatchType.PREDICTION),
        validate=validate_mock,
    )

    assert utils._build_data_link_from_file(
        application="my-app",
        filepath="/some/file/to/upload",
        sep="\t",
        version="1.2.3",
        timestamp="some-timestamp",
        inputs=["a", "b"],
        outputs=["c"],
        feedback=["f"],
        tags=["foo", "bar"],
        join_key="some_join_key",
        feedback_id=None,
        feedback_keys=None,
    ) == DataLink(
        file_type=UploadFileType.CSV_WITH_HEADERS,
        batch_type=BatchType.PREDICTION,
        num_events=1000,
        application="my-app",
        version="1.2.3",
        log_timestamp="2012-01-14T00:00:00",
        inputs="parsed_inputs",
        outputs="parsed_outputs",
        feedback="parsed_feedback",
        timestamp="parsed_ts",
        feedback_id="some_join_key",
        feedback_keys=None,
        tags="parsed_tags",
    )

    mock_get_csv_columns.assert_called_with("/some/file/to/upload", "\t")
    mock_from_cols.assert_called_with(
        ["foo", "bar"],
        ["a", "b"],
        ["c"],
        ["f"],
        ["foo", "bar"],
        "some-timestamp",
        None,
        None,
        "some_join_key",
    )
    validate_mock.assert_called_once()


def test_build_data_link_integration_deprecated(datadir):
    csv_file = datadir / "feedback_deprecated.csv"
    data_link = utils._build_data_link_from_file(
        application="test_app",
        filepath=str(csv_file),
        sep=",",
        version="1.2.3",
        feedback_id=None,
        feedback=["test_float", "test_int"],
        timestamp=None,
        inputs=None,
        outputs=None,
        tags=None,
        feedback_keys=None,
        join_key=None,
    )

    assert data_link.application == "test_app"
    assert data_link.version == "1.2.3"
    assert data_link.file_type == UploadFileType.CSV_WITH_HEADERS
    assert data_link.batch_type == BatchType.FEEDBACK
    assert data_link.feedback_id["feedback_id"].ref == 0
    assert data_link.feedback["test_float"].ref == 1
    assert data_link.feedback["test_int"].ref == 2


def test_build_data_link_integration(datadir):
    csv_file = datadir / "feedback.csv"
    data_link = utils._build_data_link_from_file(
        application="test_app",
        filepath=str(csv_file),
        sep=",",
        version="1.2.3",
        feedback_id=None,
        feedback=["test_float", "test_int"],
        timestamp=None,
        inputs=None,
        outputs=None,
        tags=None,
        feedback_keys=None,
        join_key="some_join_key",
    )

    assert data_link.application == "test_app"
    assert data_link.version == "1.2.3"
    assert data_link.file_type == UploadFileType.CSV_WITH_HEADERS
    assert data_link.batch_type == BatchType.FEEDBACK
    assert data_link.feedback_id["some_join_key"].ref == 0
    assert data_link.feedback["test_float"].ref == 1
    assert data_link.feedback["test_int"].ref == 2
