# Day 40 · 2026-11-06 · Week 11 Task 1：LangGraph 迁移

## 0. 今天只做一件事

把 W10 的手写循环迁移成 LangGraph 状态图（plan → act → tools → decide → synthesize），节点内部复用 `steps.py` 与自己的 M1 Gateway，产出与 v0 相同的 SSE 事件，并用测试证明行为对齐。

不碰：RetryPolicy / fallback / checkpointer（Day41）、记忆与审批（W12）、LangChain 模型类、LangSmith。

## 1. 资产锚点

- 构建模块：M7.2 LangGraph 工作流（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.8 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`docs/agent-graph.md` 中由代码自动生成的 Agent 流程图；`uv run python scripts/agent_v1.py "<任务>"` 输出与 v0 同构的事件序列；`tests/agent/test_parity.py` 3 个任务 v0/v1 工具序列一致。
- 今日 AI 实际应用：LangGraph 的 State + reducer + 条件边 → 用在 `app/agent/{state,nodes,graph}.py`，把 Agent 控制流从 while 循环变成可视化、可持久化的图。

## 2. 起点（前置确认）

- 已有：W10 `steps.py`（plan_step / choose_action / decide_step / synthesize）、`schemas.py`、`report.py`、`loop_v0.py`、SSE 路由、`agent_smoke.jsonl`。
- 需确认：

```bash
cd ~/lab/workpilot && git tag | tail -1                     # v0.7.0
cd apps/api && uv run pytest tests/agent -q
uv add langgraph langgraph-checkpoint-sqlite
uv run python -c "import langgraph, importlib.metadata as m; print(m.version('langgraph'), m.version('langgraph-checkpoint-sqlite'))"
```

> 记下版本号写进产出记录。LangGraph 版本迭代快：本文 API 以 `from langgraph.graph import StateGraph, START, END` 为准；若导入报错，以已安装版本的官方文档为准，不降级 Python。

## 3. 验收对齐（做完要能勾掉）

- [ ] `state.py`：`ResearchState(TypedDict)`，`observations` 与 `errors` 使用 `Annotated[list, operator.add]`
- [ ] `nodes.py`：5 个节点均为 `async def`，只做「state ⇄ AgentState 转换 + 调 steps.\*」，不复制业务逻辑
- [ ] `graph.py`：`build_graph()` 含 3 条条件边（continue→act / replan→plan / finish→synthesize），`synthesize → END`
- [ ] `docs/agent-graph.md` 含 `draw_mermaid()` 输出
- [ ] `events.py` + `runner.run_v1_events()`：v1 产出与 v0 同类型事件；`recursion_limit` 已配置
- [ ] `test_parity.py` 3 个任务（假 LLM）v0/v1 工具序列与停止原因一致；已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                      |
| ----------- | ------ | --------------------------------------------------------- |
| 0–20 min    | P0     | 读文档：StateGraph、reducer、条件边（只看这三块）         |
| 20–40 min   | P0     | `state.py` + `to_agent_state()` 转换                      |
| 40–70 min   | P0     | `nodes.py` 5 个节点 + `graph.py` + Mermaid                |
| 70–90 min   | P0     | `events.py` + `runner.py` + `agent_v1.py` 跑 1 个真实任务 |
| 90–110 min  | P1     | `test_parity.py`                                          |
| 110–120 min | P0     | 提交                                                      |

时间不足时最低保留：state + nodes + graph + Mermaid + 1 个真实任务跑通。

## 5. 今日学习（只学完成任务必须的）

- **State + reducer**：节点只返回「要更新的字段」；默认覆盖，`Annotated[list, operator.add]` 表示追加——多个步骤的观察自动累积。
- **Node**：普通（async）函数 `state -> partial update`；节点里调用什么由你决定，所以可以继续用自己的 Gateway。
- **条件边**：`add_conditional_edges("decide", router, {"continue": "act", ...})`，router 返回字符串键。
- **recursion_limit**：一次运行最多执行的超步数（默认 25），超过抛 `GraphRecursionError`；8 步 × 3 节点就会超，必须显式调大。
- **stream_mode="updates"**：每个节点完成后产出 `{node_name: update}`，正好映射为 SSE 事件。
- 资料：
  - https://langchain-ai.github.io/langgraph/ （Graph API：StateGraph / Reducers / Conditional edges / Streaming）
  - https://docs.python.org/3/library/typing.html#typing.Annotated

## 6. 执行步骤

### Step 1 · state.py

`apps/api/app/agent/state.py`：

