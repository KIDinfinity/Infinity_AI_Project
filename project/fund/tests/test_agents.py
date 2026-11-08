"""`agents/*.py` 单元测试，对应 design/09_feature_checklist.md F4.3~F4.6。

全部使用 fake call_llm_fn + fake 数据，不发真实网络/LLM 请求。
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from fund.adapter import AdapterResult
from fund.config import AppConfig


def _ok_result(data: dict, data_warning: str = "") -> AdapterResult:
    return AdapterResult(ok=True, data=data, degraded=False, data_warning=data_warning)


def _degraded_result(data_warning: str) -> AdapterResult:
    return AdapterResult(ok=False, data=None, degraded=True, data_warning=data_warning)


# ---------------------------------------------------------------------------
# F4.3 position_analyst
# ---------------------------------------------------------------------------


def test_position_analyst_run_happy_path(tmp_data_root: Path, app_config: AppConfig) -> None:
    from fund import knowledge
    from fund.agents import position_analyst

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        assert "000001" in prompt
        return json.dumps(
            {
                "next_week_trend_text": "周一小幅震荡，周五受财报催化上涨",
                "analysis_argument": {
                    "stock_holding": "持仓稳定",
                    "financial_report": "业绩符合预期",
                    "macro_economy": "宏观中性",
                    "industry_news": "行业政策平稳",
                    "bond_market": "利率平稳",
                },
            }
        )

    result = position_analyst.run(
        config=app_config,
        fund_code="000001",
        fund_name="示例基金一号",
        buy_cost=1.0,
        hold_days=45,
        current_yield=0.12,
        as_of=date(2026, 11, 8),
        fund_info=_ok_result({"nav": 1.12}),
        stock_financial=_ok_result({"revenue": 100}),
        macro_data=_ok_result({"cpi": 2.1}),
        industry_news=_ok_result({"headline": "行业平稳"}),
        call_llm_fn=fake_call_llm,
    )

    assert result["fund_code"] == "000001"
    assert result["base_profit_signal"] == "卖出"
    assert "满足最低持有天数" in result["early_sell_fee_judge"]
    assert result["next_week_trend_text"] == "周一小幅震荡，周五受财报催化上涨"
    assert result["analysis_argument"].stock_holding == "持仓稳定"
    assert result["data_warning"] == ""

    # F4.3 额外断言：knowledge_base 对应文件被正确写入
    profile = knowledge.get_fund_profile("000001")
    assert profile is not None
    assert profile.fund_name == "示例基金一号"
    assert len(profile.historical_behavior) == 1
    assert profile.historical_behavior[0].outcome_summary == "周一小幅震荡，周五受财报催化上涨"


def test_position_analyst_run_propagates_data_warning(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import position_analyst

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return "{}"

    result = position_analyst.run(
        config=app_config,
        fund_code="000002",
        fund_name="示例基金二号",
        buy_cost=2.0,
        hold_days=5,
        current_yield=0.02,
        as_of=date(2026, 11, 8),
        fund_info=_ok_result({"nav": 2.1}),
        stock_financial=_degraded_result("stock_financial 数据源降级"),
        macro_data=_ok_result({"cpi": 2.1}),
        industry_news=_degraded_result("industry_news 数据源降级"),
        call_llm_fn=fake_call_llm,
    )

    assert "stock_financial 数据源降级" in result["data_warning"]
    assert "industry_news 数据源降级" in result["data_warning"]
    assert result["base_profit_signal"] == "持有"


def test_position_analyst_run_malformed_llm_response_degrades_gracefully(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import position_analyst

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return "不是合法 JSON"

    result = position_analyst.run(
        config=app_config,
        fund_code="000003",
        fund_name="示例基金三号",
        buy_cost=1.0,
        hold_days=45,
        current_yield=0.12,
        as_of=date(2026, 11, 8),
        fund_info=_ok_result({}),
        stock_financial=_ok_result({}),
        macro_data=_ok_result({}),
        industry_news=_ok_result({}),
        call_llm_fn=fake_call_llm,
    )

    assert result["next_week_trend_text"] == ""
    assert result["analysis_argument"].stock_holding == ""


# ---------------------------------------------------------------------------
# F4.4 bull_scanner
# ---------------------------------------------------------------------------


def test_bull_scanner_run_buy_recommend_when_confidence_and_gain_valid(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import bull_scanner

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return json.dumps(
            {
                "expected_gain": "0.1~0.2",
                "confidence": 85,
                "reason_list": ["业绩超预期", "产业政策利好"],
            }
        )

    alert = bull_scanner.run(
        config=app_config,
        fund_code="000001",
        candidate_pool=["000004", "000005"],
        as_of=date(2026, 11, 8),
        fund_info=_ok_result({"position": ["贵州茅台"]}),
        stock_financial=_ok_result({"revenue": 100}),
        industry_news=_ok_result({"headline": "行业政策利好"}),
        call_llm_fn=fake_call_llm,
    )

    assert alert.is_surge is True
    assert alert.confidence == 85
    assert alert.expected_gain == "0.1~0.2"
    assert alert.reason_list == ["业绩超预期", "产业政策利好"]


def test_bull_scanner_run_low_confidence_is_watch_only(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import bull_scanner

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return json.dumps({"expected_gain": "0.2", "confidence": 50, "reason_list": ["理由1"]})

    alert = bull_scanner.run(
        config=app_config,
        fund_code="000001",
        candidate_pool=[],
        as_of=date(2026, 11, 8),
        fund_info=_ok_result({}),
        stock_financial=_ok_result({}),
        industry_news=_ok_result({}),
        call_llm_fn=fake_call_llm,
    )

    assert alert.is_surge is False
    assert alert.confidence == 50


def test_bull_scanner_run_appends_data_warning_to_reason_list(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import bull_scanner

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return json.dumps({"expected_gain": "0.2", "confidence": 90, "reason_list": ["理由1"]})

    alert = bull_scanner.run(
        config=app_config,
        fund_code="000001",
        candidate_pool=[],
        as_of=date(2026, 11, 8),
        fund_info=_ok_result({}),
        stock_financial=_degraded_result("stock_financial 数据源降级"),
        industry_news=_ok_result({}),
        call_llm_fn=fake_call_llm,
    )

    assert any("数据缺失警告" in reason for reason in alert.reason_list)
    # F4.4 新增约束（design/06_daily_weekly_flow.md）：data_warning 非空时 confidence
    # 必须封顶到 confidence_threshold - 1，不允许输出"置信度拉满的强推荐"。
    assert alert.confidence == app_config.strategy.confidence_threshold - 1
    assert alert.is_surge is False


# ---------------------------------------------------------------------------
# F4.5 risk_alert
# ---------------------------------------------------------------------------


def test_risk_alert_run_detects_crash(tmp_data_root: Path, app_config: AppConfig) -> None:
    from fund.agents import risk_alert

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        assert "000001" in prompt
        return json.dumps(
            {
                "is_crash": True,
                "escape_window": "建议2日内脱身",
                "prev_error_summary": "此前低估了行业政策收紧的影响",
                "bad_factors": ["行业政策收紧", "重仓个股业绩暴雷"],
            }
        )

    crash_risk = risk_alert.run(
        config=app_config,
        fund_code="000001",
        as_of=date(2026, 11, 8),
        prev_analysis_summary="此前判断持续看多",
        stock_financial=_ok_result({"revenue": 100}),
        macro_data=_ok_result({"cpi": 2.1}),
        industry_news=_ok_result({"headline": "行业政策收紧"}),
        call_llm_fn=fake_call_llm,
    )

    assert crash_risk.is_crash is True
    assert crash_risk.escape_window == "建议2日内脱身"
    assert crash_risk.bad_factors == ["行业政策收紧", "重仓个股业绩暴雷"]


def test_risk_alert_run_no_crash_and_data_warning_appended(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import risk_alert

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return json.dumps(
            {
                "is_crash": False,
                "escape_window": "",
                "prev_error_summary": "无前期误判",
                "bad_factors": [],
            }
        )

    crash_risk = risk_alert.run(
        config=app_config,
        fund_code="000001",
        as_of=date(2026, 11, 8),
        prev_analysis_summary="",
        stock_financial=_degraded_result("stock_financial 数据源降级"),
        macro_data=_ok_result({}),
        industry_news=_ok_result({}),
        call_llm_fn=fake_call_llm,
    )

    assert crash_risk.is_crash is False
    assert any("数据缺失警告" in factor for factor in crash_risk.bad_factors)


# ---------------------------------------------------------------------------
# F4.6 weekly_reviewer
# ---------------------------------------------------------------------------


def _sample_analysis_record(fund_code: str, data_warning: str = "") -> "AnalysisRecord":
    from fund.models import AnalysisArgument, AnalysisRecord, BullAlert, CrashRisk

    return AnalysisRecord(
        execute_date=date(2026, 11, 2),
        fund_code=fund_code,
        fund_name=f"示例基金{fund_code}",
        buy_cost=1.0,
        hold_days=40,
        current_yield=0.12,
        base_profit_signal="卖出",
        early_sell_fee_judge="满足最低持有天数",
        bull_alert=BullAlert(is_surge=False, expected_gain="0", confidence=50, reason_list=[]),
        crash_risk=CrashRisk(
            is_crash=False, escape_window="", prev_error_summary="", bad_factors=[]
        ),
        next_week_trend_text="震荡上行",
        analysis_argument=AnalysisArgument(
            stock_holding="",
            financial_report="",
            macro_economy="",
            industry_news="",
            bond_market="",
        ),
        final_decision="止盈卖出",
        data_warning=data_warning,
    )


def test_weekly_reviewer_run_produces_review_and_appends_lessons(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund import knowledge
    from fund.agents import weekly_reviewer

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        assert "2026-W45" in prompt
        return json.dumps(
            {
                "total_predict": 10,
                "correct_rate": 0.8,
                "surge_warning_hit_rate": 0.75,
                "crash_warning_hit_rate": 1.0,
                "error_classification": {"macro_miss": 2},
                "new_analysis_factors": ["应纳入央行议息会议前瞻"],
                "prompt_optimize_content": "daily_analysis 增加央行议息日历",
                "risk_threshold_adjust": "维持 confidence_threshold=70",
                "next_week_context": "关注央行议息会议",
            }
        )

    review = weekly_reviewer.run(
        config=app_config,
        review_week="2026-W45",
        analysis_records=[_sample_analysis_record("000001")],
        trade_decisions=[],
        real_nav_data={"000001": 1.25},
        call_llm_fn=fake_call_llm,
    )

    assert review.review_week == "2026-W45"
    assert review.total_predict == 10
    assert review.correct_rate == 0.8
    assert review.new_analysis_factors == ["应纳入央行议息会议前瞻"]
    assert review.data_warning == ""

    # F4.6 额外断言：knowledge_base 对应文件被正确写入
    lessons = knowledge.query_lessons()
    assert len(lessons) == 1
    assert lessons[0].lesson_text == "应纳入央行议息会议前瞻"
    assert lessons[0].lesson_id == "L-2026-W45-01"


def test_weekly_reviewer_run_clamps_invalid_rates_and_propagates_warning(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import weekly_reviewer

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        return json.dumps(
            {
                "total_predict": "not-a-number",
                "correct_rate": 1.5,  # 超出 [0,1]，应被夹到 1.0
                "surge_warning_hit_rate": -0.2,  # 应被夹到 0.0
                "crash_warning_hit_rate": 0.5,
                "new_analysis_factors": [],
            }
        )

    review = weekly_reviewer.run(
        config=app_config,
        review_week="2026-W46",
        analysis_records=[_sample_analysis_record("000002", data_warning="industry_news 数据源降级")],
        trade_decisions=[],
        real_nav_data={},
        call_llm_fn=fake_call_llm,
    )

    assert review.total_predict == 1  # 非法值兜底为 len(analysis_records)
    assert review.correct_rate == 1.0
    assert review.surge_warning_hit_rate == 0.0
    assert review.data_warning == "industry_news 数据源降级"
    assert review.new_analysis_factors == []
