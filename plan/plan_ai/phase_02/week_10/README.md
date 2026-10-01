# Week 10 · 手写 Agent + Research Agent v0（Phase 2 · Day37–Day39 · 11-03 → 11-05）

## 1. 本周核心目标

不用任何 Agent 框架，手写一个 plan → act → observe → decide 循环（`loop_v0.py`），在其上做出 **Research Agent v0**：输入调研主题，多源（KB / Web / Gitea）检索，输出带 [S1] 来源映射的结构化报告；通过 `POST /v1/agent/run` 以 SSE 推送步骤事件，前端用竖向时间线展示每一步。打 tag `v0.7.0`，同时完成三版简历骨架。

## 2. 资产锚点

| 构建模块               | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                                                 |
| ---------------------- | ---------- | ------------------------------------------------------------------------------------------------------------- |
| M7.1 手写循环 v0       | v0.7       | CLI 跑任务，打印 plan / tool_call / observation / decision 完整 trace                                         |
| M7.5 Research Agent    | v0.7       | 输出 `ResearchReport`（结论 / 发现 / 冲突 / 待确认问题 / 来源表），每条发现可追溯到 KB chunk / URL / 仓库路径 |
| M4.3 Agent 运行视图    | v0.7       | Web「Agent」页：输入任务 → 时间线逐步出现 → 最终报告 + 来源列表 + tokens/成本                                 |
| M3.3（前置）Agent 冒烟 | v0.7       | 10 个任务冒烟报告 `eval/reports/20261105-agent-v0-smoke.md`                                                   |
| M13.3 简历             | —          | `career/resume/` 三版骨架（frontend / ai-fullstack / ai-engineer）                                            |

## 3. 为什么这一周存在

- **先手写再上框架**：W11 用 LangGraph 前，自己实现一遍状态、规划、决策、停止条件，面试时才能讲清「框架替你做了什么、代价是什么」，也才有 v0 vs v1 的对比数据（Day42）。
- Research Agent（SP-F）是最通用、最容易演示的 Agent 场景，也是 P2 作品集的主角；SP-B 等场景之后复用同一套运行时。
- 时间线 UI 是前端优势的集中展示：AI 工程师里能把 Agent 过程可视化的人不多。

## 4. 本周在路线中的位置

```text
上周产出（W9）：Tool Registry + 5 个只读工具 + tool_loop + 工具选择基线（v0.6）
        ↓
本周（W10）：loop_v0（Plan / Decision 结构化输出 + 停止条件）→ ResearchReport + 来源映射 → SSE 事件 + AgentRun/AgentStep 表 → AgentPage 时间线 → v0.7.0
        ↓
下周输入（W11）：可复用的节点函数（planner / executor / decider / synthesizer）、事件 schema、agent_smoke.jsonl 10 任务、v0 基线数据 → LangGraph 迁移与对比
```

## 5. 每日安排

| Day   | 日期  | Task                                       | 当日 P0 产出                                                                              | 模块       | 状态 |
| ----- | ----- | ------------------------------------------ | ----------------------------------------------------------------------------------------- | ---------- | ---- |
| Day37 | 11-03 | Task 1：手写 plan→act→observe 循环 v0      | `app/agent/loop_v0.py` + `prompts/planner.v1.md` `decider.v1.md` + CLI 3 个任务 trace     | M7.1       | TODO |
| Day38 | 11-04 | Task 2：Research Agent 报告 + SSE 步骤事件 | `ResearchReport` + `POST /v1/agent/run`（SSE）+ `AgentRun`/`AgentStep` 表 + `docs/api.md` | M7.5       | TODO |
| Day39 | 11-05 | Task 3：Agent 时间线 UI + 简历 v0（v0.7）  | `pages/AgentPage.tsx` + 10 任务冒烟报告 + 三版简历骨架 + tag `v0.7.0`                     | M4.3 M13.3 | TODO |

## 6. 本周必须留下的资产

