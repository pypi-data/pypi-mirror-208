from unittest.mock import patch

import pytest
import responses

from gantry.alerts.client import AlertsAggregation, AlertsCheck, GantryAlerts
from gantry.api_client import APIClient
from gantry.exceptions import GantryException

from .conftest import ORIGIN


@pytest.fixture
def gantry_alerts_obj():
    api_client = APIClient(origin=ORIGIN, api_key="abcd1234")
    return GantryAlerts(api_client)


@pytest.mark.parametrize(
    ["data", "application_name", "expected"],
    [
        (
            {"data": {"id": "02d7c315-9083-476d-8fe6-4d41db6045b8"}, "response": "ok"},
            "test_app",
            {"id": "02d7c315-9083-476d-8fe6-4d41db6045b8"},
        )
    ],
)
def test_get_application(data, application_name, expected, gantry_alerts_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/models/{}/schemas".format(ORIGIN, application_name),
            json=data,
        )
        assert gantry_alerts_obj._get_application(application_name) == expected


@pytest.mark.parametrize(
    ["data", "application_name", "expected"],
    [
        (
            {"error": "Model not found", "response": "error"},
            "dne",
            None,
        ),
    ],
)
def test_get_application_for_nonexistent_app(data, application_name, expected, gantry_alerts_obj):
    with pytest.raises(GantryException):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "{}/api/v1/models/{}/schemas".format(
                    ORIGIN, application_name
                ),  # we mock the error response
                json=data,
                status=404,
            )
            assert gantry_alerts_obj._get_application(application_name) == expected


@patch(
    "gantry.alerts.client.GantryAlerts._get_application",
    return_value={
        "feedback_datanodes": [{"name": "one", "id": "5393dc5f-1304-4fc8-a06a-bba6f6483c1a"}],
        "prediction_datanodes": [{"name": "two", "id": "7382bc29-3ab1-4bc8-ac28-cd2a49886bdc"}],
        "projection_datanodes": [{"name": "three", "id": "7d4647fc-a447-4dfa-bf19-99e080404029"}],
    },
)
def test_map_column_names_to_ids(mock_req, gantry_alerts_obj):
    expected = {
        "one": "5393dc5f-1304-4fc8-a06a-bba6f6483c1a",
        "two": "7382bc29-3ab1-4bc8-ac28-cd2a49886bdc",
        "three": "7d4647fc-a447-4dfa-bf19-99e080404029",
    }
    actual = gantry_alerts_obj._map_column_names_to_ids("test app", ["one", "two", "three"])
    assert actual == expected


@patch(
    "gantry.alerts.client.GantryAlerts._get_application",
    return_value={},
)
def test_map_column_names_throws_when_node_not_found(mock_req, gantry_alerts_obj):
    with pytest.raises(ValueError):
        gantry_alerts_obj._map_column_names_to_ids("test app", ["one"])


@pytest.mark.parametrize(
    [
        "application_name",
        "triggered",
        "triggered_from",
        "triggered_to",
        "mock_resp_data",
    ],
    [
        (
            "test_app",
            False,
            None,
            None,
            [{"alert_id": "02342a0d-4bce-40e0-a8bd-82e5892ca2ea"}],
        )
    ],
)
def test_get_alerts(
    application_name,
    triggered,
    triggered_from,
    triggered_to,
    mock_resp_data,
    gantry_alerts_obj,
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/alerts".format(ORIGIN),
            json={"data": {"alerts": mock_resp_data}, "response": "ok"},
        )
        assert (
            gantry_alerts_obj.get_alerts(
                application_name=application_name,
                triggered=triggered,
                triggered_from=triggered_from,
                triggered_to=triggered_to,
            )
            == mock_resp_data
        )


@pytest.mark.parametrize(
    ["application_name", "triggered", "triggered_from", "triggered_to", "mock_resp_data"],
    [
        (
            "test_app",
            True,
            "1970-01-01T00:00:00",
            "2022-10-03T14:21:14.454125",
            [{"alert_id": "02342a0d-4bce-40e0-a8bd-82e5892ca2ea"}],
        ),
        (
            "test_app",
            True,
            None,
            None,
            [{"alert_id": "02342a0d-4bce-40e0-a8bd-82e5892ca2ea"}],
        ),
    ],
)
def test_get_triggered_alerts(
    application_name, triggered, triggered_from, triggered_to, mock_resp_data, gantry_alerts_obj
):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "{}/api/v1/alerts/triggered/all".format(ORIGIN),
            json={"data": {"triggered_alerts": mock_resp_data}, "response": "ok"},
        )
        assert (
            gantry_alerts_obj.get_alerts(
                application_name=application_name,
                triggered=triggered,
                triggered_from=triggered_from,
                triggered_to=triggered_to,
            )
            == mock_resp_data
        )


