from spotlight.api.organization.model import OrganizationRequest


def _get_organization_request_info(id: str) -> dict:
    return {"endpoint": f"dq/organization/{id}"}


def _get_organizations_request_info() -> dict:
    return {"endpoint": f"dq/organization"}


def _get_active_organization_request_info() -> dict:
    return {"endpoint": f"dq/organization/active"}


def _create_organization_request_info(request: OrganizationRequest) -> dict:
    return {"endpoint": f"dq/organization", "json": request.request_dict()}


def _update_organization_request_info(id: str, request: OrganizationRequest) -> dict:
    return {"endpoint": f"dq/organization/{id}", "json": request.request_dict()}


def _delete_organization_request_info(id: str) -> dict:
    return {"endpoint": f"dq/organization/{id}"}
