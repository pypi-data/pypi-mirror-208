from abc import ABC, abstractmethod
from typing import Any, Optional, List

from spotlight.api.job.model import JobResponse
from spotlight.core.pipeline.execution.rule.abstract import AbstractRule
from spotlight.core.pipeline.model.pipeline import PipelineResult
from spotlight.core.pipeline.model.rule import RuleResult
from spotlight.core.pipeline.runner.batch import (
    pipeline_runner,
    async_pipeline_runner,
    offline_pipeline_runner,
)
from spotlight.core.pipeline.runner.stream.asynchronous import (
    async_stream_pipeline_runner,
    async_offline_stream_pipeline_runner,
)
from spotlight.core.pipeline.runner.stream.source.abstract import (
    AbstractDataSource,
    AbstractAsyncDataSource,
)
from spotlight.core.pipeline.runner.stream.synchronous import (
    stream_pipeline_runner,
    offline_stream_pipeline_runner,
)


class AbstractPipeline(ABC):
    @classmethod
    @abstractmethod
    def apply_rule(cls, data: Any, rule: AbstractRule) -> RuleResult:
        """
        This method applies a rule to the data provided

        Args:
            data (Any): The data associated with the plugin
            rule (AbstractRule): The rule being run on the data

        Returns:
            RuleResult: The result of the rule run
        """
        pass

    @classmethod
    def run(
        cls,
        data: Any,
        job_name: str,
        *,
        tag_names: Optional[List[str]] = None,
        tag_ids: Optional[List[str]] = None,
        additional_rules: Optional[List[AbstractRule]] = None,
        metadata: Optional[dict] = None,
        multi_processing: bool = False,
        processes: int = 5,
    ) -> JobResponse:
        """
        Runs data through the pipeline.

        NOTE: You must provide the tag names and/or the tag ids for this method to run.
        NOTE: The number of rules run in parallel is dependent on the number of processes.

        Args:
            data (Any): Data that is run through the pipeline
            job_name (str): Name assigned to the job created from running this pipeline
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
        return pipeline_runner(
            data=data,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            tag_names=tag_names,
            tag_ids=tag_ids,
            additional_rules=additional_rules,
            metadata=metadata,
            multi_processing=multi_processing,
            processes=processes,
        )

    @classmethod
    async def async_run(
        cls,
        data: Any,
        job_name: str,
        *,
        tag_names: Optional[List[str]] = None,
        tag_ids: Optional[List[str]] = None,
        additional_rules: Optional[List[AbstractRule]] = None,
        metadata: Optional[dict] = None,
        multi_processing: bool = False,
        processes: int = 5,
    ) -> JobResponse:
        """
        Asynchronously runs data through a pipeline.

        NOTE: You must provide the tag names and/or the tag ids for this method to run.
        NOTE: The number of rules run in parallel is dependent on the number of processes.

        Args:
            data (Any): Data that is run through the pipeline
            job_name (str): Name assigned to the job created from running this pipeline
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
        result = await async_pipeline_runner(
            data=data,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            tag_names=tag_names,
            tag_ids=tag_ids,
            additional_rules=additional_rules,
            metadata=metadata,
            multi_processing=multi_processing,
            processes=processes,
        )
        return result

    @classmethod
    def offline_run(
        cls,
        data: Any,
        job_name: str,
        rules: List[AbstractRule],
        *,
        multi_processing: bool = False,
        processes: int = 5,
    ) -> PipelineResult:
        """
        Runs data through the pipeline.

        NOTE: This pipeline will run locally and the results will NOT be synced to the API making the results
        unavailable in the UI
        NOTE: The number of rules run in parallel is dependent on the number of processes.

        Args:
            data (Any): Data that is run through the pipeline
            job_name (str): Name for the test job
            rules (List[RuleRequest]): A list of the rules to run on the pipeline
            multi_processing (bool): Optional flag to run the rules over the data concurrently
            processes (int): Optional number of process to spin up when running the rules concurrently

        Returns:
            PipelineResult: The result of the pipeline
        """
        return offline_pipeline_runner(
            data=data,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            rules=rules,
            multi_processing=multi_processing,
            processes=processes,
        )

    @classmethod
    def stream(
        cls,
        data_source: AbstractDataSource,
        job_name: str,
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
        return stream_pipeline_runner(
            data_source=data_source,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            tag_names=tag_names,
            tag_ids=tag_ids,
            additional_rules=additional_rules,
            metadata=metadata,
            multi_processing=multi_processing,
            processes=processes,
        )

    @classmethod
    async def async_stream(
        cls,
        data_source: AbstractAsyncDataSource,
        job_name: str,
        *,
        tag_names: Optional[List[str]] = None,
        tag_ids: Optional[List[str]] = None,
        additional_rules: Optional[List[AbstractRule]] = None,
        metadata: Optional[dict] = None,
        multi_processing: bool = False,
        processes: int = 5,
    ) -> JobResponse:
        """
        Asynchronously processes stream messages through a pipeline

        NOTE: You must provide the tag names and/or the tag ids for this method to run.
        NOTE: The number of rules run in parallel is dependent on the number of processes.

        Args:
            data_source (AbstractAsyncDataSource): Streaming data source
            job_name (str): Name assigned to the job created from running this pipeline
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
        result = await async_stream_pipeline_runner(
            data_source=data_source,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            tag_names=tag_names,
            tag_ids=tag_ids,
            additional_rules=additional_rules,
            metadata=metadata,
            multi_processing=multi_processing,
            processes=processes,
        )
        return result

    @classmethod
    def offline_stream(
        cls,
        data_source: AbstractDataSource,
        job_name: str,
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
            rules (List[RuleRequest]): A list of the rules to run on the pipeline
            multi_processing (bool): Optional flag to run the rules over the data concurrently
            processes (int): Optional number of process to spin up when running the rules concurrently

        Returns:
            List[PipelineResult]: A list of all the results from each iterator of data emitted from the data source
        """
        return offline_stream_pipeline_runner(
            data_source=data_source,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            rules=rules,
            multi_processing=multi_processing,
            processes=processes,
        )

    @classmethod
    async def async_offline_stream(
        cls,
        data_source: AbstractAsyncDataSource,
        job_name: str,
        rules: List[AbstractRule],
        *,
        multi_processing: bool = False,
        processes: int = 5,
    ) -> List[PipelineResult]:
        """
        Asynchronously streams data through a pipeline.

        NOTE: This pipeline will run locally and the results will NOT be synced to the API making the results
        unavailable in the UI
        NOTE: The number of rules run in parallel is dependent on the number of processes.

        Args:
            data_source (AbstractAsyncDataSource): Streaming data source
            job_name (str): Name for the test job
            rules (List[RuleRequest]): A list of the rules to run on the pipeline
            multi_processing (bool): Optional flag to run the rules over the data concurrently
            processes (int): Optional number of process to spin up when running the rules concurrently

        Returns:
            List[PipelineResult]: A list of all the results from each iterator of data emitted from the data source
        """
        result = await async_offline_stream_pipeline_runner(
            data_source=data_source,
            job_name=job_name,
            apply_rule=cls.apply_rule,
            rules=rules,
            multi_processing=multi_processing,
            processes=processes,
        )
        return result
