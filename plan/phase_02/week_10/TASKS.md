# Week 10 · TASKS

## Task 1：手写 plan→act→observe 循环 v0（Day37 · 11-03）

### 做什么

实现 `app/agent/loop_v0.py`：`AgentState(task, plan, observations, step_count, final)`；planner 结构化输出 `Plan{steps:[{id, goal, suggested_tool}]}`；executor 让 LLM 为当前步选工具与参数；observe 记录结果；decider 结构化输出 `Decision{action: continue|replan|finish, reason}`；停止条件 max_steps=8、token 预算、重复调用检测。提示词 `prompts/planner.v1.md`、`prompts/decider.v1.md`。CLI 跑 3 个任务打印 trace。

### 为什么做

先手写理解 Agent 的本质（一个带状态的 while 循环 + 两次结构化 LLM 调用 + 工具执行），面试能讲清；同时产出 v0 基线，W11 才能证明 LangGraph 带来了什么。

### 资产锚点

M7.1 手写循环 v0 → 为 v0.7 做准备

### 前置依赖

W9 的 registry / 5 个工具 / `chat_with_tools()`；M1.3 `gateway.structured()`；M1.6 prompt 加载器。

### 具体执行步骤（概要，详见 day37_20261103/PLAN.md）

1. `schemas.py`：Plan / PlanStep / Decision / Observation / AgentEvent。
2. 两个提示词文件。
3. `steps.py`：plan_step / act_step / decide_step（纯函数，W11 复用）。
4. `loop_v0.py`：`run_events()` 异步生成器 + 4 个停止条件。
5. `scripts/agent_v0.py` 跑 3 个任务；单测停止条件；提交。

### 验收标准

- [ ] 3 个任务均有完整 trace（plan → step × N → decision → final）
- [ ] 停止条件单测：finish / max_steps / token 预算 / 重复调用
- [ ] Planner / Decider 输出均通过 Pydantic 校验

### 完成后的产出（文件路径）

`apps/api/app/agent/{schemas,steps,loop_v0}.py`、`prompts/planner.v1.md`、`prompts/decider.v1.md`、`scripts/agent_v0.py`、`apps/api/tests/agent/test_loop_v0.py`

### 求职映射

Agent 架构原理（Plan-and-Execute + ReAct）、结构化输出、停止条件设计 → AI Agent Engineer。

### 如果时间不够 / 没有必要

token 预算与重复检测推迟到 Day38 开头；CLI 只跑 1 个任务。

---

## Task 2：Research Agent 报告 + SSE 步骤事件（Day38 · 11-04）

### 做什么

1. `synthesize`：LLM 产出报告草稿（title / summary / findings[{claim, sources}] / conflicts / open_questions），来源表 `[S1]…` 由代码从 observations 的 `SourceRef` 生成（映射到 KB chunk id / URL / Gitea 路径），无效来源 id 由代码剔除；冲突检测提示词；渲染 Markdown。
2. `POST /v1/agent/run`：SSE 事件 `plan / step_start / tool_call / tool_result / decision / report / done / error`；事件 schema 写入 `docs/api.md`。
3. `AgentRun`、`AgentStep` 表落 SQLite。

### 为什么做

Research Agent 是 P2 的主演示；可追溯来源是「可信 AI」的最低要求；SSE 事件协议是前端时间线与后续 trace（W15）的共同基础。

### 资产锚点

M7.5 Research Agent → 为 v0.7 做准备

### 前置依赖

Task 1 的 `run_events()`；W9 工具返回的 `sources`；phase_01 的 SSE 实现（`/v1/kb/ask/stream`）和 SQLModel 会话。

### 具体执行步骤（概要，详见 day38_20261104/PLAN.md）