@pytest.mark.parametrize(
    ["application_name", "triggered_from", "triggered_to"],
    [
        ("test app", "2022-10-03T14:21:14.454125", None),
        ("test app", None, "2022-10-03T14:21:14.454125"),
    ],
)
def test_get_triggered_alerts_raises_if_not_filtering_and_specifiying_times(
    application_name, triggered_from, triggered_to, gantry_alerts_obj
):
    with pytest.raises(ValueError):
        gantry_alerts_obj.get_alerts(
            application_name=application_name,
            triggered=False,
            triggered_from=triggered_from,
            triggered_to=triggered_to,
        )


@patch(
    "gantry.api_client.APIClient.request",
    return_value={
        "data": {"alert": {"id": "3ca87947-5d26-41a9-9e9f-c07050188c6d"}},
        "response": "ok",
    },
)
@patch(
    "gantry.alerts.client.GantryAlerts._get_application",
    return_value={"id": "5bc22499-cb09-4984-a450-cf16c4a05c5f"},
)
@patch(
    "gantry.alerts.client.GantryAlerts._map_column_names_to_ids",
    return_value={"some.feature": "db144056-ec59-44ca-9ed5-4e8b162a4fbc"},
)
def test_create_alert(mock_map, mock_get_app, mock_req, gantry_alerts_obj):
    application_name = "test app"
    alert_name = "test alert"

    alert_checks = [
        AlertsCheck(
            **{
                "aggregation": AlertsAggregation.MAX,
                "column_names": ["some.feature"],
                "lower_bound": 1000,
                "upper_bound": 1001,
            }
        )
    ]
    evaluation_window = "PT1H5M26S"
    evaluation_delay = "PT1H5M26S"
    tags = {"env": "dev"}
    gantry_alerts_obj.create_alert(
        application_name=application_name,
        alert_name=alert_name,
        alert_checks=alert_checks,
        evaluation_window=evaluation_window,
        evaluation_delay=evaluation_delay,
        tags=tags,
    )
    mock_get_app.assert_called_once()
    mock_req.assert_called_with(
        "POST",
        "/api/v1/alerts",
        json={
            "alert_type": GantryAlerts.ALERT_TYPE,
            "alert_name": alert_name,
            "model_node_id": "5bc22499-cb09-4984-a450-cf16c4a05c5f",
            "relative_time": evaluation_window,
            "delay_time": evaluation_delay,
            "checks": [
                {
                    "aggregation": "maximum",
                    "lower_bound": 1000,
                    "upper_bound": 1001,
                    "check_type": "range_check",
                    "data_node_ids": ["db144056-ec59-44ca-9ed5-4e8b162a4fbc"],
                }
            ],
            "tags": tags,
        },
        raise_for_status=True,
    )


@patch(
    "gantry.api_client.APIClient.request",
    return_value={
        "data": {"alert": {"id": "3ca87947-5d26-41a9-9e9f-c07050188c6d"}},
        "response": "ok",
    },
)
@patch(
    "gantry.alerts.client.GantryAlerts._get_application",
    return_value={"id": "5bc22499-cb09-4984-a450-cf16c4a05c5f"},
)
@patch(
    "gantry.alerts.client.GantryAlerts._map_column_names_to_ids",
    return_value={"some.feature": "db144056-ec59-44ca-9ed5-4e8b162a4fbc"},
)
def test_update_alert(mock_map, mock_get_app, mock_req, gantry_alerts_obj):
    alert_id = "6848c6b3-e8bc-4d65-ba1c-7bace4350cbd"
    application_name = "test app"
    alert_name = "test alert"
    alert_checks = [
        AlertsCheck(
            **{
                "aggregation": AlertsAggregation.MAX,
                "column_names": ["some.feature"],
                "lower_bound": 1000,
                "upper_bound": 1001,
            }
        )
    ]
    evaluation_window = "PT1H5M26S"
    evaluation_delay = "PT1H5M26S"
    tags = {"env": "dev"}
    gantry_alerts_obj.update_alert(
        application_name=application_name,
        alert_id=alert_id,
        alert_name=alert_name,
        alert_checks=alert_checks,
        evaluation_window=evaluation_window,
        evaluation_delay=evaluation_delay,
        tags=tags,
    )
    mock_get_app.assert_called_once()
    mock_req.assert_called_with(
        "POST",
        "/api/v1/alerts",
        json={
            "alert_type": GantryAlerts.ALERT_TYPE,
            "alert_name": alert_name,
            "model_node_id": "5bc22499-cb09-4984-a450-cf16c4a05c5f",
            "alert_id": alert_id,
            "relative_time": evaluation_window,
            "delay_time": evaluation_delay,
            "checks": [
                {
                    "aggregation": "maximum",
                    "data_node_ids": ["db144056-ec59-44ca-9ed5-4e8b162a4fbc"],
                    "lower_bound": 1000,
                    "upper_bound": 1001,
                    "check_type": "range_check",
                }
            ],
            "tags": tags,
        },
        raise_for_status=True,
    )


