# Week 12 · TASKS

## Task 1：会话记忆 + 上下文压缩（Day43 · 11-09）

### 做什么

`thread_id` 绑定 conversation（`AgentRun.conversation_id`）；checkpointer 持久化会话状态；`ResearchState` 增加 `messages`（`add_messages`）与 `summary`，每轮把用户任务与最终报告写入 messages；planner / synthesizer 读取 summary + 最近 k 条消息，支持追问「把上一份报告第二点展开」。上下文预算：tiktoken 近似计数，超阈值时 summarize 节点把旧消息压缩进 `summary`，保留最近 k 条原文。每轮开始重置单次运行字段（observations 等）。测试。

### 为什么做

研发协作天然是多轮的；没有会话记忆，每次追问都要重新描述上下文。压缩保证长会话成本与延迟可控。

### 资产锚点

M7.3 Memory（会话 / checkpointer）→ 为 v0.8 做准备

### 前置依赖

W11 的 AsyncSqliteSaver、`build_graph()`；Day38 `AgentRun.conversation_id` 字段；phase_01 `Conversation` 表。

### 具体执行步骤（概要，详见 day43_20261109/PLAN.md）

1. state 改造：`messages`、`summary`、可重置 reducer。
2. `new_turn_input()`：每轮输入。
3. `context.py` + `summarize` 节点 + `prompts/summarizer.v1.md`。
4. planner / synthesizer 注入历史。
5. API 接收 `conversation_id`，并发保护；测试 + 演示；提交。

### 验收标准

- [ ] 同一会话第二轮 planner 输入包含上一份报告（测试）
- [ ] 超阈值后 messages 只剩 k 条且 summary 非空（测试）
- [ ] 第二轮 observations 不包含第一轮的观察（测试）
- [ ] 同一会话已有运行中任务时返回 409

### 完成后的产出（文件路径）

`apps/api/app/agent/{state,context,nodes,graph}.py`（改 / 新）、`prompts/summarizer.v1.md`、`apps/api/app/routes/agent.py`（改）、`apps/api/tests/agent/test_conversation.py`

### 求职映射

Agent 短期记忆、上下文窗口管理、LangGraph reducer 深入 → AI Agent Engineer。

### 如果时间不够 / 没有必要

压缩只做测试；409 并发保护推迟到 Day44 开头。

---

## Task 2：长期记忆（Day44 · 11-10）

### 做什么

Qdrant collection `memories_{workspace}`，payload `{text, type: preference|fact|project_context, source_run, created_at, importance}`。写入：运行结束后 LLM 结构化抽取候选记忆（只看用户消息），`importance ≥ 阈值` 且不重复（相似度 > 0.9 则更新）才写入；读取：plan 前检索 top3 记忆 + 常驻偏好注入 planner / synthesizer；写入前脱敏（密钥 / 手机号 / 邮箱）。API：`GET /v1/memories`、`DELETE /v1/memories/{id}`。Demo：说「报告用中文且先给结论」→ 新会话遵守。

### 为什么做

偏好与项目上下文跨会话复用，减少重复交代；可查可删是用户对 AI 记忆的基本控制权。

### 资产锚点

M7.3 Memory（长期 / Qdrant `memories`）→ 为 v0.8 做准备

### 前置依赖

Task 1 的 state / graph；phase_01 的 Qdrant 客户端与 bge-m3 embedding（`app/rag/embedding.py`、`store.py`）。

### 具体执行步骤（概要，详见 day44_20261110/PLAN.md）

1. `security/redact.py` + 单测。
2. `memory.py`：`MemoryStore`（ensure / upsert 去重 / search / preferences / list / delete）。
3. `prompts/memory_extractor.v1.md` + `remember` 节点；plan 前注入。
4. `routes/memories.py`。
5. 测试（Qdrant `:memory:`）+ 偏好演示；提交。

### 验收标准

