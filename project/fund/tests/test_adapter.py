"""`adapter.py` 单元测试，对应 design/09_feature_checklist.md F1.1~F1.4。"""

from __future__ import annotations

import httpx
import pytest

from fund import storage
from fund.adapter import call_with_adapter
from fund.config import AppConfig


def test_success_first_try_not_degraded(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    request_fn = fake_request_fn_factory([200])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is True
    assert result.data == {"value": "ok"}
    assert result.degraded is False
    assert result.data_warning == ""
    assert recording_sleep_fn.calls == []
    assert storage.load_api_error_log() == []


def test_401_fails_without_retry_or_backup(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    request_fn = fake_request_fn_factory([401])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is False
    assert result.degraded is True
    assert "鉴权失败" in result.data_warning
    assert len(request_fn.calls) == 1  # 不重试、不切换备用
    assert recording_sleep_fn.calls == []

    error_log = storage.load_api_error_log()
    assert len(error_log) == 1
    assert error_log[0].stage == "give_up"
    assert error_log[0].status_code == 401


def test_403_fails_without_retry_or_backup(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    request_fn = fake_request_fn_factory([403])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is False
    assert len(request_fn.calls) == 1


def test_429_retries_twice_then_succeeds(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    request_fn = fake_request_fn_factory([429, 429, 200])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is True
    assert result.degraded is False
    assert len(request_fn.calls) == 3
    # rate_limit_sleep=5, backoff_factor=2 -> 5*2^0, 5*2^1
    assert recording_sleep_fn.calls == [5, 10]


def test_5xx_retry_exhausted_then_switch_backup_succeeds(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    # retry_max=3：主地址第一次 + 3 次重试全部 500（共 4 次调用），随后切换备用成功
    request_fn = fake_request_fn_factory([500, 500, 500, 500, 200])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is True
    assert result.degraded is True
    assert "备用" in result.data_warning
    assert len(request_fn.calls) == 5
    assert request_fn.calls[-1][0] == "https://backup.example.com/api/fund"

    error_log = storage.load_api_error_log()
    assert len(error_log) == 4  # 主地址 4 次失败各记一条日志


def test_all_endpoints_exhausted_returns_degraded_failure(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    # 主地址 1 个备用地址，共 2 个地址，每个地址 1(首次)+3(重试) = 4 次全部 500
    responses = [500] * 8
    request_fn = fake_request_fn_factory(responses)

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is False
    assert result.degraded is True
    assert len(request_fn.calls) == 8

    error_log = storage.load_api_error_log()
    assert error_log[-1].stage == "give_up"
    assert error_log[-1].status_code is None


def test_timeout_retries_then_succeeds(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    request_fn = fake_request_fn_factory(
        [httpx.ConnectError("连接失败"), httpx.ReadTimeout("超时"), 200]
    )

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is True
    assert len(request_fn.calls) == 3
    assert recording_sleep_fn.calls == [5, 10]


def test_format_error_triggers_payload_reduce_then_succeeds(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    # 第一次 200 但 body 非法 JSON -> 触发精简 payload；精简后第二次 200 合法
    request_fn = fake_request_fn_factory([(200, None), 200])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001", "000002"], "extra_fields": ["x"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is True
    assert result.degraded is True
    assert "精简参数" in result.data_warning
    assert len(request_fn.calls) == 2

    second_call_params = request_fn.calls[1][1]
    assert second_call_params["codes"] == ["000001"]
    assert "extra_fields" not in second_call_params


def test_format_error_reduce_fails_then_switch_backup_succeeds(
    app_config: AppConfig, fake_request_fn_factory, recording_sleep_fn
) -> None:
    # 精简一次后仍失败（第二次仍是非法 JSON）-> 切换备用地址成功
    request_fn = fake_request_fn_factory([(200, None), (200, None), 200])

    result = call_with_adapter(
        source="fund_data",
        params={"codes": ["000001", "000002"]},
        request_fn=request_fn,
        config=app_config,
        sleep_fn=recording_sleep_fn,
    )

    assert result.ok is True
    assert result.degraded is True
    assert len(request_fn.calls) == 3
    assert request_fn.calls[-1][0] == "https://backup.example.com/api/fund"


def test_unknown_source_raises_value_error(app_config: AppConfig, fake_request_fn_factory) -> None:
    request_fn = fake_request_fn_factory([200])

    with pytest.raises(ValueError):
        call_with_adapter(
            source="not_a_real_source",
            params={},
            request_fn=request_fn,
            config=app_config,
        )
