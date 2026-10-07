# Day 29 · 2026-11-12 · Week 07 Task 4：CI + 云端备份恢复演练

## 0. 今天只做一件事

让每次 push 自动跑 lint / test / typecheck / build（Gitea Actions），并为云端数据建立「每日备份 → 拉回 Mac → 清空 → 恢复 → 问答验证」的可证明流程，耗时写进 runbook，完成 Week 7 复盘。

不碰：CD 自动部署（W19）、评测门禁（W14/W22）、GitHub Actions（W8 公开后再说）、对象存储异地复制、备份加密方案选型。

## 1. 资产锚点

- 构建模块：M5.4 CI/CD（Gitea Actions）、M5.5 备份 / 恢复 / 运行手册（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：Gitea Actions 页绿色构建；`backup.sh` 产出包含 Qdrant 快照 + SQLite + MinIO 的 tar；恢复演练 RTO = \_\_\_\_ 分钟（写入 `docs/runbook.md`）
- 今日 AI 实际应用：RAG 系统的「状态」分散在三处（向量 / 业务库 / 原始文档），三者必须一起备份恢复，否则会出现「引用指向已不存在的文档」——这是 AI 应用特有的一致性问题

## 2. 起点（前置确认）

- 已有：Day28 云端运行中；`apps/api/tests`；pytest 中调用真实 LLM / Qdrant 的测试。
- 需确认：

```bash
cd ~/lab/workpilot
docker exec gitea gitea --version                      # ≥ 1.21 默认启用 Actions
grep -n "markers" -A3 apps/api/pyproject.toml          # 是否已注册 live 标记
grep -rln "deepseek\|QdrantClient(\|httpx" apps/api/tests | head   # 需打 @pytest.mark.live 的测试
uv --directory apps/api run ruff --version || echo "需要 uv add --dev ruff"
ssh wp-prod 'cd workpilot && docker compose -f deploy/docker-compose.prod.yml ps'
```

## 3. 验收对齐（做完要能勾掉）

- [ ] Gitea 站点管理 → Actions → Runners 中 runner 状态为 Idle / Online
- [ ] push 后 Actions 页 `ci` 工作流 api / web 两个 job 均绿色
- [ ] 故意引入一个 ruff 错误 push → CI 红 → 修复后绿（证明门禁有效）
- [ ] 服务器 `~/backups/wp-*.tgz` 存在，内含 `qdrant-*.snapshot`、`workpilot.db`、`minio.tgz`
- [ ] Mac `~/lab/backups/workpilot-cloud/` 有同一份副本
- [ ] 恢复演练：清空卷后问答失败 → 恢复后同一问题返回带引用答案；RTO 写入 runbook
- [ ] 服务器 `crontab -l` 含每日备份；Week 7 复盘已填；已 commit + push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                                                   |
| ------- | ------ | -------------------------------------------------------------------------------------- |
| 0–10    | P0     | 前置确认；给外部依赖测试打 `live` 标记                                                 |
| 10–30   | P0     | 启动 act_runner 并注册                                                                 |
| 30–55   | P0     | `ci.yml`，push，修到绿                                                                 |
| 55–80   | P0     | `backup.sh` + 服务器跑一次 + Mac 拉回                                                  |
| 80–105  | P0     | 恢复演练（计时）+ `restore.sh`                                                         |
| 105–115 | P0     | runbook + crontab + 周复盘 + 提交                                                      |
| 115–120 | P1     | README 加 CI 状态徽章（Gitea：`/<user>/workpilot/actions/workflows/ci.yml/badge.svg`） |

时间不足时最低保留：备份 + 恢复演练（不可替代）；CI 若卡在网络问题 → 记录原因，CONDITIONAL，W9 第一天补。

## 5. 今日学习（只学完成任务必须的）

- Gitea Actions 语法兼容 GitHub Actions；act_runner 是执行器，以 Docker 容器方式为每个 job 启动一个环境容器。
- 容器里的 `localhost` 不是 Mac；在 Docker Desktop 中容器访问宿主服务用 `host.docker.internal`——runner 连接 Gitea、job 里 checkout 代码都要用它。
- Qdrant 快照：`POST /collections/{name}/snapshots` 创建，`GET .../snapshots/{snap}` 下载，`POST .../snapshots/upload?priority=snapshot` 恢复；恢复需版本兼容。
- SQLite 运行中备份要用 online backup API（`sqlite3.Connection.backup`），直接 `cp` 可能拷到写了一半的页。
- 资料：https://docs.gitea.com/usage/actions/overview 、https://docs.gitea.com/usage/actions/act-runner 、https://qdrant.tech/documentation/concepts/snapshots/ 、https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup 、https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes

