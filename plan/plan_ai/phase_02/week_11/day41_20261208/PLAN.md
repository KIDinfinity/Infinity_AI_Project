# Day 41 · 2026-12-08 · Week 11 Task 2：重试 / 降级 / checkpoint

## 0. 今天只做一件事

让 LangGraph Agent 在真实故障下「要么优雅完成、要么明确失败、还能断点续跑」：节点级 RetryPolicy、工具错误转观察、Gateway provider 降级、SQLite checkpointer + 中断恢复，并用故障注入测试证明。

不碰：会话记忆 / thread 绑定 conversation（Day43）、interrupt 审批（Day45）、成本预算守卫与限流（W15）。

## 1. 资产锚点

- 构建模块：M7.2 LangGraph（retry / checkpoint）、M1.2 可靠性（provider fallback）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.8 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：① 把 DeepSeek base_url 改成错误地址，Agent 自动切到备用 provider 完成任务，日志可见 `provider_fallback`；② 运行中 Ctrl+C，`scripts/agent_v1.py --resume <run_id>` 从断点继续直到 done；③ `tests/agent/test_faults.py` 3 个故障注入用例全绿。
- 今日 AI 实际应用：LLM 应用的分层容错（SDK / Gateway / 节点 / 工具）与持久化执行 → 用在 `app/llm/gateway.py`、`app/agent/graph.py`、`app/main.py` lifespan。

## 2. 起点（前置确认）

