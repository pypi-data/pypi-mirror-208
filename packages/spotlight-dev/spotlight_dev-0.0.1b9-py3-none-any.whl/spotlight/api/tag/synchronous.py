from typing import Dict, Any, List

import backoff
import requests

from spotlight.api.model import SearchRequest, LookupRequest
from spotlight.api.tag.__util import (
    _get_tag_request_info,
    _get_tag_by_name_request_info,
    _get_tags_request_info,
    _get_tags_by_rule_id_request_info,
    _search_tags_request_info,
    _create_tag_request_info,
    _update_tag_request_info,
    _delete_tag_request_info,
    _unique_tag_name_request_info,
    _get_tags_by_lookup_request_info,
)
from spotlight.api.tag.model import TagRequest
from spotlight.core.common.decorators import data_request

from spotlight.core.common.requests import (
    __get_request,
    __post_request,
    __put_request,
    __delete_request,
)


@data_request
def get_tag(id: str) -> Dict[str, Any]:
    """
    Get tag by ID.

    Args:
        id (str): Tag ID

    Returns:
        Dict[str, Any]: Tag response
    """
    request_info = _get_tag_request_info(id)
    return __get_request(**request_info)


@data_request
def get_tag_by_name(tag_name: str) -> Dict[str, Any]:
    """
    Get tag by name.

    Args:
        tag_name (str): Tag name

    Returns:
        Dict[str, Any]: Tag response
    """
    request_info = _get_tag_by_name_request_info(tag_name)
    return __get_request(**request_info)


@data_request
def get_tags() -> List[Dict[str, Any]]:
    """
    Get all tags.

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _get_tags_request_info()
    return __get_request(**request_info)


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
    max_tries=3,
)
@data_request
def get_tags_by_lookup(request: LookupRequest) -> List[Dict[str, Any]]:
    """
    Get all tags by lookup.

    Args:
        request (LookupRequest): The tag information used in the tag look up

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _get_tags_by_lookup_request_info(request)
    return __post_request(**request_info)


@data_request
def get_tags_by_rule_id(rule_id: str) -> List[Dict[str, Any]]:
    """
    Get all tags by rule ID.

    Args:
        rule_id (str): Rule ID

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _get_tags_by_rule_id_request_info(rule_id)
    return __get_request(**request_info)


@data_request
def search_tags(request: SearchRequest) -> List[Dict[str, Any]]:
    """
    Search all tags.

    Parameters:
        request (SearchRequest): A request carrying the search query

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _search_tags_request_info(request)
    return __post_request(**request_info)


@data_request
def create_tag(request: TagRequest) -> Dict[str, Any]:
    """
    Create tag.

    Args:
        request (TagRequest): Tag request

    Returns:
        Dict[str, Any]: Tag response
    """
    request_info = _create_tag_request_info(request)
    return __put_request(**request_info)


@data_request
def update_tag(id: str, request: TagRequest) -> Dict[str, Any]:
    """
    Update tag.

    Args:
        id (str): Tag ID
        request (TagRequest): Tag request

    Returns:
        Dict[str, Any]: Tag response
    """
    request_info = _update_tag_request_info(id, request)
    return __post_request(**request_info)


@data_request
def delete_tag(id: str) -> None:
    """
    Delete tag by ID.

    Args:
        id (str): Tag ID

    Returns:
        None
    """
    request_info = _delete_tag_request_info(id)
    return __delete_request(**request_info)


@data_request
def is_tag_name_unique(tag_name: str) -> bool:
    """
    Checks to see if the tag name is unique

    Args:
        tag_name (str): The new tag name that is being tested

    Returns:
        Bool: A boolean representing if the name is unique
    """
    request_info = _unique_tag_name_request_info(tag_name)
    return __post_request(**request_info)