## 6. 执行步骤

### Step 1 · 测试分层

`apps/api/pyproject.toml`：

```toml
[tool.pytest.ini_options]
markers = ["live: 调用真实外部服务（LLM / Qdrant / Ollama），CI 中跳过"]
```

给需要外部服务的测试加 `@pytest.mark.live`；本地 `uv run pytest -m "not live"` 必须全绿且无网络调用。

### Step 2 · 启动并注册 act_runner

Gitea Web：站点管理 → Actions → Runners → 「创建新的 Runner」，复制 registration token。仓库设置中确认「Actions」单元已勾选。

```bash
mkdir -p ~/gitea/runner
docker run -d --name gitea-runner --restart unless-stopped \
  -e GITEA_INSTANCE_URL=http://host.docker.internal:3000 \
  -e GITEA_RUNNER_REGISTRATION_TOKEN=<token> \
  -e GITEA_RUNNER_NAME=mac-runner \
  -e GITEA_RUNNER_LABELS=ubuntu-latest:docker://gitea/runner-images:ubuntu-latest \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/gitea/runner:/data \
  gitea/act_runner:latest
docker logs -f gitea-runner        # 看到 "runner: mac-runner ... declared successfully" 即可 Ctrl-C
```

token 只用于首次注册（注册信息存于 `~/gitea/runner/.runner`），用完即可在后台作废重建。

### Step 3 · .gitea/workflows/ci.yml

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  api:
    runs-on: ubuntu-latest
    env: # Day27 fail fast：CI 需要占位配置，不放真实密钥
      APP_ENV: dev
      LLM_BASE_URL: http://llm.invalid
      LLM_API_KEY: ci-dummy
      EMBEDDING_BASE_URL: http://embedding.invalid
    defaults:
      run:
        working-directory: apps/api
    steps:
      - uses: actions/checkout@v4
        with:
          github-server-url: http://host.docker.internal:3000 # job 容器里 localhost:3000 不可达
      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"
      - name: Sync deps
        run: uv sync --frozen
      - name: Lint
        run: uv run ruff check .
      - name: Test
        run: uv run pytest -m "not live" -q

  web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
        with:
          github-server-url: http://host.docker.internal:3000
      - name: Enable pnpm
        run: npm i -g corepack@latest && corepack enable
      - name: Install
        run: pnpm install --frozen-lockfile
      - name: Typecheck
        run: pnpm exec tsc --noEmit -p tsconfig.app.json # 根 tsconfig 是 references，直接 tsc 不检查任何文件
      - name: Build
        run: pnpm build
```

```bash
git add .gitea apps/api/pyproject.toml apps/api/tests
git commit -m "ci: add gitea actions for api lint/test and web typecheck/build" && git push
```

打开 Gitea 仓库 → Actions 看日志；绿了以后做一次「故意加未使用 import → 红 → 修复 → 绿」。

### Step 4 · deploy/scripts/backup.sh（在服务器运行）

```bash
#!/usr/bin/env bash
# 服务器：~/workpilot/deploy/scripts/backup.sh  → ~/backups/wp-YYYYmmdd-HHMMSS.tgz，保留 7 份
set -euo pipefail
cd "$(dirname "$0")/../.."
COMPOSE="docker compose --env-file .env -f deploy/docker-compose.prod.yml"
NET="workpilot_default"; COLL="${QDRANT_COLLECTION:-kb_default}"   # 集合名以你的配置为准
ROOT="${BACKUP_ROOT:-$HOME/backups}"; TS="$(date +%Y%m%d-%H%M%S)"; WORK="$ROOT/wp-$TS"
curl_net() { docker run --rm --network "$NET" curlimages/curl -sfS "$@"; }
mkdir -p "$WORK"

# 1) Qdrant：创建快照 → 下载 → 删除服务端快照
SNAP=$(curl_net -X POST "http://qdrant:6333/collections/$COLL/snapshots?wait=true" \
       | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["name"])')
curl_net "http://qdrant:6333/collections/$COLL/snapshots/$SNAP" > "$WORK/qdrant-$COLL.snapshot"
curl_net -X DELETE "http://qdrant:6333/collections/$COLL/snapshots/$SNAP" > /dev/null

