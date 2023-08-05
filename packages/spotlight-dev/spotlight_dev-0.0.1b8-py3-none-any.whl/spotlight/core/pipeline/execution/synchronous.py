import logging
from multiprocessing import Pool
from typing import Any, List, Callable

from spotlight.core.common.date.function import current_timestamp
from spotlight.core.pipeline.execution.rule import AbstractRule
from spotlight.core.pipeline.model.pipeline import PipelineResult
from spotlight.core.pipeline.model.rule import RuleResult

logger = logging.getLogger(__name__)


ApplyRule = Callable[[Any, AbstractRule], RuleResult]


def execute_pipeline(
    data: Any,
    job_name: str,
    apply_rule: ApplyRule,
    rules: List[AbstractRule],
    multi_processing: bool = False,
    processes: int = 5,
) -> PipelineResult:
    start_time = current_timestamp()
    logger.info(f"Starting data quality pipeline [{job_name=}, {start_time=}]")
    rule_results = __run_pipeline(
        data, rules, apply_rule, multi_processing=multi_processing, processes=processes
    )
    end_time = current_timestamp()
    result = PipelineResult.build_result(job_name, start_time, end_time, rule_results)
    logger.debug(f"Data quality pipeline result: {result}")
    logger.info(
        f"Data quality pipeline finished [{job_name=}, {end_time=}]: {result.status}"
    )
    return result


def __run_pipeline(
    data: Any,
    rules: List[AbstractRule],
    apply_rule: ApplyRule,
    *,
    multi_processing: bool = False,
    processes: int = 5,
) -> List[RuleResult]:
    """
    Wrapper for the different pipeline types.

    Args:
        data (Any): The data being run through the pipeline
        rules (List[AbstractRule]): The rules being run on the data
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        multi_processing (bool): Optional flag to run the rules over the data concurrently
        processes (int): Optional number of process to spin up when running the rules concurrently

    Returns:
        List[RuleResult]: The result of running the pipeline
    """
    if multi_processing:
        logger.debug(f"Running the multiprocessing pipeline with {processes} processes")
        return _multiprocessing_pipeline(apply_rule, data, rules, processes)
    return _synchronous_pipeline(apply_rule, data, rules)


def _synchronous_pipeline(
    apply_rule: ApplyRule, data: Any, rules: List[AbstractRule]
) -> List[RuleResult]:
    """
    Runs all the rules sequentially over the data.

    Args:
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        data (Any): The data being run through the pipeline
        rules(List[AbstractRule]): The rules being run on the data

    Returns:
        List[RuleResult]: The result of running the pipeline
    """
    results = [_apply_rule(apply_rule, data, rule) for rule in rules]
    return results


def _multiprocessing_pipeline(
    apply_rule: ApplyRule, data: Any, rules: List[AbstractRule], processes: int
) -> List[RuleResult]:
    """
    Runs all the rules over the data in parallel.

    NOTE: The number of rules run in parallel is dependent on the number of processes.

    Args:
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        data (Any): The data being run through the pipeline
        rules (List[AbstractRule]): The rules being run on the data
        processes (int): The number of process to spin up when running the rules concurrently

    Returns:
        List[RuleResult]: The result of running the pipeline
    """
    with Pool(processes=processes) as pool:
        results = pool.map(lambda rule: _apply_rule(apply_rule, data, rule), rules)
    return results


def _apply_rule(apply_rule: ApplyRule, data: Any, rule: AbstractRule) -> RuleResult:
    """
    Wrapper for logging purposes

    Args:
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        data (Any): The data being run through the pipeline
        rule (AbstractRule): The rule being run on the data

    Returns:
        RuleResult: The result of the rule
    """
    logger.debug(f"Running rule {rule.name}")
    result = apply_rule(data, rule)
    logger.info(
        f"Rule completed [name={rule.name}, flagged_results={result.flagged_results}, threshold={rule.threshold}, "
        f"threshold_type={rule.threshold_type}]: {result.status}"
    )
    return result
