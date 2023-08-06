import datetime
import uuid
from typing import List, Optional

import dateparser
from pydantic import BaseModel, validator

from gantry.automations.curators.selectors import Selector


class CreateCuratorRequest(BaseModel):
    application_name: str
    name: str
    curated_dataset_name: str
    start_on: datetime.datetime
    curation_interval: datetime.timedelta
    curation_delay: datetime.timedelta = datetime.timedelta(days=0)
    curate_past_intervals: bool = False
    selectors: List[Selector]


class UpdateCuratorRequest(BaseModel):
    name: str
    new_name: Optional[str]
    new_curated_dataset_name: Optional[str]
    curation_interval: Optional[datetime.timedelta]
    selectors: Optional[List[Selector]]
    allow_create_new_dataset: bool = False


class EnableCuratorRequest(BaseModel):
    name: str
    enable: bool


class CuratorInfo(BaseModel):
    id: uuid.UUID
    application_name: str
    name: str
    curated_dataset_name: str
    start_on: datetime.datetime
    curation_interval: datetime.timedelta
    curation_delay: datetime.timedelta
    curate_past_intervals: bool
    created_at: datetime.datetime
    selectors: List[Selector]

    @validator("start_on", "created_at", pre=True)
    def parse_datetime(cls, v):
        return dateparser.parse(v)


class DeletedCuratorInfo(BaseModel):
    curated_dataset_name: str
    id: uuid.UUID
    application_name: str
    deleted_at: datetime.datetime
