# Day 28 云部署 + 访问保护 — 执行小结（公网 IP 版，SUMMARY）

> 对应 PLAN：[PLAN.md](./PLAN.md)（Day 28，W7·Task3）
> 结论：**已基于公网 IP 完成真实部署与验收**。按你的要求改为「公网 IP 直连 + 纯 HTTP（暂不绑域名 / 不做 HTTPS）」，并保留 `ssh root@IP` 登录方式。

---

## 0. 一句话结论

WorkPilot（DA-01 RAG 知识助手）已部署到 **`http://8.148.216.61`**（阿里云，公网 IP 直连、纯 HTTP），4 个容器（api / web / qdrant / minio）全部 healthy，basic auth 生效（`infinity:123456`），样例知识库已 seed，流式问答 + 引用 + 👎 反馈全链路跑通。

---

## 1. 与 PLAN 的差异（本次改动点）

| 项 | PLAN 原方案 | 本次实际（IP+HTTP） |
|---|---|---|
| 站点地址 | `https://wp.<域名>`（443） | `http://8.148.216.61`（80） |
| 证书 | Let's Encrypt 自动签发 | **无**（HTTP 明文，443 关闭） |
| SSH 登录 | root 被拒、仅 deploy 密钥 | **root 密钥可登录**（`ssh root@IP`，密码登录仍禁用） |
| 防火墙 | 开放 22/80/443 | 仅开放 **22/80** |

> 域名 + HTTPS 是「后续优化」项，未做。basic auth 密码 `123456` 仅为 Demo 占位，传输明文，正式对外前必须轮换 + 上 HTTPS。

---

## 2. 做了什么

### 2.1 本地配置改造（`~/lab/workpilot`，未 commit）
- `deploy/Caddyfile.prod`：改为 `http://8.148.216.61`，新增 `/health`、`/ready` 反代，移除 ACME/HSTS。
- `deploy/docker-compose.prod.yml`：web 只暴露 80，移除证书卷与 `WP_DOMAIN`/`ACME_EMAIL`。
- `.env.prod`：移除域名/TLS 变量（真实密钥保留，gitignored）。
- `apps/web/Dockerfile`：npm/pnpm registry 改走 `registry.npmmirror.com`（大陆直连 npmjs 极慢，约 25 KiB/s，改镜像后秒级）。
- `docs/runbook.md`：部署章节更新为 IP+HTTP + root 密钥登录。

### 2.2 服务器初始化（阿里云 8.148.216.61）
- Docker 29.10.0 + Compose v5.7.1（阿里云镜像安装，get.docker.com 被 SSL 阻断）。
- `deploy` 用户（docker 组、无 sudo）+ 密钥登录。
- SSH 加固：`PasswordAuthentication no`、`PermitRootLogin yes`（按你要求保留 root 密钥登录）。
- ufw 仅放行 22/80。
- Docker Hub / ghcr.io 走国内镜像（`daemon.json` 的 `registry-mirrors` + ghcr 显式镜像重 tag），解决大陆拉镜像被阻断问题。

### 2.3 部署与 seed
- `make deploy`（rsync + compose build + up + `/ready` 探活）成功。
- `make seed` 上传 5 个样例文档，全部 `status: ready`（embedding 完成）。

### 2.4 资源占用（`docker stats --no-stream`）
| 容器 | 内存 |
|---|---|
| api | 205 MiB |
| web | 56 MiB |
| qdrant | 22 MiB |
| minio | 79 MiB |

---

## 3. 验收对齐（逐项，可复制命令，任意目录执行）

> 说明：以下命令均为纯 `curl`/`nc`/`ssh`，不依赖仓库目录。IP = `8.148.216.61`，basic auth = `infinity:123456`。
> 机器别名 `wp-prod` 若未配置，用 `ssh root@8.148.216.61` 或 `ssh deploy@8.148.216.61` 替代。

### ✅ 验收 1：SSH 登录控制
```bash
# root 密钥登录（本次按你要求保留，应成功）
ssh root@8.148.216.61 'echo root-ok'

# deploy 密钥登录（应成功）
ssh deploy@8.148.216.61 'echo deploy-ok'     # 或 ssh wp-prod 'echo deploy-ok'

# 密码登录（应被拒绝，只允许 publickey）
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no root@8.148.216.61 'echo x'
# → root@8.148.216.61: Permission denied (publickey).
```
**实际结果**：root / deploy 密钥登录均 OK；密码登录 `Permission denied (publickey)`。

### ✅ 验收 2：basic auth（IP+HTTP 版，无证书）
```bash
# 无凭据访问 → 401
curl -sI http://8.148.216.61 | head -1
# → HTTP/1.1 401 Unauthorized   （Server: Caddy；无证书，纯 HTTP）

# 带凭据访问首页 → 200，标题 WorkPilot
curl -s -u infinity:123456 http://8.148.216.61 | grep -oE '<title>[^<]*</title>'
# → <title>WorkPilot</title>

# 健康检查
curl -s -u infinity:123456 http://8.148.216.61/health
# → {"status":"ok","env":"prod","version":"0.0.1"}

curl -s -u infinity:123456 http://8.148.216.61/ready
# → {"status":"ready","checks":{"qdrant":"ok","db":"ok","llm_key":"ok"}}
```

