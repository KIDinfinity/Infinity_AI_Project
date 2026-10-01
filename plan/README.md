# plan — 半年智能解决方案孵化执行目录

> 本目录是 DA-01 的**唯一执行工作空间**。历史/总计划在 `history/`，本目录只放当前可执行、可验收、可持续迭代的计划。
> **最终要交付什么**：见 [DA01_TARGET_ASSET.md](DA01_TARGET_ASSET.md)（目标数字资产蓝图，所有计划的锚点）。

---

## 1. 半年最终目标

> **半年内交付 DA-01 = WorkPilot（工作代号）：一个可私有部署、经过评测、可运行可交付可迭代的「研发工作 AI 助手平台」；它同时是 P1/P2/P3 三份求职作品集、个人日常效率工具、可售卖的标准化资产，以及可复用工程模板的来源。**

最终结果 = 1 个真实智能解决方案资产 + 1 套「问题 → 解决方案 → 资产」生产方法 + 1 套可求职的 AI 工程作品集（简历 / Portfolio / 面试材料）。

## 1.1 通用解决方案闭环（最高方法论）

```text
现实问题 → 感知/数据 → AI 理解 → 决策/规划 → 工具执行 → 反馈 → Evaluation → Badcase → 优化
```

在 WorkPilot 中：研发痛点（M10）→ 文档/仓库导入（M2.1）→ LLM + 检索（M1/M2）→ Agent 规划（M7）→ 工具（M6）→ 反馈/审批（F2/F3）→ 评测（M3）。

---

## 2. DA-01 与三个里程碑

| 里程碑                  | 版本 | 周     | 内容                                                                        | 求职对应                                 |
| ----------------------- | ---- | ------ | --------------------------------------------------------------------------- | ---------------------------------------- |
| P1 WorkPilot Knowledge  | v0.5 | W2–8   | LLM Gateway + RAG + 评测 + Web Console + 云部署                             | AI Engineer / GenAI Application Engineer |
| P2 WorkPilot Agent      | v1.0 | W9–16  | Tools + Agent(LangGraph) + Memory + HITL + MCP + Agent Eval + Observability | AI Agent Engineer / LLM Engineer         |
| P3 WorkPilot Production | v2.0 | W17–23 | 场景包 + 多空间/认证 + 安全护栏 + 回归体系 + 在线 Demo + Pro Kit            | AI Full-Stack / AI Platform Engineer     |

- 能力骨架（M0–M9、M11）固定；**具体解决哪个痛点（M10 场景包）第 3 周 Day13 从真实问题池选出**。
- 决策顺序仍是：问题 → 用户 → 场景 → 价值 → 验证 → 形态 → 技术组合 → 技术栈。
- 数据合规红线见 [DA01_TARGET_ASSET.md §8](DA01_TARGET_ASSET.md)：公司机密不进外部 LLM。

## 2.1 四条能力线

| 能力线                       | 目标                                   | 在 WorkPilot 中                    |
| ---------------------------- | -------------------------------------- | ---------------------------------- |
| A 线：AI 产品 / 变现         | 真实问题 + 标准化交付                  | M10 场景包、M12 开源核心 + Pro Kit |
| B 线：AI Engineering         | RAG + Agent + Eval + Production AI     | M1 M2 M3 M6 M7 M8                  |
| C 线：Infrastructure         | Docker + Cloud + CI/CD + Observability | M0 M5 M9 M11                       |
| D 线：Job Market / Portfolio | 简历 / GitHub / Demo / 面试            | M13                                |

优先级：W1–8 **B > A > C > D**；W9–16 **B > D > A > C**；W17–26 **D ≈ B > A > C**。

---

## 3. 三阶段关系

| 阶段                  | 周 / Day          | WorkPilot 版本推进                  | 核心问题                                                    |
| --------------------- | ----------------- | ----------------------------------- | ----------------------------------------------------------- |
| phase_01 探索与 P1    | W1–8 / Day01–33   | 无 → v0.5（P1 发布）                | 解决哪个真实痛点？RAG 知识助手能否上线并被评测？            |
| phase_02 Agent 与 P2  | W9–16 / Day34–57  | v0.5 → v1.0（P2 发布）              | Agent 能否可靠调用工具、可审批、可评测、可观测？            |
| phase_03 生产化与求职 | W17–26 / Day58–77 | v1.0 → v2.0（P3 发布）→ 求职 / 复盘 | 能否成为安全的生产级方案？能否转化为 offer 证据和收入验证？ |

---

## 4. 26 周路线（周 = 2–5 天冲刺，每天 1–2 小时）

