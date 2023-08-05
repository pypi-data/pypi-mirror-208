from typing import Dict, Any, List

import aiohttp
import backoff

from spotlight.api.model import SearchRequest, LookupRequest
from spotlight.api.tag.__util import (
    _get_tag_request_info,
    _get_tags_request_info,
    _create_tag_request_info,
    _update_tag_request_info,
    _delete_tag_request_info,
    _search_tags_request_info,
    _unique_tag_name_request_info,
    _get_tag_by_name_request_info,
    _get_tags_by_rule_id_request_info,
    _get_tags_by_lookup_request_info,
)
from spotlight.api.tag.model import TagRequest
from spotlight.core.common.decorators import async_data_request

from spotlight.core.common.requests import (
    __async_get_request,
    __async_post_request,
    __async_put_request,
    __async_delete_request,
)


@async_data_request
async def async_get_tag(id: str) -> Dict[str, Any]:
    """
    Asynchronously get tag by ID.

    Args:
        id (str): tag ID

    Returns:
        Dict[str, Any]: tag response
    """
    request_info = _get_tag_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_tag_by_name(tag_name: str) -> Dict[str, Any]:
    """
    Asynchronously get tag by name.

    Args:
        tag_name (str): tag name

    Returns:
        Dict[str, Any]: tag response
    """
    request_info = _get_tag_by_name_request_info(tag_name)
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_tags() -> List[Dict[str, Any]]:
    """
    Asynchronously get all tags.

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _get_tags_request_info()
    return await __async_get_request(**request_info)


@backoff.on_exception(
    backoff.expo, (aiohttp.ClientTimeout, aiohttp.ClientConnectionError), max_tries=3
)
@async_data_request
async def async_get_tags_by_lookup(request: LookupRequest) -> List[Dict[str, Any]]:
    """
    Asynchronously get all tags by lookup.

    Args:
        request (LookupRequest): The tag information used in the tag look up

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _get_tags_by_lookup_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_get_tags_by_rule_id(rule_id: str) -> List[Dict[str, Any]]:
    """
    Asynchronously get all tags by rule ID.

    Args:
        rule_id (str): Rule ID

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _get_tags_by_rule_id_request_info(rule_id)
    return await __async_get_request(**request_info)


@async_data_request
async def async_search_tags(request: SearchRequest) -> List[Dict[str, Any]]:
    """
    Asynchronously search all tags.

    Parameters:
        request (SearchRequest): A request carrying the search query

    Returns:
        List[Dict[str, Any]]: List of tag responses
    """
    request_info = _search_tags_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_create_tag(request: TagRequest) -> Dict[str, Any]:
    """
    Asynchronously create tag.

    Args:
        request (TagRequest): tag request

    Returns:
        Dict[str, Any]: tag response
    """
    request_info = _create_tag_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request
async def async_update_tag(id: str, request: TagRequest) -> Dict[str, Any]:
    """
    Asynchronously update tag.

    Args:
        id (str): tag ID
        request (TagRequest): tag request

    Returns:
        Dict[str, Any]: tag response
    """
    request_info = _update_tag_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_delete_tag(id: str) -> None:
    """
    Asynchronously delete tag by ID.

    Args:
        id (str): tag ID

    Returns:
        None
    """
    request_info = _delete_tag_request_info(id)
    return await __async_delete_request(**request_info)


@async_data_request
async def async_is_tag_name_unique(tag_name: str) -> bool:
    """
    Asynchronously checks to see if the tag name is unique

    Args:
        tag_name (str): The new tag name that is being tested

    Returns:
        Bool: A boolean representing if the name is unique
    """
    request_info = _unique_tag_name_request_info(tag_name)
    return await __async_post_request(**request_info)
