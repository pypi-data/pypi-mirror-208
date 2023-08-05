import logging
from typing import Any, List, Optional

from spotlight.api.job.model import JobResponse
from spotlight.core.pipeline.execution.rule import AbstractRule
from spotlight.core.pipeline.execution import ApplyRule, execute_pipeline
from spotlight.core.pipeline.model.pipeline import PipelineResult
from spotlight.core.pipeline.runner.utils import start_job, stop_job

logger = logging.getLogger(__name__)


def pipeline_runner(
    data: Any,
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
    Runs data through a data quality pipeline.

    NOTE: You must provide the tag names and/or the tag ids for this method to run.
    NOTE: The number of rules run in parallel is dependent on the number of processes.

    Args:
        data (Any): Data that is run through the pipeline
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
        JobResponse: The job response with all the information from the run
    """
    job, rules = start_job(
        job_name=job_name,
        tag_names=tag_names,
        tag_ids=tag_ids,
        metadata=metadata,
    )
    rules.extend(additional_rules or [])
    result = execute_pipeline(
        data, job.name, apply_rule, rules, multi_processing, processes
    )

    job = stop_job(
        job=job,
        pipeline_result=result,
    )
    return job


def offline_pipeline_runner(
    data: Any,
    job_name: str,
    apply_rule: ApplyRule,
    rules: List[AbstractRule],
    *,
    multi_processing: bool = False,
    processes: int = 5,
) -> PipelineResult:
    """
    Runs data through a data quality pipeline.

    NOTE: This pipeline will run locally and the results will NOT be synced to the API making the results unavailable in
    the UI
    NOTE: The number of rules run in parallel is dependent on the number of processes.

    Args:
        job_name (str): Name for the test job
        data (Any): Data that is run through the pipeline
        apply_rule (ApplyRule): function for applying the rule(s) to the data provided
        rules (List[RuleRequest]): A list of the rules to run on the pipeline
        multi_processing (bool): Optional flag to run the rules over the data concurrently
        processes (int): Optional number of process to spin up when running the rules concurrently

    Returns:
        PipelineResult: The result of the pipeline
    """
    result = execute_pipeline(
        data, job_name, apply_rule, rules, multi_processing, processes
    )
    return result
