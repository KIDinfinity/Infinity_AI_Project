# Day 43 · 2026-11-09 · Week 12 Task 1：会话记忆 + 上下文压缩

## 0. 今天只做一件事

让 Agent 在同一个会话里「记得上一轮说了什么」：`thread_id` 绑定 conversation，状态里保存对话消息与摘要，支持「把上一份报告第二点展开」这类追问；历史过长时自动压缩成摘要。

不碰：跨会话长期记忆（Day44）、审批（Day45）、多用户 / workspace 隔离（W19）。

## 1. 资产锚点

- 构建模块：M7.3 Memory —— 会话记忆（checkpointer）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.8 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：第一次 `POST /v1/agent/run` 返回 `X-Conversation-Id`；带上该 id 追问「把上一份报告第二点展开」，Agent 直接基于上一份报告展开；`tests/agent/test_conversation.py` 3 个用例（追问可见历史 / 单轮字段重置 / 超阈值压缩）全绿。
- 今日 AI 实际应用：上下文窗口管理（token 计数 + 滚动摘要 + 最近 k 轮原文）→ 用在 `app/agent/context.py` 与图中的 `summarize` 节点。

## 2. 起点（前置确认）

- 已有：W11 `build_graph(checkpointer)`、AsyncSqliteSaver（lifespan）、`runner.run_v1_events`；Day38 `AgentRun.conversation_id` 字段；phase_01 `Conversation` 表。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api && uv run pytest tests/agent -q
uv run python -c "from langgraph.graph.message import add_messages; from langchain_core.messages import RemoveMessage; print('ok')"
uv add tiktoken
grep -n "class Conversation" app/db/models.py
```

> `langchain_core` 是 LangGraph 的依赖，这里只用它的消息类型（HumanMessage / AIMessage / RemoveMessage），不使用任何 LangChain 模型类。

## 3. 验收对齐（做完要能勾掉）

- [ ] `ResearchState` 新增 `messages: Annotated[list[AnyMessage], add_messages]`、`summary: str`
- [ ] `observations` / `errors` 改为可重置 reducer；`new_turn_input()` 每轮重置单次运行字段
- [ ] `synthesize` 节点把报告 Markdown 作为 `AIMessage` 追加到 messages
- [ ] `context.py`：`count_tokens()`（tiktoken `cl100k_base` 近似）+ `history_for_prompt()`；`summarize` 节点超阈值时压缩，保留最近 `KEEP_LAST=4` 条
- [ ] planner / synthesizer 提示词带「对话历史」；planner 提示词升级 v1.2（追问规则）
- [ ] API：`RunIn.conversation_id` 可选；`thread_id = conversation_id`；同会话有 running / waiting_approval 运行时返回 409；响应头 `X-Conversation-Id`
- [ ] 3 个测试全绿；curl 追问演示成功；已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                        |
| ----------- | ------ | ----------------------------------------------------------- |
| 0–25 min    | P0     | state 改造 + `new_turn_input()` + synthesize 追加 AIMessage |
| 25–50 min   | P0     | `context.py` + `summarize` 节点 + `summarizer.v1.md`        |
| 50–65 min   | P0     | steps 注入历史 + planner v1.2                               |
| 65–85 min   | P0     | API conversation_id / 409 / 响应头                          |
| 85–105 min  | P0     | `test_conversation.py`                                      |
| 105–115 min | P1     | curl 追问演示；前端保存 conversationId +「新会话」按钮      |
| 115–120 min | P0     | 提交                                                        |

时间不足时最低保留：messages + thread 绑定 + 追问演示 + 追问测试（压缩只写测试，不演示）。

## 5. 今日学习（只学完成任务必须的）

- **thread_id 即会话**：同一 thread 的多次调用共享 checkpoint 中的状态；所以「每轮要重置的字段」必须在输入里显式重置。
- **add_messages**：按消息 id 追加或替换；返回 `RemoveMessage(id=...)` 可删除指定消息——这是压缩时丢弃旧消息的方式。
- **可重置 reducer**：`operator.add` 无法清空；自定义 reducer「收到 None 就清空」，否则第二轮会带着第一轮的观察。
- **滚动摘要**：旧消息 → 摘要（与已有摘要合并），最近 k 条保留原文；摘要会丢细节，所以只压缩「足够旧」的部分。
- **token 计数是近似**：DeepSeek 的分词器与 `cl100k_base` 不同，误差可接受；预算留 20% 余量。
- 资料：
  - https://langchain-ai.github.io/langgraph/ （Memory：short-term memory / manage message history；Persistence：threads）
  - https://github.com/openai/tiktoken

## 6. 执行步骤

### Step 1 · state 改造

`app/agent/state.py`：

```python
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages

