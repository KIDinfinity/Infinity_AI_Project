# Phase 02 · Agent 与 P2（第 9–16 周 · Day34–Day57 · 11-23 → 01-13）

## 1. 阶段目标

在 WorkPilot v0.5 的同一仓库上，加入工具层、Agent 运行时、记忆与人工审批、MCP 集成、Agent 评测和生产级可观测，推进到 **v1.0 = P2 WorkPilot Agent**；同时启动求职验证（JD 追踪、简历 v0 → v1），并完成开源发布与产品页。

## 2. 资产锚点

| 项                     | 内容                                                                                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 版本推进               | v0.5 → v0.6（Tools）→ v0.7（Research Agent v0）→ v0.8（LangGraph + Memory + HITL）→ v0.9（MCP）→ **v1.0（P2 发布）**                                                             |
| 构建模块               | M6 Tool Layer、M7 Agent Runtime、M8 MCP、M3.3/M3.5 Agent Eval、M9 Observability、M11.3 Guardrail v0、M4.3/M4.4 前端、M12.1/M12.3 开源与产品页、M13 求职                          |
| 完成后最终产品多了什么 | WorkPilot 从「会回答」变成「会做事」：能规划、调用工具（知识库/网页/Gitea）、写操作需审批、能在 IDE 中通过 MCP 使用、每次修改能用评测判断变好变坏、能看到每次请求的 trace 与成本 |

```text
W9 Tools → W10 手写 Agent → W11 LangGraph → W12 Memory/HITL → W13 MCP → W14 Agent Eval → W15 Production → W16 P2 发布
```

## 3. 为什么这个阶段存在

JD 中 Agent / Tool Calling / MCP / Evaluation / Observability 是区分「会调 API」与「AI 工程师」的关键。这些能力也正是 DA-01 「结合工作内容提升效率」的执行层——没有工具和审批，WorkPilot 只是问答机器人。

## 4. 本阶段必须产生什么（文件级）

| 线  | 产出                                              | 位置                                                                |
| --- | ------------------------------------------------- | ------------------------------------------------------------------- |
| B   | Tool Registry + ≥5 个内置工具 + 单测              | `apps/api/app/tools/`                                               |
| B   | 手写循环 v0 + LangGraph v1 + Memory + HITL        | `apps/api/app/agent/`                                               |
| B   | MCP Server（stdio + HTTP）+ MCP Client            | `apps/mcp-server/`、`app/tools/mcp_client.py`                       |
| B   | Agent 评测集 30 任务 + runner + CI 门禁           | `eval/datasets/agent_tasks.jsonl`、`eval/runners/run_agent_eval.py` |
| C   | Trace / 成本账本 / 预算守卫 / 限流 / Guardrail v0 | `apps/api/app/obs/`、`app/security/guardrails.py`                   |
| B/D | Agent 时间线 + 审批 UI + Ops 看板                 | `apps/web/src/pages/`                                               |
| A   | 开源边界、产品页、首篇技术文章                    | `docs/product/`、产品页                                             |
| D   | JD 追踪 ≥ 3 次、简历 v0/v1、面试题 ≥ 25           | `projects/career/`                                                  |

## 5. 本阶段不应该做什么

- 不做 Multi-Agent、不做 Agent 群聊、不追新框架（只用 LangGraph）。
- 不做认证 / 多租户 / Postgres（phase_03）。
- 不把「学 LangGraph / MCP」本身当目标：每个知识点必须落到 WorkPilot 的一个可演示功能。
- 不接定制外包、不主动私聊拓客。
- JD 出现新技术 ≠ 加入计划；只有「多个岗位反复出现 + 与 WorkPilot 相关 + 1–2 周内能出成果」才考虑。

## 6. 本阶段核心能力

- **B**：Function Calling、Tool Schema、ReAct / Plan-Execute、LangGraph（State/Node/Edge/Checkpointer/Interrupt）、Memory、MCP、Agent Evaluation、LLM-as-a-judge。
- **C**：Tracing、Token/Cost、Rate Limit、Timeout/Retry、Guardrail、CI 门禁。
- **D**：JD 追踪、简历 v0/v1、P2 作品集、面试题库。
- **A**：开源核心 / Pro Kit 边界、产品页、SEO 文章。

## 7. 进入条件

phase_01 核心验收 PASS：WorkPilot v0.5 已部署、50 题评测基线存在、P1 作品集完成。

## 8. 完成条件 / 阶段验收（第 16 周 Day57）

- [ ] v1.0 tag 已打，云端已更新
- [ ] Agent 30 任务评测报告：任务成功率、工具选择准确率、平均步数、P95 延迟、平均成本均有数值
- [ ] 未经审批的写操作 = 0（有测试证明）
- [ ] 在 VS Code / Cursor / Claude Desktop 任一 IDE 中通过 MCP 调用 WorkPilot 成功（录屏）
- [ ] 任一请求可在 Trace 页面看到 LLM / 检索 / 工具调用明细与成本
- [ ] `make eval` 在 CI 中运行，回归下降会失败
- [ ] P2 作品集：README + 架构 + Demo + 评测报告 + 技术文章
- [ ] 简历 v1 完成；JD 追踪记录 ≥ 3 次；面试题 ≥ 25 道

## 9. 下一阶段依赖什么

phase_03 复用：Agent 运行时（场景包就是一个 LangGraph 工作流）、HITL（场景写操作）、Eval Kit（场景评测与回归）、Observability（生产运维）、Guardrail v0（安全加固起点）、开源仓库与产品页（Portfolio 与 Pro Kit 入口）。

## 完成本阶段后，DA-01 比阶段开始前多了什么？

从「带引用的知识助手」变成「可审批、可评测、可观测、可嵌入 IDE 的研发 Agent 平台」（v1.0 / P2），并已公开发布，有第二份作品集和简历 v1。
