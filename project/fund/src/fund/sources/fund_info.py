"""`fetch_fund_info`：持仓/净值数据源 client。

详细规范见 ../../../design/05_agents_skills_prompts.md。当前阶段（Phase 2）默认走
本地样例数据，不发真实网络请求；真实接口接入见 feature checklist F7.2（Optional）。
"""

from __future__ import annotations

import time
from typing import Callable

import httpx

from ..adapter import AdapterResult, RequestFn, call_with_adapter
from ..config import AppConfig

_SAMPLE_FUND_INFO: dict[str, dict] = {
    "000001": {
        "fund_name": "示例基金一号",
        "nav": 1.234,
        "nav_date": "2026-11-07",
        "position": ["贵州茅台", "宁德时代"],
    },
    "000002": {
        "fund_name": "示例基金二号",
        "nav": 2.345,
        "nav_date": "2026-11-07",
        "position": ["腾讯控股", "比亚迪"],
    },
}


def _default_request_fn(endpoint: str, params: dict, headers: dict) -> httpx.Response:
    codes = params.get("codes", [])
    data = {
        code: _SAMPLE_FUND_INFO.get(
            code,
            {"fund_name": "未知基金", "nav": None, "nav_date": None, "position": []},
        )
        for code in codes
    }
    return httpx.Response(200, json={"data": data})


def fetch_fund_info(
    config: AppConfig,
    fund_codes: list[str],
    request_fn: RequestFn | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> AdapterResult:
    return call_with_adapter(
        source="fund_data",
        params={"codes": fund_codes},
        request_fn=request_fn or _default_request_fn,
        config=config,
        sleep_fn=sleep_fn,
    )
