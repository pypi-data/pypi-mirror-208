from typing import Optional, List

from spotlight.core.common.base import Base


class TagRequest(Base):
    name: str
    description: Optional[str] = None


class TagResponse(Base):
    id: str
    name: str
    description: Optional[str]
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]
