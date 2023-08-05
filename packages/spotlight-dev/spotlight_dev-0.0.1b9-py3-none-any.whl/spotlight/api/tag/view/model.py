from typing import Optional, List

from spotlight.api.rule.model import RuleResponse
from spotlight.core.common.base import Base


class TagViewResponse(Base):
    id: str
    name: str
    description: Optional[str]
    rules: List[RuleResponse]
    created_by: str
    created_at: int
    updated_by: Optional[str]
    updated_at: Optional[int]
