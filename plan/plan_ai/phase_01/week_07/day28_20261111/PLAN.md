# Day 28 · 2026-11-11 · Week 07 Task 3：云部署 + HTTPS + 访问保护

## 0. 今天只做一件事

把 WorkPilot 部署到一台 2C4G 云服务器：Caddy 自动 HTTPS、basic auth 保护 Demo、Qdrant / MinIO 不暴露公网、Embedding 切 SiliconFlow `BAAI/bge-m3`，用 `deploy.sh` 一条命令发布，公网带引用问答可用。

不碰：自动部署（W19）、登录系统（W19）、监控告警、CDN、多台机器、把 `data/corpus` 或任何公司内容传上服务器。

## 1. 资产锚点

- 构建模块：M5.3 云部署 + HTTPS（Caddy）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备（P1 验收「公网可访问」）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`https://<域名>` 证书有效 → 输入 basic auth → 上传 / 流式问答 / 反馈全流程；外部扫描只开放 22/80/443
- 今日 AI 实际应用：Embedding 从本地 Ollama 切到 SiliconFlow 同模型 API——同一模型保证 dev / prod 检索行为一致，同时让服务器不需要 GPU / 大内存，单次导入成本可计量

## 2. 起点（前置确认）

- 已有：Day26–27 的镜像、compose、`/ready`；`data/sample` 公开样例。
- **需提前完成（不占今天时间）**：购买 2C4G 轻量服务器（香港 / 新加坡区，Ubuntu 22.04/24.04，≤ ¥100/月）；购买域名（约 ¥60/年，国内注册商需先完成实名认证，可能要 1–3 天）；注册 SiliconFlow 并创建 API Key。
- 需确认：

```bash
ssh-keygen -t ed25519 -f ~/.ssh/workpilot_ed25519 -C "workpilot-deploy"   # 若还没有专用密钥
dig +short wp.<你的域名>              # 今天要配置的子域名，预期为空或旧值
curl -s https://api.siliconflow.cn/v1/embeddings -H "Authorization: Bearer $SILICONFLOW_KEY" \
  -H 'Content-Type: application/json' -d '{"model":"BAAI/bge-m3","input":"hello"}' | head -c 200
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `ssh root@<IP>` 与密码登录均被拒绝；`ssh -i ~/.ssh/workpilot_ed25519 deploy@<IP>` 可登录
- [ ] `curl -sI https://wp.<域名> | head -1` 返回 `401`；`curl -vI` 显示证书由 Let's Encrypt 或 ZeroSSL 签发
- [ ] 浏览器输入 basic auth 后：上传样例 → ready → 流式问答带引用 → 👎 反馈成功
- [ ] `nc -zvw3 <IP> 6333 9000 9001 8000` 全部失败，`nc -zvw3 <IP> 443` 成功
- [ ] 服务器 `stat -c %a ~/workpilot/.env` 输出 `600`
- [ ] `docs/runbook.md` 有「部署」章节；已 commit + push（不含任何密钥）

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                                       |
| ------- | ------ | -------------------------------------------------------------------------- |
| 0–10    | P0     | 方案 A / B 确认，记录理由                                                  |
| 10–40   | P0     | 服务器初始化：deploy 用户、SSH 加固、ufw、Docker                           |
| 40–50   | P0     | DNS A 记录；生成 basic auth 哈希                                           |
| 50–75   | P0     | `docker-compose.prod.yml` + `Caddyfile.prod` + `deploy.sh` + 服务器 `.env` |
| 75–100  | P0     | 首次部署、seed 样例、逐项验证                                              |
| 100–115 | P0     | runbook 部署章节 + 提交                                                    |
| 115–120 | P1     | 记录首次构建耗时、内存占用（`docker stats --no-stream`）                   |

时间不足时最低保留：公网 HTTPS + basic auth + 问答一次（加固项中 SSH 禁密码不可省略）。

## 5. 今日学习（只学完成任务必须的）

- Caddy 站点地址写域名时，会自动向 ACME CA 申请并续期证书，前提是 DNS 已指向本机且 80/443 可达。
- Docker 发布的端口会绕过 ufw 规则（直接写 iptables），所以「不暴露」必须靠 compose 不写 `ports`，而不是靠防火墙。
- `sshd_config.d/` 中同一指令以**先读到的为准**，云镜像常带 `50-cloud-init.conf` 开启密码登录，自定义文件要用更小的序号。
- basic auth 只适合 W19 前的 Demo 保护：凭据 bcrypt 哈希存服务器，传输依赖 HTTPS。
- 资料：https://caddyserver.com/docs/automatic-https 、https://caddyserver.com/docs/caddyfile/directives/basic_auth 、https://docs.docker.com/engine/install/ubuntu/ 、https://docs.docker.com/engine/network/packet-filtering-firewalls/ 、https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/

