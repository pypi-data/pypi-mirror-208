import dataclasses
import itertools
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from gantry.api_client import APIClient
from gantry.exceptions import GantryException

logger = logging.getLogger(__name__)


class SlackNotificationFrequency(Enum):
    DAILY = "DAILY"
    IMMEDIATELY = "IMMEDIATELY"


class AlertsAggregation(str, Enum):
    """
    Allowed aggregations for Gantry Alerts.

    The full list of aggregations are:

    .. code-block:: python

        TOTAL
        MAX
        MIN
        MEAN
        STD
        PDF
        QUANTILES
        PERCENT_NULL
        PERCENT_TRUE
        PERCENT_FALSE
        CATEGORY_PERCENTS
        ACCURACY
        MAE
        MSE
        MAPE
        MAX_ERROR
        CONFUSION_MATRIX
        F1
        R2
        PRECISION
        RECALL
        ROC_AUC_SCORE
        PR_AUC_SCORE
        D1
        DINF
        KL
        KS
        CATEGORICAL_D1
        CATEGORICAL_DINF
        CATEGORICAL_KL
        X2
        ROC_CURVE_PLOT
        PR_CURVE_PLOT
        DISTRIBUTION_SKETCH
        CATEGORICAL_SKETCH

    """

    # Standard Aggregation
    TOTAL = "total"
    MAX = "maximum"
    MIN = "minimum"
    MEAN = "mean"
    STD = "stddev"
    PDF = "pdf"
    QUANTILES = "quantiles"
    PERCENT_NULL = "percent_null"
    PERCENT_TRUE = "percent_true"
    PERCENT_FALSE = "percent_false"
    CATEGORY_PERCENTS = "category_percents"
    # Metric Aggregations
    ACCURACY = "accuracy_score"
    MAE = "mean_absolute_error"
    MSE = "mean_squared_error"
    MAPE = "mean_absolute_percentage_error"
    MAX_ERROR = "maximum_error"
    CONFUSION_MATRIX = "confusion_matrix"
    F1 = "f1_score"
    R2 = "r2_score"
    PRECISION = "precision_score"
    RECALL = "recall_score"
    ROC_AUC_SCORE = "roc_auc_score"
    PR_AUC_SCORE = "precision_recall_auc_score"
    D1 = "d1"
    DINF = "dinf"
    KL = "kl"
    KS = "ks"
    CATEGORICAL_D1 = "categorical_d1"
    CATEGORICAL_DINF = "categorical_dinf"
    CATEGORICAL_KL = "categorical_kl"
    X2 = "x2"
    # Plots
    ROC_CURVE_PLOT = "roc_curve_plot"
    PR_CURVE_PLOT = "pr_curve_plot"
    # Sketch Aggregations.
    DISTRIBUTION_SKETCH = "distribution_sketch"
    CATEGORICAL_SKETCH = "categorical_sketch"


@dataclass
class AlertsCheck:
    """
    Data shape definition for alert checks.

    column_names correspond to the schema columns in your application.
    """

    aggregation: AlertsAggregation
    column_names: List[str]
    lower_bound: float
    upper_bound: float
    check_type: str = "range_check"


