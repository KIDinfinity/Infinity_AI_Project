# Day 63 · 2027-02-02 · Week 19 Task 2：异步导入 + 自动部署（v1.2）

## 0. 今天只做一件事

用 Postgres 任务表 + `FOR UPDATE SKIP LOCKED` worker 把 KB 导入改成异步，并打通「推 tag → 构建 amd64 镜像 → 推 Gitea 容器仓库 → ssh 部署 → /ready 冒烟 → 失败回滚」，发布 `v1.2.0`。

不碰：Redis / Celery、K8s、蓝绿部署、多副本、卡死任务回收（Backlog）、PostgresSaver。

## 1. 资产锚点

- 构建模块：M5.4 CI/CD、M2.1 Ingest（异步化）、M5.5 回滚（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v1.2**（Postgres + 登录 + 多空间 + 异步导入 + 自动部署）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：上传大文档秒回 202，状态 queued → processing → ready；`git push origin v1.2.0` 后服务器自动更新；冒烟失败自动回滚（有演练记录）
- 今日 AI 实际应用：RAG 数据管道（解析 → 分块 → 向量化）从请求内同步执行变为可重试的后台任务，失败原因可见（F1「显示处理状态与失败原因」）

## 2. 起点（前置确认）

- 已有：Day62 Postgres + Alembic + 认证；W7 云服务器（ssh 可登录、compose prod、Caddy）；W7 Gitea Actions + act_runner；Gitea Packages。
- 需确认：

```bash
cd ~/lab/workpilot && uv run --directory apps/api pytest -q         # Day62 测试绿
docker buildx ls                                                    # 有支持 linux/amd64 的 builder
ssh deploy@<server> 'uname -m && docker compose version'            # 服务器多半是 x86_64
cat ~/.config/act_runner/config.yaml 2>/dev/null | grep -A3 labels  # runner 标签（路径以你 W7 安装为准）
curl -s http://localhost:3000/v2/ -o /dev/null -w "%{http_code}\n"  # 401 = 容器仓库可用
```

> 关键事实：Gitea 只在本机 `localhost:3000`，云服务器默认访问不到。今天用 **ssh 反向隧道**（`ssh -R 3000:localhost:3000`）在部署期间让服务器的 `localhost:3000` 指向本机 Gitea，镜像名 `localhost:3000/<owner>/workpilot-api:<tag>` 两端一致（Docker 默认允许 localhost 的 HTTP 仓库）。前提：服务器 3000 端口空闲。

## 3. 验收对齐（做完要能勾掉）

- [ ] Job 表迁移完成；`POST /v1/kb/ingest` 返回 202 + `job_id`；`GET /v1/jobs/{id}` 可查状态
- [ ] worker 处理后 KBDocument 状态 ready；人为制造失败 → attempts=3 后 status=failed 且 `last_error` 有内容
- [ ] compose（dev / prod）有 `worker` 服务：同镜像，command `python -m app.worker`
- [ ] `deploy/scripts/deploy.sh <tag>` 手动执行成功：迁移 → pull → up → /ready 通过
- [ ] 故意部署坏镜像（/ready 失败）→ 自动回滚到上一 tag，线上恢复
- [ ] `.gitea/workflows/deploy.yml` 由 tag 触发跑通；secrets 不出现在仓库与日志
- [ ] `v1.2.0` 已在服务器运行

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                               |
| ----------- | ------ | -------------------------------------------------- |
| 0–15 min    | P0     | Job 模型 + 迁移 + ingest 改 202                    |
| 15–40 min   | P0     | worker.py（claim / 执行 / 重试）+ compose worker   |
| 40–50 min   | P0     | 失败重试测试                                       |
| 50–80 min   | P0     | deploy.sh（隧道 + 迁移 + 冒烟 + 回滚）手动跑通     |
| 80–100 min  | P1     | deploy.yml + secrets + tag 触发                    |
| 100–110 min | P1     | 回滚演练 + runbook                                 |
| 110–120 min | P0     | tag v1.2.0                                         |
| 顺延        | P2     | 卡死任务回收、web 镜像分开发布、部署通知 → Backlog |

时间不足时最低保留：worker 跑通 + `deploy.sh` 手动部署 v1.2.0 成功。

## 5. 今日学习（只学完成任务必须的）

