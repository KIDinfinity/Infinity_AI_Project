# Week 03 · 结构化输出 / 流式 / 成本 + DA-01 场景选型（Phase 1 · Day11–Day14 · 10-12 → 10-15）

## 1. 本周核心目标

1. 把 W2 的 LLM Gateway v0 补齐为「可用于产品」的调用层：**结构化输出（Pydantic 校验 + 失败重试）、SSE 流式、Token/成本记录、Prompt 版本化**。
2. **从痛点池中选定 DA-01 的主场景包（1 主 + 1 辅）**，写出 `da01-definition.md`（8 要素 + 成功指标 + 不做清单 + W4 语料计划）。
3. 交付 **WorkPilot v0.1**：一个「无检索的技术文档助手 v0」+ 10 题冒烟 + 首批幻觉 Badcase，用证据说明「为什么下周必须做 RAG」。

## 2. 资产锚点

| 项                            | 内容                                                                                                                                                                                                                                                                                                                         |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 构建模块                      | M1.3 Structured Output、M1.4 Streaming、M1.5 Token/成本计量、M1.6 Prompt 版本化、M10 场景包选型、M3.4 Badcase 库（首批条目）                                                                                                                                                                                                 |
| 版本里程碑                    | **v0.1**（tag `v0.1.0`，Day14）                                                                                                                                                                                                                                                                                              |
| 本周结束 WorkPilot 能演示什么 | ① `curl -N` 看到 `/v1/chat/stream` 逐 token 输出并在 `done` 事件里给出 tokens/成本/延迟；② `scripts/chat.py` 多轮 CLI 聊天 + `/cost`；③ `/v1/structured/answer`、`/v1/structured/breakdown` 返回通过 Pydantic 校验的 JSON；④ `/v1/ask` 文档助手 v0 + 10 题冒烟报告；⑤ `docs/product/da01-definition.md` 写明主场景与语料计划 |

## 3. 为什么这一周存在

- RAG（W4）、Agent（W9+）、评测 judge（W5）全部依赖「结构化输出 + 流式 + 成本记录」：不先补齐，后面每个模块都会各写一套调用代码。
- GLOBAL_CONTEXT 要求「最晚第 3 周明确 DA-01 解决什么问题」。Day13 是 Phase 1 最重要的决策日：它决定 W4 用什么语料、W5 评测什么问题、W17–18 做哪个场景包。
- v0.1 的冒烟 + 幻觉案例是 P1 作品集「为什么需要 RAG」的第一手证据（面试时能讲「我先做了无检索基线，量化了幻觉」）。

## 4. 本周在路线中的位置

```text
W2 产出：FastAPI 骨架 + M1 LLM Gateway v0（POST /v1/chat，timeout/retry）
        + MinIO/Qdrant/Ollama bge-m3 可用 + 备份脚本 + 痛点池 ≥10 条 + 能力矩阵
   ↓
W3（本周）：Gateway 补齐 结构化 / 流式 / 成本 / Prompt 版本
        → Day13 选定主场景包（1 主 + 1 辅）+ W4 语料计划
        → Day14 无检索文档助手 v0 + 10 题冒烟 + 幻觉 Badcase → tag v0.1.0
   ↓
W4 输入：da01-definition.md 的语料计划、StructuredAnswer schema、prompts/ 体系、
        gateway.stream()、llm_calls.jsonl 成本日志、badcases.md（RAG 要修复的问题）
```

## 5. 每日安排

