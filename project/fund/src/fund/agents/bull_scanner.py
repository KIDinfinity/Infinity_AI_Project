"""`bull_scanner.py`：Target2，短期暴涨机会预警。

详见 ../../../design/05_agents_skills_prompts.md。产出 `BullAlert`；`is_surge` /
是否最终推荐买入由 `rules.py::classify_bull_alert` 二次裁决，不单纯信任 LLM 给出
的 `confidence`/`expected_gain`。

当前阶段没有独立的"资金流向"数据源（见 design/01_directory_structure.md 只有
fund_info/stock_financial/macro_data/industry_news 四个 sources），`fund_flow_summary`
这里用 `fund_info` 的持仓数据近似代替，后续如果新增专门的资金流数据源，只需要在
`sources/` 新增文件并替换这里的参数来源，不需要改 prompt 模板。
"""

from __future__ import annotations

import json
from datetime import date
from typing import Callable

from .. import knowledge
from ..adapter import AdapterResult
from ..config import AppConfig
from ..llm import call_llm, load_prompt
from ..models import BullAlert
from ..rules import BASE_RULE_TEXT, cap_confidence_when_degraded, classify_bull_alert
from ._common import (
    collect_data_warning,
    parse_expected_gain,
    parse_llm_json_response,
    summarize_adapter_result,
)


def run(
    config: AppConfig,
    fund_code: str,
    candidate_pool: list[str],
    as_of: date,
    fund_info: AdapterResult,
    stock_financial: AdapterResult,
    industry_news: AdapterResult,
    call_llm_fn: Callable[[AppConfig, str], str] = call_llm,
) -> BullAlert:
    data_warning = collect_data_warning([fund_info, stock_financial, industry_news])
    knowledge_context = knowledge.get_knowledge_context(config, fund_code, as_of)

    prompt = load_prompt(
        "bull_scanner",
        fund_list=fund_code,
        candidate_pool=", ".join(candidate_pool) if candidate_pool else "（无）",
        position_detail=summarize_adapter_result(fund_info),
        financial_summary=summarize_adapter_result(stock_financial),
        news_summary=summarize_adapter_result(industry_news),
        fund_flow_summary=summarize_adapter_result(fund_info),
        base_rule_text=BASE_RULE_TEXT,
        knowledge_context=json.dumps(knowledge_context, ensure_ascii=False),
    )

    raw_response = call_llm_fn(config, prompt)
    parsed = parse_llm_json_response(raw_response)

    expected_gain_raw = parsed.get("expected_gain", "0")
    confidence_raw = parsed.get("confidence", 0)
    try:
        confidence = int(confidence_raw)
    except (TypeError, ValueError):
        confidence = 0
    confidence = max(0, min(100, confidence))

    reason_list = parsed.get("reason_list", [])
    if not isinstance(reason_list, list):
        reason_list = []
    reason_list = [str(reason) for reason in reason_list]
    if data_warning:
        reason_list.append(f"【数据缺失警告】{data_warning}")

    confidence = cap_confidence_when_degraded(confidence, data_warning, config.strategy)
    expected_gain_value = parse_expected_gain(expected_gain_raw)
    classification = classify_bull_alert(expected_gain_value, confidence, config.strategy)

    return BullAlert(
        is_surge=classification == "buy_recommend",
        expected_gain=str(expected_gain_raw),
        confidence=confidence,
        reason_list=reason_list,
    )
