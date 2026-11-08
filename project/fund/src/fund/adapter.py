"""`api_adapter` 容错核心逻辑。

详细状态机设计见 ../../design/04_api_adapter.md。所有外部数据请求必须经过本
模块的 `call_with_adapter`，`agents/` 与 `sources/` 不允许直接发 HTTP 请求。

关于"返回格式异常/字段缺失"的判定：本模块不了解具体业务 schema，统一约定为
"响应体不是合法 JSON，或解析后不是非空 dict"，由此触发一次性 payload 精简重试。
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Callable

import httpx
from pydantic import BaseModel

from . import storage
from .config import AppConfig, ApiEndpointConfig
from .models import ApiErrorLogEntry

RequestFn = Callable[[str, dict, dict], httpx.Response]
ReduceFn = Callable[[dict], dict]


class AdapterResult(BaseModel):
    ok: bool
    data: dict | None
    degraded: bool
    data_warning: str


def _get_endpoint_config(config: AppConfig, source: str) -> ApiEndpointConfig:
    endpoint_config = getattr(config.api, source, None)
    if endpoint_config is None:
        raise ValueError(f"未知数据源: {source}")
    return endpoint_config


def _default_reduce_payload(params: dict) -> dict:
    reduced = dict(params)
    codes = reduced.get("codes")
    if isinstance(codes, list) and codes:
        reduced["codes"] = codes[:1]
    reduced.pop("extra_fields", None)
    return reduced


def _safe_parse_json(response: httpx.Response) -> dict | None:
    try:
        parsed = response.json()
    except ValueError:
        return None
    if not isinstance(parsed, dict) or not parsed:
        return None
    return parsed


def _log(source: str, stage: str, status_code: int | None, detail: str) -> None:
    storage.append_api_error_log(
        ApiErrorLogEntry(
            timestamp=datetime.now(),
            source=source,
            stage=stage,  # type: ignore[arg-type]
            status_code=status_code,
            detail=detail,
        )
    )


def call_with_adapter(
    source: str,
    params: dict,
    request_fn: RequestFn,
    config: AppConfig,
    reduce_fn: ReduceFn | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> AdapterResult:
    endpoint_config = _get_endpoint_config(config, source)
    adapter_config = config.api_adapter

    endpoints = [endpoint_config.endpoint]
    if adapter_config.enable_switch_backup:
        endpoints.extend(endpoint_config.backup_endpoints)

    headers = {"Authorization": f"Bearer {endpoint_config.api_key}"} if endpoint_config.api_key else {}

    current_params = params
    used_backup_or_reduced = False
    reduced_once = False

    for endpoint_index, endpoint in enumerate(endpoints):
        is_backup = endpoint_index > 0
        attempt = 0

        while True:
            if attempt == 0:
                stage = "switch_backup" if is_backup else "first_try"
            else:
                stage = "retry"

            try:
                response = request_fn(endpoint, current_params, headers)
            except httpx.RequestError as exc:
                _log(source, stage, None, f"请求异常（超时/连接失败）：{exc}")
                if attempt < endpoint_config.retry_max:
                    sleep_fn(adapter_config.rate_limit_sleep * adapter_config.backoff_factor**attempt)
                    attempt += 1
                    continue
                break  # 该地址重试耗尽，尝试下一个地址

            status = response.status_code

            if status == 200:
                parsed = _safe_parse_json(response)
                if parsed is not None:
                    if is_backup or reduced_once:
                        used_backup_or_reduced = True
                    return AdapterResult(
                        ok=True,
                        data=parsed,
                        degraded=used_backup_or_reduced,
                        data_warning=(
                            f"{source} 使用了备用地址或精简参数，数据可能不完整"
                            if used_backup_or_reduced
                            else ""
                        ),
                    )

                _log(source, "reduce_payload", status, "响应格式异常或字段缺失")
                if adapter_config.auto_reduce_payload and not reduced_once:
                    reduce = reduce_fn or _default_reduce_payload
                    current_params = reduce(current_params)
                    reduced_once = True
                    continue  # 精简后立即在同一地址重试一次，不计入 retry_max
                break  # 精简后仍失败（或不允许精简），切换下一个地址

            if status in (401, 403):
                _log(source, "give_up", status, "鉴权失败，不重试、不切换备用地址")
                return AdapterResult(
                    ok=False,
                    data=None,
                    degraded=True,
                    data_warning=f"{source} 接口鉴权失败（状态码 {status}），请检查 api_key",
                )

            if status == 429 or 500 <= status < 600:
                _log(source, stage, status, f"状态码 {status}，准备退避重试")
                if attempt < endpoint_config.retry_max:
                    sleep_fn(adapter_config.rate_limit_sleep * adapter_config.backoff_factor**attempt)
                    attempt += 1
                    continue
                break  # 该地址重试耗尽，尝试下一个地址

            _log(source, stage, status, f"未覆盖的状态码 {status}，放弃该地址")
            break  # 未知状态码不重试，直接尝试下一个地址

    _log(source, "give_up", None, f"{source} 全部地址（含备用）均失败")
    return AdapterResult(
        ok=False,
        data=None,
        degraded=True,
        data_warning=f"{source} 数据源全部失败，已降级（无可用数据）",
    )
