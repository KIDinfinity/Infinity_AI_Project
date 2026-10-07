# Week 07 · TASKS

## Task 1：Dockerfile + compose 全栈（Day26 · 11-09）

### 做什么

`apps/api/Dockerfile`（builder：`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`，`uv sync --frozen --no-dev`；runtime：`python:3.12-slim-bookworm` 拷贝 `.venv`，非 root，uvicorn）+ 仓库根 `.dockerignore`；`apps/web/Dockerfile`（node:20-alpine + corepack pnpm 构建 → caddy:2-alpine 托管 dist）；`deploy/Caddyfile`（`/v1/*` 反代 api:8000 且 `flush_interval -1`，其余 `try_files {path} /index.html`）；`deploy/docker-compose.yml`（api / web / qdrant / minio，volumes，env_file，healthcheck + `depends_on: condition`，embedding 走 `host.docker.internal:11434`）；Makefile `up/down/logs`；`data/sample` + `seed_sample.sh`。

### 为什么做

容器化是云部署、CI、干净环境恢复的共同前提；Caddy 同时解决 SPA 路由回退、SSE 不缓冲、同源免 CORS。

### 资产锚点

M5.1 · 为 v0.5 做准备

### 前置依赖

v0.4.0；`apps/api/uv.lock` 已提交；`apps/web/pnpm-lock.yaml` 已提交；Ollama bge-m3 在 Mac 上运行。

### 具体执行步骤（概要，详见 day26 PLAN.md）

1. 确认锁文件、配置项名（数据库路径、prompts 路径、Qdrant / MinIO / Embedding 地址）可用环境变量覆盖。
2. api Dockerfile + `.dockerignore`，单独 `docker build` 验证。
3. web Dockerfile + Caddyfile。
4. compose + Makefile；`make up`。
5. `data/sample` + seed；浏览器全流程；提交。

### 验收标准

- [ ] `make up` 后 `make ps` 四个服务均 healthy / running
- [ ] http://localhost:8080 上传 sample → ready → 流式问答带引用；刷新 `/kb` 不 404
- [ ] `docker compose exec api id` 显示非 root
- [ ] `make down && make up` 后会话历史与文档仍在（volume 持久化）

### 完成后的产出（文件路径）

`apps/api/Dockerfile`、`apps/web/Dockerfile`、`.dockerignore`、`deploy/Caddyfile`、`deploy/docker-compose.yml`、`Makefile`、`data/sample/`、`scripts/seed_sample.sh`

### 求职映射

「多阶段构建、非 root、健康检查编排、反向代理与 SSE」。

### 如果时间不够 / 没有必要

构建缓存优化、镜像瘦身、`seed` 脚本 → P2（手动在页面上传即可）。

---

## Task 2：配置 / 健康检查 / JSON 日志 / request_id（Day27 · 11-10）

### 做什么

Settings 必填项启动即校验（fail fast），`APP_ENV=dev|prod` 且 prod 有额外约束；`/health`（存活）与 `/ready`（Qdrant、DB、LLM key 存在）分离并返回 JSON 明细；JSON 日志 + 中间件生成 / 透传 `X-Request-ID`（contextvars），每行日志带 request_id，响应头回传，访问日志含 method / path / status / latency；全局异常处理统一 `{"error":{"code","message","request_id"}}`，不泄漏堆栈与密钥。

### 为什么做

上云后看不到终端，日志和健康检查是唯一的眼睛；统一错误体让前端、CI、未来的 MCP 客户端都能稳定处理错误。

### 资产锚点

M5.2 M9.1 · 为 v0.5 做准备

### 前置依赖

Task 1 完成（compose 可用，便于验证 /ready 失败场景）。

### 具体执行步骤（概要，详见 day27 PLAN.md）

1. `config.py`：必填项 + SecretStr + prod 校验。
2. `core/logging.py`：JsonFormatter + RequestIdFilter。
3. `core/middleware.py`：request_id + 访问日志 + 兜底 500。
4. `core/errors.py`：HTTPException / 校验错误统一格式。
5. `routes/health.py`：/health /ready；pytest；提交。

### 验收标准

- [ ] 删掉 `.env` 中 `LLM_API_KEY` → `make up` 后 api 容器退出，日志指明字段
- [ ] `curl -i localhost:8080/v1/kb/docs` 响应头有 `X-Request-ID`；日志同 id
- [ ] 传入 `X-Request-ID: abc'"\n` 被替换为新 id（防日志注入）
- [ ] `docker compose stop qdrant` 后 `/ready` 返回 503，`checks.qdrant` 为 fail
- [ ] 触发 500 时响应体无 Traceback

### 完成后的产出（文件路径）

`apps/api/app/core/{config,logging,middleware,errors}.py`、`app/routes/health.py`、`tests/test_observability.py`、`.env.example`

