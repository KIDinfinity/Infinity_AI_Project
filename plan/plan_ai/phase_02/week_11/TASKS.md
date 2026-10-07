# Week 11 · TASKS

## Task 1：LangGraph 迁移（Day40 · 12-07）

### 做什么

`uv add langgraph langgraph-checkpoint-sqlite`；`app/agent/state.py` 定义 `ResearchState(TypedDict){task, plan, current_step, observations: Annotated[list, operator.add], decision, report, step_count, errors}`（另加 `pending_call`、`tokens_used`）；`app/agent/graph.py` 节点 plan → act → tools → decide，条件边 continue→act / replan→plan / finish→synthesize → END，`compile()`；`graph.get_graph().draw_mermaid()` 输出到 `docs/agent-graph.md`；与 v0 在 3 个任务上做行为对齐测试；事件适配器让 v1 产出与 v0 相同的 SSE 事件。

### 为什么做

LangGraph 把 v0 中隐含在 while 循环里的状态与流程显式化，是 W11 checkpoint 和 W12 interrupt 的前提。

### 资产锚点

M7.2 LangGraph 工作流 → 为 v0.8 做准备

### 前置依赖

W10 的 `steps.py` 纯函数、`schemas.py`、`report.py`、SSE 事件协议。

### 具体执行步骤（概要，详见 day40_20261106/PLAN.md）

1. 安装依赖，读 StateGraph / reducer / 条件边文档（20 分钟）。
2. `state.py` + `nodes.py`（每个节点包装 steps.py）。
3. `graph.py` + Mermaid 图。
4. `events.py` 适配器 + `scripts/agent_v1.py`。
5. 对齐测试（假 Gateway）；提交。

### 验收标准

- [ ] `build_graph().get_graph().draw_mermaid()` 输出含 5 个节点与 3 条条件边
- [ ] `scripts/agent_v1.py` 跑通 1 个真实任务，事件序列与 v0 同构
- [ ] 对齐测试：3 个任务在假 LLM 下 v0/v1 工具序列一致

### 完成后的产出（文件路径）

`apps/api/app/agent/{state,nodes,graph,events}.py`、`scripts/agent_v1.py`、`docs/agent-graph.md`、`apps/api/tests/agent/test_parity.py`

### 求职映射

LangGraph StateGraph、reducer、条件路由 → AI Agent Engineer（JD 高频关键词）。

### 如果时间不够 / 没有必要

对齐测试只做 1 个任务；事件适配器推迟到 Day41 开头。

---

## Task 2：重试 / 降级 / checkpoint（Day41 · 12-08）

### 做什么

1. `add_node(..., retry_policy=RetryPolicy(...))` 处理瞬时错误；工具报错转为 observation 让 planner/decider 恢复。
2. Gateway 增加 provider fallback（主 `deepseek-chat` → 备 Qwen DashScope 兼容模式或本地 Ollama），配置化。
3. `langgraph-checkpoint-sqlite` checkpointer，`thread_id = run_id`，演示中断后恢复。
4. 故障注入测试：工具超时、LLM 500（mock），验证优雅完成或明确失败。

### 为什么做

真实环境中 LLM API 限流 / 5xx、工具超时是常态；没有降级与恢复，Agent 无法交付给别人用。

### 资产锚点

M7.2（retry / checkpoint）、M1.2（provider fallback）→ 为 v0.8 做准备

### 前置依赖

Task 1 的 graph；phase_01 Gateway 的重试 / 超时实现；备用 provider 的 key（DashScope）或本机 Ollama。

### 具体执行步骤（概要，详见 day41_20261107/PLAN.md）

1. 梳理「重试分层表」，确定每层职责。
2. Gateway fallback + respx 单测。
3. 节点 RetryPolicy + 工具错误观察化 + decider 提示词补充。
4. AsyncSqliteSaver + `--resume` 演示。
5. 故障注入测试 3 个；提交。

### 验收标准

- [ ] 主 500 → 备成功；全失败 → `LLMUnavailable` → run failed + error 事件
- [ ] 工具超时运行仍完成，报告 open_questions 体现缺失信息
- [ ] Ctrl+C 后 `--resume` 继续执行直至 done
- [ ] RetryPolicy 单测通过

### 完成后的产出（文件路径）

`apps/api/app/llm/gateway.py`（改）、`apps/api/app/core/config.py`（改）、`apps/api/app/agent/graph.py`（改）、`apps/api/app/agent/runner.py`、`apps/api/tests/agent/{test_faults,test_checkpoint}.py`、`apps/api/tests/llm/test_fallback.py`

### 求职映射

LLM 应用可靠性工程、多供应商容灾、持久化执行 → AI Engineer / AI Platform Engineer。

### 如果时间不够 / 没有必要

Ollama 实测跳过（只做 mock 单测）；RetryPolicy 单测推迟到 Day42 开头。

---

## Task 3：v0 vs v1 对比 + ADR + JD 追踪（Day42 · 12-09）

### 做什么

1. `eval/runners/compare_agents.py`：`agent_smoke.jsonl` 10 任务 × 两版，对比成功率、步数、延迟、tokens、成本、失败类型，报告写 `eval/reports/20261209-agent-v0-vs-v1.md`。
2. `docs/adr/0006-why-langgraph.md`：显式状态、checkpoint、interrupt、可视化 vs 手写的代价。
3. `/v1/agent/run` 默认切到 v1，`AGENT_VERSION=v0` 可回退。
4. JD 追踪第 2 轮 + 能力矩阵更新；周复盘。

### 为什么做

用数据而不是感觉做技术决策，是作品集与面试中最有说服力的部分；ADR 让决策可追溯。

### 资产锚点

M7（v0/v1 收口）、M13.1 → 为 v0.8 做准备

### 前置依赖

Task 1–2 完成；phase_01 的 `eval/judge.py`（LLM-as-a-judge）。

### 具体执行步骤（概要，详见 day42_20261108/PLAN.md）

1. 写 compare 脚本并运行（后台跑，同时写 ADR）。
2. 人工抽查 + judge 打分，填对比表。
3. ADR-0006。
4. 配置开关 + 路由切换 + 冒烟。
5. JD 第 2 轮；周复盘；提交。

### 验收标准

- [ ] 对比报告含 6 个维度与结论
- [ ] ADR-0006 含背景 / 决策 / 备选 / 后果 / 回退方案
- [ ] 前端 Agent 页在 v1 下正常，切 v0 也正常
- [ ] `job-market.md` 第 2 轮 + `capability-matrix.md` 更新日期与分数

### 完成后的产出（文件路径）

`eval/runners/compare_agents.py`、`eval/reports/20261209-agent-v0-vs-v1.md`、`docs/adr/0006-why-langgraph.md`、`apps/api/app/routes/agent.py`（改）、`~/lab/projects/career/{job-market,capability-matrix}.md`

### 求职映射

技术选型方法论、评测驱动决策、ADR → 所有中高级岗位通用。

### 如果时间不够 / 没有必要

对比只跑 5 个任务；JD 压缩为 5 个；能力矩阵只更新 Agent 相关行。

---
