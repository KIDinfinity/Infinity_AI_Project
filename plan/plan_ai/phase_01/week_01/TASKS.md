# Week 01 · TASKS

> 顺序按编号排列；Task 0（痛点池）贯穿本周，集中在 Day03 落地。
> 详细命令见各 `dayNN_xxx/PLAN.md`。

---

## Task 1：Docker 环境（Day01 · 09-28）✅ 已完成

### 做什么

安装 Docker Desktop（`brew install --cask docker`），跑通 `hello-world`、nginx，练熟 `run / ps / logs / stop / rm`，完成 volume 挂载练习。

### 为什么做

WorkPilot 的 Gitea、MinIO、Qdrant 以及 W7 的全栈部署都跑在 Docker 上；「容器可删、数据不丢」是后续备份恢复的前提。

### 资产锚点

M0.1 Docker 运行时。

### 前置依赖

无。

### 具体执行步骤

见 `day01_20260928/PLAN.md`。实际情况（`draft.md`）：未配置 daemon 代理也能拉镜像；Docker Desktop 卡死时可 kill 进程重启。

### 验收标准

- [x] 5 条命令独立完成
- [x] 能解释 image / container / volume

### 完成后的产出

Docker Desktop 可用；`~/docker-lab/site`（volume 练习目录）。

### 求职映射

Docker 基础 → AI Engineer / AI Full-Stack JD 中的「Docker / 容器化」。

### 如果时间不够 / 没有必要

已完成，无需再投入。

---

## Task 2：Gitea + 三目录（Day02 · 09-29）✅ 已完成

### 做什么

用 Docker 运行 Gitea（`:3000`，SSH `:2222`，数据 `~/gitea/data`），建 `test-repo` 跑通 clone / commit / push，建 `projects` 仓库并推送 `product-lab / ai-lab / infra` 三目录。

### 为什么做

所有资产（代码、规范、痛点池、脚本）必须有唯一归口，可版本化、可备份。

### 资产锚点

M0.2 Gitea 代码托管。

### 前置依赖

Task 1。

### 具体执行步骤

见 `day02_20260929/PLAN.md`。**教训**：仓库必须先在 Gitea Web UI 创建，再 `git clone` 到本地；本地 `git init` 或直接往挂载目录放仓库，Gitea 识别不到。

### 验收标准

- [x] Web UI 可登录、可建仓
- [x] clone / commit / push 跑通
- [x] 三目录已推送

### 完成后的产出

`http://localhost:3000`；`~/lab/test-repo`；`~/lab/projects/{product-lab,ai-lab,infra}/README.md`。

### 求职映射

Git 工作流、自托管服务运维。

### 如果时间不够 / 没有必要

已完成。

---

## Task 0：研发工作痛点池 v0（Day03 · 09-30）

### 做什么

在 `~/lab/projects/product-lab/pain-pool.md` 用 11 列统一表格记录 ≥ 8 条过去两周**亲历**的研发工作痛点，并标注问题类型、合规风险、候选场景包（SP-A..SP-F / 新）。

### 为什么做

蓝图 §1.3：能力骨架固定，但场景包 M10 由真实痛点决定。没有事实输入，Day13 的选型只能拍脑袋。

### 资产锚点

M10 Scenario Packs（候选输入）；为 W3 Day13 场景选型准备。

### 前置依赖

Task 2（`projects` 仓库）。可能存在的旧草稿（Day01/02「今日额外」随手记的痛点）。

### 具体执行步骤

1. 建 `pain-pool.md`，写表头与列定义。
2. 迁移旧草稿条目。
3. 按 8 类回忆提示（查规范、理解需求、拆任务、评审、排障、写周报、重复问答、AI 工具不好用）逐类回忆。
4. 补全频率 / 耗时 / 类型 / 合规 / 场景包。
5. 脱敏自查（grep 公司关键词）→ push。

### 验收标准

- [ ] ≥ 8 条，11 列齐全，全部亲历或亲眼观察
- [ ] 脱敏 grep 无输出
- [ ] 已 push

### 完成后的产出

`~/lab/projects/product-lab/pain-pool.md`

### 求职映射

AI 产品思维：「从真实痛点出发定义 AI 场景」，面试可讲「为什么做这个项目」。

### 如果时间不够 / 没有必要

压缩为 40 分钟：只写 ≥ 8 条、6 列（ID / 场景 / 痛点 / 频率 / 耗时 / 类型）；其余列 Day10 补。**不可跳过**：Day13 依赖它。