### 求职映射

「可观测性基础：结构化日志、请求追踪、健康检查分层」。

### 如果时间不够 / 没有必要

日志采样、日志轮转、OpenTelemetry → 不做（W15 自研轻量 trace）。

---

## Task 3：云部署 + HTTPS + 访问保护（Day28 · 11-11）

### 做什么

对比方案 A 轻量服务器（推荐）/ B Cloudflare Tunnel；服务器初始化（SSH key、禁用密码登录、ufw 22/80/443、get.docker.com、deploy 用户）；域名 + A 记录；`deploy/docker-compose.prod.yml`（不暴露 qdrant / minio 端口，Caddy 域名自动 HTTPS，`basic_auth` 保护，embedding 切 SiliconFlow `BAAI/bge-m3`）；`deploy/scripts/deploy.sh`（rsync 排除 .env / data / node_modules / .venv → 远端 `up -d --build`）；服务器 `.env` chmod 600；云端只导入公开 / 脱敏样例。

### 为什么做

P1 验收「公网可访问、可演示」；也是面试中「你的项目在哪能看」的直接答案。

### 资产锚点

M5.3 · 为 v0.5 做准备

### 前置依赖

Task 1–2 完成；已购买 2C4G 香港 / 新加坡轻量服务器与域名；SiliconFlow API key。

### 具体执行步骤（概要，详见 day28 PLAN.md）

1. 选 A / B，记录理由。
2. 服务器初始化与加固（先验证 key 登录再禁密码）。
3. DNS A 记录；`Caddyfile.prod` + `docker-compose.prod.yml`。
4. `deploy.sh` + 服务器 `.env`。
5. 部署 → seed 样例 → 验证证书 / 401 / 问答。

### 验收标准

- [ ] `curl -I https://<域名>` 返回 401，证书由 Let's Encrypt / ZeroSSL 签发
- [ ] 带凭据可流式问答且引用样例文档
- [ ] 服务器外部扫描仅 22/80/443 开放；qdrant / minio 无公网端口
- [ ] `ssh root@<IP>` 与密码登录均被拒

### 完成后的产出（文件路径）

`deploy/docker-compose.prod.yml`、`deploy/Caddyfile.prod`、`deploy/scripts/deploy.sh`、`docs/runbook.md`（部署章节）

### 求职映射

「Linux 服务器加固、HTTPS、最小暴露面、生产配置与开发配置分离」。

### 如果时间不够 / 没有必要

Fail2ban、自动安全更新、监控告警 → P2；CDN → 不做。

---

## Task 4：CI + 云端备份恢复演练（Day29 · 11-12）

### 做什么

确认 Gitea Actions 已启用；Docker 运行 `gitea/act_runner` 并用管理后台的 registration token 注册；`.gitea/workflows/ci.yml`：api（uv、`ruff check`、`pytest -m "not live"`）+ web（pnpm install、`tsc --noEmit`、`pnpm build`）。服务器 `deploy/scripts/backup.sh`：Qdrant snapshot API + SQLite 在线备份 + MinIO 数据 → tar → 保留 7 份；Mac 端拉回；crontab 每日。恢复演练：清空卷 → 恢复 → 问答验证，耗时写入 `docs/runbook.md`。Week 7 复盘。

### 为什么做

CI 是之后每次改动（W9 起加 Agent）的安全网；没演练过的备份等于没有备份。

### 资产锚点

M5.4 M5.5 · 为 v0.5 做准备

### 前置依赖

Task 3 完成（云端已运行）；pytest 已用 `live` 标记区分调用外部 API 的测试。

### 具体执行步骤（概要，详见 day29 PLAN.md）

1. 启用 Actions + 运行 act_runner + 注册。
2. 写 ci.yml，push，修到绿。
3. backup.sh / restore.sh；服务器跑一次；Mac 拉回。
4. 恢复演练计时；runbook；cron。
5. 周复盘；提交。

### 验收标准

- [ ] Gitea 仓库 Actions 页 main 最新一次 CI 绿色
- [ ] 服务器 `~/backups/` 有 tar 包，Mac `~/lab/backups/workpilot-cloud/` 有副本
- [ ] 演练：卷清空后问答失败 → 恢复后问答成功，耗时 \_\_\_\_ 分钟写入 runbook
- [ ] `crontab -l` 有每日备份任务

### 完成后的产出（文件路径）

`.gitea/workflows/ci.yml`、`deploy/scripts/{backup,restore}.sh`、`docs/runbook.md`

### 求职映射

「CI 门禁、RPO / RTO、恢复演练」。

### 如果时间不够 / 没有必要

CI 失败修不绿 → 记录原因，CONDITIONAL，W9 Day34 前 30 分钟补；Mac 端 launchd 定时拉取 → P2（手动拉即可）。

---
