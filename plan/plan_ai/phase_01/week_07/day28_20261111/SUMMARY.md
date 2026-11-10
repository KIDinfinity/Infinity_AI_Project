# Day 28 云部署 + HTTPS + 访问保护 — 执行小结（SUMMARY）

> 对应 PLAN：[PLAN.md](./PLAN.md)（Day 28，W7·Task3）
> 结论：**纯本地能做的全部完成**；真正的「部署 + 验收」被外部资源阻断（无服务器 / 域名 / SiliconFlow key），等你补齐资源后按 §5 顺序执行即可。

---

## 0. 一句话结论

生产配置（HTTPS Caddyfile、prod compose、.env.prod、deploy.sh、Makefile、runbook）全部就绪并已通过本地校验；但云服务器、域名、SiliconFlow API Key 三个外部资源缺失，导致 PLAN 的 Step 2~7（真实部署与线上验收）无法在本地完成。下面给出：缺失资源的获取步骤 + 用途（§3）、完整可复制的验收命令（§4）、拿到资源后的操作顺序（§5）。

---

## 1. 做了什么（本地产出，全部在 `~/lab/workpilot`）

| 产出 | 路径 | 说明 |
|---|---|---|
| 生产 Caddyfile | `deploy/Caddyfile.prod` | HTTPS 自动证书 + basic auth + `/v1/*` SSE 反代 + 静态站 + HSTS/安全头 |
| 生产 Compose | `deploy/docker-compose.prod.yml` | api 用 SiliconFlow embedding；web 挂 80/443；qdrant/minio 不暴露端口；caddy 持久化卷 |
| 生产环境变量 | `.env.prod` | gitignored；已生成 MinIO 强凭据 + basic auth 哈希；`<...>` 占位待替换 |
| 部署脚本 | `deploy/scripts/deploy.sh` | rsync + ssh + compose up + `/ready` 探活（已 `chmod +x`，`bash -n` 通过） |
| Makefile | `Makefile` | 新增 `deploy:` 目标（`DEPLOY_HOST` 默认 `wp-prod`） |
| Runbook | `docs/runbook.md` | 新增「部署」章节：服务器信息 / 首次初始化清单 / 部署 / 日志 / 证书与 401 排障 / 轮换密码 |

**本地校验已通过**：`docker-compose.prod.yml` YAML 语法 OK；`deploy.sh` bash 语法 OK；`Caddyfile.prod` 缩进为 TAB（与 dev 一致）；`.env.prod` 确认被 `.gitignore` 忽略。

**未提交任何代码**（按你的要求）。

---

## 2. 没做 / 被阻断的（需要你补齐资源后才能做）

| PLAN 步骤 | 状态 | 阻断原因 |
|---|---|---|
| Step 1 生成密钥 + 配置 | ⏸ 本地可做，见 §5 | 依赖你要部署的服务器；密钥属于你的凭据，建议你亲手生成 |
| Step 2 服务器初始化 | ❌ 阻断 | 无服务器 IP |
| Step 3 域名 + 证书 | ❌ 阻断 | 无域名 |
| Step 4 SiliconFlow 接入 | ❌ 阻断 | 无 SiliconFlow Key |
| Step 5 deploy.sh 一键部署 | ❌ 阻断 | 无服务器 |
| Step 6 basic auth | ✅ 哈希已生成 | 密码 `ChangeMe_2026_Demo` 为占位，**部署前必须轮换** |
| Step 7 验收 | ❌ 阻断 | 无线上环境；§4 已给出完整命令，上线后逐条跑 |

---

## 3. 缺失资源的获取步骤 + 用途

### 3.1 云服务器（2C4G，Ubuntu 22.04/24.04）

