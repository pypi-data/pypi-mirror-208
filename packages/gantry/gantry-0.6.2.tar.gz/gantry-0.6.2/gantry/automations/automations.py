import logging
from typing import Optional

from gantry.api_client import APIClient
from gantry.automations import globals
from gantry.automations.actions import Action, SendSlackMessage
from gantry.automations.curators import Curator
from gantry.automations.curators.main import get_curator
from gantry.automations.triggers import AggregationTrigger, IntervalTrigger, Trigger

logger = logging.getLogger(__name__)


class Automation:
    def __init__(
        self,
        name: str,
        trigger: Trigger,
        action: Action,
        api_client: Optional[APIClient] = None,
        application: Optional[str] = None,
    ):
        """
        Automation is the process of automatically executing tasks.
        It consists of 2 main components: Trigger and Action.

        Trigger is the condition that, when met, cause the action to be executed.

        Currently, we are supporting:

        - **IntervalTrigger**: based on time intervals & delays
        - **AggregationTrigger**: same idea of Alert on the UI. It tracks if an aggregation
            is outside of the range for the evaluation window and triggers when conditions are met.
        - **SendSlackMessage** (Action): This action sets up a notification setting that will send
        users a slack notification when executed by the trigger.
        - **Curator** (Action): This action creates a new curator.
        - Note:
            - `AggregationTrigger` can only be paired with `SendSlackMessage`
            - `IntervalTrigger` can only be paired with `Curator`

        To setup and start an automation process, there are a few steps:
        - Define the trigger
            .. code-block:: python

                from gantry.automations.triggers import AggregationTrigger
                from gantry.query.time_window import RelativeTimeWindow

                alert_trigger = AggregationTrigger(
                    name = "alert-trigger",
                    aggregation = "maximum",
                    fields = ["inputs.speed"],
                    lower_bound = 1,
                    upper_bound = 5,
                    evaluation_window=RelativeTimeWindow(
                        window_length=datetime.timedelta(minutes=10)
                    ),
                    tags = None
                )

        - Define the action
            .. code-block:: python

                from gantry.automations.actions import SendSlackMessage
                # Set up action to send slack message to the specified webhook.
                slack_action = SendSlackMessage(
                    name = "demo-slack",
                    webhook_url="SLACK_WEBHOOK_URL"
                )

        - Define the automation and put trigger & action together
            .. code-block:: python

                from gantry.automations.automations import Automation
                # Define automation object and put trigger and action together.
                automation_alert = Automation(
                    name = "alert-automation",
                    trigger=alert_trigger,
                    action=slack_action
                )
        - Add the automation to an application
            .. code-block:: python

                app.add_automation(automation_alert)

        """
        self.name = name
        self.trigger = trigger
        self.action = action
        self.application = application
        self._api_client = globals._API_CLIENT if api_client is None else api_client  # type: ignore

    def add_to_application(self, application_name):
        """
        Add automation to an application.
        This method shouldn't be called directly.
        It will be called once you call `application.add_automation()`.
        """
        self.application = application_name
        self.trigger.add_to_application(application_name)
        logger.info("Automation has been added to application.")
        self.prep()
        self.start()

    def remove_from_application(self):
        """
        Remove automation from an application.
        This method shouldn't be called directly.
        It will be called once you stop the automation process.
        """
        self.application = None
        self.trigger.remove_from_application()
        logger.info("Automation has been removed from application.")

    @classmethod
    def from_dict(cls, data):
        trigger = Trigger()
        if data["trigger"]["type"] == "AggregationTrigger":
            trigger = AggregationTrigger.from_dict(data["trigger"]["content"])
        elif data["trigger"]["type"] == "IntervalTrigger":
            trigger = IntervalTrigger.from_dict(data["trigger"]["content"])

        action = Action()
        if data["action"]["type"] == "SendSlackMessage":
            action = SendSlackMessage.from_dict(data["action"]["content"])
        elif data["action"]["type"] == "curator":
            action = get_curator(data["action"]["content"]["curator_name"])
        return cls(
            name=data["name"],
            application=data["application"],
            trigger=trigger,
            action=action,
        )

    def to_dict(self):
        action_dict = None
        if isinstance(self.action, Curator):
            action_dict = {
                "type": "curator",
                "content": {
                    "curator_name": self.action._name,
                    "curated_dataset": self.action._curated_dataset_name,
                },
            }
        else:
            action_dict = self.action.to_dict()
        return {
            "name": self.name,
            "application_name": self.application,
            "trigger": self.trigger.to_dict(),
            "action": action_dict,
        }

    def prep(self):
        if isinstance(self.trigger, IntervalTrigger) and isinstance(self.action, Curator):
            if self.trigger.start_on:
                self.action.update_curation_start_on(self.trigger.start_on)
            if self.trigger.interval:
                self.action.update_curation_interval(self.trigger.interval)
            if self.trigger.delay:
                self.action.update_curation_delay(self.trigger.delay)
        if isinstance(self.trigger, AggregationTrigger):
            alert_id = self.trigger.generate_alert()
            self.action.update_trigger(alert_id)

    def start(self):
        self.action.start()
        data = self.to_dict()
        self._api_client.request("POST", "/api/v1/automations", json=data, raise_for_status=True)
        logger.info("Automation has started.")

    def stop(self):
        self._api_client.request(
            "DELETE",
            f"/api/v1/automations/{self.name}",
            params={"application_name": self.application},
            raise_for_status=True,
        )
        self.remove_from_application()
        self.action.stop()
        logger.info("Automation has stopped.")
