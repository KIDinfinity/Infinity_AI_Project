# Week 11 · LangGraph Agent v1（Phase 2 · Day40–Day42 · 11-06 → 11-08）

## 1. 本周核心目标

把 W10 手写的 v0 循环迁移到 LangGraph（显式 State / Node / 条件边），加上节点级重试、工具错误转观察、Gateway provider 降级、SQLite checkpointer（可中断后恢复），并用 10 个任务做 v0 vs v1 的量化对比，写 ADR-0006，把 `/v1/agent/run` 默认切到 v1。

## 2. 资产锚点

| 构建模块              | 版本里程碑     | 本周结束 WorkPilot 能演示什么                                                           |
| --------------------- | -------------- | --------------------------------------------------------------------------------------- |
| M7.2 LangGraph 工作流 | 为 v0.8 做准备 | `docs/agent-graph.md` 中由代码生成的 Mermaid 图；同一 SSE 事件协议下前端无改动即可跑 v1 |
| M7.2 + M1.2 可靠性    | 为 v0.8 做准备 | 故障注入：工具超时 / 主 LLM 500 时，运行优雅完成或明确失败；主 provider 挂掉自动切备用  |
| M7.2 checkpoint       | 为 v0.8 做准备 | 运行中 Ctrl+C，`--resume <run_id>` 从上一个已完成节点继续                               |
| M7 对比 + ADR         | 为 v0.8 做准备 | `eval/reports/20261108-agent-v0-vs-v1.md` + `docs/adr/0006-why-langgraph.md`            |
| M13.1 JD 追踪         | —              | `career/job-market.md` 第 2 轮 + `capability-matrix.md` 更新                            |

## 3. 为什么这一周存在

- LangGraph 是 JD 中出现最多的 Agent 框架；更重要的是 W12 的 checkpoint 记忆与 `interrupt()` 人工审批都是它的原生能力，手写实现成本高且易错。
- 先有 v0 再迁移，才能用数据回答「框架带来了什么、付出了什么」，而不是「因为火所以用」。
- 可靠性（重试 / 降级 / 恢复）是从 Demo 到生产的分水岭，也是面试中区分度最高的话题之一。

## 4. 本周在路线中的位置

```text
上周产出（W10）：loop_v0 + steps.py 纯函数 + ResearchReport + SSE 事件协议 + AgentPage + agent_smoke.jsonl 基线（v0.7）
        ↓
本周（W11）：state.py / graph.py（复用 steps.py）→ RetryPolicy + 工具错误转观察 + provider fallback → AsyncSqliteSaver checkpoint → 故障注入测试 → v0 vs v1 对比 + ADR-0006 → 默认 v1
        ↓
下周输入（W12）：带 checkpointer 的 compiled graph、thread_id 机制、updates→SSE 事件适配器、AgentRun 的 conversation_id/pending_action 字段 → 会话记忆、长期记忆、interrupt 审批
```

## 5. 每日安排

| Day   | 日期  | Task                                  | 当日 P0 产出                                                                        | 模块      | 状态 |
| ----- | ----- | ------------------------------------- | ----------------------------------------------------------------------------------- | --------- | ---- |
| Day40 | 11-06 | Task 1：LangGraph 迁移                | `app/agent/state.py` `graph.py` `nodes.py` + `docs/agent-graph.md` + v0/v1 对齐测试 | M7.2      | TODO |
| Day41 | 11-07 | Task 2：重试 / 降级 / checkpoint      | RetryPolicy + Gateway fallback + AsyncSqliteSaver + 恢复演示 + 故障注入测试         | M7.2 M1.2 | TODO |
| Day42 | 11-08 | Task 3：v0 vs v1 对比 + ADR + JD 追踪 | 对比报告 + ADR-0006 + `AGENT_VERSION` 开关 + JD 第 2 轮                             | M7 M13.1  | TODO |

## 6. 本周必须留下的资产