@pytest.mark.parametrize(
    ["notify_daily", "daily_notification_time"],
    [
        (
            True,
            None,
        ),
        (True, "12:00:00"),
        (False, None),
    ],
)
@patch(
    "gantry.api_client.APIClient.request",
    return_value={
        "data": {"channel": {"id": "646e7bf1-fe23-4972-a5bf-896fd8f340c5"}},
        "response": "ok",
    },
)
def test_create_slack_notification(
    mock_req, notify_daily, daily_notification_time, gantry_alerts_obj
):
    gantry_alerts_obj.create_slack_notification(
        alert_id="6848c6b3-e8bc-4d65-ba1c-7bace4350cbd",
        notification_name="test notification",
        slack_webhook_url="test hook",
        notify_daily=notify_daily,
        daily_notification_time=daily_notification_time,
    )
    if daily_notification_time is not None:
        mock_req.assert_called_with(
            "POST",
            "/api/v1/alerts/notifications",
            json={
                "channel_type": GantryAlerts.CHANNEL_TYPE,
                "channel_name": "test notification",
                "webhook_url": "test hook",
                "alert_id": "6848c6b3-e8bc-4d65-ba1c-7bace4350cbd",
                "frequency": "DAILY" if notify_daily else "IMMEDIATELY",
                "frequency_relative_time": daily_notification_time,
            },
            raise_for_status=True,
        )
    else:
        mock_req.assert_called_with(
            "POST",
            "/api/v1/alerts/notifications",
            json={
                "channel_type": GantryAlerts.CHANNEL_TYPE,
                "channel_name": "test notification",
                "webhook_url": "test hook",
                "alert_id": "6848c6b3-e8bc-4d65-ba1c-7bace4350cbd",
                "frequency": "DAILY" if notify_daily else "IMMEDIATELY",
            },
            raise_for_status=True,
        )


@pytest.mark.parametrize(
    "mock_resp_data",
    [[{"id": "2d37db9b-fc01-41e2-9f20-4f31e74d78f3"}]],
)
def test_get_slack_notifications(mock_resp_data, gantry_alerts_obj):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "{}/api/v1/alerts/channels".format(ORIGIN),
            json={"data": {"channels": mock_resp_data}, "response": "ok"},
        )
        assert gantry_alerts_obj.get_slack_notifications() == mock_resp_data


@patch("gantry.api_client.APIClient.request", return_value={"response": "ok"})
def test_delete_alert(mock_req, gantry_alerts_obj):
    gantry_alerts_obj.delete_alert(alert_id="6848c6b3-e8bc-4d65-ba1c-7bace4350cbd")
    mock_req.assert_called_with(
        "DELETE", "/api/v1/alerts/6848c6b3-e8bc-4d65-ba1c-7bace4350cbd", raise_for_status=True
    )


@patch("gantry.api_client.APIClient.request", return_value={"response": "ok"})
def test_delete_slack_notification(mock_req, gantry_alerts_obj):
    gantry_alerts_obj.delete_slack_notification(
        alert_id="6848c6b3-e8bc-4d65-ba1c-7bace4350cbd",
        slack_notification_id="02342a0d-4bce-40e0-a8bd-82e5892ca2ea",
    )
    mock_req.assert_called_with(
        "DELETE",
        "/api/v1/alerts/channels",
        json={
            "alert_id": "6848c6b3-e8bc-4d65-ba1c-7bace4350cbd",
            "channel_id": "02342a0d-4bce-40e0-a8bd-82e5892ca2ea",
        },
        raise_for_status=True,
    )
