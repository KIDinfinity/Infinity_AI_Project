# Week 08 · TASKS

## Task 1：README + 架构图 + ADR（Day30 · 11-16）

### 做什么

写面向招聘方的 `README.md`（标题 + 一句话 + Demo GIF 占位 + 功能 + 架构 mermaid + 技术栈 + 3 条命令快速开始 + 评测结果表 + 设计决策链接 + 路线图 P2/P3 + License）；`docs/architecture.md`（组件图 + 问答链路 sequenceDiagram + 数据模型 erDiagram）；ADR 0001 LLM 供应商与网关、0002 选 Qdrant、0004 RAG v1 不用 LangChain、0005 Compose + Caddy 部署（0003 已有）；补全 `docs/runbook.md`。

### 为什么做

README 是作品集的首页，ADR 是「你会做技术决策」的证据，面试官最爱问「为什么这样选」。

### 资产锚点

M13.2 · 为 v0.5 做准备

### 前置依赖

W5 评测报告；W7 部署 / 备份已完成；`.env.example` 完整。

### 具体执行步骤（概要，详见 day30 PLAN.md）

1. 收集事实：评测数字、技术栈版本、命令。
2. README 骨架 → 填内容。
3. architecture.md 三张 mermaid 图。
4. ADR 模板 + 4 篇。
5. runbook 补全；提交。

### 验收标准

- [ ] README 中每个评测数字可追溯到 `eval/reports/` 文件
- [ ] 3 条命令快速开始在本机能直接执行
- [ ] mermaid 在 Gitea / VS Code 预览中正常渲染
- [ ] ADR 0001–0005 齐全

### 完成后的产出（文件路径）

`README.md`、`docs/architecture.md`、`docs/adr/0001-*.md`、`0002-*.md`、`0004-*.md`、`0005-*.md`、`docs/runbook.md`

### 求职映射

「技术写作、架构表达、技术决策记录」。

### 如果时间不够 / 没有必要

ADR 0001 / 0005 可只写「决策 + 两条理由」；erDiagram → P1。

---

## Task 2：Demo 录制 + 技术复盘 8 问（Day31 · 11-17）

### 做什么

写 90 秒 Demo 脚本（上传文档 → 库内提问看引用 → 库外提问看拒答 → 反馈 → 展示评测报告），用 Kap 或 QuickTime 录制，导出 GIF（<10MB）存 `docs/assets/`；`docs/portfolio/p1.md` 用报告中的真实数字回答总计划 §4.8 的 8 问；写 3 分钟讲稿。

### 为什么做

Demo 让招聘方 90 秒内相信「它真的能用」；8 问是 RAG 面试的高频追问清单，提前写成文字等于提前准备面试。

### 资产锚点

M13.2 · 为 v0.5 做准备

### 前置依赖

Task 1 完成；本地 `make up` 或云端可用；`data/sample` 已导入。

### 具体执行步骤（概要，详见 day31 PLAN.md）

1. 准备 Demo 数据与问题，清空无关历史。
2. 按脚本彩排 1 次 → 录制 → 导出 GIF / 压缩。
3. p1.md 8 问（每问：结论 + 数字 + 证据链接）。
4. 3 分钟讲稿 + 计时朗读 1 次；提交。

### 验收标准

- [ ] GIF < 10MB，5 个镜头齐全，README 中已替换占位
- [ ] p1.md 8 问全部有数字或文件证据
- [ ] 讲稿朗读时长 2:30–3:15

### 完成后的产出（文件路径）

`docs/assets/demo.gif`、`docs/portfolio/p1.md`

### 求职映射

「项目叙事 + 量化结果」直接用于面试自我介绍和项目深挖。

### 如果时间不够 / 没有必要

GIF 降级为 3 张截图；讲稿只写要点提纲。

---

## Task 3：GitHub 公开 + 简历条目 + 面试 10 题（Day32 · 11-18）

### 做什么

