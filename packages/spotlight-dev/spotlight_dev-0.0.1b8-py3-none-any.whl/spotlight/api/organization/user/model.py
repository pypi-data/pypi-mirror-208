from typing import Optional

from pydantic import Field

from spotlight.api.organization.user.enum import State
from spotlight.core.common.base import Base


class OrganizationUserRequest(Base):
    organization_id: str
    user_email: str
    state: State
    user_id: Optional[str] = Field(default=None)


class OrganizationUserResponse(Base):
    organization_id: str
    user_email: str
    state: State
    user_id: Optional[str]
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]
