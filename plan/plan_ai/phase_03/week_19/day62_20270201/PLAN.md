# Day 62 · 2027-02-01 · Week 19 Task 1：Postgres + Alembic + 认证 + 空间隔离

## 0. 今天只做一件事

切到 Postgres 16 + Alembic，加上 JWT httpOnly cookie 登录与 owner/member/viewer 角色，让所有数据访问（DB + Qdrant）强制按 `workspace_id` 过滤，并用自动化测试证明两个空间互不可见。

不碰：异步导入 / 部署流水线（Day63）、OAuth / SSO / 公开注册 / 找回密码、PostgresSaver（checkpointer 继续用 SqliteSaver）。

## 1. 资产锚点

- 构建模块：M11.1 认证 JWT + 用户 / 空间 / 角色、M11.2 数据隔离、M4.5 登录与空间切换（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：v1.2（数据与身份部分）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：两个账号登录各自空间，互相看不到文档、运行、检索结果；`pytest tests/integration/test_isolation.py` 绿
- 今日 AI 实际应用：RAG 检索层的租户隔离（Qdrant payload 过滤）——防 OWASP LLM08 Vector and Embedding Weaknesses 中的跨租户泄露

## 2. 起点（前置确认）

- 已有：SQLModel 模型（9 张表）、Day59 ER 图与迁移方案、Caddy basic_auth、W12 SqliteSaver。
- 需确认 + 先备份（**P0 第一件事**）：

```bash
cd ~/lab/workpilot
DB=apps/api/data/workpilot.db                          # 以 .env 中 DATABASE_URL 为准
mkdir -p ~/lab/backup && cp $DB ~/lab/backup/workpilot-20270201.db
for t in conversation message feedback agentrun; do
  sqlite3 -json $DB "select * from $t" > ~/lab/backup/$t-20270201.json
done
ls -lh ~/lab/backup/                                    # 4 个 json + 1 个 db
docker compose -f deploy/docker-compose.yml ps          # qdrant / minio 在跑
```

> 这些 JSON 是半年验收「真实使用 ≥ 30 次」的证据，放 `~/lab/backup/`（不进公开仓库）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `docker compose up -d postgres` 健康；`alembic upgrade head` 在空库建出全部表（含 user / workspace / membership）
- [ ] `POST /v1/auth/login` 设置 `wp_session` cookie（HttpOnly、SameSite=Lax）；`/v1/me` 返回用户与空间列表；`logout` 清 cookie
- [ ] 未登录 → 401；非成员 `X-Workspace-Id` → 404；viewer 启动 SP-B → 403（3 个测试）
- [ ] 仓储层所有查询经 `WorkspaceRepo`；Qdrant 检索带 `must workspace_id`，且已建 keyword payload 索引
- [ ] `test_isolation.py`：A 读不到 B 的文档、运行、检索结果 —— 通过
- [ ] （P1）前端登录页 + 空间切换；Caddy basic_auth 移除

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                 |
| ----------- | ------ | -------------------------------------------------------------------- |
| 0–10 min    | P0     | 备份 + 导出（第 2 节命令）                                           |
| 10–30 min   | P0     | compose postgres + 依赖 + Alembic init/autogenerate/upgrade          |
| 30–55 min   | P0     | auth.py + routes/auth.py + CLI 建 owner/空间                         |
| 55–80 min   | P0     | rbac.py（get_workspace / require_role）+ repo.py + Qdrant 过滤与索引 |
| 80–100 min  | P0     | 隔离测试 + 401/404/403 测试                                          |
| 100–115 min | P1     | 前端 LoginPage + 空间切换 + 移除 basic_auth                          |
| 115–120 min | P0     | 提交                                                                 |
| 顺延        | P2     | SQLite → PG 使用数据迁移脚本、owner 添加成员页面、改密码 → Backlog   |

时间不足时最低保留：Postgres + Alembic + 后端登录 + get_workspace + 隔离测试。

## 5. 今日学习（只学完成任务必须的）

- **Alembic + SQLModel**：`env.py` 里 `target_metadata = SQLModel.metadata` 并 import 全部模型；`script.py.mako` 加 `import sqlmodel`，否则 autogenerate 出的 `AutoString` 报错。
- **密码哈希**：argon2id（`pwdlib[argon2]` 的 `PasswordHash.recommended()`），只存哈希；登录失败统一返回「用户名或密码错误」。
- **JWT in cookie**：pyjwt `encode/decode(algorithms=["HS256"])` 必须显式指定算法；cookie `HttpOnly` 防 XSS 读取，`SameSite=Lax` 挡大部分跨站 POST，生产 `Secure`。
- **租户来自鉴权，不来自信任**：`X-Workspace-Id` 只是「选择」，必须校验 membership；非成员返回 404 不暴露空间是否存在。
- 资料：https://alembic.sqlalchemy.org/ 、https://fastapi.tiangolo.com/tutorial/security/ 、https://qdrant.tech/documentation/guides/multiple-partitions/ 、https://www.postgresql.org/docs/

