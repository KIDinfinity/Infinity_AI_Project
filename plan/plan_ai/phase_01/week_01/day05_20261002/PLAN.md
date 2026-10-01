# Day 05 · 2026-10-02 · Week 01 Task 4：工程模板 + 创建 workpilot 仓库（v0.0）

## 0. 今天只做一件事

把 `ai-project-template` 补成可直接复用的模板（README 模板 / ADR 模板 / Makefile / compose 示例 / bootstrap），在 Gitea 标记为模板仓库，用它生成 DA-01 仓库 `workpilot`，打 tag `v0.0.0`。

不碰：Python / FastAPI 代码（Day07）、CI（W7）、MinIO / Qdrant（Day09）、Gitea 模板变量替换等高级功能。

## 1. 资产锚点

- 构建模块：M0.3 项目规范 + 模板（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.0**（仓库骨架 + 规范 + 模板）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：Gitea 上有 `workpilot` 仓库与 tag `v0.0.0`；`make help` 列出统一入口；`make up` 起一个示例容器、`make down` 清理；README 写清一句话定位与版本路线。
- 今日 AI 实际应用：用 Copilot 生成 README / ADR / Makefile 样板 → 自己核对 Makefile 的 Tab、`help` 的 grep 规则和 compose 项目名逻辑；之后每个 AI 项目都从这个模板起步（M14 模板库的第一块）。

## 2. 起点（前置确认）

- 已有：`~/lab/ai-project-template`（Day04：规范 + 骨架 + 三件套，已 push）。
- 需确认：

```bash
cd ~/lab/ai-project-template && git pull && git status --short   # 干净
grep -c '^## ' PROJECT_STANDARD.md                                # ≥ 9（不足先补，限 15 分钟）
docker version --format '{{.Server.Version}}'                     # 有版本号
lsof -iTCP:8081 -sTCP:LISTEN || echo "8081 free"                  # 示例容器用 8081
```

## 3. 验收对齐（做完要能勾掉）

- [ ] 模板中存在 `README.md`、`Makefile`、`deploy/docker-compose.yml`、`scripts/bootstrap.sh`、`docs/adr/0000-template.md`
- [ ] `make help` 输出 ≥ 8 个命令及说明
- [ ] `make up` 后 `curl -s localhost:8081 | head -3` 有 `Hostname:` 输出；`make down` 后 `docker ps` 无该容器
- [ ] `bash scripts/bootstrap.sh` 生成 `.env` 并列出 docker / uv / node / pnpm 安装状态
- [ ] Gitea 中 `ai-project-template` 为模板仓库，`workpilot` 由「使用此模板」生成，本地在 `~/lab/workpilot`
- [ ] `cd ~/lab/workpilot && git ls-remote --tags origin` 含 `refs/tags/v0.0.0`
- [ ] Week 01 README §11 周复盘已填写；`PROJECT_CONFIG.md` DA-01 路径回填为 `~/lab/workpilot`

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                               |
| ----------- | ------ | ------------------------------------------------------------------ |
| 0–10 min    | P0     | 前置确认                                                           |
| 10–25 min   | P0     | README 模板 + ADR 模板                                             |
| 25–50 min   | P0     | Makefile + compose 示例，验证 `make help / up / down`              |
| 50–65 min   | P0     | `scripts/bootstrap.sh` + 提交模板                                  |
| 65–80 min   | P0     | Gitea 模板化 → 生成 `workpilot` → clone                            |
| 80–95 min   | P0     | `workpilot` README + `docs/product/target-asset.md` + tag `v0.0.0` |
| 95–108 min  | P0     | 本周验收勾选 + 周复盘 + 回填 `PROJECT_CONFIG.md`                   |
| 108–120 min | P1     | `brew install uv pnpm node`，验证版本（为 Day07 准备）             |
| —           | P2     | Gitea 仓库描述 / 主题标签；README 加徽章                           |

时间不足时最低保留：Makefile（help / up / down）+ 模板化 + 生成 `workpilot` + tag `v0.0.0`。bootstrap 与 target-asset.md 顺延到 Day07 开头；P1 安装顺延到 Day07 Step 1。

## 5. 今日学习（只学完成任务必须的）

