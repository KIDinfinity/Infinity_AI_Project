# 09. 功能点实现清单（按顺序逐条推进）

> 使用方法：按 Phase 顺序、Phase 内按编号顺序实现。每条完成后对照「验收标准」自查，`uv run pytest` 全绿再进入下一条。不允许跳跃实现（如在 Phase 1 没完成前先写 Phase 3），除非该条明确标注 Optional。

## Phase 0 · 项目骨架

- [x] **F0.1** 初始化 `pyproject.toml`（uv 项目，依赖：`pydantic`、`pytest`、`httpx`、`pyyaml`），`uv run pytest` 能跑通（哪怕 0 条用例）。
  - 验收：`uv sync` 成功；`uv run pytest` 退出码 0。
- [x] **F0.2** `config.py`：`AppConfig` 模型 + `load_config()` + `${ENV}` 占位符替换。
  - 验收：`tests/test_config.py` 覆盖"合法加载/缺字段报错/环境变量替换"三类用例，全部通过。
- [x] **F0.3** `models.py`：实现 [03_data_model.md](03_data_model.md) 中全部模型。
  - 验收：`tests/test_models.py` 覆盖"合法构造/字段越界报错/序列化往返一致"。
- [x] **F0.4** `storage.py`：实现 [03_data_model.md](03_data_model.md) 末尾列出的全部读写函数。
  - 验收：`tests/test_storage.py` 写入再读回，内容与原对象一致；JSONL 追加不覆盖旧行。

## Phase 1 · 容错适配器

- [x] **F1.1** `adapter.py`：实现状态机骨架（成功路径 + 401/403 失败路径），日志写入 `api_error_log`。
  - 验收：两类用例通过，且 `ApiErrorLogEntry` 被正确写入。
- [x] **F1.2** 补全 429 / 5xx / 超时的指数退避重试（用注入的 `sleep_fn` 保证秒级跑完测试）。
  - 验收：模拟"重试 2 次后成功"和"重试耗尽"两种场景均断言正确。
- [x] **F1.3** 补全备用 endpoint 切换逻辑。
  - 验收：主地址全部重试失败 -> 切备用 -> 备用成功 / 备用也失败两种场景均覆盖。
- [x] **F1.4** 补全 payload 精简降级逻辑。
  - 验收：格式异常触发精简 -> 精简后成功 / 精简后仍失败两种场景均覆盖。

## Phase 2 · 数据源

- [x] **F2.1** `sources/fund_info.py`（`fetch_fund_info`，先接 fake/本地样例数据，真实接口地址留空走 `config`）。
- [x] **F2.2** `sources/stock_financial.py`（`fetch_stock_financial`）。
- [x] **F2.3** `sources/macro_data.py`（`fetch_macro_data`）。
- [x] **F2.4** `sources/industry_news.py`（`fetch_industry_news`）。
  - 每条验收：`tests/test_sources.py` 对应用例，验证参数组装 + 降级标记透传正确。

## Phase 2.5 · 知识库与真实操作记录（新增，Phase 4 的 agent 会依赖这里的 `knowledge.py`）

- [x] **F2.5.1** `models.py` 补充 `ActualOperation` / `LessonLearned` / `FundProfile`（含 `ProfileObservation`）/ `MarketPatternEntry`；`storage.py` 补充对应读写函数（见 [03_data_model.md](03_data_model.md) 第 6 节）。
  - 验收：`tests/test_models.py` / `tests/test_storage.py` 补充用例，写入再读回内容一致。
- [x] **F2.5.2** `knowledge.py::upsert_fund_profile` / `get_fund_profile`，`knowledge.py::append_lesson_from_review` / `query_lessons`（按 `tags` + `applicable_scope` 过滤，且只返回 `status="active"`）。
  - 验收：`tests/test_knowledge.py` 覆盖"追加观察不覆盖旧记录"、"按 tag/scope 过滤正确"、"deprecated 条目不返回"。
- [x] **F2.5.3** `knowledge.py::match_market_patterns`（按 `applicable_condition` 做简单日期/关键字规则匹配，不做语义检索）。
  - 验收：`tests/test_knowledge.py` 覆盖"命中"和"不命中"两类用例。
- [x] **F2.5.4** 初始化 `data/knowledge_base/market_patterns/patterns.json` 种子数据（人工整理 ≥ 5 条近几十年市场规律，AI 可协助起草，用户审阅后入库，见 [10_knowledge_base.md](10_knowledge_base.md) 第 6 节）。
  - 已写入 6 条草稿（春季躁动/红包行情/美林时钟/降息周期利好权益估值/两会政策窗口/年末红利低估值效应），经用户审阅批准后入库，均通过 `MarketPatternEntry` 校验。
  - 验收：`load_market_patterns()` 能正确读出 ≥ 5 条，字段完整。
- [x] **F2.5.5** `cli.py::record-operation` 子命令，手工录入 `ActualOperation`。
  - 验收：`tests/test_cli.py` 调用 `main(["record-operation", ...])`，覆盖正常落盘 + 可选参数（amount-unit/related-signal-id/note），断言落盘内容正确且不发起任何网络/LLM 调用。