## 6. 执行步骤

### Step 1 · 方案选择（写进 runbook）

| 维度       | A 轻量服务器 + Caddy（推荐）           | B Cloudflare Tunnel 暴露本机    |
| ---------- | -------------------------------------- | ------------------------------- |
| 成本       | ¥60–100/月 + 域名                      | 免费（域名需托管在 Cloudflare） |
| 可用性     | 7×24                                   | Mac 合盖 / 断网即不可用         |
| Embedding  | SiliconFlow API                        | 可继续用本机 Ollama             |
| 学到的能力 | Linux 加固、HTTPS、生产配置（JD 高频） | 隧道 / Zero Trust               |
| 适用       | P1 公网 Demo、面试演示                 | 预算为 0 或临时演示             |

B 方案最小命令（仅备选）：`brew install cloudflared` → `cloudflared tunnel login` → `cloudflared tunnel create workpilot` → `cloudflared tunnel route dns workpilot wp.<域名>` → `cloudflared tunnel run --url http://localhost:8080 workpilot`；保护用 Cloudflare Access 或在 dev Caddyfile 加 basic_auth。

### Step 2 · 服务器初始化（用云厂商给的 root / ubuntu 账号登录）

```bash
# 在 Mac：把公钥放到服务器默认管理账号
ssh-copy-id -i ~/.ssh/workpilot_ed25519.pub root@<IP>      # 或 ubuntu@<IP>
# 在服务器（管理账号）：
curl -fsSL https://get.docker.com | sudo sh                 # 官方安装脚本（含 compose 插件）
sudo adduser --disabled-password --gecos "" deploy           # 部署用户：无密码、无 sudo
sudo usermod -aG docker deploy                               # 注意：docker 组 ≈ root 权限，只给部署用户
sudo mkdir -p /home/deploy/.ssh && sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
sudo chown -R deploy:deploy /home/deploy/.ssh && sudo chmod 700 /home/deploy/.ssh && sudo chmod 600 /home/deploy/.ssh/authorized_keys
# SSH 加固：文件名用 00- 前缀，保证先于 50-cloud-init.conf 被读取
printf 'PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin no\n' | sudo tee /etc/ssh/sshd_config.d/00-hardening.conf
sudo sshd -t && sudo sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'
sudo systemctl restart ssh
# 防火墙
sudo ufw allow OpenSSH && sudo ufw allow 80/tcp && sudo ufw allow 443 && sudo ufw --force enable && sudo ufw status
```

**保持当前 SSH 会话不要关**，另开一个 Mac 终端验证：`ssh -i ~/.ssh/workpilot_ed25519 deploy@<IP> docker ps` 成功、`ssh root@<IP>` 被拒，确认后再关旧会话。云厂商控制台的「防火墙 / 安全组」同样只放行 22/80/443。

Mac `~/.ssh/config` 加别名（之后都用 `wp-prod`）：

```text
Host wp-prod
  HostName <IP>
  User deploy
  IdentityFile ~/.ssh/workpilot_ed25519
```

### Step 3 · DNS + basic auth 哈希

- 域名控制台添加 A 记录：`wp` → `<IP>`，TTL 600；`dig +short wp.<域名>` 返回 IP 再继续。
- 生成哈希（交互输入密码，不进 shell 历史）：`docker run --rm -it caddy:2-alpine caddy hash-password`，复制输出的 `$2a$14$...`。

### Step 4 · 生产配置

`deploy/Caddyfile.prod`（Tab 缩进）：

```caddyfile
{
	email {$ACME_EMAIL}
}

{$WP_DOMAIN} {
	basic_auth {
		{$BASIC_AUTH_USER} {$BASIC_AUTH_HASH}
	}
	handle /v1/* {
		reverse_proxy api:8000 {
			flush_interval -1
		}
	}
	handle {
		root * /srv
		encode zstd gzip
		try_files {path} /index.html
		file_server
	}
	header {
		Strict-Transport-Security "max-age=31536000"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "strict-origin-when-cross-origin"
		-Server
	}
}
```

`deploy/docker-compose.prod.yml`：以 dev compose 为底复制一份，**只改下面这些**（其余 healthcheck / depends_on / restart 保持一致）：

