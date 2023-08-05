from collections import defaultdict
from typing import List

from spotlight.core.common.base import Base
from spotlight.core.common.enum import Status
from spotlight.core.pipeline.model.rule import RuleResult


class Metadata(Base):
    """
    This is a model that contains the metadata from running a set of rules.
    """

    results: List[RuleResult]
    succeeded: int
    failed: int
    warned: int
    total_rules: int

    @classmethod
    def from_rule_results(cls, results: List[RuleResult]):
        counts = defaultdict(int)
        for result in results:
            counts[result.status] += 1

        return cls(
            results=results,
            succeeded=counts[Status.SUCCESS.value],
            failed=counts[Status.FAILURE.value],
            warned=counts[Status.WARNING.value],
            total_rules=len(results),
        )


class PipelineResult(Base):
    """
    This is a model of the data quality pipeline result
    """

    name: str
    status: Status
    start_time: int
    end_time: int
    metadata: Metadata

    @classmethod
    def build_result(
        cls, name: str, start_time: int, end_time: int, results: List[RuleResult]
    ) -> "PipelineResult":
        metadata = Metadata.from_rule_results(results)
        return cls(
            name=name,
            status=cls.get_status(metadata),
            start_time=start_time,
            end_time=end_time,
            metadata=metadata,
        )

    @staticmethod
    def get_status(metadata: Metadata) -> Status:
        if metadata.failed > 0:
            return Status.FAILURE
        elif metadata.warned > 0:
            return Status.WARNING
        else:
            return Status.SUCCESS
