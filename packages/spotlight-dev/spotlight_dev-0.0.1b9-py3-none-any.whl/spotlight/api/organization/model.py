from typing import Optional

from pydantic import Field

from spotlight.core.common.base import Base


class OrganizationRequest(Base):
    name: str
    description: Optional[str] = Field(default=None)


class OrganizationResponse(Base):
    id: str
    name: str
    description: Optional[str]
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]
