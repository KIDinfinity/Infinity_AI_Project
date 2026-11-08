"""记录读写（JSON / JSONL）。

全部读写统一走本模块的函数，详细落盘格式见 ../../design/03_data_model.md。
本文件实现第 1~6 节对应的读写函数。

`data_root` 通过 `config.load_config()` 解析得到，不在函数签名中显式传入，
保证调用方（agents/cli）无需关心存储细节。
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from . import config as config_module
from .models import (
    ActualOperation,
    AnalysisRecord,
    ApiErrorLogEntry,
    FundProfile,
    LessonLearned,
    MarketPatternEntry,
    PerformanceRecord,
    TradeDecision,
    WeeklyReview,
)


def _data_root() -> Path:
    return Path(config_module.load_config().path.data_root)


def _ensure_dir(relative: str) -> Path:
    directory = _data_root() / relative
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_daily_analysis(records: list[AnalysisRecord]) -> Path:
    if not records:
        raise ValueError("records 不能为空，无法确定文件日期")

    execute_date = records[0].execute_date
    directory = _ensure_dir("analysis_log")
    file_path = directory / f"{execute_date:%Y-%m-%d}.json"

    payload = [record.model_dump(mode="json") for record in records]
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def load_daily_analysis(date_: date) -> list[AnalysisRecord]:
    file_path = _data_root() / "analysis_log" / f"{date_:%Y-%m-%d}.json"
    if not file_path.is_file():
        return []

    raw_list = json.loads(file_path.read_text(encoding="utf-8"))
    return [AnalysisRecord.model_validate(item) for item in raw_list]


def append_trade_decision(record: TradeDecision) -> None:
    directory = _ensure_dir("trade_decision")
    file_path = directory / f"{record.signal_date:%Y-%m}.jsonl"

    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(record.model_dump_json())
        fh.write("\n")


def load_trade_decisions(year_month: str) -> list[TradeDecision]:
    file_path = _data_root() / "trade_decision" / f"{year_month}.jsonl"
    if not file_path.is_file():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines()
    return [TradeDecision.model_validate_json(line) for line in lines if line.strip()]


def _render_weekly_review_markdown(review: WeeklyReview) -> str:
    error_lines = "\n".join(
        f"- {key}: {count}" for key, count in review.error_classification.items()
    )
    factor_lines = "\n".join(f"- {factor}" for factor in review.new_analysis_factors)

    return f"""# 周复盘 {review.review_week}

- 本周预测总数：{review.total_predict}
- 命中率：{review.correct_rate}
- 暴涨预警命中率：{review.surge_warning_hit_rate}
- 暴跌预警命中率：{review.crash_warning_hit_rate}

## 误差分类

{error_lines or "（无）"}

## 新增分析因子

{factor_lines or "（无）"}

## Prompt 优化建议

{review.prompt_optimize_content}

## 置信度调整方案

{review.risk_threshold_adjust}

## 下周分析强制前置条件

{review.next_week_context}

## 数据异常记录

{review.data_warning or "（无）"}
"""


def save_weekly_review(review: WeeklyReview) -> tuple[Path, Path]:
    directory = _ensure_dir("weekly_review_log")
    base_name = f"{review.review_week}-review"
    json_path = directory / f"{base_name}.json"
    md_path = directory / f"{base_name}.md"

    json_path.write_text(review.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(_render_weekly_review_markdown(review), encoding="utf-8")
    return json_path, md_path


def append_performance_record(record: PerformanceRecord) -> None:
    directory = _ensure_dir("performance_db")
    file_path = directory / f"{record.predict_date.year}.jsonl"

    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(record.model_dump_json())
        fh.write("\n")


def load_performance_records(year: int) -> list[PerformanceRecord]:
    file_path = _data_root() / "performance_db" / f"{year}.jsonl"
    if not file_path.is_file():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines()
    return [PerformanceRecord.model_validate_json(line) for line in lines if line.strip()]


def append_api_error_log(entry: ApiErrorLogEntry) -> None:
    directory = _ensure_dir("raw_data")
    file_path = directory / "api_error_log.json"

    if file_path.is_file():
        existing_raw = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        existing_raw = []

    existing_raw.append(entry.model_dump(mode="json"))
    file_path.write_text(json.dumps(existing_raw, ensure_ascii=False, indent=2), encoding="utf-8")


def load_api_error_log() -> list[ApiErrorLogEntry]:
    file_path = _data_root() / "raw_data" / "api_error_log.json"
    if not file_path.is_file():
        return []

    raw_list = json.loads(file_path.read_text(encoding="utf-8"))
    return [ApiErrorLogEntry.model_validate(item) for item in raw_list]


def append_actual_operation(op: ActualOperation) -> None:
    directory = _ensure_dir("actual_operations")
    file_path = directory / f"{op.operation_date:%Y-%m}.jsonl"

    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(op.model_dump_json())
        fh.write("\n")


def load_actual_operations(fund_code: str | None = None) -> list[ActualOperation]:
    directory = _data_root() / "actual_operations"
    if not directory.is_dir():
        return []

    operations: list[ActualOperation] = []
    for file_path in sorted(directory.glob("*.jsonl")):
        lines = file_path.read_text(encoding="utf-8").splitlines()
        operations.extend(ActualOperation.model_validate_json(line) for line in lines if line.strip())

    if fund_code is not None:
        operations = [op for op in operations if op.fund_code == fund_code]
    return operations


def append_lesson(lesson: LessonLearned) -> None:
    directory = _ensure_dir("knowledge_base/lessons_learned")
    file_path = directory / "lessons.jsonl"

    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(lesson.model_dump_json())
        fh.write("\n")


def load_lessons() -> list[LessonLearned]:
    file_path = _data_root() / "knowledge_base" / "lessons_learned" / "lessons.jsonl"
    if not file_path.is_file():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines()
    return [LessonLearned.model_validate_json(line) for line in lines if line.strip()]


def save_fund_profile(profile: FundProfile) -> None:
    directory = _ensure_dir("knowledge_base/fund_profiles")
    file_path = directory / f"{profile.fund_code}.json"
    file_path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")


def load_fund_profile(fund_code: str) -> FundProfile | None:
    file_path = _data_root() / "knowledge_base" / "fund_profiles" / f"{fund_code}.json"
    if not file_path.is_file():
        return None
    return FundProfile.model_validate_json(file_path.read_text(encoding="utf-8"))


def load_market_patterns() -> list[MarketPatternEntry]:
    file_path = _data_root() / "knowledge_base" / "market_patterns" / "patterns.json"
    if not file_path.is_file():
        return []

    raw_list = json.loads(file_path.read_text(encoding="utf-8"))
    return [MarketPatternEntry.model_validate(item) for item in raw_list]

