"""`models.py` 单元测试，对应 design/09_feature_checklist.md F0.3 与 F2.5.1。"""

from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from fund.models import (
    ActualOperation,
    FundProfile,
    LessonLearned,
    MarketPatternEntry,
    ProfileObservation,
    AnalysisArgument,
    AnalysisRecord,
    ApiErrorLogEntry,
    BullAlert,
    CrashRisk,
    PerformanceRecord,
    TradeDecision,
    WeeklyReview,
)


def _make_analysis_record() -> AnalysisRecord:
    return AnalysisRecord(
        execute_date=date(2026, 11, 8),
        fund_code="000001",
        fund_name="示例基金",
        buy_cost=1.234,
        hold_days=35,
        current_yield=0.12,
        base_profit_signal="卖出",
        early_sell_fee_judge="持有超过 30 天，无需豁免判断",
        bull_alert=BullAlert(
            is_surge=True,
            expected_gain="0.1~0.3",
            confidence=80,
            reason_list=["行业景气度上升"],
        ),
        crash_risk=CrashRisk(
            is_crash=False,
            escape_window="",
            prev_error_summary="",
            bad_factors=[],
        ),
        next_week_trend_text="预计震荡上行",
        analysis_argument=AnalysisArgument(
            stock_holding="持仓集中度正常",
            financial_report="财报符合预期",
            macro_economy="宏观环境中性",
            industry_news="行业新闻正面",
            bond_market="债市平稳",
        ),
        final_decision="止盈卖出",
        data_warning="",
    )


def test_analysis_record_valid_construction() -> None:
    record = _make_analysis_record()

    assert record.fund_code == "000001"
    assert record.bull_alert.confidence == 80


def test_analysis_record_round_trip_serialization() -> None:
    record = _make_analysis_record()

    dumped = record.model_dump_json()
    restored = AnalysisRecord.model_validate_json(dumped)

    assert restored == record


def test_bull_alert_confidence_out_of_range_raises() -> None:
    with pytest.raises(ValidationError):
        BullAlert(is_surge=True, expected_gain="0.1~0.3", confidence=101, reason_list=[])

    with pytest.raises(ValidationError):
        BullAlert(is_surge=True, expected_gain="0.1~0.3", confidence=-1, reason_list=[])


def test_analysis_record_invalid_final_decision_raises() -> None:
    data = _make_analysis_record().model_dump()
    data["final_decision"] = "不存在的决策"

    with pytest.raises(ValidationError):
        AnalysisRecord(**data)


def test_trade_decision_round_trip_serialization() -> None:
    decision = TradeDecision(
        decision_id="000001-2026-11-08-止盈",
        fund_code="000001",
        signal_date=date(2026, 11, 8),
        signal_type="止盈",
        trigger_condition="收益率达到 10%",
        executed=False,
        realized_return=None,
    )

    restored = TradeDecision.model_validate_json(decision.model_dump_json())

    assert restored == decision


def test_weekly_review_round_trip_serialization() -> None:
    review = WeeklyReview(
        review_week="2026-W45",
        total_predict=10,
        correct_rate=0.8,
        surge_warning_hit_rate=0.75,
        crash_warning_hit_rate=1.0,
        error_classification={"macro_miss": 1, "info_delay": 2},
        new_analysis_factors=["新增行业轮动因子"],
        prompt_optimize_content="增加宏观上下文权重",
        risk_threshold_adjust="置信度阈值维持 70",
        next_week_context="关注央行议息会议",
        data_warning="",
    )

    restored = WeeklyReview.model_validate_json(review.model_dump_json())

    assert restored == review


def test_performance_record_confidence_out_of_range_raises() -> None:
    with pytest.raises(ValidationError):
        PerformanceRecord(
            fund_code="000001",
            predict_date=date(2026, 11, 1),
            predict_return=0.05,
            real_return=0.03,
            error=-0.02,
            confidence=150,
            factor_list=[],
        )


def test_api_error_log_entry_round_trip_serialization() -> None:
    entry = ApiErrorLogEntry(
        timestamp=datetime(2026, 11, 8, 9, 30, 0),
        source="fund_data",
        stage="retry",
        status_code=503,
        detail="服务暂不可用",
    )

    restored = ApiErrorLogEntry.model_validate_json(entry.model_dump_json())

    assert restored == entry


