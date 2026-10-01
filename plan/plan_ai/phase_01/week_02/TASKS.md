# Week 02 · TASKS

> 详细命令与代码见各 `dayNN_xxx/PLAN.md`。本周所有密钥只放 `.env`，不入库。

---

## Task 1：AI 岗位能力矩阵 v1（Day06 · 10-03）

### 做什么

在 `projects` 仓库新增 `career/`：收集 10 个 AI 应用方向真实 JD 记入 `job-market.md`，统计技能频次，建 `capability-matrix.md`（能力 | JD 次数 | 当前水平 | 目标水平 | WorkPilot 证明模块 | 证据文件 | 计划周），产出 Top-12 能力与差距清单；建 `interview-questions.md` 空骨架与 `resume/`。

### 为什么做

D 线的反馈数据：确认蓝图 §1.1 的「JD 能力 ↔ WorkPilot 模块」映射是否成立，后续每 2 周用新 JD 校准。原则：**JD 是反馈数据，不是学习清单。**

### 资产锚点

M13.1 AI 岗位能力矩阵 + JD 追踪。

### 前置依赖

`~/lab/projects` 仓库；蓝图 §1.1、§5。

### 具体执行步骤（概要）

1. 建 `career/` 四件套骨架。
2. 按 5 个关键词在 Boss 直聘 / 拉勾 / LinkedIn / 公司官网收集 10 条 JD。
3. 用 AI 抽取技能（提示词见 PLAN），人工核对。
4. 统计频次 → 填矩阵 → 标 Top-12 与差距 → push。

### 验收标准

- [ ] `job-market.md` 10 条 JD，每条 7 个字段齐全
- [ ] 矩阵 Top-12 能力每项都填了 WorkPilot 证明模块与计划周
- [ ] 差距清单 ≥ 3 项（当前水平与目标差 ≥ 2）

### 完成后的产出

`~/lab/projects/career/{capability-matrix.md,job-market.md,interview-questions.md,resume/README.md}`

### 求职映射

直接产出 D 线资产；面试「你为什么觉得自己能胜任 AI 工程岗」的数据依据。

### 如果时间不够 / 没有必要

6 条 JD + Top-10，W3 末补齐；不允许跳过统计直接凭感觉填矩阵。

---

## Task 2：Python 工具链 + FastAPI 骨架（Day07 · 10-04）

### 做什么

`uv python install 3.12`；在 `~/lab/workpilot/apps/api` 用 uv 初始化，加 fastapi / uvicorn / pydantic-settings 与 dev 依赖 pytest / httpx / ruff；写 `app/main.py`、`app/core/config.py`（读仓库根 `.env`）、`app/routes/health.py`、`tests/test_health.py`；Makefile 接上 `dev / test / lint`。

### 为什么做

M1 LLM Gateway、M2 RAG、M6 Tools 都是这个 FastAPI 应用里的模块；先把配置读取、路由组织、测试、lint 的骨架定好。

### 资产锚点

M1 前置（`apps/api` 骨架）；为 v0.1 做准备。

### 前置依赖

Day05 `workpilot` 仓库、`.env.example`；`uv` 已安装（Day05 P1，否则今天 Step 1 装）。

### 具体执行步骤（概要）

1. 安装 Python 3.12，uv 初始化项目，加依赖。
2. 写 4 个文件 + pyproject 中 pytest / ruff 配置。
3. Makefile 改 `dev / test / lint`。
4. 验证 uvicorn / curl / `/docs` / pytest / ruff → 提交。

### 验收标准

- [ ] `make dev` 后 `curl -s localhost:8000/health` 返回 `{"status":"ok","env":"dev","version":"0.0.1"}`
- [ ] `/docs` 可打开
- [ ] `make test` 通过（≥ 2 个测试）；`make lint` 无报错

### 完成后的产出

`~/lab/workpilot/apps/api/{pyproject.toml,uv.lock,.python-version,app/**,tests/test_health.py}`、更新后的 `Makefile`

### 求职映射

Python / FastAPI / Pydantic / pytest —— AI 工程 JD 第一高频技能。

### 如果时间不够 / 没有必要

最低：`/health` + 1 个测试 + `make dev/test`；ruff 与 `/v1/echo` 示例可顺延到 Day08 开头。

---

## Task 3：LLM Gateway v0（Day08 · 10-05）

### 做什么

申请 DeepSeek API Key（小额充值）写入 `.env`；`uv add openai tenacity`；实现 `LLMGateway.chat(messages, **kw) -> ChatResult`（AsyncOpenAI + timeout + tenacity 指数退避最多 3 次 + 日志），错误归一化为结构化 JSON；路由 `POST /v1/chat`；假 provider 单测 + `@pytest.mark.live` 冒烟 + 超时 504 测试。

### 为什么做

蓝图 M1：所有 LLM 调用的唯一出口。之后 RAG、Agent、评测都只依赖 `LLMGateway`，换供应商只改 `.env`。

### 资产锚点

M1.1 Provider 抽象、M1.2 可靠性（timeout / retry）。

### 前置依赖

Task 2。

### 具体执行步骤（概要）

