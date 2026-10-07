# Day 12 · 2026-10-13 · Week 03 Task 2：Streaming SSE + 成本记录 + CLI 聊天

## 0. 今天只做一件事

让 Gateway 支持流式输出（SSE），并让每一次 LLM 调用都留下 tokens / 成本 / 延迟记录；用一个 CLI 聊天脚本把它们串起来演示。

不碰：前端页面（W6）、数据库存储成本（W15 迁库）、预算守卫/限流（W15）、WebSocket。

## 1. 资产锚点

- 构建模块：M1.4 Streaming、M1.5 Token / 成本计量（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.1 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`curl -N` 看到逐 token 输出；每次调用在 `data/logs/llm_calls.jsonl` 多一行；`scripts/chat.py` 多轮聊天并显示累计成本；可测量「首 token 延迟 ttft_ms」与「单次成本」
- 今日 AI 实际应用：OpenAI SDK 流式 + usage 统计 → W4 `/v1/kb/ask/stream`、W6 Web 流式渲染、P1 指标「单次成本 < ¥0.02」直接用这里的数据

## 2. 起点（前置确认）

- 已有：Day11 的 `ChatResult` / `Usage`、`gateway.chat(**extra)`、`/v1/chat`。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
uv run pytest -m "not llm" -q                     # Day11 全绿
grep -n "data/" ../../.gitignore                  # data/ 是否已被忽略（应忽略，保留 data/sample/）
uv run uvicorn app.main:app --reload --port 8000  # 另开终端
```

- 打开 DeepSeek 文档确认 3 件事并记到第 11 节：① 是否支持 `stream_options.include_usage`；② usage 中 cache 命中字段名（`prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`）；③ 定价页的单位与币种（每百万 tokens，区分缓存命中输入 / 未命中输入 / 输出）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `curl -N` 调 `POST /v1/chat/stream`：出现多条 `event: token`，最后 1 条 `event: done`
- [ ] `done` 数据含 `usage.total_tokens > 0`、`cost`（已配置价格时非空）、`latency_ms`、`ttft_ms`、`request_id`
- [ ] 调一次 `/v1/chat` 或 `/v1/chat/stream`，`wc -l data/logs/llm_calls.jsonl` +1
- [ ] `uv run --project apps/api python scripts/chat.py`：3 轮对话 → `/cost` 显示累计 → `/reset` 后模型不记得上文 → `/exit` 退出
- [ ] `test_pricing.py`、`test_sse.py` 通过；`.env.example` 有价格键（无真实值以外的猜测数字）
- [ ] 已 push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                 |
| ------- | ------ | ---------------------------------------------------- |
| 0–15    | P0     | 读 DeepSeek 流式与定价文档、MDN SSE 格式             |
| 15–35   | P0     | config 价格键 + `pricing.py` + 单测 + `usage_log.py` |
| 35–65   | P0     | `gateway.stream()` + `/v1/chat/stream`               |
| 65–80   | P0     | `curl -N` 验证 + `test_sse.py`                       |
| 80–105  | P1     | `scripts/chat.py`                                    |
| 105–120 | P1     | 提交 + 自检                                          |

时间不足时最低保留：`stream()` + `/v1/chat/stream` + jsonl 日志；CLI 顺延到 Day14 开头 20 分钟。

## 5. 今日学习（只学完成任务必须的）

- SSE 报文格式：每个事件是若干 `field: value` 行，以空行结束；`event:` 指定事件名，`data:` 是负载（这里用单行 JSON）。
- OpenAI 兼容流式：`stream=True` 返回异步迭代器，每块 `chunk.choices[0].delta.content` 是增量；开启 `include_usage` 时最后一块 `choices` 为空、`usage` 有值。
- 流式请求的重试只能在「第一个 token 之前」做；已输出给用户的内容无法回滚。
- 成本 = 缓存命中输入 × 单价 + 未命中输入 × 单价 + 输出 × 单价（单价按每百万 tokens）；价格会变，必须配置化。
- 资料：https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events 、https://api-docs.deepseek.com/api/create-chat-completion 、https://api-docs.deepseek.com/quick_start/pricing 、https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse 、https://www.python-httpx.org/quickstart/#streaming-responses

## 6. 执行步骤

### Step 1 · 配置与价格（数值自己从官方定价页抄）

`app/core/config.py` 的 `Settings` 增加：

```python
price_currency: str = "CNY"
price_input_hit_per_m: float | None = None     # 每百万 tokens，缓存命中输入
price_input_miss_per_m: float | None = None    # 每百万 tokens，缓存未命中输入
price_output_per_m: float | None = None        # 每百万 tokens，输出
llm_log_path: Path = REPO_ROOT / "data" / "logs" / "llm_calls.jsonl"
```

`.env.example` 追加（只写键和注释）：

```bash
# 价格：从 https://api-docs.deepseek.com/quick_start/pricing 抄写当前 deepseek-chat 价格（每百万 tokens）
PRICE_CURRENCY=CNY
PRICE_INPUT_HIT_PER_M=
PRICE_INPUT_MISS_PER_M=
PRICE_OUTPUT_PER_M=
```

自己的 `apps/api/.env` 填真实值，并在 `.env` 注释里写抄写日期。

`app/llm/schemas.py` 的 `ChatResult` 增加字段：

```python
request_id: str = ""
cost: float | None = None
ttft_ms: int | None = None          # 首 token 延迟，仅流式
usage_estimated: bool = False
```

`app/llm/pricing.py`：

```python
from app.core.config import settings
from app.llm.schemas import Usage

