# Day 04 · 2026-10-01 · Week 01 Task 3：项目规范 PROJECT_STANDARD

## 0. 今天只做一件事

在 Gitea 新建模板仓库 `ai-project-template`，写出 `PROJECT_STANDARD.md`，并按规范落地骨架目录 + `.gitignore` / `.editorconfig` / `.env.example`，push 成功。

不碰：Makefile、README 模板、bootstrap 脚本、compose（Day05）；任何 Python / 前端代码（Day07 起）；CI（W7）。

## 1. 资产锚点

- 构建模块：M0.3 项目规范 + 模板（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.0 做准备（Day05 由模板生成 `workpilot` 并打 `v0.0.0`）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：一份可执行的规范 + 一个目录结构与蓝图 §6.2 对齐的空骨架；`git check-ignore` 可证明密钥与本地数据不会入库。
- 今日 AI 实际应用：用 Copilot 按本计划 Step 4 的要点起草规范正文 → 自己逐节审改；`.env.example` 的键名就是 Day07/08 `Settings` 的字段（M1 LLM Gateway 读取配置的来源）。

## 2. 起点（前置确认）

- 已有：Docker、Gitea（`:3000`）、`~/lab/projects`；HTTPS + 访问令牌推送已跑通（Day02）。
- 需确认：

```bash
docker ps --filter name=gitea --format '{{.Names}} {{.Status}}'   # gitea Up
git config --global user.name && git config --global init.defaultBranch   # 有值；分支为 main
ls ~/lab                                                             # 有 projects，无 ai-project-template
```

## 3. 验收对齐（做完要能勾掉）

- [ ] Gitea 上存在 Private 仓库 `ai-project-template`，本地在 `~/lab/ai-project-template`
- [ ] `find . -path ./.git -prune -o -print | sort` 输出与本计划 Step 2「预期输出」一致
- [ ] `git check-ignore -v .env .env.local data/x.csv eval/runs/a.json` 4 行均有输出
- [ ] `git check-ignore .env.example data/README.md data/sample/README.md` 无输出（`echo $?` 为 1）
- [ ] `PROJECT_STANDARD.md` 含 9 节（`grep -c '^## ' PROJECT_STANDARD.md` ≥ 9）
- [ ] 合上文档，口述 8 个顶层目录（apps / prompts / eval / data / deploy / scripts / docs / .gitea）各放什么、不放什么
- [ ] `git log --oneline origin/main` 有今天的提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                |
| ----------- | ------ | ------------------------------------------------------------------- |
| 0–10 min    | P0     | 前置确认 + Web UI 建仓 + clone                                      |
| 10–25 min   | P0     | 骨架目录 + 各目录 README / .gitkeep                                 |
| 25–45 min   | P0     | `.gitignore` / `.editorconfig` / `.env.example` + check-ignore 验证 |
| 45–90 min   | P0     | `PROJECT_STANDARD.md` §1–§6（§1 目录表必须自己逐行过）              |
| 90–100 min  | P1     | `PROJECT_STANDARD.md` §7–§9                                         |
| 100–110 min | P0     | 结构自检 + 提交 push                                                |
| 110–120 min | P1     | 概念自检口述 + 产出记录                                             |

时间不足时最低保留：建仓 + 骨架 + `.gitignore` + `.env.example` + 规范 §1–§4 + push（§5–§9 Day05 开头补 15 分钟）。

## 5. 今日学习（只学完成任务必须的）

- **Conventional Commits**：`type(scope): subject`，type 常用 feat / fix / docs / test / refactor / chore / ci。
- **SemVer**：`MAJOR.MINOR.PATCH`；0.x 阶段 API 不稳定，MINOR 对应蓝图版本里程碑。
- **.gitignore 取反**：`data/*` 忽略子项，`!data/sample/` 再放回；父目录被整体忽略（写成 `data/`）时子项无法取反。
- **EditorConfig**：跨编辑器统一编码 / 换行 / 缩进；Makefile 必须 Tab。
- **ADR**：一页纸记录「当时为什么这么选」，只增不改，被取代时新开一篇。
- 资料：https://www.conventionalcommits.org/ 、https://semver.org/ 、https://editorconfig.org/ 、https://git-scm.com/docs/gitignore 、https://docs.gitea.com/

## 6. 执行步骤

### Step 1 · Gitea 建仓并 clone（P0）

1. 浏览器打开 `http://localhost:3000` → 右上角「+」→「新建仓库」。
2. 名称 `ai-project-template`，可见性 **Private**，**不勾选**「初始化仓库」（不加 README / .gitignore / License，避免和本地内容冲突）。
3. 本地：