```yaml
name: workpilot
services:
  api:
    # build / env_file / volumes / depends_on / healthcheck 同 dev
    environment:
      APP_ENV: prod
      DATABASE_URL: sqlite:////app/data/workpilot.db
      QDRANT_URL: http://qdrant:6333
      MINIO_ENDPOINT: minio:9000
      EMBEDDING_BASE_URL: https://api.siliconflow.cn/v1 # 与 dev 同模型 bge-m3，1024 维
      EMBEDDING_MODEL: BAAI/bge-m3 # EMBEDDING_API_KEY 放服务器 .env
  web:
    ports: ["80:80", "443:443", "443:443/udp"]
    environment:
      WP_DOMAIN: ${WP_DOMAIN}
      ACME_EMAIL: ${ACME_EMAIL}
      BASIC_AUTH_USER: ${BASIC_AUTH_USER}
      BASIC_AUTH_HASH: ${BASIC_AUTH_HASH}
    volumes:
      - ./Caddyfile.prod:/etc/caddy/Caddyfile:ro
      - caddy-data:/data # 证书持久化：丢了会重复申请触发 CA 限流
      - caddy-config:/config
  qdrant: # 不写 ports —— 只在 compose 内网可达
  minio: # 不写 ports；MINIO_ROOT_* 使用与 dev 不同的强密码
volumes:
  {
    api-data: {},
    qdrant-data: {},
    minio-data: {},
    caddy-data: {},
    caddy-config: {},
  }
```

Mac 上准备 `.env.prod`（被 `.env.*` 忽略，**确认 `git check-ignore .env.prod` 有输出**）：在 `.env.example` 基础上填 `APP_ENV=prod`、LLM / SiliconFlow key、新的 MinIO 强密码、`WP_DOMAIN=wp.<域名>`、`ACME_EMAIL=`、`BASIC_AUTH_USER=`、`BASIC_AUTH_HASH='$2a$14$...'`（**单引号**：Compose 对单引号值不做 `$` 插值）。

### Step 5 · deploy/scripts/deploy.sh

```bash
#!/usr/bin/env bash
# 用法：DEPLOY_HOST=wp-prod ./deploy/scripts/deploy.sh
set -euo pipefail
HOST="${DEPLOY_HOST:?请设置 DEPLOY_HOST，如 wp-prod}"
DIR="${DEPLOY_DIR:-workpilot}"                      # 远端 home 下的目录
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE="docker compose --env-file .env -f deploy/docker-compose.prod.yml"

# --delete 不会删除被 exclude 的远端文件，所以服务器上的 .env 是安全的
rsync -az --delete \
  --exclude '.git/' --exclude '.env' --exclude '.env.*' \
  --exclude '/data/' --exclude 'apps/api/data/' --exclude '/eval/' \
  --exclude 'node_modules/' --exclude '.venv/' --exclude 'dist/' \
  --exclude '__pycache__/' --exclude '.pytest_cache/' \
  "$ROOT/" "$HOST:$DIR/"

ssh "$HOST" "cd $DIR && test -f .env || { echo '缺少服务器 .env'; exit 1; }"
ssh "$HOST" "cd $DIR && $COMPOSE up -d --build --remove-orphans && $COMPOSE ps"
ssh "$HOST" "cd $DIR && $COMPOSE exec -T api python -c \
  \"import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8000/ready',timeout=5).read().decode())\""
```

Makefile 增加 `deploy:` → `DEPLOY_HOST=$(or $(DEPLOY_HOST),wp-prod) ./deploy/scripts/deploy.sh`。

### Step 6 · 首次部署 + 验证

```bash
ssh wp-prod 'mkdir -p ~/workpilot'
scp .env.prod wp-prod:~/workpilot/.env && ssh wp-prod 'chmod 600 ~/workpilot/.env'
chmod +x deploy/scripts/deploy.sh && make deploy           # 首次构建 5–10 分钟
curl -sI https://wp.<域名> | head -1                       # HTTP/2 401
curl -vI https://wp.<域名> 2>&1 | grep -iE 'issuer|expire'
BASIC_AUTH='<user>:<pass>' make seed BASE=https://wp.<域名>  # 只导入 data/sample 公开样例
nc -zvw3 <IP> 6333 9000 9001 8000                          # 均应失败
```

浏览器打开 `https://wp.<域名>` → 输入凭据 → 问一个样例中的问题 + 一个库外问题（应拒答）+ 一次 👎。

### Step 7 · runbook + 提交