def calc_cost(u: Usage) -> float | None:
    s = settings
    if None in (s.price_input_hit_per_m, s.price_input_miss_per_m, s.price_output_per_m):
        return None                                  # 未配置价格：不猜
    miss = max(u.prompt_tokens - u.cache_hit_tokens, 0)
    total = (u.cache_hit_tokens * s.price_input_hit_per_m
             + miss * s.price_input_miss_per_m
             + u.completion_tokens * s.price_output_per_m)
    return round(total / 1_000_000, 6)

def estimate_tokens(text: str) -> int:
    """无 usage 时的粗估：以 DeepSeek 文档的中英文换算比例为准，这里用保守值。"""
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return int(cjk * 0.6 + (len(text) - cjk) * 0.3) + 1
```

`tests/test_pricing.py`：用 `monkeypatch.setattr(settings, ...)` 设置假单价（如 1/2/3），断言 `Usage(prompt_tokens=1000, cache_hit_tokens=400, completion_tokens=500)` 的成本计算正确；未配置时返回 `None`。

### Step 2 · 调用日志

`app/llm/usage_log.py`：

```python
import json, time
from app.core.config import settings
from app.llm.schemas import ChatResult

def log_call(result: ChatResult, *, stream: bool, ok: bool = True, error: str | None = None) -> None:
    path = settings.llm_log_path
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "request_id": result.request_id,
        "model": result.model, "stream": stream, "ok": ok, "error": error,
        "prompt_tokens": result.usage.prompt_tokens, "completion_tokens": result.usage.completion_tokens,
        "cache_hit_tokens": result.usage.cache_hit_tokens, "usage_estimated": result.usage_estimated,
        "cost": result.cost, "currency": settings.price_currency,
        "latency_ms": result.latency_ms, "ttft_ms": result.ttft_ms,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
```

注意：日志不写 messages 原文（避免日后把敏感内容落盘；W15 再做可选脱敏存档）。

在 `gateway.chat()` 末尾：生成 `request_id = uuid.uuid4().hex[:12]`、`cost = calc_cost(usage)`，`log_call(result, stream=False)` 后返回。

### Step 3 · gateway.stream()（核心逻辑自己写）

```python
async def stream(self, messages: list[dict], **extra) -> AsyncIterator[dict]:
    rid, t0, ttft = uuid.uuid4().hex[:12], time.perf_counter(), None
    resp = await self._client.chat.completions.create(          # 流式不走自动重试：首 token 后无法回滚
        model=self.model, messages=messages, stream=True,
        stream_options={"include_usage": True}, timeout=self.timeout, **extra)
    parts, raw_usage = [], None
    async for chunk in resp:
        if chunk.usage:
            raw_usage = chunk.usage
        if chunk.choices and chunk.choices[0].delta.content:
            if ttft is None:
                ttft = int((time.perf_counter() - t0) * 1000)
            parts.append(chunk.choices[0].delta.content)
            yield {"type": "token", "text": parts[-1]}
    content = "".join(parts)
    if raw_usage:
        usage = Usage(prompt_tokens=raw_usage.prompt_tokens, completion_tokens=raw_usage.completion_tokens,
                      total_tokens=raw_usage.total_tokens,
                      cache_hit_tokens=getattr(raw_usage, "prompt_cache_hit_tokens", 0) or 0)
    else:                                                       # 不支持 include_usage 时估算
        p = sum(estimate_tokens(m["content"]) for m in messages)
        c = estimate_tokens(content)
        usage = Usage(prompt_tokens=p, completion_tokens=c, total_tokens=p + c)
    result = ChatResult(content=content, model=self.model, usage=usage, request_id=rid,
                        latency_ms=int((time.perf_counter() - t0) * 1000), ttft_ms=ttft,
                        cost=calc_cost(usage), usage_estimated=raw_usage is None)
    log_call(result, stream=True)
    yield {"type": "done", "result": result}
