from typing import Optional, List

from pydantic import Field

from spotlight.core.common.base import Base
from spotlight.core.common.enum import Status, JobType


class JobRequest(Base):
    name: str
    status: Status
    type: Optional[JobType] = Field(default=JobType.BATCH)
    tag_ids: Optional[List[str]] = Field(default=None)
    start_time: Optional[int] = Field(default=None)
    end_time: Optional[int] = Field(default=None)
    metadata: Optional[dict] = Field(default=None)


class JobResponse(Base):
    id: str
    name: str
    status: Status
    type: JobType
    start_time: Optional[int]
    end_time: Optional[int]
    metadata: dict
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]


class JobTagResponse(Base):
    tag_id: str
    rule_id: str
    created_by: str
    created_at: int
