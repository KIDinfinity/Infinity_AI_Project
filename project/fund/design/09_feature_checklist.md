# 09. 功能点实现清单（按顺序逐条推进）

> 使用方法：按 Phase 顺序、Phase 内按编号顺序实现。每条完成后对照「验收标准」自查，`uv run pytest` 全绿再进入下一条。不允许跳跃实现（如在 Phase 1 没完成前先写 Phase 3），除非该条明确标注 Optional。

## Phase 0 · 项目骨架

- [ ] **F0.1** 初始化 `pyproject.toml`（uv 项目，依赖：`pydantic`、`pytest`、`httpx`、`pyyaml`），`uv run pytest` 能跑通（哪怕 0 条用例）。
  - 验收：`uv sync` 成功；`uv run pytest` 退出码 0。
- [ ] **F0.2** `config.py`：`AppConfig` 模型 + `load_config()` + `${ENV}` 占位符替换。
  - 验收：`tests/test_config.py` 覆盖"合法加载/缺字段报错/环境变量替换"三类用例，全部通过。
- [ ] **F0.3** `models.py`：实现 [03_data_model.md](03_data_model.md) 中全部模型。
  - 验收：`tests/test_models.py` 覆盖"合法构造/字段越界报错/序列化往返一致"。
- [ ] **F0.4** `storage.py`：实现 [03_data_model.md](03_data_model.md) 末尾列出的全部读写函数。
  - 验收：`tests/test_storage.py` 写入再读回，内容与原对象一致；JSONL 追加不覆盖旧行。

## Phase 1 · 容错适配器

- [ ] **F1.1** `adapter.py`：实现状态机骨架（成功路径 + 401/403 失败路径），日志写入 `api_error_log`。
  - 验收：两类用例通过，且 `ApiErrorLogEntry` 被正确写入。
- [ ] **F1.2** 补全 429 / 5xx / 超时的指数退避重试（用注入的 `sleep_fn` 保证秒级跑完测试）。
  - 验收：模拟"重试 2 次后成功"和"重试耗尽"两种场景均断言正确。
- [ ] **F1.3** 补全备用 endpoint 切换逻辑。
  - 验收：主地址全部重试失败 -> 切备用 -> 备用成功 / 备用也失败两种场景均覆盖。
- [ ] **F1.4** 补全 payload 精简降级逻辑。
  - 验收：格式异常触发精简 -> 精简后成功 / 精简后仍失败两种场景均覆盖。

## Phase 2 · 数据源

- [ ] **F2.1** `sources/fund_info.py`（`fetch_fund_info`，先接 fake/本地样例数据，真实接口地址留空走 `config`）。
- [ ] **F2.2** `sources/stock_financial.py`（`fetch_stock_financial`）。
- [ ] **F2.3** `sources/macro_data.py`（`fetch_macro_data`）。
- [ ] **F2.4** `sources/industry_news.py`（`fetch_industry_news`）。
  - 每条验收：`tests/test_sources.py` 对应用例，验证参数组装 + 降级标记透传正确。

## Phase 2.5 · 知识库与真实操作记录（新增，Phase 4 的 agent 会依赖这里的 `knowledge.py`）

- [ ] **F2.5.1** `models.py` 补充 `ActualOperation` / `LessonLearned` / `FundProfile`（含 `ProfileObservation`）/ `MarketPatternEntry`；`storage.py` 补充对应读写函数（见 [03_data_model.md](03_data_model.md) 第 6 节）。
  - 验收：`tests/test_models.py` / `tests/test_storage.py` 补充用例，写入再读回内容一致。
- [ ] **F2.5.2** `knowledge.py::upsert_fund_profile` / `get_fund_profile`，`knowledge.py::append_lesson_from_review` / `query_lessons`（按 `tags` + `applicable_scope` 过滤，且只返回 `status="active"`）。
  - 验收：`tests/test_knowledge.py` 覆盖"追加观察不覆盖旧记录"、"按 tag/scope 过滤正确"、"deprecated 条目不返回"。
