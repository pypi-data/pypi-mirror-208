from typing import Dict, Any, List

import backoff
import requests

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
from spotlight.core.common.decorators import data_request
from spotlight.core.common.requests import (
    __get_request,
    __post_request,
    __put_request,
    __delete_request,
)


@data_request
def get_rule(id: str) -> Dict[str, Any]:
    """
    Get rule by ID.

    Args:
        id (str): Rule ID

    Returns:
        Dict[str, Any]: Rule response
    """
    request_info = _get_rule_request_info(id)
    return __get_request(**request_info)


@data_request
def get_rules() -> List[Dict[str, Any]]:
    """
    Get all rules.

    Returns:
        List[Dict[str, Any]]: List of rule responses
    """
    request_info = _get_rules_request_info()
    return __get_request(**request_info)


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
    max_tries=3,
)
@data_request
def get_rules_by_tags(request: LookupRequest) -> List[Dict[str, Any]]:
    """
    Get all rules by tags.

    Args:
        request (LookupRequest): The tag information used in the rule look up

    Returns:
        List[Dict[str, Any]]: List of rule responses
    """
    request_info = _get_all_rules_by_tags_request_info(request)
    return __post_request(**request_info)


@data_request
def search_rules(request: SearchRequest) -> List[Dict[str, Any]]:
    """
    Search all rules.

    Parameters:
        request (SearchRequest): A request carrying the search query

    Returns:
        List[Dict[str, Any]]: List of rule responses
    """
    request_info = _search_rules_request_info(request)
    return __post_request(**request_info)


@data_request
def create_rule(request: RuleRequest) -> Dict[str, Any]:
    """
    Create rule.

    Args:
        request (RuleRequest): Rule request

    Returns:
        Dict[str, Any]: Rule response
    """
    request_info = _create_rule_request_info(request)
    return __put_request(**request_info)


@data_request
def update_rule(id: str, request: RuleRequest) -> Dict[str, Any]:
    """
    Update rule.

    Args:
        id (str): Rule ID
        request (RuleRequest): Rule request

    Returns:
        Dict[str, Any]: Rule response
    """
    request_info = _update_rule_request_info(id, request)
    return __post_request(**request_info)


@data_request
def declarative_update_rule_tags(id: str, tag_ids: List[str]) -> Dict[str, Any]:
    """
    Sets the state of the rule's tags to the ones passed in.

    Args:
        id (str): Rule ID
        tag_ids (List[str]): List of tag ids to put the rule in

    Returns:
        Dict[str, Any]: Rule tag response
    """
    request_info = _declarative_update_rule_tags_request_info(id, tag_ids)
    return __post_request(**request_info)


@data_request
def delete_rule(id: str) -> None:
    """
    Delete rule by ID.

    Args:
        id (str): Rule ID

    Returns:
        None
    """
    request_info = _delete_rule_request_info(id)
    return __delete_request(**request_info)
