"""`storage.py` 单元测试，对应 design/09_feature_checklist.md F0.4 与 F2.5.1。"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fund import storage
from fund.models import (
    ActualOperation,
    AnalysisArgument,
    AnalysisRecord,
    ApiErrorLogEntry,
    BullAlert,
    CrashRisk,
    FundProfile,
    LessonLearned,
    MarketPatternEntry,
    PerformanceRecord,
    ProfileObservation,
    TradeDecision,
    WeeklyReview,
)


def _make_analysis_record(execute_date: date, fund_code: str = "000001") -> AnalysisRecord:
    return AnalysisRecord(
        execute_date=execute_date,
        fund_code=fund_code,
        fund_name="示例基金",
        buy_cost=1.0,
        hold_days=40,
        current_yield=0.11,
        base_profit_signal="卖出",
        early_sell_fee_judge="持有超过 30 天，无需豁免判断",
        bull_alert=BullAlert(is_surge=False, expected_gain="0~0.1", confidence=50, reason_list=[]),
        crash_risk=CrashRisk(is_crash=False, escape_window="", prev_error_summary="", bad_factors=[]),
        next_week_trend_text="预计平稳",
        analysis_argument=AnalysisArgument(
            stock_holding="正常",
            financial_report="正常",
            macro_economy="正常",
            industry_news="正常",
            bond_market="正常",
        ),
        final_decision="止盈卖出",
        data_warning="",
    )


def test_save_and_load_daily_analysis_round_trip(tmp_data_root: Path) -> None:
    execute_date = date(2026, 11, 8)
    records = [
        _make_analysis_record(execute_date, "000001"),
        _make_analysis_record(execute_date, "000002"),
    ]

    saved_path = storage.save_daily_analysis(records)

    assert saved_path == tmp_data_root / "analysis_log" / "2026-11-08.json"
    loaded = storage.load_daily_analysis(execute_date)
    assert loaded == records


def test_load_daily_analysis_missing_file_returns_empty(tmp_data_root: Path) -> None:
    assert storage.load_daily_analysis(date(2099, 1, 1)) == []


def test_append_trade_decision_does_not_overwrite_existing_lines(tmp_data_root: Path) -> None:
    first = TradeDecision(
        decision_id="000001-2026-11-01-止盈",
        fund_code="000001",
        signal_date=date(2026, 11, 1),
        signal_type="止盈",
        trigger_condition="收益率达到 10%",
    )
    second = TradeDecision(
        decision_id="000002-2026-11-02-暴涨预警",
        fund_code="000002",
        signal_date=date(2026, 11, 2),
        signal_type="暴涨预警",
        trigger_condition="置信度达到 80",
    )

    storage.append_trade_decision(first)
    storage.append_trade_decision(second)

    loaded = storage.load_trade_decisions("2026-11")
    assert loaded == [first, second]


def test_save_weekly_review_writes_json_and_markdown(tmp_data_root: Path) -> None:
    review = WeeklyReview(
        review_week="2026-W45",
        total_predict=10,
        correct_rate=0.8,
        surge_warning_hit_rate=0.75,
        crash_warning_hit_rate=1.0,
        error_classification={"macro_miss": 1},
        new_analysis_factors=["新增因子"],
        prompt_optimize_content="优化建议",
        risk_threshold_adjust="维持阈值",
        next_week_context="关注会议",
        data_warning="",
    )

    json_path, md_path = storage.save_weekly_review(review)

    assert json_path == tmp_data_root / "weekly_review_log" / "2026-W45-review.json"
    assert md_path == tmp_data_root / "weekly_review_log" / "2026-W45-review.md"
    restored = WeeklyReview.model_validate_json(json_path.read_text(encoding="utf-8"))
    assert restored == review
    assert "2026-W45" in md_path.read_text(encoding="utf-8")


def test_append_performance_record_does_not_overwrite_existing_lines(tmp_data_root: Path) -> None:
    first = PerformanceRecord(
        fund_code="000001",
        predict_date=date(2026, 11, 1),
        predict_return=0.05,
        real_return=0.04,
        error=-0.01,
        confidence=80,
        factor_list=["因子A"],
    )
    second = PerformanceRecord(
        fund_code="000002",
        predict_date=date(2026, 11, 2),
        predict_return=0.03,
        real_return=0.03,
        error=0.0,
        confidence=70,
        factor_list=["因子B"],
    )

    storage.append_performance_record(first)
    storage.append_performance_record(second)

    loaded = storage.load_performance_records(2026)
    assert loaded == [first, second]


def test_append_api_error_log_appends_without_overwriting(tmp_data_root: Path) -> None:
    first = ApiErrorLogEntry(
        timestamp=datetime(2026, 11, 8, 9, 0, 0),
        source="fund_data",
        stage="first_try",
        status_code=500,
        detail="服务器错误",
    )
    second = ApiErrorLogEntry(
        timestamp=datetime(2026, 11, 8, 9, 1, 0),
        source="fund_data",
        stage="retry",
        status_code=503,
        detail="重试仍失败",
    )

    storage.append_api_error_log(first)
    storage.append_api_error_log(second)

    loaded = storage.load_api_error_log()
    assert loaded == [first, second]


def test_append_and_load_actual_operations_by_fund_code(tmp_data_root: Path) -> None:
    first = ActualOperation(
        operation_id="000001-2026-11-01-买入",
        fund_code="000001",
        operation_date=date(2026, 11, 1),
        operation_type="买入",
        amount=10000.0,
        amount_unit="金额",
        price_or_nav=1.1,
    )
    second = ActualOperation(
        operation_id="000002-2026-11-02-卖出",
        fund_code="000002",
        operation_date=date(2026, 11, 2),
        operation_type="卖出",
        amount=5000.0,
        amount_unit="金额",
        price_or_nav=2.2,
    )

    storage.append_actual_operation(first)
    storage.append_actual_operation(second)

    assert storage.load_actual_operations() == [first, second]
    assert storage.load_actual_operations(fund_code="000001") == [first]


def test_append_lesson_does_not_overwrite_existing_lines(tmp_data_root: Path) -> None:
    first = LessonLearned(
        lesson_id="L-2026W45-01",
        created_at=date(2026, 11, 8),
        source="weekly_review:2026-W45",
        category="macro_miss",
        trigger_pattern="x",
        lesson_text="x",
        applicable_scope={"type": "market_wide", "value": ""},
        confidence=70,
    )
    second = LessonLearned(
        lesson_id="L-2026W45-02",
        created_at=date(2026, 11, 8),
        source="weekly_review:2026-W45",
        category="positive_pattern",
        trigger_pattern="y",
        lesson_text="y",
        applicable_scope={"type": "fund_code", "value": "000001"},
        confidence=80,
    )

    storage.append_lesson(first)
    storage.append_lesson(second)

    assert storage.load_lessons() == [first, second]


def test_save_and_load_fund_profile_round_trip(tmp_data_root: Path) -> None:
    profile = FundProfile(
        fund_code="000001",
        fund_name="示例基金一号",
        manager_style="稳健成长",
        known_risk_factors=["重仓白酒"],
        historical_behavior=[
            ProfileObservation(
                date=date(2026, 11, 8),
                context_summary="宏观中性",
                outcome_summary="净值上涨 0.3%",
            )
        ],
        last_updated=date(2026, 11, 8),
    )

    storage.save_fund_profile(profile)

    assert storage.load_fund_profile("000001") == profile


def test_load_fund_profile_missing_returns_none(tmp_data_root: Path) -> None:
    assert storage.load_fund_profile("999999") is None


def test_load_market_patterns_reads_seed_file(tmp_data_root: Path) -> None:
    directory = tmp_data_root / "knowledge_base" / "market_patterns"
    directory.mkdir(parents=True, exist_ok=True)
    entry = MarketPatternEntry(
        pattern_id="P-001",
        pattern_type="季节性",
        name="春季躁动",
        description="一季度市场风险偏好回升",
        historical_evidence="2005-2024 年多次应验",
        applicable_condition="每年 1-2 月",
        confidence_note="样本有限，仅供参考",
        source="用户整理笔记",
    )
    (directory / "patterns.json").write_text(
        f"[{entry.model_dump_json()}]", encoding="utf-8"
    )

    assert storage.load_market_patterns() == [entry]


def test_load_market_patterns_missing_file_returns_empty(tmp_data_root: Path) -> None:
    assert storage.load_market_patterns() == []

