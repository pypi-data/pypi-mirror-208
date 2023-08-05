from spotlight.api.organization.user.model import OrganizationUserRequest


def _create_organization_user_request_info(request: OrganizationUserRequest) -> dict:
    return {"endpoint": f"dq/organization/user", "json": request.request_dict()}


def _update_organization_user_request_info(request: OrganizationUserRequest) -> dict:
    return {"endpoint": f"dq/organization/user", "json": request.request_dict()}


def _delete_organization_user_request_info(
    organization_id: str, user_email: str
) -> dict:
    return {
        "endpoint": f"dq/organization/user",
        "params": {"organization_id": organization_id, "user_email": user_email},
    }
