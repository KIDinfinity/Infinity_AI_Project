# Day 26 · 2026-10-23 · Week 07 Task 1：Dockerfile + compose 全栈

## 0. 今天只做一件事

写出 api / web 两个 Dockerfile、Caddyfile 和 dev compose，让 `make up` 一条命令在本机起 api + web(Caddy) + qdrant + minio，浏览器 http://localhost:8080 完成上传 → 流式问答。

不碰：云服务器（Day28）、JSON 日志 / `/ready`（Day27）、CI（Day29）、镜像推送到 Registry、K8s。

## 1. 资产锚点

- 构建模块：M5.1 Dockerfile（api 多阶段 / web 静态）+ compose（dev）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make up` → 4 个容器 healthy → localhost:8080 全流程可用；api 镜像大小 \_\_\_\_MB、非 root
- 今日 AI 实际应用：RAG 服务的「可交付形态」——Embedding 仍走本机 Ollama（`host.docker.internal`），向量库 / 对象存储在容器内，为 Day28 切换 SiliconFlow 同模型做好配置抽象

## 2. 起点（前置确认）

- 已有：v0.4.0；infra 中的 MinIO / Qdrant（本次 compose 起**独立的一套**，不暴露端口，不与 infra 冲突）。
- 需确认：

```bash
cd ~/lab/workpilot
git ls-files apps/api/uv.lock apps/web/pnpm-lock.yaml     # 两个锁文件都必须已提交
grep -rn "prompts" apps/api/app --include=*.py | head     # prompts 目录如何定位？需能被 PROMPTS_DIR 覆盖
grep -n "url\|endpoint\|database" apps/api/app/core/config.py   # 记下 Qdrant/MinIO/Embedding/DB 的环境变量名
docker version --format '{{.Server.Version}}' && docker compose version
pnpm -v      # 记下版本，Step 3 用 corepack 固定
```

下面 compose 中的变量名（`QDRANT_URL` / `MINIO_ENDPOINT` / `EMBEDDING_BASE_URL` / `DATABASE_URL` / `PROMPTS_DIR`）为示意，**一律改成你 config.py 里的真实名字**。

## 3. 验收对齐（做完要能勾掉）

- [ ] `make up` 成功；`make ps` 显示 api / qdrant / minio 为 healthy，web 为 running
- [ ] http://localhost:8080 上传样例 md → ready → 流式问答（逐字）带引用
- [ ] 直接访问 http://localhost:8080/kb 并刷新，不出现 404
- [ ] `docker compose -p workpilot exec api id` 显示 `uid=10001(app)`（非 root）
- [ ] `make down && make up` 后会话历史与文档仍在
- [ ] 镜像中不含 `.env`：`docker compose -p workpilot exec api ls -a /app | grep -c '^.env$'` 输出 0
- [ ] 已 commit + push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                   |
| ------- | ------ | ------------------------------------------------------ |
| 0–10    | P0     | 前置确认，记录变量名                                   |
| 10–35   | P0     | api Dockerfile + `.dockerignore`，单独 build 验证      |
| 35–55   | P0     | web Dockerfile + Caddyfile                             |
| 55–85   | P0     | compose + Makefile，`make up` 排错到全绿               |
| 85–105  | P0     | 浏览器全流程 + 持久化验证 + 提交                       |
| 105–115 | P1     | `data/sample` + `scripts/seed_sample.sh` + `make seed` |
| 115–120 | P2     | 记录镜像大小，尝试 BuildKit cache mount                |

时间不足时最低保留：api + web + qdrant + minio 能起，浏览器能问答一次。

## 5. 今日学习（只学完成任务必须的）

- 多阶段构建：builder 阶段装依赖 / 编译，runtime 阶段只拷贝产物（`.venv`、`dist`），镜像小、攻击面小。
- uv 官方 Docker 模式：先只拷 `pyproject.toml` + `uv.lock` 装依赖（利用层缓存），再拷源码；`--frozen` 保证与锁文件一致。
- Compose `healthcheck` + `depends_on.condition: service_healthy`：等依赖真正可用再启动，而不是只等容器启动。
- Caddy：`reverse_proxy` + `flush_interval -1` 让 SSE 立即下发；`try_files {path} /index.html` 支持 SPA 路由。
- 资料：https://docs.astral.sh/uv/guides/integration/docker/ 、https://docs.docker.com/build/building/multi-stage/ 、https://docs.docker.com/compose/how-tos/startup-order/ 、https://caddyserver.com/docs/caddyfile/directives/reverse_proxy 、https://caddyserver.com/docs/caddyfile/directives/try_files

## 6. 执行步骤

### Step 1 · 仓库根 `.dockerignore`（构建上下文 = 仓库根，因为 api 需要根目录的 `prompts/`）

```text
**/.git
**/node_modules
**/.venv
**/__pycache__
**/.pytest_cache
**/.ruff_cache
**/dist
**/*.db
.env
.env.*
!.env.example
data/
apps/api/data/
eval/
docs/
```

### Step 2 · apps/api/Dockerfile（按 uv 官方指南改写；理解每一层再让 AI 补注释）

```dockerfile
# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
# 1) 只用锁文件装第三方依赖：源码改动不会使这一层失效
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=apps/api/uv.lock,target=uv.lock \
    --mount=type=bind,source=apps/api/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
# 2) 再拷源码并安装项目本身
COPY apps/api/ /app/
COPY prompts/ /app/prompts/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# runtime 与 builder 同为 Debian bookworm + /usr/local/bin/python3.12，.venv 里的解释器软链才有效
FROM python:3.12-slim-bookworm AS runtime
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /app --no-create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
RUN mkdir -p /app/data && chown app:app /app/data
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PROMPTS_DIR=/app/prompts
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
```

```bash
docker build -f apps/api/Dockerfile -t workpilot-api:dev .
docker image ls workpilot-api:dev            # 记录大小
docker run --rm workpilot-api:dev id         # uid=10001(app)
```

### Step 3 · apps/web/Dockerfile + deploy/Caddyfile

先固定 pnpm 版本（写入 `package.json` 的 `packageManager` 字段，容器内 corepack 据此安装同版本）：`cd apps/web && corepack use pnpm@<本机版本>`。

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /app
RUN npm i -g corepack@latest && corepack enable
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY apps/web/ ./
RUN pnpm build

FROM caddy:2-alpine
COPY --from=build /app/dist /srv
COPY deploy/Caddyfile /etc/caddy/Caddyfile
```

> Node 20 已于 2026-04 结束维护；若本机是 22，基础镜像改为 `node:22-alpine`，与本机主版本一致即可。

`deploy/Caddyfile`（dev，Tab 缩进）：

```caddyfile
:80 {
	handle /v1/* {
		reverse_proxy api:8000 {
			flush_interval -1    # SSE：每个 token 立即下发，不缓冲
		}
	}
	handle /health {
		reverse_proxy api:8000
	}
	handle {
		root * /srv
		encode gzip            # 只压缩静态资源，不作用于 SSE
		try_files {path} /index.html
		file_server
	}
}
```

### Step 4 · deploy/docker-compose.yml

```yaml
name: workpilot

services:
  api:
    build: { context: .., dockerfile: apps/api/Dockerfile }
    env_file: ../.env # 密钥；下面 environment 覆盖容器内地址
    environment:
      APP_ENV: dev
      DATABASE_URL: sqlite:////app/data/workpilot.db
      QDRANT_URL: http://qdrant:6333
      MINIO_ENDPOINT: minio:9000
      EMBEDDING_BASE_URL: http://host.docker.internal:11434/v1 # Mac 上的 Ollama；若用原生 API 去掉 /v1
    volumes: [api-data:/app/data]
    depends_on:
      qdrant: { condition: service_healthy }
      minio: { condition: service_healthy }
    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)",
        ]
      interval: 10s
      timeout: 5s
      retries: 6
      start_period: 20s
    restart: unless-stopped

  web:
    build: { context: .., dockerfile: apps/web/Dockerfile }
    ports: ["8080:80"]
    volumes: [./Caddyfile:/etc/caddy/Caddyfile:ro]
    depends_on:
      api: { condition: service_healthy }
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest # 改成与 infra 相同的固定 tag：快照恢复要求版本兼容
    volumes: [qdrant-data:/qdrant/storage]
    healthcheck: # 镜像内没有 curl/wget，用 bash 探测端口
      test: ["CMD-SHELL", "bash -c ':> /dev/tcp/127.0.0.1/6333' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 6
    restart: unless-stopped

  minio:
    image: minio/minio:latest # 改成与 infra 相同的固定 tag
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes: [minio-data:/data]
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
      timeout: 5s
      retries: 6
    restart: unless-stopped

volumes:
  api-data:
  qdrant-data:
  minio-data:
```

`.env.example` 补上 `MINIO_ROOT_USER=`、`MINIO_ROOT_PASSWORD=`（无值），并确认 api 用的 MinIO access/secret 与之对应。

### Step 5 · Makefile（`--env-file .env` 让 `${MINIO_ROOT_USER}` 从仓库根 .env 插值；recipe 行必须 Tab）

```makefile
PROJECT ?= workpilot
COMPOSE := docker compose -p $(PROJECT) --env-file .env -f deploy/docker-compose.yml
BASE ?= http://localhost:8080

.PHONY: up down logs ps seed
up:
	$(COMPOSE) up -d --build
down:
	$(COMPOSE) down
logs:
	$(COMPOSE) logs -f --tail=100
ps:
	$(COMPOSE) ps
seed:
	BASE=$(BASE) ./scripts/seed_sample.sh
```

```bash
make up && make ps
curl -s localhost:8080/health
curl -N -X POST localhost:8080/v1/kb/ask/stream -H 'Content-Type: application/json' -d '{"question":"测试"}' | head -5
```

注意：容器内是**一套新的空 Qdrant / MinIO**，需要重新导入（Step 6），这是预期行为。

### Step 6 · P1：公开样例语料 + 一键导入

- `data/sample/`：5–8 篇**可公开**的 md（自己写的 WorkPilot 使用说明、架构说明 + 少量 MIT 许可的开源文档节选），`data/sample/SOURCES.md` 写来源与许可。今后 Demo、云端、干净环境恢复都只用它。
- `.gitignore`：把原来的 `data/` 改为 `/data/*` + `!/data/sample/`（父目录被整体忽略时，子目录的 `!` 规则不生效）。

```bash
#!/usr/bin/env bash
# scripts/seed_sample.sh — 批量上传 data/sample/*.md；云端：BASE=https://域名 BASIC_AUTH=user:pass
set -euo pipefail
BASE="${BASE:-http://localhost:8080}"
for f in data/sample/*.md; do
  [[ "$(basename "$f")" == "SOURCES.md" ]] && continue
  echo "upload $f"
  curl -sfS ${BASIC_AUTH:+-u "$BASIC_AUTH"} -F "file=@${f}" "$BASE/v1/kb/upload"; echo
done
```

```bash
chmod +x scripts/seed_sample.sh && make seed
```

### Step 7 · 提交

```bash
git add .dockerignore .gitignore Makefile apps/api/Dockerfile apps/web/Dockerfile apps/web/package.json \
        deploy/ data/sample scripts/seed_sample.sh .env.example
git status    # 再次确认没有 .env、*.db
git commit -m "build: dockerize api and web, add compose stack with caddy and healthchecks"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么先 bind 锁文件 `uv sync --no-install-project`，再 COPY 源码？（答：依赖层只在锁文件变化时重建，改业务代码只重建最后几层，构建快很多）
2. 为什么 runtime 用 `python:3.12-slim-bookworm` 而不是任意 slim？（答：`.venv` 里的 python 是指向 `/usr/local/bin/python3.12` 的软链，需与 builder 的发行版 / 路径一致）
3. 容器里为什么用 `qdrant:6333` 而不是 `localhost:6333`？（答：每个容器有自己的 localhost；compose 默认网络用服务名做 DNS）
4. `depends_on` 不加 `condition: service_healthy` 会怎样？（答：只等容器进程启动，api 可能在 Qdrant 尚未就绪时连接失败）
5. 为什么 SPA 需要 `try_files {path} /index.html`？（答：`/kb` 是前端路由，服务器上没有该文件，需回退到 index.html 交给 react-router）

## 8. 对 DA-01 的贡献

F8「`docker compose up -d` 一键部署」的 dev 版落地。WorkPilot 第一次与「我的 Mac 环境」解耦：任何人有 Docker 就能跑，这是云部署、CI、W8 干净环境恢复、W22 Pro Kit 部署包的共同基础。

## 9. 求职映射（D 线）

- 岗位能力：Docker 多阶段构建、Compose 编排、反向代理
- 对应岗位：AI Engineer / AI Platform Engineer / Full-Stack
- 简历 bullet 草稿：基于 uv 多阶段构建 FastAPI 镜像（\_\_MB，非 root 运行），以 Docker Compose 编排 API / Web / Qdrant / MinIO 并配置健康检查依赖，Caddy 统一反代与 SPA 托管，`make up` 一键启动全栈。
- 面试可能问：
  - 「怎么减小 Python 镜像体积？」要点：多阶段、slim 基础镜像、`--no-dev`、`.dockerignore`、不带编译工具链进 runtime。
  - 「SSE 经过反向代理为什么会卡住？」要点：代理缓冲；Caddy `flush_interval -1`、Nginx `proxy_buffering off`；压缩中间件也可能缓冲。

## 10. 卡住时的处理

| 现象                                                              | 处理                                                                             |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `error: Unable to find lockfile at uv.lock` / `--frozen` 失败     | 在 `apps/api` 执行 `uv lock` 并提交 `uv.lock`                                    |
| api 容器 `exec /app/.venv/bin/uvicorn: no such file or directory` | builder 与 runtime 的 Python 路径不一致：两者都用 bookworm 的 3.12 镜像          |
| `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH` / lockfile 版本不兼容         | 容器内 pnpm 版本与本机不同：`corepack use pnpm@<本机版本>` 写入 `packageManager` |
| `Cannot find matching keyid` / corepack 签名错误                  | 已在 Dockerfile 中 `npm i -g corepack@latest`；本机同样执行一次                  |
| api 一直 unhealthy，日志连接 `host.docker.internal:11434` 失败    | 确认 Mac 上 `ollama serve` 运行、`curl localhost:11434/api/tags` 有 bge-m3       |
| 拉 `ghcr.io` / Docker Hub 镜像超时                                | 按 Day01 方式给 Docker Desktop 配代理（Settings → Resources → Proxies）          |

## 11. 产出记录（执行时填写）

- api 镜像大小 / web 镜像大小：\_**\_ / \_\_**
- `make up` 冷启动到全部 healthy 用时：\_\_\_\_ s
- 样例语料篇数 / 导入耗时：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day27（配置 / 健康检查 / JSON 日志 / request_id）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
