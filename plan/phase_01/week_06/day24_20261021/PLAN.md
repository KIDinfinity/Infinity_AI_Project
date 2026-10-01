# Day 24 · 2026-10-21 · Week 06 Task 3：会话历史（SQLite）+ 反馈

## 0. 今天只做一件事

用 SQLModel + SQLite 保存会话 / 消息 / 反馈：刷新页面后历史仍在、可续问；每条答案可 👍/👎（👎 必选原因）；差评可一键导出为 badcase 候选。

不碰：Alembic 迁移（W19）、Postgres（W19）、登录 / 多用户（W19）、会话重命名 / 删除、上传（Day25）。

## 1. 资产锚点

- 构建模块：M4.1 Chat（历史 + 反馈 UI）、M3.6 在线反馈闭环（入库 + 导出）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.4 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：左侧历史会话列表；每条答案下 👍/👎；`feedback` 表可查询；`export_feedback` 产出 `eval/badcases/candidates-YYYYMMDD.jsonl`
- 今日 AI 实际应用：把「用户反馈」变成 RAG 评测数据（M3.4 badcase 池的在线来源）——这是生产 LLM 应用持续改进的标准做法

## 2. 起点（前置确认）

- 已有：Day23 流式问答 + 引用面板；`app/core/config.py`（pydantic-settings）；`eval/` 下 W5 的 badcases。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
grep -n "lifespan\|on_event" app/main.py      # 有无 lifespan，决定 Step 2 怎么挂 init_db
grep -n "^data\|data/" ../../.gitignore        # 确认 apps/api/data/ 会被忽略（未忽略则今天加上）
which sqlite3                                  # macOS 自带
```

## 3. 验收对齐（做完要能勾掉）

- [ ] 启动 API 后自动生成 `apps/api/data/workpilot.db`，含 conversation / message / feedback 三张表
- [ ] 问两轮 → 刷新浏览器 → 左侧出现该会话，点击恢复全部消息（含引用），可继续追问
- [ ] 👎 时必须选原因（wrong / no_citation / irrelevant / incomplete / other）才能提交；同一消息再次评价为更新而非新增
- [ ] `uv run python -m scripts.export_feedback` 生成 jsonl，每行含 question / answer / reason
- [ ] `uv run pytest` 新增的会话 / 反馈测试通过
- [ ] 已 commit + push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                               |
| ------- | ------ | -------------------------------------------------- |
| 0–10    | P0     | 前置确认，`uv add sqlmodel`                        |
| 10–30   | P0     | `db/models.py` + `db/session.py` + lifespan 建表   |
| 30–55   | P0     | `crud.save_turn` + ask / stream 落库（done 带 id） |
| 55–70   | P0     | 会话 / 消息 / 反馈路由 + 2 个 pytest               |
| 70–100  | P0     | 前端历史侧栏 + FeedbackBar                         |
| 100–110 | P0     | 导出脚本 + 提交                                    |
| 110–120 | P1     | 会话标题取首问前 30 字；P2：按今天 / 更早分组      |

时间不足时最低保留：消息 + 反馈入库（后端）+ FeedbackBar；侧栏可顺延。

## 5. 今日学习（只学完成任务必须的）

- SQLModel = Pydantic 模型 + SQLAlchemy 表，`table=True` 的类即是表，也可直接做响应模型。
- `SQLModel.metadata.create_all()` 只建**不存在的表**，不会给已有表加列——这就是 W19 要引入 Alembic 的原因。
- SQLite 在多线程（FastAPI 线程池）下需 `check_same_thread=False`；每个请求一个 Session（依赖注入）。
- 流式响应的生成器里**不要复用请求依赖注入的 Session**，自己 `with Session(engine)` 开新的，避免依赖清理时机问题。
- 资料：https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/ 、https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/ 、https://fastapi.tiangolo.com/advanced/events/ 、https://www.sqlite.org/lang.html

## 6. 执行步骤

### Step 1 · 数据模型（apps/api/app/db/models.py）——字段设计必须自己定

```bash
cd ~/lab/workpilot/apps/api && uv add sqlmodel && mkdir -p app/db && touch app/db/__init__.py
```

```python
import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    title: str = Field(default="新会话", max_length=200)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow, index=True)