- **Makefile**：配方行必须以 **Tab** 开头；`.PHONY` 声明非文件目标；`$$` 在 Makefile 中表示 shell 的 `$`。
- **compose 项目名**：默认取 compose 文件所在目录名（这里会是 `deploy`，多个项目会冲突），用 `-p` 显式指定。
- **Gitea 模板仓库**：设置里勾选「模板」后，仓库页出现「使用此模板」，可复制 Git 内容生成新仓库（历史不继承）。
- **附注 tag**：`git tag -a` 带作者、日期、说明，适合发布；`git push` 默认不推 tag，需单独推。
- 资料：https://docs.gitea.com/ 、https://docs.docker.com/compose/ 、https://www.gnu.org/software/make/manual/make.html 、https://semver.org/

## 6. 执行步骤

### Step 1 · README 模板 + ADR 模板（P0，可让 AI 生成）

`README.md`（模板，用 `<>` 标占位，章节对应规范 §7）：

```markdown
# <项目名>

> <一句话定位：给谁、解决什么问题、怎么解决>

## 功能

- [ ] <功能 1>

## 架构

<mermaid 图或链接 docs/architecture.md>

## 快速开始

make bootstrap # 复制 .env、检查依赖
make up # 启动依赖服务
make dev # 本地开发

## 目录

见 PROJECT_STANDARD.md §1

## 常用命令

make help

## 配置

所有键见 .env.example；真实值只放 .env（不提交）

## 评测

make eval → eval/reports/

## 部署

见 docs/runbook.md

## 路线图

| 版本 | 内容 | 状态 |
```

`docs/adr/0000-template.md`：内容即 `PROJECT_STANDARD.md` §8 的 ADR 模板（直接复制），标题改为 `# 0000. ADR 模板（复制本文件并改编号）`。

### Step 2 · Makefile + compose 示例（P0，核心，自己理解每一行）

`deploy/docker-compose.yml`（最小示例，只证明 `make up/down` 通路；W7 换成真实服务）：

```yaml
services:
  whoami:
    image: traefik/whoami:latest # 返回请求信息的极小 HTTP 服务
    ports:
      - "8081:80"
    restart: "no"
```

`Makefile`（**配方行开头是 Tab**；`.editorconfig` 已设置，VS Code 右下角应显示「Tab」）：

```makefile
.DEFAULT_GOAL := help
PROJECT ?= $(notdir $(CURDIR))
COMPOSE := docker compose -p $(PROJECT) -f deploy/docker-compose.yml

.PHONY: help bootstrap dev test lint up down logs eval backup

help: ## 列出所有命令
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

bootstrap: ## 初始化本地环境（复制 .env、检查依赖）
	@bash scripts/bootstrap.sh

dev: ## 本地开发启动（Day07 接入 apps/api）
	@echo "TODO: dev"

test: ## 运行测试（Day07 接入 pytest）
	@echo "TODO: test"

lint: ## 代码检查（Day07 接入 ruff）
	@echo "TODO: lint"

up: ## 启动 compose 服务
	$(COMPOSE) up -d

down: ## 停止并移除 compose 服务
	$(COMPOSE) down

logs: ## 跟踪 compose 日志
	$(COMPOSE) logs -f --tail=100

eval: ## 运行评测（W5 接入）
	@echo "TODO: eval"

backup: ## 备份数据（W7 接入 deploy/scripts/backup.sh）
	@echo "TODO: backup"
```

要点：`PROJECT` 取仓库目录名，所以模板里是 `ai-project-template`，生成的 workpilot 里自动变成 `workpilot`，无需改 Makefile。

验证：

```bash
make            # 等同 make help，期望 10 行命令说明
make up && docker ps --format '{{.Names}}'     # 期望 ai-project-template-whoami-1
curl -s localhost:8081 | head -3               # 期望 Hostname: ...
make down && docker ps --format '{{.Names}}'   # 期望不再有 whoami
```

### Step 3 · scripts/bootstrap.sh（P0）

