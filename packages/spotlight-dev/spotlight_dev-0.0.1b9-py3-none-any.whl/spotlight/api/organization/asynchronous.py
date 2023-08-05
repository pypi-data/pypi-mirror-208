from typing import Dict, Any, List

from spotlight.api.organization.__util import (
    _get_organization_request_info,
    _get_organizations_request_info,
    _create_organization_request_info,
    _update_organization_request_info,
    _delete_organization_request_info,
    _get_active_organization_request_info,
)
from spotlight.api.organization.model import OrganizationRequest
from spotlight.core.common.decorators import async_data_request

from spotlight.core.common.requests import (
    __async_get_request,
    __async_post_request,
    __async_put_request,
    __async_delete_request,
)


@async_data_request
async def async_get_organization(id: str) -> Dict[str, Any]:
    """
    Asynchronously get organization by ID.

    Args:
        id (str): Organization ID

    Returns:
        Dict[str, Any]: Organization response
    """
    request_info = _get_organization_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_organizations() -> List[Dict[str, Any]]:
    """
    Asynchronously get all organizations.

    Returns:
        List[Dict[str, Any]]: List of organization responses
    """
    request_info = _get_organizations_request_info()
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_active_organization() -> Dict[str, Any]:
    """
    Asynchronously get the active organization for a user.

    Returns:
        Dict[str, Any]: An organization responses
    """
    request_info = _get_active_organization_request_info()
    return await __async_get_request(**request_info)


@async_data_request
async def async_create_organization(request: OrganizationRequest) -> Dict[str, Any]:
    """
    Asynchronously create organization.

    Args:
        request (OrganizationRequest): Organization request

    Returns:
        Dict[str, Any]: Organization response
    """
    request_info = _create_organization_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request
async def async_update_organization(
    id: str, request: OrganizationRequest
) -> Dict[str, Any]:
    """
    Asynchronously update organization.

    Args:
        id (str): Organization ID
        request (OrganizationRequest): Organization request

    Returns:
        Dict[str, Any]: Organization response
    """
    request_info = _update_organization_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_delete_organization(id: str) -> None:
    """
    Asynchronously delete organization by ID.

    Args:
        id (str): Organization ID

    Returns:
        None
    """
    request_info = _delete_organization_request_info(id)
    return await __async_delete_request(**request_info)