## 6. 执行步骤

### Step 1 · Postgres + Alembic（P0）

`deploy/docker-compose.yml` 增加：

```yaml
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: workpilot
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set in .env}
      POSTGRES_DB: workpilot
    volumes: ["pgdata:/var/lib/postgresql/data"]
    ports: ["127.0.0.1:5432:5432"]          # 只绑本机
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U workpilot"]
      interval: 5s
      retries: 10
volumes:
  pgdata:
```

```bash
cd ~/lab/workpilot/apps/api
uv add "psycopg[binary]" alembic pyjwt "pwdlib[argon2]"
# .env: DATABASE_URL=postgresql+psycopg://workpilot:<pwd>@localhost:5432/workpilot
docker compose -f ../../deploy/docker-compose.yml up -d postgres
uv run alembic init alembic
```

`alembic/env.py` 关键改动：

```python
from sqlmodel import SQLModel
from app.core.config import settings
from app.db import models  # noqa: F401  确保所有表注册到 metadata
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = SQLModel.metadata
```

`alembic/script.py.mako` 顶部 import 区加 `import sqlmodel`。

在 `app/db/models.py` 新增 User / Workspace / Membership（字段见 Day59 ER 图），并给 KBDocument、Conversation、Message、Feedback、AgentRun、AgentStep、Trace、Span、LLMCall 加 `workspace_id: uuid.UUID = Field(index=True)`；AgentStep 加 `idem_key: str | None = Field(default=None, unique=True)`。

```bash
uv run alembic revision --autogenerate -m "init schema with workspaces"
# 打开生成文件人工检查：表、外键、索引、unique 是否齐全
uv run alembic upgrade head
docker compose -f ../../deploy/docker-compose.yml exec postgres psql -U workpilot -c '\dt'
```

### Step 2 · 认证（P0，核心逻辑自己写）

```python
# app/security/auth.py
import datetime as dt
import jwt
from fastapi import Depends, HTTPException, Request
from pwdlib import PasswordHash
from sqlmodel import Session
from app.core.config import settings
from app.db.session import get_session
from app.db.models import User

ph = PasswordHash.recommended()       # argon2id
COOKIE = "wp_session"
ALG = "HS256"

def hash_password(p: str) -> str: return ph.hash(p)
def verify_password(p: str, h: str) -> bool: return ph.verify(p, h)

def create_token(user_id: str) -> str:
    now = dt.datetime.now(dt.UTC)
    return jwt.encode({"sub": user_id, "iat": now, "exp": now + dt.timedelta(hours=12)},
                      settings.jwt_secret, algorithm=ALG)

def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    token = request.cookies.get(COOKIE)
    if not token:
        raise HTTPException(401, "not authenticated")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALG])
    except jwt.InvalidTokenError:
        raise HTTPException(401, "invalid session")
    user = session.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(401, "invalid session")
    return user
```

```python
# app/routes/auth.py
@router.post("/v1/auth/login")
def login(body: LoginIn, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email.lower())).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "用户名或密码错误")          # 不区分哪一个错
    response.set_cookie(COOKIE, create_token(str(user.id)), httponly=True, samesite="lax",
                        secure=settings.cookie_secure, max_age=12 * 3600, path="/")
    return {"ok": True}

@router.post("/v1/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}

@router.get("/v1/me")
def me(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    rows = session.exec(select(Membership, Workspace).join(Workspace)
                        .where(Membership.user_id == user.id)).all()
    return {"email": user.email, "workspaces": [{"id": str(w.id), "name": w.name, "role": m.role} for m, w in rows]}
```

无公开注册：`uv run python -m app.cli create-owner --email me@example.com --workspace personal`（交互输入密码）；owner 通过 `POST /v1/workspaces/{id}/members`（require_role("owner")）创建成员账号并设临时密码。登录路由已有 slowapi，给 login 单独加 `5/minute`。

### Step 3 · 空间与角色依赖 + 仓储层（P0）