- [ ] **F2.5.3** `knowledge.py::match_market_patterns`（按 `applicable_condition` 做简单日期/关键字规则匹配，不做语义检索）。
  - 验收：`tests/test_knowledge.py` 覆盖"命中"和"不命中"两类用例。
- [ ] **F2.5.4** 初始化 `data/knowledge_base/market_patterns/patterns.json` 种子数据（人工整理 ≥ 5 条近几十年市场规律，AI 可协助起草，用户审阅后入库，见 [10_knowledge_base.md](10_knowledge_base.md) 第 6 节）。
  - 验收：`load_market_patterns()` 能正确读出 ≥ 5 条，字段完整。
- [ ] **F2.5.5** `cli.py::record-operation` 子命令，手工录入 `ActualOperation`。
  - 验收：`tests/test_cli.py` 调用 `main(["record-operation", ...])`，断言落盘内容正确；不调用任何 LLM/网络。

## Phase 3 · 规则引擎

- [ ] **F3.1** `rules.py::check_base_profit`（Target1，含 30 天豁免逻辑）。
- [ ] **F3.2** `rules.py::classify_bull_alert`（Target2，含置信度分界）。
- [ ] **F3.3** `rules.py::crash_priority_over_profit` + 合并裁决辅助函数。
  - 每条验收：`tests/test_rules.py` 覆盖设计文档列出的边界用例。

## Phase 4 · LLM + Prompt + Agents

- [ ] **F4.1** `llm.py`：`call_llm`，先实现 `"fake"` provider（固定/可配置返回），预留 `"openai"` 分支（可先 `NotImplementedError` 占位）。
- [ ] **F4.2** `prompts/*.md` 四个模板文件落地（内容取自 draft 第五章，变量化改造，新增 `knowledge_context` 占位）+ 模板加载/渲染函数 + 快照测试。
- [ ] **F4.3** `agents/position_analyst.py`（Target1 + Target4 论证组装；调用 `knowledge.get_knowledge_context(...)` 注入 prompt，分析完成后调用 `knowledge.upsert_fund_profile(...)` 追加观察）。
- [ ] **F4.4** `agents/bull_scanner.py`（Target2；同样消费 `knowledge_context`）。
- [ ] **F4.5** `agents/risk_alert.py`（Target3；同样消费 `knowledge_context`）。
- [ ] **F4.6** `agents/weekly_reviewer.py`（复盘统计 + 误差分类 + 新增因子生成；产出 `new_analysis_factors` 后必须调用 `knowledge.append_lesson_from_review(...)` 落成 `LessonLearned`）。
  - 每条验收：`tests/test_agents.py` 用 fake provider + fake 数据，断言输出模型字段符合预期，且 `data_warning` 传导正确；F4.3/F4.6 额外断言 `knowledge_base` 对应文件被正确写入。

## Phase 5 · 编排落盘

- [ ] **F5.1** `agents/orchestrator.py::run_daily`：串联 Phase 2~4，合并为 `AnalysisRecord` 列表，落盘，必要时写 `trade_decision`。
  - 验收：集成测试跑通，断言"暴跌优先于止盈"的合并规则生效。
- [ ] **F5.2** `agents/orchestrator.py::run_weekly`：读历史 + 调用 `weekly_reviewer` + 落盘 `weekly_review_log` + 回填 `performance_db`。
  - 验收：集成测试跑通，`.json`/`.md` 均生成且内容一致。

## Phase 6 · CLI 入口

- [ ] **F6.1** `cli.py`：`fund daily [--fund-code]`、`fund weekly [--week]`。
  - 验收：`tests/test_cli.py` 调用 `main(["daily"])`/`main(["weekly"])`，断言退出码与落盘结果。
- [ ] **F6.2** `README.md` 补充真实可执行的使用说明（安装、配置、运行、测试）。

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
