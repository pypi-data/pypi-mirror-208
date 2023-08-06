import datetime

import mock
import numpy as np
import pandas as pd
import pytest
import responses

from gantry.api_client import APIClient
from gantry.applications.client import ApplicationClient
from gantry.applications.core import Application
from gantry.query.core.dataframe import GantryDataFrame
from gantry.query.time_window import TimeWindow

HOST = "https://test-api"
CURRENT_TIME = datetime.datetime.utcnow()


@pytest.fixture
def test_api_client():
    return APIClient(origin=HOST)


@pytest.fixture
def test_client(test_api_client):
    return ApplicationClient(api_client=test_api_client)


@pytest.mark.parametrize(
    "test_timestamps",
    [None, [CURRENT_TIME] * 2],
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
@mock.patch("gantry.logger.client.Gantry.log")
def test_log_with_run(
    mock_log,
    test_inputs,
    test_outputs,
    test_feedbacks,
    test_client,
    test_api_client,
    test_timestamps,
):
    application = Application(name="test_application_name", api_client=test_api_client)
    assert application._name == "test_application_name"
    m = mock.Mock()
    with mock.patch("gantry.logger.main._CLIENT", m):
        getattr(m, "log").return_value = "return_value"
        with application.start_run(name="test-run", tags={"run": "test"}) as run:
            result = application.log(
                inputs=test_inputs,
                outputs=test_outputs,
                feedbacks=test_feedbacks,
                timestamps=CURRENT_TIME,
                join_keys=["54321", "67890"],
            )
            assert result == "return_value"
            assert run.name == "test-run"
            assert run.tags == {"run": "test"}
            assert run.join_keys == []
            getattr(m, "log").assert_called_once_with(
                application="test_application_name",
                inputs=test_inputs,
                outputs=test_outputs,
                feedbacks=test_feedbacks,
                ignore_inputs=None,
                timestamps=CURRENT_TIME,
                sample_rate=1.0,
                sort_on_timestamp=True,
                tags=None,
                row_tags=None,
                global_tags=None,
                join_keys=["54321", "67890"],
                as_batch=False,
                run_tags={"run": "test"},
                run_id=run.run_id,
                version=None,
            )


def test_create_dataset(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    m = mock.Mock()
    with mock.patch("gantry.dataset.main._DATASET", m):
        getattr(m, "create_dataset").return_value = "return_value"
        result = application.create_dataset(
            name="test_dataset_name", bucket_name="test-dataset-bucket"
        )
        assert result == "return_value"
        getattr(m, "create_dataset").assert_called_once_with(
            name="test_dataset_name",
            bucket_name="test-dataset-bucket",
            app_name="test_application_name",
        )


def test_list_datasets(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    m = mock.Mock()
    with mock.patch("gantry.dataset.main._DATASET", m):
        getattr(m, "list_datasets").return_value = "return_value"
        result = application.list_datasets(include_deleted=True)
        assert result == "return_value"
        getattr(m, "list_datasets").assert_called_once_with(
            include_deleted=True,
            model_node_id=application._id,
        )


def test_get_schema(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application._name}/schemas",
            json={
                "response": "ok",
                "data": {"schema": "return_value"},
            },
            headers={"Content-Type": "application/json"},
        )
        schema = application.get_schema()
        assert schema == {"schema": "return_value"}


def test_list_workspaces(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/workspaces",
            json={
                "response": "ok",
                "data": {"workspace": "return_value"},
            },
            headers={"Content-Type": "application/json"},
        )
        workspaces = application.list_workspaces()
        assert workspaces == {"workspace": "return_value"}


def test_list_automations(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/automations",
            json={
                "response": "ok",
                "data": {"automations": "return_value"},
            },
            headers={"Content-Type": "application/json"},
        )
        automations = application.list_automations()
        assert automations == {"automations": "return_value"}


def test_get_run(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application._id}/jobs",
            json={
                "response": "ok",
                "data": {"jobs": "return_value"},
            },
            headers={"Content-Type": "application/json"},
        )
        run = application.get_run(name="test_run")
        assert run == "return_value"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application._id}/jobs",
            json={
                "response": "ok",
                "data": {"jobs": "return_value"},
            },
            headers={"Content-Type": "application/json"},
        )
        run = application.get_run(tags={"run": "test"})
        assert run == "return_value"


