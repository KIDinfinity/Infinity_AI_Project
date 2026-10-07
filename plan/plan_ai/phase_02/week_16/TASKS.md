# Week 16 · TASKS

## Task 1：P2 README / 架构 / 评测报告（v1.0）（Day55 · 01-11）

### 做什么

README 新增 P2 章节（Agent、MCP、Eval、Observability）+ 架构图 v1 + LangGraph 图 + RAG/Agent 评测表 + 截图；写 `docs/portfolio/p2.md`（问题、为什么用 Agent、架构、工具设计、HITL、评测方法与数字、badcases、优化、成本/延迟、部署）；部署 v1.0 到云端（MCP HTTP 不公开或 token 保护）；tag `v1.0.0` + Release notes。

### 为什么做

P2 作品集是求职线本阶段最重要的证据；v1.0 是 phase_03 的稳定基线。

### 资产锚点

M13.2 · **v1.0（P2 发布）**

### 前置依赖

W14 评测报告与基线、W15 Trace/Ops 截图、W13 MCP 文档；云服务器与 W7 部署流程可用。

### 具体执行步骤（概要，详见 day55_20261121/PLAN.md）

1. 收集数字（报告文件）与截图。
2. 导出 LangGraph mermaid 图，更新 `docs/architecture.md`。
3. README P2 章节。
4. `docs/portfolio/p2.md`。
5. 云端部署 v1.0 + 冒烟。
6. CHANGELOG + tag + Release notes。

### 验收标准

- [ ] README P2 章节完整，数字可追溯
- [ ] 云端 `/health` 显示 1.0.0；MCP HTTP 未公开暴露
- [ ] tag `v1.0.0` + GitHub Release 可见

### 完成后的产出（文件路径）

`README.md`、`docs/architecture.md`、`docs/portfolio/p2.md`、`docs/assets/*.png`、`CHANGELOG.md`

### 求职映射

项目叙事、架构表达、评测数据呈现 → 所有 AI 工程岗位。

### 如果时间不够 / 没有必要

P0 = README P2 章节 + 评测表 + tag；`p2.md` 先写大纲 + 数字；云端部署可顺延到 Day56 开头。

---

## Task 2：Demo + 技术文章 + 产品页 / 开源边界（Day56 · 01-12）

### 做什么

录 2–3 分钟 Demo 视频（研究任务 + 审批、IDE 中 MCP、Trace 页）；写 2000–3000 字技术文章（如《从 RAG 到可审批的研发 Agent：WorkPilot 的评测驱动实践》），发布到个人博客 / 掘金（只发布，不私聊拓客），链接 GitHub；`docs/product/open-core.md` 定稿（免费 vs Pro Kit）；产品页（README 顶部或 GitHub Pages：功能、截图、Pro Kit 即将推出，通过 GitHub Star / Discussions 被动收集兴趣）；发布前 gitleaks 再扫一次。

### 为什么做

视频与文章让作品集「可被快速理解」，同时是 SEO 与被动流量入口；开源边界决定 W22 Pro Kit 能卖什么。

### 资产锚点

M12.1 M12.3 · v1.0

### 前置依赖

Task 1 完成（README、截图、数字）；云端 v1.0 可访问；W13 MCP 录屏素材。

### 具体执行步骤（概要，详见 day56_20261122/PLAN.md）

1. Demo 脚本 + 录制 + 上传。
2. 文章大纲 → AI 起草 → 自己改写关键段落与数字 → 发布。
3. `open-core.md` 定稿。
4. README 顶部产品区块 / GitHub Pages + 开启 Discussions。
5. gitleaks + 合规检查 + 提交。

### 验收标准

- [ ] 视频 2–3 分钟，三个场景齐全
- [ ] 文章发布链接可访问，字数 2000–3000
- [ ] `open-core.md` 有功能边界表与定价区间
- [ ] 产品页可访问；gitleaks 0 告警

### 完成后的产出（文件路径）

`docs/product/open-core.md`、`README.md`（顶部产品区块）、`docs/site/index.html`（可选）、文章链接、视频链接

### 求职映射

技术写作、产品化表达、开源运营 → AI Full-Stack / Developer Advocate 加分项。

### 如果时间不够 / 没有必要

P0 = 视频 + open-core + gitleaks；文章可先发 1500 字精简版；GitHub Pages 可不做（README 顶部即产品页）。

---

## Task 3：简历 v1 + 面试题 + Phase 2 复盘（Day57 · 01-13）

### 做什么

简历 v1（ai-fullstack、ai-engineer 两版）用报告数字写 P1+P2 量化 bullets；`interview-questions.md` 新增 15 道（Agent / Tool / MCP / Eval / Observability）→ 总数 ≥ 25；逐项勾选 phase_02 README 第 8 节；写 `projects/product-lab/reviews/phase02-review.md`；`PROJECT_CONFIG.md` 更新为阶段三 · 第 17 周。

### 为什么做

把 8 周的工程成果转换成求职资产；阶段验收决定 phase_03 是否可以开始，避免带着 P0 缺口进入新阶段。

### 资产锚点

M13.3 M13.4 · Phase 2 收尾

### 前置依赖

Task 1 的数字与文档；W10 简历 v0；已有面试题（RAG 约 10 道 + W13 MCP 5 道）。

### 具体执行步骤（概要，详见 day57_20261123/PLAN.md）

1. 数字清单 → 两版简历 v1。
2. 新增 15 道面试题。
3. phase_02 第 8 节逐项勾选（附证据路径）。
4. phase02-review.md。
5. PROJECT_CONFIG + 周复盘 + 提交。

### 验收标准

- [ ] 两版简历 v1，每版 P1/P2 各 ≥ 3 条量化 bullet
- [ ] 面试题总数 ≥ 25
- [ ] 第 8 节 8 项全部有 PASS/FAIL 与证据
- [ ] review 文档与 PROJECT_CONFIG 已更新

### 完成后的产出（文件路径）

`~/lab/projects/career/resume/ai-fullstack-v1.md`、`ai-engineer-v1.md`、`~/lab/projects/career/interview-questions.md`、`~/lab/projects/product-lab/reviews/phase02-review.md`、`PROJECT_CONFIG.md`

### 求职映射

简历量化、面试准备、复盘能力 → 所有目标岗位。

### 如果时间不够 / 没有必要

P0 = ai-engineer 简历 v1 + 面试题 ≥ 25 + 第 8 节勾选 + PROJECT_CONFIG；ai-fullstack 版与完整复盘顺延到 Day58 开头 30 分钟。

---
