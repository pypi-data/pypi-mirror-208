import datetime
from typing import Optional, Union


class TimeWindow:
    def __init__(
        self, start_time: Union[str, datetime.datetime], end_time: Union[str, datetime.datetime]
    ):
        self.start_time = start_time
        self.end_time = end_time


class RelativeTimeWindow(TimeWindow):
    def __init__(
        self,
        window_length: datetime.timedelta,
        offset: Optional[datetime.timedelta] = None,
    ):
        self.window_length = window_length
        self.offset = offset
        if self.offset is None:
            self.offset = datetime.timedelta()
        end_time: datetime.datetime = (
            datetime.datetime.utcnow() - self.offset if self.offset else datetime.datetime.utcnow()
        )
        start_time: datetime.datetime = end_time - window_length
        super().__init__(start_time, end_time)
