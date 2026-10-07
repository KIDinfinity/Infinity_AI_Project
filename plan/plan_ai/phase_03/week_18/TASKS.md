# Week 18 · TASKS

## Task 1：主场景包工作流实现（Day60 · 01-25）

### 做什么

实现 `apps/api/app/scenarios/sp_b_req_breakdown/`：schemas（ParsedRequirement / Task / TaskBreakdown / SelfCheck）、prompts（parse / breakdown / self_check）、graph（7 节点 + 条件边 + interrupt + 幂等写），以及 `POST /v1/scenarios/{sp}/runs` 与 resume 端点；3 个样例跑通。

### 为什么做

这是 DA-01 价值层第一次端到端落地，P3 的核心代码；后续评测、安全、Pro Kit 都围绕它。

### 资产锚点

- 模块：M10 场景包（依赖 M1.3 structured、M2 检索、M6.2 gitea 工具、M7.2 LangGraph、M7.4 HITL）
- 版本：v1.1（后端部分）

### 前置依赖

- Day59 场景图与 State 设计
- W12 HITL 审批端点、SqliteSaver checkpointer
- W9 `kb_search`、`gitea_issue_read`、`gitea_issue_create` 工具
- `data/scenarios/` ≥ 3 个样例；规范 KB 已导入（团队规范示例文档）

### 具体执行步骤（概要，详见 day60_20261126/PLAN.md）

1. 写 schemas.py（Pydantic）。
2. 写 3 个 prompt（版本化 `.v1.md`）。
3. 写 graph.py：节点函数 + 条件边 + interrupt + 幂等键。
4. 写 routes/scenarios.py：启动 run、resume、查询。
5. 单测：回边上限、幂等；3 样例冒烟。
6. 写 SP-C/D/E 替换对照表到 `app/scenarios/README.md`。

### 验收标准

- [ ] 3 个样例跑到 interrupt，返回 TaskBreakdown（每任务含估时 + 验收标准）
- [ ] resume(approve) 后创建 Issue；重复 resume 不重复创建
- [ ] self_check 回边最多 1 次（单测）
- [ ] 每次运行有 Trace（复用 W15 obs）

### 完成后的产出

- `apps/api/app/scenarios/sp_b_req_breakdown/*`
- `apps/api/app/routes/scenarios.py`
- `apps/api/tests/scenarios/test_sp_b_graph.py`
- `apps/api/app/scenarios/README.md`（替换对照表）

### 求职映射

LangGraph 场景工作流 + HITL + 幂等，是 AI Agent Engineer 面试的高频追问点。

### 如果时间不够 / 没有必要

- create_issues 先用 dry-run（只写 AgentStep，不调 Gitea），Day61 再接真实写入。
- self_check 先用规则（任务数、验收标准非空、标题去重），LLM 自检进 P1。

---

## Task 2：场景页面 + 5 个真实样例（v1.1）（Day61 · 01-26）

### 做什么

实现 ScenarioPage：输入表单（粘贴 / 上传 .md）、复用 Agent 时间线、审批前可编辑任务表（改估时 / 删任务 / 改验收标准）、批准后显示 Issue 链接；用 5 个脱敏样例端到端跑，记录手工 vs WorkPilot 耗时到 `docs/portfolio/p3-notes.md`；发布 `v1.1.0`。

### 为什么做

可编辑审批是 P3 的 AI UX 亮点，也是前端优势展示；5 个样例耗时对比是 P3「价值」的第一份证据。

### 资产锚点

- 模块：M10、M4.3（时间线复用）、M4 新页面
- 版本：**v1.1**

### 前置依赖

- Day60 后端端点
- W10/W12 的时间线组件与审批组件

### 具体执行步骤（概要，详见 day61_20261127/PLAN.md）

1. API client + 路由 `/scenarios/sp_b`。
2. 表单 → 启动 run → SSE / 轮询时间线。
3. TaskTableEditor：编辑 / 删除 / 合计估时。
4. 批准 → resume → 显示 Issue 链接。
5. 5 样例端到端 + 计时 → p3-notes.md。
6. tag v1.1.0。

### 验收标准

- [ ] 页面完成「输入 → 时间线 → 编辑 → 批准 → 链接」闭环
- [ ] 5 个样例完成，p3-notes.md 有耗时表
- [ ] `v1.1.0` tag 已推送，CI 绿

### 完成后的产出

- `apps/web/src/pages/ScenarioPage.tsx`、`apps/web/src/components/TaskTableEditor.tsx`
- `docs/portfolio/p3-notes.md`
- tag `v1.1.0`

### 求职映射

前端 AI UX：「人机协作式审批」——前端岗与 AI Full-Stack 岗的差异化卖点。

### 如果时间不够 / 没有必要

- 编辑只做「删任务 + 改估时」；上传文件只做粘贴。
- 样例 3 个也可发 v1.1.0，另 2 个 Day62 前补。

---