# 2) SQLite：在线备份 API，再拷出容器
$COMPOSE exec -T api python -c "import sqlite3; s=sqlite3.connect('/app/data/workpilot.db'); \
d=sqlite3.connect('/app/data/backup.db'); s.backup(d); d.close(); s.close()"
$COMPOSE cp api:/app/data/backup.db "$WORK/workpilot.db"
$COMPOSE exec -T api rm -f /app/data/backup.db

# 3) MinIO：只读挂载数据卷打包（单节点、低写入量下可接受；严格一致可先 stop minio）
docker run --rm -v workpilot_minio-data:/data:ro -v "$WORK":/backup alpine \
  tar czf /backup/minio.tgz -C /data .

tar czf "$ROOT/wp-$TS.tgz" -C "$ROOT" "wp-$TS" && rm -rf "$WORK"
ls -1t "$ROOT"/wp-*.tgz | tail -n +8 | xargs -r rm -f          # 只保留最近 7 份
echo "backup ok: $ROOT/wp-$TS.tgz ($(du -h "$ROOT/wp-$TS.tgz" | cut -f1))"
```

```bash
make deploy                                   # 把脚本同步到服务器
ssh wp-prod 'chmod +x workpilot/deploy/scripts/backup.sh && workpilot/deploy/scripts/backup.sh'
ssh wp-prod 'tar tzf $(ls -1t ~/backups/wp-*.tgz | head -1)'          # 校验内容
mkdir -p ~/lab/backups/workpilot-cloud && rsync -az wp-prod:backups/ ~/lab/backups/workpilot-cloud/
```

服务器无法主动连回 Mac（NAT），所以「回传」由 Mac 拉取；每周至少手动拉一次（P2：launchd 定时）。

### Step 5 · 恢复演练（计时，破坏性操作仅限云端 Demo 环境）

先确认：Mac 上已有最新备份副本、`tar tzf` 校验通过。这一步会删除云端数据卷，**只在只含公开样例数据的 Demo 环境执行**。

```bash
ssh wp-prod
cd ~/workpilot && START=$SECONDS
C="docker compose --env-file .env -f deploy/docker-compose.prod.yml"
B=$(ls -1t ~/backups/wp-*.tgz | head -1) && mkdir -p /tmp/restore && tar xzf "$B" -C /tmp/restore && R=$(ls -d /tmp/restore/wp-*)
$C down && docker volume rm workpilot_qdrant-data workpilot_minio-data workpilot_api-data
$C up --no-start && $C start qdrant                           # 由 compose 建出空卷（带标签），只启动 qdrant
docker run --rm -v workpilot_minio-data:/data -v "$R":/backup alpine sh -c 'tar xzf /backup/minio.tgz -C /data'
docker run --rm -v workpilot_api-data:/data -v "$R":/backup alpine sh -c 'cp /backup/workpilot.db /data/ && chown 10001:10001 /data/workpilot.db'
until docker run --rm --network workpilot_default curlimages/curl -sf http://qdrant:6333/readyz >/dev/null; do sleep 2; done
docker run --rm --network workpilot_default -v "$R":/backup curlimages/curl -sfS \
  -X POST "http://qdrant:6333/collections/kb_default/snapshots/upload?priority=snapshot" \
  -F "snapshot=@/backup/qdrant-kb_default.snapshot"
