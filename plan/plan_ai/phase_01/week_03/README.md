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
| Day11 | 10-12 | Task 1：Structured Output + Prompt 版本化   | `app/llm/structured.py`、`app/llm/prompts.py`、`prompts/*.v1.md`、`POST /v1/structured/answer` + `/breakdown`、5 输入校验通过率 | M1.3 M1.6   | TODO |
| Day12 | 10-13 | Task 2：Streaming SSE + 成本记录 + CLI 聊天 | `gateway.stream()`、`POST /v1/chat/stream`、`app/llm/pricing.py`、`data/logs/llm_calls.jsonl`、`scripts/chat.py`                | M1.4 M1.5   | TODO |
| Day13 | 10-14 | Task 3：DA-01 决策——场景包选型              | 评分矩阵 + `docs/product/da01-definition.md`（含 W4 语料计划）+ 三处状态回填                                                    | M10         | TODO |
| Day14 | 10-15 | Task 4：LLM 应用 v0 + 10 题冒烟             | `POST /v1/ask`(+stream)、`eval/datasets/smoke_v0.jsonl`、`scripts/run_smoke.py`、`eval/badcases/badcases.md`、tag `v0.1.0`      | v0.1 / M3.4 | TODO |

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
scripts/chat.py  scripts/run_smoke.py
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

- [ ] `uv run pytest -m "not llm"` 全绿；`uv run pytest -m llm -s` 中 5 个结构化输入校验通过 ≥ 4/5（含重试）
- [ ] `curl -N` 调 `/v1/chat/stream` 可见逐段 `event: token`，最后有 `event: done` 且含 `usage`、`cost`、`latency_ms`
- [ ] `data/logs/llm_calls.jsonl` 每次调用新增 1 行，字段含 `request_id/model/tokens/cost/latency_ms`
- [ ] `scripts/chat.py` 可多轮对话，`/cost` `/reset` `/exit` 可用
- [ ] `prompts/` 下每个 prompt 带 front matter（id/version/model/changelog），代码只通过 `load_prompt()` 读取
- [ ] `docs/product/da01-definition.md` 存在：8 要素 + 成功指标 + 明确不做 + W4 语料计划（30–80 篇、来源与合规检查）
- [ ] 评分矩阵有加权总分，主场景/辅场景选择理由可追溯到分数
- [ ] `PROJECT_CONFIG.md` DA-01 状态已回填，CHANGELOG 已追加
- [ ] 10 题冒烟报告存在，`badcases.md` ≥ 3 条幻觉案例
- [ ] `git tag` 中有 `v0.1.0` 且已 push 到 Gitea

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

- 完成：＿＿
- 未完成及原因：＿＿
- WorkPilot 本周多了什么可演示的东西：＿＿
- 结构化通过率 / 首 token 延迟 / 单次平均成本：＿＿ / ＿＿ / ＿＿
- 选定的主场景 / 辅场景：＿＿ / ＿＿（理由一句话：＿＿）
- 是否出现无效学习或范围扩张：＿＿
- 下周调整：＿＿
