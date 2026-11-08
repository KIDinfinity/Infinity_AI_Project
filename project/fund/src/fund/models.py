"""全部 pydantic 数据模型。

详细字段说明与落盘格式见 ../../design/03_data_model.md。

本文件实现第 1~6 节全部模型：第 1~5 节（`AnalysisRecord`、`TradeDecision`、
`WeeklyReview`、`PerformanceRecord`、`ApiErrorLogEntry`）+ 第 6 节知识库/真实
操作模型（`ActualOperation`、`LessonLearned`、`FundProfile`/`ProfileObservation`、
`MarketPatternEntry`）。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class BullAlert(BaseModel):
    is_surge: bool
    expected_gain: str
    confidence: int = Field(ge=0, le=100)
    reason_list: list[str] = Field(default_factory=list)


class CrashRisk(BaseModel):
    is_crash: bool
    escape_window: str
    prev_error_summary: str
    bad_factors: list[str] = Field(default_factory=list)


class AnalysisArgument(BaseModel):
    stock_holding: str
    financial_report: str
    macro_economy: str
    industry_news: str
    bond_market: str


class AnalysisRecord(BaseModel):
    execute_date: date
    fund_code: str
    fund_name: str
    buy_cost: float
    hold_days: int
    current_yield: float
    base_profit_signal: Literal["持有", "卖出"]
    early_sell_fee_judge: str
    bull_alert: BullAlert
    crash_risk: CrashRisk
    next_week_trend_text: str
    analysis_argument: AnalysisArgument
    final_decision: Literal["持有", "减仓", "清仓", "止盈卖出"]
    data_warning: str = ""


class TradeDecision(BaseModel):
    decision_id: str
    fund_code: str
    signal_date: date
    signal_type: Literal["止盈", "暴涨预警", "暴跌预警"]
    trigger_condition: str
    executed: bool = False
    realized_return: float | None = None


class WeeklyReview(BaseModel):
    review_week: str
    total_predict: int
    correct_rate: float
    surge_warning_hit_rate: float
    crash_warning_hit_rate: float
    error_classification: dict[str, int] = Field(default_factory=dict)
    new_analysis_factors: list[str] = Field(default_factory=list)
    prompt_optimize_content: str
    risk_threshold_adjust: str
    next_week_context: str
    data_warning: str = ""


class PerformanceRecord(BaseModel):
    fund_code: str
    predict_date: date
    predict_return: float
    real_return: float
    error: float
    confidence: int = Field(ge=0, le=100)
    factor_list: list[str] = Field(default_factory=list)


class ApiErrorLogEntry(BaseModel):
    timestamp: datetime
    source: str
    stage: Literal["first_try", "retry", "switch_backup", "reduce_payload", "give_up"]
    status_code: int | None = None
    detail: str


class ActualOperation(BaseModel):
    operation_id: str
    fund_code: str
    operation_date: date
    operation_type: Literal["买入", "卖出", "加仓", "减仓"]
    amount: float
    amount_unit: Literal["金额", "份额"]
    price_or_nav: float
    related_signal_id: str | None = None
    note: str = ""


class LessonLearned(BaseModel):
    lesson_id: str
    created_at: date
    source: str
    category: str
    trigger_pattern: str
    lesson_text: str
    applicable_scope: dict
    tags: list[str] = Field(default_factory=list)
    confidence: int = Field(ge=0, le=100)
    status: Literal["active", "deprecated"] = "active"


class ProfileObservation(BaseModel):
    date: date
    context_summary: str
    outcome_summary: str


class FundProfile(BaseModel):
    fund_code: str
    fund_name: str
    manager_style: str = ""
    known_risk_factors: list[str] = Field(default_factory=list)
    historical_behavior: list[ProfileObservation] = Field(default_factory=list)
    last_updated: date


class MarketPatternEntry(BaseModel):
    pattern_id: str
    pattern_type: Literal["利率周期", "政策周期", "季节性", "经济周期", "其他"]
    name: str
    description: str
    historical_evidence: str
    applicable_condition: str
    confidence_note: str
    source: str
