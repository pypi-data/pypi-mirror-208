import logging
from typing import Any, List, Optional, Callable, Type

from spotlight.api.job.model import JobResponse
from spotlight.core.common.enum import JobType, Status
from spotlight.core.pipeline.execution.rule import AbstractRule
from spotlight.core.pipeline.execution import ApplyRule, execute_pipeline
from spotlight.core.pipeline.model.pipeline import PipelineResult
from spotlight.core.pipeline.runner.stream.source.abstract import AbstractDataSource
from spotlight.core.pipeline.runner.utils import start_job, stop_job

logger = logging.getLogger(__name__)


def __process_stream(
    data_source: AbstractDataSource,
    job_name: str,
    apply_rule: ApplyRule,
    rules: List[AbstractRule],
    multi_processing: bool = False,
    processes: int = 5,
    on_failure: Callable[[PipelineResult], Any] = lambda x: None,
) -> List[PipelineResult]:
    """
    This helper processes each message in the stream and runs it through a data pipeline

     Args:
        data_source (AbstractDataSource): Streaming data source
        job_name (str): Name assigned to the job created from running this pipeline
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        rules (List[AbstractRule]): The rules being run on the data
        multi_processing (bool): Optional flag to run the rules over the data concurrently
        processes (int): Optional number of process to spin up when running the rules concurrently
        on_failure (Callable[[PipelineResult], Any]): Optional function that is called when a message fails teh pipeline

    Returns:
        List[PipelineResult]: All the results from each pipeline iteration ran
    """
    results = []
    try:
        for idx, data in enumerate(data_source):
            logger.debug(f"Processing message in stream {idx=}: {data}")
            result = execute_pipeline(
                data, job_name, apply_rule, rules, multi_processing, processes
            )
            results.append(result)
            if result.status != Status.SUCCESS:
                logger.info(f"Message failed: {idx=}")
                logger.debug(f"Message failed {idx=}: {result}")
                on_failure(result)
    finally:
        logger.debug("Shutting down stream processor...")
        data_source.teardown()
    return results


def stream_pipeline_runner(
    data_source: AbstractDataSource,
    job_name: str,
    apply_rule: ApplyRule,
    *,
    tag_names: Optional[List[str]] = None,
    tag_ids: Optional[List[str]] = None,
    additional_rules: Optional[List[AbstractRule]] = None,
    metadata: Optional[dict] = None,
    multi_processing: bool = False,
    processes: int = 5,
) -> JobResponse:
    """
    Processes stream messages through a pipeline

    NOTE: You must provide the tag names and/or the tag ids for this method to run.
    NOTE: The number of rules run in parallel is dependent on the number of processes.

    Args:
        data_source (AbstractDataSource): Streaming data source
        job_name (str): Name assigned to the job created from running this pipeline
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        tag_names (Optional[List[str]]): List of tag names to use with the pipeline
        tag_ids (Optional[List[str]]): List of tag ids to use with the pipeline
        additional_rules (List[AbstractRule]): additional rules to run on the pipeline (specifically rules that aren't
        supported in the API i.e. AbstractCustomCodeRules)
        metadata (Optional[dict]): Metadata added to the job information
        multi_processing (bool): Optional flag to run the rules over the data concurrently
        processes (int): Optional number of process to spin up when running the rules concurrently

    Returns:
        JobResponse: The job response for the stream job
    """
    job, rules = start_job(
        job_name=job_name,
        tag_names=tag_names,
        tag_ids=tag_ids,
        job_type=JobType.STREAM,
        metadata=metadata,
    )
    rules.extend(additional_rules or [])

    __process_stream(
        data_source,
        job.name,
        apply_rule,
        rules,
        multi_processing,
        processes,
        lambda result: stop_job(job, result),
    )
    return job


def offline_stream_pipeline_runner(
    data_source: AbstractDataSource,
    job_name: str,
    apply_rule: ApplyRule,
    rules: List[AbstractRule],
    *,
    multi_processing: bool = False,
    processes: int = 5,
) -> List[PipelineResult]:
    """
    Streams data through a pipeline.

    NOTE: This pipeline will run locally and the results will NOT be synced to the API making the results
    unavailable in the UI
    NOTE: The number of rules run in parallel is dependent on the number of processes.

    Args:
        data_source (AbstractDataSource): Streaming data source
        job_name (str): Name for the test job
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        rules (List[RuleRequest]): A list of the rules to run on the pipeline
        multi_processing (bool): Optional flag to run the rules over the data concurrently
        processes (int): Optional number of process to spin up when running the rules concurrently

    Returns:
        List[PipelineResult]: A list of all the results from each iterator of data emitted from the data source
    """
    results = __process_stream(
        data_source, job_name, apply_rule, rules, multi_processing, processes
    )
    return results
