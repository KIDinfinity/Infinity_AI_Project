# Week 19 · TASKS

## Task 1：Postgres + Alembic + 认证 + 空间隔离（Day62 · 11-28）

### 做什么

compose 加 postgres:16；Alembic 初始化 + autogenerate 首个迁移（User/Workspace/Membership + 现有表加 workspace_id）；`/v1/auth/login`、`/v1/auth/logout`、`/v1/me`；owner 通过 `POST /v1/workspaces/{id}/members` 创建成员（无公开注册）；依赖 `get_current_user`、`get_workspace`（`X-Workspace-Id` + membership 校验）、`require_role`；仓储层强制 workspace_id；Qdrant 检索强制 must 过滤 + `workspace_id` keyword payload 索引；隔离测试；前端登录页 + 空间切换；移除 Caddy basic_auth。

### 为什么做

多租户与认证是 P3「可以给团队用」的门槛，也是 OWASP LLM02 / LLM08 防护的基础（跨空间泄露）。

### 资产锚点

- 模块：M11.1、M11.2、M4.5
- 版本：v1.2（数据与身份部分）

### 前置依赖

- Day59 ER 图 + ADR 0007 + 迁移方案
- 现有 SQLite 已按迁移方案备份并导出使用数据

### 具体执行步骤（概要，详见 day62_20261128/PLAN.md）

1. 备份 SQLite + 导出使用数据。
2. compose 加 postgres；`DATABASE_URL` 切换；Alembic init + autogenerate + upgrade。
3. auth.py（pwdlib argon2 + pyjwt + cookie）、routes/auth.py、CLI 建 owner。
4. rbac.py：`get_workspace`、`require_role`；repo.py 强制过滤；Qdrant 过滤 + 索引。
5. 隔离测试。
6. 前端登录页 + 空间切换；移除 basic_auth。

### 验收标准

- [ ] `alembic upgrade head` 在空库成功
- [ ] 401 / 404 / 403 三种拒绝都有测试
- [ ] 隔离测试（文档 / 运行 / 检索）通过
- [ ] 前端可登录、切换空间（P1）

### 完成后的产出

- `apps/api/alembic/`、`app/security/auth.py`、`app/security/rbac.py`、`app/routes/auth.py`、`app/db/repo.py`
- `tests/integration/test_isolation.py`
- `apps/web/src/pages/LoginPage.tsx`

### 求职映射

后端岗与 AI Platform 岗的核心题：认证、鉴权、多租户隔离。

### 如果时间不够 / 没有必要

- 前端登录页顺延；今天用 curl / pytest 证明即可。
- 使用数据迁移脚本（SQLite → PG）顺延为 P2，只要 JSONL 导出已完成证据不丢。
- 不做邀请链接 / 改密码页面。

---

## Task 2：异步导入 + 自动部署（v1.2）（Day63 · 11-29）

### 做什么

Job 表 + `app/worker.py`（同镜像不同 command，`SELECT ... FOR UPDATE SKIP LOCKED` 取任务，失败重试 3 次并记录 last_error）；`POST /v1/kb/ingest` 改为 202 + job_id；`.gitea/workflows/deploy.yml`：tag v\* → buildx linux/amd64 → 推 Gitea 容器仓库 → ssh 服务器 `alembic upgrade` + `docker compose pull && up -d` → /ready 冒烟 → 失败回滚上一 tag；secrets 配置；tag `v1.2.0`。

### 为什么做

异步导入解决大文档阻塞与失败可见性；自动部署让后续安全修复和 v2.0 可以「打 tag 即上线」，并成为 CI/CD 面试证据。

### 资产锚点

- 模块：M5.4、M2.1（异步化）、M5.5（回滚）
- 版本：**v1.2**

### 前置依赖

- Day62 Postgres 已就绪
- W7 云服务器 + ssh + Caddy；W7 Gitea Actions runner 可用
- Gitea Packages（容器仓库）已启用

### 具体执行步骤（概要，详见 day63_20261129/PLAN.md）

1. Job 模型 + Alembic 迁移。
2. worker.py：claim SQL + handler + 重试。
3. ingest 路由改 202；前端状态轮询沿用 W6。
4. compose 增加 worker 服务。
5. deploy.sh（ssh 反向隧道访问本机 Gitea 仓库 + 回滚）+ deploy.yml + secrets。
6. 演练：正常部署 + 故意失败回滚；tag v1.2.0。

### 验收标准

- [ ] 上传 → 202 → worker 处理 → ready
- [ ] 制造失败 → 3 次后 failed + last_error
- [ ] 推 tag 自动部署成功；故意失败时回滚成功
- [ ] `v1.2.0` 已部署到服务器

### 完成后的产出

- `apps/api/app/worker.py`、`apps/api/app/jobs/ingest.py`
- `.gitea/workflows/deploy.yml`、`deploy/scripts/deploy.sh`
- `docs/runbook.md`（部署 / 回滚节）

### 求职映射

「无 Redis 任务队列 + tag 即部署 + 自动回滚」——中小团队后端/平台岗高频追问。

### 如果时间不够 / 没有必要

- workflow 自动触发顺延；先手动执行 `deploy.sh v1.2.0` 跑通。
- 卡死任务回收（locked_at 超时重排队）进 Backlog。

---