class Message(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str = Field(max_length=16)                 # user / assistant
    content: str
    citations_json: str | None = None                # json.dumps(list[Citation])
    usage_json: str | None = None                    # tokens / cost / latency（W3 计量结果）
    created_at: datetime = Field(default_factory=utcnow)


class FeedbackRating(str, Enum):
    up = "up"
    down = "down"


class FeedbackReason(str, Enum):
    wrong = "wrong"                  # 答案事实错误
    no_citation = "no_citation"      # 没有引用 / 引用对不上
    irrelevant = "irrelevant"        # 答非所问 / 检索跑偏
    incomplete = "incomplete"        # 不完整
    other = "other"


class Feedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message_id: str = Field(foreign_key="message.id", unique=True, index=True)  # 一条消息一个反馈，再评即更新
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=utcnow)
```

### Step 2 · Session（apps/api/app/db/session.py）+ 启动建表

`config.py` 增加 `database_url: str = "sqlite:///data/workpilot.db"`（相对 `apps/api` 运行目录；Day26 容器里改为 `sqlite:////app/data/workpilot.db`）。

```python
from collections.abc import Iterator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)


def init_db() -> None:
    """W6–W18：create_all；W19 换 Postgres 后改为 Alembic 迁移。"""
    if settings.database_url.startswith("sqlite:///"):
        Path(settings.database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    from app.db import models  # noqa: F401  确保模型已注册到 metadata
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

`main.py`：用 `@asynccontextmanager async def lifespan(app): init_db(); yield`，`FastAPI(lifespan=lifespan)`。`.gitignore` 加 `apps/api/data/`。

### Step 3 · 保存一轮问答（app/db/crud.py）+ 接入 ask / stream

```python
import json
from sqlmodel import Session
from app.db.models import Conversation, Message, utcnow


def save_turn(session: Session, conversation_id: str | None, question: str, answer: str,
              citations: list[dict], usage: dict | None) -> tuple[str, str]:
    conv = session.get(Conversation, conversation_id) if conversation_id else None
    if conv is None:
        conv = Conversation(title=question[:30])
        session.add(conv)
    conv.updated_at = utcnow()
    session.add(Message(conversation_id=conv.id, role="user", content=question))
    ans = Message(conversation_id=conv.id, role="assistant", content=answer,
                  citations_json=json.dumps(citations, ensure_ascii=False),
                  usage_json=json.dumps(usage or {}, ensure_ascii=False))
    session.add(ans)
    session.commit()
    return conv.id, ans.id
