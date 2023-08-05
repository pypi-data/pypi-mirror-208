from typing import Optional, List

from spotlight.api.rule.model import RuleResponse
from spotlight.core.common.enum import Severity, ThresholdType
from spotlight.core.pipeline.execution.rule.abstract import AbstractRule
from spotlight.core.pipeline.execution.rule.enum import RuleTypes


class SQLRule(AbstractRule):
    def __init__(
        self,
        name: str,
        predicate: str,
        threshold: float,
        threshold_type: ThresholdType,
        severity: Severity,
        sampling_fields: Optional[List[str]] = None,
    ):
        self._name = name
        self.predicate = predicate
        self._threshold = threshold
        self._threshold_type = threshold_type
        self._severity = severity
        self._sampling_fields = sampling_fields

    @property
    def name(self) -> str:
        return self._name

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def threshold_type(self) -> ThresholdType:
        return self._threshold_type

    @property
    def severity(self) -> Severity:
        return self._severity

    @property
    def sampling_fields(self) -> Optional[List[str]]:
        return self._sampling_fields

    def to_dict(self):
        props = self._properties()
        props.update({"type": RuleTypes.SQL.value, "predicate": self.predicate})
        return props

    @classmethod
    def from_rule_response(cls, rule: RuleResponse) -> "SQLRule":
        return cls(
            name=rule.name,
            predicate=rule.predicate,
            threshold=rule.threshold,
            threshold_type=rule.threshold_type,
            severity=Severity(rule.severity),
            sampling_fields=rule.sampling_fields,
        )
