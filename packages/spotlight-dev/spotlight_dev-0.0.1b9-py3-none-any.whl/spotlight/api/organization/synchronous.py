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
from spotlight.core.common.decorators import data_request
from spotlight.core.common.requests import (
    __get_request,
    __post_request,
    __put_request,
    __delete_request,
)


@data_request
def get_organization(id: str) -> Dict[str, Any]:
    """
    Get organization by ID.

    Args:
        id (str): Organization ID

    Returns:
        Dict[str, Any]: Organization response
    """
    request_info = _get_organization_request_info(id)
    return __get_request(**request_info)


@data_request
def get_organizations() -> List[Dict[str, Any]]:
    """
    Get all organizations.

    Returns:
        List[Dict[str, Any]]: List of organization responses
    """
    request_info = _get_organizations_request_info()
    return __get_request(**request_info)


@data_request
def get_active_organization() -> Dict[str, Any]:
    """
    Get the active organization for a user.

    Returns:
        Dict[str, Any]: List of organization responses
    """
    request_info = _get_active_organization_request_info()
    return __get_request(**request_info)


@data_request
def create_organization(request: OrganizationRequest) -> Dict[str, Any]:
    """
    Create organization.

    Args:
        request (OrganizationRequest): Organization request

    Returns:
        Dict[str, Any]: Organization response
    """
    request_info = _create_organization_request_info(request)
    return __put_request(**request_info)


@data_request
def update_organization(id: str, request: OrganizationRequest) -> Dict[str, Any]:
    """
    Update organization.

    Args:
        id (str): Organization ID
        request (OrganizationRequest): Organization request

    Returns:
        Dict[str, Any]: Organization response
    """
    request_info = _update_organization_request_info(id, request)
    return __post_request(**request_info)


@data_request
def delete_organization(id: str) -> None:
    """
    Delete organization by ID.

    Args:
        id (str): Organization ID

    Returns:
        None
    """
    request_info = _delete_organization_request_info(id)
    return __delete_request(**request_info)
