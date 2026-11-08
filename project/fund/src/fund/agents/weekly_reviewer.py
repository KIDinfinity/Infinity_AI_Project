"""`weekly_reviewer.py`：每周复盘统计 + 误差分类 + 新增分析因子生成。

详见 ../../../design/05_agents_skills_prompts.md。产出 `WeeklyReview`；产出的
`new_analysis_factors` 之后**必须**调用 `knowledge.append_lesson_from_review(...)`
转成结构化 `LessonLearned` 落盘，不允许只停留在复盘报告的自然语言里（硬约束，见
design/01_directory_structure.md 扩展点表格）。

命中率/准确率等数字由 LLM 直接根据 `analysis_logs_summary`/`real_nav_summary`
给出（不在代码里重新计算），但做了防御性解析：非法数值用默认值兜底，比率字段强制
夹到 `[0, 1]` 区间，避免异常 LLM 输出污染 `performance_db` 统计口径。
"""

from __future__ import annotations

import json
from typing import Callable

from .. import knowledge
from ..config import AppConfig
from ..llm import call_llm, load_prompt
from ..models import AnalysisRecord, TradeDecision, WeeklyReview
from ..rules import BASE_RULE_TEXT
from ._common import coerce_int, coerce_rate, collect_data_warning, parse_llm_json_response


def run(
    config: AppConfig,
    review_week: str,
    analysis_records: list[AnalysisRecord],
    trade_decisions: list[TradeDecision],
    real_nav_data: dict[str, float],
    call_llm_fn: Callable[[AppConfig, str], str] = call_llm,
) -> WeeklyReview:
    data_warning = collect_data_warning(analysis_records)

    prompt = load_prompt(
        "weekly_improve",
        review_week=review_week,
        analysis_logs_summary=json.dumps(
            [record.model_dump(mode="json") for record in analysis_records], ensure_ascii=False
        ),
        trade_decisions_summary=json.dumps(
            [decision.model_dump(mode="json") for decision in trade_decisions], ensure_ascii=False
        ),
        real_nav_summary=json.dumps(real_nav_data, ensure_ascii=False),
        base_rule_text=BASE_RULE_TEXT,
    )

    raw_response = call_llm_fn(config, prompt)
    parsed = parse_llm_json_response(raw_response)

    error_classification = parsed.get("error_classification", {})
    if not isinstance(error_classification, dict):
        error_classification = {}
    error_classification = {
        str(key): coerce_int(value) for key, value in error_classification.items()
    }

    new_analysis_factors = parsed.get("new_analysis_factors", [])
    if not isinstance(new_analysis_factors, list):
        new_analysis_factors = []
    new_analysis_factors = [str(factor) for factor in new_analysis_factors]

    review = WeeklyReview(
        review_week=review_week,
        total_predict=coerce_int(parsed.get("total_predict"), default=len(analysis_records)),
        correct_rate=coerce_rate(parsed.get("correct_rate")),
        surge_warning_hit_rate=coerce_rate(parsed.get("surge_warning_hit_rate")),
        crash_warning_hit_rate=coerce_rate(parsed.get("crash_warning_hit_rate")),
        error_classification=error_classification,
        new_analysis_factors=new_analysis_factors,
        prompt_optimize_content=str(parsed.get("prompt_optimize_content", "")),
        risk_threshold_adjust=str(parsed.get("risk_threshold_adjust", "")),
        next_week_context=str(parsed.get("next_week_context", "")),
        data_warning=data_warning,
    )

    if review.new_analysis_factors:
        knowledge.append_lesson_from_review(review)

    return review