```

> 若 DeepSeek 返回参数错误（不认 `stream_options`），去掉该参数，走估算分支，并在第 11 节记录。

### Step 4 · SSE 路由

`app/routes/chat.py` 追加：

```python
import json, logging
from fastapi.responses import StreamingResponse
log = logging.getLogger(__name__)

def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

@router.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):            # Day08 的请求模型（含 messages）
    async def gen():
        try:
            async for ev in gateway.stream([m.model_dump() for m in req.messages]):
                if ev["type"] == "token":
                    yield sse("token", {"text": ev["text"]})
                else:
                    r = ev["result"]
                    yield sse("done", r.model_dump(include={"request_id", "usage", "cost", "latency_ms",
                                                            "ttft_ms", "usage_estimated"}))
        except Exception:
            log.exception("chat stream failed")
            yield sse("error", {"message": "LLM 调用失败，请稍后重试"})   # 不把内部异常细节返回给客户端
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

验证（`-N` 关闭 curl 缓冲）：

```bash
curl -N -X POST localhost:8000/v1/chat/stream -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用三句话解释 SSE 和 WebSocket 的区别"}]}'
```

预期输出形如：

```text
event: token
data: {"text": "SSE"}

event: token
data: {"text": " 是单向"}
...
event: done
data: {"request_id": "3f9a0c1b2d4e", "usage": {"prompt_tokens": 18, "completion_tokens": 96, "total_tokens": 114, "cache_hit_tokens": 0}, "cost": 0.0002, "latency_ms": 2310, "ttft_ms": 480, "usage_estimated": false}
```

```bash
tail -n 2 ../../data/logs/llm_calls.jsonl
```

`tests/test_sse.py`（AI 生成样板）：monkeypatch 一个假 `gateway.stream` 依次 yield 2 个 token + done；用 `TestClient` 的 `client.stream("POST", "/v1/chat/stream", json=...)` 读取全文，断言包含 2 个 `event: token`、1 个 `event: done`；再测一个抛异常的假 stream → 出现 `event: error` 且不含异常原文。

### Step 5 · CLI 聊天（P1）

`scripts/chat.py`（只依赖 httpx，已随 openai SDK 安装）：

```python
import json, httpx

API = "http://localhost:8000/v1/chat/stream"

def stream_once(history: list[dict]) -> tuple[str, dict]:
    event, reply, done = None, [], {}
    with httpx.stream("POST", API, json={"messages": history}, timeout=httpx.Timeout(10, read=120)) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data = json.loads(line[5:].strip())
                if event == "token":
                    print(data["text"], end="", flush=True); reply.append(data["text"])
                elif event == "done":
                    done = data
                elif event == "error":
                    print(f"\n[error] {data['message']}")
    print()
    return "".join(reply), done

def main() -> None:
    history, calls, total = [], 0, 0.0
    print("WorkPilot CLI · /cost /reset /exit")
    while True:
        q = input("you> ").strip()
        if q == "/exit": break
        if q == "/reset": history.clear(); print("[history 已清空]"); continue
        if q == "/cost": print(f"[本会话] {calls} 次调用，累计成本 {total:.6f}"); continue
        if not q: continue
        history.append({"role": "user", "content": q})
        reply, done = stream_once(history)
        history.append({"role": "assistant", "content": reply})
        calls += 1; total += done.get("cost") or 0
        print(f"[tokens {done.get('usage', {}).get('total_tokens')} | cost {done.get('cost')} "
              f"| ttft {done.get('ttft_ms')}ms | total {done.get('latency_ms')}ms]")

if __name__ == "__main__":
    main()
```

