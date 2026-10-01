# Week 25 · TASKS

## Task 1：面试题库 + 系统设计（Day74 · 12-10）

### 做什么

整理面试题库 ≥ 30 题，分六大类（AI 基础 / RAG / Agent / Engineering / System Design / STAR），每题写要点答案（3–5 bullet）+ WorkPilot 证据链接；完成 2 道系统设计题（企业 AI 知识库 + AI 客服 Agent 或自选），含架构图与关键权衡。

### 为什么做

总计划 §6.6 的必备资产；面试中「能讲清楚」比「能做出来」更需要刻意练习；系统设计是 AI Full-Stack / AI Platform 岗位的高频考察点。

### 资产锚点

- 模块：M13.4
- 版本：—（引用 v0.5 / v1.0 / v2.0 证据）

### 前置依赖

- W24 JD 高频汇总（决定题库优先级）
- Eval v2 报告、安全报告、架构文档、ADR
- W16 面试题 ≥ 25（本次扩展到 ≥ 30 并补充证据链接）

### 具体执行步骤（概要，详见 day74_20261210/PLAN.md）

1. 从 W16 题库 + JD 高频要求出发，确定 30 题清单。
2. 逐题写要点答案（3–5 bullet）+ 证据链接。
3. 系统设计 ×2：画架构图 → 写关键权衡 → 自问自答追问。
4. 提交。

### 验收标准

- [ ] 题库 ≥ 30 题，六大类覆盖
- [ ] ≥ 50% 题目有 WorkPilot 证据链接
- [ ] 系统设计 ×2 有架构图 + ≥ 3 个权衡

### 完成后的产出

- `career/interview/questions.md`
- `career/interview/system-design-1.md`
- `career/interview/system-design-2.md`

### 求职映射

直接用于面试。

### 如果时间不够 / 没有必要

- 先完成 AI 基础 + RAG + Agent 三类（约 20 题）+ 系统设计 ×1。
- Engineering / System Design / STAR 类顺延到 Day75 或 W26。

---

## Task 2：STAR + 模拟面试（Day75 · 12-11）

### 做什么

写 3 个 STAR 故事（覆盖 P1/P2/P3 各一个场景），每个含「情境 → 任务 → 行动 → 结果 + 数字」；用 LLM 扮演面试官进行 ≥ 1 轮模拟面试（技术面 + 项目面），记录反馈与改进点。

### 为什么做

STAR 是行为面试的标准框架；模拟面试暴露「以为自己懂了但讲不清楚」的盲区。

### 资产锚点

- 模块：M13.4
- 版本：—

### 前置依赖

- Day74 题库 + 系统设计
- P1/P2/P3 作品集与评测报告

### 具体执行步骤（概要，详见 day75_20261211/PLAN.md）

1. 写 3 个 STAR 故事（P1 知识库 / P2 Agent / P3 生产化）。
2. LLM 模拟面试：技术面（30 min）+ 项目面（20 min）。
3. 记录反馈 + 改进点 → `mock-interview-log.md`。
4. 提交。

### 验收标准

- [ ] STAR ×3，每个有「情境 → 任务 → 行动 → 结果 + 数字」
- [ ] 模拟面试 ≥ 1 轮，有 LLM 反馈 + 改进记录

### 完成后的产出

- `career/interview/star-stories.md`
- `career/interview/mock-interview-log.md`

### 求职映射

直接用于面试。

### 如果时间不够 / 没有必要

- STAR ×2（P2/P3）+ 模拟面试 1 轮（技术面）。
- P1 STAR 和项目面顺延到 W26。