---

## Task 3：项目规范 PROJECT_STANDARD（Day04 · 10-01）

### 做什么

在 Gitea 新建 `ai-project-template`（Private、不初始化），clone 到 `~/lab/ai-project-template`；写 `PROJECT_STANDARD.md`（目录 / 命名 / 分支与提交 / 环境变量 / 版本与 tag / Makefile 约定 / README 必含章节 / ADR 模板 / 数据合规）；按规范落地骨架目录与 `.gitignore`、`.editorconfig`、`.env.example`。

### 为什么做

所有后续代码都会按这套规范放置；规范在第一天定下，避免 W4–W7 返工。`.env.example` 的键名就是 Day07/08 Settings 的字段来源。

### 资产锚点

M0.3 项目规范 + 模板。

### 前置依赖

Task 2。

### 具体执行步骤

1. Web UI 建仓 → clone。
2. `mkdir -p` 建骨架 → 每个目录写 README.md 或 `.gitkeep`。
3. 写根配置三件套。
4. 写 `PROJECT_STANDARD.md` 9 节（AI 起草，自己逐条审）。
5. `find` / `git check-ignore` 自检 → 提交 push。

### 验收标准

- [ ] 目录结构与规范 §1 一致（`find` 输出对照）
- [ ] `git check-ignore -v .env data/x.csv eval/runs/a.json` 三条都命中；`.env.example`、`data/sample/README.md` 不被忽略
- [ ] 不看文档能说出每个顶层目录用途
- [ ] push 成功

### 完成后的产出

`~/lab/ai-project-template/{PROJECT_STANDARD.md,.gitignore,.editorconfig,.env.example}` + 骨架目录及各目录 README。

### 求职映射

工程规范化能力；面试题「AI 项目目录如何组织」「密钥如何管理」。

### 如果时间不够 / 没有必要

最低：骨架 + `.gitignore` + `.env.example` + 规范 §1–§4；§5–§9 在 Day05 开头 15 分钟补。

---

## Task 4：工程模板 + 创建 workpilot 仓库（Day05 · 10-02）

### 做什么

在模板中补 README 模板、`docs/adr/0000-template.md`、Makefile（`make help` 自动列出）、`deploy/docker-compose.yml`（`traefik/whoami` 示例）、`scripts/bootstrap.sh`；在 Gitea 设置中把它标为模板仓库，用「使用此模板」生成 `workpilot`，写 README 定位与版本路线、`docs/product/target-asset.md`，打 tag `v0.0.0`。

### 为什么做

模板是 M14 模板库的第一块；`workpilot` 是 DA-01 唯一代码仓库，从此所有 B/C 线产出都进这里。

### 资产锚点

M0.3 / **v0.0**。

### 前置依赖

Task 3。

### 具体执行步骤

1. 补模板文件 → `make help`、`make up/down`、`bash scripts/bootstrap.sh` 验证 → push。
2. Gitea 仓库设置勾选「模板」。
3. 「使用此模板」生成 `workpilot`（勾选 Git 内容）→ clone `~/lab/workpilot`。
4. 写 README + `docs/product/target-asset.md` → commit → tag `v0.0.0` → push。
5. 周验收 + 周复盘；回填 `PROJECT_CONFIG.md`。
6. P1：`brew install uv pnpm node`。

### 验收标准

- [ ] `make help` ≥ 8 个命令；`make up` 后 `curl localhost:8081` 有 whoami 输出；`make down` 清理
- [ ] Gitea 中 `ai-project-template` 显示模板标识，`workpilot` 由模板生成
- [ ] `git ls-remote --tags origin` 含 `v0.0.0`
- [ ] Week 01 README §11 已填写

### 完成后的产出

`~/lab/ai-project-template/{README.md,Makefile,deploy/docker-compose.yml,scripts/bootstrap.sh,docs/adr/0000-template.md}`；`~/lab/workpilot`（tag `v0.0.0`）；`~/lab/workpilot/docs/product/target-asset.md`。

### 求职映射

「模板化 / 平台化思维」：把重复的项目初始化工作标准化；面试可讲「为什么用 Makefile 做统一入口」。

### 如果时间不够 / 没有必要

最低：Makefile（help/up/down）+ 模板化 + 生成 workpilot + tag。`bootstrap.sh` 与 `target-asset.md` 可顺延到 Day07 开头 15 分钟；P1 安装工具顺延到 Day07 Step 1。

---