| Day   | 日期  | Task                                        | 当日 P0 产出                                                                                                                    | 模块        | 状态 |
| ----- | ----- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------- | ---- |
| Day11 | 10-12 | Task 1：Structured Output + Prompt 版本化   | `app/llm/structured.py`、`app/llm/prompts.py`、`prompts/*.v1.md`、`POST /v1/structured/answer` + `/breakdown`、5 输入校验通过率 | M1.3 M1.6   | DONE |
| Day12 | 10-13 | Task 2：Streaming SSE + 成本记录 + CLI 聊天 | `gateway.stream()`、`POST /v1/chat/stream`、`app/llm/pricing.py`、`data/logs/llm_calls.jsonl`、`scripts/chat.py`                | M1.4 M1.5   | DONE |
| Day13 | 10-14 | Task 3：DA-01 决策——场景包选型              | 评分矩阵 + `docs/product/da01-definition.md`（含 W4 语料计划）+ 三处状态回填                                                    | M10         | DONE |
| Day14 | 10-15 | Task 4：LLM 应用 v0 + 10 题冒烟             | `POST /v1/ask`(+stream)、`eval/datasets/smoke_v0.jsonl`、`eval/runners/run_smoke.py`、`eval/badcases/badcases.md`、tag `v0.1.0`  | v0.1 / M3.4 | DONE |

## 6. 本周必须留下的资产（文件路径级）

仓库 `~/lab/workpilot`：

```text
prompts/structured_answer.v1.md
prompts/task_breakdown.v1.md
prompts/qa_answer.v0.md
apps/api/app/llm/schemas.py          # Usage / ChatResult / StructuredAnswer / TaskBreakdown
apps/api/app/llm/prompts.py          # front matter 解析 + 渲染
apps/api/app/llm/structured.py       # generate_structured()
apps/api/app/llm/pricing.py          # calc_cost()
apps/api/app/llm/usage_log.py        # 追加 data/logs/llm_calls.jsonl
apps/api/app/llm/gateway.py          # chat() 返回 ChatResult + stream()
apps/api/app/routes/structured.py    # /v1/structured/*
apps/api/app/routes/chat.py          # /v1/chat/stream
apps/api/app/routes/ask.py           # /v1/ask、/v1/ask/stream
apps/api/tests/test_structured.py  test_pricing.py  test_sse.py
scripts/chat.py
eval/runners/run_smoke.py
eval/datasets/smoke_v0.jsonl
eval/reports/20261015-smoke-v0.1.md
eval/badcases/badcases.md
docs/product/da01-definition.md
README.md（v0.1 章节）  .env.example（价格键、PROMPTS_DIR）
git tag v0.1.0
```

`~/lab/projects`：`product-lab/pain-pool.md`（追加评分矩阵）。
本目录：`PROJECT_CONFIG.md`（DA-01 状态）、`plan/plan_ai/DA01_TARGET_ASSET.md`（M10 标注已选）、`plan/CHANGELOG.md`（追加一条）。

## 7. 本周验收标准（PASS/FAIL 勾选）

- [x] `uv run pytest -m "not llm"` 全绿；`uv run pytest -m llm -s` 中 5 个结构化输入校验通过 ≥ 4/5（含重试）→ **32 passed, 2 deselected**；live 通过率 **5/5, first-try: 5/5**（0 次重试）
- [x] `curl -N` 调 `/v1/chat/stream` 可见逐段 `event: token`，最后有 `event: done` 且含 `usage`、`cost`、`latency_ms`
- [x] `data/logs/llm_calls.jsonl` 每次调用新增 1 行，字段含 `request_id/model/tokens/cost/latency_ms`（当前 69 行）
- [x] `scripts/chat.py` 可多轮对话，`/cost` `/reset` `/exit` 可用
- [x] `prompts/` 下每个 prompt 带 front matter（id/version/model/changelog），代码只通过 `load_prompt()` 读取
- [x] `docs/product/da01-definition.md` 存在：8 要素 + 成功指标 + 明确不做 + W4 语料计划（30–80 篇、来源与合规检查）
- [x] 评分矩阵有加权总分，主场景/辅场景选择理由可追溯到分数（3 条候选：3.90 / 3.85 / 3.35）
- [x] `PROJECT_CONFIG.md` DA-01 状态已回填，CHANGELOG 已追加
- [x] 10 题冒烟报告存在，`badcases.md` ≥ 3 条幻觉案例（实为 **9 条**，含 1 条 prompt 约束类）
- [ ] `git tag` 中有 `v0.1.0` 且已 push 到 Gitea → ⏭️ **未做：用户明确要求本轮不提交、不 push**（代码与文档均已就位，commit 后一个命令即可补 tag）

