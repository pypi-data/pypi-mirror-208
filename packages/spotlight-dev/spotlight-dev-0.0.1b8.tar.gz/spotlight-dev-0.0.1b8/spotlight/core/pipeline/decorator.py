from typing import Any, Type, Callable

from spotlight.core.pipeline.abstract import AbstractPipeline
from spotlight.core.pipeline.execution.rule import AbstractRule
from spotlight.core.pipeline.execution.synchronous import ApplyRule
from spotlight.core.pipeline.model.rule import RuleResult


def pipeline(
    apply_rule: ApplyRule = None,
    *,
    name: str = "Unnamed",
) -> Callable[[Any], Type[AbstractPipeline]]:
    """
    This is a decorator to create a plugin from the apply_rule method

    Args:
        apply_rule (Callable[[Any, Any], RuleResult]): The apply rule method for a plugin
        name (str): Name of the plugin
    """

    def wrap(fxn):
        @classmethod
        def _apply_rule(cls, data: Any, rule: AbstractRule) -> RuleResult:
            return fxn(data, rule)

        new_pipeline = type(
            name,
            (AbstractPipeline,),
            {"apply_rule": _apply_rule},
        )
        return new_pipeline

    if apply_rule is None:
        return wrap

    return wrap(apply_rule)