```text
~/lab/workpilot/
├── apps/api/app/agent/
│   ├── schemas.py              # Plan / PlanStep / Decision / Observation / AgentEvent / ResearchReport
│   ├── steps.py                # plan_step / act_step / decide_step / synthesize（v0、v1 共用的纯函数）
│   ├── loop_v0.py              # run_events() 异步生成器
│   └── report.py               # 来源登记 + Markdown 渲染
├── apps/api/app/routes/agent.py        # POST /v1/agent/run（SSE）、GET /v1/agent/runs/{id}
├── apps/api/app/db/models.py           # + AgentRun / AgentStep
├── apps/api/tests/agent/
├── prompts/planner.v1.md  prompts/decider.v1.md  prompts/synthesizer.v1.md
├── scripts/agent_v0.py
├── docs/api.md                          # Agent SSE 事件 schema
├── apps/web/src/lib/sse.ts              # 从 useStreamingAnswer 抽出的 SSE 解析
├── apps/web/src/hooks/useAgentRun.ts
├── apps/web/src/components/agent/{AgentTimeline,TimelineItem,ReportView}.tsx
├── apps/web/src/pages/AgentPage.tsx
├── eval/datasets/agent_smoke.jsonl      # 10 任务（W11 对比复用）
└── eval/reports/20261105-agent-v0-smoke.md
~/lab/projects/career/resume/{resume-frontend,resume-ai-fullstack,resume-ai-engineer}.md
```

## 7. 本周验收标准

- [ ] PASS / FAIL：`loop_v0` 有 4 个停止条件：finish 决策 / max_steps=8 / token 预算 / 重复调用检测，各有单测
- [ ] PASS / FAIL：Planner 与 Decider 使用 M1.3 结构化输出（Pydantic），校验失败有重试
- [ ] PASS / FAIL：报告中每条 finding 的来源 id 都存在于来源表；不存在的 id 被代码剔除（单测）
- [ ] PASS / FAIL：`curl -N -X POST /v1/agent/run` 能看到 plan → … → report → done 事件流；`docs/api.md` 有完整 schema
- [ ] PASS / FAIL：AgentRun / AgentStep 落 SQLite，可按 run_id 回放
- [ ] PASS / FAIL：AgentPage 时间线逐步渲染、工具参数 / 结果可折叠、显示耗时与 token 成本、报告来源可点击
- [ ] PASS / FAIL：10 任务冒烟报告存在（成功数、平均步数、平均 tokens、失败原因）
- [ ] PASS / FAIL：三版简历骨架已提交；tag `v0.7.0` 已推送

## 8. 求职映射

- 本周能力：Agent 规划与执行循环（Plan-and-Execute / ReAct 混合）、停止条件设计、引用可追溯、SSE 事件流、Agent UX。
- 简历 bullet 草稿：
  - 从零实现 Plan→Act→Observe→Decide Agent 循环（结构化规划、重规划、步数 / token 预算、重复调用检测），作为 Research Agent 输出带来源映射的调研报告；10 任务冒烟成功 **/10，平均 ** 步、\_\_ tokens。
  - 设计 Agent 事件协议（8 类 SSE 事件）并实现 React 时间线视图，实时展示规划、工具调用、观察与决策，单次运行成本可视化。
- 面试题：
  1. ReAct 和 Plan-and-Execute 有什么区别？你为什么混合使用？
  2. Agent 怎么停下来？有哪些停止条件，各防什么问题？
  3. 报告里的引用怎么保证不是模型编造的？

## 9. 本周禁止事项

- 不引入 LangGraph / LangChain（W11 才迁移），不引入任何其他 Agent 框架。
- 不做 Multi-Agent（如「研究员 + 审稿人」双 Agent）。
- 不做写操作工具、不做审批（W12）。
- 不做记忆（W12）、不做 checkpoint（W11）。
- 前端不做复杂动画、不引入新的 UI 组件库；沿用 Tailwind。

## 10. 时间不够时（最小保留）

- Day37：`loop_v0` + planner/decider + max_steps 停止；token 预算与重复检测可推迟到 Day38 第一段。
- Day38：`ResearchReport` + SSE 接口；AgentStep 表可先只存 AgentRun（报告 + 状态）。
- Day39：AgentPage 只做时间线 + 报告（不折叠、不显示成本）；冒烟 5 个任务；简历只建 ai-engineer 一版。

## 11. 周复盘（Day39 结束时填写）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（AgentPage 录屏 30–60 秒）
- 冒烟：成功 **/10，平均步数 **，平均 tokens **，主要失败类型 \_\_**
- 手写 Agent 最难的部分（W11 对比时要验证 LangGraph 是否解决它）：\_\_\_\_
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