- 已有：Day40 `graph.py` / `nodes.py` / `runner.py`；phase_01 Gateway 的 timeout + 指数退避重试。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api && uv run pytest tests/agent -q
grep -n "max_retries\|retry\|backoff\|timeout" app/llm/gateway.py      # 现有重试实现在哪
uv run python -c "from langgraph.types import RetryPolicy; print('ok')"
uv run python -c "from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver; print('ok')"
ollama list 2>/dev/null | head -5                                      # 可选：本地是否有 qwen2.5 等支持 tools 的模型
```

- 备用 provider 二选一：DashScope（Qwen 兼容模式，需 key，少量费用）或本机 Ollama（零成本，需已拉取支持 tool calling 的模型，如 `qwen2.5:7b`）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `docs/` 或 draft 中写出「重试分层表」（每层处理什么、次数）
- [ ] Gateway：`LLM_FALLBACK_BASE_URL / LLM_FALLBACK_MODEL / LLM_FALLBACK_API_KEY` 配置化；超时 / 连接错误 / 429 / 5xx 触发降级，400 类不降级；全失败抛 `LLMUnavailable`；日志与成本记录带 provider 名
- [ ] OpenAI SDK 客户端 `max_retries=0`（避免与 Gateway 重试叠加）
- [ ] 节点 `retry_policy=RetryPolicy(...)`，`retry_on` 排除 `LLMUnavailable`
- [ ] `AsyncSqliteSaver` 在 FastAPI lifespan 中创建；`thread_id = run_id`
- [ ] `--resume` 演示成功（终端输出存到产出记录）
- [ ] 故障注入测试 3 个 + checkpoint 测试 1 个全绿；已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                             |
| ----------- | ------ | ---------------------------------------------------------------- |
| 0–10 min    | P0     | 写重试分层表，定每层职责                                         |
| 10–40 min   | P0     | Gateway fallback + `test_fallback.py`（respx）                   |
| 40–55 min   | P0     | 节点 RetryPolicy + decider 提示词补「工具失败时优先换工具/参数」 |
| 55–80 min   | P0     | AsyncSqliteSaver + lifespan + `--resume` 演示                    |
| 80–105 min  | P0     | `test_faults.py` + `test_checkpoint.py`                          |
| 105–115 min | P1     | 真实演练：改错主 base_url 跑一次任务                             |
| 115–120 min | P0     | 提交                                                             |

时间不足时最低保留：checkpointer + 恢复演示 + 工具超时测试 + fallback 单测（不做真实演练）。

## 5. 今日学习（只学完成任务必须的）

- **重试只能有一个主人**：SDK、Gateway、节点三层都重试会让 1 次故障放大成 3×3×3 次调用；每类错误只在一层处理。
- **降级 ≠ 重试**：重试是同一 provider 再试，降级是换 provider；只对「对方的问题」（超时 / 429 / 5xx）降级，对「我们的问题」（400 参数错误）不降级。
- **RetryPolicy**：`max_attempts`、`initial_interval`、`backoff_factor`、`retry_on`（异常类或返回 bool 的函数）；作用于整个节点重新执行。
- **Checkpointer**：每个超步结束保存一次 state；同一 `thread_id` 再次以 `None` 为输入调用即从最后一个 checkpoint 继续。节点是 async 时必须用异步版 `AsyncSqliteSaver`（同包 `langgraph.checkpoint.sqlite.aio`，依赖 aiosqlite）；同步 `SqliteSaver` 适用于同步 `invoke/stream`。
- 资料：
  - https://langchain-ai.github.io/langgraph/ （Persistence / Checkpointers；How-to：add retry policies）
  - https://github.com/openai/openai-python#handling-errors
  - https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope
  - https://github.com/ollama/ollama/blob/main/docs/openai.md

## 6. 执行步骤

### Step 1 · 重试分层表（先想清楚再写代码）

| 层                  | 处理的错误                          | 策略                                                                | 次数             |
| ------------------- | ----------------------------------- | ------------------------------------------------------------------- | ---------------- |
| OpenAI SDK          | —                                   | 关闭（`max_retries=0`）                                             | 0                |
| Gateway 单 provider | 超时、连接错误、429、5xx            | 指数退避重试（phase_01 已有）                                       | 2                |
| Gateway 多 provider | 上一层重试耗尽                      | 切换到 fallback provider                                            | 1 次切换         |
| 节点 RetryPolicy    | 结构化输出校验失败、偶发非 LLM 异常 | 重新执行整个节点                                                    | `max_attempts=2` |
| 工具                | 超时、HTTP 错误、参数错误           | 不重试，`ToolResult(ok=False)` → 观察 → decider 决定换工具或 replan | 0                |
| 全部失败            | `LLMUnavailable`                    | 不再重试，run 置 failed，发 error 事件                              | —                |

### Step 2 · Gateway provider fallback

`app/core/config.py` 新增：

```python
LLM_FALLBACK_BASE_URL: str | None = None      # https://dashscope.aliyuncs.com/compatible-mode/v1 或 http://localhost:11434/v1
LLM_FALLBACK_MODEL: str | None = None         # qwen-plus 或 qwen2.5:7b
LLM_FALLBACK_API_KEY: SecretStr | None = None # Ollama 可填任意非空字符串
CHECKPOINT_DB: str = "data/checkpoints.sqlite"
```

`app/llm/gateway.py` 关键改动（在 phase_01 的 `_create()` 外面包一层；变量名以你的实现为准）：

```python
import logging
import openai
from openai import AsyncOpenAI

log = logging.getLogger("workpilot.llm")
FALLBACK_ON = (openai.APITimeoutError, openai.APIConnectionError,
               openai.RateLimitError, openai.InternalServerError)

class LLMUnavailable(RuntimeError):
    """所有 provider 都失败；上层不应再重试。"""

class Provider:
    def __init__(self, name: str, base_url: str, api_key: str, model: str, timeout_s: float):
        self.name, self.model = name, model
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout_s, max_retries=0)

def build_providers(s) -> list[Provider]:
    ps = [Provider("deepseek", s.LLM_BASE_URL, s.LLM_API_KEY.get_secret_value(), s.LLM_MODEL, s.LLM_TIMEOUT_S)]
    if s.LLM_FALLBACK_BASE_URL and s.LLM_FALLBACK_MODEL:
        key = s.LLM_FALLBACK_API_KEY.get_secret_value() if s.LLM_FALLBACK_API_KEY else "ollama"
        ps.append(Provider("fallback", s.LLM_FALLBACK_BASE_URL, key, s.LLM_FALLBACK_MODEL, s.LLM_TIMEOUT_S))
    return ps

