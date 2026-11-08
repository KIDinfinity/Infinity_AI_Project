"""`sources/*.py` 单元测试，对应 design/09_feature_checklist.md F2.1~F2.4。"""

from __future__ import annotations

from fund.config import AppConfig
from fund.sources.fund_info import fetch_fund_info
from fund.sources.industry_news import fetch_industry_news
from fund.sources.macro_data import fetch_macro_data
from fund.sources.stock_financial import fetch_stock_financial


def test_fetch_fund_info_default_sample_data(app_config: AppConfig) -> None:
    result = fetch_fund_info(app_config, ["000001", "999999"])

    assert result.ok is True
    assert result.degraded is False
    assert result.data["data"]["000001"]["fund_name"] == "示例基金一号"
    assert result.data["data"]["999999"]["fund_name"] == "未知基金"


def test_fetch_fund_info_param_assembly_with_fake_request_fn(
    app_config: AppConfig, fake_request_fn_factory
) -> None:
    request_fn = fake_request_fn_factory([200])

    fetch_fund_info(app_config, ["000001", "000002"], request_fn=request_fn)

    endpoint, params, _headers = request_fn.calls[0]
    assert endpoint == app_config.api.fund_data.endpoint
    assert params == {"codes": ["000001", "000002"]}


def test_fetch_fund_info_degraded_flag_propagates(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    request_fn = fake_request_fn_factory([401])

    result = fetch_fund_info(
        app_config, ["000001"], request_fn=request_fn, sleep_fn=recording_sleep_fn
    )

    assert result.ok is False
    assert result.degraded is True
    assert result.data_warning != ""


def test_fetch_stock_financial_default_sample_data(app_config: AppConfig) -> None:
    result = fetch_stock_financial(app_config, ["贵州茅台", "未知个股"])

    assert result.ok is True
    assert result.data["data"]["贵州茅台"]["revenue_growth"] == 0.15
    assert result.data["data"]["未知个股"]["revenue_growth"] is None


def test_fetch_stock_financial_param_assembly(
    app_config: AppConfig, fake_request_fn_factory
) -> None:
    request_fn = fake_request_fn_factory([200])

    fetch_stock_financial(app_config, ["贵州茅台"], request_fn=request_fn)

    _endpoint, params, _headers = request_fn.calls[0]
    assert params == {"codes": ["贵州茅台"]}


def test_fetch_macro_data_default_sample_data(app_config: AppConfig) -> None:
    result = fetch_macro_data(app_config)

    assert result.ok is True
    assert result.data["data"]["interest_rate"] == 0.0335


def test_fetch_macro_data_custom_indicators_param_assembly(
    app_config: AppConfig, fake_request_fn_factory
) -> None:
    request_fn = fake_request_fn_factory([200])

    fetch_macro_data(app_config, indicators=["cpi"], request_fn=request_fn)

    _endpoint, params, _headers = request_fn.calls[0]
    assert params == {"indicators": ["cpi"]}


def test_fetch_industry_news_default_sample_data(app_config: AppConfig) -> None:
    result = fetch_industry_news(app_config, ["白酒", "未知行业"])

    assert result.ok is True
    assert result.data["data"]["白酒"] == ["消费复苏预期升温，白酒板块估值修复"]
    assert result.data["data"]["未知行业"] == []


def test_fetch_industry_news_degraded_flag_propagates_after_backup(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    # financial_news 的 backup_endpoints 为空列表，重试耗尽后应直接失败降级
    request_fn = fake_request_fn_factory([500, 500, 500, 500, 500])

    result = fetch_industry_news(
        app_config, ["白酒"], request_fn=request_fn, sleep_fn=recording_sleep_fn
    )

    assert result.ok is False
    assert result.degraded is True
