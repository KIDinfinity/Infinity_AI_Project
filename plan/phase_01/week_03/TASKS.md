# Week 03 · TASKS

## Task 1：Structured Output + Prompt 版本化（Day11 · 10-08）

### 做什么

- 新建 `prompts/` 体系：`structured_answer.v1.md`、`task_breakdown.v1.md`，文件头 front matter（id / version / model / changelog），正文用 `{placeholder}`。
- `app/llm/prompts.py`：解析 front matter + 安全渲染（只替换 `{标识符}`，不破坏 JSON 花括号）。
- `app/llm/structured.py`：`async generate_structured(model_cls, messages)`——`response_format={"type":"json_object"}` + system prompt 注入 `model_json_schema()` + Pydantic 校验，`ValidationError` 时把错误回灌模型重试 1 次。
- Schema：`StructuredAnswer`、`TaskBreakdown`；路由 `POST /v1/structured/answer`、`POST /v1/structured/breakdown`。
- Gateway 小改：`chat()` 透传 `**extra` 并返回 `ChatResult(content, model, usage, latency_ms)`。

### 为什么做

后续 RAG 回答、LLM-judge、Agent 规划、SP-B 任务拆解都需要「可校验的 JSON」。Prompt 版本化是评测报告「配置快照」能记录 prompt 版本的前提。

### 资产锚点

M1.3 Structured Output、M1.6 Prompt 版本化；为 v0.1 做准备。

### 前置依赖

Day08 的 `LLMGateway.chat`（异步、带 timeout/retry）与 `POST /v1/chat` 可用；`.env` 中 DeepSeek key 可用。

### 具体执行步骤（概要，详细见 day11_20261008/PLAN.md）

1. Gateway 返回 `ChatResult`，透传 `response_format` 等参数。
2. 写 2 个 prompt 文件 + `prompts.py` 加载器 + 单测。
3. 写 schemas + `generate_structured()` + 假 Gateway 单测（第一次非法、第二次合法）。
4. 挂路由，curl 验证。
5. 5 个真实输入的 `@pytest.mark.llm` 测试，记录通过率。
6. 提交。

### 验收标准

- [ ] `uv run pytest -m "not llm"` 全绿（含重试逻辑单测）
- [ ] `uv run pytest -m llm -s` 打印通过率，≥ 4/5
- [ ] 两个路由 curl 返回 JSON 且字段合法（`confidence ∈ low|mid|high`，`type ∈ frontend|backend|test|doc`）
- [ ] 代码中没有内联长 prompt，全部 `load_prompt("xxx.v1")`

### 完成后的产出（文件路径）

`prompts/structured_answer.v1.md`、`prompts/task_breakdown.v1.md`、`apps/api/app/llm/{schemas,prompts,structured}.py`、`apps/api/app/routes/structured.py`、`apps/api/tests/test_prompts.py`、`apps/api/tests/test_structured.py`

### 求职映射

AI Engineer / LLM Application Engineer：「Structured Output + 校验重试」是 JD 高频词；面试常问「LLM 输出格式不稳定怎么办」。

### 如果时间不够 / 没有必要

保留 `StructuredAnswer` + `/answer`；`TaskBreakdown` + `/breakdown` 顺延到 Day14 前（它是 SP-B 预演，不阻塞 v0.1）。

---

## Task 2：Streaming SSE + 成本记录 + CLI 聊天（Day12 · 10-09）

### 做什么

- `gateway.stream()` 异步生成器：`stream=True` + `stream_options={"include_usage": True}`（先查 DeepSeek 文档确认），yield token 事件，最后 yield 带 usage/cost/latency/ttft 的 done 事件；拿不到 usage 时按字符估算并标记 `usage_estimated`。
- `POST /v1/chat/stream`：`StreamingResponse(media_type="text/event-stream")`，事件 `token` / `done` / `error`。
- `app/llm/pricing.py`：价格从配置读取（值从 DeepSeek 官方定价页抄到 `.env`），`calc_cost(usage)`。
- `app/llm/usage_log.py`：每次调用追加一行到 `data/logs/llm_calls.jsonl`。
- `scripts/chat.py`：httpx 流式消费 SSE，多轮 history，支持 `/cost` `/reset` `/exit`。