## Phase 3 · 规则引擎

- [x] **F3.1** `rules.py::check_base_profit`（Target1，含 30 天豁免逻辑）。
- [x] **F3.2** `rules.py::classify_bull_alert`（Target2，含置信度分界）。
- [x] **F3.3** `rules.py::crash_priority_over_profit` + 合并裁决辅助函数。
  - 每条验收：`tests/test_rules.py` 覆盖设计文档列出的边界用例。
  - 实现说明：`classify_bull_alert` 的 `surge_upper_target` 解读为"暴涨预期上限"，超出上限视为预测过于激进同样只标观察；合并裁决函数 `resolve_final_decision` 只处理"止盈 vs 暴跌"两条自动化路径的优先级仲裁，`"减仓"` 不由规则引擎自动产出，留给上层 agent 结合 LLM 判断。

## Phase 4 · LLM + Prompt + Agents

- [x] **F4.1** `llm.py`：`call_llm`，先实现 `"fake"` provider（固定/可配置返回），预留 `"openai"` 分支（可先 `NotImplementedError` 占位）。
  - 实现说明：`call_llm` 本身只做 provider 级别的薄分发（`fake` 返回固定占位 JSON `"{}"`，`openai` 抛 `NotImplementedError`，未知 provider 抛 `ValueError`）；各 agent 真正做单测时不依赖这个占位值，而是各自在函数签名里注入 `call_llm_fn` 参数（与 `adapter.py` 的 `request_fn` 同一套注入约定），测试传入返回特定 JSON 的 fake 函数。
- [x] **F4.2** `prompts/*.md` 四个模板文件落地（内容取自 draft 第五章，变量化改造，新增 `knowledge_context` 占位）+ 模板加载/渲染函数 + 快照测试。
  - 验收：`tests/test_llm.py` 覆盖 `load_prompt` 正常渲染、缺变量报错、四个模板文件存在且带 `required_vars` 头注释。
- [x] **F4.3** `agents/position_analyst.py`（Target1 + Target4 论证组装；调用 `knowledge.get_knowledge_context(...)` 注入 prompt，分析完成后调用 `knowledge.upsert_fund_profile(...)` 追加观察）。
  - 实现说明：新增了 `knowledge.get_knowledge_context(config, fund_code, as_of) -> dict`（05_agents_skills_prompts.md 提到但 F2.5.2/F2.5.3 未覆盖，在这里补上），合并 `get_fund_profile` + `query_lessons`（按 `fund_code` scope）+ `match_market_patterns`（仅走月份规则，不传 `macro_context`）。`run(...)` 返回 dict（不含 `bull_alert`/`crash_risk`），由 Phase 5 `orchestrator.py` 合并成完整 `AnalysisRecord`。
- [x] **F4.4** `agents/bull_scanner.py`（Target2；同样消费 `knowledge_context`）。
  - 实现说明：没有独立"资金流向"数据源，`fund_flow_summary` 暂用 `fund_info` 数据近似代替；`expected_gain` 解析取区间上限（如 "0.1~0.2" 取 0.2）喂给 `rules.py::classify_bull_alert` 做二次裁决；数据降级时把 `data_warning` 追加进 `reason_list`，保证可见性。
- [x] **F4.5** `agents/risk_alert.py`（Target3；同样消费 `knowledge_context`）。
  - 实现说明：没有独立"债市"数据源，`bond_rate_summary` 暂用 `macro_data` 近似代替；`prev_analysis_summary` 由调用方（orchestrator）传入上一次分析摘要；数据降级时把 `data_warning` 追加进 `bad_factors`。
- [x] **F4.6** `agents/weekly_reviewer.py`（复盘统计 + 误差分类 + 新增因子生成；产出 `new_analysis_factors` 后必须调用 `knowledge.append_lesson_from_review(...)` 落成 `LessonLearned`）。
  - 每条验收：`tests/test_agents.py` 用 fake provider + fake 数据，断言输出模型字段符合预期，且 `data_warning` 传导正确；F4.3/F4.6 额外断言 `knowledge_base` 对应文件被正确写入。
  - 实现说明：命中率/准确率等数字直接取 LLM 输出（不在代码里重新计算），但做了防御性解析——非法数值用默认值兜底，比率字段强制夹到 `[0,1]`；`agents/_common.py` 新增了 `coerce_int`/`coerce_rate` 共享工具函数。

## Phase 5 · 编排落盘

- [x] **F5.1** `agents/orchestrator.py::run_daily`：串联 Phase 2~4，合并为 `AnalysisRecord` 列表，落盘，必要时写 `trade_decision`。
  - 验收：集成测试跑通，断言"暴跌优先于止盈"的合并规则生效。
  - 实现说明：没有独立的"当前持仓清单"数据源/模型，`holdings` 由调用方显式传入（每项含 `fund_code`/`buy_cost`/`hold_days`/`current_yield`，`fund_name`/`industries` 可选）；`risk_alert` 的 `prev_analysis_summary` 取 `as_of` 前一天 `analysis_log` 中同一基金的 `next_week_trend_text`；`crash_risk.is_crash` 为真时只生成"暴跌预警"`trade_decision`，不会额外生成"止盈"（已用集成测试验证优先级）；新增 `rules.cap_confidence_when_degraded` 并接入 `bull_scanner.py`，`data_warning` 非空时强制封顶 `confidence` 到 `confidence_threshold - 1`。