- **SKIP LOCKED**：`SELECT ... FOR UPDATE SKIP LOCKED` 让多个 worker 并发取任务时跳过别人已锁住的行，不阻塞、不重复。
- **claim 再处理**：在一个短事务里把任务改成 running 并提交，处理过程不持有锁；代价是进程崩溃会留下 running 任务（回收进 Backlog）。
- **Gitea 容器仓库**：镜像名 `<host>/<owner>/<image>:<tag>`，用带 package 权限的 token `docker login`。
- **跨架构构建**：Apple Silicon 默认 arm64，服务器是 amd64 → `docker buildx build --platform linux/amd64`。
- **expand-only 迁移**：只加表/加列（可空）不删不改，旧镜像能在新 schema 上运行 → 回滚镜像无需回滚数据库。
- 资料：https://www.postgresql.org/docs/ （SELECT → The Locking Clause）、https://docs.gitea.com/usage/packages/container 、https://docs.gitea.com/usage/actions/overview

## 6. 执行步骤

### Step 1 · Job 模型 + 异步 ingest（P0）

```python
# app/db/models.py
class Job(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workspace_id: uuid.UUID = Field(index=True)
    kind: str                                  # "ingest"
    payload: dict = Field(sa_column=Column(JSONB))
    status: str = Field(default="queued", index=True)   # queued|running|done|failed
    attempts: int = 0
    run_after: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

```bash
cd apps/api && uv run alembic revision --autogenerate -m "add job table" && uv run alembic upgrade head
```

ingest 路由：保存原文到 MinIO → 写 KBDocument(status=queued) → 写 Job(kind=ingest, payload={doc_id}) → `return JSONResponse({"job_id": ..., "doc_id": ...}, status_code=202)`。

### Step 2 · worker（P0，claim SQL 必须自己理解）

```python
# app/worker.py
import signal, time, traceback
from sqlalchemy import text
from app.db.session import engine
from app.jobs.ingest import run_ingest

HANDLERS = {"ingest": run_ingest}
MAX_ATTEMPTS = 3
CLAIM = text("""
UPDATE job SET status='running', attempts=attempts+1, updated_at=now()
WHERE id = (
  SELECT id FROM job
  WHERE status='queued' AND run_after <= now()
  ORDER BY created_at
  FOR UPDATE SKIP LOCKED
  LIMIT 1)
RETURNING id, kind, payload, workspace_id, attempts
""")
DONE = text("UPDATE job SET status='done', last_error=NULL, updated_at=now() WHERE id=:id")
RETRY = text("""UPDATE job SET status='queued', last_error=:err,
  run_after=now() + make_interval(secs => 30 * :attempts), updated_at=now() WHERE id=:id""")
FAIL = text("UPDATE job SET status='failed', last_error=:err, updated_at=now() WHERE id=:id")

stop = False
def _stop(*_):
    global stop; stop = True
signal.signal(signal.SIGTERM, _stop); signal.signal(signal.SIGINT, _stop)

def main():
    while not stop:
        with engine.begin() as conn:                       # 短事务：只负责 claim
            job = conn.execute(CLAIM).mappings().first()
        if not job:
            time.sleep(2); continue
        try:
            HANDLERS[job["kind"]](job)                      # 内部按 job.workspace_id 写 Qdrant payload
            with engine.begin() as conn: conn.execute(DONE, {"id": job["id"]})
        except Exception:
            err = traceback.format_exc()[-2000:]
            stmt = FAIL if job["attempts"] >= MAX_ATTEMPTS else RETRY
            with engine.begin() as conn:
                conn.execute(stmt, {"id": job["id"], "err": err, "attempts": job["attempts"]})

if __name__ == "__main__":
    main()
```

`run_ingest` 内同步更新 KBDocument：processing → ready / failed（failed 时写 error 摘要，前端 W6 状态列直接显示）。

compose 增加（dev 与 prod 同理，prod 用镜像）：

```yaml
worker:
  image: ${API_IMAGE:-workpilot-api}:${IMAGE_TAG:-dev}
  command: ["python", "-m", "app.worker"]
  env_file: [.env]
  depends_on: { postgres: { condition: service_healthy } }
  restart: unless-stopped
```

测试失败重试：上传一个 handler 会抛错的文件（如伪造损坏的 PDF），观察：

```bash
docker compose -f deploy/docker-compose.yml exec postgres psql -U workpilot -c \
 "select kind,status,attempts,left(last_error,80) from job order by created_at desc limit 3;"