```text
~/lab/workpilot/
├── apps/api/app/agent/
│   ├── state.py                 # ResearchState(TypedDict)
│   ├── nodes.py                 # plan / act / tools / decide / synthesize 节点（包装 steps.py）
│   ├── graph.py                 # build_graph(checkpointer=None, interrupt_before=None)
│   ├── events.py                # LangGraph updates → AgentEvent（复用 W10 SSE 协议）
│   └── runner.py                # run_v1_events()：astream + 事件适配 + 落库
├── apps/api/app/llm/gateway.py  # + provider fallback（LLM_FALLBACK_*）
├── apps/api/app/core/config.py  # + LLM_FALLBACK_* / AGENT_VERSION / CHECKPOINT_DB
├── apps/api/tests/agent/{test_parity.py,test_faults.py,test_checkpoint.py}
├── scripts/agent_v1.py          # 支持 --resume <run_id>
├── docs/agent-graph.md          # draw_mermaid() 生成
├── docs/adr/0006-why-langgraph.md
├── eval/runners/compare_agents.py
└── eval/reports/20261108-agent-v0-vs-v1.md
~/lab/projects/career/{job-market.md,capability-matrix.md}
```

## 7. 本周验收标准

- [ ] PASS / FAIL：图结构为 plan → act → tools → decide，条件边 continue→act / replan→plan / finish→synthesize → END；Mermaid 图已生成
- [ ] PASS / FAIL：v0/v1 对齐测试（假 LLM，3 个任务）工具调用序列一致
- [ ] PASS / FAIL：节点 RetryPolicy 生效（单测：第 1 次抛瞬时错误，第 2 次成功）
- [ ] PASS / FAIL：主 provider 500 → 备用 provider 成功（respx 单测）；全部失败 → run 状态 failed + error 事件，不挂起
- [ ] PASS / FAIL：工具超时 → 观察中记录错误 → 运行仍能完成
- [ ] PASS / FAIL：checkpoint 恢复演示成功（截图 / 终端输出存档）
- [ ] PASS / FAIL：对比报告 10 任务 × 2 版本，含成功率 / 步数 / 延迟 / tokens / 成本 / 失败类型
- [ ] PASS / FAIL：ADR-0006 已提交；`/v1/agent/run` 默认 v1，`AGENT_VERSION=v0` 可回退
- [ ] PASS / FAIL：JD 第 2 轮 + 能力矩阵已更新

## 8. 求职映射

- 本周能力：LangGraph（StateGraph / reducer / 条件边 / RetryPolicy / checkpointer）、LLM 多供应商降级、故障注入测试、架构决策记录。
- 简历 bullet 草稿：
  - 将手写 Agent 迁移至 LangGraph 状态图，复用节点逻辑实现 v0/v1 行为对齐；10 任务对比显示成功率 **%→**%、平均步数 **→**。
  - 设计三层可靠性策略（Gateway 重试 + Provider 自动降级 + 节点级 RetryPolicy）与 SQLite checkpoint，支持中断恢复；故障注入测试覆盖工具超时与 LLM 5xx。
- 面试题：
  1. LangGraph 的 State reducer 是什么？`Annotated[list, operator.add]` 解决了什么问题？
  2. 重试应该放在哪一层？多层重试会带来什么问题？
  3. 为什么不直接用 LangChain 的 AgentExecutor / create_react_agent？

## 9. 本周禁止事项

- 不做 Multi-Agent / 子图编排 / supervisor 模式。
- 不引入 LangChain 的模型类（ChatOpenAI 等）替换 M1 Gateway；节点内部继续调自己的 Gateway。
- 不上 LangSmith / LangGraph Platform / LangGraph Studio 云服务（数据外发 + 范围扩张）。
- 不改前端协议：v1 必须产出与 v0 相同的 SSE 事件。
- 不在本周做记忆与审批（W12）。

## 10. 时间不够时（最小保留）

- Day40：state + graph + 节点 + Mermaid 图；对齐测试只做 1 个任务。
- Day41：checkpointer + 恢复演示 + 工具超时测试；provider fallback 只做配置与单测，不做 Ollama 实测。
- Day42：对比只跑 5 个任务；ADR 写「决策 / 理由 / 代价」三段；JD 追踪压缩为 5 个。

## 11. 周复盘（Day42 结束时填写）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（Mermaid 图 + 恢复演示 + 对比表）
- v0 vs v1 关键数字：成功率 ** / **，平均步数 ** / **，平均成本 ¥** / ¥**
- LangGraph 解决了 W10 复盘里记下的哪个难点？没解决哪个？\_\_\_\_
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