## 8. 求职映射

- 本周能力：LLM API 工程化（Structured Output / JSON mode / Pydantic 校验重试）、SSE 流式、Token 成本核算、Prompt 版本管理、AI 产品场景选型（加权评分）。
- 简历 bullet 草稿：
  - 「设计统一 LLM Gateway：基于 Pydantic v2 的结构化输出（JSON mode + schema 注入 + 校验失败自动修复重试），结构化调用校验通过率达 ＿＿%；SSE 流式输出首 token 延迟 ＿＿ms；每次调用记录 tokens/成本/延迟，单次平均成本 ¥＿＿。」
  - 「以 8 维加权评分矩阵从 ＿＿ 个真实研发痛点中选定产品主场景，定义成功指标（每周节省 ＿＿ 小时）并据此规划语料与评测。」
- 面试题：
  1. JSON mode 和 function calling / strict structured outputs 有什么区别？模型输出不合 schema 怎么办？（答要点：JSON mode 只保证合法 JSON 不保证 schema；schema 注入 + Pydantic 校验 + 把错误回灌重试；必要时降级。）
  2. 为什么用 SSE 而不是 WebSocket 做 LLM 流式？（答要点：单向、基于 HTTP、自动重连、代理友好；需要双向时才用 WS。）
  3. 你怎么决定先做哪个 AI 场景？（答要点：频率×耗时×AI 适配×数据合规×可评测，用评分矩阵 + 硬性门槛。）

## 9. 本周禁止事项

- 不做检索 / 向量入库（W4）；Day14 的 `/v1/ask` 明确「无检索」。
- 不引入 LangChain / LlamaIndex / instructor 等框架做结构化输出，手写 30 行即可。
- 不为价格表写死数值（从官方定价页填到 `.env`）；不做成本看板（W15）。
- 不做前端页面（W6）；CLI + curl 足够演示。
- Day13 不允许「都想做」：只能 1 主 + 1 辅，其余进 Backlog。
- 不用公司真实文档/代码做测试输入（合规红线 §8）。

## 10. 时间不够时（最小保留）

1. Day11：`generate_structured()` + `StructuredAnswer` + `/v1/structured/answer`（breakdown 可顺延）。
2. Day12：`gateway.stream()` + `/v1/chat/stream` + jsonl 日志（CLI 可顺延到 Day14 前半小时）。
3. Day13：**不可裁剪**——评分矩阵 + 选型 + da01-definition 的「问题/用户/场景/价值」+ 语料计划。
4. Day14：`/v1/ask` + 10 题冒烟 + 3 条 badcase + tag（流式版、README 美化可延期）。

## 11. 周复盘（周末填写）

- 完成：
  - Day11：`generate_structured()`（JSON mode + schema 注入 + Pydantic 校验 + 错误回灌重试 1 次）、`load_prompt()`（front matter + `{标识符}` 渲染）、`/v1/structured/answer` + `/breakdown`；live 通过率 **5/5（first-try 5/5）**。
  - Day12：`gateway.stream()` + `/v1/chat/stream`（SSE `token`/`done`）、`pricing.py::calc_cost()`、`data/logs/llm_calls.jsonl`（现 69 行）、`scripts/chat.py`（`/cost` `/reset` `/exit`）。
  - Day13：8 维加权评分矩阵（3 条候选）→ 主场景 **SP-A 深化**（3.90 / 3.85）；`docs/product/da01-definition.md`（8 要素 + 成功指标 + 不做 8 条 + W4 语料 30–80 篇）；`PROJECT_CONFIG.md` 回填。
  - Day14：`prompts/qa_answer.v0.md`、`POST /v1/ask` + `/v1/ask/stream`（带 `source_note`）、`eval/datasets/smoke_v0.jsonl`（10 题）、`eval/runners/run_smoke.py`、冒烟报告、`eval/badcases/badcases.md`（9 条）、README v0.1 章节。
