# Week 08 · P1 作品集 + 8 周总验收（Phase 1 · Day30–Day33 · 10-27 → 10-30）

## 1. 本周核心目标

把 W2–W7 做出的东西**包装成招聘方 5 分钟能看懂、30 分钟能复现的 P1 作品集**，公开到 GitHub，完成 phase_01 的 8 周总验收，发布 **v0.5.0 = P1 WorkPilot Knowledge**。

一句话验收：**陌生人打开 GitHub 仓库 → README 里看到 Demo GIF、架构图、评测数字 → 按 3 条命令在干净目录 30 分钟内跑起来；你能脱稿 3 分钟讲清 P1。**

## 2. 资产锚点

| 构建模块                        | 版本里程碑       | 本周结束 WorkPilot 能演示什么                                                           |
| ------------------------------- | ---------------- | --------------------------------------------------------------------------------------- |
| M13.2 项目写作：P1 技术复盘     | v0.5             | README（招聘方视角）+ `docs/architecture.md` + ADR ×5 + `docs/portfolio/p1.md`（8 问）  |
| M13.2 Demo                      | v0.5             | 90 秒 Demo GIF（上传 → 引用问答 → 拒答 → 反馈 → 评测报告）                              |
| M12.1 开源核心                  | v0.5             | GitHub 公共仓库（MIT），通过 gitleaks 与人工敏感信息检查                                |
| M13.3 / M13.4 简历条目 + 面试题 | —                | `career/resume/ai-fullstack-draft.md` P1 bullets、`career/interview-questions.md` 10 题 |
| v0.5 总验收                     | **v0.5 P1 发布** | 干净环境恢复计时、phase_01 §8 逐项 PASS/FAIL、Release notes、阶段复盘                   |

## 3. 为什么这一周存在

- **没有被看见的作品等于不存在**：招聘方平均只花几分钟看一个仓库；README 首屏 + Demo GIF + 评测数字决定是否继续看。
- 总计划 §4.8 要求 P1 包含 README / Architecture / Demo / Evaluation / Badcases / Docker / Deployment / Technical-Writeup，并回答 8 问——这是面试 RAG 项目的标准追问清单。
- 公开前的敏感信息检查是 DA01 §8 的硬性要求（W8 / W16 / W23 各一次）。
- 阶段验收决定能否进入 phase_02（Agent）：地基不稳，后面 Tool / Agent / MCP 都会返工。

## 4. 本周在路线中的位置

```text
W7 产出：make up 一键起、公网 HTTPS Demo、CI 绿、备份恢复 RTO 记录、runbook
   ↓
W8 本周：README + 架构图 + ADR → Demo GIF + p1.md 8 问 + 3 分钟讲稿
         → gitleaks + GitHub 公开 + 简历条目 + 面试 10 题 → 干净环境恢复 + 总验收 → v0.5.0
   ↓
W9 输入：v0.5.0（app/llm、app/rag、eval/、apps/web、deploy/ 全部可复用）
         + 阶段复盘中的 CONDITIONAL 项清单 → Tool Calling（M6）
```

## 5. 每日安排

| Day | 日期  | Task                                        | 当日 P0 产出                                                        | 模块              | 状态 |
| --- | ----- | ------------------------------------------- | ------------------------------------------------------------------- | ----------------- | ---- |
| 30  | 10-27 | Task 1：README + 架构图 + ADR               | `README.md`、`docs/architecture.md`、ADR 0001/0002/0004/0005        | M13.2             | TODO |
| 31  | 10-28 | Task 2：Demo 录制 + 技术复盘 8 问           | `docs/assets/demo.gif`（<10MB）、`docs/portfolio/p1.md`、3 分钟讲稿 | M13.2             | TODO |
| 32  | 10-29 | Task 3：GitHub 公开 + 简历条目 + 面试 10 题 | gitleaks 通过、GitHub 公共仓库、简历 bullets、10 题                 | M12.1 M13.3 M13.4 | TODO |
| 33  | 10-30 | Task 4：8 周总验收 + 干净环境恢复           | 恢复计时 < 30 分钟、验收表、tag `v0.5.0`、阶段复盘                  | v0.5              | TODO |

## 6. 本周必须留下的资产（文件路径级）

