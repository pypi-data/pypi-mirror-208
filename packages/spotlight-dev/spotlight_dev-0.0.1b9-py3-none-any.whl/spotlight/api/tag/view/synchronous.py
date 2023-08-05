from typing import Dict, Any

from spotlight.api.tag.view.__util import (
    _get_tag_view_request_info,
    _get_tag_view_by_name_request_info,
)
from spotlight.core.common.decorators import data_request

from spotlight.core.common.requests import (
    __get_request,
)


@data_request
def get_tag_view(id: str) -> Dict[str, Any]:
    """
    Get tag view by ID.

    Args:
        id (str): Tag ID

    Returns:
        Dict[str, Any]: Tag view response
    """
    request_info = _get_tag_view_request_info(id)
    return __get_request(**request_info)


@data_request
def get_tag_view_by_name(name: str) -> Dict[str, Any]:
    """
    Get tag view by name.

    Args:
        name (str): Tag name

    Returns:
        Dict[str, Any]: Tag view response
    """
    request_info = _get_tag_view_by_name_request_info(name)
    return __get_request(**request_info)
