"""知识检索与沉淀（建立在 `storage.py` 之上的业务层）。

详细设计动机见 ../../design/10_knowledge_base.md，函数签名约定见
../../design/05_agents_skills_prompts.md。本文件不直接碰文件，所有持久化都
通过 `storage.py`。
"""

from __future__ import annotations

import re
from datetime import date

from . import storage
from .config import AppConfig
from .models import FundProfile, LessonLearned, MarketPatternEntry, ProfileObservation, WeeklyReview

_DEFAULT_LESSON_CONFIDENCE = 60
_MONTH_RANGE_PATTERN = re.compile(r"每年\s*(\d{1,2})\s*-\s*(\d{1,2})\s*月")


def get_fund_profile(fund_code: str) -> FundProfile | None:
    return storage.load_fund_profile(fund_code)


def get_knowledge_context(config: AppConfig, fund_code: str, as_of: date) -> dict:
    """检索 `fund_profile` + 命中的 `lessons_learned` + 命中的 `market_patterns`，组装成 prompt 变量。

    `config` 参数当前未直接用于数据访问（`storage.py` 内部自行通过
    `config.load_config()` 解析 `data_root`），保留在签名里是为了和其他
    agent 层函数的调用约定保持一致，便于未来按需扩展（如基于配置的功能开关）。
    这里的 `market_patterns` 检索只走月份/季节性规则（不传 `macro_context`），
    关键字规则匹配需要调用方在更具体的场景里直接调用 `match_market_patterns`。
    """
    _ = config  # 当前未使用，见上面的 docstring 说明
    profile = get_fund_profile(fund_code)
    lessons = query_lessons(scope={"type": "fund_code", "value": fund_code})
    patterns = match_market_patterns(as_of=as_of)

    return {
        "fund_profile": profile.model_dump(mode="json") if profile else None,
        "lessons_learned": [lesson.model_dump(mode="json") for lesson in lessons],
        "market_patterns": [pattern.model_dump(mode="json") for pattern in patterns],
    }


def upsert_fund_profile(
    fund_code: str,
    observation: ProfileObservation,
    fund_name: str | None = None,
) -> FundProfile:
    """追加一条观察到该基金的画像，不覆盖/删除历史观察。

    若该基金尚无画像，会新建一份；此时若未提供 `fund_name`，暂用 `fund_code`
    占位（后续调用可传入真实名称更新）。
    """
    existing = storage.load_fund_profile(fund_code)
    if existing is None:
        profile = FundProfile(
            fund_code=fund_code,
            fund_name=fund_name or fund_code,
            historical_behavior=[observation],
            last_updated=observation.date,
        )
    else:
        profile = existing.model_copy(
            update={
                "fund_name": fund_name or existing.fund_name,
                "historical_behavior": [*existing.historical_behavior, observation],
                "last_updated": observation.date,
            }
        )

    storage.save_fund_profile(profile)
    return profile


def append_lesson_from_review(review: WeeklyReview) -> list[LessonLearned]:
    """把 `WeeklyReview.new_analysis_factors` 转成结构化 `LessonLearned` 并落盘。"""
    lessons: list[LessonLearned] = []
    for index, factor in enumerate(review.new_analysis_factors, start=1):
        lesson = LessonLearned(
            lesson_id=f"L-{review.review_week}-{index:02d}",
            created_at=date.today(),
            source=f"weekly_review:{review.review_week}",
            category="new_analysis_factor",
            trigger_pattern=review.next_week_context,
            lesson_text=factor,
            applicable_scope={"type": "market_wide", "value": ""},
            tags=[],
            confidence=_DEFAULT_LESSON_CONFIDENCE,
            status="active",
        )
        storage.append_lesson(lesson)
        lessons.append(lesson)
    return lessons


def query_lessons(
    tags: list[str] | None = None,
    scope: dict | None = None,
) -> list[LessonLearned]:
    """按 `tags` 交集 + `applicable_scope` 过滤，只返回 `status="active"` 的条目。

    `scope` 匹配规则：`applicable_scope.type == "market_wide"` 的条目始终命中
    （视为全局通用经验）；否则要求 `applicable_scope` 与传入的 `scope` 完全相等。
    """
    lessons = [lesson for lesson in storage.load_lessons() if lesson.status == "active"]

    if tags:
        tag_set = set(tags)
        lessons = [lesson for lesson in lessons if tag_set & set(lesson.tags)]

    if scope is not None:
        def _scope_matches(applicable_scope: dict) -> bool:
            if applicable_scope.get("type") == "market_wide":
                return True
            return applicable_scope == scope

        lessons = [lesson for lesson in lessons if _scope_matches(lesson.applicable_scope)]

    return lessons


def _matches_month_range(condition: str, month: int) -> bool:
    match = _MONTH_RANGE_PATTERN.search(condition)
    if not match:
        return False
    start, end = int(match.group(1)), int(match.group(2))
    if start <= end:
        return start <= month <= end
    return month >= start or month <= end  # 跨年区间，如 "12-2 月"


def _matches_keyword(condition: str, macro_context: dict) -> bool:
    for value in macro_context.values():
        text = str(value)
        if text and text in condition:
            return True
    return False


def match_market_patterns(
    as_of: date,
    macro_context: dict | None = None,
) -> list[MarketPatternEntry]:
    """按 `applicable_condition` 做简单日期/关键字规则匹配，不做语义检索。"""
    matched: list[MarketPatternEntry] = []
    for pattern in storage.load_market_patterns():
        condition = pattern.applicable_condition
        if _matches_month_range(condition, as_of.month):
            matched.append(pattern)
            continue
        if macro_context and _matches_keyword(condition, macro_context):
            matched.append(pattern)
    return matched
