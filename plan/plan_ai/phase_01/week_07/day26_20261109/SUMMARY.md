# Day 26 · Week 07 Task 1 · Dockerfile + compose 全栈 —— 执行总结

> 依据 [PLAN.md](./PLAN.md) 逐 Step 执行，最终状态：**Task 1 DONE**（§12 完成判定满足，除「commit + push」按用户要求跳过）。

## 一、做了什么（逐 Step 对应）

| Step | 结果 |
| --- | --- |
| Step 1 `.dockerignore` | 新建仓库根 `.dockerignore`（构建上下文 = 仓库根，含 `prompts/`），按 PLAN 原文 |
| Step 2 `apps/api/Dockerfile` | uv 多阶段构建：builder=`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`，runtime=`python:3.12-slim-bookworm`；先 bind 锁文件 `uv sync --no-install-project` 再 COPY 源码；uid 10001 非 root；`PROMPTS_DIR=/app/prompts`。**镜像 content size = 181MB** |
| Step 3 `apps/web/Dockerfile` | node:22-alpine `npm i -g pnpm@12.8.1` + `pnpm install --frozen-lockfile` + `vite build`；caddy:2-alpine 托管静态产物。**镜像 content size = 23.6MB** |
| Step 4 `deploy/Caddyfile` | `/v1/*` 反代 api（`flush_interval -1` 让 SSE 立即下发）、`/health` 反代、SPA `try_files {path} /index.html` + gzip |
| Step 5 `deploy/docker-compose.yml` | 重写为 api/web/qdrant/minio 四服务编排（`name: workpilot`），healthcheck + `depends_on.condition: service_healthy`，命名卷 api-data/qdrant-data/minio-data |
| Step 6 `Makefile` + `scripts/seed_sample.sh` | `COMPOSE` 带 `--env-file .env`、`PROJECT=workpilot`、`up -d --build`，新增 `ps`/`seed`；seed 脚本跳过 README.md/SOURCES.md |
| Step 7 提交 | **按用户要求未执行**（不 commit / push） |

### 附带修复（执行中暴露的既有问题）

- `apps/api/app/core/config.py` 的 `ROOT_DIR` 用 `parents[4]` 在容器内越界（源码在 `/app/app/...` 少一层）→ 改为按 parents 长度兜底，退到 `/app`。
- `apps/web/pnpm-lock.yaml` 缺失 Day25 新增的 5 个依赖（@playwright/test、@tailwindcss/typography、react-markdown、rehype-sanitize、remark-gfm）→ `pnpm install --lockfile-only` 补齐（+967 行），否则 `--frozen-lockfile` 失败。

## 二、与原 PLAN 的偏差

1. **corepack / packageManager 固定 pnpm** → 未用。pnpm 12 的 `packageManager` 字段会引入 `packageManagerDependencies`，`--frozen-lockfile` 时因锁文件未含该段直接失败，且官方锁文件会额外长出 ~1100 行 @pnpm/exe 多平台定义。改为 Dockerfile 内 `npm i -g pnpm@12.8.1`（与本机同版本）。
2. **MinIO 根账号变量** → 直接复用 `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`（与 api 配置同名），不新增 `MINIO_ROOT_USER`，避免两套凭据。
3. **config.py `ROOT_DIR`** → 容器内层级与仓库不同，加长度判断兜底（见上）。
4. **`deploy/docker-compose.yml` 原为 traefik/whoami 示例** → 整体替换为 workpilot 全栈。
5. **锁文件补齐** → 原锁文件与 package.json 不同步（Day25 遗留），需 `--lockfile-only` 才能冻结安装。

## 三、产出记录（PLAN §11）

- api 镜像 / web 镜像大小：**181MB / 23.6MB**（content size）
- `make up` 冷启动到全部 healthy 用时：**约 21s**（镜像已构建；首次全量构建约 45s）
- 样例语料篇数 / 导入耗时：**5 篇**，冷启动首次导入约 20–30s，Embedding 预热后单篇约 1s
- 卡点：pnpm lockfile 不同步、corepack/packageManager 冲突、config.py ROOT_DIR 容器内越界
- 用时：约 90 分钟

