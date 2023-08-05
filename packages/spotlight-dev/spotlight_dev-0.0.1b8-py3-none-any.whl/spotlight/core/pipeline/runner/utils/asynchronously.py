import copy
from typing import Optional, List, Tuple

from spotlight.api.tag.asynchronous import async_get_tags_by_lookup
from spotlight.api.tag.model import TagResponse
from spotlight.api.job import (
    async_create_job,
    async_update_job,
)
from spotlight.api.job.model import JobRequest, JobResponse
from spotlight.api.rule.asynchronous import async_get_rules_by_tags
from spotlight.api.rule.model import RuleResponse
from spotlight.api.model import LookupRequest
from spotlight.core.common.enum import Status, JobType
from spotlight.core.pipeline.execution.rule import SQLRule
from spotlight.core.pipeline.model.pipeline import PipelineResult


async def __async_get_rule_and_tag_info(
    tag_names: Optional[List[str]] = None, tag_ids: Optional[List[str]] = None
) -> Tuple[List[TagResponse], List[RuleResponse]]:
    """
    Asynchronous helper method for getting the tag of rules from the tag_id or tag_name.

    Args:
        tag_names (Optional[List[str]]): The name of rule tags
        tag_ids (Optional[List[str]]): The id of the rule tags

    Returns:
        Tuple[List[TagResponse], List[RuleResponse]]: A list of all the tags, and rules associated with the tag
        info passed in
    """
    request = LookupRequest(
        tag_names=tag_names if tag_names else [],
        tag_ids=tag_ids if tag_ids else [],
    )
    response = await async_get_rules_by_tags(request)
    rules = [RuleResponse(**rule) for rule in response]
    tag_response = await async_get_tags_by_lookup(request)
    tags = [TagResponse(**tag) for tag in tag_response]
    return tags, rules


async def async_start_job(
    job_name: str,
    *,
    tag_names: Optional[List[str]] = None,
    tag_ids: Optional[List[str]] = None,
    job_type: JobType = JobType.BATCH,
    metadata: Optional[dict] = None,
) -> Tuple[JobResponse, List[SQLRule]]:
    """
    Asynchronously creates the job with the starting information.

    NOTE: You must provide the tag_name or tag_id but not both.

    Args:
        job_name (str): Name assigned to the job created from running this pipeline
        tag_names (Optional[List[str]]): The name of rule tags
        tag_ids (Optional[List[str]]): The id of the rule tags
        job_type (JobType): The type of job
        metadata (Optional[dict]): Metadata added to the job information

    Returns:
        Tuple[JobResponse, List[Rule]]: The created job and the rules used in the job
    """
    tags, rules = await __async_get_rule_and_tag_info(
        tag_names=tag_names, tag_ids=tag_ids
    )
    request = JobRequest(
        name=job_name,
        status=Status.IN_PROGRESS,
        tag_ids=[tag.id for tag in tags],
        metadata=metadata,
    )
    response = await async_create_job(request)
    job = JobResponse(**response)
    return job, [SQLRule.from_rule_response(rule) for rule in rules]


async def async_stop_job(
    job: JobResponse,
    pipeline_result: PipelineResult,
) -> JobResponse:
    """
    Asynchronously stops the job and updates it with all the results.

    Args:
        job (JobResponse): The job being updated
        pipeline_result (PipelineResult): The result of the piepline

    Returns:
        JobResponse: The updated job
    """
    combined_metadata = copy.deepcopy(job.metadata)
    combined_metadata.update(pipeline_result.metadata.request_dict())
    request = JobRequest(
        name=job.name,
        status=pipeline_result.status,
        start_time=pipeline_result.start_time,
        end_time=pipeline_result.end_time,
        metadata=combined_metadata,
    )
    response = await async_update_job(job.id, request)
    job = JobResponse(**response)
    return job
