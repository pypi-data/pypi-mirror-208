from enum import Enum


class BatchType(str, Enum):
    RECORD = "RECORD"
    FEEDBACK = "FEEDBACK"
    PREDICTION = "PREDICTION"


class UploadFileType(str, Enum):
    CSV_WITH_HEADERS = "CSV_WITH_HEADERS"
    EVENTS = "EVENTS"


class Delimiter(Enum):
    COMMA = ","


CHUNK_SIZE = 20 * 1024 * 1024  # File upload chunk size 20MB


class ScheduleFrequency(str, Enum):
    EVERY_HOUR = "1 hour"
    EVERY_2_HOURS = "2 hours"
    EVERY_4_HOURS = "4 hours"
    EVERY_8_HOURS = "8 hours"
    EVERY_12_HOURS = "12 hours"
    EVERYDAY = "1 day"


class ScheduleType(str, Enum):
    INCREMENTAL_APPEND = "INCREMENTAL_APPEND"
    FULL_REFRESH_APPEND = "FULL_REFRESH_APPEND"