async def _create(self, **kw):
    last: Exception | None = None
    for p in self.providers:
        try:
            resp = await self._create_with_retry(p, model=p.model, **kw)   # phase_01 的重试逻辑，改为接收 provider
            if p is not self.providers[0]:
                log.warning("provider_fallback", extra={"provider": p.name, "reason": type(last).__name__})
            self._record_cost(resp.usage, provider=p.name)                 # pricing 表按 provider/model 取价
            return resp
        except FALLBACK_ON as e:
            last = e
            log.error("provider_failed", extra={"provider": p.name, "error": type(e).__name__})
    raise LLMUnavailable("all llm providers failed") from last
```

注意：`openai.BadRequestError`（400）、`AuthenticationError`（401）不在 `FALLBACK_ON` 中——参数错误换 provider 也会错，key 错误应立即暴露。

`tests/llm/test_fallback.py`（respx 拦截 OpenAI SDK 的 httpx 请求）：

```python
import httpx, pytest, respx

OK = {"id": "x", "object": "chat.completion", "created": 0, "model": "m",
      "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "ok"}}],
      "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}

@pytest.mark.asyncio
@respx.mock
async def test_fallback_on_500(make_gateway):          # fixture：用测试配置构建 Gateway，重试退避设为 0
    primary = respx.post("https://api.deepseek.com/chat/completions").mock(return_value=httpx.Response(500))
    backup = respx.post("http://fallback.test/v1/chat/completions").mock(return_value=httpx.Response(200, json=OK))
    gw = make_gateway(fallback_base_url="http://fallback.test/v1", fallback_model="m")
    res = await gw.chat([{"role": "user", "content": "hi"}])
    assert primary.called and backup.called

@pytest.mark.asyncio
@respx.mock
async def test_all_down_raises(make_gateway):
    respx.post(url__regex=r".*/chat/completions").mock(return_value=httpx.Response(503))
    gw = make_gateway(fallback_base_url="http://fallback.test/v1", fallback_model="m")
    with pytest.raises(LLMUnavailable):
        await gw.chat([{"role": "user", "content": "hi"}])
```

### Step 3 · 节点 RetryPolicy + 工具错误观察化

`graph.py`：

```python
from langgraph.types import RetryPolicy
from app.llm.gateway import LLMUnavailable

def is_transient(exc: Exception) -> bool:
    if isinstance(exc, LLMUnavailable):
        return False                                   # Gateway 已穷尽所有 provider
    return isinstance(exc, (ValueError, TimeoutError, ConnectionError))   # 含结构化输出校验失败

LLM_RETRY = RetryPolicy(max_attempts=2, initial_interval=0.5, backoff_factor=2.0, retry_on=is_transient)

# build_graph 中：
g.add_node("plan", nodes.plan_node, retry_policy=LLM_RETRY)
g.add_node("act", nodes.act_node, retry_policy=LLM_RETRY)
g.add_node("decide", nodes.decide_node, retry_policy=LLM_RETRY)
g.add_node("synthesize", nodes.synthesize_node, retry_policy=LLM_RETRY)
g.add_node("tools", nodes.tools_node)                  # 工具不重试：错误已在 execute() 中转为 ok=False
```

> 旧版本 LangGraph 的参数名是 `retry=`，新版本是 `retry_policy=`；以已安装版本为准（`help(StateGraph.add_node)` 一看便知）。Pydantic 的 `ValidationError` 是 `ValueError` 子类，因此结构化输出校验失败会被节点重试。

`tools_node` 已把失败写成观察；再做两件小事：① 失败时额外返回 `{"errors": [f"{tool}: {error}"]}`；② `prompts/decider.v1.md` 增加一条「最近一步工具失败时：同一工具换参数最多一次，否则 replan 换信息源」，版本号改为 v1.1 并写 changelog。

### Step 4 · checkpointer + lifespan + 恢复演示

`app/main.py` lifespan（合并到 phase_01 已有 lifespan 中）：

```python
from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agent.graph import build_graph

@asynccontextmanager
async def lifespan(app):
    async with AsyncSqliteSaver.from_conn_string(settings.CHECKPOINT_DB) as saver:
        app.state.agent_graph = build_graph(checkpointer=saver)
        yield
```

`scripts/agent_v1.py` 增加 `--resume`：

```python
async def main(task: str | None, resume: str | None):
    async with AsyncSqliteSaver.from_conn_string("data/checkpoints.sqlite") as saver:
        graph = build_graph(checkpointer=saver)
        run_id = resume or uuid.uuid4().hex
        config = {"recursion_limit": 60, "configurable": {"thread_id": run_id}}
        print("run_id:", run_id)
        inp = None if resume else initial_state(task)
        if resume:
            snap = await graph.aget_state(config)
            print("resume from next =", snap.next, "step_count =", snap.values.get("step_count"))
        async for chunk in graph.astream(inp, config, stream_mode="updates"):
            for node, upd in chunk.items():
                print(f"[{node}]", {k: v for k, v in (upd or {}).items() if k in ("decision", "stop_reason", "step_count")})
```

演示：

```bash
uv run python ../../scripts/agent_v1.py --task "调研 Qdrant hybrid search 并对比我们知识库的检索配置"
# 看到 2–3 个 [tools] 输出后按 Ctrl+C
uv run python ../../scripts/agent_v1.py --resume <上面打印的 run_id>
# 期望：resume from next = ('decide',) 或 ('act',) …，随后继续直至 [synthesize]
```

`data/` 已在 `.gitignore`（phase_01 约定），checkpoint 文件不进 Git。

### Step 5 · 故障注入测试

`tests/agent/test_faults.py`（AI 生成样板，断言自己写）：

1. `test_tool_timeout_graceful`：注册临时工具 `_slow`（`timeout_s=0.05`，内部 sleep 1s）；假 `choose_action` 第一步选 `_slow`、第二步选 `calculator`；假 decide 在 2 条观察后 finish。断言：`done` 事件存在、observations[0].error 含 `timeout`、`report` 事件存在。
2. `test_node_retry_once`：假 `decide_step` 第 1 次抛 `ValueError("bad json")`、第 2 次返回 finish。断言：运行完成，假函数被调用 2 次。
3. `test_llm_unavailable_fails_fast`：假 `plan_step` 抛 `LLMUnavailable`。断言：`run_v1_events` 在 `asyncio.wait_for(..., 5)` 内抛出 `LLMUnavailable`，且假函数只被调用 1 次（未被 RetryPolicy 重试）。

`tests/agent/test_checkpoint.py`：用 `tmp_path` 下的 sqlite 文件，`build_graph(saver, interrupt_before=["decide"])` 跑到第一次中断 → 断言 `snap.next == ("decide",)` → 用**新的** graph 实例（同一个 db、不带 interrupt）`ainvoke(None, config)` → 断言最终 state 有 `report`。

```bash
uv run pytest tests/agent tests/llm -q
```

### Step 6 ·（P1）真实演练

`.env` 临时把 `LLM_BASE_URL` 改为 `https://api.deepseek.com.invalid`，配置好 fallback，跑一次 `agent_v1.py`；确认日志有 `provider_failed` → `provider_fallback`，任务完成；改回配置。

### Step 7 · 提交

```bash
cd ~/lab/workpilot
git add apps/api scripts/agent_v1.py prompts/decider.v1.md .env.example
git commit -m "feat(agent): node retry policy, provider fallback and sqlite checkpointer with resume"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么要把 SDK 的 `max_retries` 关掉？（答：Gateway 已统一重试，SDK 默认还会重试 2 次，叠加后故障时调用次数和延迟成倍放大，且日志无法反映真实重试次数。）
2. 什么错误该降级、什么错误不该？（答：超时 / 连接 / 429 / 5xx 是对方问题，换 provider 有意义；400 / 401 是我们的问题，换了也错，应立即暴露。）
3. `LLMUnavailable` 为什么不让 RetryPolicy 重试？（答：它代表所有 provider 都已重试并失败，再重试只会拖长失败时间，应快速失败并给用户明确结果。）
4. checkpoint 在什么时候保存？恢复时从哪里开始？（答：每个超步（节点执行完）后保存；恢复时以 `None` 为输入，从最后保存的 state 的 `next` 节点开始，已完成节点不重跑。）
5. 恢复时正在执行的那个节点会怎样？（答：它没有完成就不会有 checkpoint，恢复后整个节点重新执行——所以节点要尽量幂等，有副作用的写操作必须放在审批之后单独节点里。）
6. 降级到备用模型有什么隐患？（答：能力差异：tool calling / JSON 输出质量可能更差，需要在评测中单独测；成本与数据合规（本地 Ollama 更安全）也不同。）

## 8. 对 DA-01 的贡献

WorkPilot 的 Agent 从「能跑」变成「扛得住」：单一 LLM 供应商故障不再导致服务不可用，长任务进程中断可续跑，每类故障有确定的处理路径——这是 F8 交付运维与 P2「生产护栏」的核心证据。

## 9. 求职映射（D 线）

- 岗位能力：LLM 应用可靠性（分层重试、多供应商降级）、持久化执行（checkpoint）、故障注入测试。
- 对应岗位：AI Engineer、AI Platform Engineer、AI Agent Engineer。
- 简历 bullet 草稿：为 LLM Gateway 设计多 provider 自动降级（DeepSeek → Qwen/Ollama），结合节点级重试与 SQLite checkpoint 实现 Agent 断点续跑；故障注入测试覆盖工具超时、LLM 5xx、全部 provider 不可用等 \_\_ 种场景。
- 面试可能问：
  - Q：多层重试会有什么问题，你怎么设计？要点：重试风暴与延迟放大，每类错误单一负责层，`LLMUnavailable` 快速失败，工具错误转观察。
  - Q：LangGraph checkpoint 恢复时如何避免重复副作用？要点：超步级保存、未完成节点重跑、节点幂等、写操作独立成审批后节点（W12）。

## 10. 卡住时的处理

| 现象                                                           | 处理                                                                                        |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `add_node() got an unexpected keyword argument 'retry_policy'` | 旧版本用 `retry=`；或 `uv add -U langgraph` 后再试                                          |
| `NotImplementedError` / 提示 SqliteSaver 不支持 async          | 异步图用 `AsyncSqliteSaver`（`langgraph.checkpoint.sqlite.aio`）；`uv add aiosqlite` 若缺失 |
| `--resume` 后从头开始执行                                      | 确认传入的输入是 `None` 且 `thread_id` 与之前一致；确认两次用的是同一个 db 文件路径         |
| respx 拦截不到 OpenAI SDK 请求                                 | URL 必须与 `base_url + /chat/completions` 完全一致；测试中关闭 Gateway 重试退避避免超时     |
| Ollama 模型不调用工具                                          | 换支持 tool calling 的模型（如 qwen2.5 系列）；本周只要求 mock 单测，真实演练可跳过         |
| FastAPI 启动报 lifespan 冲突                                   | phase_01 已有 lifespan 时把 `async with AsyncSqliteSaver...` 嵌入原函数，不要定义第二个     |

## 11. 产出记录（执行时填写）

- 备用 provider：\_**\_（DashScope / Ollama），真实演练结果：\_\_**
- `--resume` 演示：中断前 step_count **，恢复后 next = \_\_**，最终 stop_reason \_\_\_\_
- 测试通过数：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day42「v0 vs v1 对比 + ADR + JD 追踪」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