```python
# app/security/rbac.py
from dataclasses import dataclass
from fastapi import Depends, Header, HTTPException

@dataclass(frozen=True)
class WsCtx:
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: str                     # owner | member | viewer

def get_workspace(x_workspace_id: uuid.UUID = Header(...), user=Depends(get_current_user),
                  session=Depends(get_session)) -> WsCtx:
    m = session.exec(select(Membership).where(Membership.user_id == user.id,
                                              Membership.workspace_id == x_workspace_id)).first()
    if not m:
        raise HTTPException(404, "workspace not found")    # 不暴露存在性
    return WsCtx(x_workspace_id, user.id, m.role)

def require_role(*roles: str):
    def dep(ctx: WsCtx = Depends(get_workspace)) -> WsCtx:
        if ctx.role not in roles:
            raise HTTPException(403, "forbidden")
        return ctx
    return dep
```

```python
# app/db/repo.py —— 业务代码只能通过它访问带 workspace_id 的表
class WorkspaceRepo:
    def __init__(self, session: Session, ctx: WsCtx):
        self.s, self.ws = session, ctx.workspace_id
    def list(self, model, *where, limit=50):
        return self.s.exec(select(model).where(model.workspace_id == self.ws, *where).limit(limit)).all()
    def get(self, model, obj_id):
        obj = self.s.get(model, obj_id)
        return obj if obj and obj.workspace_id == self.ws else None   # 跨空间 = 不存在
    def add(self, obj):
        obj.workspace_id = self.ws                                    # 永远以 ctx 为准
        self.s.add(obj); return obj
```

路由改造规则：读接口 `Depends(get_workspace)`，写 KB `require_role("owner","member")`，启动 SP-B `require_role("owner","member")`（viewer → 403）。场景图 state 的 `workspace_id` 从 ctx 传入（替换 Day60 的 `"default"`）。

Qdrant（`app/rag/store.py`）：

```python
from qdrant_client import models
client.create_payload_index(COLLECTION, field_name="workspace_id",
    field_schema=models.KeywordIndexParams(type="keyword", is_tenant=True))

def search(workspace_id: str, vector, top_k=5):
    flt = models.Filter(must=[models.FieldCondition(key="workspace_id",
                                                    match=models.MatchValue(value=workspace_id))])
    hits = client.query_points(COLLECTION, query=vector, query_filter=flt, limit=top_k).points
    assert all(h.payload.get("workspace_id") == workspace_id for h in hits)   # W21 改为记录+拒绝
    return hits
```

旧向量没有 `workspace_id`：按迁移方案把 KB 重新导入到 owner 的 personal 空间（可重建数据）。

### Step 4 · 隔离测试（P0）

```python
# tests/integration/test_isolation.py（需要 compose 中的 postgres + qdrant）
def test_docs_runs_search_isolated(login_as, seed):
    a, b = login_as("a@test.local"), login_as("b@test.local")
    ws_a, ws_b = seed.ws_a, seed.ws_b
    b.post("/v1/kb/ingest", headers={"X-Workspace-Id": ws_b},
           files={"file": ("secret.md", b"# B only\nZEBRA-42 is the code.")})
    assert a.get("/v1/kb/docs", headers={"X-Workspace-Id": ws_b}).status_code == 404
    docs = a.get("/v1/kb/docs", headers={"X-Workspace-Id": ws_a}).json()
    assert all("secret.md" != d["filename"] for d in docs)
    r = a.post("/v1/kb/search", headers={"X-Workspace-Id": ws_a}, json={"query": "ZEBRA-42"})
    assert "ZEBRA-42" not in r.text
    run_b = seed.agent_run_in(ws_b)
    assert a.get(f"/v1/agent/runs/{run_b}", headers={"X-Workspace-Id": ws_a}).status_code == 404

def test_unauthenticated_401(client): assert client.get("/v1/me").status_code == 401
def test_viewer_cannot_run_write_scenario(login_as, seed):
    v = login_as("viewer@test.local")
    r = v.post("/v1/scenarios/sp_b/runs", headers={"X-Workspace-Id": seed.ws_a}, json={"requirement": "x"})
    assert r.status_code == 403
```

> 测试库用独立数据库 `workpilot_test`（`createdb` 一次），fixture 中 `alembic upgrade head`；Qdrant 测试用独立 collection 名。检索接口名以你 W4/W9 实际路由为准。

### Step 5 · 前端登录 + 空间切换 + 移除 basic_auth（P1）

- `LoginPage.tsx`：email/password 表单 → `fetch("/api/v1/auth/login", {method:"POST", credentials:"include"})` → 跳转。
- 全局 `api()` 包装：`credentials: "include"`，自动带 `X-Workspace-Id`（存 localStorage 的「当前空间 id」不是敏感数据）；收到 401 跳登录页。
- 顶栏空间下拉：数据来自 `/v1/me`。
- `deploy/Caddyfile` 删除 `basic_auth` 块；prod `.env` 设 `COOKIE_SECURE=true`、强随机 `JWT_SECRET`（`openssl rand -hex 32`）。