发布前检查：`brew install gitleaks`；gitleaks 扫描含全部历史；grep 公司名 / 人名 / 内网地址 / 本机路径；确认 `.env`、`data/corpus` 从未进入历史（若进入，说明需 `git filter-repo` 处理——破坏性操作，必须先停下确认）。GitHub 新建公共仓库 `workpilot`，推送 main + tags（或配置 Gitea 推送镜像）；LICENSE MIT。`career/resume/ai-fullstack-draft.md` 写 P1 bullets；`career/interview-questions.md` 写 10 道 RAG 题（答案链接到 WorkPilot 证据）；更新能力矩阵证据列。

### 为什么做

公开仓库是作品集的载体；敏感信息检查是合规红线；简历条目和题库把项目转化为求职材料。

### 资产锚点

M12.1 M13.3 M13.4 · 为 v0.5 做准备

### 前置依赖

Task 1–2 完成；GitHub 账号（建议开启 2FA）。

### 具体执行步骤（概要，详见 day32 PLAN.md）

1. gitleaks + grep + 历史文件检查 + 提交作者邮箱检查。
2. 若有问题：停止，记录，按 PLAN 中的决策树处理。
3. LICENSE；GitHub 建仓；推送 main + tags。
4. 简历 bullets；面试 10 题；能力矩阵；提交 projects 仓库。

### 验收标准

- [ ] `gitleaks git .` 0 leaks（或误报已加入 `.gitleaksignore` 并说明）
- [ ] GitHub 仓库公开，README / GIF 正常显示，tags 齐全
- [ ] 简历 bullets ≥ 3 条带数字；10 题每题有证据链接
- [ ] 能力矩阵 ≥ 12 项标出证据模块

### 完成后的产出（文件路径）

`LICENSE`、GitHub `workpilot` 公共仓库、`~/lab/projects/career/resume/ai-fullstack-draft.md`、`career/interview-questions.md`、`career/capability-matrix.md`

### 求职映射

GitHub 链接写进简历；10 题即面试题库 M13.4 的第一批。

### 如果时间不够 / 没有必要

Gitea 推送镜像 → P2（手动 push 即可）；面试题先 5 道，W9 补齐。

---

## Task 4：8 周总验收 + 干净环境恢复（v0.5）（Day33 · 11-19）

### 做什么

干净环境演练：`~/tmp/wp-clean` 从 GitHub clone → 填 `.env` → `make up` → 导入 sample → 问答通过，全程计时（目标 < 30 分钟）。逐项勾选 phase_01 README §8（PASS / FAIL / CONDITIONAL）；tag `v0.5.0` + Release notes；写 `projects/product-lab/reviews/phase01-review.md`；`PROJECT_CONFIG.md` 更新为「阶段二 · 第 9 周」；录一次 3 分钟讲解。

### 为什么做

「文档写的能跑」和「真的能跑」之间总有差距，只有干净环境演练能暴露；阶段验收决定是否进入 phase_02。

### 资产锚点

**v0.5（P1 发布）**

### 前置依赖

Task 1–3 完成；GitHub 仓库公开。

### 具体执行步骤（概要，详见 day33 PLAN.md）

1. 干净环境演练 + 计时 + 记录 README 中的坑并修复。
2. §8 逐项验收表。
3. Release notes + tag `v0.5.0`（Gitea + GitHub）。
4. 阶段复盘 + PROJECT_CONFIG 更新 + 3 分钟录音。

### 验收标准

- [ ] 干净环境计时 < 30 分钟（记录实际分钟数）
- [ ] §8 8 项全部有结论与证据链接；核心项全 PASS
- [ ] `v0.5.0` tag 在 Gitea 与 GitHub 均可见，Release notes 已发布
- [ ] phase01-review.md 已写；PROJECT_CONFIG 当前状态已更新

### 完成后的产出（文件路径）

`docs/releases/v0.5.0.md`、`~/lab/projects/product-lab/reviews/phase01-review.md`、`PROJECT_CONFIG.md`（更新）、3 分钟讲解录音（本地，不入库）

### 求职映射

「从零到上线的完整交付 + 可复现性」——面试中可直接说「clone 后 30 分钟内能跑起来，我实测过」。

### 如果时间不够 / 没有必要

GitHub Release 页面 → 只保留 `docs/releases/v0.5.0.md`；讲解录音 → W9 Day34 补。

---
