"""`position_analyst.py`：Target1 + Target4，单只基金的持仓研判。

详见 ../../../design/05_agents_skills_prompts.md。产出字典不含 `bull_alert` /
`crash_risk` 子字段（分别由 `bull_scanner.py` / `risk_alert.py` 产出），由
`agents/orchestrator.py`（Phase 5）合并成完整的 `AnalysisRecord`。
"""

from __future__ import annotations

import json
from datetime import date
from typing import Callable

from .. import knowledge
from ..adapter import AdapterResult
from ..config import AppConfig
from ..llm import call_llm, load_prompt
from ..models import AnalysisArgument, ProfileObservation
from ..rules import BASE_RULE_TEXT, check_base_profit
from ._common import collect_data_warning, parse_llm_json_response, summarize_adapter_result


def run(
    config: AppConfig,
    fund_code: str,
    fund_name: str,
    buy_cost: float,
    hold_days: int,
    current_yield: float,
    as_of: date,
    fund_info: AdapterResult,
    stock_financial: AdapterResult,
    macro_data: AdapterResult,
    industry_news: AdapterResult,
    call_llm_fn: Callable[[AppConfig, str], str] = call_llm,
) -> dict:
    """产出单只基金的持仓研判草稿（不含 `bull_alert`/`crash_risk`）。"""
    data_warning = collect_data_warning([fund_info, stock_financial, macro_data, industry_news])

    # 简化判定：当前收益已达到止盈线即视为足以覆盖提前赎回手续费
    # （提前赎回手续费相对基础止盈幅度通常很小，设计文档未给出精确公式，这里采用保守近似）。
    fee_covered_by_gain = current_yield >= config.strategy.base_profit_rate
    base_profit_signal, early_sell_fee_judge = check_base_profit(
        current_yield=current_yield,
        hold_days=hold_days,
        fee_covered_by_gain=fee_covered_by_gain,
        cfg=config.strategy,
    )

    knowledge_context = knowledge.get_knowledge_context(config, fund_code, as_of)

    prompt = load_prompt(
        "daily_analysis",
        fund_list=fund_code,
        position_detail=(
            f"{fund_name}（{fund_code}），持仓成本 {buy_cost}，"
            f"持有 {hold_days} 天，当前收益率 {current_yield:.2%}"
        ),
        financial_summary=summarize_adapter_result(stock_financial),
        macro_summary=summarize_adapter_result(macro_data),
        news_summary=summarize_adapter_result(industry_news),
        base_rule_text=BASE_RULE_TEXT,
        knowledge_context=json.dumps(knowledge_context, ensure_ascii=False),
    )

    raw_response = call_llm_fn(config, prompt)
    parsed = parse_llm_json_response(raw_response)

    next_week_trend_text = parsed.get("next_week_trend_text", "")
    argument = parsed.get("analysis_argument")
    if not isinstance(argument, dict):
        argument = {}
    analysis_argument = AnalysisArgument(
        stock_holding=argument.get("stock_holding", ""),
        financial_report=argument.get("financial_report", ""),
        macro_economy=argument.get("macro_economy", ""),
        industry_news=argument.get("industry_news", ""),
        bond_market=argument.get("bond_market", ""),
    )

    observation = ProfileObservation(
        date=as_of,
        context_summary=f"止盈信号={base_profit_signal}；{early_sell_fee_judge}",
        outcome_summary=next_week_trend_text,
    )
    knowledge.upsert_fund_profile(fund_code, observation, fund_name=fund_name)

    return {
        "execute_date": as_of,
        "fund_code": fund_code,
        "fund_name": fund_name,
        "buy_cost": buy_cost,
        "hold_days": hold_days,
        "current_yield": current_yield,
        "base_profit_signal": base_profit_signal,
        "early_sell_fee_judge": early_sell_fee_judge,
        "next_week_trend_text": next_week_trend_text,
        "analysis_argument": analysis_argument,
        "data_warning": data_warning,
    }
