# 03. 数据模型与落盘格式

所有模型定义在 `src/fund/models.py`，用 `pydantic.BaseModel`。字段名与 draft 中 JSON 示例保持一致，便于直接对照需求。

## 1. `AnalysisRecord`（对应 `data/analysis_log/YYYY-MM-DD.json`）

一天一个文件，文件内容是 `list[AnalysisRecord]`（当天持有的每只基金一条）。

| 字段                   | 类型                                       | 说明                                   |
| ---------------------- | ------------------------------------------ | -------------------------------------- |
| `execute_date`         | `date`                                     | 执行日期                               |
| `fund_code`            | `str`                                      | 基金代码                               |
| `fund_name`            | `str`                                      | 基金名称                               |
| `buy_cost`             | `float`                                    | 买入成本                               |
| `hold_days`            | `int`                                      | 已持有天数                             |
| `current_yield`        | `float`                                    | 当前收益率                             |
| `base_profit_signal`   | `Literal["持有","卖出"]`                   | Target1 结果                           |
| `early_sell_fee_judge` | `str`                                      | 手续费测算说明（是否满足提前止盈豁免） |
| `bull_alert`           | `BullAlert`                                | Target2 结果（嵌套模型）               |
| `crash_risk`           | `CrashRisk`                                | Target3 结果（嵌套模型）               |
| `next_week_trend_text` | `str`                                      | 一周文字涨势描述                       |
| `analysis_argument`    | `AnalysisArgument`                         | 多维度论证（嵌套模型）                 |
| `final_decision`       | `Literal["持有","减仓","清仓","止盈卖出"]` | 最终结论                               |
| `data_warning`         | `str`                                      | 数据缺失/降级提示，无则空字符串        |

```python
class BullAlert(BaseModel):
    is_surge: bool
    expected_gain: str          # 如 "0.1~0.3"
    confidence: int             # 0~100
    reason_list: list[str]

class CrashRisk(BaseModel):
    is_crash: bool
    escape_window: str
    prev_error_summary: str
    bad_factors: list[str]

class AnalysisArgument(BaseModel):
    stock_holding: str
    financial_report: str
    macro_economy: str
    industry_news: str
    bond_market: str
```

校验规则：`confidence` 必须在 `[0, 100]`；当 `confidence < strategy.confidence_threshold` 时，`bull_alert.is_surge` 不允许同时为推荐买入（由 `rules.py` 保证，不是模型层强校验，模型层只管类型/范围）。

## 2. `TradeDecision`（对应 `data/trade_decision/*.jsonl`，按月分文件 `YYYY-MM.jsonl`）

JSONL：每行一条独立 JSON，便于追加写入、流式读取。

| 字段                | 类型                                    | 说明                                                                                |
| ------------------- | --------------------------------------- | ----------------------------------------------------------------------------------- |
| `decision_id`       | `str`                                   | `{fund_code}-{signal_date}-{signal_type}` 组合生成，保证可重现                      |
| `fund_code`         | `str`                                   | 基金代码                                                                            |
| `signal_date`       | `date`                                  | 信号产生日期                                                                        |
| `signal_type`       | `Literal["止盈","暴涨预警","暴跌预警"]` | 信号类型                                                                            |
| `trigger_condition` | `str`                                   | 触发条件说明                                                                        |
| `executed`          | `bool`                                  | 用户是否执行（默认 `False`，人工事后标注，暂不做自动回填 UI，见 feature checklist） |
| `realized_return`   | `float \| None`                         | 兑现收益，未执行则为 `None`                                                         |

## 3. `WeeklyReview`（对应 `data/weekly_review_log/YYYY-WW-review.json` + 同名 `.md`）

| 字段                      | 类型             | 说明                                 |
| ------------------------- | ---------------- | ------------------------------------ |
| `review_week`             | `str`            | 如 `"2026-W43"`                      |
| `total_predict`           | `int`            | 本周预测总数                         |
| `correct_rate`            | `float`          | 命中率                               |
| `surge_warning_hit_rate`  | `float`          | 暴涨预警命中率                       |
| `crash_warning_hit_rate`  | `float`          | 暴跌预警命中率                       |
| `error_classification`    | `dict[str, int]` | 误差分类计数，key 为固定枚举（见下） |
| `new_analysis_factors`    | `list[str]`      | 新增分析因子                         |
| `prompt_optimize_content` | `str`            | 对 daily 分析 prompt 的修改建议      |
| `risk_threshold_adjust`   | `str`            | 置信度调整方案                       |
| `next_week_context`       | `str`            | 下周分析强制前置条件                 |
| `data_warning`            | `str`            | 数据源异常记录                       |

`error_classification` 固定枚举 key（对应 draft Target 要求的误差分类）：
`financial_misjudge`、`macro_miss`、`industry_black_swan`、`fund_position_change`、`style_switch`、`bond_rate_risk`、`info_delay`、`subjective_bias`。