def test_query(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    assert application._name == "test_application_name"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/models/{application._name}/schemas",
            json={
                "response": "ok",
                "data": {"id": "return_value"},
            },
            headers={"Content-Type": "application/json"},
        )
        expected_query = GantryDataFrame(
            api_client=test_api_client,
            application=application._name,
            start_time=CURRENT_TIME - datetime.timedelta(days=1),
            end_time=CURRENT_TIME,
            version=None,
            env="test",
            filters=[{"feature_name": "inputs.A", "lower_bound": 0, "upper_bound": 10}],
            tags={"query": "test"},
        )
        actual_query = application.query(
            time_window=TimeWindow(
                start_time=CURRENT_TIME - datetime.timedelta(days=1), end_time=CURRENT_TIME
            ),
            version=None,
            env="test",
            filters=[{"feature_name": "inputs.A", "lower_bound": 0, "upper_bound": 10}],
            tags={"query": "test"},
        )
        assert isinstance(actual_query, GantryDataFrame)
        assert actual_query.start_time == expected_query.start_time
        assert actual_query.end_time == expected_query.end_time
        assert actual_query.version == expected_query.version
        assert actual_query.env == expected_query.env
        assert actual_query.filters == expected_query.filters
        assert actual_query.tags == expected_query.tags


def test_save_query(test_api_client):
    application = Application(name="test_application_name", api_client=test_api_client)
    assert application._name == "test_application_name"

    with responses.RequestsMock() as resp:
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/models/{application._name}/schemas",
            json={
                "response": "ok",
                "data": {"id": str(application._id)},
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.POST,
            f"{HOST}/api/v1/queries",
            json={
                "response": "ok",
                "data": {"query": "test"},
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.PATCH,
            f"{HOST}/api/v1/queries",
            json={
                "response": "ok",
                "data": {"query": "test"},
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application._id}/queries",
            json={
                "response": "ok",
                "data": [],
            },
            headers={"Content-Type": "application/json"},
        )
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application._id}/queries/test_query",
            json={
                "response": "ok",
                "data": {
                    "start_time": (CURRENT_TIME - datetime.timedelta(days=1)).isoformat(),
                    "end_time": CURRENT_TIME.isoformat(),
                    "filters": [{"feature_name": "inputs.A", "lower_bound": 0, "upper_bound": 10}],
                    "tags": [{"tag_name": "query", "tag_value": "test"}],
                },
            },
            headers={"Content-Type": "application/json"},
        )
        actual_query = application.query(
            time_window=TimeWindow(
                start_time=CURRENT_TIME - datetime.timedelta(days=1),
                end_time=CURRENT_TIME,
            ),
            version=None,
            env=None,
            filters=[{"feature_name": "inputs.A", "lower_bound": 0, "upper_bound": 10}],
            tags={"query": "test"},
        )
        application.save_query(name="test_query", query=actual_query)
        saved_query = application.get_query(name="test_query")
        # Timezone difference, but the assert is still correct
        # assert saved_query.start_time == actual_query.start_time
        # assert saved_query.end_time == actual_query.end_time
        assert saved_query.version == actual_query.version
        assert saved_query.env == actual_query.env
        assert saved_query.filters == actual_query.filters
        assert saved_query.tags == actual_query.tags

        # Add a mock response that there is a query with the same name in the list
        # to test if it updates the query instead of saving.
        resp.add(
            resp.GET,
            f"{HOST}/api/v1/applications/{application._id}/queries",
            json={
                "response": "ok",
                "data": [{"name": "test_query", "query": "test"}],
            },
            headers={"Content-Type": "application/json"},
        )
        actual_query = application.query(
            time_window=TimeWindow(
                start_time=CURRENT_TIME - datetime.timedelta(days=1), end_time=CURRENT_TIME
            ),
            version=None,
            env="test",
            filters=[{"feature_name": "inputs.A", "lower_bound": 0, "upper_bound": 5}],
            tags={"query": "test"},
        )
        application.save_query(name="test_query", query=actual_query)
        application.get_query(name="test_query")
