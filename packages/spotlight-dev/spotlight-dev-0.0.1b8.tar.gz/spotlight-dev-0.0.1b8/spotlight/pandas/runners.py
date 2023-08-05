import logging
import duckdb
import pandas as pd

from spotlight.core.common.date.function import current_timestamp
from spotlight.core.pipeline.execution.rule import SQLRule, AbstractCustomCodeRule
from spotlight.core.pipeline.model.rule import RuleResult
from spotlight.pandas.__util import build_rule_result

logger = logging.getLogger(__name__)


def pandas_sql_rule_runner(data: pd.DataFrame, rule: SQLRule) -> RuleResult:
    """
    Runs the sql rule on the data.

    Args:
        data (pd.DataFrame): The data being tested
        rule (SQLRule): The rule being applied to the data

    Result:
        RuleResult: The result of the rule
    """
    logger.debug(f"Running pandas sql rule {rule.name}")
    query = f"""
        SELECT *
        FROM data
        WHERE {rule.predicate}
    """
    start_time = current_timestamp()
    result = duckdb.query(query).to_df()
    end_time = current_timestamp()
    logger.debug(f"Pandas sql rule {rule.name} completed")
    result = build_rule_result(rule, start_time, end_time, data, result)
    return result


def pandas_custom_code_rule_runner(
    data: pd.DataFrame, rule: AbstractCustomCodeRule
) -> RuleResult:
    """
    Runs the custom code rule on the data.

    Args:
        data (pd.DataFrame): The data being tested
        rule (AbstractCustomCodeRule): The rule being applied to the data

    Result:
        RuleResult: The result of the rule
    """
    logger.debug(f"Running pandas custom code rule {rule.name}")
    start_time = current_timestamp()
    result = rule.test(data)
    end_time = current_timestamp()
    result = build_rule_result(rule, start_time, end_time, data, result)
    logger.debug(f"Pandas custom code rule {rule.name} completed")
    return result