```

- `/v1/kb/ask`：请求模型加 `conversation_id: str | None = None`；用 `Depends(get_session)` 调 `save_turn`，响应加 `conversation_id`、`message_id`。
- `/v1/kb/ask/stream`：生成器里累积 token；在 yield `done` **之前** `with Session(engine) as s: cid, mid = save_turn(s, ...)`，把 `conversation_id`、`message_id` 放进 done 的 data。前端 `start(question, { conversation_id })`，从 `r.done` 读 id。

### Step 4 · 路由（app/routes/conversations.py）

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, col, select

from app.db.models import Conversation, Feedback, FeedbackRating, FeedbackReason, Message
from app.db.session import get_session

router = APIRouter(prefix="/v1", tags=["conversations"])


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class FeedbackIn(BaseModel):
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = Field(default=None, max_length=1000)


@router.get("/conversations", response_model=list[Conversation])
def list_conversations(limit: int = Query(50, le=200), s: Session = Depends(get_session)):
    return s.exec(select(Conversation).order_by(col(Conversation.updated_at).desc()).limit(limit)).all()


@router.post("/conversations", response_model=Conversation, status_code=201)
def create_conversation(body: ConversationCreate, s: Session = Depends(get_session)):
    conv = Conversation(title=body.title or "新会话")
    s.add(conv); s.commit(); s.refresh(conv)
    return conv


@router.get("/conversations/{conv_id}/messages", response_model=list[Message])
def list_messages(conv_id: str, s: Session = Depends(get_session)):
    if not s.get(Conversation, conv_id):
        raise HTTPException(404, "conversation not found")
    return s.exec(select(Message).where(Message.conversation_id == conv_id)
                  .order_by(col(Message.created_at))).all()


@router.post("/messages/{message_id}/feedback", response_model=Feedback, status_code=201)
def give_feedback(message_id: str, body: FeedbackIn, s: Session = Depends(get_session)):
    msg = s.get(Message, message_id)
    if msg is None or msg.role != "assistant":
        raise HTTPException(404, "assistant message not found")
    if body.rating == FeedbackRating.down and body.reason is None:
        raise HTTPException(422, "reason is required for down rating")
    fb = s.exec(select(Feedback).where(Feedback.message_id == message_id)).first() \
        or Feedback(message_id=message_id, rating=body.rating)
    fb.rating, fb.reason, fb.comment = body.rating, body.reason, body.comment
    s.add(fb); s.commit(); s.refresh(fb)
    return fb
```

`main.py` 挂载 `app.include_router(conversations.router)`。测试 `tests/test_conversations.py`：用 `app.dependency_overrides[get_session]` 指向 `sqlite://`（内存库，配 `poolclass=StaticPool`），测「👎 无 reason → 422」「再次评价 → 仍只有 1 条」。

### Step 5 · 前端历史 + 反馈

```bash
cd ~/lab/workpilot && make web-types      # API 已启动时重新生成类型
```

- `api/client.ts` 增加 `listConversations()`、`listMessages(id)`、`sendFeedback(id, body)`。
- `components/ConversationList.tsx`：左栏 `w-60`，「+ 新会话」按钮（清空当前 `conversationId` 与消息）；点击条目 → `listMessages` → 把 `citations_json` `JSON.parse` 后放回消息。
- `components/FeedbackBar.tsx`：👍 直接提交；👎 展开 `<select>`（5 个原因，中文标签）+ 可选备注 + 「提交」；提交后显示「已反馈」并禁用。
- ChatPage 布局：`grid-cols-[240px_1fr_320px]`；`start(question, { conversation_id })`；done 后保存返回的 `conversation_id`、`message_id` 并刷新左侧列表。

### Step 6 · 差评导出（apps/api/scripts/export_feedback.py）

脚本要 `import app`，所以放在 `apps/api/scripts/`，从 `apps/api` 以模块方式运行。

```python
"""导出 👎 反馈为 badcase 候选：cd apps/api && uv run python -m scripts.export_feedback"""
import json
from datetime import date
from pathlib import Path

from sqlmodel import Session, col, select

from app.db.models import Feedback, FeedbackRating, Message
from app.db.session import engine

OUT = Path(__file__).resolve().parents[3] / "eval" / "badcases" / f"candidates-{date.today():%Y%m%d}.jsonl"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with Session(engine) as s, OUT.open("w", encoding="utf-8") as f:
        for fb in s.exec(select(Feedback).where(Feedback.rating == FeedbackRating.down)):
            ans = s.get(Message, fb.message_id)
            q = s.exec(select(Message).where(Message.conversation_id == ans.conversation_id,
                                             Message.role == "user",
                                             col(Message.created_at) <= ans.created_at)
                       .order_by(col(Message.created_at).desc())).first()
            f.write(json.dumps({"question": q.content if q else None, "answer": ans.content,
                                "citations": json.loads(ans.citations_json or "[]"),
                                "reason": fb.reason, "comment": fb.comment,
                                "message_id": ans.id, "created_at": fb.created_at.isoformat()},
                               ensure_ascii=False) + "\n")
            n += 1
    print(f"exported {n} candidates → {OUT}")


if __name__ == "__main__":
    main()
```