1. `ResearchReportDraft` / `ResearchReport` 模型 + `report.py`（来源登记、校验、渲染）。
2. `prompts/synthesizer.v1.md`（含冲突检测规则）。
3. `AgentRun` / `AgentStep` 模型。
4. `routes/agent.py`：SSE 路由 + 落库；`docs/api.md`。
5. curl 验证 + 单测 + 提交。

### 验收标准

- [ ] 报告 Markdown 中每条发现带 [Sx]，来源表每项有可点击 ref
- [ ] 伪造来源 id 被剔除（单测）
- [ ] `curl -N` 看到完整事件流，最后是 `done`；异常时是 `error`
- [ ] SQLite 中能查到 run 与有序 steps

### 完成后的产出（文件路径）

`apps/api/app/agent/report.py`、`prompts/synthesizer.v1.md`、`apps/api/app/routes/agent.py`、`apps/api/app/db/models.py`（改）、`docs/api.md`、`apps/api/tests/agent/test_report.py`

### 求职映射

引用可追溯 / 防幻觉、流式事件协议设计、Agent 运行记录 → AI Engineer / AI Full-Stack。

### 如果时间不够 / 没有必要

冲突检测只保留提示词规则不做单测；AgentStep 表推迟到 Day39 开头。

---

## Task 3：Agent 时间线 UI + 简历 v0（v0.7）（Day39 · 11-05）

### 做什么

1. `apps/web/src/pages/AgentPage.tsx`：任务输入、竖向时间线（按事件类型图标、折叠显示工具参数 / 结果、耗时、token 成本）、最终报告与来源列表；从 `useStreamingAnswer` 抽出 SSE 解析复用。
2. 10 个任务冒烟（`eval/datasets/agent_smoke.jsonl`），结果写 `eval/reports/20261105-agent-v0-smoke.md`。
3. `career/resume/` 建三版简历骨架（frontend / ai-fullstack / ai-engineer），填 P1 + P2（进行中）条目。
4. tag `v0.7.0`，周复盘。

### 为什么做

时间线 UI 让 Agent「可观察、可解释」，是作品集最直观的画面；冒烟数据是 W11 对比的基线；简历 v0 让求职线从 W10 开始有可迭代的文件。

### 资产锚点

M4.3 Agent 运行视图、M13.3 简历 → **v0.7**

### 前置依赖

Task 2 的 SSE 接口与事件 schema；phase_01 的 `useStreamingAnswer`、react-markdown + rehype-sanitize。

### 具体执行步骤（概要，详见 day39_20261105/PLAN.md）

1. `lib/sse.ts` 抽取 + `useAgentRun.ts`。
2. `AgentTimeline` / `TimelineItem` / `ReportView` 组件 + 路由。
3. `agent_smoke.jsonl` 10 任务 + `run_agent_smoke.py` 冒烟。
4. 三版简历骨架。
5. tag + push + 周复盘。

### 验收标准

- [ ] 页面可完成一次端到端运行，时间线逐条出现
- [ ] 工具结果以纯文本渲染（不可信内容不走 HTML）
- [ ] 冒烟报告含成功数 / 平均步数 / 平均 tokens / 失败原因
- [ ] 三份简历文件存在且各有 ≥3 条 bullet
- [ ] `v0.7.0` 已推送

### 完成后的产出（文件路径）

`apps/web/src/lib/sse.ts`、`apps/web/src/hooks/useAgentRun.ts`、`apps/web/src/components/agent/*`、`apps/web/src/pages/AgentPage.tsx`、`eval/datasets/agent_smoke.jsonl`、`eval/runners/run_agent_smoke.py`、`eval/reports/20261105-agent-v0-smoke.md`、`~/lab/projects/career/resume/*.md`

### 求职映射

AI UX（流式 + 过程可视化）、React + TS 工程化、简历定位分化 → AI Full-Stack / Frontend（AI 方向）。

### 如果时间不够 / 没有必要

不做折叠与成本显示；冒烟 5 个任务；简历只做 ai-engineer 一版，其余两版 W16 补。

---
