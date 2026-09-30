# plan — 半年智能解决方案孵化执行目录

> 本目录是 DA-01 的**唯一执行工作空间**。历史文件在 `history/`，本目录只放当前可执行、可验收、可持续迭代的计划。

---

## 1. 半年最终目标

> **半年内完成至少一个经过真实验证、可以运行、可以交付、可以继续迭代的「智能解决方案资产」（DA-01），同时建立可直接用于求职的 AI 工程能力矩阵、GitHub 作品集、简历面试材料，形成以后可以重复「发现痛点 → 组合技术 → 验证 → 开发 → 发布 → 迭代 → 变现」的方法。**

最终结果不是「学会技术」，而是：一个真实智能解决方案资产 + 一套可复制的解决方案生产能力 + 一套可求职的 AI 工程作品集。

---

## 1.1 通用解决方案闭环（最高方法论）

```text
现实问题 → 感知 → AI → 决策 → 执行 → 反馈 → 学习优化
```

拿到任何真实问题，先判断问题类型（纯软件 / AI / 自动化 / 视觉 / 物理世界 / 机器人），再按需组合技术。不是每个问题都需要物理世界能力。

---

## 2. DA-01 定义

- **DA-01 = Intelligent Solution Asset 01**，本半年正在孵化的第一个智能解决方案资产，同时是求职作品集 Project 3（P3）的载体。
- DA-01 是「解决一个真实痛点的 AI × 软件 × 自动化 ×（必要时）物理世界能力的组合」，数字资产只是沉淀形式之一。
- 技术组合按需选择，不预设形态：
  - 第一层 纯数字：SaaS / Agent / CLI / API / 插件 / 工作流 / 数据产品 / SDK
  - 第二层 数字+现实：摄像头+AI / IoT+Agent / 机器人+Agent / 计算机视觉+自动化 / 传感器+决策
  - 第三层 完整解决方案：现实问题 → 感知 → AI → 决策 → 执行 → 反馈
- 决定顺序：**问题 → 用户 → 场景 → 价值 → 验证 → 解决方案形态 → 技术组合 → 技术栈**，而不是「技术 → 项目 → 找问题」。
- 最晚 **第 3 周** 明确 DA-01 的问题与技术组合；第 1–2 周处于问题探索状态。
- 不擅自编造产品名称、用户、商业模式。

## 2.1 三个锚点项目（求职作品集）

| 项目 | 代码 | 周范围 | 覆盖能力 | 求职对应 |
|---|---|---|---|---|
| P1 个人AI知识库助手 | P1-RAG-Assistant | 4–8 | LLM API / RAG / Chunk / Retrieval / Docker / Deployment | AI Engineer / GenAI Application |
| P2 AI Research Agent | P2-AI-Agent | 10–16 | Tool Calling / Agent Workflow / MCP / Evaluation / Observability | AI Agent Engineer / LLM Engineer |
| P3 完整AI生产级应用 | P3-AI-Solution | 17–26 | RAG + Agent + Production + Security + Guardrail | AI Full-Stack / AI Platform Engineer |

> 原则：同一个项目既是产品探索的里程碑，也是求职作品集的可解释成果。

## 2.2 四条能力线（贯穿所有周）

| 能力线 | 目标 | 代表内容 |
|---|---|---|
| **A线：AI产品 / 变现** | 做一个真实AI解决方案 | DA-01、用户、收入、SEO |
| **B线：AI Engineering** | RAG + Agent + Evaluation + Production AI | P1、P2、P3 的核心链路 |
| **C线：Infrastructure** | Docker + Cloud + CI/CD + Observability | 部署、监控、安全、备份 |
| **D线：Job Market / Portfolio** | 把项目转化成简历、GitHub、Demo、面试能力 | JD分析、能力矩阵、简历、面试 |

各阶段主线优先级：
- **第 1–8 周**：B > D > A > C
- **第 9–16 周**：B > D > A > C
- **第 17–26 周**：D ≈ B > A > C

---

## 3. 三阶段关系

| 阶段 | 周范围 | 生命周期 | 核心问题 |
|---|---|---|---|
| phase_01 探索与沉淀期 | 第 1–8 周 | 探索 / 建立 / 验证 | 解决什么真实问题？DA-01 是什么？最小可行方案是什么？ |
| phase_02 方案落地变现期 | 第 9–16 周 | 开发 / 交付 / 验证 | 能不能做出来？能不能运行？能不能让别人使用？能不能产生首笔收入？ |
| phase_03 迭代放大期 | 第 17–26 周 | 发布 / 商业化验证 / 迭代 / 沉淀 | 能不能形成可持续智能资产？能否验证商业价值？能否复制到 DA-02？ |

---

## 4. 26 周路线