自测：故意问 3 个答不好的问题并 👎，运行脚本，挑 1 条按 W5 的分类法写进 `eval/badcases/badcases.md`（闭环走一遍）。

### Step 7 · 提交

```bash
cd ~/lab/workpilot && uv --directory apps/api run pytest -q
git add apps/api apps/web eval/badcases .gitignore
git commit -m "feat: persist conversations and feedback in sqlite, export downvotes as badcase candidates"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. `create_all` 能不能给已有的 `message` 表加一列？（答：不能，只建不存在的表；要么删库重建（开发期），要么 Alembic 迁移（W19））
2. 为什么 `citations_json` 存成字符串而不是关系表？（答：引用是答案的快照，只读不查询；SQLite 下 JSON 字符串最简单，W19 Postgres 可改 JSONB）
3. 为什么流式接口要在发送 done **之前**落库？（答：前端需要 done 中的 `message_id` 才能提交反馈）
4. 👎 为什么必须带原因？（答：没有原因的差评无法归因到检索 / 生成 / 语料，不能转成可修复的 badcase）
5. Feedback 的 `message_id` 为什么 unique？（答：一条答案只保留用户最终评价，避免重复计数，统计口径清晰）

## 8. 对 DA-01 的贡献

F2「多轮对话、历史记录、👍/👎 + 原因反馈 → 自动进入 Badcase 池」落地前半段。WorkPilot 第一次有了业务数据库，W10 Agent 运行记录、W15 trace 表、W19 用户 / 空间都在这套 `app/db` 上扩展。

## 9. 求职映射（D 线）

- 岗位能力：数据建模、FastAPI 依赖注入、LLM 应用反馈闭环
- 对应岗位：AI Engineer / AI Full-Stack Engineer
- 简历 bullet 草稿：设计会话 / 消息 / 反馈数据模型（SQLModel），实现 👍/👎 + 5 类原因的用户反馈采集，差评一键导出为评测候选，首周将 ** 条线上差评转化为 ** 条回归用例。
- 面试可能问：
  - 「上线后怎么持续提升 RAG 质量？」要点：反馈采集（带原因）→ 导出候选 → 人工归因 → 进评测集 → 改检索 / Prompt → 回归对比。
  - 「为什么现在用 SQLite？」要点：单机单用户足够、零运维；接口通过 SQLModel 抽象，W19 换 Postgres 只改连接串 + 迁移。

## 10. 卡住时的处理

| 现象                                                                      | 处理                                                                                      |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `sqlite3.OperationalError: unable to open database file`                  | `data/` 目录不存在或运行目录不是 `apps/api`：确认 `init_db` 里 `mkdir` 执行、或用绝对路径 |
| `SQLite objects created in a thread can only be used in that same thread` | `create_engine` 缺 `connect_args={"check_same_thread": False}`                            |
| 改了模型字段，但表结构没变                                                | `create_all` 不改已有表：开发期直接删 `apps/api/data/workpilot.db` 重启                   |
| 流式接口落库报 `Instance is not bound to a Session` / Session 已关闭      | 生成器里不要用 `Depends(get_session)` 的会话，改 `with Session(engine) as s:`             |
| `ModuleNotFoundError: No module named 'app'`（导出脚本）                  | 必须在 `apps/api` 下用 `uv run python -m scripts.export_feedback` 运行                    |
| 前端 `citations_json` 显示为字符串                                        | 加载历史时需 `JSON.parse(m.citations_json ?? '[]')`                                       |

## 11. 产出记录（执行时填写）

- 三张表行数（`sqlite3 apps/api/data/workpilot.db "select count(*) from message"`）：\_\_\_\_
- 导出的候选条数 / 转入 badcases.md 条数：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → 明天进入 Day25（知识库管理页 + E2E 冒烟 + v0.4.0）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