```bash
cd ~/lab/workpilot && uv run --project apps/api python scripts/chat.py
```

演示脚本：「我叫小王」→「我刚才说我叫什么？」（应答对）→ `/reset` →「我刚才说我叫什么？」（应答不知道）→ `/cost`。

### Step 6 · 提交

```bash
cd ~/lab/workpilot
git add apps/api scripts/chat.py .env.example
git status --short | grep -E "\.env$|llm_calls" && echo "!! 不要提交 .env / 日志"
git commit -m "feat(llm): SSE streaming, cost calculation and call logging; add CLI chat"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. SSE 一个事件的结束标志是什么？（答：一个空行，即 `\n\n`。）
2. 为什么流式请求不在中途自动重试？（答：已经把部分 token 发给用户，重试会重复/错乱输出；只能在首 token 前重试或返回 error 事件。）
3. `ttft_ms` 和 `latency_ms` 分别反映什么？（答：首 token 延迟决定「感觉快不快」，总延迟决定吞吐与成本时长。）
4. 为什么价格不能硬编码？（答：价格会调整、有缓存命中/未命中/时段差异；配置化才能随官方更新且可追溯。）
5. 为什么日志不记录 messages 原文？（答：减少敏感信息落盘风险，成本统计不需要原文。）

## 8. 对 DA-01 的贡献

WorkPilot 有了流式交互（W6 Web 与 W4 KB 流式直接复用 `stream()` 和 SSE 事件约定）和第一版成本账本（jsonl），之后每个版本的「单次成本 / P95 延迟」都能被测量，而不是凭感觉。

## 9. 求职映射（D 线）

- 岗位能力：LLM Streaming、SSE、Token / 成本治理、可观测性基础。
- 对应岗位：AI Full-Stack Engineer、AI Engineer、AI Platform Engineer。
- 简历 bullet 草稿：「为 LLM Gateway 实现 SSE 流式输出与调用级成本核算（区分缓存命中/未命中输入），首 token 延迟 P50 **ms，单次对话平均成本 ¥**，全部调用写入结构化日志供后续账本与预算守卫使用。」
- 面试可能问：
  1. 「流式输出时怎么统计 token 和成本？」——要点：`include_usage` 拿最后一块 usage；不支持则估算并标记；按缓存命中/未命中/输出三类单价计算。
  2. 「前端怎么消费 POST 的 SSE？」——要点：`EventSource` 只支持 GET，POST 需用 `fetch` + `ReadableStream` 自己按空行切分事件（W6 实现）。

## 10. 卡住时的处理

| 现象                                                  | 处理                                                                                         |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| curl 一次性输出全部内容，没有「逐个」效果             | 加 `-N`；确认生成器每块都 `yield`；中间若有代理/中间件缓冲，响应头加 `X-Accel-Buffering: no` |
| `openai.BadRequestError` 提到 `stream_options`        | 该端点不支持，去掉参数走估算分支，第 11 节记录                                               |
| `done` 中 `cost` 为 `null`                            | `.env` 未填价格键或字段名不匹配（pydantic-settings 默认大小写不敏感，检查拼写）              |
| `TypeError: 'async_generator' object is not iterable` | 在同步函数里用了 `for`，改成 `async for`；StreamingResponse 可直接接收异步生成器             |
| CLI 报 `httpx.ReadTimeout`                            | 长回答超过 read 超时，调大 `read=120`；或服务端卡住看 uvicorn 日志                           |
| `llm_calls.jsonl` 出现在 `git status`                 | `.gitignore` 加 `data/*` 与 `!data/sample/`                                                  |

## 11. 产出记录（执行时填写）

- DeepSeek 是否支持 include_usage：\_**\_；cache 字段名：\_\_**；定价抄写日期：\_\_\_\_
- 一次流式调用 ttft / 总延迟 / tokens / 成本：\_**\_ / \_\_** / \_**\_ / \_\_**
- CLI 3 轮对话累计成本：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day13（DA-01 决策：场景包选型）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（Day13 是决策日，补课不超过 20 分钟）。