def resettable_add(left: list | None, right: list | None) -> list:
    """收到 None 清空，否则追加。用于每轮需要重置的累积字段。"""
    if right is None:
        return []
    return (left or []) + right

class ResearchState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]     # 会话：用户任务 + 最终报告
    summary: str                                            # 更早对话的滚动摘要
    task: str
    plan: dict | None
    current_step: int
    pending_call: dict | None
    observations: Annotated[list[dict], resettable_add]
    errors: Annotated[list[str], resettable_add]
    decision: dict | None
    report: dict | None
    step_count: int
    replans: int
    seen_calls: dict[str, int]
    tokens_used: int
    cost_cny: float
    last_usage: dict | None
    stop_reason: str | None

def new_turn_input(task: str) -> dict:
    """每一轮运行的输入：追加用户消息，并重置所有单次运行字段（messages / summary 不重置）。"""
    return {"task": task, "messages": [HumanMessage(content=task)],
            "plan": None, "current_step": 0, "pending_call": None, "observations": None, "errors": None,
            "decision": None, "report": None, "step_count": 0, "replans": 0, "seen_calls": {},
            "tokens_used": 0, "cost_cny": 0.0, "last_usage": None, "stop_reason": None}
```

`initial_state()` 改为调用 `new_turn_input()`（保持 W11 调用点可用）。`synthesize_node` 返回值追加 `"messages": [AIMessage(content=md)]`。

### Step 2 · context.py + summarize 节点

```python
import tiktoken
from langchain_core.messages import AnyMessage, RemoveMessage
from app.llm.gateway import gateway
from app.prompts import load_prompt

_enc = tiktoken.get_encoding("cl100k_base")
HISTORY_TOKEN_BUDGET = 3000        # 超过即压缩（DeepSeek 上下文远大于此，这里控制的是成本与注意力）
KEEP_LAST = 4                      # 保留最近 4 条原文（约 2 轮）

def count_tokens(msgs: list[AnyMessage]) -> int:
    return sum(len(_enc.encode(str(m.content))) + 4 for m in msgs)

def history_for_prompt(st: dict, per_msg_limit: int = 3000) -> str:
    parts = [f"【更早对话摘要】\n{st['summary']}"] if st.get("summary") else []
    for m in st.get("messages", [])[:-1][-KEEP_LAST:]:            # 去掉最后一条（就是当前任务）
        role = "用户" if m.type == "human" else "WorkPilot"
        parts.append(f"【{role}】\n{str(m.content)[:per_msg_limit]}")
    return "\n\n".join(parts) or "（无）"

async def summarize_text(old_summary: str, msgs: list[AnyMessage]) -> str:
    convo = "\n".join(f"{m.type}: {str(m.content)[:2000]}" for m in msgs)
    res = await gateway.chat([{"role": "system", "content": load_prompt("summarizer", "v1")},
                              {"role": "user", "content": f"已有摘要：\n{old_summary or '（无）'}\n新增对话：\n{convo}"}])
    return res.content                                           # 以 Gateway 返回结构为准

async def summarize_node(st: dict) -> dict:
    msgs = st.get("messages", [])
    if len(msgs) <= KEEP_LAST or count_tokens(msgs) <= HISTORY_TOKEN_BUDGET:
        return {}
    old, _ = msgs[:-KEEP_LAST], msgs[-KEEP_LAST:]
    summary = await summarize_text(st.get("summary", ""), old)
    return {"summary": summary, "messages": [RemoveMessage(id=m.id) for m in old]}