def test_api_error_log_entry_invalid_stage_raises() -> None:
    with pytest.raises(ValidationError):
        ApiErrorLogEntry(
            timestamp=datetime(2026, 11, 8, 9, 30, 0),
            source="fund_data",
            stage="unknown_stage",
            status_code=None,
            detail="x",
        )


def test_actual_operation_round_trip_serialization() -> None:
    operation = ActualOperation(
        operation_id="000001-2026-11-08-买入",
        fund_code="000001",
        operation_date=date(2026, 11, 8),
        operation_type="买入",
        amount=10000.0,
        amount_unit="金额",
        price_or_nav=1.234,
        related_signal_id="000001-2026-11-08-止盈",
        note="跟随止盈信号加仓",
    )

    restored = ActualOperation.model_validate_json(operation.model_dump_json())

    assert restored == operation


def test_actual_operation_invalid_operation_type_raises() -> None:
    with pytest.raises(ValidationError):
        ActualOperation(
            operation_id="x",
            fund_code="000001",
            operation_date=date(2026, 11, 8),
            operation_type="不存在的操作",
            amount=1.0,
            amount_unit="金额",
            price_or_nav=1.0,
        )


def test_lesson_learned_round_trip_serialization() -> None:
    lesson = LessonLearned(
        lesson_id="L-2026W45-01",
        created_at=date(2026, 11, 8),
        source="weekly_review:2026-W45",
        category="macro_miss",
        trigger_pattern="央行超预期降息后持仓未及时加仓",
        lesson_text="降息周期应适度提高权益仓位",
        applicable_scope={"type": "market_wide", "value": ""},
        tags=["利率周期", "仓位管理"],
        confidence=70,
        status="active",
    )

    restored = LessonLearned.model_validate_json(lesson.model_dump_json())

    assert restored == lesson


def test_lesson_learned_confidence_out_of_range_raises() -> None:
    with pytest.raises(ValidationError):
        LessonLearned(
            lesson_id="L-2026W45-02",
            created_at=date(2026, 11, 8),
            source="weekly_review:2026-W45",
            category="macro_miss",
            trigger_pattern="x",
            lesson_text="x",
            applicable_scope={"type": "market_wide", "value": ""},
            confidence=200,
        )


def test_fund_profile_round_trip_serialization_with_observations() -> None:
    profile = FundProfile(
        fund_code="000001",
        fund_name="示例基金一号",
        manager_style="稳健成长风格",
        known_risk_factors=["重仓白酒，受消费政策影响大"],
        historical_behavior=[
            ProfileObservation(
                date=date(2026, 11, 7),
                context_summary="宏观中性，行业景气度上升",
                outcome_summary="净值上涨 0.5%",
            ),
            ProfileObservation(
                date=date(2026, 11, 8),
                context_summary="宏观中性，行业新闻正面",
                outcome_summary="净值上涨 0.3%",
            ),
        ],
        last_updated=date(2026, 11, 8),
    )

    restored = FundProfile.model_validate_json(profile.model_dump_json())

    assert restored == profile
    assert len(restored.historical_behavior) == 2


def test_market_pattern_entry_round_trip_serialization() -> None:
    entry = MarketPatternEntry(
        pattern_id="P-001",
        pattern_type="季节性",
        name="春季躁动",
        description="每年一季度市场风险偏好回升，中小盘成长股表现相对占优",
        historical_evidence="2005-2024 年 20 次中约 14 次应验",
        applicable_condition="每年 1-2 月",
        confidence_note="样本有限，仅供参考，不作为唯一决策依据",
        source="用户整理的历史复盘笔记",
    )

    restored = MarketPatternEntry.model_validate_json(entry.model_dump_json())

    assert restored == entry


def test_market_pattern_entry_invalid_pattern_type_raises() -> None:
    with pytest.raises(ValidationError):
        MarketPatternEntry(
            pattern_id="P-002",
            pattern_type="不存在的类型",
            name="x",
            description="x",
            historical_evidence="x",
            applicable_condition="x",
            confidence_note="x",
            source="x",
        )

