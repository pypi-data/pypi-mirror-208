from typing import List, Optional

from spotlight.core.common.base import Base
from spotlight.core.common.enum import Status


class RuleResult(Base):
    start_time: int
    end_time: int
    status: Status
    flagged_results: int
    rule: dict
    samples: Optional[List[dict]]
