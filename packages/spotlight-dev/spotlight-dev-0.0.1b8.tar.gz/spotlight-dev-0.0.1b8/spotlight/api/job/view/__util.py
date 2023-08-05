def _get_job_view_request_info(id: str) -> dict:
    return {"endpoint": f"config/job/view/{id}"}