```

`prompts/summarizer.v1.md`：「把对话压缩为 ≤300 字中文摘要。保留：用户目标、已确认结论、每份报告的标题与编号要点、用户提出的偏好或约束。丢弃：工具原文、寒暄、重复内容。与已有摘要合并，不要丢掉已有摘要中的要点。」

`graph.py`：`START → summarize → plan`（把原来的 `START → plan` 改掉），`summarize` 节点挂 `LLM_RETRY`。重新生成 `docs/agent-graph.md`。

### Step 3 · 注入历史

- `AgentState` 增加 `history: str = ""`；`to_agent_state()` 中 `history=history_for_prompt(st)`。v0 不受影响（默认空）。
- `steps.plan_step` 与 `steps.synthesize` 的 user 消息开头加 `对话历史：\n{s.history}\n`。
- `prompts/planner.v1.md` → v1.2，新增规则：「若任务是对之前报告的追问（如『第二点展开』『换个角度』），先根据对话历史定位所指内容，只为补充信息规划检索步骤；不要重复做已完成的调研。」更新 changelog。

### Step 4 · API：conversation_id、409、响应头

`routes/agent.py`：

```python
class RunIn(BaseModel):
    task: str = Field(..., min_length=2, max_length=2000)
    conversation_id: str | None = Field(None, max_length=64)