`.md` 文件是 `.json` 的人类可读渲染版本（由 `storage.py` 的渲染函数生成，内容来自同一个 `WeeklyReview` 对象，避免两份数据手写导致不一致）。

## 4. `PerformanceRecord`（对应 `data/performance_db/*.jsonl`，按年分文件 `YYYY.jsonl`）

| 字段             | 类型        | 说明                           |
| ---------------- | ----------- | ------------------------------ |
| `fund_code`      | `str`       | 基金代码                       |
| `predict_date`   | `date`      | 预测日期                       |
| `predict_return` | `float`     | 预测收益率                     |
| `real_return`    | `float`     | 实际收益率（下一周期回填）     |
| `error`          | `float`     | `real_return - predict_return` |
| `confidence`     | `int`       | 预测时的置信分                 |
| `factor_list`    | `list[str]` | 预测时使用的关键因子           |

## 5. `ApiErrorLogEntry`（对应 `data/raw_data/api_error_log.json`，`list[ApiErrorLogEntry]`，追加写入）

| 字段          | 类型                                                                      | 说明                                  |
| ------------- | ------------------------------------------------------------------------- | ------------------------------------- |
| `timestamp`   | `datetime`                                                                | 发生时间                              |
| `source`      | `str`                                                                     | 接口标识，如 `"fund_data"`            |
| `stage`       | `Literal["first_try","retry","switch_backup","reduce_payload","give_up"]` | 容错所处阶段                          |
| `status_code` | `int \| None`                                                             | HTTP 状态码（超时/连接失败为 `None`） |
| `detail`      | `str`                                                                     | 错误详情                              |

## 6. 知识库与真实操作记录模型（详细设计动机见 [10_knowledge_base.md](10_knowledge_base.md)）

### 6.1 `ActualOperation`（对应 `data/actual_operations/YYYY-MM.jsonl`）

用户真实买卖记录，与 AI 产生的 `TradeDecision`（建议）严格区分——这是检验"建议是否被采纳、采纳后效果如何"的唯一真值来源，**完全由用户手工录入，系统不猜测**。

| 字段                | 类型                                   | 说明                                                                                |
| ------------------- | -------------------------------------- | ----------------------------------------------------------------------------------- |
| `operation_id`      | `str`                                  | `{fund_code}-{operation_date}-{operation_type}` 组合生成                            |
| `fund_code`         | `str`                                  | 基金代码                                                                            |
| `operation_date`    | `date`                                 | 操作日期                                                                            |
| `operation_type`    | `Literal["买入","卖出","加仓","减仓"]` | 操作类型                                                                            |
| `amount`            | `float`                                | 金额或份额（二选一，用 `amount_unit` 区分）                                         |
| `amount_unit`       | `Literal["金额","份额"]`               | 配合 `amount`                                                                       |
| `price_or_nav`      | `float`                                | 成交净值/价格                                                                       |
| `related_signal_id` | `str \| None`                          | 若该操作采纳了某条 `TradeDecision`，填其 `decision_id`，便于回溯"建议→实际执行"链路 |
| `note`              | `str`                                  | 用户备注（为什么这么做）                                                            |

### 6.2 `LessonLearned`（对应 `data/knowledge_base/lessons_learned/lessons.jsonl`）

从每周复盘的 `new_analysis_factors` 提炼出的**结构化、可检索**教训，追加写入、不物理删除（失效时标记 `status="deprecated"`，保留历史演变轨迹）。

| 字段               | 类型                             | 说明                                                                                                       |
| ------------------ | -------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `lesson_id`        | `str`                            | 唯一 id，如 `L-2026W43-01`                                                                                 |
| `created_at`       | `date`                           | 产生日期                                                                                                   |
| `source`           | `str`                            | 来源，如 `"weekly_review:2026-W43"`                                                                        |
| `category`         | `str`                            | 复用 `WeeklyReview.error_classification` 的枚举，或 `"positive_pattern"`（做对的经验也值得沉淀，不止错误） |
| `trigger_pattern`  | `str`                            | 什么情况下适用（供后续检索判断是否命中）                                                                   |
| `lesson_text`      | `str`                            | 经验/教训正文                                                                                              |
| `applicable_scope` | `dict`                           | `{"type": "fund_code\|sector\|market_wide", "value": str}`                                                 |
| `tags`             | `list[str]`                      | 便于按标签检索                                                                                             |
| `confidence`       | `int`                            | 0~100，该经验当前被验证的可信程度                                                                          |
| `status`           | `Literal["active","deprecated"]` | 失效时置为 `deprecated`，不删除                                                                            |

### 6.3 `FundProfile`（对应 `data/knowledge_base/fund_profiles/{fund_code}.json`，一基金一文件，整体覆盖式更新）

