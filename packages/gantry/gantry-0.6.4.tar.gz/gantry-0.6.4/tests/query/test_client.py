import datetime
import re

import mock
import pytest
import responses
from responses import matchers

from gantry.api_client import APIClient
from gantry.exceptions import GantryException, GantryRequestException
from gantry.query.client import COLOR_OPTIONS_FOR_VIEW, GantryQuery
from gantry.query.core.dataframe import GantryDataFrame

from .conftest import END_TIME, ORIGIN, SOME_DURATION, START_TIME


@pytest.fixture
def gantry_query_obj():
    api_client = APIClient(origin=ORIGIN, api_key="abcd1234")
    return GantryQuery(api_client)


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        ({"application_1": {}, "application_2": {}}, ["application_1", "application_2"]),
        (
            {
                "application": {},
            },
            ["application"],
        ),
        ({}, []),
    ],
)
def test_list_applications(data, expected, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models".format(ORIGIN),
            match=[matchers.query_param_matcher({"limit": "10"})],
            json={
                "response": "ok",
                "data": data,
            },
        )

        assert gantry_query_obj.list_applications() == expected


@pytest.mark.parametrize(
    ["versions", "expected"],
    [
        ([{"internal_version": 10, "version": "baz"}], ["baz"]),
        (
            [
                {"internal_version": 10, "version": "baz"},
                {"internal_version": 20, "version": "bar"},
            ],
            ["baz", "bar"],
        ),
        ([], []),
    ],
)
def test_list_application_versions(versions, expected, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar".format(ORIGIN),
            match=[matchers.query_param_matcher({"include_names": "True"})],
            json={"response": "ok", "data": {"versions": versions}},
        )

        assert gantry_query_obj.list_application_versions("foobar") == expected


@pytest.mark.parametrize(
    ["envs", "expected"],
    [
        (["A", "B", "C"], ["A", "B", "C"]),
        ([], []),
    ],
)
def test_list_application_environments(envs, expected, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar".format(ORIGIN),
            json={"response": "ok", "data": {"environments": envs}},
        )

        assert gantry_query_obj.list_application_environments("foobar") == expected


@pytest.mark.parametrize("batch_id", [None, "foobar"])
@mock.patch(
    "gantry.query.client._build_batch_id_filter", return_value={"batch_id_filter": "barbaz"}
)
@mock.patch("gantry.query.client._get_application_batches", return_value=[{"id": "foobar"}])
def test_query(mock_get_application_batches, mock_build_batch_filter, batch_id, gantry_query_obj):
    application = "foobar"
    version = "1.2.3"
    environment = "env"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/foobar/schemas".format(ORIGIN),
            json={"response": "ok", "data": {"id": "ABCD1234", "environments": []}},
            match=[
                matchers.query_param_matcher(
                    {
                        "end_time": "2008-09-10 23:58:23",
                        "start_time": "2008-09-03 20:56:35",
                        "version": "1.2.3",
                    }
                )
            ],
        )

        gantry_df = gantry_query_obj.query(
            application,
            START_TIME,
            END_TIME,
            version,
            environment,
            [{"filter": "foobar"}],
            batch_id=batch_id,
        )

        assert isinstance(gantry_df, GantryDataFrame)
        assert gantry_df.api_client == gantry_query_obj._api_client
        assert gantry_df.filters == (
            [{"filter": "foobar"}]
            if batch_id is None
            else [{"filter": "foobar"}, {"batch_id_filter": "barbaz"}]
        )

        assert gantry_df.query_info.application == application
        assert gantry_df.query_info.version == version
        assert gantry_df.query_info.environment == environment
        assert gantry_df.query_info.start_time == START_TIME
        assert gantry_df.query_info.end_time == END_TIME


@mock.patch("gantry.query.client.GantryDataFrame.from_view")
@mock.patch("gantry.query.client.GantryQuery.list_application_views")
def test_query_with_view(mock_application_views, mock_factory, gantry_query_obj):
    mock_application_views.return_value = ["barbaz"]
    mock_factory.return_value = "data"

    assert (
        gantry_query_obj.query(
            "foobar", version="1.2.3", environment="foo", view="barbaz", tags={"foo": "bar"}
        )
        == "data"
    )
    mock_factory.assert_called_once_with(
        gantry_query_obj._api_client, "foobar", "barbaz", "1.2.3", "foo", tags={"foo": "bar"}
    )