## 四、验收对齐（PLAN §3，7 条，命令均可在任意目录执行）

以下命令统一用 `cd ~/lab/workpilot` 开头（任意目录均可运行）；`make` 目标内部已固定 `-p workpilot --env-file .env -f deploy/docker-compose.yml`。

### 1. `make up` 成功；api/qdrant/minio healthy，web running

```bash
cd ~/lab/workpilot && make up && make ps
```
期望：api / minio / qdrant 均为 `(healthy)`，web 为 `Up`（`0.0.0.0:8080->80/tcp`）。

### 2. 上传样例 md → ready → 流式问答（逐字）带引用

```bash
cd ~/lab/workpilot && curl -s -F "file=@data/sample/vite-why.md" http://localhost:8080/v1/kb/upload
# 返回 {"id":"<DOC_ID>",...}，记下 DOC_ID
cd ~/lab/workpilot && curl -s http://localhost:8080/v1/kb/docs/<DOC_ID>
# 期望 status=ready，chunks>0
cd ~/lab/workpilot && curl -sN -X POST http://localhost:8080/v1/kb/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"为什么 Vite 打包很快？","top_k":3}'
```
期望：SSE 逐字输出 `retrieved` → 多个 `token` 事件 → `done`（`refused=false`，含 `citations`、`conversation_id`、`message_id`）。

### 3. 直接访问 /kb 并刷新，不 404

```bash
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' http://localhost:8080/kb
```
期望：`200 text/html`（SPA 回退到 index.html）。

### 4. api 容器非 root（uid=10001）

```bash
cd ~/lab/workpilot && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml exec api id
```
期望：`uid=10001(app) gid=10001(app)`。

### 5. `make down && make up` 后会话历史与文档仍在

```bash
cd ~/lab/workpilot && make down && make up && sleep 5
curl -s http://localhost:8080/v1/kb/docs | python3 -c 'import json,sys; print("docs:", len(json.load(sys.stdin)))'
curl -s http://localhost:8080/v1/conversations | python3 -c 'import json,sys; print("convs:", len(json.load(sys.stdin)))'
```
期望：docs 与 convs 数量在重启前后一致（命名卷持久化）。

### 6. 镜像中不含 `.env`

```bash
cd ~/lab/workpilot && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml exec api ls -a /app | grep -c '^.env$'
```
期望：输出 `0`。

### 7. 已 commit + push —— **按用户要求未执行**

> 用户明确要求「不提交代码」，故本条跳过；`git status` 仍保留 Day25/Day26 全部未提交改动（含新增的 `.dockerignore`、`apps/api/Dockerfile`、`apps/web/Dockerfile`、`deploy/Caddyfile`、`scripts/seed_sample.sh` 等），待用户后续决定是否提交。

## 五、概念自检（PLAN §7 答案摘要）

1. 先 bind 锁文件 sync → 依赖层只在锁文件变化时重建，改业务代码只重建最后几层。
2. runtime 与 builder 同为 bookworm 的 3.12 → `.venv` 中 python 软链指向 `/usr/local/bin/python3.12` 路径一致。
3. 用 `qdrant:6333` → 每个容器有自己的 localhost，compose 默认网络用服务名做 DNS。
4. 不加 `condition: service_healthy` → 只等容器进程启动，api 可能在 Qdrant 未就绪时连接失败。
5. SPA 需 `try_files {path} /index.html` → `/kb` 是前端路由，服务器无此文件，需回退给 react-router。

## 六、对 DA-01 的贡献（PLAN §8）

F8「`docker compose up -d` 一键部署」的 dev 版落地：WorkPilot 首次与「我的 Mac 环境」解耦，任何人有 Docker 即可 `make up` 跑起 RAG 全栈，为 Day28 云部署、CI、W8 干净环境恢复、W22 Pro Kit 部署包奠定基础。