| 字段                  | 类型                       | 说明                                 |
| --------------------- | -------------------------- | ------------------------------------ |
| `fund_code`           | `str`                      | 基金代码                             |
| `fund_name`           | `str`                      | 基金名称                             |
| `manager_style`       | `str`                      | 基金经理风格描述（人工/AI 协助维护） |
| `known_risk_factors`  | `list[str]`                | 已知风险点                           |
| `historical_behavior` | `list[ProfileObservation]` | 持续累加的观察记录，见下             |
| `last_updated`        | `date`                     | 最近更新日期                         |

```python
class ProfileObservation(BaseModel):
    date: date
    context_summary: str   # 当时的宏观/市场背景摘要
    outcome_summary: str   # 该基金的实际表现摘要
```

`historical_behavior` 只追加，不覆盖删除旧观察，保证"这只基金在类似环境下历史上表现如何"始终可追溯。

### 6.4 `MarketPatternEntry`（对应 `data/knowledge_base/market_patterns/patterns.json`，`list[MarketPatternEntry]`）

近几十年市场运行规律的参考库，**人工维护为主**（可由 AI 协助整理草稿，但入库前必须人工审阅确认，系统日常流程不自动写入这一层，避免幻觉污染长期参考知识）。

| 字段                   | 类型                                                        | 说明                                                                       |
| ---------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------- |
| `pattern_id`           | `str`                                                       | 唯一 id                                                                    |
| `pattern_type`         | `Literal["利率周期","政策周期","季节性","经济周期","其他"]` | 规律分类                                                                   |
| `name`                 | `str`                                                       | 规律名称，如"春season季躁动"                                               |
| `description`          | `str`                                                       | 规律描述                                                                   |
| `historical_evidence`  | `str`                                                       | 近几十年的具体例证（如"2005-2024 年 N 次中 M 次应验"）                     |
| `applicable_condition` | `str`                                                       | 触发/适用条件描述，供匹配时判断是否命中（如"每年 1-2 月"、"央行降息周期"） |
| `confidence_note`      | `str`                                                       | 当前被认为的可靠程度与局限性说明                                           |
| `source`               | `str`                                                       | 信息来源（书籍/研报/用户整理），避免编造                                   |

## 落盘格式选择依据

| 数据                                | 格式                          | 理由                                                                                      |
| ----------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------- |
| `analysis_log`                      | 按天一个 JSON 文件            | 每天只生成一次、整体读取/整体展示，文件即"一天快照"                                       |
| `trade_decision` / `performance_db` | JSONL 按月/按年分文件         | 持续追加、未来量化训练要逐行流式读取，JSONL 更合适                                        |
| `weekly_review_log`                 | 一周一个 JSON + 一份 Markdown | JSON 给程序读，Markdown 给人读复盘                                                        |
| `api_error_log`                     | 单一 JSON 数组文件            | 量小、偶发，直接整体读写最简单；超过一定大小（如 10MB）才考虑按月切分（后置优化，先不做） |
| `actual_operations`                 | JSONL 按月分文件              | 用户手工持续录入的真值记录，适合流式追加                                                  |
| `fund_profiles`                     | 一基金一个 JSON（整体覆盖写） | 单个基金的画像是"当前最新状态"的完整快照，覆盖写更新最简单                                |
| `lessons_learned`                   | 单一 JSONL 追加写入           | 持续增长、需要按条过滤检索，JSONL 便于逐行扫描                                            |
| `market_patterns`                   | 单一 JSON 数组文件            | 人工维护为主、更新频率低，整体读写足够                                                    |

## `storage.py` 对外函数签名（设计约定，实现时照此签名写）

```python
def save_daily_analysis(records: list[AnalysisRecord]) -> Path: ...
def load_daily_analysis(date_: date) -> list[AnalysisRecord]: ...
def append_trade_decision(record: TradeDecision) -> None: ...
def save_weekly_review(review: WeeklyReview) -> tuple[Path, Path]: ...  # (json_path, md_path)
def append_performance_record(record: PerformanceRecord) -> None: ...
def append_api_error_log(entry: ApiErrorLogEntry) -> None: ...

# 知识库 / 真实操作（新增，纯 I/O，不含检索/匹配逻辑——检索逻辑在 knowledge.py）
def append_actual_operation(op: ActualOperation) -> None: ...
def load_actual_operations(fund_code: str | None = None) -> list[ActualOperation]: ...
def append_lesson(lesson: LessonLearned) -> None: ...
def load_lessons() -> list[LessonLearned]: ...
def save_fund_profile(profile: FundProfile) -> None: ...
def load_fund_profile(fund_code: str) -> FundProfile | None: ...
def load_market_patterns() -> list[MarketPatternEntry]: ...
```

所有读写统一走这些函数，禁止在 `agents/` 里直接 `open()` 文件，保证"换存储格式只改 `storage.py` 一处"。`knowledge.py` 建立在这些函数之上做过滤/匹配/组装（见 [05_agents_skills_prompts.md](05_agents_skills_prompts.md)），不直接碰文件。