@mock.patch("gantry.query.client.GantryQuery.list_application_views")
def test_query_with_view_not_found(mock_application_views, gantry_query_obj):
    mock_application_views.return_value = ["A", "B", "C"]

    with pytest.raises(ValueError):
        _ = gantry_query_obj.query("foobar", view="not-found")


@mock.patch(
    "gantry.query.client._get_application_batches",
    return_value=[{"id": "foobar"}, {"id": "barbaz"}],
)
def test_query_with_batch_id_not_found(mock_application_batches, gantry_query_obj):
    with pytest.raises(ValueError):
        _ = gantry_query_obj.query("foobar", batch_id="not-found")


@pytest.mark.parametrize(
    ["start_time", "end_time", "filters", "batch_id"],
    [
        (START_TIME, None, None, None),
        (START_TIME, None, {}, None),
        (START_TIME, END_TIME, None, None),
        (None, END_TIME, {}, None),
        (None, END_TIME, None, None),
        (START_TIME, END_TIME, {"foo": "bar"}, None),
        (None, None, {"foo": "bar"}, None),
        (None, END_TIME, {"foo": "bar"}, None),
        (START_TIME, None, {"foo": "bar"}, None),
        (None, None, {}, "foobar"),
        (None, None, {}, None),
        (START_TIME, None, {"foo": "bar"}, "foobar"),
    ],
)
def test_query_invalid_call_with_view_and_others(
    start_time, end_time, filters, batch_id, gantry_query_obj
):
    with pytest.raises(ValueError):
        _ = gantry_query_obj.query(
            "foobar", start_time, end_time, filters=filters, batch_id=batch_id, view="foobar"
        )


def test_get_current_feedback_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.get_current_metric_schema("application")


def test_update_feedback_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.update_feedback_schema("application", [])


def test_add_feedback_field(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.add_feedback_field("application", {})


def test_get_current_metric_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.get_current_metric_schema("application")


def test_update_metric_schema(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.update_metric_schema("application", [])


def test_add_metric(gantry_query_obj):
    with pytest.raises(NotImplementedError):
        gantry_query_obj.add_metric("application", {})


@pytest.mark.parametrize(
    ["duration", "start_time", "end_time"],
    [
        (SOME_DURATION, START_TIME, None),
        (SOME_DURATION, None, END_TIME),
        (SOME_DURATION, START_TIME, END_TIME),
        (None, None, END_TIME),
        (None, START_TIME, None),
        (None, None, None),
    ],
)
@mock.patch("gantry.query.client.get_application_node_id")
def test_create_view_invalid_time_params(
    mock_get_app_node_id, gantry_query_obj, duration, start_time, end_time
):
    mock_get_app_node_id.return_value = "foobar12345"
    with pytest.raises(ValueError):
        gantry_query_obj.create_view(
            application="foo",
            name="bar",
            version="2",
            duration=duration,
            start_time=start_time,
            end_time=end_time,
        )


@pytest.mark.parametrize(
    ["app", "version", "error_msg"],
    [
        ("foo", "2", re.escape("Application foo[2] does not exist.")),
        ("foobar", None, re.escape("Application foobar[latest] does not exist.")),
    ],
)
@mock.patch("gantry.query.client.get_application_node_id")
def test_create_view_inexistent_model(
    mock_get_app_node_id, gantry_query_obj, app, version, error_msg
):
    mock_get_app_node_id.side_effect = GantryRequestException("staging.com", 100, "error msg")
    with pytest.raises(ValueError, match=error_msg):
        gantry_query_obj.create_view(
            application=app,
            name="bar",
            version=version,
            duration=datetime.timedelta(days=1),
        )


@pytest.mark.parametrize(
    ["kwargs", "expected_data"],
    [
        (
            {
                "application": "baz",
                "name": "foo",
                "version": "1.2.3",
                "tag_filters": {"foo": "bar"},
                "data_filters": [{"some": "filter"}],
                "duration": datetime.timedelta(days=1),
            },
            {
                "name": "foo",
                "model_node_id": "foobar12345",
                "tag_filters": {"foo": "bar"},
                "data_filters": [{"some": "filter"}],
                "details": {"color": "#foobar"},
                "duration": "P1D",
            },
        ),
        (
            {
                "application": "baz",
                "name": "foo",
                "version": "1.2.3",
                "data_filters": [],
                "start_time": START_TIME,
                "end_time": END_TIME,
            },
            {
                "name": "foo",
                "model_node_id": "foobar12345",
                "tag_filters": {},
                "data_filters": [],
                "details": {"color": "#foobar"},
                "start_time": "2008-09-03T20:56:35Z",
                "end_time": "2008-09-10T23:58:23Z",
            },
        ),
    ],
)
@mock.patch("gantry.query.client.random.choice", return_value="#foobar")
@mock.patch("gantry.query.client.get_application_node_id")
def test_create_view(mock_get_app_node_id, mock_choice, kwargs, expected_data, gantry_query_obj):
    mock_get_app_node_id.return_value = "foobar12345"
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/views".format(ORIGIN),
            json={
                "response": "ok",
                "data": "OK",
            },
            match=[matchers.json_params_matcher(expected_data)],
        )

        gantry_query_obj.create_view(**kwargs)
    mock_get_app_node_id.assert_called_once_with(
        gantry_query_obj._api_client, kwargs["application"], version=kwargs["version"]
    )
    mock_choice.assert_called_once_with(COLOR_OPTIONS_FOR_VIEW)


@pytest.mark.parametrize(
    ["kwargs", "expected_data"],
    [
        (
            {
                "application": "baz",
                "name": "foo",
                "version": "1.2.3",
                "tag_filters": {"foo": "bar"},
                "data_filters": [{"some": "filter"}],
                "duration": datetime.timedelta(days=1),
            },
            {
                "name": "foo",
                "model_node_id": "foobar12345",
                "tag_filters": {"foo": "bar"},
                "data_filters": [{"some": "filter"}],
                "details": {"color": "#foobar"},
                "duration": "P1D",
            },
        ),
        (
            {
                "application": "baz",
                "name": "foo",
                "version": "1.2.3",
                "data_filters": [],
                "start_time": START_TIME,
                "end_time": END_TIME,
            },
            {
                "name": "foo",
                "model_node_id": "foobar12345",
                "tag_filters": {},
                "data_filters": [],
                "details": {"color": "#foobar"},
                "start_time": "2008-09-03T20:56:35Z",
                "end_time": "2008-09-10T23:58:23Z",
            },
        ),
    ],
)
@mock.patch("gantry.query.client.random.choice", return_value="#foobar")
@mock.patch("gantry.query.client.get_application_node_id")
def test_create_view_error(
    mock_get_app_node_id, mock_choice, kwargs, expected_data, gantry_query_obj
):
    mock_get_app_node_id.return_value = "foobar12345"
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/views".format(ORIGIN),
            json={
                "response": "not ok",
                "data": "OK",
            },
            status=400,
            match=[matchers.json_params_matcher(expected_data)],
        )

        with pytest.raises(GantryException):
            gantry_query_obj.create_view(**kwargs)

        mock_choice.assert_called_once_with(COLOR_OPTIONS_FOR_VIEW)


