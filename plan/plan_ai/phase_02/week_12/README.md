# Week 12 · Memory + Human-in-the-loop（Phase 2 · Day43–Day45 · 12-14 → 12-16）

## 1. 本周核心目标

让 WorkPilot Agent 「记得住、问得了人」：会话记忆（thread*id 绑定 conversation + 上下文压缩，支持「把上一份报告第二点展开」）、长期记忆（Qdrant `memories*{workspace}`，抽取 / 去重 / 脱敏 / 可查可删）、写操作人工审批（`interrupt()`+`Command(resume=...)`，前端审批卡片），并用 SP-B 迷你流程「需求 → 任务拆解 → 审批 → 在沙盒仓库建 Issue」跑通第一个「会做事」的场景。打 tag `v0.8.0`。

## 2. 资产锚点

| 构建模块       | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                              |
| -------------- | ---------- | ------------------------------------------------------------------------------------------ |
| M7.3 会话记忆  | v0.8       | 同一会话中追问「把上一份报告第二点展开」，Agent 基于上一份报告继续；长会话自动压缩         |
| M7.3 长期记忆  | v0.8       | 说一次「报告用中文且先给结论」，新会话里的报告自动遵守；`GET/DELETE /v1/memories` 可查可删 |
| M7.4 HITL 审批 | v0.8       | Agent 要创建 Issue 时暂停，前端出现审批卡片（可改参数）；批准后才写入 Gitea 沙盒仓库       |
| M10 SP-B 试点  | v0.8       | 一段需求文本 → TaskBreakdown → 审批 → sandbox-issues 中出现对应 Issue                      |
| M13.3 简历     | —          | 三版简历双周更新（加入 LangGraph / Memory / HITL 条目）                                    |

> 若 W3 Day13 选定的主场景不是 SP-B：保留 HITL 机制不变，把 Day45 的迷你流程换成主场景的写操作（如 SP-E 周报 → 审批后发评论、SP-C 评审 → 审批后写 PR 评论），工具仍只作用于沙盒仓库。

## 3. 为什么这一周存在

- 「未经审批的写操作 = 0」是 DA01 §11 的硬指标，也是 F3「写操作必须人工审批」的产品承诺——没有 HITL，Agent 不能碰任何写工具。
- 记忆让 WorkPilot 从「一次性问答」变成「持续协作」：追问、偏好、项目上下文。
- SP-B 是 DA-01 主场景（默认），本周第一次端到端跑通，W17–W18 在此基础上做场景包 MVP。

## 4. 本周在路线中的位置

```text
上周产出（W11）：LangGraph v1（plan/act/tools/decide/synthesize）+ RetryPolicy + provider fallback + AsyncSqliteSaver + 默认 v1
        ↓
本周（W12）：thread_id=conversation_id + messages/summary 压缩 → Qdrant 长期记忆（抽取/去重/脱敏/注入）→ gitea_issue_create(write) + approve 节点 interrupt() + approve API + 审批卡片 → SP-B 迷你流程 → v0.8.0
        ↓
下周输入（W13）：可审批的工具层（permission + approved 执行门）、kb/gitea 工具、Agent run API → MCP Server 暴露工具、MCP Client 接入外部工具
```

## 5. 每日安排

| Day   | 日期  | Task                                             | 当日 P0 产出                                                                                            | 模块     | 状态 |
| ----- | ----- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | -------- | ---- |
| Day43 | 12-14 | Task 1：会话记忆 + 上下文压缩                    | `messages` / `summary` 状态 + summarize 节点 + 追问演示 + 测试                                          | M7.3     | TODO |
| Day44 | 12-15 | Task 2：长期记忆                                 | `app/agent/memory.py` + remember 节点 + 注入 + `GET/DELETE /v1/memories` + 偏好演示                     | M7.3     | TODO |
| Day45 | 12-16 | Task 3：HITL 审批 + SP-B 试点 + 简历更新（v0.8） | `gitea_issue_create` + approve 节点 + approve API + mock 断言测试 + 审批卡片 + SP-B 流程 + tag `v0.8.0` | M7.4 M10 | TODO |

## 6. 本周必须留下的资产