class GantryAlerts:

    ALERT_TYPE = "RangeAlert"  # only one supported
    CHANNEL_TYPE = "SLACK_WEBHOOK"  # only one supported

    def __init__(self, api_client: APIClient):
        self._api_client = api_client

    @classmethod
    def from_api_key(cls, api_url, api_key):
        return cls(api_client=APIClient(origin=api_url, api_key=api_key))

    def _get_application(self, application_name: str) -> Dict:
        """
        Get all application details for a particular application in Gantry.

        This is useful in case you need the application or column (data node) IDs
        to perform some other interaction with the API for your application.

        Args:
            application_name (str): The name of your existing application in Gantry.

        Returns:
            Dict: All application details in Gantry.
        """
        response = self._api_client.request(
            "GET", f"/api/v1/models/{application_name}/schemas", raise_for_status=True
        )
        return response["data"]

    def _map_column_names_to_ids(
        self, application_name: str, column_names: List[str]
    ) -> Dict[str, str]:
        """
        Returns a map of column_name -> data_node_id.

        Args:
            application_name (str): Application in Gantry.
            column_names (List[str]): Data node names that map to the schema of the application.

        Returns:
            Dict[str, str]: Map from column_name to data_node_id
        """
        application_data = self._get_application(application_name)

        feedback_data_nodes = application_data.get("feedback_datanodes", [])
        prediction_data_nodes = application_data.get("prediction_datanodes", [])
        projection_data_nodes = application_data.get("projection_datanodes", [])

        name_to_id = {}
        for column_name in column_names:
            found = False
            for data_node in itertools.chain(
                feedback_data_nodes, prediction_data_nodes, projection_data_nodes
            ):
                if data_node["name"] == column_name:
                    name_to_id[column_name] = data_node["id"]
                    found = True
                    break
            if not found:
                raise ValueError(f"{column_name} not found in application.")

        return name_to_id

    def get_alerts(
        self,
        application_name: str,
        triggered: bool = False,
        triggered_from: Optional[str] = None,
        triggered_to: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get alerts (and their properties) that exist for your application in Gantry. This
        method also allows you to get alerts that have been triggered within a time window.

        NOTE: The data shape of the returned objects differs slightly if you specify the
        `triggered` filter.

        Args:
            application_name (str): The name of your existing application in Gantry.
            triggered (bool): Whether or not to get alerts that have been triggered by
                their check definitions.
            triggered_from (Optional[str]): If provided, will get triggered alerts from
                this time. ISO formatted string. Defaults to the beginning of the UNIX epoch.
            triggered_to (Optional[str]): If provided, will get triggered alerts to this
                time. ISO formatted string. Defaults to now() + 1 day to capture all recent
                alerts.
        Returns:
            List[Dict]: All of the alerts and their properties that exist under the
                application_name (optionally, that are `triggered`)
        """
        if not triggered:
            if triggered_from or triggered_to:
                raise ValueError(
                    "Triggered time window is only valid when requesting triggered alerts."
                )
            query_params = {"model_name": application_name}
            response = self._api_client.request(
                "GET", "/api/v1/alerts", params=query_params, raise_for_status=True
            )
            return response["data"]["alerts"]
        else:
            triggered_from = triggered_from or datetime.utcfromtimestamp(0).isoformat()
            # Have noticed that for just triggered alerts, there can be a lag, so by default
            # we can pad the window.
            triggered_to = triggered_to or (datetime.now() + timedelta(days=1)).isoformat()
            json_data = {
                "start_time": triggered_from,
                "end_time": triggered_to,
                "statuses": ["OPEN"],  # options are 'OPEN' or 'CLOSED'
            }
            response = self._api_client.request(
                "POST", "/api/v1/alerts/triggered/all", json=json_data, raise_for_status=True
            )
            return response["data"]["triggered_alerts"]

    def _create_or_update_alert(
        self,
        application_name: str,
        alert_name: str,
        alert_checks: List[AlertsCheck],
        evaluation_window: str,
        evaluation_delay: str,
        tags: Optional[Dict[str, str]] = None,
        alert_id: Optional[Union[str, UUID]] = None,
    ) -> str:
        """
        Create or update (upsert) an alert in the Gantry application.

        Example check:

        .. code-block:: python

            from gantry.alerts import AlertsCheck

            check = AlertsCheck(
                aggregation=AlertsAggregation.MAX,
                data_node_names=[
                    "inputs.field",
                ],
                lower_bound=10,
                upper_bound=20,
            )

        Args:
            application_name (str): The name of your existing application in Gantry.
            alert_name (str): Whatever you would like to call your (existing) alert!
            alert_checks (List[Dict]): A list of metric checks that define this alert.
                See example.
            evaluation_window (str): Determines the time window of data to compute the alert
                metric on and is an ISO 8601 formatted duration such
                as "PT1H5M26S".
            evaluation_delay (str): Determines how long the system will wait for data to come
                in before evaluating a window and is an ISO 8601 formatted duration such as
                "PT1H5M26S".
            tags (Optional[Dict[str, str]]): Tags for this alert such as {"env": "dev"}.
            alert_id (Union[str, UUID]): If an update is desired, provide the alert UUID here.

        Returns:
            str: The affected alert ID
        """
        if tags is None:
            tags = {}
        try:
            application_id = self._get_application(application_name)["id"]
        except GantryException as ge:
            raise ValueError(
                f'Could not find "{application_name}". Reason: "{ge}". Check the spelling?'
            )
        _alert_checks = []
        for check in alert_checks:
            check_as_dict = dataclasses.asdict(check)
            check_as_dict["aggregation"] = check_as_dict["aggregation"].value
            check_as_dict["data_node_ids"] = [
                data_node_id
                for __, data_node_id in self._map_column_names_to_ids(
                    application_name, check_as_dict["column_names"]
                ).items()
            ]
            check_as_dict.pop("column_names")
            _alert_checks.append(check_as_dict)
        json_data = {
            "alert_type": GantryAlerts.ALERT_TYPE,
            "alert_name": alert_name,
            "model_node_id": application_id,
            "relative_time": evaluation_window,
            "delay_time": evaluation_delay,
            "checks": _alert_checks,
            "tags": tags,
        }
        if alert_id is not None:
            # This will update instead of create on the backend. Names can be re-used
            # across alert ids so we can't disambiguate one-to-one without it.
            json_data["alert_id"] = alert_id

        response = self._api_client.request(
            "POST", "/api/v1/alerts", json=json_data, raise_for_status=True
        )
        return response["data"]["alert"]["id"]

    def create_alert(
        self,
        application_name: str,
        alert_name: str,
        alert_checks: List[AlertsCheck],
        evaluation_window: str,
        evaluation_delay: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create an alert in your Gantry application.

        NOTE: Alerts will only trigger for data whose tags match the alert tags here,
        if applicable.

        All alerts require check definitions that define what metrics trigger
        the alert. An example check is:

        .. code-block:: python

            from gantry.alerts import AlertsCheck

            check = AlertsCheck(
                aggregation=AlertsAggregation.MAX,
                data_node_names=[
                    "inputs.field",
                ],
                lower_bound=10,
                upper_bound=20,
            )

        Args:
            application_name (str): The name of your existing application in Gantry.
            alert_name (str): Whatever you would like to call your alert!
            alert_checks (List[AlertsCheck]): A list of metric checks that define this alert.
                See example.
            evaluation_window (str): Determines the time window of data to compute the alert
                metric on and is an ISO 8601 formatted duration such
                as "PT1H5M26S".
            evaluation_delay (str): Determines how long the system will wait for data to come
                in before evaluating a window and is an ISO 8601 formatted duration such as
                "PT1H5M26S".
            tags (Optional[Dict[str, str]]): Tags for this alert such as {"env": "dev"}.

        Returns:
            str: The affected alert ID
        """
        return self._create_or_update_alert(
            application_name=application_name,
            alert_name=alert_name,
            alert_checks=alert_checks,
            evaluation_window=evaluation_window,
            evaluation_delay=evaluation_delay,
            tags=tags,
        )

    def update_alert(
        self,
        application_name: str,
        alert_id: Union[str, UUID],
        alert_name: str,
        alert_checks: List[AlertsCheck],
        evaluation_window: str,
        evaluation_delay: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Update an alert in your Gantry application.

        NOTE: This method will OVERWRITE your existing alert checks.

        All alerts require check definitions that define what metrics trigger
        the alert. An example check is:

        .. code-block:: python

            from gantry.alerts import AlertsCheck

            check = AlertsCheck(
                aggregation=AlertsAggregation.MAX,
                data_node_names=[
                    "inputs.field",
                ],
                lower_bound=10,
                upper_bound=20,
            )

        Args:
            application_name (str): The name of your existing application in Gantry.
            alert_id (Union[str, UUID]): The ID for your alert. (You can use the .get_alerts()
                method to get the IDs of your existing alerts.)
            alert_name (str): Whatever you would like to call your (existing) alert!
            alert_checks (List[AlertCheck]): A list of metric checks that define this alert.
                See example.
            evaluation_window (str): Determines the time window of data to compute the alert
                metric on and is an ISO 8601 formatted duration such
                as "PT1H5M26S".
            evaluation_delay (str): Determines how long the system will wait for data to come
                in before evaluating a window and is an ISO 8601 formatted duration such as
                "PT1H5M26S".
            tags (Optional[Dict[str, str]]): Tags for this alert such as {"env": "dev"}.

        Returns:
            str: The affected alert ID
        """
        return self._create_or_update_alert(
            application_name=application_name,
            alert_id=alert_id,
            alert_name=alert_name,
            alert_checks=alert_checks,
            evaluation_window=evaluation_window,
            evaluation_delay=evaluation_delay,
            tags=tags,
        )

    # To hide the complexity of the backend data model from the user, use
    # separate create / delete methods for Slack notifications (otherwise
    # they will need the channel_id / frequency_id, and editting these notifications
    # did not work for me in the API anyway.
    def create_slack_notification(
        self,
        alert_id: str,
        notification_name: str,
        slack_webhook_url: str,
        notify_daily: bool,
        daily_notification_time: Optional[str] = None,
    ) -> str:
        """
        An alert notification sets up the means by which you will be notified
        in case any of your alert checks trigger. This method will set up a
        Slack notification for you.

        Args:
            alert_id (Union[str, UUID]): The alert to which this Slack notification will trigger on.
            notification_name (str): The name for this notification.
            slack_webhook_url (str): The webhook for the Slack application.
            notify_daily (bool): Whether or not the notification should occur daily at a particular
                time (see arg `daily_notification_time`).
            daily_notification_time (str): The time at which you will be notified daily if
                `notify_daily` is True, e.g. "12:00:00"

        Returns:
            str: The affected Slack notification ID.
        """
        if notify_daily:
            frequency = SlackNotificationFrequency.DAILY.value
        else:
            frequency = SlackNotificationFrequency.IMMEDIATELY.value
        json_data = {
            "channel_type": GantryAlerts.CHANNEL_TYPE,
            "channel_name": notification_name,
            "webhook_url": slack_webhook_url,
            "alert_id": alert_id,
            "frequency": frequency,
        }
        if daily_notification_time is not None:
            json_data["frequency_relative_time"] = daily_notification_time
        response = self._api_client.request(
            "POST", "/api/v1/alerts/notifications", json=json_data, raise_for_status=True
        )
        return response["data"]["channel"]["id"]

    def get_slack_notifications(self) -> List[Dict]:
        """
        Get a list of all of the Slack notification objects in the system.

        Returns:
            List[Dict]: All of your Slack notification objects.
        """
        response = self._api_client.request("GET", "/api/v1/alerts/channels", raise_for_status=True)
        return response["data"]["channels"]

    def delete_alert(self, alert_id: Union[str, UUID]) -> None:
        """
        Deletes a particular alert, specified by `alert_id`.

        Args:
            alert_id (Union[str, UUID]): The alert_id.

        Returns:
            None: This is a side-effect.
        """
        self._api_client.request("DELETE", f"/api/v1/alerts/{alert_id}", raise_for_status=True)

    def delete_slack_notification(
        self, alert_id: Union[str, UUID], slack_notification_id: Union[str, UUID]
    ) -> None:
        """
        Deletes a particular Slack notification, specified by the alert and
        Slack notification IDs.

        Args:
            alert_id (Union[str, UUID]): The alert ID.
            slack_notification_id (Union[str, UUID]): The Slack notification ID.
        """
        json_data = {"alert_id": alert_id, "channel_id": slack_notification_id}
        self._api_client.request(
            "DELETE", "/api/v1/alerts/channels", json=json_data, raise_for_status=True
        )