- [ ] 脱敏单测通过
- [ ] 同一偏好说两次，collection 中只有 1 条（更新）
- [ ] 偏好演示成功（两次运行截图）
- [ ] `GET` 能列出、`DELETE` 后不再注入

### 完成后的产出（文件路径）

`apps/api/app/security/redact.py`、`apps/api/app/agent/memory.py`、`prompts/memory_extractor.v1.md`、`apps/api/app/routes/memories.py`、`apps/api/tests/agent/test_memory.py`

### 求职映射

长期记忆设计（写入策略 / 去重 / 遗忘 / 隐私）、向量库二次应用 → AI Agent Engineer / AI Engineer。

### 如果时间不够 / 没有必要

DELETE 接口推迟；抽取只支持 preference 一类。

---

## Task 3：HITL 审批 + SP-B 试点 + 简历更新（v0.8）（Day45 · 11-11）

### 做什么

1. 写工具 `gitea_issue_create`（permission=write，只作用于沙盒仓库 `sandbox-issues`，独立写 token）。
2. 图在执行 write 工具前进入 `approve` 节点调用 `interrupt()` → run 状态 `waiting_approval` + `pending_action`；`POST /v1/agent/runs/{id}/approve {decision: approve|reject|edit, edited_args}` → `Command(resume=...)` 继续。
3. 前端审批卡片：工具名、参数（可编辑）、批准 / 拒绝。
4. 测试：未批准时 Gitea API 绝不被调用（respx 断言）。
5. SP-B 迷你流程：需求文本 → TaskBreakdown（W3 Day11 schema）→ 审批 → 沙盒仓库建 Issue。
6. 简历双周更新；tag `v0.8.0`；周复盘。

### 为什么做

「写操作必须人工审批」是 WorkPilot 的产品承诺与 §11 硬指标；SP-B 是 DA-01 主场景的第一次端到端验证。

### 资产锚点

M7.4 Human-in-the-loop、M10 SP-B、M13.3 → **v0.8**

### 前置依赖

Task 1–2；Gitea 中已建 `sandbox-issues` 仓库与 bot 账号写 token；W3 Day11 的 `TaskBreakdown` schema。

### 具体执行步骤（概要，详见 day45_20261111/PLAN.md）

1. Gitea 准备：bot 账号 + 沙盒仓库协作者 + 写 token。
2. `gitea_issue_create` + `execute(approved=...)` 门禁。
3. `hitl.py` approve 节点 + 路由 + 事件 `approval_required`。
4. approve API + 测试（核心断言）。
5. 审批卡片。
6. SP-B 迷你图 + CLI。
7. 简历 + tag + 周复盘。

### 验收标准

- [ ] respx 断言：中断时 0 次、拒绝后 0 次、批准后 1 次
- [ ] `execute("gitea_issue_create", ..., approved=False)` 返回 `approval_required`
- [ ] 前端批准 / 拒绝 / 修改后批准均可用
- [ ] SP-B 流程在沙盒仓库建 ≥2 个 Issue
- [ ] `v0.8.0` 推送

### 完成后的产出（文件路径）

`apps/api/app/tools/builtin/gitea.py`（改）、`apps/api/app/tools/registry.py`（改）、`apps/api/app/agent/hitl.py`、`apps/api/app/agent/graph.py`（改）、`apps/api/app/routes/agent.py`（改）、`apps/api/tests/agent/test_hitl.py`、`apps/web/src/components/agent/ApprovalCard.tsx`、`apps/api/app/scenarios/sp_b_req_breakdown/graph.py`、`scripts/sp_b_pilot.py`、`docs/api.md`、`~/lab/projects/career/resume/*.md`

### 求职映射

HITL、最小权限与过度代理防护、场景落地（研发效能） → AI Agent Engineer / AI Full-Stack。

### 如果时间不够 / 没有必要

审批卡片与 SP-B 顺延到 Day46 开头 30 分钟；P0 只保留后端审批 + 断言测试 + tag。

---
