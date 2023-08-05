import logging
from typing import List

import pandas as pd

from spotlight.api.rule.model import RuleResponse
from spotlight.core.common.enum import Severity, Status, ThresholdType
from spotlight.core.pipeline.execution.rule import AbstractRule
from spotlight.core.pipeline.model.rule import RuleResult

logger = logging.getLogger(__name__)


def build_rule_result(
    rule: AbstractRule,
    start_time: int,
    end_time: int,
    data: pd.DataFrame,
    result: pd.DataFrame,
) -> RuleResult:
    """
    Helper method for building the rule result.

    Args:
        rule (RuleResponse): The rule being applied to the data
        start_time (int): The timestamp from when the job started
        end_time (int): The timestamp from when the job ended
        data (pd.DataFrame): The raw dataset being tested
        result (pd.DataFrame): All the rules that failed the test

    Result:
        RuleResult: The result of the rule
    """
    status = get_rule_status(rule, data, result)
    samples = construct_samples(rule, result) if status != Status.SUCCESS else []
    return RuleResult(
        start_time=start_time,
        end_time=end_time,
        status=status,
        flagged_results=len(result),
        rule=rule.to_dict(),
        samples=samples,
    )


def get_rule_status(
    rule: AbstractRule,
    data: pd.DataFrame,
    result: pd.DataFrame,
) -> Status:
    """
    Helper method for determining the Status of the rule.

    Args:
        rule (RuleResponse): The rule applied to the data
        data (pd.DataFrame): The raw dataset being tested
        result (pd.DataFrame): All the rules that failed the test

    Returns:
        Status: The status of the rule
    """
    success = is_successful(len(result), len(data), rule)
    if success:
        return Status.SUCCESS
    elif rule.severity == Severity.WARN:
        return Status.WARNING
    else:
        return Status.FAILURE


def is_successful(failure_count: int, total_count: int, rule: AbstractRule) -> bool:
    """
    Helper method for determining the success of a rule

    Args:
        failure_count (int): The number of flagged results
        total_count (int): The total number of data points tested
        rule (AbstractRule): The rule run on the data

    Returns:
        bool: A flag representing the success of a job
    """
    if rule.threshold_type == ThresholdType.TOTAL:
        return failure_count < rule.threshold
    elif rule.threshold_type == ThresholdType.PERCENTAGE:
        failure_percentage = (failure_count / total_count) * 100
        return failure_percentage < rule.threshold


def construct_samples(rule: AbstractRule, results: pd.DataFrame) -> List[dict]:
    """
    Helper method for extracting a sample from the failed results
    """
    fields = set(rule.sampling_fields) if rule.sampling_fields else set()
    if fields == set():
        return []

    schema = set(results.columns)
    fields = schema if fields == {"*"} else fields.intersection(set(schema))
    sample = results[list(fields)][:10]
    return sample.to_dict("records")
