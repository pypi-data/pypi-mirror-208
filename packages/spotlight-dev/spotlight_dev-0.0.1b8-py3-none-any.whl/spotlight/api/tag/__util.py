from spotlight.api.model import SearchRequest, LookupRequest
from spotlight.api.tag.model import TagRequest


def _get_tag_request_info(id: str) -> dict:
    return {"endpoint": f"dq/tag/{id}"}


def _get_tag_by_name_request_info(name: str) -> dict:
    return {"endpoint": f"dq/tag", "params": {"name": name}}


def _get_tags_request_info() -> dict:
    return {"endpoint": f"dq/tag"}


def _get_tags_by_lookup_request_info(request: LookupRequest) -> dict:
    return {"endpoint": f"dq/tag", "json": request.request_dict()}


def _get_tags_by_rule_id_request_info(rule_id: str) -> dict:
    return {"endpoint": f"dq/tag", "params": {"rule_id": rule_id}}


def _search_tags_request_info(request: SearchRequest) -> dict:
    return {"endpoint": f"dq/tag", "json": request.request_dict()}


def _create_tag_request_info(request: TagRequest) -> dict:
    return {"endpoint": f"dq/tag", "json": request.request_dict()}


def _update_tag_request_info(id: str, request: TagRequest) -> dict:
    return {"endpoint": f"dq/tag/{id}", "json": request.request_dict()}


def _delete_tag_request_info(id: str) -> dict:
    return {"endpoint": f"dq/tag/{id}"}


def _unique_tag_name_request_info(name: str) -> dict:
    return {
        "endpoint": f"dq/tag/unique",
        "params": {"tag_name": name},
    }