```python
import operator
from typing import Annotated, Any, TypedDict
from app.agent.schemas import AgentState, Observation, Plan

class ResearchState(TypedDict, total=False):
    task: str
    plan: dict | None                      # Plan.model_dump()；存 dict 便于 checkpoint 序列化
    current_step: int
    pending_call: dict | None              # act → tools 传递：{step_id, goal, tool, args_json, thought}
    observations: Annotated[list[dict], operator.add]
    decision: dict | None
    report: dict | None                    # {"report": {...}, "markdown": "..."}
    step_count: int
    replans: int
    seen_calls: dict[str, int]
    tokens_used: int
    cost_cny: float
    last_usage: dict | None                # 供事件适配器读取本节点的 usage
    stop_reason: str | None
    errors: Annotated[list[str], operator.add]

def initial_state(task: str) -> ResearchState:
    return ResearchState(task=task, plan=None, current_step=0, step_count=0, replans=0, seen_calls={},
                         tokens_used=0, cost_cny=0.0, observations=[], errors=[])

def to_agent_state(st: ResearchState) -> AgentState:
    """把图状态转成 W10 的 AgentState，让 steps.* 无需修改即可复用。"""
    return AgentState(task=st["task"], plan=Plan(**st["plan"]) if st.get("plan") else None,
                      current=st.get("current_step", 0),
                      observations=[Observation(**o) for o in st.get("observations", [])],
                      step_count=st.get("step_count", 0), replans=st.get("replans", 0),
                      tokens_used=st.get("tokens_used", 0), cost_cny=st.get("cost_cny", 0.0),
                      seen_calls=st.get("seen_calls", {}))

def add_usage(st: ResearchState, u: dict | None) -> dict[str, Any]:
    if not u:
        return {"last_usage": None}
    return {"tokens_used": st.get("tokens_used", 0) + int(u["tokens"]),
            "cost_cny": st.get("cost_cny", 0.0) + u["cost_cny"], "last_usage": u}
```

为什么 state 里存 dict 而不是 Pydantic 对象：Day41 的 checkpointer 要序列化整个 state，dict 最稳。

### Step 2 · nodes.py（只做转换 + 调用）

```python
from app.agent import steps
from app.agent.schemas import Observation, ToolCallReq
from app.agent.state import ResearchState, add_usage, to_agent_state
from app.tools.registry import execute

MAX_STEPS, TOKEN_BUDGET, MAX_REPLANS = 8, 30_000, 2

async def plan_node(st: ResearchState) -> dict:
    plan, u = await steps.plan_step(to_agent_state(st))
    replans = st.get("replans", 0) + (1 if st.get("plan") else 0)
    return {"plan": plan.model_dump(), "current_step": 0, "replans": replans, **add_usage(st, u)}

async def act_node(st: ResearchState) -> dict:
    s = to_agent_state(st)
    step = s.plan.steps[s.current]
    call, thought, u = await steps.choose_action(s, step)
    pc = {"step_id": step.id, "goal": step.goal, "tool": call.tool if call else None,
          "args_json": call.args_json if call else "{}", "thought": thought}
    return {"pending_call": pc, **add_usage(st, u)}

async def tools_node(st: ResearchState) -> dict:
    pc = st["pending_call"]
    seen = dict(st.get("seen_calls", {}))
    if pc["tool"] is None:
        obs = Observation(step_id=pc["step_id"], ok=True, content=pc["thought"])
    else:
        k = ToolCallReq(tool=pc["tool"], args_json=pc["args_json"]).key()
        seen[k] = seen.get(k, 0) + 1
        if seen[k] > 1:
            obs = Observation(step_id=pc["step_id"], tool=pc["tool"], ok=False,
                              error="duplicate_call_blocked：相同工具和参数已调用过，请换参数或换工具")
        else:
            r = await execute(pc["tool"], pc["args_json"])
            obs = Observation(step_id=pc["step_id"], tool=pc["tool"], ok=r.ok, content=r.content,
                              error=r.error, latency_ms=r.latency_ms, sources=r.sources)
    return {"observations": [obs.model_dump(mode="json")], "step_count": st.get("step_count", 0) + 1,
            "seen_calls": seen, "pending_call": None, "last_usage": None}

def _forced_stop(st: ResearchState) -> str | None:
    if sum(v - 1 for v in st.get("seen_calls", {}).values()) >= 2: return "repeated_calls"
    if st.get("step_count", 0) >= MAX_STEPS: return "max_steps"
    if st.get("tokens_used", 0) >= TOKEN_BUDGET: return "token_budget"
    return None

async def decide_node(st: ResearchState) -> dict:
    if stop := _forced_stop(st):
        return {"decision": {"action": "finish", "reason": stop}, "stop_reason": stop, "last_usage": None}
    d, u = await steps.decide_step(to_agent_state(st))
    action, stop = d.action, None
    if action == "replan" and st.get("replans", 0) >= MAX_REPLANS:
        action = "continue"
    if action == "continue" and st["current_step"] + 1 >= len(st["plan"]["steps"]):
        action, stop = "finish", "plan_completed"
    upd = {"decision": {"action": action, "reason": d.reason}, **add_usage(st, u)}
    if action == "continue":
        upd["current_step"] = st["current_step"] + 1
    if action == "finish":
        upd["stop_reason"] = stop or "finish"
    return upd

async def synthesize_node(st: ResearchState) -> dict:
    r, md, u = await steps.synthesize(to_agent_state(st))
    return {"report": {"report": r.model_dump(mode="json"), "markdown": md}, **add_usage(st, u)}
```

