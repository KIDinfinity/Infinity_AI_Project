"""`llm.py` 单元测试，对应 design/09_feature_checklist.md F4.1~F4.2。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund import llm
from fund.config import AppConfig


def test_call_llm_fake_provider_returns_fixed_placeholder(app_config: AppConfig) -> None:
    assert llm.call_llm(app_config, "任意 prompt") == "{}"


def test_call_llm_openai_provider_not_implemented(app_config: AppConfig) -> None:
    openai_config = app_config.model_copy(
        update={"llm": app_config.llm.model_copy(update={"provider": "openai"})}
    )
    with pytest.raises(NotImplementedError):
        llm.call_llm(openai_config, "任意 prompt")


def test_call_llm_unknown_provider_raises_value_error(app_config: AppConfig) -> None:
    unknown_config = app_config.model_copy(
        update={"llm": app_config.llm.model_copy(update={"provider": "unknown"})}
    )
    with pytest.raises(ValueError, match="不支持的 llm.provider"):
        llm.call_llm(unknown_config, "任意 prompt")


def test_load_prompt_renders_all_variables(tmp_data_root: Path) -> None:
    rendered = llm.load_prompt(
        "daily_analysis",
        fund_list="000001",
        position_detail="示例基金一号，持仓成本1.0",
        financial_summary="{}",
        macro_summary="{}",
        news_summary="{}",
        base_rule_text="Target1...",
        knowledge_context="{}",
    )

    assert "000001" in rendered
    assert "示例基金一号，持仓成本1.0" in rendered
    assert "Target1..." in rendered
    assert "{{" not in rendered  # 所有占位符都应该被替换


def test_load_prompt_missing_variable_raises_value_error(tmp_data_root: Path) -> None:
    with pytest.raises(ValueError, match="缺少变量"):
        llm.load_prompt("daily_analysis", fund_list="000001")


@pytest.mark.parametrize(
    "name",
    ["daily_analysis", "bull_scanner", "risk_alert", "weekly_improve"],
)
def test_all_prompt_templates_exist_and_have_required_vars_header(name: str) -> None:
    from fund.llm import _PROMPTS_DIR

    content = (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    assert content.startswith("<!-- required_vars:")