$C up -d && echo "RTO: $((SECONDS-START))s"
```

浏览器用同一个样例问题验证：答案带引用、引用点开有片段、知识库页文档列表与备份前一致、历史会话仍在。把以上命令整理为 `deploy/scripts/restore.sh <backup.tgz>`（让 AI 根据上面命令生成，你逐行审查删卷部分）。

### Step 6 · runbook + cron + 复盘 + 提交

`docs/runbook.md` 增加：「备份」（内容、位置、保留策略、Mac 拉取命令）、「恢复」（步骤 + 本次 RTO \_\_\_\_ 分钟 + 日期）、「CI」（runner 启动命令、常见失败）。

```bash
ssh wp-prod '(crontab -l 2>/dev/null; echo "30 3 * * * $HOME/workpilot/deploy/scripts/backup.sh >> $HOME/backups/backup.log 2>&1") | crontab -'
ssh wp-prod 'crontab -l'        # 服务器时区通常为 UTC：03:30 UTC = 北京时间 11:30
git add deploy/scripts docs/runbook.md
git commit -m "ops: add cloud backup/restore scripts and runbook with restore drill result" && git push
```

填写 `plan/phase_01/week_07/README.md` 第 11 节周复盘。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 CI 里要排除 `live` 测试？（答：CI 不应依赖外部付费 API 和网络状况，结果要确定、免费、快；live 测试本地或评测时跑）
2. RAG 系统备份为什么要三件一起？（答：向量 payload 引用 doc_id，SQLite 记录文档 / 会话 / 反馈，MinIO 存原文；任何一处缺失都会导致引用失效或无法重建索引）
3. RPO 和 RTO 分别是多少？（答：每日备份 → RPO ≤ 24 小时；RTO = 本次演练实测的 \_\_\_\_ 分钟）
4. 为什么备份要拉回 Mac？（答：服务器本身故障 / 被删时，同机备份一起丢失；异地副本才算备份）
5. job 容器里 checkout 为什么要改 `github-server-url`？（答：Gitea 的 ROOT_URL 是 `localhost:3000`，job 容器里 localhost 指向容器自己；Docker Desktop 提供 `host.docker.internal` 指向 Mac）

## 8. 对 DA-01 的贡献

F8「备份 / 恢复脚本 + 恢复演练记录」与 M5.4 CI 落地：WorkPilot 从「能跑」变成「改动有门禁、数据可恢复」，满足 phase_01 §8 中 CI 与恢复演练两项，也为 W14 评测门禁、W19 自动部署提供流水线位置。

## 9. 求职映射（D 线）

- 岗位能力：CI 流水线、测试分层、备份恢复与 RTO / RPO
- 对应岗位：AI Platform Engineer / AI Engineer / DevOps 方向全栈
- 简历 bullet 草稿：搭建自托管 Gitea Actions CI（ruff / pytest / tsc / build，单次 ** 分钟），区分 live 与离线测试；实现向量库快照 + SQLite 在线备份 + 对象存储归档的每日备份与异地副本，完成全量恢复演练，RTO ** 分钟、RPO 24 小时。
- 面试可能问：
  - 「怎么保证备份可用？」要点：定期恢复演练、校验备份内容、记录 RTO、异地副本、版本兼容（Qdrant 快照）。
  - 「LLM 应用的 CI 测什么？」要点：确定性部分（解析、切分、路由、schema）用单测；LLM 行为用小样本评测集 + 阈值门禁（W14 / W22）；外部 API mock 或打 live 标记。

## 10. 卡住时的处理

| 现象                                                               | 处理                                                                                                                                        |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| runner 日志 `dial tcp 127.0.0.1:3000: connect: connection refused` | `GITEA_INSTANCE_URL` 不能用 localhost，改 `http://host.docker.internal:3000` 并删除 `~/gitea/runner/.runner` 重新注册                       |
| checkout 失败 `unable to access 'http://localhost:3000/...'`       | 未设置 `github-server-url`，或 Gitea 版本过旧；按 Step 3 配置                                                                               |
| 拉取 `actions/checkout` 或 `gitea/runner-images` 超时              | 网络问题：给 runner 容器加 `-e HTTPS_PROXY=http://host.docker.internal:7890`，或在 `~/gitea/runner/config.yaml` 的 `runner.envs` 中配置代理 |
| CI 中 `ValidationError: Field required`                            | Day27 fail fast 生效：在 workflow `env` 补占位变量（不放真实密钥）                                                                          |
| Qdrant 快照恢复报版本不兼容                                        | 备份与恢复必须同一 Qdrant 版本：compose 中固定 tag，不用 `latest`                                                                           |
| 恢复后 api 报 `attempt to write a readonly database`               | 恢复的 db 文件属主为 root：按 Step 5 `chown 10001:10001`                                                                                    |

## 11. 产出记录（执行时填写）

- CI 单次耗时（api / web）：\_**\_ / \_\_**
- 备份包大小：\_**\_；Qdrant 点数（备份前 / 恢复后）：\_\_** / \_\_\_\_
- RTO：\_\_\_\_ 分钟
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE → Week 7 DONE → 明天进入 Day30（Week 08 Task 1：README + 架构图 + ADR）。任一未通过 → 保持 IN PROGRESS，明天先补 P0；CI 若因网络未绿可标 CONDITIONAL，W9 第一天补齐。
