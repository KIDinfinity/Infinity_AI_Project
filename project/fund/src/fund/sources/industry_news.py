"""`fetch_industry_news`：行业/政策新闻数据源 client。

详细规范见 ../../../design/05_agents_skills_prompts.md。当前阶段（Phase 2）默认走
本地样例数据，不发真实网络请求；真实接口接入见 feature checklist F7.2（Optional）。

对应 `config.api.financial_news`（配置字段命名沿用 02_config.md，与文件名
`industry_news.py` 不完全一致，属历史设计用词，不重复定义新字段）。
"""

from __future__ import annotations

import time
from typing import Callable

import httpx

from ..adapter import AdapterResult, RequestFn, call_with_adapter
from ..config import AppConfig

_SAMPLE_INDUSTRY_NEWS: dict[str, list[str]] = {
    "白酒": ["消费复苏预期升温，白酒板块估值修复"],
    "新能源": ["电池级碳酸锂价格企稳，产业链盈利有望改善"],
    "互联网": ["监管环境边际宽松，平台经济政策利好释放"],
}


def _default_request_fn(endpoint: str, params: dict, headers: dict) -> httpx.Response:
    industries = params.get("industries", [])
    data = {industry: _SAMPLE_INDUSTRY_NEWS.get(industry, []) for industry in industries}
    return httpx.Response(200, json={"data": data})


def fetch_industry_news(
    config: AppConfig,
    industries: list[str],
    request_fn: RequestFn | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> AdapterResult:
    return call_with_adapter(
        source="financial_news",
        params={"industries": industries},
        request_fn=request_fn or _default_request_fn,
        config=config,
        sleep_fn=sleep_fn,
    )