```text
~/lab/workpilot/
├── apps/api/app/agent/
│   ├── state.py                 # + messages(add_messages) / summary / memories；observations 改为可重置 reducer
│   ├── context.py               # 计数（tiktoken 近似）+ 压缩策略
│   ├── memory.py                # MemoryStore（Qdrant）+ 抽取 + 脱敏
│   ├── hitl.py                  # approve_node + 路由
│   └── graph.py                 # + summarize / remember / approve 节点
├── apps/api/app/security/redact.py          # 密钥 / 手机号 / 邮箱脱敏正则
├── apps/api/app/tools/builtin/gitea.py      # + gitea_issue_create（permission=write，仅沙盒仓库）
├── apps/api/app/tools/registry.py           # execute(..., approved=False) 写操作门禁
├── apps/api/app/routes/{agent.py,memories.py}
├── apps/api/app/scenarios/sp_b_req_breakdown/graph.py
├── apps/api/tests/agent/{test_conversation.py,test_memory.py,test_hitl.py}
├── apps/web/src/components/agent/ApprovalCard.tsx
├── prompts/{summarizer.v1.md,memory_extractor.v1.md}
├── scripts/sp_b_pilot.py
└── docs/api.md                              # + approval_required 事件、approve / memories 接口
~/lab/projects/career/resume/*.md            # 双周更新
```

## 7. 本周验收标准

- [ ] PASS / FAIL：同一 `conversation_id` 两次运行，第二次追问能引用第一次报告内容（测试 + 演示）
- [ ] PASS / FAIL：历史超过 token 阈值时生成 `summary`，原文只保留最近 k 条（测试）
- [ ] PASS / FAIL：偏好记忆写入后，新会话报告遵守偏好；相似度 > 0.9 的记忆更新而非新增（测试用 Qdrant `:memory:`）
- [ ] PASS / FAIL：记忆写入前脱敏（密钥 / 手机号 / 邮箱单测）；记忆只从用户消息抽取，不从工具输出抽取
- [ ] PASS / FAIL：**未批准时 Gitea 写接口调用次数 = 0**（respx 断言：中断时、拒绝后均为 0；批准后为 1）
- [ ] PASS / FAIL：`registry.execute()` 对未审批的 write 工具直接拒绝（单测）
- [ ] PASS / FAIL：前端审批卡片可批准 / 拒绝 / 修改参数后批准，时间线继续
- [ ] PASS / FAIL：SP-B 迷你流程在 sandbox-issues 中创建 ≥ 2 个 Issue（截图）
- [ ] PASS / FAIL：tag `v0.8.0` 推送；简历已更新

## 8. 求职映射

- 本周能力：Agent Memory（短期 / 长期、压缩、去重、遗忘）、Human-in-the-loop、过度代理（Excessive Agency）防护、隐私脱敏。
- 简历 bullet 草稿：
  - 基于 LangGraph checkpointer 与 Qdrant 实现 Agent 双层记忆：会话上下文自动摘要压缩（tokens 降低 \_\_%），长期偏好记忆抽取、去重（相似度 > 0.9 合并）与脱敏，支持用户查看与删除。
  - 使用 `interrupt()` 实现写操作人工审批（批准 / 拒绝 / 修改参数），执行层二次门禁，测试证明未审批写操作为 0；落地「需求 → 任务拆解 → 审批 → 自动建 Issue」研发场景。
- 面试题：
  1. Agent 的短期记忆和长期记忆分别怎么实现？长期记忆什么时候写、写什么、怎么防止污染？
  2. 人工审批节点恢复执行时，节点会重新执行吗？怎么避免重复写入？
  3. 如何防止 Agent 越权执行写操作？（OWASP LLM Top 10：Excessive Agency）

## 9. 本周禁止事项

- 不做 Multi-Agent、不做「记忆图谱」/ 知识图谱。
- 写工具只允许 `gitea_issue_create` 且只对 `sandbox-issues`；不接公司 Gitea / Jira / 飞书。
- 不做自动审批 / 白名单自动放行（全部人工）；不做批量审批 UI 之外的花样。
- 不把工具输出、网页内容写入长期记忆。
- 不做登录与多用户（W19），`workspace` 先固定为 `default`。

## 10. 时间不够时（最小保留）

- Day43：thread 绑定 conversation + 追问演示；压缩只写测试不做真实长会话演练。
- Day44：MemoryStore + 手动写入 / 读取注入 + 脱敏；自动抽取用最简提示词；API 只做 GET。
- Day45：write 工具 + approve 节点 + approve API + mock 断言测试 + tag（P0）；审批卡片与 SP-B 流程顺延到 Day46 前 30 分钟（在 draft.md 记录顺延）。

## 11. 周复盘（Day45 结束时填写）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（审批卡片录屏 + sandbox-issues 截图）
- 未审批写操作测试结果：\_\_\_\_
- 记忆是否真的改善了体验？有没有出现错误记忆 / 记忆污染：\_\_\_\_
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