`docs/runbook.md` 新建「部署」章节：服务器信息（不写 IP 也可，写别名）、首次初始化清单、`make deploy`、查看日志 `ssh wp-prod 'cd workpilot && docker compose -f deploy/docker-compose.prod.yml logs -f --tail=100 api'`、证书 / 401 排查、轮换 basic auth 密码步骤。

```bash
git add deploy/ Makefile docs/runbook.md
git diff --cached | grep -nE 'sk-|\$2a\$|PASSWORD=.+' && echo "!!! 发现疑似密钥，停止提交"
git commit -m "feat(deploy): production compose with caddy https, basic auth and rsync deploy script"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 qdrant / minio 不写 `ports` 比依赖 ufw 更可靠？（答：Docker 发布端口会直接改 iptables 绕过 ufw；不发布则只在 compose 内网可达）
2. Caddy 自动 HTTPS 需要哪些前提？（答：域名 A 记录指向本机、80/443 从公网可达（HTTP-01 / TLS-ALPN 挑战）、证书目录持久化）
3. 为什么 prod 要换 SiliconFlow 而向量库要重新导入？（答：服务器无 Ollama；虽然同为 bge-m3，不同推理实现的向量存在细微数值差异，同一个 collection 内必须由同一来源生成）
4. basic auth 的风险和适用边界？（答：凭据每次请求都发送，必须 HTTPS；无用户区分、无法单独吊销；只做 W19 前的 Demo 门禁）
5. `rsync --delete` 为什么不会删掉服务器上的 `.env`？（答：被 `--exclude` 匹配的文件不参与删除，除非加 `--delete-excluded`）

## 8. 对 DA-01 的贡献

F8「云端部署」落地，WorkPilot 第一次有公网地址——P1 作品集、面试演示、W23 在线 Demo、W22 Pro Kit 的「生产部署包」都从这套 prod compose + Caddyfile + deploy.sh 演化而来。

## 9. 求职映射（D 线）

- 岗位能力：云部署、Linux 安全加固、HTTPS、最小暴露面
- 对应岗位：AI Engineer / AI Platform Engineer / Full-Stack
- 简历 bullet 草稿：将 RAG 知识助手部署至云服务器（2C4G），Caddy 自动 HTTPS + 访问保护，仅暴露 80/443，向量库与对象存储内网隔离；dev / prod 共用 bge-m3 模型（本地 Ollama / 云端 API），单次文档入库成本 ¥\_\_。
- 面试可能问：
  - 「你的服务部署后做了哪些安全措施？」要点：key 登录禁密码、禁 root、防火墙 + 不发布内部端口、HTTPS + HSTS、密钥文件 600、访问保护、合规语料。
  - 「开发和生产 embedding 不一样怎么办？」要点：同模型不同推理端；collection 不混用来源；切换时全量重建索引并重跑评测确认指标。

## 10. 卡住时的处理

| 现象                                                      | 处理                                                                                                                                        |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| Caddy 日志 `challenge failed` / `no such host`            | DNS 未生效或指错：`dig +short`；确认云控制台安全组放行 80/443                                                                               |
| 证书申请过多被限流 `too many certificates`                | 没持久化 `caddy-data` 导致反复申请；加 volume，等待限流窗口，期间可用 `acme_ca https://acme-staging-v02.api.letsencrypt.org/directory` 调试 |
| 改完 sshd 后 `Permission denied (publickey)` 且旧会话已关 | 用云厂商控制台的 VNC / 救援登录，恢复 `authorized_keys` 权限（700/600）                                                                     |
| api 启动失败 `APP_ENV=prod 需要 EMBEDDING_API_KEY`        | Day27 的 prod 守卫生效：服务器 `.env` 补 key                                                                                                |
| basic auth 一直 401（密码正确）                           | 哈希中的 `$` 被插值吃掉：`.env` 中改为单引号，或 `docker compose ... config                                                                 | grep BASIC` 检查展开结果 |
| 服务器构建 web 时 OOM / 极慢                              | 2C4G 一般够；可临时加 2G swap（`fallocate -l 2G /swapfile` …）或在 Mac 构建好 `dist` 再传                                                   |

## 11. 产出记录（执行时填写）

- 方案 A / B 及理由：\_\_\_\_
- 云厂商 / 区域 / 月费：\_**\_；域名 / 年费：\_\_**
- 首次构建耗时：\_**\_；`docker stats` 内存占用：\_\_**
- 公网问答首 token 延迟：\_\_\_\_ s
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → 明天进入 Day29（CI + 云端备份恢复演练 + Week 7 复盘）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