### 为什么做

流式是 AI UX 的基本要求（W6 Web Console 直接复用）；成本记录是 P1 指标「单次成本 < ¥0.02」的数据来源，也是 W15 成本账本的原型。

### 资产锚点

M1.4 Streaming、M1.5 Token/成本计量；为 v0.1 做准备。

### 前置依赖

Task 1 的 `ChatResult` / `Usage`。

### 具体执行步骤（概要，详细见 day12_20261009/PLAN.md）

1. 查 DeepSeek 文档：`stream_options`、usage 字段、定价单位。
2. config 加价格键与日志路径；写 `pricing.py` + 单测。
3. 写 `usage_log.py`，在 `chat()` 中接入。
4. 写 `gateway.stream()` + `/v1/chat/stream` + SSE 单测（假 Gateway）。
5. `curl -N` 验证；写 `scripts/chat.py`。
6. 提交。

### 验收标准

- [ ] `curl -N` 能看到多条 `event: token` 和一条 `event: done`
- [ ] `done` 中 `usage.total_tokens > 0`、`cost` 非空（已配置价格时）、`latency_ms`、`ttft_ms`
- [ ] 每次调用 `wc -l data/logs/llm_calls.jsonl` +1
- [ ] `scripts/chat.py` 3 轮对话后 `/cost` 显示累计成本，`/reset` 后模型不记得上文
- [ ] `test_pricing.py`、`test_sse.py` 通过

### 完成后的产出（文件路径）

`apps/api/app/llm/{gateway,pricing,usage_log}.py`、`apps/api/app/routes/chat.py`、`apps/api/tests/{test_pricing,test_sse}.py`、`scripts/chat.py`、`.env.example`（价格键）

### 求职映射

AI Full-Stack / AI Engineer：「Streaming + 成本控制」是生产化 LLM 应用的必问点。

### 如果时间不够 / 没有必要

P0 = stream + SSE 路由 + jsonl 日志；`scripts/chat.py` 的 `/cost` 可简化为只打印每轮 done 信息。

---

## Task 3：DA-01 决策——场景包选型（Day13 · 10-10）

### 做什么

- 以 `product-lab/pain-pool.md` 为输入，用 8 维评分矩阵（频率、单次耗时、AI 适配度、数据可得且合规、可评测性、求职相关度、商业化潜力、实现成本-反向）加权打分，设置合规硬门槛。
- 每个痛点映射到 SP-A..SP-F 或「新」；选 1 主 + 1 辅（SP-A 始终是基线）。
- 写 `~/lab/workpilot/docs/product/da01-definition.md`：8 要素 + 成功指标 + 明确不做 + **W4 语料计划**。
- 同步回填：`PROJECT_CONFIG.md`、`plan/DA01_TARGET_ASSET.md` M10、`plan/CHANGELOG.md`。

### 为什么做

GLOBAL_CONTEXT 要求第 3 周明确 DA-01；蓝图 §1.3 规定场景包由真实痛点决定。W4 语料、W5 评测题、W17–18 场景包都以此为输入。

### 资产锚点

M10 Scenario Packs（选型）；DA01_TARGET_ASSET §12.4 / §12.5。

### 前置依赖

痛点池 ≥10 条且已分类（Day03 / Day10）。

### 具体执行步骤（概要，详细见 day13_20261010/PLAN.md）

1. 痛点池清洗（合并重复、补「每周发生次数 / 每次分钟数」）。
2. 映射 SP-A..F，打 8 维分，算加权总分。
3. 过硬门槛（合规 ≥3、可评测 ≥3），选 1 主 + 1 辅。
4. 写 da01-definition.md（含语料计划与合规检查清单）。
5. 同步三处文件 + 提交两个仓库。