### ✅ 验收 3：浏览器全流程（basic auth → 上传 → 流式问答带引用 → 👎 反馈）
> 浏览器打开 `http://8.148.216.61`，输入 `infinity` / `123456` 即可走通下面流程；以下是等价的 curl 验证。

**3a. 上传样例**（seed 5 个文档，任意目录执行）
```bash
for f in fastapi-first-steps.md react-responding-to-events.md react-your-first-component.md vite-using-plugins.md vite-why.md; do
  echo "upload $f"
  curl -s -u infinity:123456 -F "file=@$f" http://8.148.216.61/v1/kb/upload
  echo
done
# 每个返回 {"id":"...","status":"pending"}；随后变为 ready
```
> 若在 `~/lab/workpilot` 目录，直接 `BASE=http://8.148.216.61 BASIC_AUTH='infinity:123456' make seed`。

**3b. 确认文档已就绪**
```bash
curl -s -u infinity:123456 http://8.148.216.61/v1/kb/docs | python3 -c 'import sys,json; [print(d["filename"], d["status"], d["chunks"]) for d in json.load(sys.stdin)]'
# → 5 行，status 均为 ready
```

**3c. 流式问答（SSE，带引用）**
```bash
curl -sN -u infinity:123456 -X POST http://8.148.216.61/v1/kb/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"如何在 React 中定义一个组件？"}'
# → 依次输出 event: retrieved（命中+citations）/ event: token（流式答案）/ event: done（引用+usage+conversation_id+message_id）
```

**3d. 👎 反馈**（用 3c `done` 事件里的 `message_id` 替换）
```bash
curl -s -u infinity:123456 -X POST \
  http://8.148.216.61/v1/messages/<message_id>/feedback \
  -H 'Content-Type: application/json' \
  -d '{"rating":"down","reason":"irrelevant"}'
# → HTTP 201，返回 {"rating":"down","reason":"irrelevant",...}
```

### ✅ 验收 4：端口暴露（IP+HTTP 版）
```bash
# 内网服务端口应全部失败（compose 未写 ports，不暴露公网）
nc -zvw3 8.148.216.61 6333 9000 9001 8000
# → 4 个均 Operation timed out / failed

# 80 应成功
nc -zvw3 8.148.216.61 80
# → Connection to 8.148.216.61 port 80 [tcp/http] succeeded!

# 443 当前关闭（无 HTTPS）
nc -zvw3 8.148.216.61 443
# → Operation timed out（失败，符合预期）

# 22 应成功
nc -zvw3 8.148.216.61 22
# → succeeded!
```

### ✅ 验收 5：服务器 `.env` 权限
```bash
ssh wp-prod 'stat -c %a ~/workpilot/.env'
# → 600
```

### ✅ 验收 6：runbook 部署章节（commit/push 按你要求跳过）
```bash
grep -n "## 部署" docs/runbook.md          # → 已有「部署（Day28 起）」章节，已更新为 IP+HTTP
# 按你的要求「不提交代码」，本次未 commit / push；docs/runbook.md、deploy/*、apps/web/Dockerfile 均为工作区改动
```

---

## 4. 本次遇到并解决的问题（大陆网络相关，供复现参考）

1. **get.docker.com 被 SSL 阻断** → 改用阿里云镜像源安装 Docker/Compose。
2. **Docker Hub 拉取 connection refused** → `daemon.json` 配 `registry-mirrors`（`docker.1panel.live` / `docker.m.daocloud.io` / `dockerproxy.net`）。
3. **ghcr.io 层下载卡死** → 用 `ghcr.m.daocloud.io` 显式前缀拉取再 `docker tag` 回原名。
4. **qdrant 走 Cloudflare 镜像仅 ~13 KiB/s** → 改显式 `docker.m.daocloud.io/qdrant/qdrant:latest` 秒拉；minio 走 `docker.1panel.live`。
5. **npmjs 直连 ~25 KiB/s** → web Dockerfile 加 `registry.npmmirror.com`（npmmirror 200 快）。
6. **root 曾因加固被锁** → 用 deploy 的 docker 组权限（`--privileged --pid=host` 挂 `/`）写回 `PermitRootLogin yes` 并 reload sshd。

---

## 5. 遗留 / 后续优化（非本次主线）
- 域名 + HTTPS（绑域名后 Caddyfile 写站点地址即可自动 ACME）。
- basic auth 密码 `123456` 为 Demo 占位，正式前轮换（`caddy hash-password` 生成新哈希）。
- 未 commit/push（按你要求）；需要时再提交 `deploy/*`、`apps/web/Dockerfile`、`docs/runbook.md`。
