import datetime
from abc import ABC
from typing import Dict, List, Optional

from gantry.alerts import create_alert
from gantry.alerts.client import AlertsAggregation, AlertsCheck
from gantry.query.time_window import RelativeTimeWindow
from gantry.utils import from_isoformat_duration, to_datetime, to_isoformat_duration


class Trigger(ABC):
    def __init__(self):
        self._application_name = None

    def add_to_application(self, application_name: str):
        self._application_name = application_name

    def remove_from_application(self):
        self._application_name = None

    def to_dict(self):
        pass


class IntervalTrigger(Trigger):
    def __init__(
        self,
        start_on: datetime.datetime,
        interval: datetime.timedelta,
        delay: datetime.timedelta = datetime.timedelta(),
    ):
        super().__init__()
        self.start_on = start_on
        self.interval = interval
        self.delay = delay or datetime.timedelta()

    def is_triggered(self):
        raise NotImplementedError

    def to_dict(self) -> Dict:
        return {
            "type": "IntervalTrigger",
            "content": {
                "start_on": self.start_on.isoformat(),
                "interval": to_isoformat_duration(self.interval),
                "delay": to_isoformat_duration(self.delay),
            },
        }

    @classmethod
    def from_dict(cls, d) -> "IntervalTrigger":
        return cls(
            start_on=to_datetime(d["start_on"]),
            interval=from_isoformat_duration(d["interval"]),
            delay=from_isoformat_duration(d["delay"]),
        )


class AggregationTrigger(Trigger):
    def __init__(
        self,
        name: str,
        aggregation: AlertsAggregation,
        fields: List[str],
        lower_bound: float,
        upper_bound: float,
        evaluation_window: RelativeTimeWindow,
        tags: Optional[Dict] = None,
    ):
        super().__init__()
        self.name = name
        self.aggregation = aggregation
        self.fields = fields
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.evaluation_window = evaluation_window.window_length
        self.delay = evaluation_window.offset
        self.tags = tags

    def generate_alert(self) -> str:
        alert_check = AlertsCheck(
            self.aggregation, self.fields, self.lower_bound, self.upper_bound, "range_check"
        )
        evaluation_window = to_isoformat_duration(self.evaluation_window)
        delay = to_isoformat_duration(datetime.timedelta())
        if self.delay:
            delay = to_isoformat_duration(self.delay)
        alert_id = create_alert(
            self._application_name,
            self.name,
            [alert_check],
            evaluation_window,
            delay,
            self.tags,
        )
        return alert_id

    def to_dict(self) -> Dict:
        return {
            "type": "AggregationTrigger",
            "content": {
                "name": self.name,
                "aggregation": self.aggregation,
                "fields": self.fields,
                "lower_bound": self.lower_bound,
                "upper_bound": self.upper_bound,
                "evaluation_window": to_isoformat_duration(self.evaluation_window),
                "delay": to_isoformat_duration(self.delay)
                if self.delay
                else to_isoformat_duration(datetime.timedelta()),
                "tags": self.tags,
            },
        }

    @classmethod
    def from_dict(cls, d) -> "AggregationTrigger":
        return cls(
            d["name"],
            d["aggregation"],
            d["fields"],
            d["lower_bound"],
            d["upper_bound"],
            RelativeTimeWindow(
                window_length=from_isoformat_duration(d["evaluation_window"]),
                offset=from_isoformat_duration(d["delay"]),
            ),
            d["tags"],
        )
