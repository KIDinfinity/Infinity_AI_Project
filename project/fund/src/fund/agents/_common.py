"""`agents/*.py` 内部共享的小工具函数，非公开 agent，只做代码复用。

不在 feature checklist 中单独计费，随 F4.3 一起从 `position_analyst.py` 里提取出来，
避免 `bull_scanner.py` / `risk_alert.py` / `weekly_reviewer.py` 重复实现同样的
"汇总 AdapterResult" / "合并 data_warning" / "宽容解析 LLM JSON 输出" 逻辑。
"""

from __future__ import annotations

import json
import re
from typing import Protocol

from ..adapter import AdapterResult

_RANGE_SPLIT_PATTERN = re.compile(r"[~～]")


class _HasDataWarning(Protocol):
    data_warning: str


def summarize_adapter_result(result: AdapterResult) -> str:
    if result.data is None:
        return "（无数据）"
    return json.dumps(result.data, ensure_ascii=False)


def collect_data_warning(results: list[_HasDataWarning]) -> str:
    """合并多个对象（`AdapterResult` 或 `AnalysisRecord` 等）的 `data_warning` 字段。"""
    warnings = [result.data_warning for result in results if result.data_warning]
    return "；".join(warnings)


def parse_llm_json_response(raw: str) -> dict:
    """宽容解析 LLM 返回的 JSON 字符串：解析失败或不是对象时返回空 dict，不抛异常。"""
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    return parsed


def coerce_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def parse_expected_gain(raw: object) -> float:
    """解析形如 `"0.1~0.3"` 或 `"0.2"` 或 `"30%"` 的预期涨幅字符串，取区间上限。

    由 `bull_scanner.py` 产出 `BullAlert.expected_gain` 时使用，也供
    `orchestrator.py` 回填 `performance_db` 时复用同一套解析逻辑。
    """
    text = str(raw)
    is_percentage = "%" in text
    parts = [part.strip() for part in _RANGE_SPLIT_PATTERN.split(text) if part.strip()]

    numbers: list[float] = []
    for part in parts:
        cleaned = part.rstrip("%").strip()
        try:
            value = float(cleaned)
        except ValueError:
            continue
        numbers.append(value / 100 if is_percentage else value)

    if not numbers:
        return 0.0
    return max(numbers)


def coerce_rate(value: object, default: float = 0.0) -> float:
    """解析 LLM 返回的比率字段，强制夹到 [0, 1] 区间，防止异常值污染统计。"""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, number))
