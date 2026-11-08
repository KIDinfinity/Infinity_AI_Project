"""纯函数规则引擎，Target1/2/3 的硬约束。

详见 ../../design/05_agents_skills_prompts.md 和 ../../design/02_config.md。
不依赖网络、不依赖 LLM，输入输出都是基本类型/pydantic 模型。

设计文档未完全细化之处，本文件做出以下明确约定：

- `classify_bull_alert`：`confidence_threshold` 是硬性门槛（低于门槛一律只标观察）；
  `surge_upper_target` 作为"暴涨预期上限"，超出该上限视为预测过于激进、可信度不足，
  同样只标观察而不直接推荐买入，避免过度信任 LLM 给出的极端预测值。
- `resolve_final_decision`：这是 Target1/Target3 的合并裁决辅助函数，只处理"止盈信号
  vs 暴跌风险"两条自动化路径的优先级（`crash_priority_over_profit` 恒为 True，暴跌风险
  检测到时直接清仓，优先级高于止盈）。`"减仓"` 不由本规则引擎自动产出，留给上层
  agent 结合 LLM 论证手动判断，规则引擎只保证"暴跌优先于止盈"这一条硬约束。
"""

from __future__ import annotations

from typing import Literal

from fund.config import StrategyConfig
from fund.models import CrashRisk

BASE_RULE_TEXT = """\
Target1 基础止盈规则：收益达到 strategy.base_profit_rate 触发卖出信号，默认持有 \
≥ strategy.min_hold_days 天；若短期收益能覆盖提前赎回手续费，可豁免最低持有天数限制。
Target2 短期暴涨机会预警：预判短期涨幅超过阈值时需提供多条可核验支撑理由，置信度低于 \
strategy.confidence_threshold 仅标记观察，不生成买入推荐。
Target3 暴跌脱身风险预警：原有看多逻辑失效或出现突发利空时，输出脱身窗口与误判原因， \
风险优先级高于止盈规则。
Target4 每日持仓研判 + 每周迭代闭环：每日覆盖全部持仓做分析并预测下周走势；每周复盘预测 \
误差、提炼新增分析因子、沉淀为可复用经验。
系统边界：只输出分析结论和信号，不自动对接券商/基金软件下单；不编造不存在的数据，接口失败 \
时必须标注 data_warning。
"""


def check_base_profit(
    current_yield: float,
    hold_days: int,
    fee_covered_by_gain: bool,
    cfg: StrategyConfig,
) -> tuple[Literal["持有", "卖出"], str]:
    """Target1：基础止盈判断，含 30 天（`min_hold_days`）豁免逻辑。"""
    if current_yield < cfg.base_profit_rate:
        return ("持有", f"当前收益率 {current_yield:.2%} 未达到基础止盈目标 {cfg.base_profit_rate:.2%}")

    if hold_days >= cfg.min_hold_days:
        return (
            "卖出",
            f"已达到止盈目标 {cfg.base_profit_rate:.2%} 且持有 {hold_days} 天满足最低持有天数 {cfg.min_hold_days} 天",
        )

    if fee_covered_by_gain:
        return (
            "卖出",
            f"持有 {hold_days} 天未满 {cfg.min_hold_days} 天，但收益可覆盖提前赎回手续费，予以豁免卖出",
        )

    return (
        "持有",
        f"持有 {hold_days} 天未满 {cfg.min_hold_days} 天，且收益不足以覆盖提前赎回手续费，继续持有",
    )


def classify_bull_alert(
    expected_gain: float, confidence: int, cfg: StrategyConfig
) -> Literal["buy_recommend", "watch_only"]:
    """Target2：暴涨预警二次裁决，不单纯信任 LLM 的 confidence/expected_gain 输出。"""
    if confidence < cfg.confidence_threshold:
        return "watch_only"
    if expected_gain <= 0 or expected_gain > cfg.surge_upper_target:
        return "watch_only"
    return "buy_recommend"


def crash_priority_over_profit() -> bool:
    """Target3：恒定返回 True，显式建模"风险优先级 > 止盈规则"这条规则。"""
    return True


def cap_confidence_when_degraded(
    confidence: int, data_warning: str, cfg: StrategyConfig
) -> int:
    """数据源降级时强制封顶 `confidence`，避免输出"置信度拉满的强推荐"。

    见 design/06_daily_weekly_flow.md「关键约束」：`data_warning` 非空时，
    `confidence` 上限封顶为 `confidence_threshold - 1`，即自动降为
    `classify_bull_alert` 判定下的"观察"（watch_only），不直接推荐买入。
    """
    if not data_warning:
        return confidence
    return min(confidence, cfg.confidence_threshold - 1)


def resolve_final_decision(
    base_profit_signal: Literal["持有", "卖出"],
    crash_risk: CrashRisk,
) -> Literal["持有", "清仓", "止盈卖出"]:
    """合并裁决：暴跌风险优先于止盈信号。"""
    if crash_risk.is_crash and crash_priority_over_profit():
        return "清仓"
    if base_profit_signal == "卖出":
        return "止盈卖出"
    return "持有"
