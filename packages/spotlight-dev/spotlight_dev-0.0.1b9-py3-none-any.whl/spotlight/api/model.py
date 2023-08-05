from typing import List
from spotlight.core.common.base import Base


class SearchRequest(Base):
    """
    Model for search requests
    """

    query: str


class LookupRequest(Base):
    tag_ids: List[str]
    tag_names: List[str]