- [x] **F5.2** `agents/orchestrator.py::run_weekly`：读历史 + 调用 `weekly_reviewer` + 落盘 `weekly_review_log` + 回填 `performance_db`。
  - 验收：集成测试跑通，`.json`/`.md` 均生成且内容一致。
  - 实现说明：`run_weekly` 本身仍是 `review_week`/`analysis_records`/`trade_decisions`/`real_nav_data`（`fund_code -> 本周真实收益率`）均由调用方显式传入的低层函数，保持简单可测；`agents/orchestrator.py` 里新增了 `compute_default_week`/`load_week_analysis_records`/`load_week_trade_decisions` 三个辅助函数供 F6.1 的 `cli.py fund weekly` 使用（比原计划提前实现，F7.3.3 的 Optional 范围收窄为仅剩"Web UI 复用 + 显式格式/范围校验"）。`performance_db` 回填用 `agents/_common.py::parse_expected_gain`（从 `bull_scanner.py` 提取为共享函数）解析 `bull_alert.expected_gain` 得到 `predict_return`；当前没有历史净值数据源，`real_nav_data` 由 `cli.py` 侧固定传空 dict，`performance_db` 回填相应留空（文档化限制，见 F7.2）。

## Phase 6 · CLI 入口

- [x] **F6.1** `cli.py`：`fund daily [--fund-code]`、`fund weekly [--week]`。
  - 验收：`tests/test_cli.py` 调用 `main(["daily"])`/`main(["weekly"])`，断言退出码与落盘结果。
  - 实现说明：没有独立的"持仓快照"数据源，`fund daily` 的持仓清单由新增的 `orchestrator.build_holdings_from_operations(config, as_of)` 从 `actual_operations` 流水按加权平均成本法重建（份额归零后再次买入视为重新建仓，`hold_days` 从新建仓日起算；已清仓基金不纳入）；`--fund-code` 过滤后若不在当前持仓中则跳过本次研判（退出码仍为 0，打印提示）。`fund weekly` 的 `--week` 缺省时用 `orchestrator.compute_default_week` 取"上一周"，`analysis_records`/`trade_decisions` 用 `orchestrator.load_week_analysis_records`/`load_week_trade_decisions` 按周读取；`real_nav_data` 暂固定传空 dict（无历史净值数据源）。
- [x] **F6.2** `README.md` 补充真实可执行的使用说明（安装、配置、运行、测试）。

## Phase 7 · Optional（非必须，按需触发）

- [ ] **F7.1（Optional）** 真实 LLM provider 接入 `llm.py`（如 OpenAI 兼容接口）。
- [ ] **F7.2（Optional）** 真实数据源接口接入（替换 `sources/*.py` 中的样例数据为真实 `endpoint`）。
- [ ] **F7.3（Optional）** 本地最小 Web UI，详细设计见 [11_web_ui.md](11_web_ui.md)，拆成以下子项：
  - [ ] **F7.3.1** `web.py` 骨架 + 登录（`/login`、`POST /api/login`、`POST /api/logout`、session cookie、失败次数锁定）。
    - 验收：新增 `tests/test_web.py`，覆盖"密码正确登录成功/密码错误 401/未登录访问 `/` 302 到 `/login`/连续失败 5 次后 429"。
  - [ ] **F7.3.2** `orchestrator.py::list_missing_weekly_reviews` + `GET /api/todo`。
    - 验收：`tests/test_web.py` 断言缺失周列表正确（含"跳过当前自然周"、"`lookback_weeks` 截断"两类用例）。
  - [ ] **F7.3.3** `orchestrator.py::compute_default_week` + `run_weekly(config, week=None)` 支持显式周参数与格式/范围校验；`POST /api/weekly`、`cli.py --week` 均复用这一个函数。
    - 验收：`tests/test_rules.py` 或新建用例覆盖"不传週取上一周"、"传非法格式报错"、"传未来周报错"。
  - [ ] **F7.3.4** `web_static/{login.html,index.html,app.js,style.css}` 静态页面，主页面含 Daily/Weekly 操作区 + 右下角可收起 TODO 小窗口。
    - 验收：手工验收（无自动化 UI 测试要求），对照 [11_web_ui.md](11_web_ui.md) 第 3/4 节逐项检查。
- [ ] **F7.4（Optional）** 定时任务（`launchd`/`cron`）自动触发 daily/weekly（需用户确认后再配置）。

## 进度追踪方式

实现时直接在本文件勾选 `[ ]` → `[x]`，作为唯一进度来源，不另建进度文档。