- **用途**：7×24 运行 WorkPilot 的 api/web/caddy/qdrant/minio 五个容器，公网唯一入口。
- **获取步骤**：
  1. 选「轻量应用服务器」（腾讯云轻量 / 阿里云轻量 / UCloud 均可，香港或新加坡区免备案），2C4G，≤ 约 ¥100/月。
  2. 镜像选 Ubuntu 22.04 或 24.04（`get.docker.com` 脚本兼容）。
  3. 购买后在控制台「重置密码」拿到 root 密码，并记录**公网 IP**（即下文 `<IP>`）。
  4. 防火墙：只放行 TCP 22 / 80 / 443（443 也可放行 UDP，供 HTTP/3）。

### 3.2 域名（一个子域名 `wp` 即可）

- **用途**：Caddy 必须靠域名申请 Let's Encrypt/ZeroSSL 证书才能上 HTTPS；**纯 IP 无法申请证书**。
- **获取步骤**：
  1. 国内注册商（阿里云/腾讯云域名）约 ¥60/年，需实名认证（1~3 天）——若想当天能用，可选海外注册商（Namecheap / Cloudflare Registrar）免实名。
  2. 购买后在 DNS 控制台加一条 **A 记录**：主机记录 `wp`，指向服务器 IP，TTL 600。
  3. 验证生效：`dig +short wp.<域名>` 返回你的 IP 再继续（§5 第 5 步）。

### 3.3 SiliconFlow API Key（Embedding 用）

- **用途**：生产环境用 `BAAI/bge-m3`（1024 维）做向量化，与 dev 的 Ollama 同模型、保证检索行为一致；服务器 2C4G 不用跑大模型/GPU。
- **获取步骤**：
  1. 打开 <https://cloud.siliconflow.cn>（或 <https://siliconflow.cn>）注册/登录。
  2. 控制台 → API 密钥 → 新建，得到 `sk-...`。
  3. 模型选 `BAAI/bge-m3`，按量计费；首次导入几十篇文档成本极低（几分~几毛钱）。
  4. 填入 `.env.prod` 的 `EMBEDDING_API_KEY`。

### 3.4 LLM Key（已有，复用即可）

- dev 已经在用 DeepSeek，直接把 dev 的 `DEEPSEEK_API_KEY` 填进 `.env.prod`；无需新申请。

### 3.5 SSH 部署密钥（本地生成，非「获取」）

- 见 §5 第 1 步 `ssh-keygen`，在你自己 Mac 上生成，用于无密码登录服务器。

---

## 4. 验收对齐（逐条对应 PLAN §3，命令完整可复制）

> 统一占位符，执行前整体替换：
> - `<IP>` → 服务器公网 IP
> - `<域名>` → 你的域名，`wp.<域名>` 即完整站点地址
> - `<basic-user>` → `.env.prod` 里 `BASIC_AUTH_USER` 填的值
> - `<basic-pass>` → basic auth 密码（占位密码是 `ChangeMe_2026_Demo`，轮换后填新值）
> - 下面命令可在**任意目录**执行（全部绝对路径或带域名，不依赖 cwd）。

### 4.1 验收 1：SSH 硬化（root/密码被拒，密钥可登录）

```bash
# ① root 直连应被拒绝（期望：Permission denied / Connection refused，且不出现密码提示）
ssh -o BatchMode=yes -o ConnectTimeout=5 root@<IP> 'echo SHOULD_NOT_REACH'

# ② 密码登录应被禁用（期望：输出 no，看不到 yes）
ssh -o BatchMode=yes -o ConnectTimeout=5 deploy@<IP> \
  'sshd -T | grep -E "^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin)"'

# ③ 密钥登录应成功（期望：打印 Docker 版本，如 "Docker version 27.x.x"）
ssh -i ~/.ssh/workpilot_ed25519 deploy@<IP> docker version --format '{{.Server.Version}}'

# ③'（配置好 ~/.ssh/config 的 wp-prod 别名后，等价短写）
ssh wp-prod docker version --format '{{.Server.Version}}'
```

> 注意：① `root@<IP>` 用 `BatchMode=yes` 是为了「非交互、不弹密码、干净地失败」；真正验收「被拒绝」看它的非零退出码 + 无 shell 输出即可。