> MCP Server 与 eval runners 之前直接调 API：今天给它们用一个 `eval@local` 成员账号登录拿 cookie（脚本里 `requests.Session()`）；长期方案（个人 API token）进 Backlog。

### Step 6 · 提交

```bash
cd ~/lab/workpilot
uv run --directory apps/api pytest -q
git add deploy/docker-compose.yml apps/api apps/web/src deploy/Caddyfile .env.example
git commit -m "feat(auth): postgres+alembic, jwt cookie auth, rbac and workspace isolation"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 `jwt.decode` 必须传 `algorithms`？（答：防止算法混淆攻击，如 `alg=none` 或用公钥当 HMAC 密钥）
2. httpOnly cookie 能防什么、不能防什么？（答：防 XSS 脚本读取 token；不能防 CSRF——靠 SameSite=Lax + 需要自定义 header 的接口触发 CORS 预检）
3. 非成员访问空间为什么返回 404 而不是 403？（答：不暴露资源存在性，防枚举）
4. 仓储层 `add()` 为什么覆盖 workspace_id？（答：永远以鉴权得到的上下文为准，客户端传来的 workspace_id 不可信）
5. Qdrant `is_tenant=true` 有什么作用？（答：告诉 Qdrant 按租户字段组织存储，提升同租户检索局部性与效率，适合单 collection 多租户）
6. 为什么 checkpointer 暂不换 PostgresSaver？（答：控制范围；SqliteSaver 文件放 volume 即可工作，备份时一并处理，迁移进 Backlog）

## 8. 对 DA-01 的贡献

WorkPilot 从「个人工具」变成「可以给一个小团队安全使用的系统」：有账号、有角色、有空间，数据隔离由代码结构和自动化测试保证。这是 P3「生产级」叙事的地基，也是 Pro Kit 卖点「认证 / 多空间」的来源。

## 9. 求职映射（D 线）

- 岗位能力：Postgres / Alembic 迁移、认证鉴权、RBAC、多租户隔离、测试驱动安全。
- 对应岗位：AI Platform Engineer、AI Full-Stack Engineer、Backend Engineer。
- 简历 bullet 草稿：「实现 JWT（httpOnly cookie）+ argon2 认证与 owner/member/viewer RBAC；仓储层与 Qdrant payload 过滤双重强制租户隔离，\_\_ 条隔离用例纳入 CI」
- 面试可能问：
  1. 多租户 SaaS 怎么防越权？——要点：身份来自 token；租户来自 membership 校验；仓储层统一过滤；对象级再校验；测试覆盖 401/403/404。
  2. Alembic autogenerate 能完全信任吗？——要点：不能；需人工检查重命名（会被识别为删+建）、索引、server_default、数据迁移需手写。

## 10. 卡住时的处理

| 现象                                                      | 处理                                                                                        |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| autogenerate 报 `sqlmodel.sql.sqltypes.AutoString` 未定义 | `script.py.mako` 加 `import sqlmodel`，重新生成                                             |
| autogenerate 生成空迁移                                   | `env.py` 没 import `app.db.models`，或 URL 指向了旧库                                       |
| `psycopg` 连接被拒                                        | compose 端口只绑 127.0.0.1；容器内用 `postgres:5432`，宿主机用 `localhost:5432`             |
| 登录后请求仍 401                                          | 前端未 `credentials: "include"`；或开发时前后端不同源导致 cookie 不发送——走 Vite proxy 同源 |
| Qdrant `KeywordIndexParams` 不存在                        | qdrant-client 版本旧：`uv add "qdrant-client>=1.11"`；或先用 `field_schema="keyword"`       |
| 超过 100 分钟还没跑通隔离测试                             | 前端全部顺延；只保后端 + 测试，明天 Day63 前 20 分钟补                                      |

## 11. 产出记录（执行时填写）

- 备份文件：\_**\_（会话 ** 条 / 反馈 \_\_ 条）
- Alembic revision id：\_\_\_\_
- 测试：隔离 ** / 401 ** / 404 ** / 403 **
- basic_auth 是否已移除：是 / 否
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节 P0 项全部勾上 → Task 1 DONE → 明天进入 Day63 · W19 Task 2「异步导入 + 自动部署（v1.2）」。任一 P0 未通过 → 保持 IN PROGRESS，明天先补 P0（迁移 / 认证 / 隔离测试）。
