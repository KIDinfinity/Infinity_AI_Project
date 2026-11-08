"""`knowledge.py` 单元测试，对应 design/09_feature_checklist.md F2.5.2~F2.5.3 + F4.3 用到的 get_knowledge_context。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fund import knowledge
from fund.config import AppConfig
from fund.models import LessonLearned, MarketPatternEntry, ProfileObservation, WeeklyReview


def test_upsert_fund_profile_creates_new_profile(tmp_data_root: Path) -> None:
    observation = ProfileObservation(
        date=date(2026, 11, 8), context_summary="宏观中性", outcome_summary="净值上涨 0.3%"
    )

    profile = knowledge.upsert_fund_profile("000001", observation, fund_name="示例基金一号")

    assert profile.fund_code == "000001"
    assert profile.fund_name == "示例基金一号"
    assert profile.historical_behavior == [observation]
    assert knowledge.get_fund_profile("000001") == profile


def test_upsert_fund_profile_appends_without_overwriting_old_observations(
    tmp_data_root: Path,
) -> None:
    first_observation = ProfileObservation(
        date=date(2026, 11, 7), context_summary="宏观中性", outcome_summary="净值上涨 0.5%"
    )
    second_observation = ProfileObservation(
        date=date(2026, 11, 8), context_summary="行业新闻正面", outcome_summary="净值上涨 0.3%"
    )

    knowledge.upsert_fund_profile("000001", first_observation, fund_name="示例基金一号")
    profile = knowledge.upsert_fund_profile("000001", second_observation)

    assert profile.historical_behavior == [first_observation, second_observation]
    assert profile.fund_name == "示例基金一号"  # 第二次未传 fund_name，沿用原有值


def test_get_fund_profile_missing_returns_none(tmp_data_root: Path) -> None:
    assert knowledge.get_fund_profile("999999") is None


def test_append_lesson_from_review_creates_structured_lessons(tmp_data_root: Path) -> None:
    review = WeeklyReview(
        review_week="2026-W45",
        total_predict=10,
        correct_rate=0.8,
        surge_warning_hit_rate=0.75,
        crash_warning_hit_rate=1.0,
        error_classification={"macro_miss": 1},
        new_analysis_factors=["新增因子A", "新增因子B"],
        prompt_optimize_content="优化建议",
        risk_threshold_adjust="维持阈值",
        next_week_context="关注央行议息会议",
        data_warning="",
    )

    lessons = knowledge.append_lesson_from_review(review)

    assert [lesson.lesson_text for lesson in lessons] == ["新增因子A", "新增因子B"]
    assert lessons[0].lesson_id == "L-2026-W45-01"
    assert lessons[1].lesson_id == "L-2026-W45-02"
    assert all(lesson.status == "active" for lesson in lessons)
    assert knowledge.query_lessons() == lessons


def test_query_lessons_filters_by_tags_and_excludes_deprecated(tmp_data_root: Path) -> None:
    from fund import storage

    active_matching = LessonLearned(
        lesson_id="L-001",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="命中标签",
        applicable_scope={"type": "fund_code", "value": "000001"},
        tags=["利率周期"],
        confidence=70,
        status="active",
    )
    active_non_matching = LessonLearned(
        lesson_id="L-002",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="不命中标签",
        applicable_scope={"type": "fund_code", "value": "000001"},
        tags=["季节性"],
        confidence=70,
        status="active",
    )
    deprecated_matching = LessonLearned(
        lesson_id="L-003",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="已失效不应返回",
        applicable_scope={"type": "fund_code", "value": "000001"},
        tags=["利率周期"],
        confidence=70,
        status="deprecated",
    )
    storage.append_lesson(active_matching)
    storage.append_lesson(active_non_matching)
    storage.append_lesson(deprecated_matching)

    result = knowledge.query_lessons(tags=["利率周期"])

    assert result == [active_matching]


def test_query_lessons_filters_by_scope_but_market_wide_always_included(
    tmp_data_root: Path,
) -> None:
    from fund import storage

    fund_specific = LessonLearned(
        lesson_id="L-010",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="仅适用于 000001",
        applicable_scope={"type": "fund_code", "value": "000001"},
        tags=[],
        confidence=70,
        status="active",
    )
    other_fund_specific = LessonLearned(
        lesson_id="L-011",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="仅适用于 000002",
        applicable_scope={"type": "fund_code", "value": "000002"},
        tags=[],
        confidence=70,
        status="active",
    )
    market_wide = LessonLearned(
        lesson_id="L-012",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="全局通用经验",
        applicable_scope={"type": "market_wide", "value": ""},
        tags=[],
        confidence=70,
        status="active",
    )
    storage.append_lesson(fund_specific)
    storage.append_lesson(other_fund_specific)
    storage.append_lesson(market_wide)

    result = knowledge.query_lessons(scope={"type": "fund_code", "value": "000001"})

    assert result == [fund_specific, market_wide]


def _make_pattern(pattern_id: str, applicable_condition: str) -> MarketPatternEntry:
    return MarketPatternEntry(
        pattern_id=pattern_id,
        pattern_type="季节性",
        name="示例规律",
        description="示例描述",
        historical_evidence="示例例证",
        applicable_condition=applicable_condition,
        confidence_note="仅供参考",
        source="测试数据",
    )


def test_match_market_patterns_hits_month_range(tmp_data_root: Path) -> None:
    from fund import storage

    storage._ensure_dir("knowledge_base/market_patterns")
    patterns = [
        _make_pattern("P-001", "每年 1-2 月"),
        _make_pattern("P-002", "每年 6-7 月"),
    ]
    (tmp_data_root / "knowledge_base" / "market_patterns" / "patterns.json").write_text(
        "[" + ",".join(p.model_dump_json() for p in patterns) + "]",
        encoding="utf-8",
    )

    result = knowledge.match_market_patterns(as_of=date(2026, 1, 15))

    assert [p.pattern_id for p in result] == ["P-001"]


def test_match_market_patterns_no_hit_returns_empty(tmp_data_root: Path) -> None:
    from fund import storage

    storage._ensure_dir("knowledge_base/market_patterns")
    patterns = [_make_pattern("P-001", "每年 1-2 月")]
    (tmp_data_root / "knowledge_base" / "market_patterns" / "patterns.json").write_text(
        "[" + ",".join(p.model_dump_json() for p in patterns) + "]",
        encoding="utf-8",
    )

    result = knowledge.match_market_patterns(as_of=date(2026, 6, 1))

    assert result == []


def test_match_market_patterns_hits_keyword_in_macro_context(tmp_data_root: Path) -> None:
    from fund import storage

    storage._ensure_dir("knowledge_base/market_patterns")
    patterns = [_make_pattern("P-003", "央行降息周期")]
    (tmp_data_root / "knowledge_base" / "market_patterns" / "patterns.json").write_text(
        "[" + ",".join(p.model_dump_json() for p in patterns) + "]",
        encoding="utf-8",
    )

    hit = knowledge.match_market_patterns(
        as_of=date(2026, 6, 1), macro_context={"policy_cycle": "降息周期"}
    )
    miss = knowledge.match_market_patterns(
        as_of=date(2026, 6, 1), macro_context={"policy_cycle": "加息周期"}
    )

    assert [p.pattern_id for p in hit] == ["P-003"]
    assert miss == []


def test_get_knowledge_context_combines_profile_lessons_and_patterns(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    from fund import storage

    observation = ProfileObservation(
        date=date(2026, 11, 7), context_summary="宏观中性", outcome_summary="净值上涨 0.3%"
    )
    knowledge.upsert_fund_profile("000001", observation, fund_name="示例基金一号")

    fund_specific_lesson = LessonLearned(
        lesson_id="L-020",
        created_at=date(2026, 11, 8),
        source="manual",
        category="positive_pattern",
        trigger_pattern="x",
        lesson_text="仅适用于 000001",
        applicable_scope={"type": "fund_code", "value": "000001"},
        tags=[],
        confidence=70,
        status="active",
    )
    storage.append_lesson(fund_specific_lesson)

    storage._ensure_dir("knowledge_base/market_patterns")
    seasonal_pattern = _make_pattern("P-010", "每年11-12月")
    (tmp_data_root / "knowledge_base" / "market_patterns" / "patterns.json").write_text(
        "[" + seasonal_pattern.model_dump_json() + "]",
        encoding="utf-8",
    )

    context = knowledge.get_knowledge_context(app_config, "000001", as_of=date(2026, 11, 20))

    assert context["fund_profile"]["fund_code"] == "000001"
    assert [item["lesson_id"] for item in context["lessons_learned"]] == ["L-020"]
    assert [item["pattern_id"] for item in context["market_patterns"]] == ["P-010"]


def test_get_knowledge_context_missing_profile_returns_none(
    tmp_data_root: Path, app_config: AppConfig
) -> None:
    context = knowledge.get_knowledge_context(app_config, "999999", as_of=date(2026, 11, 20))

    assert context["fund_profile"] is None
    assert context["lessons_learned"] == []
    assert context["market_patterns"] == []

