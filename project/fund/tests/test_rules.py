"""`rules.py` 单元测试，对应 design/09_feature_checklist.md F3.1~F3.3。"""

from __future__ import annotations

import pytest

from fund import rules
from fund.config import StrategyConfig
from fund.models import CrashRisk


@pytest.fixture()
def strategy_cfg() -> StrategyConfig:
    return StrategyConfig(
        base_profit_rate=0.10,
        min_hold_days=30,
        confidence_threshold=70,
        surge_upper_target=0.30,
    )


# ---------------------------------------------------------------------------
# F3.1 check_base_profit
# ---------------------------------------------------------------------------


def test_check_base_profit_below_target_holds(strategy_cfg: StrategyConfig) -> None:
    signal, reason = rules.check_base_profit(
        current_yield=0.05, hold_days=40, fee_covered_by_gain=True, cfg=strategy_cfg
    )
    assert signal == "持有"
    assert "未达到基础止盈目标" in reason


def test_check_base_profit_meets_target_and_min_hold_days_sells(
    strategy_cfg: StrategyConfig,
) -> None:
    signal, reason = rules.check_base_profit(
        current_yield=0.10, hold_days=30, fee_covered_by_gain=False, cfg=strategy_cfg
    )
    assert signal == "卖出"
    assert "满足最低持有天数" in reason


def test_check_base_profit_under_min_hold_days_with_fee_covered_sells(
    strategy_cfg: StrategyConfig,
) -> None:
    signal, reason = rules.check_base_profit(
        current_yield=0.15, hold_days=10, fee_covered_by_gain=True, cfg=strategy_cfg
    )
    assert signal == "卖出"
    assert "豁免卖出" in reason


def test_check_base_profit_under_min_hold_days_without_fee_covered_holds(
    strategy_cfg: StrategyConfig,
) -> None:
    signal, reason = rules.check_base_profit(
        current_yield=0.15, hold_days=10, fee_covered_by_gain=False, cfg=strategy_cfg
    )
    assert signal == "持有"
    assert "不足以覆盖提前赎回手续费" in reason


# ---------------------------------------------------------------------------
# F3.2 classify_bull_alert
# ---------------------------------------------------------------------------


def test_classify_bull_alert_low_confidence_is_watch_only(
    strategy_cfg: StrategyConfig,
) -> None:
    assert rules.classify_bull_alert(0.20, 69, strategy_cfg) == "watch_only"


def test_classify_bull_alert_confidence_at_threshold_with_valid_gain_recommends_buy(
    strategy_cfg: StrategyConfig,
) -> None:
    assert rules.classify_bull_alert(0.20, 70, strategy_cfg) == "buy_recommend"


def test_classify_bull_alert_gain_at_upper_target_recommends_buy(
    strategy_cfg: StrategyConfig,
) -> None:
    assert rules.classify_bull_alert(0.30, 90, strategy_cfg) == "buy_recommend"


def test_classify_bull_alert_gain_above_upper_target_is_watch_only(
    strategy_cfg: StrategyConfig,
) -> None:
    assert rules.classify_bull_alert(0.31, 90, strategy_cfg) == "watch_only"


def test_classify_bull_alert_non_positive_gain_is_watch_only(
    strategy_cfg: StrategyConfig,
) -> None:
    assert rules.classify_bull_alert(0.0, 90, strategy_cfg) == "watch_only"
    assert rules.classify_bull_alert(-0.05, 90, strategy_cfg) == "watch_only"


# ---------------------------------------------------------------------------
# F5.1 cap_confidence_when_degraded
# ---------------------------------------------------------------------------


def test_cap_confidence_when_degraded_caps_to_threshold_minus_one(
    strategy_cfg: StrategyConfig,
) -> None:
    capped = rules.cap_confidence_when_degraded(95, "stock_financial 数据源降级", strategy_cfg)
    assert capped == strategy_cfg.confidence_threshold - 1


def test_cap_confidence_when_degraded_keeps_lower_confidence_untouched(
    strategy_cfg: StrategyConfig,
) -> None:
    low_confidence = strategy_cfg.confidence_threshold - 5
    capped = rules.cap_confidence_when_degraded(low_confidence, "数据源降级", strategy_cfg)
    assert capped == low_confidence


def test_cap_confidence_when_degraded_no_warning_is_noop(strategy_cfg: StrategyConfig) -> None:
    assert rules.cap_confidence_when_degraded(95, "", strategy_cfg) == 95


# ---------------------------------------------------------------------------
# F3.3 crash_priority_over_profit + resolve_final_decision
# ---------------------------------------------------------------------------


def test_crash_priority_over_profit_is_always_true() -> None:
    assert rules.crash_priority_over_profit() is True


def _crash_risk(is_crash: bool) -> CrashRisk:
    return CrashRisk(
        is_crash=is_crash,
        escape_window="次日开盘",
        prev_error_summary="",
        bad_factors=["行业政策收紧"] if is_crash else [],
    )


def test_resolve_final_decision_crash_overrides_profit_signal() -> None:
    assert rules.resolve_final_decision("卖出", _crash_risk(True)) == "清仓"
    assert rules.resolve_final_decision("持有", _crash_risk(True)) == "清仓"


def test_resolve_final_decision_no_crash_follows_profit_signal() -> None:
    assert rules.resolve_final_decision("卖出", _crash_risk(False)) == "止盈卖出"
    assert rules.resolve_final_decision("持有", _crash_risk(False)) == "持有"
