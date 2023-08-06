import mock
import pytest

from gantry.alerts import main
from gantry.alerts.client import GantryAlerts


@pytest.mark.parametrize("backend", ["", "/some/file", "tcp://other/protocol"])
def test_global_init_error(backend):
    with mock.patch.dict("os.environ", {"GANTRY_LOGS_LOCATION": backend}):
        with pytest.raises(ValueError):
            main._init()


@pytest.mark.parametrize("valid_backend", ["https://app.gantry.io", "http://app.gantry.io"])
def test_global_init_valid_logs_location(valid_backend):
    with mock.patch.dict("os.environ", {"GANTRY_LOGS_LOCATION": valid_backend}):
        main._init(api_key="ABCD1234")


def test_no_api_key_provided():
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": ""}):
        with pytest.raises(ValueError):
            main._init(api_key=None)


@mock.patch("gantry.alerts.main.globals")
def test_passed_api_key_overrides_env(mock_globals):
    passed_api_key = "some_key"
    env_api_key = "some_other_key"
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": env_api_key}):
        main._init(api_key=passed_api_key)
        assert mock_globals._Alerts._api_client._api_key == passed_api_key
        assert mock_globals._Alerts._api_client._api_key != env_api_key


@mock.patch("gantry.alerts.main.globals")
def test_global_init_default(mock_globals):
    passed_api_key = "some_key"
    with mock.patch.dict("os.environ", {"GANTRY_API_KEY": passed_api_key}):
        main._init()  # api_key is required as param or env var
        assert mock_globals._Alerts._api_client._host == "https://app.gantry.io"
        assert mock_globals._Alerts._api_client._api_key == passed_api_key


@mock.patch("gantry.alerts.main.globals")
def test_global_init(mock_globals):
    main._init(api_key="ABCD1234")
    assert mock_globals._Alerts._api_client._host == "https://app.gantry.io"
    assert mock_globals._Alerts._api_client._api_key == "ABCD1234"


@pytest.mark.parametrize(
    ["method", "params"],
    [
        (
            "get_alerts",
            {
                "application_name": "app name",
                "triggered": False,
                "triggered_from": None,
                "triggered_to": None,
            },
        ),
        (
            "get_alerts",
            {
                "application_name": "app name",
                "triggered": True,
                "triggered_from": "1970-01-01T00:00:00",
                "triggered_to": "2022-10-03T14:21:14.454125",
            },
        ),
        (
            "create_alert",
            {
                "application_name": "gantry-demo-logger-14b3910-dev",
                "alert_name": "sdk alert",
                "alert_checks": {
                    "aggregation": "minimum",
                    "data_node_ids": ["fad635d7-13f1-4ceb-ad10-684cf523181b"],
                    "lower_bound": 1000,
                    "upper_bound": 1001,
                },
                "evaluation_window": "PT5M",
                "evaluation_delay": "PT5M",
                "tags": {"env": "dev"},
            },
        ),
        (
            "update_alert",
            {
                "application_name": "gantry-demo-logger-14b3910-dev",
                "alert_id": "13b7ebc2-2cad-4ebe-88df-33a62847d3b9",
                "alert_name": "sdk alert",
                "alert_checks": {
                    "aggregation": "minimum",
                    "data_node_ids": ["fad635d7-13f1-4ceb-ad10-684cf523181b"],
                    "lower_bound": 1000,
                    "upper_bound": 1001,
                },
                "evaluation_window": "PT5M",
                "evaluation_delay": "PT5M",
                "tags": {"env": "dev"},
            },
        ),
        (
            "create_slack_notification",
            {
                "alert_id": "13b7ebc2-2cad-4ebe-88df-33a62847d3b9",
                "notification_name": "Slack notification 1",
                "slack_webhook_url": "hook",
                "notify_daily": True,
                "daily_notification_time": "17:01:00",
            },
        ),
        (
            "create_slack_notification",
            {
                "alert_id": "13b7ebc2-2cad-4ebe-88df-33a62847d3b9",
                "notification_name": "Slack notification 1",
                "slack_webhook_url": "hook",
                "notify_daily": False,
                "daily_notification_time": None,
            },
        ),
        ("get_slack_notifications", {}),
        ("delete_alert", {"alert_id": "13b7ebc2-2cad-4ebe-88df-33a62847d3b9"}),
        (
            "delete_slack_notification",
            {
                "alert_id": "13b7ebc2-2cad-4ebe-88df-33a62847d3b9",
                "slack_notification_id": "a21c4157-7bee-4701-9153-d5d8af2a363b",
            },
        ),
    ],
)
@mock.patch("gantry.alerts.main.validate_init")
@mock.patch("gantry.alerts.main.globals._Alerts", spec=GantryAlerts)
def test_alert_methods(mock_query, mock_validate_init, method, params):
    getattr(mock_query, method).return_value = "foo"
    assert getattr(main, method)(**params) == "foo"
    mock_validate_init.assert_called_once()
    getattr(mock_query, method).assert_called_once_with(**params)
