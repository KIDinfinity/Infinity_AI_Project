# Week 17 · P3 问题定义 + 架构 v2（Phase 3 · Day58–Day59 · 11-24 → 11-25）

## 1. 本周核心目标

把 WorkPilot 从「v1.0 能演示的 Agent 平台」重新对准一个**具体研发痛点**：写出 P3 问题定义（8 要素 + 成功指标 + 范围），并完成支撑 v1.1–v2.0 的**架构 v2 与数据模型**（多空间、认证、Postgres、异步导入、场景图、安全分层）。本周只写文档和设计图，不写产品代码。

## 2. 资产锚点

| 构建模块                                                              | 版本里程碑            | 本周结束 WorkPilot 能演示什么                                                                                                                                     |
| --------------------------------------------------------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M10 场景包（SP-B 默认）、M11 安全与多租户（设计）、M3（成功指标定义） | 为 v1.1 / v1.2 做准备 | 能用 `docs/product/p3-definition.md` + `docs/architecture-v2.md` 在 5 分钟内讲清「P3 解决什么问题、怎么验证、系统怎么演进」；`data/scenarios/` 有 ≥ 20 个脱敏样例 |

## 3. 为什么这一周存在

- P3 是 AI Full-Stack / AI Platform 岗位最看重的证据，面试官会追问「为什么做这个、怎么证明有用」。没有问题定义，后面 4 周就会变成堆功能。
- W19 要从 SQLite 切到 Postgres、引入认证和多空间，W21 要做安全加固——**先设计后编码**，避免 W19 返工数据模型。
- 只有 2 天：Day58 定义「做什么、怎么算成功」，Day59 定义「系统怎么承载」。

## 4. 本周在路线中的位置

```text
上周产出（W16）：v1.0 tag、P2 作品集 p2.md、open-core.md、简历 v1、使用日志与反馈数据（SQLite）
        ↓
本周（W17）：p3-definition.md（8 要素 + §11 指标）+ data/scenarios/ ≥20 脱敏样例
             architecture-v2.md + ER 图 + ADR 0007 + 场景图设计
        ↓
下周输入（W18）：按场景图节点实现 app/scenarios/sp_b_req_breakdown/，用 data/scenarios/ 样例跑通
```

## 5. 每日安排

| Day   | 日期  | Task                       | 当日 P0 产出                                                                                          | 模块      | 状态 |
| ----- | ----- | -------------------------- | ----------------------------------------------------------------------------------------------------- | --------- | ---- |
| Day58 | 11-24 | Task 1：P3 问题定义        | `docs/product/p3-definition.md`（8 要素 + 成功指标 + 范围）+ `data/scenarios/` ≥ 10 个样例（冲刺 20） | M10       | TODO |
| Day59 | 11-25 | Task 2：架构 v2 + 数据模型 | `docs/architecture-v2.md`（含 ER 图、场景图）+ `docs/adr/0007-multi-tenancy.md`                       | M11 / M10 | TODO |

## 6. 本周必须留下的资产

- `~/lab/workpilot/docs/product/p3-definition.md`
- `~/lab/workpilot/data/scenarios/README.md`（脱敏检查清单）+ `data/scenarios/spb_*.md` ≥ 20 个（本地，gitignore）
- `~/lab/workpilot/docs/architecture-v2.md`（mermaid：系统架构 v2、ER 图、场景图、迁移方案）
- `~/lab/workpilot/docs/adr/0007-multi-tenancy.md`
- `~/lab/workpilot/eval/reports/<日期>-usage-stats.md`（W8 以来使用数据统计，P1）

## 7. 本周验收标准

- [ ] PASS / FAIL：p3-definition.md 8 要素齐全，每个要素有具体内容（不是空模板）
- [ ] PASS / FAIL：成功指标直接引用蓝图 §11 的 P3 行（rubric 通过率 ≥ 0.75、攻击拦截 100%、恢复 < 30 分钟、真实使用 ≥ 30 次）
- [ ] PASS / FAIL：范围内 / 范围外清单各 ≥ 5 条，风险 ≥ 5 条且有应对
- [ ] PASS / FAIL：`data/scenarios/` ≥ 20 个样例，全部通过脱敏检查清单
- [ ] PASS / FAIL：ER 图包含 16 个实体，所有业务表带 `workspace_id`
- [ ] PASS / FAIL：ADR 0007 写清「单 collection + payload 过滤」vs「每空间一个 collection」的取舍与结论
- [ ] PASS / FAIL：场景图标出所有节点、条件边、interrupt 点、写工具位置

## 8. 求职映射

- 本周能力：AI 产品问题定义、成功指标设计、多租户架构设计、数据建模、ADR 写作。
- 简历 bullet 草稿：
  - 「基于 ≥ ** 次真实使用日志与 ** 条反馈，定义 P3 场景『需求→任务拆解→Issue』，设定 rubric 通过率 ≥ 0.75、攻击拦截 100% 等可量化验收指标」
  - 「设计多租户架构 v2（JWT + RBAC + 行级 workspace_id + Qdrant payload 过滤），以 ADR 记录 collection 隔离方案取舍」
- 面试题：
  1. 你怎么判断一个 AI 功能值得做？（答要点：真实频率 × 耗时 × 可验证性；用使用日志与手工耗时对比，而不是凭感觉）
  2. 多租户向量库怎么隔离？（答要点：单 collection + `workspace_id` keyword 索引 + 强制 must 过滤；租户少且需物理隔离时才每租户一个 collection）
  3. 为什么要写 ADR？（答要点：记录上下文、选项、取舍和后果，避免重复争论，方便新人和面试官理解决策）

## 9. 本周禁止事项

- 不写场景包代码、不改数据库、不装 Postgres（W18/W19 再做）。
- 不把任何公司真实需求原文放进 `data/scenarios/`、外部 LLM 或公开仓库。
- 不新增场景包（只做 W3 Day13 选定的 1 主 + 1 辅；本组计划以 SP-B 为例）。
- 不引入 Redis、Kafka、K8s、微服务等新基础设施。

## 10. 时间不够时（最小保留）

- Day58：8 要素 + 成功指标 + 10 个脱敏样例（剩余 10 个在 Day59 / Day60 前补齐）。
- Day59：ER 图 + ADR 0007（架构图 v2 与场景图可在 Day60 开头 15 分钟补）。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（预期：P3 定义 + 架构 v2 讲解 5 分钟）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
