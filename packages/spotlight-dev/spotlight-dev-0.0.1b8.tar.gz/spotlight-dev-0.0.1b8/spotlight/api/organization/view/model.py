from typing import Optional, List

from spotlight.api.organization.user.model import OrganizationUserResponse
from spotlight.core.common.base import Base


class OrganizationViewResponse(Base):
    id: str
    name: str
    description: Optional[str]
    users: List[OrganizationUserResponse]
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]