### 4.2 验收 2：HTTPS + 证书 + basic auth 401

```bash
# ① 未带凭据应返回 401（期望第一行：HTTP/2 401）
curl -sI https://wp.<域名> | head -1

# ② 证书由受信 CA 签发（期望：issuer 含 Let's Encrypt 或 ZeroSSL，且未出现 self-signed）
curl -vI https://wp.<域名> 2>&1 | grep -iE 'issuer:|subject:|expire date'

# ③ 带正确凭据应返回 200（期望第一行：HTTP/2 200）
curl -sI -u '<basic-user>:<basic-pass>' https://wp.<域名> | head -1

# ④ 带错误凭据应返回 401（期望第一行：HTTP/2 401）
curl -sI -u '<basic-user>:wrongpass' https://wp.<域名> | head -1
```

### 4.3 验收 3：上传样例 → ready → 流式问答带引用 → 👎 反馈

**（3a）后端可脚本化冒烟（用 curl 跑通「上传 → ready → 问答带引用」）：**

```bash
# ① 上传一个样例文件（期望：返回 {"id":"...","status":"pending"}）
curl -s -u '<basic-user>:<basic-pass>' -F 'file=@README.md;type=text/markdown' \
  https://wp.<域名>/v1/kb/upload

# ② 轮询直到 status=ready（期望：最新一条文档 status 变为 "ready"；替换 <doc-id> 为①返回的 id）
curl -s -u '<basic-user>:<basic-pass>' https://wp.<域名>/v1/kb/docs | python3 -m json.tool

# ③ 带引用问答（期望：answer 非空，且 citations 非空数组，字段含 chunk 引用）
curl -s -u '<basic-user>:<basic-pass>' -H 'Content-Type: application/json' \
  -d '{"question":"这个项目是做什么的？"}' \
  https://wp.<域名>/v1/kb/ask | python3 -m json.tool

# ④ 流式问答（期望：先见 event:retrieved，再见连续 event:token，最后 event:done 带 citations 与 message_id）
curl -sN -u '<basic-user>:<basic-pass>' -H 'Content-Type: application/json' \
  -d '{"question":"这个项目是做什么的？"}' \
  https://wp.<域名>/v1/kb/ask/stream

# ⑤ 👎 反馈（期望：返回 201，body.rating=="down"；<message-id> 取自④ done 事件里的 message_id）
curl -s -o /dev/null -w '%{http_code}\n' -u '<basic-user>:<basic-pass>' \
  -H 'Content-Type: application/json' \
  -d '{"rating":"down","reason":"wrong","comment":"冒烟验收"}' \
  https://wp.<域名>/v1/messages/<message-id>/feedback
```

**（3b）浏览器人工走查（👎 按钮的最终确认）：**

1. 浏览器开 `https://wp.<域名>` → 弹 basic auth → 输入 `<basic-user>` / `<basic-pass>`。
2. 上传样例文件 → 看到状态变「ready」。
3. 提问 → 看到**流式逐字输出** + 答案下方**带引用**。
4. 点「👎」→ 前端提示反馈成功（后端对应上面 ⑤，返回 201）。

### 4.4 验收 4：端口收敛（内部端口全关，仅 443 开）

```bash
# bash 内置 /dev/tcp 探测，macOS/Linux 通用（期望：6333/9000/9001/8000 全部「关闭」，443「开放」）
for p in 6333 9000 9001 8000 443; do
  (echo > /dev/tcp/<IP>/$p) >/dev/null 2>&1 && echo "$p 开放" || echo "$p 关闭"
done

# 等价 nc 版本（Linux netcat-openbsd 语法，即 PLAN 原文；macOS 的 nc 用 -G 3 而非 -w3）
nc -zvw3 <IP> 6333 9000 9001 8000   # 期望：全部 connection refused / timeout
nc -zvw3 <IP> 443                   # 期望：succeeded / open
```

### 4.5 验收 5：服务器 .env 权限 600