```bash
cd ~/lab
git clone http://localhost:3000/<user>/ai-project-template.git
cd ai-project-template
# 提示 "You appear to have cloned an empty repository." 属正常
```

### Step 2 · 建骨架目录（P0）

一条命令建全部目录：

```bash
mkdir -p apps/api/tests apps/web prompts eval/{datasets,runners,reports,badcases} \
  data/sample deploy/scripts scripts docs/{adr,product,portfolio} .gitea/workflows
```

用 `printf` 给每个目录写一句话 README（`w` 是临时 shell 函数，关掉终端即消失）：

```bash
w() { printf '# %s\n\n%s\n' "$1" "$2" > "$1/README.md"; }
w apps           "可运行应用：每个子目录一个可独立启动的 app，自带 tests/。不放实验脚本和笔记。"
w apps/api       "后端服务（Python 3.12 + FastAPI，uv 管理）。代码在 app/，测试在 tests/。"
w apps/web       "前端应用（Vite + React + TS，pnpm 管理）。只调用 API，不放任何密钥。"
w prompts        "版本化提示词：<name>.v<N>.md。改 prompt = 新增版本文件，旧版本保留用于回归对比。"
w eval           "评测：datasets/ 数据集、runners/ 脚本、reports/ 报告（提交）、badcases/ 坏例库；运行明细写 eval/runs/（忽略）。"
w data           "本地数据，整体被 .gitignore 忽略；只有本文件和 data/sample/ 会提交。"
w data/sample    "可公开的小样例（单文件 ≤ 1MB），用于测试与演示。禁止放公司数据。"
w deploy         "部署：docker-compose*.yml、Caddyfile；deploy/scripts/ 放备份 / 恢复 / 健康检查脚本。"
w scripts        "开发辅助脚本（bootstrap、ingest、调试 CLI）。运维脚本放 deploy/scripts/。"
w docs           "文档：architecture.md、runbook.md、api.md、adr/、product/、portfolio/。"
w docs/adr       "架构决策记录：NNNN-kebab-title.md，模板见 0000-template.md（Day05 补）。"
w docs/product   "产品文档：定位、场景定义、路线图。不写实现细节。"
w docs/portfolio "求职写作：项目技术复盘、作品集文稿。"
printf '# Architecture\n\nTODO：mermaid 架构图 + 数据流\n' > docs/architecture.md
printf '# Runbook\n\nTODO：启动 / 部署 / 备份 / 恢复 / 排障\n' > docs/runbook.md
printf '# API\n\nTODO：端点列表与示例\n' > docs/api.md
touch apps/api/tests/.gitkeep eval/{datasets,runners,reports,badcases}/.gitkeep \
  deploy/scripts/.gitkeep .gitea/workflows/.gitkeep
```

预期输出（`find . -path ./.git -prune -o -print | sort`，Step 3/4 完成后）：

```text
.  ./.editorconfig  ./.env.example  ./.gitea  ./.gitea/workflows  ./.gitea/workflows/.gitkeep  ./.gitignore
./PROJECT_STANDARD.md  ./apps  ./apps/README.md  ./apps/api  ./apps/api/README.md  ./apps/api/tests
./apps/api/tests/.gitkeep  ./apps/web  ./apps/web/README.md  ./data  ./data/README.md  ./data/sample
./data/sample/README.md  ./deploy  ./deploy/README.md  ./deploy/scripts  ./deploy/scripts/.gitkeep
./docs  ./docs/README.md  ./docs/adr  ./docs/adr/README.md  ./docs/api.md  ./docs/architecture.md
./docs/portfolio/README.md  ./docs/product/README.md  ./docs/runbook.md  ./eval/README.md
./eval/{badcases,datasets,reports,runners}/.gitkeep  ./prompts/README.md  ./scripts/README.md
```

（实际为每行一个路径，这里压缩展示；`brew install tree` 后可用 `tree -a -I .git` 看树形。）

### Step 3 · 根配置三件套（P0）

`.gitignore`：

```gitignore
# OS / IDE
.DS_Store
.idea/
.vscode/*
!.vscode/extensions.json
# 密钥与环境：.env 及其变体全部忽略，只提交 .env.example
.env
.env.*
!.env.example
*.pem
*.key
# Python
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
*.egg-info/
# Node / 前端
node_modules/
dist/
*.tsbuildinfo
pnpm-debug.log*
# 本地数据：忽略 data/ 下所有内容，放回 README 与公开样例
data/*
!data/README.md
!data/sample/
# 评测运行明细（报告在 eval/reports/ 提交）
eval/runs/
# 运行时产物
*.log
*.sqlite
*.db
```

