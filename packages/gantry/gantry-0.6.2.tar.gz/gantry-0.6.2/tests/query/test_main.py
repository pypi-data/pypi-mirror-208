import mock
import pytest

from gantry.query import main
from gantry.query.client import GantryQuery


@pytest.mark.parametrize("backend", ["", "/some/file", "tcp://other/protocol"])
def test_global_init_error(backend):
    with mock.patch.dict("os.environ", {"GANTRY_LOGS_LOCATION": backend}):
        with pytest.raises(ValueError):
            main.init()


@pytest.mark.parametrize("valid_backend", ["https://app.gantry.io", "http://app.gantry.io"])
def test_global_init_valid_logs_location(valid_backend):
    with mock.patch.dict("os.environ", {"GANTRY_LOGS_LOCATION": valid_backend}):
        main.init(api_key="ABCD1234")


def test_no_api_key_provided():
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": ""}):
        with pytest.raises(ValueError):
            main.init(api_key=None)


@mock.patch("gantry.query.main.globals")
def test_passed_api_key_overrides_env(mock_globals):
    passed_api_key = "some_key"
    env_api_key = "some_other_key"
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": env_api_key}):
        main.init(passed_api_key)
        assert mock_globals._Query._api_client._api_key == passed_api_key
        assert mock_globals._Query._api_client._api_key != env_api_key


@mock.patch("gantry.query.main.globals")
def test_global_init_default(mock_globals):
    passed_api_key = "some_key"
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": passed_api_key}):
        main.init()  # api_key is required as param or env var
        assert mock_globals._Query._api_client._host == "https://app.gantry.io"
        assert mock_globals._Query._api_client._api_key == passed_api_key


@mock.patch("gantry.query.main.globals")
def test_global_init(mock_globals):
    main.init(api_key="ABCD1234")
    assert mock_globals._Query._api_client._host == "https://app.gantry.io"
    assert mock_globals._Query._api_client._api_key == "ABCD1234"


@pytest.mark.parametrize(
    ["method", "params"],
    [
        ("list_application_environments", {"application": "foobar"}),
        ("list_application_versions", {"application": "foobar"}),
        (
            "list_application_views",
            {"application": "foobar", "version": "1.2.3", "environment": "dev"},
        ),
        (
            "list_application_batches",
            {"application": "foobar", "version": "1.2.3"},
        ),
        ("list_applications", {}),
        ("print_application_info", {"application": "foobar"}),
        (
            "query",
            {
                "application": "foobar",
                "start_time": "2020",
                "end_time": "2020",
                "version": "1.2.3",
                "environment": "dev",
                "filters": [],
                "view": "foo",
                "tags": {"foo": "bar"},
                "batch_id": "barbaz",
            },
        ),
        (
            "create_view",
            {
                "name": "barbaz",
                "application": "foobar",
                "version": "1.2.3",
                "start_time": "2020",
                "end_time": "2020",
                "duration": "1D",
                "data_filters": [],
                "tag_filters": {"foo": "bar"},
            },
        ),
    ],
)
@mock.patch("gantry.query.main.validate_init")
@mock.patch("gantry.query.main.globals._Query", spec=GantryQuery)
def test_query_methods(mock_query, mock_validate_init, method, params):
    getattr(mock_query, method).return_value = "foo"
    assert getattr(main, method)(**params) == "foo"
    mock_validate_init.assert_called_once()
    getattr(mock_query, method).assert_called_once_with(**params)
