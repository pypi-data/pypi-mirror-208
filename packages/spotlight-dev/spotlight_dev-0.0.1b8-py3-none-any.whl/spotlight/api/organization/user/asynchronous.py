from typing import Dict, Any, List

from spotlight.api.organization.user.__util import (
    _create_organization_user_request_info,
    _update_organization_user_request_info,
    _delete_organization_user_request_info,
)
from spotlight.api.organization.user.model import OrganizationUserRequest
from spotlight.core.common.decorators import async_data_request

from spotlight.core.common.requests import (
    __async_post_request,
    __async_put_request,
    __async_delete_request,
)


@async_data_request
async def async_create_organization_user(
    request: OrganizationUserRequest,
) -> Dict[str, Any]:
    """
    Asynchronously create organization user.

    Args:
        request (OrganizationUserRequest): Organization user request

    Returns:
        Dict[str, Any]: Organization user response
    """
    request_info = _create_organization_user_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request
async def async_update_organization_user(
    id: str, request: OrganizationUserRequest
) -> Dict[str, Any]:
    """
    Asynchronously update organization user.

    Args:
        id (str): Organization user ID
        request (OrganizationUserRequest): Organization user request

    Returns:
        Dict[str, Any]: Organization user response
    """
    request_info = _update_organization_user_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_delete_organization_user(organization_id: str, user_email: str) -> None:
    """
    Asynchronously delete organization user.

    Args:
        organization_id (str): Organization user ID
        user_email (str): User email

    Returns:
        None
    """
    request_info = _delete_organization_user_request_info(organization_id, user_email)
    return await __async_delete_request(**request_info)