| 周  | Day   | 主线  | 核心目标                                     | 资产锚点                  | 版本        |
| --- | ----- | ----- | -------------------------------------------- | ------------------------- | ----------- |
| 1   | 01–05 | C/A   | 研发底座 + 痛点池 + 项目规范/模板            | M0.1–M0.3 M10             | v0.0        |
| 2   | 06–10 | D/B/C | 能力矩阵 + FastAPI + LLM Gateway + 存储/备份 | M13.1 M1.1 M1.2 M0.4 M0.5 | —           |
| 3   | 11–14 | B/A   | 结构化输出 / 流式 / 成本 + DA-01 场景选型    | M1.3–M1.6 M10             | v0.1        |
| 4   | 15–18 | B     | RAG Pipeline                                 | M2 M3.1                   | v0.2        |
| 5   | 19–21 | B     | RAG 评测与优化                               | M2.2 M2.4 M3.2 M3.4       | v0.3        |
| 6   | 22–25 | B/A   | AI Full-Stack Web Console                    | M4.1 M4.2 M3.6            | v0.4        |
| 7   | 26–29 | C     | Docker / 云部署 / CI / 备份                  | M5 M9.1                   | —           |
| 8   | 30–33 | D     | P1 作品集 + 8 周验收                         | M13.2 M12.1               | **v0.5 P1** |
| 9   | 34–36 | B     | Tool Calling                                 | M6                        | v0.6        |
| 10  | 37–39 | B/D   | 手写 Agent + Research Agent + 简历 v0        | M7.1 M7.5 M4.3 M13.3      | v0.7        |
| 11  | 40–42 | B     | LangGraph                                    | M7.2                      | —           |
| 12  | 43–45 | B     | Memory / HITL                                | M7.3 M7.4                 | v0.8        |
| 13  | 46–48 | B     | MCP                                          | M8                        | v0.9        |
| 14  | 49–51 | B     | Agent Evaluation + 回归                      | M3.3 M3.5                 | —           |
| 15  | 52–54 | C/B   | Production AI（Trace/成本/限流/护栏）        | M9 M11.3 M4.4             | —           |
| 16  | 55–57 | D     | P2 作品集 + 开源/产品页 + 简历 v1            | M13 M12                   | **v1.0 P2** |
| 17  | 58–59 | A/B   | P3 问题定义 + 架构 v2                        | M10 M11                   | —           |
| 18  | 60–61 | A/B   | 主场景包 MVP                                 | M10                       | v1.1        |
| 19  | 62–63 | C/B   | Postgres + 认证 + 多空间 + 自动部署          | M11.1 M11.2 M5.4          | v1.2        |
| 20  | 64–65 | B     | 场景评测 + 反馈闭环                          | M3 M4.4                   | v1.3        |
| 21  | 66–67 | C     | 安全加固（OWASP LLM Top 10）                 | M11                       | v1.4        |
| 22  | 68–69 | B/A   | Eval v2 + 模板库 + Pro Kit                   | M3.5 M14 M12.2            | **v2.0 P3** |
| 23  | 70–71 | D     | Portfolio 网站 + 在线 Demo                   | M13.5 M12.4               | —           |
| 24  | 72–73 | D     | 简历 ×3 + 小批量投递                         | M13.3                     | —           |
| 25  | 74–75 | D/B   | 面试题库 + System Design                     | M13.4                     | —           |
| 26  | 76–77 | 全部  | 半年验收 + DA-02 规划                        | 全部                      | —           |

逐日明细：[DA01_TARGET_ASSET.md 附录 A](DA01_TARGET_ASSET.md)。

---

## 5. 当前所在阶段 / 周

以 `PROJECT_CONFIG.md` 的「当前状态」为准。Day01（Docker）、Day02（Gitea）已完成。

---

## 6. 如何使用这个目录

Agent 执行任务时**按最小必要上下文逐层加载**：

```text
GLOBAL_CONTEXT.md                → 长期原则 / 防偏航
PROJECT_CONFIG.md                → 路径 / 当前状态
plan/DA01_TARGET_ASSET.md        → 最终产品长什么样（模块编号 = 资产锚点）
plan/README.md                   → 半年总路线
plan/phase_XX/README.md          → 阶段目标、版本推进、进出条件
plan/phase_XX/week_XX/README.md  → 本周模块、每日安排、验收
plan/phase_XX/week_XX/TASKS.md   → 本周任务细节
plan/phase_XX/week_XX/dayNN_*/PLAN.md → 当天可直接执行的步骤
```

不要一次性读取全部 26 周。

### 每日文件约定

- `PLAN.md`：当天计划（计划生成后不随意改动）。
- `draft.md`：执行时自己的笔记 / 勾选结果（Day01、Day02 已采用）。
- 当天未完成：次日 PLAN 不改，只在 `draft.md` 记录「顺延项」，并优先完成 P0。

---

## 7. 阶段之间的产出关系

```text
phase_01：底座 + 痛点池 + DA-01 场景 + WorkPilot v0.5（P1：RAG 知识助手，已部署、已评测）
   ↓ 作为输入
phase_02：在同一仓库上加 Tools / Agent / MCP / Eval / Observability → v1.0（P2）
   ↓ 作为输入
phase_03：场景包 + 安全 + 多空间 + 回归 → v2.0（P3）→ 模板库 / Portfolio / 简历 / 面试 / DA-02
```

## 8. 计划演化机制

计划变化记录在 `plan/CHANGELOG.md`：为什么改、改了什么、哪一周受影响、DA-01 / 目标资产是否变化。
