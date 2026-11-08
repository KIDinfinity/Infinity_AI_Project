"""`fetch_stock_financial`：重仓个股财报数据源 client。

详细规范见 ../../../design/05_agents_skills_prompts.md。当前阶段（Phase 2）默认走
本地样例数据，不发真实网络请求；真实接口接入见 feature checklist F7.2（Optional）。
"""

from __future__ import annotations

import time
from typing import Callable

import httpx

from ..adapter import AdapterResult, RequestFn, call_with_adapter
from ..config import AppConfig

_SAMPLE_STOCK_FINANCIAL: dict[str, dict] = {
    "贵州茅台": {"revenue_growth": 0.15, "profit_growth": 0.17, "pe_ratio": 28.5},
    "宁德时代": {"revenue_growth": 0.22, "profit_growth": 0.18, "pe_ratio": 32.1},
    "腾讯控股": {"revenue_growth": 0.09, "profit_growth": 0.12, "pe_ratio": 19.8},
    "比亚迪": {"revenue_growth": 0.25, "profit_growth": 0.20, "pe_ratio": 24.3},
}


def _default_request_fn(endpoint: str, params: dict, headers: dict) -> httpx.Response:
    codes = params.get("codes", [])
    data = {
        code: _SAMPLE_STOCK_FINANCIAL.get(
            code,
            {"revenue_growth": None, "profit_growth": None, "pe_ratio": None},
        )
        for code in codes
    }
    return httpx.Response(200, json={"data": data})


def fetch_stock_financial(
    config: AppConfig,
    stock_codes: list[str],
    request_fn: RequestFn | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> AdapterResult:
    return call_with_adapter(
        source="stock_financial",
        params={"codes": stock_codes},
        request_fn=request_fn or _default_request_fn,
        config=config,
        sleep_fn=sleep_fn,
    )