`.editorconfig`：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4

[Makefile]
indent_style = tab

[*.md]
trim_trailing_whitespace = false
```

`.env.example`（键名即 Day07/08 `Settings` 字段；空值 = 密钥，必须在 `.env` 填写）：

```dotenv
# ===== 应用 =====
# [必填] 运行环境：dev | test | prod
APP_ENV=dev
# [可选] 日志级别：DEBUG | INFO | WARNING | ERROR（默认 INFO）
LOG_LEVEL=INFO

# ===== LLM（统一经 M1 LLM Gateway，OpenAI 兼容协议）=====
# [必填] DeepSeek=https://api.deepseek.com ；本地 Ollama=http://localhost:11434/v1
LLM_BASE_URL=https://api.deepseek.com
# [必填·密钥] 只写在 .env；Ollama 可填任意非空串（如 ollama）
LLM_API_KEY=
# [必填] 模型名
LLM_MODEL=deepseek-chat
# [可选] 单次请求超时（秒，默认 30）
LLM_TIMEOUT_S=30

# ===== Embedding（bge-m3，1024 维；dev=Ollama，prod=SiliconFlow 同模型）=====
# [必填] 容器内访问宿主机 Ollama 时改为 http://host.docker.internal:11434/v1
EMBEDDING_BASE_URL=http://localhost:11434/v1
# [必填·密钥] Ollama 填 ollama；SiliconFlow 填真实 key
EMBEDDING_API_KEY=ollama
# [必填] Ollama 为 bge-m3；SiliconFlow 以其模型列表名称为准
EMBEDDING_MODEL=bge-m3

# ===== 向量库 Qdrant =====
# [必填] HTTP 端口 6333
QDRANT_URL=http://localhost:6333

# ===== 对象存储 MinIO（S3 兼容）=====
# [必填] API 端口 9000（控制台 9001 不在这里配）
MINIO_ENDPOINT=http://localhost:9000
# [必填·密钥]
MINIO_ACCESS_KEY=
# [必填·密钥]
MINIO_SECRET_KEY=

# ===== 业务库 =====
# [必填] W6 起 SQLite；W19 改为 postgresql+psycopg://user:pass@host:5432/db
DATABASE_URL=sqlite:///./data/app.db
```

验证忽略规则（**必须做**，这是密钥不泄漏的客观证据）：

```bash
touch .env .env.local data/x.csv && mkdir -p eval/runs && touch eval/runs/a.json
git check-ignore -v .env .env.local data/x.csv eval/runs/a.json   # 期望 4 行，每行显示命中的规则
git check-ignore .env.example data/README.md data/sample/README.md; echo "exit=$?"   # 期望无输出，exit=1
rm .env .env.local data/x.csv && rm -r eval/runs
```

### Step 4 · 写 PROJECT_STANDARD.md（P0 §1–§6，P1 §7–§9）

做法：把下面的要点贴给 Copilot Chat，要求「按以下 9 节生成中文 Markdown，表格优先，不加多余内容」；生成后**自己逐行审**。§1 的目录表是今天的核心，必须能脱稿复述。

**§1 目录规范**（直接写成表格，每个目录一行）：

| 路径                                             | 做什么                 | 放什么                                        | 不放什么                            |
| ------------------------------------------------ | ---------------------- | --------------------------------------------- | ----------------------------------- |
| `README.md`                                      | 项目门面               | 定位、快速开始、常用命令、架构图              | 长篇设计（→ docs/）                 |
| `PROJECT_STANDARD.md`                            | 本规范                 | 目录 / 命名 / 提交 / 配置规则                 | 业务说明                            |
| `Makefile`                                       | 统一命令入口           | 各 target 一两行调用                          | 复杂逻辑（> 3 行 → scripts/）       |
| `.env.example`                                   | 配置清单               | 全部键 + 注释 + 安全默认值                    | 任何真实密钥                        |
| `.gitignore` / `.editorconfig`                   | 忽略规则 / 格式统一    | 见 Step 3                                     | —                                   |
| `apps/`                                          | 可运行应用             | 每子目录一个可独立启动的 app，各自带 `tests/` | 实验脚本、笔记                      |
| `apps/api/`                                      | 后端                   | `pyproject.toml`、`uv.lock`、`app/`、`tests/` | 前端代码、数据文件                  |
| `apps/web/`                                      | 前端                   | `package.json`、`src/`、测试                  | 后端逻辑、密钥                      |
| `prompts/`                                       | 版本化提示词           | `<name>.v<N>.md`                              | 代码里再复制一份 prompt             |
| `eval/datasets/`                                 | 评测集                 | `*.jsonl`（公开 / 脱敏）                      | 机密数据                            |
| `eval/runners/`                                  | 评测脚本               | `run_*.py`                                    | 业务代码                            |
| `eval/reports/`                                  | 评测报告（提交）       | `YYYYMMDD-<name>.md`                          | 原始运行明细（→ `eval/runs/` 忽略） |
| `eval/badcases/`                                 | 坏例库                 | `badcases.md`                                 | —                                   |
| `data/`                                          | 本地数据（忽略）       | 语料、SQLite、导出文件                        | 任何需要提交的东西                  |
| `data/sample/`                                   | 公开样例（提交）       | ≤ 1MB 的可公开小样本                          | 公司数据                            |
| `deploy/`                                        | 部署编排               | `docker-compose*.yml`、`Caddyfile`            | 应用源码                            |
| `deploy/scripts/`                                | 运维脚本               | `backup.sh`、`restore.sh`、`healthcheck.sh`   | 开发辅助脚本                        |
| `scripts/`                                       | 开发辅助               | `bootstrap.sh`、`ingest.sh`、`chat.py`        | 运维脚本、正式业务逻辑              |
| `docs/architecture.md` · `runbook.md` · `api.md` | 架构 / 运维手册 / 接口 | mermaid 图、操作步骤、端点示例                | —                                   |
| `docs/adr/`                                      | 架构决策               | `NNNN-kebab-title.md`                         | 会议纪要                            |
| `docs/product/` · `docs/portfolio/`              | 产品文档 / 求职写作    | 定位、场景、路线 / 项目复盘                   | 实现细节                            |
| `.gitea/workflows/`                              | CI                     | `ci.yml`（语法兼容 GitHub Actions）           | 部署密钥                            |

**§2 命名规范**：Python 模块 / 函数 / 变量 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE`；React 组件文件与组件名 `PascalCase.tsx`，hooks `useXxx.ts`，其余 TS 文件 `camelCase.ts`；文档 `kebab-case.md`（README / 规范等约定大写文件除外）；prompt `<name>.v<N>.md`（如 `qa_answer.v1.md`）；ADR `NNNN-kebab-title.md`（如 `0001-llm-provider.md`）；环境变量 `UPPER_SNAKE`，按前缀分组（`LLM_` / `EMBEDDING_` / `MINIO_`）；分支 `feat/<短描述>`。

