import logging
from abc import ABC
from typing import Optional

from gantry.alerts import (
    create_slack_notification,
    delete_alert,
    delete_slack_notification,
)

logger = logging.getLogger(__name__)


class Action(ABC):
    pass


class SendSlackMessage(Action):
    def __init__(
        self,
        name: str,
        webhook_url: str,
        id: Optional[str] = None,
        notify_daily: bool = False,
        alert_id: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.webhook_url = webhook_url
        self.notify_daily = notify_daily
        self.alert_id = alert_id

    def update_trigger(self, alert_id: str):
        self.alert_id = alert_id

    def start(self):
        logger.info("Start sending slack notification upon triggered.")

        self.id = create_slack_notification(
            self.alert_id,
            self.name,
            self.webhook_url,
            notify_daily=self.notify_daily,
        )
        logger.info("Slack ID: " + self.id)

    def to_dict(self):
        return {
            "type": "SendSlackMessage",
            "content": {
                "id": self.id,
                "name": self.name,
                "webhook_url": self.webhook_url,
                "alert_id": self.alert_id,
                "notify_daily": self.notify_daily,
            },
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"],
            name=d["name"],
            webhook_url=d["webhook_url"],
            notify_daily=d["notify_daily"],
            alert_id=d["alert_id"],
        )

    def stop(self):
        """
        Delete the ongoing slack notification and alert.
        """
        delete_slack_notification(slack_notification_id=self.id, alert_id=self.alert_id)
        delete_alert(self.alert_id)
