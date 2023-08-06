import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from gantry.exceptions import GantryBatchCreationException
from gantry.logger.constants import (
    BatchType,
    ScheduleFrequency,
    ScheduleType,
    UploadFileType,
)


@dataclass
class DataLinkElement:
    ref: Optional[int] = None
    val: Optional[Any] = None  # Exact value of the item.

    def __post_init__(self):
        if self.ref is None and self.val is None:
            raise GantryBatchCreationException("ref or val must be populated.")
        return self


@dataclass
class DataLink:
    file_type: UploadFileType
    batch_type: BatchType
    num_events: int
    application: str
    version: Optional[str]
    batch_id: Optional[str] = None
    log_timestamp: Optional[str] = None
    run_name: Optional[str] = None
    run_tags: Optional[Dict] = None
    timestamp: Dict[str, DataLinkElement] = field(default_factory=dict)
    inputs: Dict[str, DataLinkElement] = field(default_factory=dict)
    outputs: Dict[str, DataLinkElement] = field(default_factory=dict)
    feedback: Dict[str, DataLinkElement] = field(default_factory=dict)
    tags: Dict[str, DataLinkElement] = field(default_factory=dict)
    feedback_id: Dict[str, DataLinkElement] = field(default_factory=dict)
    feedback_keys: List[str] = field(default_factory=list)


@dataclass
class ScheduleOptions:
    """
    Dictionary of key and value pairs to specify the additional specifications
    for logger schedule

    delay_time: Number of seconds to delay the scheduled ingestion. Default is 0s.
    watermark_key: Column name to use as the watermark timestamp for INCREMENTAL APPEND
    """

    delay_time: Optional[int] = 0
    watermark_key: Optional[str] = None


@dataclass
class Schedule:
    """
    start_on: (Union[datetime, str]): ISO 8601 formatted string or
        datetime object representing the start time of the scheduled ingestion.
    frequency: (ScheduleFrequency): 1 hour | 2 hours | 4 hours | 8 hours |
        12 hours | 1 day
    type: (ScheduleType): INCREMENTAL_APPEND | FULL_REFRESH_APPEND
    options: (ScheduleOptions): Dictionary of key and value pairs to specify the
        additional specifications for the schedule.

        For instance, schedule_type of INCREMENTAL_APPEND requires a "watermark_key",
        which is the timestamp column name to use as the watermark to divide the
        tumbling window for each incremental append.
    """

    frequency: ScheduleFrequency
    start_on: Optional[Union[datetime.datetime, str]] = None
    type: Optional[ScheduleType] = None
    options: Optional[ScheduleOptions] = None


@dataclass
class IngestFromDataConnectorRequest:
    """
    Request body for creating a new ingestion pipeline from a data connector.
    """

    application: str
    source_data_connector_name: str
    timestamp: Optional[str]
    inputs: Optional[List[str]]
    outputs: Optional[List[str]]
    feedbacks: Optional[List[str]]
    join_key: Optional[str]
    row_tags: Optional[List[str]]
    global_tags: Optional[Dict[str, str]]
    schedule: Optional[Schedule]
    pipeline_name: Optional[str]


@dataclass
class PipelineSourceOptions:
    """
    Pipeline source options for a data connector ingestion pipeline.
    """

    inputs: Optional[List[str]]
    outputs: Optional[List[str]]
    feedbacks: Optional[List[str]]
    join_key: Optional[str]
    timestamp: Optional[str]
    global_tags: Optional[Dict[str, str]]
    row_level_tags: Optional[List[str]]


@dataclass
class IngestFromDataConnectorResponse:
    """
    Response received after creating a new ingestion pipeline from a data connector.
    """

    id: str
    name: str
    source_options: PipelineSourceOptions
    updated_at: str
    created_at: str
