# Week 24 · TASKS

## Task 1：三版简历（Day72 · 12-08）

### 做什么

先写 `career/resume/facts.md`（数字 + 来源链接，单一事实来源），再写 Frontend / AI Full-Stack / AI Engineer 三版（各 1 页，中文为主，AI Engineer 可加英文版）；用 LLM 扮演对应岗位招聘方挑刺 → 修订；pandoc 导出 PDF。

### 为什么做

总计划 §6.5 与 §12.3 的必备资产；三版对应三类目标岗位，同一事实不同侧重。

### 资产锚点

- 模块：M13.3
- 版本：—（引用 v0.5 / v1.0 / v2.0 证据）

### 前置依赖

- Eval v2 报告、p3-notes、安全报告、usage-stats、Portfolio URL
- W16 简历 v1、W2 起 capability-matrix 与 JD 追踪

### 具体执行步骤（概要，详见 day72_20261208/PLAN.md）

1. facts.md：按「项目 / 指标 / 数值 / 来源 / 日期」逐条收集。
2. 三版简历结构与侧重。
3. 写 bullet（XYZ 公式）。
4. LLM 招聘方挑刺 → 修订 → review-log。
5. 导出 PDF，替换 Portfolio 简历。

### 验收标准

- [ ] facts.md 每条有来源
- [ ] 三版各 1 页，bullet 全部可追溯
- [ ] 修订记录可见

### 完成后的产出

- `career/resume/facts.md`、三版简历 md + PDF、`review-log.md`

### 求职映射

直接用于投递与面试。

### 如果时间不够 / 没有必要

- 先完成 AI Full-Stack（主投），另两版复用 80% 内容并调整顺序与关键词。
- 英文版进 P2。

---

## Task 2：小批量投递 + 追踪（Day73 · 12-09）

### 做什么

建 `career/applications.md`（公司 / 岗位 / 渠道 / 日期 / 版本 / JD 匹配度 / 状态 / 反馈）；按 JD 匹配度筛选 3–5 个岗位，每个做 3–5 处简历定制（关键词、bullet 顺序、项目侧重）并正常投递；记录 JD 高频要求，更新能力矩阵。

### 为什么做

用真实市场反馈检验半年成果；JD 高频要求决定 W25 面试准备优先级。

### 资产锚点

- 模块：M13.3、M13.1
- 版本：—

### 前置依赖

- Day72 三版简历
- `career/jd-tracking.md`（W2 起）

### 具体执行步骤（概要，详见 day73_20261209/PLAN.md）

1. 建追踪表与状态定义。
2. 从 JD 追踪中挑 8–10 个候选 → 打匹配度 → 选 3–5。
3. 每个岗位定制 + 投递 + 记录。
4. 汇总 JD 高频要求 → 更新能力矩阵与 W25 题库优先级。

### 验收标准

- [ ] 追踪表已建
- [ ] 3–5 个岗位已投递，每个有定制点记录
- [ ] JD 高频要求 Top 10 已更新到能力矩阵

### 完成后的产出

- `career/applications.md`、定制版简历（`resume/tailored/<公司>-<岗位>.pdf`，仅本地私有仓库）
- `career/capability-matrix.md` 更新

### 求职映射

求职漏斗管理（投递 → 回复 → 面试 → offer）。

### 如果时间不够 / 没有必要

- 投 3 个即可；定制点每个 3 处。
- 未回复不追问（被动沟通原则）。

---