**§3 分支与提交**：`main` 永远可运行；≤ 1 天的改动可直接提交 main；跨天 / 实验性改动用 `feat/xxx`，完成后合并并删分支。提交遵循 Conventional Commits，示例：

```text
feat(api): add /health endpoint
fix(llm): retry on timeout and 5xx responses
docs(adr): add 0001-llm-provider
test(rag): add hit@k unit tests
chore(deploy): pin qdrant image version
```

**§4 环境变量**：`.env` 永不提交；`.env.example` 列出全部键，每键一行注释并标 `[必填]` / `[可选]` / `[必填·密钥]`，密钥值留空；新增键与使用它的代码同一个提交；代码只通过 `Settings`（pydantic-settings）读取，不散落 `os.getenv`；**密钥轮换**：疑似泄漏或每 90 天 → 平台生成新 key → 改 `.env` → 重启 → 验证 → 撤销旧 key；误提交密钥一律视为已泄漏，立即轮换（改写 Git 历史不够）。

**§5 版本号与 tag**：SemVer；0.x 阶段 `v0.MINOR.0` 对应蓝图版本里程碑（v0.1 → `v0.1.0`），修复递增 PATCH；用附注 tag `git tag -a v0.1.0 -m "v0.1: ..."` + `git push origin v0.1.0`；只在 main 且 `make test` 通过后打；已推送的 tag 不移动、不删除。

**§6 Makefile 统一入口**：`help`（默认目标，自动列出）、`bootstrap`、`dev`、`test`、`lint`、`up`、`down`、`logs`、`eval`、`backup`；每个 target 带 `## 说明`；任何人 clone 后只需记住 `make help`。

**§7 README 必含章节**：一句话定位 / 功能 / 架构 / 快速开始 / 目录 / 常用命令 / 配置 / 评测 / 部署 / 路线图。

**§8 ADR 模板**：

```markdown
# NNNN. 标题

- 状态：提议 | 已采纳 | 已废弃 | 被 NNNN 取代
- 日期：YYYY-MM-DD

## 背景（要解决什么问题，有什么约束）

## 决策（选了什么）

## 备选方案（列出并说明放弃理由）

## 后果（好处 / 代价 / 后续动作）
```