```bash
# 期望：输出 600
ssh wp-prod 'stat -c %a ~/workpilot/.env'
```

### 4.6 验收 6：runbook 有部署章节 + commit（不含密钥）

- ✅ `docs/runbook.md` 已写好「部署」章节（本地已完成）。
- ⏸ commit + push 留给你执行（你要求本次不提交）。提交前确认 `.env` / `.env.prod` 已被 gitignore 排除：
  ```bash
  cd ~/lab/workpilot
  git check-ignore .env.prod && echo "OK: .env.prod 被忽略"
  git status --short   # 应看不到任何 .env / 密钥文件
  ```

---

## 5. 拿到资源后的完整操作顺序（照做即可上线）

```bash
cd ~/lab/workpilot

# 1) 生成部署密钥（Mac，只做一次；回车用默认路径/空口令）
ssh-keygen -t ed25519 -f ~/.ssh/workpilot_ed25519 -C "workpilot-deploy"

# 2) 把公钥放到服务器管理账号（<IP> 替换；按提示输一次 root 密码）
ssh-copy-id -i ~/.ssh/workpilot_ed25519.pub root@<IP>

# 3) 服务器初始化（root 执行，只做一次）：装 Docker + 建 deploy 用户 + SSH 加固 + 防火墙
ssh root@<IP> 'bash -s' <<'EOF'
set -e
curl -fsSL https://get.docker.com | sh
adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy
mkdir -p /home/deploy/.ssh && cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh && chmod 700 /home/deploy/.ssh && chmod 600 /home/deploy/.ssh/authorized_keys
printf 'PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin no\n' > /etc/ssh/sshd_config.d/00-hardening.conf
sshd -t && systemctl restart ssh
command -v ufw >/dev/null && { ufw allow OpenSSH; ufw allow 80/tcp; ufw allow 443; ufw --force enable; }
EOF

# 4) Mac 加别名（~/.ssh/config 追加），之后统一用 wp-prod
cat >> ~/.ssh/config <<'EOF'

Host wp-prod
    HostName <IP>
    User deploy
    IdentityFile ~/.ssh/workpilot_ed25519
EOF

# 5) 域名 A 记录：wp -> <IP>，TTL 600；确认生效再继续
dig +short wp.<域名>     # 期望：返回你的 IP

# 6) 填 .env.prod 的占位符（<sk-...> / WP_DOMAIN / ACME_EMAIL / BASIC_AUTH_USER）
#    并轮换 basic auth 密码（见 runbook「轮换 basic auth 密码」）

# 7) 首次上传 .env 并收紧权限
ssh wp-prod 'mkdir -p ~/workpilot'
scp .env.prod wp-prod:~/workpilot/.env && ssh wp-prod 'chmod 600 ~/workpilot/.env'

# 8) 一键部署（rsync 代码 + 拉镜像 + compose up + /ready 探活）
make deploy
```

部署成功后，回到 §4 逐条跑验收命令。

---

## 6. 需要注意的偏差与遗留

1. **MINIO_ENDPOINT 用 `http://minio:9000`（非 PLAN 里的 `minio:9000`）**：`config.py` 把它直接当 boto3 `endpoint_url` 用，缺 `http://` 会连不上；这与 dev 保持一致，是 PLAN 简写的笔误。
2. **basic auth 哈希是占位密码 `ChangeMe_2026_Demo`**：上线前必须用 `docker run --rm -it caddy:2-alpine caddy hash-password` 重生成并替换（见 runbook）。
3. **`/health`、`/ready` 未在 prod Caddy 反代**（只反代 `/v1/*`）：对外探活请用 `curl -u ... https://wp.<域名>/v1/...`，或直接 SSH 进服务器 `docker compose ... ps` 看容器状态；生产把健康端点藏在内网是刻意为之（避免信息泄露）。
4. **basic auth 只是 W19 前的 Demo 门禁**：无用户区分、无法单独吊销，W19 换正式登录系统（已记入 runbook 技术债）。
