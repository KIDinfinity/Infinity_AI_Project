# Week 19 · Postgres + 认证 + 多空间 + 自动部署（Phase 3 · Day62–Day63 · 11-28 → 11-29）

## 1. 本周核心目标

把 WorkPilot 从「单用户 SQLite + basic_auth」升级为「Postgres 16 + Alembic + JWT cookie 登录 + owner/member/viewer 角色 + 空间数据隔离」，KB 导入改为 Postgres 任务表 + worker 异步处理，并打通 **tag v\* → 构建镜像 → 推 Gitea 容器仓库 → ssh 部署 → /ready 冒烟 → 失败回滚**，发布 **v1.2.0**。

## 2. 资产锚点

| 构建模块                                                                   | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                                                                                                           |
| -------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M11.1 认证、M11.2 数据隔离、M4.5 登录与空间切换、M5.4 CI/CD、M2.1 异步导入 | **v1.2**   | 两个账号分别登录，看不到对方空间的文档/运行/检索结果（有自动化测试）；上传文档后状态从 queued → processing → ready；`git push origin v1.2.0` 后服务器自动更新并通过冒烟 |

## 3. 为什么这一周存在

- 「能给团队用」的前提是认证与隔离；这是 Demo 与生产系统的分水岭，也是 AI Platform 岗位必问。
- 同步导入大文档会阻塞请求；异步任务是后端工程基本功。
- 手动部署不可重复；W21 安全修复、W22 v2.0 都需要「打 tag 即上线」。
- 只有 2 天：Day62 数据与身份，Day63 任务与交付。

## 4. 本周在路线中的位置

```text
上周产出（W18）：SP-B 场景图 + ScenarioPage + v1.1.0（单用户、workspace_id 写死 default）
        ↓
本周（W19）：Postgres + Alembic + JWT/argon2 + RBAC + 仓储层/Qdrant 强制过滤 + 隔离测试 + 登录页
             Job 表 + SKIP LOCKED worker + deploy.yml（Gitea 容器仓库 + ssh + 冒烟 + 回滚）→ v1.2.0
        ↓
下周输入（W20）：场景评测需要按空间跑；EvalRun 表进入 Postgres；审批编辑 diff 写 Feedback
```

## 5. 每日安排

| Day   | 日期  | Task                                         | 当日 P0 产出                                                                               | 模块        | 状态 |
| ----- | ----- | -------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------- | ---- |
| Day62 | 11-28 | Task 1：Postgres + Alembic + 认证 + 空间隔离 | compose postgres:16 + 首个 Alembic 迁移 + login/logout/me + `get_workspace` + 隔离测试通过 | M11.1 M11.2 | TODO |
| Day63 | 11-29 | Task 2：异步导入 + 自动部署（v1.2）          | Job 表 + worker + `.gitea/workflows/deploy.yml` 跑通一次 + tag `v1.2.0`                    | M5.4 / v1.2 | TODO |

## 6. 本周必须留下的资产

- `deploy/docker-compose.yml`、`deploy/docker-compose.prod.yml`（+ postgres、+ worker）
- `apps/api/alembic.ini`、`apps/api/alembic/env.py`、`apps/api/alembic/versions/*.py`
- `apps/api/app/security/{auth.py, rbac.py}`、`apps/api/app/routes/auth.py`
- `apps/api/app/db/repo.py`（强制 workspace_id 的仓储层）
- `apps/api/tests/integration/test_isolation.py`
- `apps/api/app/worker.py`、`apps/api/app/jobs/ingest.py`
- `.gitea/workflows/deploy.yml`、`deploy/scripts/deploy.sh`
- `apps/web/src/pages/LoginPage.tsx`、空间切换组件
- `docs/runbook.md` 更新（Postgres、worker、部署、回滚）
- tag `v1.2.0`

## 7. 本周验收标准

- [ ] PASS / FAIL：`alembic upgrade head` 在空 Postgres 上建出全部表
- [ ] PASS / FAIL：未登录访问 `/v1/kb/docs` 返回 401；非成员访问他人空间返回 404
- [ ] PASS / FAIL：隔离测试通过：A 读不到 B 的文档、运行、检索结果
- [ ] PASS / FAIL：viewer 启动 SP-B 写场景返回 403
- [ ] PASS / FAIL：上传文档立即返回 202 + job_id，worker 处理后状态 ready；失败重试 3 次后 failed 且有 last_error
- [ ] PASS / FAIL：推 tag 后服务器自动部署并 /ready 通过；人为制造冒烟失败能回滚到上一 tag
- [ ] PASS / FAIL：Caddy basic_auth 已移除，公网只能通过登录访问

## 8. 求职映射

- 本周能力：关系数据库迁移、认证鉴权（JWT/cookie/argon2）、RBAC、多租户隔离、任务队列、CI/CD、回滚。
- 简历 bullet 草稿：
  - 「将单用户应用升级为多租户：Postgres 16 + Alembic、JWT httpOnly cookie + argon2、owner/member/viewer RBAC，仓储层与向量检索双重强制 workspace_id 过滤，隔离用例进入 CI」
  - 「基于 Postgres `FOR UPDATE SKIP LOCKED` 实现无 Redis 的异步导入队列（重试 3 次 + 错误记录）；Gitea Actions 实现 tag 即部署 + 冒烟失败自动回滚」
- 面试题：
  1. JWT 放 localStorage 还是 cookie？（答要点：httpOnly cookie 防 XSS 读取；SameSite=Lax 降低 CSRF；配合自定义 header 进一步防跨站）
  2. 为什么不用 Redis/Celery 做队列？（答要点：规模小、已有 Postgres；SKIP LOCKED 支持多 worker 并发安全取任务，少一个组件少一份运维）
  3. 部署失败怎么回滚？数据库迁移呢？（答要点：记录上一镜像 tag 回切；迁移只做向前兼容的 expand 变更，回滚镜像不需要回滚 schema）

## 9. 本周禁止事项

- 不做 OAuth / SSO / 邮件找回密码 / 公开注册。
- 不引入 Redis、Celery、Kafka、K8s。
- 不把每个空间拆成独立 Qdrant collection（ADR 0007 已决定）。
- 不把服务器私钥、数据库密码、JWT 密钥写进仓库或 workflow 明文。

## 10. 时间不够时（最小保留）

- Day62：Postgres + Alembic + 后端认证 + 隔离测试（登录页可先用 curl 演示，前端顺延到 Day63 P2 或 Day64 开头）。
- Day63：worker + 手动 `deploy.sh` 跑通（workflow 自动触发可顺延，但 v1.2.0 tag 必须打）。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（预期：双账号隔离演示 + tag 即部署）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