```bash
#!/usr/bin/env bash
# 新机器 / 新 clone 后执行一次：准备 .env 并检查依赖工具
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  echo "[skip] .env 已存在"
else
  cp .env.example .env
  echo "[ok]   已从 .env.example 生成 .env —— 请填写其中的密钥"
fi

missing=0
check() {   # check <命令> <安装提示>
  if command -v "$1" >/dev/null 2>&1; then
    printf '[ok]   %-6s %s\n' "$1" "$("$1" --version 2>&1 | head -n1)"
  else
    printf '[miss] %-6s 安装：%s\n' "$1" "$2"
    missing=1
  fi
}
check docker "brew install --cask docker（并启动 Docker Desktop）"
check uv     "brew install uv"
check node   "brew install node"
check pnpm   "brew install pnpm"

if docker info >/dev/null 2>&1; then echo "[ok]   docker daemon 运行中"; else echo "[warn] docker daemon 未运行：打开 Docker Desktop"; fi
[[ $missing -eq 0 ]] && echo "环境就绪" || echo "有工具缺失，按上面提示安装后重跑 make bootstrap"
```

```bash
chmod +x scripts/bootstrap.sh
make bootstrap         # 期望生成 .env，列出 4 个工具状态
git status --short     # .env 不应出现（Day04 的 .gitignore 生效）
git add . && git commit -m "feat(template): add Makefile, compose example, bootstrap and README/ADR templates"
git push
```

### Step 4 · Gitea 模板化 → 生成 workpilot（P0）

1. 打开 `http://localhost:3000/<user>/ai-project-template` →「设置」→「仓库」基本设置区 → 勾选「模板」(Template) →「更新仓库设置」。仓库标题旁出现模板标识。
2. 回到仓库首页 → 点「使用此模板」(Use this template)：
   - 仓库名 `workpilot`，Private；
   - 模板项**勾选「Git 内容（默认分支）」**（不勾则生成空仓库）；
   - 描述：`DA-01 · 研发工作 AI 助手平台`。
3. clone：

```bash
cd ~/lab
git clone http://localhost:3000/<user>/workpilot.git
cd workpilot && ls -a && make help    # 期望与模板相同的文件，make help 正常
```

### Step 5 · workpilot README + 目标资产摘要 + tag（P0）

把 `README.md` 顶部替换为（其余章节保留模板占位）：

```markdown
# WorkPilot

> 一个可私有部署的「研发工作 AI 助手平台」：接入团队/个人研发知识，用带引用的 RAG 回答问题，
> 用可审批的 Agent 调用工具完成高频研发工作流，并通过 MCP 嵌入 IDE；自带评测、可观测、安全护栏和一键部署。

## 路线图

| 版本      | 内容                                                  | 状态   |
| --------- | ----------------------------------------------------- | ------ |
| v0.0      | 仓库骨架 + 规范 + 模板                                | ✅     |
| v0.1      | LLM Gateway：结构化输出 / 流式 / 成本 / CLI           | W2–3   |
| v0.2–v0.4 | RAG MVP → 评测优化 → Web Console                      | W4–6   |
| v0.5      | P1：Knowledge 云端可访问                              | W7–8   |
| v0.6–v1.0 | Tools / Agent / Memory / HITL / MCP / Agent Eval → P2 | W9–16  |
| v1.1–v2.0 | 场景包 / 多空间 / 安全 / 回归 / 在线 Demo → P3        | W17–23 |
```

`docs/product/target-asset.md`：放蓝图摘要（复制蓝图 §0 一句话定义、§3 F1–F8 标题列表、§9 版本表），末尾注明「完整蓝图：Infinity_AI_Project/plan/plan_ai/DA01_TARGET_ASSET.md（私有规划仓库，不随本仓库公开）」。**不复制**预算、商业化定价、个人约束（W8 本仓库会公开）。

```bash
git add . && git commit -m "docs: add WorkPilot positioning, roadmap and target asset summary"
git push
git tag -a v0.0.0 -m "v0.0: skeleton + standard + template"
git push origin v0.0.0
git ls-remote --tags origin       # 期望 refs/tags/v0.0.0
```

### Step 6 · 周验收 + 复盘 + 回填（P0）