| 周 | 阶段 | 主线 | 核心目标 | 能力线侧重 | 产出 |
|---|---|---|---|---|---|
| 1 | 短期 | B/D | 研发底座 + AI岗位能力地图 | D: JD能力矩阵 / B: Docker+Git | 问题池、能力矩阵、Docker环境 |
| 2 | 短期 | B/D | 存储/向量库/备份 + Python/FastAPI/LLM API | B: API调用 / C: 基建 | AI API可用、已分类问题池 |
| 3 | 短期 | B | Structured Output / Streaming / LLM应用v0 | B: LLM基础 | LLM应用v0 (P1前导) |
| 4 | 短期 | B | 明确 DA-01 + RAG Pipeline | B: RAG MVP | P1-RAG v0、DA-01 冻结 |
| 5 | 短期 | B | Chunk / Retrieval / Evaluation | B: RAG优化 | evaluation_dataset、badcases |
| 6 | 短期 | A/B | AI Full-Stack 应用 | B: React+FastAPI | P1前端+后端完整链路 |
| 7 | 短期 | C/B | Docker + Deployment | C: 生产部署 | P1 Cloud MVP上线 |
| 8 | 短期 | D | 项目包装 / P1 Portfolio | D: 作品集 | P1 Portfolio、8周总验收 |
| 9 | 中期 | B/D | Tool Calling + 方案打磨 | B: Tool / D: 求职验证 | Tool Demo |
| 10 | 中期 | B/D | Agent Workflow + 简历初版 | B: Agent / D: 简历 | P2-Agent v0、简历初版 |
| 11 | 中期 | B/D | Agent框架 (LangGraph) + 上架准备 | B: 框架 | Agent v1 |
| 12 | 中期 | B/D | Memory/State/MCP + Agent落地 | B: MCP | MCP Demo、Agent v2 |
| 13 | 中期 | B | MCP Tool Integration + 被动引流 | B: 集成 / A: SEO | MCP集成完成 |
| 14 | 中期 | B | Evaluation框架 + 首单变现 | B: Eval / A: 收入 | Eval Harness、首单 |
| 15 | 中期 | C/B | Production AI + 能力调优 | C: 日志/监控/成本 | Production就绪 |
| 16 | 中期 | D/B | P2 Portfolio + 简历迭代 | D: 作品集/简历 | P2 Portfolio、简历v1 |
| 17 | 长期 | A/B | 完整AI应用 / P3定义 | B: 问题定义 | P3定义完成 |
| 18 | 长期 | A/B | P3核心AI链路 | B: 开发 | P3 MVP |
| 19 | 长期 | B/C | P3工程化 | C: 生产化 | Production v1 |
| 20 | 长期 | B | P3 Evaluation | B: 自动评估 | P3 Eval完成 |
| 21 | 长期 | C | Security / Guardrail / 稳定运维 | C: 安全加固 | Security审计完成 |
| 22 | 长期 | B/D | Badcase / Regression + AI资产沉淀 | B: 质量 / D: 资产 | AI资产文档 |
| 23 | 长期 | D | Portfolio网站 | D: GitHub/Demo | 个人AI Portfolio上线 |
| 24 | 长期 | D | 简历最终版 | D: 简历 | AI简历完成 |
| 25 | 长期 | D/B | 面试准备 + System Design | D: 面试 | 系统设计能力 |
| 26 | 长期 | 全部 | 半年复盘 | 全部 | 半年报告、DA-02规划 |

---

## 5. 当前所在阶段 / 周

以 `PROJECT_CONFIG.md` 的「当前状态」为准（当前：阶段一 · 第 1 周）。

---

## 6. 如何使用这个目录

Agent 执行某一周任务时，**按最小必要上下文逐层加载**：

```
GLOBAL_CONTEXT.md      → 长期原则 / 防偏航 / 工作规则
PROJECT_CONFIG.md      → 路径 / 当前状态
plan/README.md         → 半年总路线
plan/phase_XX/README.md → 阶段目标与进出条件
plan/phase_XX/week_XX/README.md → 本周为什么做 / 产出 / 验收
plan/phase_XX/week_XX/TASKS.md   → 具体执行任务
```

不要一次性读取全部 26 周。

---

## 7. 阶段之间的产出关系

```
阶段 1 产出（研发底座 + 已验证的 DA-01 候选 + MVP + AI/RAG 基础 + 模板）
        ↓ 成为
阶段 2 输入（把 MVP 打磨成可交付、可上架、可首单变现的产品 + Agent 服务）
        ↓ 成为
阶段 3 输入（放大收入、沉淀 AI 资产、复盘并规划 DA-02）
        ↓
最终形成 DA-01 可持续数字资产 + 可复制的生产方法
```

---

## 8. 计划演化机制

计划变化记录在 `plan/CHANGELOG.md`：为什么改、改了什么、哪一周受影响、DA-01 是否变化。
