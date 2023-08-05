from typing import Optional, List

from pydantic import Field

from spotlight.core.common.base import Base
from spotlight.core.common.enum import Severity, ThresholdType


class RuleRequest(Base):
    name: str
    predicate: str
    description: Optional[str] = Field(default=None)
    threshold: Optional[float] = Field(default=None)
    threshold_type: Optional[ThresholdType] = Field(default=ThresholdType.TOTAL)
    severity: Optional[Severity] = Field(default=Severity.ERROR)
    sampling_fields: Optional[List[str]] = Field(default=None)


class RuleResponse(Base):
    id: str
    name: str
    description: Optional[str]
    predicate: str
    threshold: float
    threshold_type: ThresholdType
    severity: Severity
    sampling_fields: List[str]
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]


class RuleTagResponse(Base):
    tag_id: str
    rule_id: str
    created_by: str
    created_at: int