@router.post("/run")
async def run_agent(body: RunIn, request: Request):
    with get_session_ctx() as db:
        cid = body.conversation_id
        if cid:
            if not db.get(Conversation, cid):
                raise HTTPException(404, "conversation not found")
            busy = db.exec(select(AgentRun).where(AgentRun.conversation_id == cid,
                                                  AgentRun.status.in_(["running", "waiting_approval"]))).first()
            if busy:
                raise HTTPException(409, "该会话有未完成或待审批的运行")
        else:
            conv = Conversation(title=body.task[:40]); db.add(conv); db.commit(); cid = conv.id
        run_id = uuid.uuid4().hex
        db.add(AgentRun(id=run_id, task=body.task, conversation_id=cid, agent_version=settings.AGENT_VERSION))
        db.commit()
    events = runner.run_v1_events(body.task, run_id=run_id, thread_id=cid, graph=request.app.state.agent_graph)
    return StreamingResponse(gen(run_id, events), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Conversation-Id": cid})
```

`runner.run_v1_events` 增加 `thread_id` 参数（默认等于 run_id），输入改为 `new_turn_input(task)`；`gen()` 抽成模块级函数供 Day45 的 approve 接口复用；`finally` 中若 run 仍为 running 则置为 failed（防止客户端断开后会话被永久 409）。`Conversation` 字段名以 phase_01 为准。前端（P1）：读取响应头保存 `conversationId`，「新会话」按钮清空。

> 浏览器跨域读取自定义响应头需要 `Access-Control-Expose-Headers: X-Conversation-Id`；同源（Vite 代理 / Caddy）则不需要。

### Step 5 · 测试

`tests/agent/test_conversation.py`（AI 生成样板；fixture 用 `tmp_path` 下的 AsyncSqliteSaver，并 monkeypatch `steps.*` 为假函数）：

1. `test_followup_sees_previous_report`：假 `synthesize` 第 1 轮返回 Markdown「## 发现\n1. A\n2. 第二点：向量索引用 HNSW」；假 `plan_step` 记录收到的 `s.history`。同一 thread 跑两轮，断言第 2 轮记录的 history 含「第二点：向量索引用 HNSW」。
2. `test_turn_fields_reset`：第 1 轮产生 2 条观察，第 2 轮产生 1 条；断言第 2 轮结束时 state 的 observations 长度为 1，`step_count == 1`。
3. `test_compression`：monkeypatch `context.HISTORY_TOKEN_BUDGET = 50`、`context.summarize_text` 返回 `"摘要X"`；连续跑 4 轮；断言 `summary == "摘要X"` 且 `len(messages) <= KEEP_LAST + 1`。

```bash
uv run pytest tests/agent -q
```

### Step 6 · 演示

```bash
curl -s -N -D /tmp/h.txt -X POST localhost:8000/v1/agent/run -H 'Content-Type: application/json' \
  -d '{"task":"调研我们项目的 RAG 检索配置，并对比 Qdrant hybrid search 的推荐做法"}' | tail -3
CID=$(grep -i x-conversation-id /tmp/h.txt | awk '{print $2}' | tr -d '\r')
curl -s -N -X POST localhost:8000/v1/agent/run -H 'Content-Type: application/json' \
  -d "{\"task\":\"把上一份报告第二点展开，给出具体配置示例\",\"conversation_id\":\"$CID\"}" | tail -3
```

期望：第二轮 plan 很短（0–1 个检索步骤），报告围绕上一份的第二点展开。

### Step 7 · 提交

```bash
cd ~/lab/workpilot
git add apps/api prompts/summarizer.v1.md prompts/planner.v1.md docs/agent-graph.md apps/web
git commit -m "feat(agent): conversation memory via thread_id with rolling summary compression"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么第二轮会「带着第一轮的观察」？怎么解决？（答：同一 thread 的状态被 checkpoint 持久化，`operator.add` 只能追加；改用「None 即清空」的 reducer，并在每轮输入中显式重置。）
2. `messages` 和 `observations` 为什么分开？（答：messages 是跨轮的对话（用户任务 + 最终报告），observations 是单轮内部的工具结果；工具原文体积大、可信度低，不应进入长期对话历史。）
3. 摘要压缩会丢什么？如何降低影响？（答：丢细节与原文措辞；保留最近 k 条原文、摘要提示词明确保留结论与编号要点、只压缩足够旧的消息。）
4. 为什么同一会话要禁止并发运行？（答：两个运行同时写同一 thread 的 checkpoint 会互相覆盖状态，导致历史错乱。）
5. 为什么用 tiktoken 近似而不是精确计数？（答：只用于触发压缩的阈值判断，误差可接受；精确计数需要模型对应的分词器，不值得为此增加依赖。）

## 8. 对 DA-01 的贡献

WorkPilot 的 Agent 从「一次性任务」变成「可持续对话的研发助手」：调研 → 追问 → 深挖在同一会话中完成，长会话的成本被压缩策略控制住；同时把会话与运行关联起来，为 Day45 的审批（同一 thread 暂停与恢复）打好基础。

## 9. 求职映射（D 线）

- 岗位能力：Agent 短期记忆、上下文窗口管理、LangGraph thread / reducer / RemoveMessage。
- 对应岗位：AI Agent Engineer、LLM Application Engineer。
- 简历 bullet 草稿：基于 LangGraph checkpointer 实现会话级记忆（thread 绑定会话、单轮状态重置、并发保护），通过滚动摘要 + 最近 k 轮原文的压缩策略使长会话输入 tokens 降低 \_\_%。
- 面试可能问：
  - Q：上下文窗口不够时有哪些策略？要点：截断、滚动摘要、检索式记忆、分层（摘要 + 最近原文）；各自丢失什么。
  - Q：多轮 Agent 的状态如何组织？要点：跨轮字段 vs 单轮字段、reducer 语义、thread 与 run 的关系。

## 10. 卡住时的处理

| 现象                             | 处理                                                                                                                 |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| reducer 收到 None 报 `TypeError` | 确认 `observations` 已换成 `resettable_add`，而不是仍为 `operator.add`                                               |
| 第二轮报 checkpoint 反序列化错误 | W11 的旧 checkpoint 与新 state 结构不兼容：开发环境换一个新的 `CHECKPOINT_DB` 文件路径（不要删除旧文件，改配置即可） |
| `RemoveMessage` 后消息没减少     | 确认消息有 id（`add_messages` 会自动分配）；返回的 key 必须是 `messages`                                             |
| 追问时 planner 又从头调研        | planner v1.2 的追问规则是否生效（检查 prompt 版本）；history 是否真的注入（打印 `s.history[:200]`）                  |
| 客户端断开后会话一直 409         | `gen()` 的 `finally` 中把仍为 running 的 run 置为 failed                                                             |
| 前端拿不到 `X-Conversation-Id`   | 跨域时需 expose header；或在第一个事件的 data 中也带上 conversation_id                                               |

## 11. 产出记录（执行时填写）

- 追问演示：第二轮步数 **、tokens **，是否准确定位「第二点」：\_\_\_\_
- 压缩触发时 messages 条数 / tokens：压缩前 \_**\_ → 压缩后 \_\_**
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day44「长期记忆」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
