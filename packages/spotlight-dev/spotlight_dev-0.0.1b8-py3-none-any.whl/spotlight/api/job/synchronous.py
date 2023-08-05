from typing import Dict, Any, List

import backoff
import requests

from spotlight.api.model import SearchRequest
from spotlight.api.job.__util import (
    _get_job_request_info,
    _get_jobs_request_info,
    _create_job_request_info,
    _update_job_request_info,
    _delete_job_request_info,
    _search_jobs_request_info,
)
from spotlight.api.job.model import JobRequest
from spotlight.core.common.decorators import data_request

from spotlight.core.common.requests import (
    __get_request,
    __post_request,
    __put_request,
    __delete_request,
)


@data_request
def get_job(id: str) -> Dict[str, Any]:
    """
    Get job by ID.

    Args:
        id (str): Job ID

    Returns:
        Dict[str, Any]: Job response
    """
    request_info = _get_job_request_info(id)
    return __get_request(**request_info)


@data_request
def get_jobs() -> List[Dict[str, Any]]:
    """
    Get all jobs.

    Returns:
        List[Dict[str, Any]]: List of job response
    """
    request_info = _get_jobs_request_info()
    return __get_request(**request_info)


@data_request
def search_jobs(request: SearchRequest) -> List[Dict[str, Any]]:
    """
    Search all Jobs.

    Parameters:
        request (SearchRequest): A request carrying the search query

    Returns:
        List[Dict[str, Any]]: List of job responses
    """
    request_info = _search_jobs_request_info(request)
    return __post_request(**request_info)


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
    max_tries=3,
)
@data_request
def create_job(request: JobRequest) -> Dict[str, Any]:
    """
    Create job.

    Args:
        request (JobRequest): Job request

    Returns:
        Dict[str, Any]: Job response
    """
    request_info = _create_job_request_info(request)
    return __put_request(**request_info)


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
    max_tries=3,
)
@data_request
def update_job(id: str, request: JobRequest) -> Dict[str, Any]:
    """
    Update job.

    NOTE: Tags associated to the job are not updated

    Args:
        id (str): Job ID
        request (JobRequest): Job request

    Returns:
        Dict[str, Any]: Job response
    """
    request_info = _update_job_request_info(id, request)
    return __post_request(**request_info)


@data_request
def delete_job(id: str) -> None:
    """
    Delete job by ID.

    Args:
        id (str): Job ID

    Returns:
        None
    """
    request_info = _delete_job_request_info(id)
    return __delete_request(**request_info)
