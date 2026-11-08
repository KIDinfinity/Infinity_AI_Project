"""公共 pytest fixture。

详细约定见 ../design/08_testing_strategy.md。
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import httpx
import pytest

_CONFIG_TEMPLATE = """
strategy:
  base_profit_rate: 0.10
  min_hold_days: 30
  confidence_threshold: 70
  surge_upper_target: 0.30

api:
  fund_data:
    endpoint: "https://example.com/api/fund"
    api_key: "${FUND_API_KEY}"
    timeout: 15
    retry_max: 3
    backup_endpoints: ["https://backup.example.com/api/fund"]
  stock_financial:
    endpoint: "https://example.com/api/financial"
    api_key: "${FINANCIAL_API_KEY}"
    timeout: 15
    retry_max: 3
    backup_endpoints: []
  macro_data:
    endpoint: "https://example.com/api/macro"
    api_key: "${MACRO_API_KEY}"
    timeout: 15
    retry_max: 3
    backup_endpoints: []
  financial_news:
    endpoint: "https://example.com/api/news"
    api_key: "${NEWS_API_KEY}"
    timeout: 20
    retry_max: 4
    backup_endpoints: []

api_adapter:
  backoff_factor: 2
  rate_limit_sleep: 5
  auto_reduce_payload: true
  enable_switch_backup: true

llm:
  provider: "fake"
  model: "gpt-4.1"
  api_key: "${LLM_API_KEY}"
  timeout: 60

path:
  data_root: "./data"
"""


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """生成一份写入临时目录的 config.yaml，`data_root` 指向 tmp_path，避免测试污染真实 data/ 目录。"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(_CONFIG_TEMPLATE, encoding="utf-8")
    return config_path


@pytest.fixture
def tmp_data_root(tmp_config: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """让 `storage.py` 内部 `load_config()` 读到临时 config，`data_root` 指向临时目录。"""
    monkeypatch.setenv("FUND_CONFIG_PATH", str(tmp_config))
    return tmp_config.parent / "data"


@pytest.fixture
def app_config(tmp_config: Path, tmp_data_root: Path):
    """加载好的 `AppConfig`，`data_root` 指向临时目录，配合 `tmp_data_root` 隔离测试数据。"""
    from fund.config import load_config

    return load_config(tmp_config)


@pytest.fixture
def fake_request_fn_factory() -> Callable[[list], Callable[[str, dict, dict], httpx.Response]]:
    """构造 `adapter.call_with_adapter` 需要的 `request_fn`。

    `responses` 列表按调用顺序依次消费，每项可以是：
    - `Exception` 实例：本次调用抛出该异常（模拟超时/连接失败）；
    - `int`：本次调用返回该状态码 + 默认合法 JSON body（`{"value": "ok"}`）；
    - `(int, dict | None)`：返回该状态码 + 指定 body；`body=None` 表示返回非法 JSON（模拟格式异常）。

    返回的 `request_fn` 附带 `.calls` 属性，记录每次调用的 `(endpoint, params, headers)`。
    """

    def factory(responses: list) -> Callable[[str, dict, dict], httpx.Response]:
        iterator = iter(responses)
        calls: list[tuple[str, dict, dict]] = []

        def request_fn(endpoint: str, params: dict, headers: dict) -> httpx.Response:
            calls.append((endpoint, dict(params), dict(headers)))
            spec = next(iterator)
            if isinstance(spec, Exception):
                raise spec
            if isinstance(spec, tuple):
                status, body = spec
            else:
                status, body = spec, {"value": "ok"}
            if body is None:
                return httpx.Response(status, content=b"not-json-content")
            return httpx.Response(status, json=body)

        request_fn.calls = calls  # type: ignore[attr-defined]
        return request_fn

    return factory


@pytest.fixture
def recording_sleep_fn() -> Callable[[float], None]:
    """记录每次调用参数的 `sleep_fn`，不真的等待，保证单测秒级跑完。"""
    calls: list[float] = []

    def sleep_fn(seconds: float) -> None:
        calls.append(seconds)

    sleep_fn.calls = calls  # type: ignore[attr-defined]
    return sleep_fn