```

> 重试间隔是 30s × attempts，演示时可临时把 30 改小。

### Step 3 · deploy.sh（P0）

```bash
#!/usr/bin/env bash
# deploy/scripts/deploy.sh <tag>  —— 在本机（或 runner）执行
set -euo pipefail
TAG="${1:?usage: deploy.sh <tag>}"
HOST="${DEPLOY_HOST:?}"; USER_AT="deploy@${HOST}"
KEY="${DEPLOY_KEY:-$HOME/.ssh/wp_deploy}"
# -R：部署期间服务器 localhost:3000 → 本机 Gitea（拉镜像用）
ssh -i "$KEY" -o StrictHostKeyChecking=accept-new -o ExitOnForwardFailure=yes \
    -R 3000:localhost:3000 "$USER_AT" bash -s -- "$TAG" <<'REMOTE'
set -euo pipefail
TAG="$1"; cd /opt/workpilot
C="docker compose --env-file .env.deploy -f docker-compose.prod.yml"
PREV=$(grep '^IMAGE_TAG=' .env.deploy | cut -d= -f2)
sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${TAG}/" .env.deploy
$C pull api worker web
$C run --rm api alembic upgrade head            # 只允许 expand-only 迁移
$C up -d
for i in $(seq 1 30); do
  if $C exec -T api python -c "import urllib.request as u;u.urlopen('http://localhost:8000/ready',timeout=3)"; then
    echo "deploy ${TAG} OK (prev ${PREV})"; exit 0
  fi
  sleep 2
done
echo "smoke failed → rollback to ${PREV}"
sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${PREV}/" .env.deploy
$C up -d
exit 1
REMOTE
```

服务器一次性准备：`/opt/workpilot/.env.deploy`（`IMAGE_TAG=`、`API_IMAGE=localhost:3000/<owner>/workpilot-api` 等）与 `.env`（数据库密码、JWT_SECRET，只在服务器上，权限 600）；在隧道打开时执行一次 `docker login localhost:3000`（用只读 `read:package` token）。

### Step 4 · deploy.yml + secrets（P1）

Gitea 仓库 → 设置 → Actions → Secrets：`REGISTRY_USER`、`REGISTRY_TOKEN`（write:package）、`DEPLOY_HOST`、`DEPLOY_SSH_KEY`（专用部署密钥，只授权 deploy 用户）。

```yaml
# .gitea/workflows/deploy.yml
name: deploy
on:
  push:
    tags: ["v*"]
jobs:
  deploy:
    runs-on: host # act_runner 的 host 标签：直接用本机 docker / ssh（以 W7 runner 配置为准）
    env:
      TAG: ${{ github.ref_name }}
      API_IMAGE: localhost:3000/${{ github.repository_owner }}/workpilot-api
      WEB_IMAGE: localhost:3000/${{ github.repository_owner }}/workpilot-web
    steps:
      - uses: actions/checkout@v4
      - name: login registry
        run: echo "${{ secrets.REGISTRY_TOKEN }}" | docker login localhost:3000 -u "${{ secrets.REGISTRY_USER }}" --password-stdin
      - name: build & push (amd64)
        run: |
          docker buildx build --platform linux/amd64 -f apps/api/Dockerfile -t "$API_IMAGE:$TAG" --push apps/api
          docker buildx build --platform linux/amd64 -f apps/web/Dockerfile -t "$WEB_IMAGE:$TAG" --push apps/web
      - name: deploy
        env:
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
        run: |
          install -m 600 /dev/null /tmp/wp_deploy && echo "${{ secrets.DEPLOY_SSH_KEY }}" > /tmp/wp_deploy
          DEPLOY_KEY=/tmp/wp_deploy ./deploy/scripts/deploy.sh "$TAG"
      - name: cleanup
        if: always()
        run: rm -f /tmp/wp_deploy
