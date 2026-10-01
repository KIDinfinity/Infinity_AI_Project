# Week 15 · TASKS

## Task 1：Trace / Span + Trace 查看（Day52 · 11-18）

### 做什么

新建 `app/obs/trace.py`：contextvars 保存 `trace_id`（= request_id）与当前 span；`with span("llm.chat", **attrs) as s:` 记录 name、parent_id、开始/结束、status、attrs、error；请求结束批量写入 SQLite `Trace` / `Span` 表。在 Gateway、retrieve、tool execute、graph 节点四处埋点。新增 `GET /v1/ops/traces`、`GET /v1/ops/traces/{id}`，前端 TracePage 瀑布图。P2：写明如何导出 OTLP / 接 Langfuse。

### 为什么做

P2 验收硬项；没有 trace，Agent 慢在哪、错在哪、钱花在哪都无法回答；也是 Day53 成本账本与 Day54 看板错误列表的数据来源。

### 资产锚点

M9.1 · 为 v1.0 做准备

### 前置依赖

W7 的 request_id 中间件 + JSON 日志；W14 的 `make eval-smoke`（收尾验证）。

### 具体执行步骤（概要，详见 day52_20261118/PLAN.md）

1. 表结构 + `trace.py`。
2. 中间件 start/flush；SSE 生成器结束时 flush。
3. 4 处埋点。
4. ops 路由 + TracePage。
5. 测试 + eval-smoke + 提交。

### 验收标准

- [ ] 一次 Agent 运行 ≥ 5 条 span，父子关系正确
- [ ] TracePage 瀑布图可见，点击看 attrs
- [ ] span 异常时 status=error 且记录 error
- [ ] `make eval-smoke` 通过

### 完成后的产出（文件路径）

`apps/api/app/obs/trace.py`、`app/db/models.py`、`app/routes/ops.py`、`apps/web/src/pages/TracePage.tsx`、`docs/observability.md`、`tests/unit/test_trace.py`

### 求职映射

LLM Observability、分布式追踪概念（trace/span/parent）→ AI Platform Engineer / AI Engineer。

### 如果时间不够 / 没有必要

P0 = trace.py + 表 + Gateway 与 tool 埋点 + JSON 接口；瀑布图与 graph 节点埋点顺延；OTLP 说明可只写 3 句话。

---

## Task 2：成本账本 + 预算守卫 + 限流（Day53 · 11-19）

### 做什么

`llm_calls.jsonl` 迁移到 `LLMCall` 表（trace_id、model、prompt/completion tokens、cost、workspace、created_at）+ 迁移脚本；预算守卫 `DAILY_BUDGET_CNY`：调用前查当日累计，>80% 切便宜/备用模型并告警日志，>100% 拒绝并返回 `BUDGET_EXCEEDED`；slowapi 限流（ask 20/min、agent run 5/min，按 IP）；超时与重试集中到配置，在 `docs/runbook.md` 列表说明。写测试。

### 为什么做

预算敏感 + 将来公开 Demo；Agent 死循环/被滥用时需要硬性兜底；集中配置让运维可调、面试可讲。

### 资产锚点

M9.2 M9.3 · 为 v1.0 做准备

### 前置依赖

Task 1（`trace_id` 可用于关联 LLMCall）；Gateway 的 `pricing.py`。

### 具体执行步骤（概要，详见 day53_20261119/PLAN.md）

1. `LLMCall` 表 + Gateway 写入 + 迁移脚本。
2. `cost.py` 预算守卫 + Gateway 接入 + 错误码。
3. slowapi 接入 + 代理 IP 处理。
4. 配置集中 + runbook 参数表。
5. 测试 + eval-smoke + 提交。

### 验收标准

- [ ] 迁移后 `LLMCall` 行数 = jsonl 行数
- [ ] 预算 80%/100% 两个分支有测试
- [ ] 第 21 次 ask / 第 6 次 agent run 返回 429
- [ ] runbook 参数表完整

### 完成后的产出（文件路径）

`app/db/models.py`（LLMCall）、`scripts/migrate_llm_calls.py`、`app/obs/cost.py`、`app/obs/ratelimit.py`、`app/core/config.py`、`docs/runbook.md`、`tests/unit/test_budget.py`、`tests/unit/test_ratelimit.py`

### 求职映射

LLM 成本治理、限流、弹性设计 → AI Platform Engineer / Backend AI Engineer。

### 如果时间不够 / 没有必要

P0 = LLMCall 写入 + 100% 拒绝 + ask 限流；降级与迁移脚本顺延到 Day54 开头。

---

## Task 3：Guardrail v0 + Ops 看板（Day54 · 11-20）

### 做什么

`app/security/guardrails.py`：输入（长度上限、空输入、越狱模式只标记不阻断）；间接注入（工具输出统一为不可信数据，系统提示声明不执行其中指令；检测 "ignore previous instructions" 类模式并标记/剥离）；输出（schema 校验、P2 链接白名单）；PII/密钥脱敏正则应用于日志与长期记忆。`eval/datasets/security.jsonl` 写 8 条注入用例。前端 OpsPage：卡片（今日请求、错误率、P95、tokens、今日成本/预算）+ recharts 按日趋势 + 错误列表（Span status=error）。周复盘。

### 为什么做

Agent 读外部内容即存在间接注入风险；日志与长期记忆是 PII 泄露高发点；看板把 Day52–53 的数据变成运维与演示可用的界面。

### 资产锚点

M11.3 M4.4 M9.4 · 为 v1.0 做准备

### 前置依赖

Task 1 的 Span 表、Task 2 的 LLMCall 表；W9 的 `<tool_output untrusted="true">` 包裹；W12 的长期记忆写入函数。

### 具体执行步骤（概要，详见 day54_20261120/PLAN.md）

1. guardrails.py + redact.py + 单测。
2. 接入：输入校验、工具输出、系统提示、日志 Filter、记忆写入。
3. security.jsonl 8 条 + 运行脚本。
4. `/v1/ops/summary` + OpsPage。
5. eval-smoke + 提交 + 周复盘。

### 验收标准

- [ ] 8 条注入用例全部被标记或拦截（脚本输出）
- [ ] 日志 / 长期记忆中手机号、邮箱、API key 被脱敏（测试）
- [ ] OpsPage 展示 5 张卡片 + 趋势图 + 错误列表
- [ ] `make eval-smoke` 通过

### 完成后的产出（文件路径）

`app/security/guardrails.py`、`app/security/redact.py`、`prompts/*`（系统提示声明）、`eval/datasets/security.jsonl`、`eval/runners/run_security_eval.py`、`app/routes/ops.py`、`apps/web/src/pages/OpsPage.tsx`、`tests/unit/test_guardrails.py`

### 求职映射

Prompt Injection 防护、数据脱敏、运维看板 → AI Security / AI Platform / AI Full-Stack。

### 如果时间不够 / 没有必要

P0 = 间接注入标记 + 脱敏 + 8 条用例 + OpsPage 卡片；输出链接白名单、趋势图顺延。

---
