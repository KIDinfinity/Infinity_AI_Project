# Week 18 · 主场景包 MVP（Phase 3 · Day60–Day61 · 11-26 → 11-27）

## 1. 本周核心目标

按 Day59 的场景图实现 SP-B「需求 → 任务拆解 → Issue 草案」LangGraph 工作流（含 self_check 回边、interrupt 审批、幂等写入），并做出 ScenarioPage，用 5 个脱敏样例端到端跑通，发布 **v1.1.0**。

## 2. 资产锚点

| 构建模块                                                                 | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                                                |
| ------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------ |
| M10 场景包 SP-B、M4.3 Agent 运行视图（复用）、M6.2 gitea 工具、M7.4 HITL | **v1.1**   | 在 Web 上粘贴一段需求 → 时间线看到解析/检索/拆解/自检 → 在审批前改估时、删任务 → 批准后得到 Gitea Issue 链接 |

## 3. 为什么这一周存在

- P1/P2 证明了「能力」，P3 必须证明「解决了一个具体问题」。这是 DA-01 价值层（M10）第一次端到端落地。
- 所有 W19–W22 的工程化（认证、评测、安全、回归）都要有一个真实的业务流程来承载，否则只是空架子。
- 只有 2 天：Day60 后端图跑通，Day61 前端 + 样例 + 发版。

## 4. 本周在路线中的位置

```text
上周产出（W17）：p3-definition.md、architecture-v2.md（场景图）、data/scenarios/ ≥20 样例
        ↓
本周（W18）：app/scenarios/sp_b_req_breakdown/ + POST /v1/scenarios/{sp}/runs
             ScenarioPage（表单/时间线/可编辑任务表/Issue 链接）+ 5 样例 + p3-notes.md → v1.1.0
        ↓
下周输入（W19）：场景接口需要加认证与 workspace_id；KB 导入改异步；v1.2 自动部署
```

## 5. 每日安排

| Day   | 日期  | Task                            | 当日 P0 产出                                                              | 模块   | 状态 |
| ----- | ----- | ------------------------------- | ------------------------------------------------------------------------- | ------ | ---- |
| Day60 | 11-26 | Task 1：主场景包工作流实现      | `graph.py` 7 节点跑通 + `POST /v1/scenarios/sp_b/runs` + 3 样例到审批节点 | M10    | TODO |
| Day61 | 11-27 | Task 2：场景页面 + 5 个真实样例 | ScenarioPage 可编辑审批 + 5 样例端到端 + `p3-notes.md` + tag `v1.1.0`     | M10 M4 | TODO |

## 6. 本周必须留下的资产

- `apps/api/app/scenarios/sp_b_req_breakdown/{__init__.py, graph.py, schemas.py, prompts/}`
- `apps/api/app/routes/scenarios.py`
- `apps/api/tests/scenarios/test_sp_b_graph.py`
- `apps/web/src/pages/ScenarioPage.tsx`、`apps/web/src/components/TaskTableEditor.tsx`
- `docs/portfolio/p3-notes.md`（5 样例耗时对比）
- git tag `v1.1.0`

## 7. 本周验收标准

- [ ] PASS / FAIL：3 个样例通过 API 跑到 human_review 中断，返回结构化 TaskBreakdown
- [ ] PASS / FAIL：self_check 不通过时最多回到 breakdown 1 次（单测覆盖）
- [ ] PASS / FAIL：同一 run 重复 resume 不会重复创建 Issue（幂等单测）
- [ ] PASS / FAIL：Web 上能编辑估时 / 删除任务后批准，Gitea 中出现对应 Issue
- [ ] PASS / FAIL：5 个样例端到端完成，p3-notes.md 记录手工 vs WorkPilot 耗时
- [ ] PASS / FAIL：`v1.1.0` tag 已推送，CI 绿

## 8. 求职映射

- 本周能力：场景化 Agent 工作流、结构化输出、Human-in-the-loop、幂等写操作、AI UX（可编辑审批）。
- 简历 bullet 草稿：「用 LangGraph 实现『需求→任务拆解→Issue』7 节点工作流（自检回边 + interrupt 人工审批 + 幂等写入），5 个样例平均耗时从 ** 分钟降到 ** 分钟」
- 面试题：
  1. 为什么用固定工作流而不是让 Agent 自由规划？（答要点：业务流程已知 → 工作流更可控、可评测、成本低；自由规划只用在步骤不确定的子任务）
  2. 人工审批时允许编辑草案，后端怎么处理？（答要点：resume 带回编辑后的任务表，按 schema 校验，diff 记为隐式反馈，写入以编辑后版本为准）
  3. 自检节点会不会死循环？（答要点：retries 计数 + 条件边上限 1 次，超过直接进入人工审批并展示问题）

## 9. 本周禁止事项

- 不做第二个场景包（辅场景进 Backlog）。
- 不做认证、多空间、Postgres（W19）。
- 不做批量需求、自动分配人、Jira/飞书集成。
- 不使用公司真实需求跑场景。

## 10. 时间不够时（最小保留）

- Day60：graph 跑到 human_review 中断 + resume 后 create_issues（可先 dry-run 打印），API 端点可用。
- Day61：ScenarioPage 能看草案并批准（编辑功能可只做「删任务」）；样例 3 个；tag v1.1.0。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（预期：SP-B 端到端演示 2 分钟）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
