from typing import Dict, Any

from spotlight.api.organization.user.__util import (
    _create_organization_user_request_info,
    _update_organization_user_request_info,
    _delete_organization_user_request_info,
)
from spotlight.api.organization.user.model import OrganizationUserRequest
from spotlight.core.common.decorators import data_request
from spotlight.core.common.requests import (
    __post_request,
    __put_request,
    __delete_request,
)


@data_request
def create_organization_user(request: OrganizationUserRequest) -> Dict[str, Any]:
    """
    Create organization user.

    Args:
        request (OrganizationUserRequest): Organization user request

    Returns:
        Dict[str, Any]: Organization user response
    """
    request_info = _create_organization_user_request_info(request)
    return __put_request(**request_info)


@data_request
def update_organization_user(request: OrganizationUserRequest) -> Dict[str, Any]:
    """
    Update organization user.

    Args:
        request (OrganizationUserRequest): Organization user request

    Returns:
        Dict[str, Any]: Organization user response
    """
    request_info = _update_organization_user_request_info(request)
    return __post_request(**request_info)


@data_request
def delete_organization(organization_id: str, user_email: str) -> None:
    """
    Delete organization user.

    Args:
        organization_id (str): Organization user ID
        user_email (str): User email

    Returns:
        None
    """
    request_info = _delete_organization_user_request_info(organization_id, user_email)
    return __delete_request(**request_info)