```

> owner 名含大写时镜像名需小写，手动写死小写更稳。

### Step 5 · 回滚演练 + 发布（P1 / P0）

```bash
# 演练：打一个故意让 /ready 失败的预发布 tag（如环境变量缺失触发 ready 检查失败）
git tag v1.2.0-rc.bad && git push origin v1.2.0-rc.bad      # 观察 workflow：冒烟失败 → 回滚
git push origin :refs/tags/v1.2.0-rc.bad                     # 演练结束删除远端临时 tag（本地同删）
# 正式发布
git add apps/api deploy .gitea docs/runbook.md
git commit -m "feat(ops): async ingest worker with skip-locked queue and tag-based deploy with rollback"
git push && git tag -a v1.2.0 -m "v1.2.0: postgres, auth, workspaces, async ingest, auto deploy" && git push origin v1.2.0
```

`docs/runbook.md` 追加：部署流程图、手动部署命令、回滚命令（`IMAGE_TAG=<prev>` + `up -d`）、查看 worker 日志、job 失败排查 SQL。

## 7. 概念自检（不看资料，口述，附答案）

1. 没有 SKIP LOCKED，两个 worker 同时取任务会怎样？（答：第二个会阻塞等锁，或在无锁实现下重复取到同一任务）
2. 为什么 claim 后立即提交事务？（答：避免长时间持有行锁和长事务；状态 running 本身就阻止再次被取）
3. worker 崩溃留下的 running 任务怎么办？（答：按 updated_at 超时重新排队——今天进 Backlog，runbook 先写手动 SQL）
4. 为什么部署前先跑 `alembic upgrade`，回滚时却不 downgrade？（答：迁移只做 expand（加表/加可空列），旧镜像兼容新 schema；downgrade 可能丢数据）
5. 为什么要 `--platform linux/amd64`？（答：Mac 是 arm64，服务器是 x86_64，架构不匹配会 `exec format error`）
6. 部署 SSH 密钥为什么要专用？（答：最小权限，可单独吊销；泄露不影响个人主密钥）

## 8. 对 DA-01 的贡献

WorkPilot 的数据管道变得可靠（可重试、可见失败原因），交付变得可重复（tag 即部署、失败自动回滚）。v1.2 让后续 W20–W22 的每次改进都能低成本上线，也让 Pro Kit 的「部署手册」有真实流水线可写。

## 9. 求职映射（D 线）

- 岗位能力：任务队列设计、并发控制、容器镜像仓库、CI/CD、回滚策略、密钥管理。
- 对应岗位：AI Platform Engineer、Backend / DevOps（AI 方向）、AI Full-Stack Engineer。
- 简历 bullet 草稿：「基于 Postgres SKIP LOCKED 实现异步文档导入队列（3 次重试 + 错误可视化），用 Gitea Actions 实现 tag 触发构建 → 推私有镜像仓库 → ssh 部署 → 冒烟 → 自动回滚，部署耗时约 \_\_ 分钟」
- 面试可能问：
  1. 什么时候该引入 Redis/MQ？——要点：吞吐高、需要发布订阅/延迟队列/多语言消费时；当前规模 Postgres 队列足够且少一个组件。
  2. 如何保证部署可回滚？——要点：不可变镜像 tag、记录上一版本、健康检查冒烟、expand-only 迁移、回滚演练。

## 10. 卡住时的处理

| 现象                                             | 处理                                                                                                                               |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| 服务器 `docker pull localhost:3000/...` 连接拒绝 | 隧道未建立：确认 `-R 3000:localhost:3000` 且服务器 3000 空闲；`ExitOnForwardFailure=yes` 会直接报错                                |
| pull 报 unauthorized / token realm 错误          | Gitea `ROOT_URL` 必须是 `http://localhost:3000/`（token 地址按 ROOT_URL 生成）；服务器需在隧道开启时 `docker login localhost:3000` |
| `exec format error`                              | 镜像是 arm64：确认 buildx `--platform linux/amd64`                                                                                 |
| runner 内没有 docker 命令                        | runner 标签是容器模式；为 deploy 增加 `host` 标签（act_runner config `labels: ["host:host"]`）或挂载 docker.sock                   |
| worker 取不到任务                                | `run_after` 时区问题：统一用 `timestamptz` 与 `now()`；检查 status 是否为 'queued'                                                 |
| buildx 很慢（QEMU 模拟）                         | 只构建 api（web 静态可在 runner 构建后 scp），或接受首次慢、后续用缓存                                                             |

## 11. 产出记录（执行时填写）

- 异步导入：上传到 ready 耗时 \_\_ s；失败重试演示：通过 / 未通过
- 部署耗时（tag → /ready）：\_\_ 分钟
- 回滚演练：触发 tag \_**\_，回滚耗时 ** s
- v1.2.0 线上地址 /ready：\_\_\_\_
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day64 · W20 Task 1「场景评测集 + rubric + 人审表」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（worker + 手动 deploy.sh 部署 v1.2.0）。
