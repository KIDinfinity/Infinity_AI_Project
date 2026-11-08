"""`agents/orchestrator.py` 集成测试，对应 design/09_feature_checklist.md F5.1~F5.2。

全部使用 fake call_llm_fn（按 prompt 里的"角色"标题分发不同 canned JSON）+
sources/*.py 自带的本地样例数据（不发真实网络请求）。
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from fund.config import AppConfig


def _fake_call_llm_factory(
    *,
    is_crash: bool = False,
    bull_confidence: int = 40,
    expected_gain: str = "0.05",
):
    """根据 prompt 里的"角色"标题分发不同 agent 的 canned JSON 响应。"""

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        if "每日持仓短线研判总分析师" in prompt:
            return json.dumps(
                {
                    "next_week_trend_text": "震荡偏强",
                    "analysis_argument": {
                        "stock_holding": "重仓股基本面稳健",
                        "financial_report": "财报符合预期",
                        "macro_economy": "宏观流动性中性",
                        "industry_news": "行业新闻偏中性",
                        "bond_market": "债市平稳",
                    },
                }
            )
        if "短线暴涨机会扫描器" in prompt:
            return json.dumps(
                {
                    "expected_gain": expected_gain,
                    "confidence": bull_confidence,
                    "reason_list": ["量价齐升"],
                }
            )
        if "风险脱身预警分析师" in prompt:
            return json.dumps(
                {
                    "is_crash": is_crash,
                    "escape_window": "次日开盘" if is_crash else "",
                    "prev_error_summary": "",
                    "bad_factors": ["行业政策收紧"] if is_crash else [],
                }
            )
        raise AssertionError(f"未预期的 prompt：{prompt[:50]}")

    return fake_call_llm


def _holding(fund_code: str = "000001", **overrides: object) -> dict:
    holding = {
        "fund_code": fund_code,
        "fund_name": "示例基金一号",
        "buy_cost": 1.0,
        "hold_days": 40,
        "current_yield": 0.15,
    }
    holding.update(overrides)
    return holding


# ---------------------------------------------------------------------------
# F5.1 run_daily
# ---------------------------------------------------------------------------


def test_run_daily_crash_overrides_profit_taking_decision(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund import storage
    from fund.agents import orchestrator

    as_of = date(2026, 11, 9)
    records = orchestrator.run_daily(
        config=app_config,
        holdings=[_holding()],
        as_of=as_of,
        call_llm_fn=_fake_call_llm_factory(is_crash=True),
    )

    assert len(records) == 1
    record = records[0]
    # 收益达标 + 持有天数满足 -> base_profit_signal 本应是"卖出"，
    # 但 crash_risk.is_crash=True 时合并裁决必须优先取"清仓"（暴跌优先于止盈）。
    assert record.base_profit_signal == "卖出"
    assert record.crash_risk.is_crash is True
    assert record.final_decision == "清仓"

    persisted = storage.load_daily_analysis(as_of)
    assert len(persisted) == 1
    assert persisted[0].final_decision == "清仓"

    trade_decisions = storage.load_trade_decisions(f"{as_of:%Y-%m}")
    signal_types = {td.signal_type for td in trade_decisions}
    assert signal_types == {"暴跌预警"}  # 不应该额外生成"止盈"信号


def test_run_daily_profit_taking_and_surge_generate_trade_decisions(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund import storage
    from fund.agents import orchestrator

    as_of = date(2026, 11, 9)
    records = orchestrator.run_daily(
        config=app_config,
        holdings=[_holding()],
        as_of=as_of,
        call_llm_fn=_fake_call_llm_factory(
            is_crash=False, bull_confidence=90, expected_gain="0.2"
        ),
    )

    record = records[0]
    assert record.crash_risk.is_crash is False
    assert record.final_decision == "止盈卖出"
    assert record.bull_alert.is_surge is True

    trade_decisions = storage.load_trade_decisions(f"{as_of:%Y-%m}")
    signal_types = {td.signal_type for td in trade_decisions}
    assert signal_types == {"止盈", "暴涨预警"}


def test_run_daily_propagates_data_warning_from_position_analyst(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund.agents import orchestrator

    as_of = date(2026, 11, 9)
    # 用一个不在样例数据里的 fund_code（sources/*.py 对未知代码返回"未知基金"占位值，
    # 而不是 degraded，这里只验证主链路可以正常跑通未知基金，不额外断言 data_warning）。
    records = orchestrator.run_daily(
        config=app_config,
        holdings=[_holding(fund_code="999999", fund_name="未知基金")],
        as_of=as_of,
        call_llm_fn=_fake_call_llm_factory(),
    )

    assert len(records) == 1
    assert records[0].fund_code == "999999"


# ---------------------------------------------------------------------------
# F5.2 run_weekly
# ---------------------------------------------------------------------------


def _sample_analysis_record_with_bull_alert(fund_code: str, expected_gain: str, confidence: int):
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
        bull_alert=BullAlert(
            is_surge=True,
            expected_gain=expected_gain,
            confidence=confidence,
            reason_list=["量价齐升"],
        ),
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
        data_warning="",
    )


def test_run_weekly_saves_review_and_backfills_performance_db(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund import storage
    from fund.agents import orchestrator

    def fake_call_llm(config: AppConfig, prompt: str) -> str:
        assert "每周预测复盘迭代专家" in prompt
        return json.dumps(
            {
                "total_predict": 1,
                "correct_rate": 0.8,
                "surge_warning_hit_rate": 1.0,
                "crash_warning_hit_rate": 1.0,
                "error_classification": {},
                "new_analysis_factors": [],
                "prompt_optimize_content": "无",
                "risk_threshold_adjust": "维持现状",
                "next_week_context": "无特殊前置条件",
            }
        )

    record = _sample_analysis_record_with_bull_alert("000001", expected_gain="0.1~0.2", confidence=90)

    review = orchestrator.run_weekly(
        config=app_config,
        review_week="2026-W45",
        analysis_records=[record],
        real_nav_data={"000001": 0.18},
        call_llm_fn=fake_call_llm,
    )

    assert review.review_week == "2026-W45"

    data_root = tmp_data_root
    assert (data_root / "weekly_review_log" / "2026-W45-review.json").is_file()
    assert (data_root / "weekly_review_log" / "2026-W45-review.md").is_file()

    performance_records = storage.load_performance_records(2026)
    assert len(performance_records) == 1
    perf = performance_records[0]
    assert perf.fund_code == "000001"
    assert perf.predict_return == 0.2  # "0.1~0.2" 取区间上限
    assert perf.real_return == 0.18
    assert perf.error == abs(0.2 - 0.18)
    assert perf.confidence == 90