```text
~/lab/workpilot/
├── README.md                         # 招聘方视角首页
├── LICENSE                           # MIT
├── docs/
│   ├── architecture.md               # 组件图 + 问答 sequenceDiagram + 数据模型
│   ├── adr/0001-llm-provider-and-gateway.md
│   ├── adr/0002-vector-db-qdrant.md
│   ├── adr/0003-*.md                 # W5 已有
│   ├── adr/0004-rag-without-langchain.md
│   ├── adr/0005-compose-caddy-deployment.md
│   ├── runbook.md                    # 补全
│   ├── assets/demo.gif
│   ├── portfolio/p1.md               # 8 问 + 3 分钟讲稿
│   └── releases/v0.5.0.md
~/lab/projects/
├── career/resume/ai-fullstack-draft.md
├── career/interview-questions.md
├── career/capability-matrix.md       # 证据列更新
└── product-lab/reviews/phase01-review.md
Infinity_AI_Project/PROJECT_CONFIG.md # 当前状态 → 阶段二 · 第 9 周
```

## 7. 本周验收标准

- [ ] PASS / FAIL：README 首屏（不滚动）能看到一句话定位 + Demo GIF + 快速开始入口
- [ ] PASS / FAIL：README 中的评测数字与 `eval/reports/` 中报告一致（可追溯）
- [ ] PASS / FAIL：ADR 0001–0005 齐全，每篇含「背景 / 决策 / 备选 / 后果」
- [ ] PASS / FAIL：Demo GIF < 10MB，覆盖上传 / 引用 / 拒答 / 反馈 / 评测 5 个镜头
- [ ] PASS / FAIL：`docs/portfolio/p1.md` 8 问每问都有真实数字或文件证据
- [ ] PASS / FAIL：gitleaks 扫描（含全部历史）0 发现；公司名 / 人名 / 内网地址 grep 0 命中
- [ ] PASS / FAIL：GitHub 公共仓库可访问，含 main + 全部 tag，LICENSE 为 MIT
- [ ] PASS / FAIL：简历 P1 bullets ≥ 3 条且带数字；面试题 10 道且每题链接到 WorkPilot 证据
- [ ] PASS / FAIL：干净目录从 GitHub clone → 问答通过，计时 < 30 分钟
- [ ] PASS / FAIL：phase_01 README §8 逐项给出 PASS / FAIL / CONDITIONAL；tag `v0.5.0` + Release notes
- [ ] PASS / FAIL：录制一次 3 分钟 P1 讲解（录音即可）

## 8. 求职映射

- **本周能力**：技术写作、架构表达、决策记录（ADR）、开源发布与安全检查、项目叙事（问题 → 架构 → 评测 → 结果）。
- **简历 bullet 草稿**（汇总版，Day32 定稿）：
  - 独立设计并交付 RAG 研发知识助手 WorkPilot（FastAPI + React + Qdrant + bge-m3 + DeepSeek），50 题评测集 hit@5 **、引用正确率 **、库外拒答率 **，P95 延迟 **s、单次成本 ¥\_\_。
  - 建立评测与 Badcase 闭环（检索指标 + LLM-as-judge + 在线反馈导出），经 chunk / hybrid / rewrite 实验将 hit@5 从 ** 提升到 **。
  - 实现生产化交付：Docker 多阶段 + Compose + Caddy HTTPS 云部署、request_id 结构化日志、CI、备份恢复（RTO \_\_ 分钟），开源于 GitHub。
- **面试题**：
  1. 用 3 分钟介绍你的 RAG 项目。（问题 → 架构 → 关键设计 → 评测数字 → 踩坑 → 下一步）
  2. 你为什么不用 LangChain？（ADR 0004：可控、可调试、可评测；理解原理后 W11 才在 Agent 层引入 LangGraph）
  3. 你的评测集怎么构造的？怎么防止评测集过拟合？（分层采样、库外题、badcase 回流、留出集）

## 9. 本周禁止事项

- 不加新功能（只修影响 Demo / 验收的 bug，且必须记录）。
- 不做 Portfolio 网站（W23）、不写长篇技术博客（W16）、不做产品页（W16）。
- 不美化 README 到「花哨」：不加大量徽章、动图、表情。
- 不在未通过敏感信息检查前推送到 GitHub；不在公开仓库出现任何公司信息、真实同事姓名、内网地址、本机用户名路径。
- 不开始投递简历（W24）。

## 10. 时间不够时（最小保留）

1. Day32 敏感信息检查 + GitHub 公开（作品集的「可见性」）
2. Day30 README（含架构 mermaid、快速开始、评测表）
3. Day33 干净环境恢复 + 验收表 + tag `v0.5.0`
4. Demo GIF 可降级为 3 张截图；ADR 可先写 0002 / 0004 两篇，其余 W9 补；面试题可先 5 道

## 11. 周复盘（Day33 末尾填写，同时作为 phase_01 复盘的输入）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（GitHub 链接、Demo GIF、v0.5.0 Release）
- 是否出现无效学习或范围扩张（例如反复重录 Demo、调 README 样式）：\_\_\_\_
- 下周调整（进入 W9 Tool Calling 前要补的 CONDITIONAL 项）：\_\_\_\_
