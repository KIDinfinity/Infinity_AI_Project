# Week 17 · TASKS

## Task 1：P3 问题定义（Day58 · 11-24）

### 做什么

写 `docs/product/p3-definition.md`：8 要素（问题 / 用户 / 场景 / 价值 / 验证方式 / 交付方式 / 商业模式 / 技术组合）、成功指标、用户流程、范围内外、风险清单、数据计划；在 `data/scenarios/` 收集 ≥ 20 个手工脱敏的 SP-B 样例。

### 为什么做

P3 = DA-01 主场景包的生产级版本。问题定义是后面 W18 实现、W20 评测、W23 Portfolio「Problem / Why AI」两节的唯一来源；样例是 W18 跑通、W20 评测集的原料。

### 资产锚点

- 模块：M10 场景包（SP-B 需求→任务拆解→Issue 草案）
- 版本：为 v1.1 做准备

### 前置依赖

- W3 Day13 的 `docs/product/da01-definition.md`（场景选型结果）
- W8 以来 SQLite 中的 Conversation / Message / Feedback / AgentRun 数据
- `projects/product-lab/pain-pool.md`

### 具体执行步骤（概要，详见 day58_20261124/PLAN.md）

1. 用 SQL 统计 W8 以来的使用与反馈数据，写 `eval/reports/<日期>-usage-stats.md`。
2. 按模板写 8 要素，价值用「手工耗时 vs 预期耗时」量化。
3. 写成功指标（引用蓝图 §11）、用户流程、范围内/外、风险。
4. 写 `data/scenarios/README.md` 脱敏检查清单，手工改写 ≥ 20 个样例。
5. 提交（样例不入库）。

### 验收标准

- [ ] 8 要素齐全且具体
- [ ] 成功指标 ≥ 5 条，每条有测量方式与数据来源
- [ ] 范围内 ≥ 5 / 范围外 ≥ 5 / 风险 ≥ 5
- [ ] `data/scenarios/` ≥ 20 个样例且全部过清单（P0 最低 10 个）

### 完成后的产出

- `docs/product/p3-definition.md`
- `data/scenarios/README.md`、`data/scenarios/spb_001.md` … `spb_020.md`（本地）
- `eval/reports/<日期>-usage-stats.md`

### 求职映射

「AI 产品问题定义 + 指标设计」：面试中回答「为什么做这个项目」「怎么证明有用」。

### 如果时间不够 / 没有必要

- 只保 8 要素 + 成功指标 + 10 个样例；风险清单可压到 3 条。
- 使用统计如果数据很少（< 10 次会话），如实写「样本少」，不要补造数据。

---

## Task 2：架构 v2 + 数据模型（Day59 · 11-25）

### 做什么

写 `docs/architecture-v2.md`：多空间 + 认证 + Postgres + 异步导入 worker + 场景图 + 安全分层的架构图；16 实体 mermaid ER 图；SQLite → Postgres 迁移方案；场景图节点 / 边 / interrupt 设计；写 `docs/adr/0007-multi-tenancy.md`。

### 为什么做

W19 一次性完成 Postgres + 认证 + 隔离，必须先定数据模型与隔离策略；W18 实现场景图必须先有节点设计。设计错误在文档阶段修复成本最低。

### 资产锚点

- 模块：M11.1 / M11.2（设计）、M10（场景图）、M5.4（部署链路设计）
- 版本：为 v1.1 / v1.2 做准备

### 前置依赖

- Day58 的 p3-definition.md（范围决定实体）
- `docs/architecture.md`（v1）、`docs/adr/0001–0006`
- 现有 `apps/api/app/db/models.py`

### 具体执行步骤（概要，详见 day59_20261125/PLAN.md）

1. 画架构 v2（mermaid flowchart），标出信任边界。
2. 画 ER 图（16 实体），列出每表 `workspace_id` 与索引。
3. 写 SQLite → Postgres 迁移方案（备份 → 导出使用数据 → 重建 → 可选迁移脚本）。
4. 写 ADR 0007（两种 Qdrant 隔离方案对比）。
5. 画 SP-B 场景图（节点 / 条件边 / interrupt / 写工具 / 幂等键）。
6. 确认开源边界（open-core.md）对 P3 代码存放位置的影响。

### 验收标准

- [ ] ER 图 16 实体齐全，关系与外键正确
- [ ] 每个业务表都标注 `workspace_id`（User 除外）
- [ ] ADR 0007 含上下文 / 选项 / 决策 / 后果 四节
- [ ] 场景图含 7 个节点、1 条回边（self_check → breakdown 最多 1 次）、1 个 interrupt
- [ ] 迁移方案写明「使用日志不丢」的步骤

### 完成后的产出

- `docs/architecture-v2.md`
- `docs/adr/0007-multi-tenancy.md`

### 求职映射

System Design 题「企业 AI 知识库」中的多租户、数据模型、异步处理三块直接复用本文档（W25 Day75）。

### 如果时间不够 / 没有必要

- P0 只保 ER 图 + ADR 0007；架构图 v2 与场景图可推迟到 Day60 开头 15 分钟完成。
- 不画类图、时序图（除非真的卡住才画）。

---
