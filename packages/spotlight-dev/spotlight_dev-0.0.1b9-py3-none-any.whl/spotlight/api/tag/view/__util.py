def _get_tag_view_request_info(id: str) -> dict:
    return {"endpoint": f"dq/tag/view/{id}"}


def _get_tag_view_by_name_request_info(name: str) -> dict:
    return {"endpoint": f"dq/tag/view", "params": {"name": name}}
