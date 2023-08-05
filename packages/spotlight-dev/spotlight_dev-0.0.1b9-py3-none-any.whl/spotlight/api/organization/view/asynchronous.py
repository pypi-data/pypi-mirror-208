from typing import Dict, Any

from spotlight.api.organization.view.__util import _get_organization_view_request_info
from spotlight.core.common.decorators import async_data_request
from spotlight.core.common.requests import __async_get_request


@async_data_request
async def async_get_organization_view(id: str) -> Dict[str, Any]:
    """
    Asynchronously get organization view by ID.

    Args:
        id (str): Organization ID

    Returns:
        Dict[str, Any]: Organization view response
    """
    request_info = _get_organization_view_request_info(id)
    return await __async_get_request(**request_info)
