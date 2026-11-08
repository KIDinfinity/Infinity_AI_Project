"""`risk_alert.py`：Target3，暴跌脱身风险预警。

详见 ../../../design/05_agents_skills_prompts.md。产出 `CrashRisk`；风险优先级高于
止盈规则由 `rules.py::crash_priority_over_profit` 保证，这里只负责产出判断本身，
合并裁决在 `agents/orchestrator.py`（Phase 5）里用 `rules.py::resolve_final_decision`
完成。

当前阶段没有独立的"债市"数据源，`bond_rate_summary` 暂用 `macro_data`（覆盖
interest_rate/exchange_rate/cpi）近似代替，后续如需精细化债市数据，在 `sources/`
新增文件即可，不需要改这里的签名/prompt 模板。

`prev_analysis_summary` 由调用方（`orchestrator.py`）传入，通常来自上一次分析记录
的看多论证摘要，用于让 LLM 判断"上一轮预测错在哪里"。
"""

from __future__ import annotations

import json
from datetime import date
from typing import Callable

from .. import knowledge
from ..adapter import AdapterResult
from ..config import AppConfig
from ..llm import call_llm, load_prompt
from ..models import CrashRisk
from ..rules import BASE_RULE_TEXT
from ._common import collect_data_warning, parse_llm_json_response, summarize_adapter_result


def run(
    config: AppConfig,
    fund_code: str,
    as_of: date,
    prev_analysis_summary: str,
    stock_financial: AdapterResult,
    macro_data: AdapterResult,
    industry_news: AdapterResult,
    call_llm_fn: Callable[[AppConfig, str], str] = call_llm,
) -> CrashRisk:
    data_warning = collect_data_warning([stock_financial, macro_data, industry_news])
    knowledge_context = knowledge.get_knowledge_context(config, fund_code, as_of)

    prompt = load_prompt(
        "risk_alert",
        fund_code=fund_code,
        prev_analysis_summary=prev_analysis_summary or "无前期分析记录",
        financial_summary=summarize_adapter_result(stock_financial),
        macro_summary=summarize_adapter_result(macro_data),
        news_summary=summarize_adapter_result(industry_news),
        bond_rate_summary=summarize_adapter_result(macro_data),
        base_rule_text=BASE_RULE_TEXT,
        knowledge_context=json.dumps(knowledge_context, ensure_ascii=False),
    )

    raw_response = call_llm_fn(config, prompt)
    parsed = parse_llm_json_response(raw_response)

    is_crash = bool(parsed.get("is_crash", False))
    escape_window = str(parsed.get("escape_window", ""))
    prev_error_summary = str(parsed.get("prev_error_summary", ""))

    bad_factors = parsed.get("bad_factors", [])
    if not isinstance(bad_factors, list):
        bad_factors = []
    bad_factors = [str(factor) for factor in bad_factors]
    if data_warning:
        bad_factors.append(f"【数据缺失警告】{data_warning}")

    return CrashRisk(
        is_crash=is_crash,
        escape_window=escape_window,
        prev_error_summary=prev_error_summary,
        bad_factors=bad_factors,
    )