VIEWS_DATA = [
    {"name": "view_1", "tag_filters": {"env": "env-A"}, "other": "A"},
    {"name": "view_2", "tag_filters": {"env": "env-B"}, "other": "B"},
    {"name": "view_3", "tag_filters": {"env": "env-B"}, "other": "C"},
]


@pytest.mark.parametrize(
    ["env", "response_data", "expected", "version"],
    [("dev", [], [], "1.2.3"), ("env-A", VIEWS_DATA, ["view_1"], "1.2.3")],
)
def test_list_application_views_with_other_env(
    gantry_query_obj, env, response_data, expected, version
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/barbaz/views?version={}".format(ORIGIN, version),
            json={
                "response": "ok",
                "data": response_data,
            },
        )

        assert (
            gantry_query_obj.list_application_views("barbaz", version="1.2.3", environment=env)
            == expected
        )


@pytest.mark.parametrize(
    ["response_data", "version"],
    [([], "1.2.3"), (VIEWS_DATA, "1.2.3")],
)
def test_print_application_info(response_data, version, gantry_query_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/barbaz".format(ORIGIN),
            json={
                "response": "ok",
                "data": {
                    "versions": [
                        {"internal_version": 10, "version": version},
                    ],
                    "environments": ["dev", "prod"],
                },
            },
        )
        rsps.add(
            responses.GET,
            "{}/api/v1/applications/barbaz/views".format(ORIGIN),
            json={
                "response": "ok",
                "data": response_data,
            },
            match=[matchers.query_param_matcher({"version": version})],
        )

        assert gantry_query_obj.print_application_info("barbaz") is None


@mock.patch("gantry.query.client._get_application_batches", return_value=["foo", "bar"])
def test_list_application_batches(mock_get_application_batches, gantry_query_obj):
    assert gantry_query_obj.list_application_batches("app", "2") == ["foo", "bar"]
    mock_get_application_batches.assert_called_once_with(gantry_query_obj._api_client, "app", "2")
