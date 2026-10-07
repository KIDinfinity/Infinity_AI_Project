# Day 52 · 2027-01-04 · Week 15 Task 1：Trace / Span + Trace 查看

## 0. 今天只做一件事

自研轻量 Trace：`app/obs/trace.py`（contextvars + `with span(...)`）把每个请求里的 LLM 调用、检索、工具执行、graph 节点记录成 span，请求结束批量写入 SQLite `Trace` / `Span`，并在前端 TracePage 用瀑布图查看。

不碰：成本账本与预算（Day53）、看板（Day54）、部署 Langfuse / Jaeger / OTel Collector（只写 P2 说明）。

## 1. 资产锚点

- 构建模块：M9.1 request_id / trace / span（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v1.0 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：任一请求可在 `/traces/<id>` 看到瀑布图——每个节点/LLM/检索/工具的耗时、model、tokens、cost、错误；可直接回答「这次 Agent 慢在哪」
- 今日 AI 实际应用：LLM 可观测性（trace/span、GenAI 属性）→ 用于定位 WorkPilot Agent 的延迟与成本热点

## 2. 起点（前置确认）

- 已有：W7 的 request_id 中间件（X-Request-ID）+ JSON 日志；`llm_calls.jsonl`；W14 `make eval-smoke`
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
grep -rn "request_id" app/main.py app/core/*.py | head          # 中间件位置与 contextvar 名称
grep -n "class .*(SQLModel\|Base)" app/db/models.py | head       # ORM 风格（下文以 SQLModel 为例）
grep -n "add_node" app/agent/graph.py                            # graph 节点注册处
grep -n "async def execute" app/tools/registry.py                # 工具执行入口
grep -n "def chat\|def stream\|def structured" app/llm/gateway.py
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `Trace`、`Span` 表已创建；一次 `/v1/agent/run` 产生 1 条 Trace + ≥ 5 条 Span（graph 节点 / llm / retrieve / tool）
- [ ] 子 span 的 `parent_id` 指向外层 span（单测证明嵌套与异常时 `status=error`）
- [ ] SSE 请求（agent run）的 span 在流结束后完整落库，不丢失
- [ ] `GET /v1/ops/traces`、`GET /v1/ops/traces/{id}` 返回正确 JSON
- [ ] TracePage 瀑布图可见，点击 span 显示 attrs 与 error
- [ ] `make eval-smoke` 通过；已提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                               |
| ----------- | ------ | -------------------------------------------------- |
| 0–10 min    | P0     | trace/span/parent 概念 + 确认埋点位置              |
| 10–40 min   | P0     | 表结构 + `trace.py` + 单测                         |
| 40–55 min   | P0     | 中间件 start/flush + SSE flush                     |
| 55–75 min   | P0     | 4 处埋点（Gateway / retrieve / tool / graph 节点） |
| 75–85 min   | P0     | ops 路由                                           |
| 85–110 min  | P1     | TracePage 瀑布图                                   |
| 110–120 min | P0     | eval-smoke + 提交；P2 文档 3 段                    |

时间不足时最低保留：`trace.py` + 表 + Gateway 与 tool 埋点 + `GET /v1/ops/traces/{id}`。

## 5. 今日学习（只学完成任务必须的）

- **Trace / Span**：trace = 一次请求的完整调用树；span = 树上一个有起止时间的操作，靠 `parent_id` 组成父子关系。
- **contextvars**：每个 asyncio Task 有自己的上下文副本，适合保存「当前 trace / 当前 span」，并发请求互不干扰；子任务创建时会复制父上下文。
- **批量落库**：span 先放内存缓冲，请求结束一次写入，避免每个 span 一次 DB 写；SSE 请求要在生成器结束时 flush。
- **GenAI 属性约定**：OpenTelemetry 为 LLM 调用定义了 `gen_ai.request.model`、`gen_ai.usage.input_tokens` 等属性名；今天 attrs 命名尽量对齐，便于将来导出。
- 资料：https://opentelemetry.io/docs/ （Concepts → Signals → Traces）、https://langchain-ai.github.io/langgraph/

## 6. 执行步骤

### Step 1 · 表结构（按 `db/models.py` 现有风格，以 SQLModel 为例，样板可 AI 生成）

- `Trace`：`id`（主键，= request_id）、`route`、`method`、`status_code`、`started_at`（索引）、`duration_ms`、`span_count`、`error_count`、`total_tokens`、`total_cost_cny`。
- `Span`：`id`（主键）、`trace_id`（索引）、`parent_id`（可空）、`name`（索引，如 `llm.chat` / `rag.retrieve` / `tool.kb_search` / `graph.plan`）、`start_ms`、`end_ms`、`status`（ok/error，索引）、`attrs`（JSON 字符串）、`error`（可空）。

### Step 2 · `app/obs/trace.py`（核心，必须自己理解每一行）

```python
import json, time, uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
current_span_var: ContextVar[str | None] = ContextVar("current_span", default=None)
_BUFFER: dict[str, dict] = {}        # trace_id -> {"started": ts, "spans": [SpanRec]}

@dataclass
class SpanRec:
    id: str; trace_id: str; parent_id: str | None; name: str; start_ms: float
    end_ms: float = 0.0; status: str = "ok"; error: str | None = None
    attrs: dict = field(default_factory=dict)
    def set(self, **kv): self.attrs.update(kv)

class _Noop:
    def set(self, **kv): pass

def start_trace(trace_id: str) -> None:
    now = time.time()
    for tid in [t for t, b in _BUFFER.items() if now - b["started"] > 600]:   # 防泄漏：清理 10 分钟未 flush 的
        _BUFFER.pop(tid, None)
    _BUFFER[trace_id] = {"started": now, "spans": []}
    trace_id_var.set(trace_id)

@contextmanager
def span(name: str, **attrs):
    tid = trace_id_var.get()
    if tid is None or tid not in _BUFFER:          # 不在请求中（脚本/评测）→ 空操作
        yield _Noop()
        return
    s = SpanRec(uuid.uuid4().hex[:16], tid, current_span_var.get(), name, time.time() * 1000, attrs=dict(attrs))
    token = current_span_var.set(s.id)
    try:
        yield s
    except Exception as e:
        s.status, s.error = "error", f"{type(e).__name__}: {e}"[:500]
        raise
    finally:
        s.end_ms = time.time() * 1000
        current_span_var.reset(token)
        _BUFFER[tid]["spans"].append(s)

def pop_spans(trace_id: str) -> list[SpanRec]:
    return _BUFFER.pop(trace_id, {"spans": []})["spans"]
```

`app/obs/trace_store.py`：`def flush(trace_id, route, method, status_code)` —— `pop_spans` → 汇总 tokens/cost（llm span 的 attrs）/error 数 → 写 Trace + Span（同步函数，调用处用 `await asyncio.to_thread(flush, ...)`）。约 30 行，可 AI 生成后自己审。

### Step 3 · 请求生命周期

在现有 request_id 中间件中：

```python
rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
start_trace(rid)
response = await call_next(request)
if not isinstance(response, StreamingResponse):              # SSE 由生成器自己 flush
    await asyncio.to_thread(flush, rid, request.url.path, request.method, response.status_code)
```

在 `/v1/agent/run` 的 SSE 生成器：

```python
async def event_gen():
    try:
        with span("agent.run", task_len=len(req.task)):
            async for ev in run_agent_stream(req):
                yield ev
    finally:
        await asyncio.to_thread(flush, trace_id_var.get(), "/v1/agent/run", "POST", 200)
```

### Step 4 · 四处埋点

```python
# Gateway（chat/structured；stream 见卡点表）
with span("llm.chat", **{"gen_ai.request.model": model, "provider": provider}) as s:
    resp = await self._call_with_retry(...)
    s.set(**{"gen_ai.usage.input_tokens": u.prompt_tokens, "gen_ai.usage.output_tokens": u.completion_tokens},
          cost_cny=cost, retries=attempts)

# retrieve
with span("rag.retrieve", top_k=top_k, hybrid=settings.hybrid) as s:
    hits = ...
    s.set(n_hits=len(hits), top_score=hits[0].score if hits else None)

# registry.execute
with span(f"tool.{name}", tool=name, permission=spec.permission, untrusted=spec.untrusted) as s:
    result = ...
    s.set(ok=result.ok, output_chars=len(str(result.output)))

# graph 节点：包装后再 add_node
def traced_node(name, fn):
    @functools.wraps(fn)
    async def wrapper(state, *args, **kwargs):
        with span(f"graph.{name}"):
            return await fn(state, *args, **kwargs)
    return wrapper
builder.add_node("plan", traced_node("plan", plan_node))
```

### Step 5 · ops 路由 `app/routes/ops.py`（约 18 行）

- `GET /v1/ops/traces?limit=50&status=error`：按 `started_at` 倒序，`limit` 上限 200；`status=error` 时过滤 `error_count > 0`。
- `GET /v1/ops/traces/{trace_id}`：不存在 → `HTTPException(404, detail={"code": "TRACE_NOT_FOUND"})`；返回 `{"trace": t, "spans": [...]}`，spans 按 `start_ms` 排序，`attrs` 用 `json.loads` 还原。

> 注意：云端已有 Caddy basic_auth 保护；ops 接口会暴露内部细节，W19 加认证后再改为 owner 可见。

### Step 6 · TracePage 瀑布图（P1，样板可 AI 生成，比例计算自己核对）

`apps/web/src/components/Waterfall.tsx`（约 60 行）要求：

- 输入 `spans: {id, parent_id, name, start_ms, end_ms, status, attrs, error}[]`；空数组显示「无 span」。
- 计算：`t0 = min(start_ms)`、`total = max(max(end_ms) - t0, 1)`；每行条形 `left = (start_ms - t0) / total * 100%`、`width = max((end_ms - start_ms) / total * 100, 0.5)%`。
- 缩进：沿 `parent_id` 向上数深度，`paddingLeft = depth * 12px`。
- 颜色：`llm.*` 紫、`tool.*` 琥珀、`rag.*` 绿、其他蓝；`status=error` 一律红。右侧显示耗时 ms。
- 点击行：下方 `<pre>` 展示 `JSON.stringify({...attrs, error}, null, 2)`。

路由：`/traces`（列表：时间、路由、耗时、tokens、成本、错误数）与 `/traces/:id`。P1：AgentPage 每次运行显示「查看 Trace」链接（trace_id = request_id）。

### Step 7 · 测试 + P2 文档 + 提交

`tests/unit/test_trace.py`：

```python
def test_nested_and_error():
    start_trace("t-test")
    with span("outer"):
        with pytest.raises(ValueError):
            with span("inner"):
                raise ValueError("boom")
    spans = {s.name: s for s in pop_spans("t-test")}
    assert spans["inner"].parent_id == spans["outer"].id
    assert spans["inner"].status == "error" and spans["outer"].status == "ok"
```

`docs/observability.md`：Trace 数据模型、埋点清单、attrs 命名；**P2 说明**：如需对接标准生态，可在 `flush` 处把 SpanRec 转为 OpenTelemetry span 经 OTLP 导出（属性已按 `gen_ai.*` 命名），或使用 Langfuse（仅限公开/脱敏数据，Langfuse 支持接收 OTel 数据）；当前不引入。

```bash
cd ~/lab/workpilot && uv run --project apps/api pytest apps/api/tests/unit/test_trace.py -q && make eval-smoke
git add apps/api apps/web docs/observability.md
git commit -m "feat(obs): lightweight trace/span with SQLite storage and trace waterfall page"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么用 contextvars 而不是全局变量保存当前 trace？（答：并发请求在不同 Task 中，各自有上下文副本；全局变量会串请求）
2. 为什么 SSE 请求不能在中间件里 flush？（答：中间件拿到 response 时流还没开始迭代，span 尚未产生；必须在生成器结束（finally）时 flush）
3. span 出异常时为什么要 `raise`？（答：trace 只记录不吞异常，否则会改变业务行为（重试/降级逻辑失效））
4. Trace 和 JSON 日志的区别？（答：日志是离散事件；trace 是带因果关系与时间区间的调用树，能看出并行/串行与耗时占比）
5. 为什么 attrs 用 `gen_ai.*` 命名？（答：对齐 OpenTelemetry GenAI 语义约定，未来导出到任何 OTel 后端无需改埋点）

## 8. 对 DA-01 的贡献

WorkPilot 第一次具备「请求级透视」：P2 验收项「任一请求可在 Trace 页面看到 LLM/检索/工具调用明细与成本」达成；Span 表同时是 Day53 成本归因、Day54 错误列表与 W20 评测看板的数据底座，并且零新增服务、零额外成本。

## 9. 求职映射（D 线）

- 岗位能力：LLM Observability、Tracing 设计、性能定位
- 对应岗位：AI Platform Engineer / AI Engineer / AI Full-Stack Engineer
- 简历 bullet 草稿：基于 contextvars 自研轻量 Trace/Span（SQLite 存储、OTel GenAI 属性命名），覆盖 Agent 节点 / LLM / 检索 / 工具 4 类埋点，并实现瀑布图定位 Agent 延迟热点（发现 ** 占总耗时 **%）。
- 面试可能问：
  - 为什么不直接用 Langfuse / LangSmith？（要点：单机自托管与预算约束、数据不出本机、零依赖；属性按 OTel 约定，需要时可导出——这是取舍不是不会）
  - 一个 Agent 请求很慢，你怎么排查？（要点：打开 trace → 看最长 span → 区分 LLM 生成/重试、检索、外部工具 → 对应优化：减少步数、并行工具、缓存、换模型）

## 10. 卡住时的处理

| 现象                                                     | 处理                                                                                                                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ValueError: <Token> was created in a different Context` | span 在一个上下文打开、另一个关闭（常见于流式生成器跨 Task）；流式 LLM 调用改为在生成器内完整包住，或对 stream 只记录开始/结束两个时间点后手动 append |
| agent run 的 span 为 0                                   | `start_trace` 未在该请求执行，或 SSE 生成器没 flush；打印 `trace_id_var.get()` 检查                                                                   |
| graph 节点 span 的 parent 不对                           | LangGraph 节点在新 Task 中执行，父 span 是创建 Task 时的当前 span；以 `agent.run` 为父即可接受                                                        |
| 同步节点（def）无法用 async wrapper                      | 为同步节点写同步版本 wrapper，或保持节点 async                                                                                                        |
| SQLite `database is locked`                              | flush 使用独立短事务；W6 的 SQLite 已开 WAL 则无问题，否则 `PRAGMA journal_mode=WAL`                                                                  |
| 瀑布图条宽为 0                                           | 时间单位不一致（秒 vs 毫秒）；统一 `time.time()*1000`                                                                                                 |

## 11. 产出记录（执行时填写）

- 一次 Agent 运行的 span 数与名称：\_\_\_\_
- 最耗时 span 及占比：\_\_\_\_
- TracePage 截图路径：\_\_\_\_
- eval-smoke 结果：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day53（W15 Task 2：成本账本 + 预算守卫 + 限流）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
