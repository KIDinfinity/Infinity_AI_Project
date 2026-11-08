"""`agents/orchestrator.py`：Phase 5 编排落盘，对应 Daily/Weekly Button。

详见 ../../../design/06_daily_weekly_flow.md。`run_daily` 串联 Phase 2~4 的
sources/agents/rules，合并成完整 `AnalysisRecord` 落盘，必要时写 `trade_decision`；
`run_weekly` 调用 `weekly_reviewer` 落盘 `weekly_review_log` 并回填 `performance_db`。

设计文档未覆盖之处，本文件做出以下明确简化（与此前各阶段"做出文档化简化"的处理方式
一致）：

- `config.yaml`/`storage.py` 均未定义"持仓快照"模型，只有用户手工记录的
  `actual_operations` 流水。`run_daily` 本身仍接受调用方显式传入的 `holdings`
  参数（每项至少含 `fund_code`/`buy_cost`/`hold_days`/`current_yield`；
  `fund_name`/`industries` 可选），保持函数本身简单可测；真正给 `cli.py fund daily`
  （无参数）使用的"当前持仓清单"由 `build_holdings_from_operations(...)` 按加权
  平均成本法从 `actual_operations` 重放得到（份额归零后再次买入视为重新建仓，
  `hold_days` 从新建仓日起算）。
- `risk_alert` 需要的 `prev_analysis_summary` 取"`as_of` 前一天"的 `analysis_log`
  中同一只基金的 `next_week_trend_text`（没有则传空字符串），不做更复杂的历史回溯。
- `run_weekly` 本身仍接受调用方显式传入的 `review_week`/`analysis_records`/
  `trade_decisions`/`real_nav_data`，保持函数本身简单可测；真正给 `cli.py fund weekly`
  使用时，`review_week` 缺省由 `compute_default_week(today)` 计算"当前自然周的上一周"，
  `analysis_records`/`trade_decisions` 由 `load_week_analysis_records`/
  `load_week_trade_decisions` 从 `storage.py` 按周读取拼接。`real_nav_data` 目前没有
  历史净值数据源可用，`cli.py` 侧默认传空 dict——`performance_db` 回填会相应留空，
  待 F7.2（Optional，真实数据源接入）补上历史净值后才能产出真实数值，这是已知的
  文档化限制，不在本阶段臆造虚假净值数字。
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Callable

from .. import storage
from ..adapter import AdapterResult
from ..config import AppConfig
from ..llm import call_llm
from ..models import AnalysisRecord, PerformanceRecord, TradeDecision, WeeklyReview
from ..rules import resolve_final_decision
from ..sources.fund_info import fetch_fund_info
from ..sources.industry_news import fetch_industry_news
from ..sources.macro_data import fetch_macro_data
from ..sources.stock_financial import fetch_stock_financial
from . import bull_scanner, position_analyst, risk_alert, weekly_reviewer
from ._common import parse_expected_gain


def _generate_decision_id(fund_code: str, signal_date: date) -> str:
    return f"TD-{fund_code}-{signal_date.isoformat()}-{uuid.uuid4().hex[:8]}"


def _extract_position_stocks(fund_info: AdapterResult, fund_code: str) -> list[str]:
    if fund_info.data is None:
        return []
    fund_entry = fund_info.data.get("data", {}).get(fund_code)
    if not isinstance(fund_entry, dict):
        return []
    position = fund_entry.get("position", [])
    return [str(stock) for stock in position] if isinstance(position, list) else []


def build_holdings_from_operations(config: AppConfig, as_of: date) -> list[dict]:
    """从 `actual_operations` 流水按加权平均成本法重建"当前持仓清单"。

    供 `cli.py fund daily`（不手工传参时）使用：按 `operation_date` 顺序重放每只
    基金的买入/卖出，维护份额与加权平均成本；份额归零后再次买入视为重新建仓，
    `hold_days` 从新建仓日起算；已清仓（份额为 0）的基金不纳入结果。
    """
    operations = storage.load_actual_operations()
    by_fund: dict[str, list] = {}
    for op in operations:
        by_fund.setdefault(op.fund_code, []).append(op)

    holdings: list[dict] = []
    for fund_code, ops in by_fund.items():
        ops_sorted = sorted(ops, key=lambda op: op.operation_date)
        total_shares = 0.0
        total_cost = 0.0
        position_start_date: date | None = None

        for op in ops_sorted:
            if op.operation_type in ("买入", "加仓"):
                shares = op.amount if op.amount_unit == "份额" else op.amount / op.price_or_nav
                cost = op.amount * op.price_or_nav if op.amount_unit == "份额" else op.amount
                if total_shares <= 1e-9:
                    position_start_date = op.operation_date
                total_shares += shares
                total_cost += cost
            else:  # 卖出/减仓
                if total_shares <= 1e-9:
                    continue  # 没有持仓却记了卖出，视为数据异常，忽略这条不影响后续重放
                shares_sold = op.amount if op.amount_unit == "份额" else op.amount / op.price_or_nav
                shares_sold = min(shares_sold, total_shares)
                total_cost -= (shares_sold / total_shares) * total_cost
                total_shares -= shares_sold

        if total_shares <= 1e-9:
            continue

        buy_cost = total_cost / total_shares
        hold_days = (as_of - position_start_date).days if position_start_date else 0

        fund_info_result = fetch_fund_info(config, [fund_code])
        fund_entry: dict = {}
        if fund_info_result.data:
            fund_entry = fund_info_result.data.get("data", {}).get(fund_code) or {}
        nav = fund_entry.get("nav")
        fund_name = fund_entry.get("fund_name") or fund_code
        current_yield = (nav - buy_cost) / buy_cost if nav else 0.0

        holdings.append(
            {
                "fund_code": fund_code,
                "fund_name": fund_name,
                "buy_cost": buy_cost,
                "hold_days": hold_days,
                "current_yield": current_yield,
            }
        )

    return holdings


def compute_default_week(today: date) -> str:
    """返回"当前自然周的上一周"，格式 `YYYY-Www`（ISO 周），供 `fund weekly` 缺省使用。"""
    iso_year, iso_week, _ = today.isocalendar()
    if iso_week == 1:
        # ISO 周规则：每年 12-28 必然落在该年最后一个 ISO 周内，借它反推上一年的周号。
        anchor = date(iso_year - 1, 12, 28)
        prev_iso_year, prev_iso_week, _ = anchor.isocalendar()
        return f"{prev_iso_year}-W{prev_iso_week:02d}"
    return f"{iso_year}-W{iso_week - 1:02d}"


def _week_date_range(review_week: str) -> tuple[date, date]:
    """把 `YYYY-Www` 解析为该 ISO 周 [周一, 周日] 的日期范围。"""
    year_part, week_part = review_week.split("-W")
    monday = date.fromisocalendar(int(year_part), int(week_part), 1)
    sunday = date.fromisocalendar(int(year_part), int(week_part), 7)
    return monday, sunday


def load_week_analysis_records(review_week: str) -> list[AnalysisRecord]:
    """读取指定 ISO 周全部 `analysis_log`（逐日读取后拼接）。"""
    monday, sunday = _week_date_range(review_week)
    records: list[AnalysisRecord] = []
    current = monday
    while current <= sunday:
        records.extend(storage.load_daily_analysis(current))
        current += timedelta(days=1)
    return records


def load_week_trade_decisions(review_week: str) -> list[TradeDecision]:
    """读取指定 ISO 周全部 `trade_decision`（按涉及到的年月读取后按日期范围过滤）。"""
    monday, sunday = _week_date_range(review_week)
    year_months: set[str] = set()
    current = monday
    while current <= sunday:
        year_months.add(f"{current:%Y-%m}")
        current += timedelta(days=1)

    decisions: list[TradeDecision] = []
    for year_month in year_months:
        decisions.extend(
            decision
            for decision in storage.load_trade_decisions(year_month)
            if monday <= decision.signal_date <= sunday
        )
    return decisions


def _load_prev_analysis_summary(fund_code: str, as_of: date) -> str:
    prev_records = storage.load_daily_analysis(as_of - timedelta(days=1))
    for record in prev_records:
        if record.fund_code == fund_code:
            return record.next_week_trend_text
    return ""


def run_daily(
    config: AppConfig,
    holdings: list[dict],
    as_of: date | None = None,
    candidate_pool: list[str] | None = None,
    call_llm_fn: Callable[[AppConfig, str], str] = call_llm,
) -> list[AnalysisRecord]:
    """逐只基金跑 position_analyst + bull_scanner + risk_alert，合并落盘。

    合并裁决规则：若 `crash_risk.is_crash` 为真，`final_decision` 固定取
    `rules.resolve_final_decision` 的"清仓"分支，优先级高于止盈信号（见
    design/06_daily_weekly_flow.md「关键约束」）。
    """
    effective_as_of = as_of or date.today()
    resolved_candidate_pool = candidate_pool or []

    records: list[AnalysisRecord] = []
    for holding in holdings:
        fund_code = holding["fund_code"]
        fund_name = holding.get("fund_name", fund_code)
        buy_cost = holding["buy_cost"]
        hold_days = holding["hold_days"]
        current_yield = holding["current_yield"]
        industries = holding.get("industries", [])

        fund_info_result = fetch_fund_info(config, [fund_code])
        position_stocks = _extract_position_stocks(fund_info_result, fund_code)
        stock_financial_result = fetch_stock_financial(config, position_stocks)
        macro_result = fetch_macro_data(config)
        industry_news_result = fetch_industry_news(config, industries)

        partial = position_analyst.run(
            config=config,
            fund_code=fund_code,
            fund_name=fund_name,
            buy_cost=buy_cost,
            hold_days=hold_days,
            current_yield=current_yield,
            as_of=effective_as_of,
            fund_info=fund_info_result,
            stock_financial=stock_financial_result,
            macro_data=macro_result,
            industry_news=industry_news_result,
            call_llm_fn=call_llm_fn,
        )

        bull_alert = bull_scanner.run(
            config=config,
            fund_code=fund_code,
            candidate_pool=resolved_candidate_pool,
            as_of=effective_as_of,
            fund_info=fund_info_result,
            stock_financial=stock_financial_result,
            industry_news=industry_news_result,
            call_llm_fn=call_llm_fn,
        )

        prev_analysis_summary = _load_prev_analysis_summary(fund_code, effective_as_of)
        crash_risk = risk_alert.run(
            config=config,
            fund_code=fund_code,
            as_of=effective_as_of,
            prev_analysis_summary=prev_analysis_summary,
            stock_financial=stock_financial_result,
            macro_data=macro_result,
            industry_news=industry_news_result,
            call_llm_fn=call_llm_fn,
        )

        final_decision = resolve_final_decision(partial["base_profit_signal"], crash_risk)

        record = AnalysisRecord(
            **partial,
            bull_alert=bull_alert,
            crash_risk=crash_risk,
            final_decision=final_decision,
        )
        records.append(record)

        if crash_risk.is_crash:
            storage.append_trade_decision(
                TradeDecision(
                    decision_id=_generate_decision_id(fund_code, effective_as_of),
                    fund_code=fund_code,
                    signal_date=effective_as_of,
                    signal_type="暴跌预警",
                    trigger_condition="；".join(crash_risk.bad_factors) or "风险模型判定暴跌",
                )
            )
        elif final_decision == "止盈卖出":
            storage.append_trade_decision(
                TradeDecision(
                    decision_id=_generate_decision_id(fund_code, effective_as_of),
                    fund_code=fund_code,
                    signal_date=effective_as_of,
                    signal_type="止盈",
                    trigger_condition=partial["early_sell_fee_judge"],
                )
            )

        if bull_alert.is_surge:
            storage.append_trade_decision(
                TradeDecision(
                    decision_id=_generate_decision_id(fund_code, effective_as_of),
                    fund_code=fund_code,
                    signal_date=effective_as_of,
                    signal_type="暴涨预警",
                    trigger_condition="；".join(bull_alert.reason_list) or "暴涨模型判定推荐买入",
                )
            )

    if records:
        storage.save_daily_analysis(records)

    return records


def run_weekly(
    config: AppConfig,
    review_week: str,
    analysis_records: list[AnalysisRecord],
    real_nav_data: dict[str, float],
    trade_decisions: list[TradeDecision] | None = None,
    call_llm_fn: Callable[[AppConfig, str], str] = call_llm,
) -> WeeklyReview:
    """调用 `weekly_reviewer` 生成复盘，落盘 `weekly_review_log`，并回填 `performance_db`。"""
    resolved_trade_decisions = trade_decisions or []

    review = weekly_reviewer.run(
        config=config,
        review_week=review_week,
        analysis_records=analysis_records,
        trade_decisions=resolved_trade_decisions,
        real_nav_data=real_nav_data,
        call_llm_fn=call_llm_fn,
    )

    storage.save_weekly_review(review)

    for record in analysis_records:
        if record.fund_code not in real_nav_data:
            continue
        predict_return = parse_expected_gain(record.bull_alert.expected_gain)
        real_return = real_nav_data[record.fund_code]
        storage.append_performance_record(
            PerformanceRecord(
                fund_code=record.fund_code,
                predict_date=record.execute_date,
                predict_return=predict_return,
                real_return=real_return,
                error=abs(predict_return - real_return),
                confidence=record.bull_alert.confidence,
                factor_list=record.bull_alert.reason_list,
            )
        )

    return review