1. 申请 key、充值、写 `.env`，`Settings` 加 LLM 字段。
2. 写 `schemas.py`、`errors.py`、`gateway.py`、`routes/chat.py`，在 `main.py` 注册。
3. 写测试：成功 / 重试后成功 / 重试耗尽 504 / 401 不重试 / 不泄漏 key；live 冒烟。
4. 手动验证 curl 与超时 → 提交。
5. P2：切到本地 Ollama 模型验证可切换。

### 验收标准

- [ ] `curl /v1/chat` 返回 content + model + tokens + latency_ms
- [ ] `make test` 通过（不触网）；`uv run pytest -m live` 通过（触网）
- [ ] `LLM_TIMEOUT_S=0.001` → 504 `llm_timeout`；响应与日志中无 key

### 完成后的产出

`apps/api/app/llm/{__init__.py,gateway.py,schemas.py}`、`app/core/errors.py`、`app/routes/chat.py`、`tests/test_llm_gateway.py`

### 求职映射

LLM API 集成、可靠性工程 —— 面试高频「如何处理 LLM 调用超时 / 限流」。

### 如果时间不够 / 没有必要

最低：gateway + `/v1/chat` + 「重试耗尽 → 504」单测；live 冒烟与 P2 顺延。

---

## Task 4：MinIO + Qdrant + Ollama bge-m3（Day09 · 10-06）

### 做什么

`~/lab/projects/infra/compose/docker-compose.yml` 运行 MinIO（9000 / 9001）与 Qdrant（6333 / 6334），数据在 `~/lab-data/`；建 bucket `workpilot-raw`、`backups`；`brew install ollama` + `ollama pull bge-m3`，curl 验证 `/v1/embeddings`；写 `ai-lab/storage-smoke/smoke.py` 验证上传下载 sha256 一致与 6 句话语义检索。

### 为什么做

W4 RAG 需要：原文进 MinIO、向量进 Qdrant、bge-m3 出 1024 维向量。今天把三者在最小脚本里跑通，W4 只写业务逻辑。

### 资产锚点

M0.4 对象存储 + 向量库（同时验证 M2.3 的 Embedding 前提）。

### 前置依赖

Docker；代理（拉镜像 / 模型时可能需要）。

### 具体执行步骤（概要）

1. 建数据目录、`.env`、compose → `docker compose up -d`。
2. 控制台建 bucket（或脚本建）。
3. 安装 Ollama、拉 bge-m3、curl 验证。
4. 写并运行 smoke.py → 提交。

### 验收标准

- [ ] `docker compose ps` 两个服务 running；`http://localhost:9001`、`http://localhost:6333/dashboard` 可打开
- [ ] curl embeddings 返回长度 1024 的向量
- [ ] smoke.py 输出 sha256 一致 + top-1 命中预期

### 完成后的产出

`~/lab/projects/infra/compose/docker-compose.yml`、`~/lab/projects/.gitignore`、`~/lab/projects/ai-lab/storage-smoke/{smoke.py,README.md}`

### 求职映射

Vector DB / Embedding / S3 —— RAG 岗位必备。

### 如果时间不够 / 没有必要

最低：Qdrant + bge-m3 部分；MinIO 部分顺延到 Day10 前 20 分钟。

---

## Task 5：备份恢复 + 痛点分类 + 周复盘（Day10 · 10-07）

### 做什么

写 `infra/scripts/backup.sh`（停容器 → tar 打包 Gitea / Qdrant / MinIO 数据 → 启动 → 保留最近 7 份）与 `restore.sh`（停 → 当前数据改名留底 → 解包 → 启动 → 健康验证）；演练：删 smoke collection、一个 MinIO 对象、test-repo → 恢复 → 验证并记录耗时；痛点池补到 ≥ 10 条、加「初评分」列；Week 2 复盘。

### 为什么做

从本周起 Gitea / MinIO / Qdrant 承载真实资产；没演练过的备份等于没有备份（蓝图 §11 运维指标：恢复 < 30 分钟）。痛点池是 Day13 选型输入。

### 资产锚点

M0.5 备份 / 恢复；M10 痛点分类。

### 前置依赖

Task 4（compose 与数据目录）；Day03 痛点池。

### 具体执行步骤（概要）

1. 写两个脚本，`bash -n` 语法检查。
2. 先备份 → 删除三项 → 恢复 → 验证 → 记录 `backup-drill.md`。
3. 复制一份到离线位置（外置盘 / iCloud）。
4. 痛点池补齐 + 加列；周复盘。

### 验收标准

- [ ] `~/lab-backups/<时间戳>/` 含 3 个 tar.gz + SHA256SUMS
- [ ] 删除的三项全部恢复，耗时已记录
- [ ] 痛点池 ≥ 10 条、类型全填、有初评分列
- [ ] Week 02 README §7、§11 已填

### 完成后的产出

`~/lab/projects/infra/scripts/{backup.sh,restore.sh}`、`~/lab/projects/infra/backup-drill.md`、更新后的 `product-lab/pain-pool.md`

### 求职映射

运维与可靠性意识（RTO / 备份校验），AI Platform / 全栈岗面试加分。

### 如果时间不够 / 没有必要

最低：backup.sh + 恢复 Qdrant 一项；完整三项演练放 W7 Day29（云端演练）前补。

---