关键理解：停止逻辑集中在 `decide_node`，router 只读 `decision.action`——「判断」与「路由」分离，图结构保持干净。

### Step 3 · graph.py + Mermaid

```python
from langgraph.graph import END, START, StateGraph
from app.agent import nodes
from app.agent.state import ResearchState

def route_after_decide(st: ResearchState) -> str:
    return st["decision"]["action"]                # "continue" | "replan" | "finish"

def build_graph(checkpointer=None, interrupt_before: list[str] | None = None):
    g = StateGraph(ResearchState)
    g.add_node("plan", nodes.plan_node)
    g.add_node("act", nodes.act_node)
    g.add_node("tools", nodes.tools_node)
    g.add_node("decide", nodes.decide_node)
    g.add_node("synthesize", nodes.synthesize_node)
    g.add_edge(START, "plan")
    g.add_edge("plan", "act")
    g.add_edge("act", "tools")
    g.add_edge("tools", "decide")
    g.add_conditional_edges("decide", route_after_decide,
                            {"continue": "act", "replan": "plan", "finish": "synthesize"})
    g.add_edge("synthesize", END)
    return g.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)
```

```bash
cd ~/lab/workpilot/apps/api
uv run python -c "from app.agent.graph import build_graph; print(build_graph().get_graph().draw_mermaid())"
```

把输出放进 `docs/agent-graph.md` 的 ` ```mermaid ` 代码块，并在文件开头写一句「由 `build_graph().get_graph().draw_mermaid()` 生成，图结构变更后需重新生成」。

### Step 4 · 事件适配 + runner

`app/agent/events.py`（AI 生成，按下表映射，自己核对）：

| 节点 update | 产出事件                                                                         |
| ----------- | -------------------------------------------------------------------------------- |
| plan        | `plan`（data = plan，replans>0 时带 `replan`）                                   |
| act         | `step_start`；若 `pending_call.tool` 非空再加 `tool_call`（usage 挂在这里）      |
| tools       | `tool_result`（取 `observations[-1]`：tool / ok / error / preview / latency_ms） |
| decide      | `decision`                                                                       |
| synthesize  | `report`                                                                         |

`app/agent/runner.py`：

```python
import itertools
from app.agent.events import updates_to_events
from app.agent.graph import build_graph
from app.agent.schemas import AgentEvent
from app.agent.state import initial_state

async def run_v1_events(task: str, *, run_id: str, graph=None):
    graph = graph or build_graph()
    seq = itertools.count(1)
    totals = {"step_count": 0, "tokens_used": 0, "cost_cny": 0.0, "stop_reason": None}
    config = {"recursion_limit": 60, "configurable": {"thread_id": run_id}}
    async for chunk in graph.astream(initial_state(task), config, stream_mode="updates"):
        for node, upd in chunk.items():
            upd = upd or {}
            totals.update({k: upd[k] for k in totals if k in upd})
            for type_, data, usage in updates_to_events(node, upd):
                yield AgentEvent(type=type_, run_id=run_id, seq=next(seq), data=data, usage=usage)
    yield AgentEvent(type="done", run_id=run_id, seq=next(seq),
                     data={"stop_reason": totals["stop_reason"], "steps": totals["step_count"],
                           "tokens": totals["tokens_used"], "cost_cny": round(totals["cost_cny"], 4)})