- 未完成及原因：
  1. **tag `v0.1.0` 未创建 / 未 push**　原因：用户明确要求本轮不提交代码（PLAN §6 Step 5 的 `git add/commit/tag/push` 整体跳过）。
  2. **辅场景未选**（W3 目标为 1 主 + 1 辅）　原因：Day13 按精简版执行，只打 3 条候选分；不影响 W4（W4 只需主场景语料）。已记入 `DA01_TARGET_ASSET.md` §11 M10 标注。
  3. `ruff format` 在仓库级仍报 7 个文件待格式化　原因：均为 Day11–12 早于本次的既有文件（`config.py`/`gateway.py`/`pricing.py`/`schemas.py`/`chat.py`/`test_sse.py`/`scripts/chat.py`）；本次新增的 `run_smoke.py` 已单独 format 过；`ruff check` 全绿。
  4. `data/logs/llm_calls.jsonl` 里混有空跑的测试记录（如 `model: fake-model`），本周未清理　原因：`test_pricing.py` 与冒烟脚本共用同一日志路径；W5 做成本看板前需按 `model` 字段过滤或给测试单独配日志路径。
- WorkPilot 本周多了什么可演示的东西：
  - `POST /v1/ask` → 结构化回答 + `source_note: 来源：模型通用知识（未接入知识库）` + tokens/成本/延迟；`curl -N /v1/ask/stream` 可见 340 个 `event: token` 后接 1 个 `event: done`（含 `ttft_ms`）。
  - 一条命令出评测报告：`uv run --project apps/api python eval/runners/run_smoke.py`。
  - 首份「无检索基线」证据：10 题成功后的人均可读结论——私有题 8/8 拒答，0 条高置信幻觉。
- 结构化通过率 / 首 token 延迟 / 单次平均成本：**5/5（first-try 5/5）** / **434 ms**（`/v1/ask/stream` 实测） / **¥0.001646**（`/v1/ask` 实测，703 tok）
  - 补充：冒烟 10 题平均延迟 **1816 ms**、平均成本 **¥0.001194**、总成本 **¥0.011937**、low 置信占比 **40%**。
- 选定的主场景 / 辅场景：**SP-A 深化（团队规范与组件库用法问答 · 带引用 Grounded Q&A）** / **待定**（理由一句话：P-02 与 P-07 的缺口是同一个「AI 不知道团队规范」，合并后加权分最高 3.90/3.85，且直接给 W4 RAG 定验收目标。）
- 是否出现无效学习或范围扩张：**无新增**。本周所有产出都挂在 M1.3–M1.6 / M10 / M3.1 / M3.4 下；未引入 LangChain / LlamaIndex / instructor，未碰向量检索、前端，符合 §9 禁止事项。唯一偏差是文件放置：按 `PROJECT_STANDARD.md` §1 把冒烟脚本放在 `eval/runners/`（PLAN 原写 `scripts/`），已记录在 Day14 执行记录。
- 下周调整：
  1. **先补 P0**：commit + `git tag -a v0.1.0` + push（或按用户意愿合并到 W4 首个 commit）。
  2. W4 按 `da01-definition.md` §4 准备 30–80 篇语料；切分时必须覆盖仓库里的**真实入口**（`PROJECT_STANDARD.md` / `README.md` / `.env.example` / `docs/`），因为 badcase 显示模型会推荐 `CONTRIBUTING.md`、`LICENSE` 这类并不存在的文件。
  3. 补选辅场景（1 主 + 1 辅 未闭环）。