1. 打开 `plan/phase_01/week_01/README.md` §7 逐项勾 PASS / FAIL，填 §11 周复盘。
2. 在 `Infinity_AI_Project/PROJECT_CONFIG.md` 把「DA-01 根目录」「DA-01 路径」改为已确认的 `~/lab/workpilot`（Gitea 仓库 `workpilot`，tag v0.0.0）。

### Step 7 · 工具安装（P1，为 Day07 准备）

```bash
brew install uv pnpm node
uv --version && node --version && pnpm --version
cd ~/lab/workpilot && make bootstrap     # 期望 4 个 [ok]
```

### Step 8 · 提交

模板与 workpilot 已在 Step 3、Step 5 分别提交并推送；确认：

```bash
cd ~/lab/ai-project-template && git status --short && git log --oneline -3
cd ~/lab/workpilot && git status --short && git log --oneline -3
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 Makefile 用 `-p $(PROJECT)`？（答：compose 默认用 compose 文件所在目录名 `deploy` 当项目名，多个仓库会互相覆盖容器）
2. `help` target 是怎么「自动」列出命令的？（答：grep 出带 `## ` 注释的 target 行，awk 按 `:.*## ` 切分打印）
3. 从模板生成的仓库和 fork 有什么区别？（答：模板生成是全新历史、无上游关系；fork 保留历史并可向上游提 PR）
4. 为什么 tag 用 `-a`？（答：附注 tag 是完整对象，含作者 / 日期 / 说明，适合标记发布）
5. bootstrap 为什么不覆盖已存在的 `.env`？（答：避免冲掉已填写的真实密钥）

## 8. 对 DA-01 的贡献

DA-01 从今天起有了唯一代码仓库 `~/lab/workpilot` 和第一个版本 `v0.0.0`，结构与蓝图 §6.2 一致；Week 02 的 FastAPI、LLM Gateway 直接写进 `apps/api/`，`make dev/test/lint` 已有入口。模板本身是 M14 模板库的起点。

## 9. 求职映射（D 线）

- 岗位能力：工程模板化、开发者体验（DX）、Docker Compose 基础
- 对应岗位：AI 全栈工程师、AI Platform / 工程效能方向
- 简历 bullet 草稿：设计 AI 项目模板仓库（Makefile 统一入口 + compose + bootstrap + ADR），新项目从模板生成到可运行 < \_\_ 分钟。
- 面试可能问：
  - 「为什么用 Makefile 而不是 npm scripts / just？」→ 要点：跨语言（Python + Node + Docker）、macOS / Linux 预装、`make help` 自描述；代价是 Tab 和语法古老。
  - 「新人 clone 你的项目后要做什么？」→ 要点：`make bootstrap` → 填 `.env` → `make up` → `make dev`，全部写在 README 快速开始。

## 10. 卡住时的处理

| 现象                                        | 处理                                                                                                 |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `Makefile:N: *** missing separator.  Stop.` | 配方行用了空格；VS Code 右下角切为 Tab 缩进，或 `cat -A` 查看（macOS 用 `cat -et`，Tab 显示为 `^I`） |
| `make help` 无输出                          | grep 规则要求 `target: ## 说明`，检查是否漏了 `## ` 或 target 名含点号                               |
| `make up` 报 `port is already allocated`    | 8081 被占：`lsof -iTCP:8081` 查进程，或改 compose 端口                                               |
| 拉 `traefik/whoami` 超时                    | Docker Desktop → Settings → Resources → Proxies 填 `http://127.0.0.1:7890` 后重试                    |
| 找不到「使用此模板」按钮                    | 先在设置里勾「模板」并保存；按钮在仓库首页右上方                                                     |
| 生成的 workpilot 是空仓库                   | 生成时没勾「Git 内容（默认分支）」；删掉重建（Web UI 设置 → 危险操作区）                             |

## 11. 产出记录（执行时填写）

- `make help` 命令数：\_\_\_\_
- `make up/down` 是否成功：\_\_\_\_
- bootstrap 输出（缺哪些工具）：\_\_\_\_
- workpilot 仓库地址：\_\_\_\_
- tag v0.0.0 是否推送：\_\_\_\_
- 本周验收 PASS 数 / 总数：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE，Week 01 结束（v0.0）→ 明天进入 Week 02 Day06（AI 岗位能力矩阵 v1）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