```

`scripts/agent_v1.py`：与 `agent_v0.py` 相同的打印格式，调用 `run_v1_events`。跑 Day37 的第 1 个任务，对比两版输出的事件类型序列。

### Step 5 · 对齐测试（假 LLM，按状态而非调用顺序返回）

`tests/agent/test_parity.py` 思路：

- fixture monkeypatch `steps.plan_step` / `steps.choose_action` / `steps.decide_step` / `steps.synthesize` 为**基于状态**的假函数（例如：plan 固定 3 步，每步 `suggested_tool` 决定 `choose_action` 返回的工具；decide 在 `len(observations) >= 2` 时 finish，否则 continue），并把 `registry.execute` 换成返回固定 `ToolResult` 的假函数。
- 3 个任务参数化：① 正常 finish；② 恒 continue 走到 plan_completed；③ 恒返回同一工具调用触发 repeated_calls。
- 断言：从 v0 `run_events` 与 v1 `run_v1_events` 分别提取 `[e.data["tool"] for e in events if e.type == "tool_call"]` 相等，且 `done.data.stop_reason` 相等。

```bash
uv run pytest tests/agent -q
```

> 已知差异（写进 Day42 对比报告）：v1 在 decide 前做强制停止判断，达到上限时少一次 decider LLM 调用；所以只比较工具序列与停止原因，不比较 token 数。

### Step 6 · 提交

```bash
cd ~/lab/workpilot
git add apps/api scripts/agent_v1.py docs/agent-graph.md
git commit -m "feat(agent): migrate agent loop to LangGraph StateGraph with v0 parity tests"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 节点返回 `{"observations": [obs]}` 为什么不会覆盖之前的观察？（答：该字段用 `Annotated[list, operator.add]` 声明了 reducer，更新与旧值相加；未声明 reducer 的字段才覆盖。）
2. 条件边的 router 应该做「判断」吗？（答：尽量不要；判断放在节点里写入 state，router 只读字段，保证路由纯粹、可测试。）
3. `recursion_limit` 和你的 `max_steps` 有什么区别？（答：前者是框架层「超步」安全阀，后者是业务层「工具步数」上限；业务上限应先触发，框架上限是兜底。）
4. 为什么节点里继续用自己的 Gateway 而不是 ChatOpenAI？（答：保持 M1 的重试 / 计费 / 结构化输出 / 日志一致，避免两套模型调用路径；LangGraph 本身不要求 LangChain 模型类。）
5. 迁移后 v0 的哪段代码消失了？（答：while 循环与 if/else 分支变成了图的边；状态从局部变量变成显式 `ResearchState`。）

## 8. 对 DA-01 的贡献

WorkPilot 的 Agent 运行时从「藏在循环里的流程」变成「显式、可视化的状态图」，为 Day41 的持久化恢复、W12 的会话记忆与人工审批（interrupt）铺平道路；同时前端与 API 协议零改动，体现了 W10 事件协议设计的价值。

## 9. 求职映射（D 线）

- 岗位能力：LangGraph StateGraph / reducer / 条件路由 / streaming、框架迁移与行为对齐测试。
- 对应岗位：AI Agent Engineer、LLM Engineer。
- 简历 bullet 草稿：将手写 Agent 循环迁移为 LangGraph 状态图（5 节点、3 条条件边），节点复用原有业务函数，行为对齐测试保障迁移零回归，前端事件协议保持不变。
- 面试可能问：
  - Q：LangGraph 和 LangChain AgentExecutor 有什么区别？要点：显式图 vs 黑盒循环、状态与 reducer、checkpoint / interrupt 原生、可控性更高。
  - Q：你怎么保证框架迁移不改变行为？要点：纯函数复用、基于状态的假 LLM、比较工具序列与停止原因、已知差异显式记录。

## 10. 卡住时的处理

| 现象                                    | 处理                                                                                                                            |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `GraphRecursionError`                   | 在 config 设 `recursion_limit`（示例 60）；同时检查 decide 是否永远不返回 finish                                                |
| `KeyError: 'plan'` 等                   | TypedDict `total=False` 时用 `st.get()`；确认 `initial_state()` 作为输入传入                                                    |
| 观察被重复累加两次                      | 某节点返回了完整 `observations` 列表而不是只返回新增项；reducer 字段只返回增量                                                  |
| `draw_mermaid()` 报错或空               | 先 `build_graph()` 不带 checkpointer；仍失败就用 `print(graph.get_graph())` 手写 Mermaid                                        |
| 节点里调用 async Gateway 报事件循环错误 | 节点用 `async def` 并用 `astream` / `ainvoke` 驱动；不要在节点里 `asyncio.run()`                                                |
| 对齐测试 v0/v1 工具序列不同             | 打印两边 seen_calls 与 current_step；常见原因是 continue 时 v1 先判 `plan_completed`，调整假 decide 让两边都在同一观察数 finish |

## 11. 产出记录（执行时填写）

- langgraph / langgraph-checkpoint-sqlite 版本：\_**\_ / \_\_**
- 真实任务 v0 vs v1 事件类型序列是否一致：\_\_\_\_
- 对齐测试通过数：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day41「重试 / 降级 / checkpoint」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