**§9 数据合规**（引用蓝图 §8）：公司机密代码 / 文档 / 工单不进入外部 LLM API；语料只用自己笔记、公开开源文档、手工脱敏样例；公司内真实使用需先获许可并用公司设施 + 本地模型；主业时间不开发本项目；公开仓库 / Demo 发布前做敏感信息检查。

### Step 5 · 结构自检（P0）

```bash
find . -path ./.git -prune -o -print | sort     # 对照 Step 2 预期输出
grep -c '^## ' PROJECT_STANDARD.md              # ≥ 9
git status --short                              # 不应出现 .env
```

### Step 6 · 提交（P0）

```bash
git add .
git commit -m "docs: add PROJECT_STANDARD and project skeleton"
git push -u origin main
git log --oneline origin/main | head -3
```

## 7. 概念自检（不看资料，口述，附答案）

1. `eval/reports/` 提交而 `eval/runs/` 忽略，为什么？（答：报告是结论、要随版本对比；runs 是大量原始明细，可再生成）
2. 为什么写 `data/*` 而不是 `data/`？（答：`data/` 忽略整个目录后，Git 不会进入目录，`!data/sample/` 无法生效）
3. `.env.example` 里为什么密钥留空而不是写假值？（答：空值让程序启动即暴露「未配置」，假值可能被误当真值使用；也避免被扫描工具误报）
4. 误把 key push 到仓库，`git rebase` 删掉提交就够了吗？（答：不够，视为泄漏，必须立刻在平台撤销并轮换）
5. 什么时候写 ADR？（答：选型或架构有备选方案且未来可能被质疑时，如 LLM 供应商、向量库、SQLite→Postgres）
6. `scripts/` 和 `deploy/scripts/` 的区别？（答：前者开发期辅助，后者生产运维用，部署时只需要后者）

## 8. 对 DA-01 的贡献

WorkPilot 从 Day05 起由这个模板生成，今天定下的目录就是蓝图 §6.2 的落地形态：M1 代码进 `apps/api/app/llm/`、M3 进 `eval/`、M5 进 `deploy/`、M1.6 进 `prompts/`。`.gitignore` + `.env.example` 保证 DeepSeek key 等密钥从第一天就不会入库。

## 9. 求职映射（D 线）

- 岗位能力：工程规范、配置与密钥管理、版本管理
- 对应岗位：AI Engineer、AI 全栈工程师（JD 常见「良好的工程素养」「熟悉 CI/CD 与 Git 工作流」）
- 简历 bullet 草稿：制定 AI 项目工程规范（目录 / 命名 / Conventional Commits / SemVer / 密钥管理 / ADR），沉淀为模板仓库，新项目初始化时间 < \_\_ 分钟。
- 面试可能问：
  - 「LLM 应用的 prompt 你怎么管理？」→ 要点：独立 `prompts/` 目录、`name.vN.md` 版本化、变更伴随评测回归、代码只引用版本号。
  - 「如何防止 API key 泄漏？」→ 要点：`.gitignore` 覆盖 `.env*`、`check-ignore` 验证、Settings 统一读取、日志不打印密钥、泄漏即轮换。

## 10. 卡住时的处理

| 现象                                            | 处理                                                                                        |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| clone 时 `Authentication failed`                | 用户名填 Gitea 用户名，密码填 Day02 的访问令牌；`git credential-osxkeychain erase` 清旧凭据 |
| push 报 `src refspec main does not match any`   | 还没有提交；先 `git add . && git commit`；或分支名是 master → `git branch -M main`          |
| `git check-ignore data/sample/README.md` 有输出 | `.gitignore` 写成了 `data/`；改为 `data/*` + `!data/sample/`                                |
| `zsh: no matches found: eval/{...}`             | 确认在 zsh/bash 中执行且花括号内无空格                                                      |
| Gitea 里看不到推送的仓库                        | 仓库必须先在 Web UI 创建再 clone（Day02 教训），不要本地 `git init`                         |
| 规范写到 60 分钟还没完                          | 停在 §6，§7–§9 Day05 补；规范以后通过 ADR 迭代，不追求一次写完                              |

## 11. 产出记录（执行时填写）

- 仓库地址：\_\_\_\_
- `find` 输出与预期是否一致：\_\_\_\_
- `check-ignore` 4 条命中 / 3 条不命中：\_\_\_\_
- 规范完成到第几节：\_\_\_\_
- 脱稿口述 8 个目录是否全部正确：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → 明天进入 Day05 Task 4（工程模板 + 创建 workpilot 仓库）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