### 验收标准

- [ ] `pain-pool.md` 中有评分矩阵表格，每行有加权总分
- [ ] da01-definition.md 8 要素齐全，成功指标可量化（如「每周节省 ≥ 2 小时」「hit@5 ≥ 0.85」）
- [ ] 「明确不做」≥ 5 条
- [ ] 语料计划列出 ≥ 3 类来源、目标篇数、许可证、合规检查方法
- [ ] PROJECT_CONFIG / DA01_TARGET_ASSET / CHANGELOG 三处已更新

### 完成后的产出（文件路径）

`~/lab/projects/product-lab/pain-pool.md`（评分矩阵）、`~/lab/workpilot/docs/product/da01-definition.md`、本目录三处状态文件

### 求职映射

AI Product Engineer / Solutions Engineer：能讲清「为什么做这个而不是那个」，是项目面试中区分「做 Demo」和「做产品」的关键。

### 如果时间不够 / 没有必要

不可跳过。可压缩：8 要素每项 2–3 句；语料计划先写来源与篇数，合规检查清单 Day15 补全。

---

## Task 4：LLM 应用 v0 + 10 题冒烟（Day14 · 10-11）

### 做什么

- 「技术文档助手 v0」：`POST /v1/ask`（无检索），system prompt 来自 `prompts/qa_answer.v0.md`，返回 `StructuredAnswer` + 来源标注「来源：模型通用知识（未接入知识库）」；`POST /v1/ask/stream` 流式版。
- `eval/datasets/smoke_v0.jsonl` 10 题（围绕 Day13 主场景，含 ≥3 道「团队内部知识」题）；`scripts/run_smoke.py` 输出表格（答案摘要 / 置信度 / 延迟 / 成本）。
- 观察幻觉 → `eval/badcases/badcases.md` 首批条目。
- README v0.1 章节、tag `v0.1.0`、Week 3 复盘。

### 为什么做

v0.1 是第一个可演示版本；无检索基线 + 幻觉证据是 RAG 的立项理由和 P1 作品集的对照组。

### 资产锚点

v0.1；M3.4 Badcase 库（首批）；M3.1 数据集规范（冒烟集雏形）。

### 前置依赖

Task 1–3。

### 具体执行步骤（概要，详细见 day14_20261011/PLAN.md）

1. 写 `qa_answer.v0.md` + `/v1/ask` + `/v1/ask/stream`。
2. 写 10 题冒烟集 + `run_smoke.py`，跑出报告。
3. 人工看答案，记录 ≥3 条幻觉 badcase。
4. README、tag、复盘。

### 验收标准

- [ ] `/v1/ask` 返回 `StructuredAnswer` + `source_note`
- [ ] `eval/reports/20261011-smoke-v0.1.md` 有 10 行结果 + 平均延迟 + 总成本
- [ ] `badcases.md` ≥ 3 条，每条有「现象 / 期望 / 根因：数据缺失或生成幻觉」
- [ ] `git tag` 有 `v0.1.0` 且已 push
- [ ] Week 3 README 第 11 节已填写

### 完成后的产出（文件路径）

`prompts/qa_answer.v0.md`、`apps/api/app/routes/ask.py`、`eval/datasets/smoke_v0.jsonl`、`scripts/run_smoke.py`、`eval/reports/20261011-smoke-v0.1.md`、`eval/badcases/badcases.md`、`README.md`

### 求职映射

「先建无检索基线、量化幻觉，再引入 RAG」是面试中很好的叙事起点（数据驱动而非跟风）。

### 如果时间不够 / 没有必要

流式版 `/v1/ask/stream` 与 README 美化可延期；冒烟 10 题、3 条 badcase、tag 不可省。

---
