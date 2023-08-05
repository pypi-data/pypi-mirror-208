from typing import Dict, Any

from spotlight.api.organization.view.__util import _get_organization_view_request_info
from spotlight.core.common.decorators import data_request
from spotlight.core.common.requests import __get_request


@data_request
def get_organization_view(id: str) -> Dict[str, Any]:
    """
    Get organization view by ID.

    Args:
        id (str): Organization ID

    Returns:
        Dict[str, Any]: Organization view response
    """
    request_info = _get_organization_view_request_info(id)
    return __get_request(**request_info)
