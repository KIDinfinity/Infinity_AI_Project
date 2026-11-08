"""`fetch_macro_data`：宏观/利率/汇率数据源 client。

详细规范见 ../../../design/05_agents_skills_prompts.md。当前阶段（Phase 2）默认走
本地样例数据，不发真实网络请求；真实接口接入见 feature checklist F7.2（Optional）。
"""

from __future__ import annotations

import time
from typing import Callable

import httpx

from ..adapter import AdapterResult, RequestFn, call_with_adapter
from ..config import AppConfig

_DEFAULT_INDICATORS = ["interest_rate", "exchange_rate", "cpi"]

_SAMPLE_MACRO_DATA: dict[str, float] = {
    "interest_rate": 0.0335,
    "exchange_rate": 7.12,
    "cpi": 0.021,
}


def _default_request_fn(endpoint: str, params: dict, headers: dict) -> httpx.Response:
    indicators = params.get("indicators", _DEFAULT_INDICATORS)
    data = {indicator: _SAMPLE_MACRO_DATA.get(indicator) for indicator in indicators}
    return httpx.Response(200, json={"data": data})


def fetch_macro_data(
    config: AppConfig,
    indicators: list[str] | None = None,
    request_fn: RequestFn | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> AdapterResult:
    return call_with_adapter(
        source="macro_data",
        params={"indicators": indicators or _DEFAULT_INDICATORS},
        request_fn=request_fn or _default_request_fn,
        config=config,
        sleep_fn=sleep_fn,
    )
