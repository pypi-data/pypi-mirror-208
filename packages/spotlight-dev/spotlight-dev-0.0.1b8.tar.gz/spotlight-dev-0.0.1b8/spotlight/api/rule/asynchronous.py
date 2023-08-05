from typing import Dict, Any, List

import aiohttp
import backoff

from spotlight.api.model import SearchRequest, LookupRequest
from spotlight.api.rule.__util import (
    _get_rule_request_info,
    _get_rules_request_info,
    _create_rule_request_info,
    _update_rule_request_info,
    _delete_rule_request_info,
    _search_rules_request_info,
    _declarative_update_rule_tags_request_info,
    _get_all_rules_by_tags_request_info,
)
from spotlight.api.rule.model import RuleRequest
from spotlight.core.common.decorators import async_data_request

from spotlight.core.common.requests import (
    __async_get_request,
    __async_post_request,
    __async_put_request,
    __async_delete_request,
)


@async_data_request
async def async_get_rule(id: str) -> Dict[str, Any]:
    """
    Asynchronously get rule by ID.

    Args:
        id (str): Rule ID

    Returns:
        Dict[str, Any]: Rule response
    """
    request_info = _get_rule_request_info(id)
    return await __async_get_request(**request_info)


@async_data_request
async def async_get_rules() -> List[Dict[str, Any]]:
    """
    Asynchronously get all rules.

    Returns:
        List[Dict[str, Any]]: List of rule responses
    """
    request_info = _get_rules_request_info()
    return await __async_get_request(**request_info)


@backoff.on_exception(
    backoff.expo, (aiohttp.ClientTimeout, aiohttp.ClientConnectionError), max_tries=3
)
@async_data_request
async def async_get_rules_by_tags(request: LookupRequest) -> List[Dict[str, Any]]:
    """
    Asynchronously get all rules by tags.

    Args:
        request (LookupRequest): The tag information used in the rule look up

    Returns:
        List[Dict[str, Any]]: List of rule responses
    """
    request_info = _get_all_rules_by_tags_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_search_rules(request: SearchRequest) -> List[Dict[str, Any]]:
    """
    Asynchronously search all rules.

    Parameters:
        request (SearchRequest): A request carrying the search query

    Returns:
        List[Dict[str, Any]]: List of rule responses
    """
    request_info = _search_rules_request_info(request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_create_rule(request: RuleRequest) -> Dict[str, Any]:
    """
    Asynchronously create rule.

    Args:
        request (RuleRequest): Rule request

    Returns:
        Dict[str, Any]: Rule response
    """
    request_info = _create_rule_request_info(request)
    return await __async_put_request(**request_info)


@async_data_request
async def async_update_rule(id: str, request: RuleRequest) -> Dict[str, Any]:
    """
    Asynchronously update rule.

    Args:
        id (str): Rule ID
        request (RuleRequest): Rule request

    Returns:
        Dict[str, Any]: Rule response
    """
    request_info = _update_rule_request_info(id, request)
    return await __async_post_request(**request_info)


@async_data_request
async def async_declarative_update_rule_tags(
    id: str, tag_ids: List[str]
) -> Dict[str, Any]:
    """
    Asynchronously sets the state of the rule's tags to the ones passed in.

    Args:
        id (str): Rule ID
        tag_ids (List[str]): List of tag ids to put the rule in

    Returns:
        Dict[str, Any]: Rule tag response
    """
    request_info = _declarative_update_rule_tags_request_info(id, tag_ids)
    return await __async_post_request(**request_info)


@async_data_request
async def async_delete_rule(id: str) -> None:
    """
    Asynchronously delete rule by ID.

    Args:
        id (str): Rule ID

    Returns:
        None
    """
    request_info = _delete_rule_request_info(id)
    return await __async_delete_request(**request_info)
