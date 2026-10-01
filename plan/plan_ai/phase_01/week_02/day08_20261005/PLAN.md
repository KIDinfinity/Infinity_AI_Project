# Day 08 · 2026-10-05 · Week 02 Task 3：LLM Gateway v0

## 0. 今天只做一件事

实现 WorkPilot 唯一的 LLM 出口 `LLMGateway`：经 OpenAI SDK 调 DeepSeek，带超时、指数退避重试（最多 3 次）、错误归一化、token / 延迟日志，并暴露 `POST /v1/chat`；单测不触网，超时返回结构化 504 且不泄漏 key。

不碰：结构化输出 / JSON mode（Day11）、流式 SSE 与成本计价（Day12）、prompt 文件（Day11）、provider 自动 fallback（W11）、Embedding（Day09）。

## 1. 资产锚点

- 构建模块：M1.1 Provider 抽象、M1.2 可靠性（timeout / retry）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.1 做准备（v0.1 = LLM Gateway：结构化输出 + 流式 + 成本 + CLI）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`curl /v1/chat` 得到 DeepSeek 回答，响应含 `prompt_tokens / completion_tokens / latency_ms`；超时场景 HTTP 504 + `llm_timeout`；`make test` 覆盖成功 / 重试后成功 / 鉴权失败不重试 / 重试耗尽 4 个场景。
- 今日 AI 实际应用：学 OpenAI 兼容协议 + 重试策略 → 落在 `apps/api/app/llm/gateway.py`；此后 RAG（W4）、Agent（W10）、评测 judge（W5）全部只调用 `LLMGateway.chat()`。

## 2. 起点（前置确认）

- 已有：`apps/api` FastAPI 骨架、`Settings`、`/health`、`make dev/test/lint`（Day07）。
- 需确认：

```bash
cd ~/lab/workpilot && git pull && make test       # 期望 2 passed
grep -E '^LLM_' .env.example                       # 期望 4 个键
git check-ignore .env && echo ".env 已忽略"
```

## 3. 验收对齐（做完要能勾掉）

- [ ] DeepSeek 已小额充值，key 只存在于 `~/lab/workpilot/.env`
- [ ] `curl /v1/chat` 返回 JSON 含 `content`、`model`、`prompt_tokens`、`completion_tokens`、`latency_ms`；服务日志有一行 `llm_call status=ok ...`
- [ ] `make test` 通过（≥ 6 passed，不触网，断网也能过）
- [ ] `cd apps/api && uv run pytest -m live -q` 通过（1 passed，真实调用）
- [ ] `LLM_TIMEOUT_S=0.001 make dev` 后 curl 得到 HTTP 504 + `{"error":{"code":"llm_timeout",...}}`
- [ ] `git -C ~/lab/workpilot log -p | grep -c 'sk-'` 输出 0；日志中无 key
- [ ] `make lint` 通过，已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                      |
| ----------- | ------ | ------------------------------------------------------------------------- |
| 0–15 min    | P0     | 申请 DeepSeek key、充值、写 `.env`；`uv add openai tenacity`              |
| 15–30 min   | P0     | `config.py` 加字段 + `errors.py` + `schemas.py`                           |
| 30–60 min   | P0     | `gateway.py`（重试 / 错误映射 / 日志）+ `routes/chat.py` + `main.py` 注册 |
| 60–85 min   | P0     | `tests/test_llm_gateway.py`（4 个离线场景 + live）                        |
| 85–100 min  | P0     | 手动验证 curl / 超时 504 / 泄漏检查                                       |
| 100–110 min | P0     | lint + 提交                                                               |
| 110–120 min | P2     | 同一网关切到本地 Ollama 模型（需 Day09 装好 Ollama，可延期）              |

时间不足时最低保留：gateway + `/v1/chat` + 「重试耗尽 → 504」单测 + push；live 冒烟顺延到 Day09 开头 5 分钟。

## 5. 今日学习（只学完成任务必须的）

- **OpenAI 兼容协议**：DeepSeek / Qwen / Ollama 都实现 `POST {base_url}/chat/completions`，换供应商 = 换 `base_url + api_key + model`。
- **该重试的错误**：超时、连接失败、429 限流、5xx；**不该重试**：400 参数错误、401 鉴权、内容审核拒绝——重试只会浪费钱和时间。
- **指数退避**：等待 0.5s → 1s → 2s…（有上限），给上游恢复时间并避免「重试风暴」；SDK 自带 `max_retries`（默认 2）要关掉，否则与 tenacity 叠加成 9 次。
- **错误归一化**：对外只返回 `{"error":{"code","message"}}`，不透传上游原始报错（可能含请求头、内部地址）。
- **live 测试隔离**：默认 `-m 'not live'`，CI 和日常 `make test` 不花钱。
- 资料：https://api-docs.deepseek.com/ 、https://github.com/openai/openai-python 、https://tenacity.readthedocs.io/ 、https://fastapi.tiangolo.com/tutorial/handling-errors/ 、https://docs.pytest.org/en/stable/example/markers.html

## 6. 执行步骤

### Step 1 · Key 与依赖（P0）

1. 打开 https://platform.deepseek.com/ → 注册 → 充值小额（如 ¥10–20，预付费本身就是硬上限）；若平台提供余额 / 用量提醒，开启。
2. 「API keys」→ 创建，名称 `workpilot-dev`，复制 key **直接粘贴到 `.env`**，不经过聊天工具、笔记或截图：

```dotenv
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=sk-...
LLM_MODEL=deepseek-chat
LLM_TIMEOUT_S=30
```

3. 按规范「新增键与代码同一提交」，在 `.env.example` 的 LLM 段追加：`# [可选] 最大尝试次数（含首次），默认 3` 和 `LLM_MAX_ATTEMPTS=3`。

```bash
cd ~/lab/workpilot/apps/api
uv add openai tenacity
mkdir -p app/llm && touch app/llm/__init__.py
```

### Step 2 · 配置与错误（P0）

`app/core/config.py` 的 `Settings` 中追加（顶部 `from pydantic import SecretStr`）：

```python
    llm_base_url: str = "https://api.deepseek.com"
    llm_api_key: SecretStr = SecretStr("")   # SecretStr：print / repr 显示为 **********
    llm_model: str = "deepseek-chat"
    llm_timeout_s: float = 30.0
    llm_max_attempts: int = 3
```

`app/core/errors.py`：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """可预期错误：对外只暴露 code + message，不带堆栈、上游原文和密钥。"""

    def __init__(self, code: str, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.code, self.message, self.status_code = code, message, status_code


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle(_: Request, exc: AppError) -> JSONResponse:
        body = {"error": {"code": exc.code, "message": exc.message}}
        return JSONResponse(status_code=exc.status_code, content=body)
```

`app/llm/schemas.py`：

```python
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    temperature: float = Field(0.3, ge=0, le=2)
    max_tokens: int | None = Field(None, ge=1, le=4096)


class ChatResult(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
```

### Step 3 · Gateway 核心（P0，必须自己理解每一行）

`app/llm/gateway.py`：

```python
import logging
import time
from typing import Any

from openai import (APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI,
                    AuthenticationError, RateLimitError)
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.core.errors import AppError
from app.llm.schemas import ChatResult

log = logging.getLogger("workpilot.llm")

# 顺序重要：子类在前（APITimeoutError ⊂ APIConnectionError；Auth/RateLimit ⊂ APIStatusError）
_ERROR_MAP = [
    (APITimeoutError, "llm_timeout", "上游模型响应超时", 504),
    (AuthenticationError, "llm_auth_failed", "上游鉴权失败，请检查 LLM_API_KEY 配置", 502),
    (RateLimitError, "llm_rate_limited", "上游限流，请稍后重试", 503),
    (APIConnectionError, "llm_unavailable", "无法连接上游模型", 502),
    (APIStatusError, "llm_upstream_error", "上游模型返回错误", 502),
]


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, (APITimeoutError, APIConnectionError, RateLimitError)):
        return True
    return isinstance(exc, APIStatusError) and exc.status_code >= 500


class LLMGateway:
    def __init__(self, settings: Settings, client: Any | None = None, backoff_s: float = 0.5):
        self.model = settings.llm_model
        self.max_attempts = settings.llm_max_attempts
        self.backoff_s = backoff_s  # 测试传 0，免等待
        self._client = client or AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key.get_secret_value(),
            timeout=settings.llm_timeout_s,
            max_retries=0,  # 关掉 SDK 自带重试，统一由 tenacity 控制
        )

    async def chat(self, messages: list[dict[str, str]], **kw: Any) -> ChatResult:
        start, attempts = time.perf_counter(), 0
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self.max_attempts),
                wait=wait_exponential(multiplier=self.backoff_s, max=8),
                retry=retry_if_exception(_retryable),
                reraise=True,  # 用尽后抛原始异常，而不是 tenacity.RetryError
            ):
                with attempt:
                    attempts = attempt.retry_state.attempt_number
                    resp = await self._client.chat.completions.create(
                        model=self.model, messages=messages, **kw
                    )
        except Exception as e:
            ms = int((time.perf_counter() - start) * 1000)
            for exc_type, code, msg, status in _ERROR_MAP:
                if isinstance(e, exc_type):
                    log.warning("llm_call status=error code=%s model=%s attempts=%d latency_ms=%d",
                                code, self.model, attempts, ms)
                    raise AppError(code, msg, status) from e
            raise
        ms = int((time.perf_counter() - start) * 1000)
        usage = resp.usage
        result = ChatResult(
            content=resp.choices[0].message.content or "",
            model=resp.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency_ms=ms,
        )
        log.info("llm_call status=ok model=%s attempts=%d latency_ms=%d prompt_tokens=%d "
                 "completion_tokens=%d", result.model, attempts, ms,
                 result.prompt_tokens, result.completion_tokens)
        return result  # 注意：日志只记元数据，不记 messages 内容与 key

    async def aclose(self) -> None:
        await self._client.close()
```

### Step 4 · 路由与注册（P0）

`app/routes/chat.py`：

```python
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request

from app.llm.gateway import LLMGateway
from app.llm.schemas import ChatRequest, ChatResult

router = APIRouter(prefix="/v1", tags=["llm"])


def get_gateway(request: Request) -> LLMGateway:
    return request.app.state.gateway


@router.post("/chat", response_model=ChatResult)
async def chat(body: ChatRequest, gw: Annotated[LLMGateway, Depends(get_gateway)]) -> ChatResult:
    kw: dict[str, Any] = {"temperature": body.temperature}
    if body.max_tokens:
        kw["max_tokens"] = body.max_tokens
    return await gw.chat([m.model_dump() for m in body.messages], **kw)
```

`app/main.py` 改为（新增 lifespan、日志、错误处理、chat 路由）：

```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.llm.gateway import LLMGateway
from app.routes import chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gateway = LLMGateway(get_settings())   # 进程级单例，复用 HTTP 连接池
    yield
    await app.state.gateway.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    for noisy in ("httpx", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    app = FastAPI(title="WorkPilot API", version=settings.app_version, lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(chat.router)
    return app


app = create_app()
```

### Step 5 · 测试（P0）

`pyproject.toml` 的 `[tool.pytest.ini_options]` 追加：

```toml
markers = ["live: 调用真实外部 API（需要 .env 密钥，会产生费用）"]
addopts = "-m 'not live'"
```

`tests/test_llm_gateway.py`（假 provider = 一个有 `chat.completions.create` 的对象，按脚本依次返回结果或抛异常）：

```python
import asyncio
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APITimeoutError, AuthenticationError

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.llm.gateway import LLMGateway
from app.main import app
from app.routes.chat import get_gateway

FAKE_KEY = "sk-test-should-never-leak"
REQ = httpx.Request("POST", "https://llm.invalid/chat/completions")
MSGS = [{"role": "user", "content": "ping"}]


def ok_resp(text="pong"):
    return SimpleNamespace(model="fake-model", usage=SimpleNamespace(prompt_tokens=5, completion_tokens=1),
                           choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


class FakeCompletions:
    def __init__(self, outcomes):
        self.outcomes, self.calls = list(outcomes), 0

    async def create(self, **kwargs):
        self.calls += 1
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


def make_gateway(outcomes):
    fake = FakeCompletions(outcomes)
    client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
    return LLMGateway(Settings(_env_file=None, llm_api_key=FAKE_KEY), client=client, backoff_s=0), fake


def test_success_returns_usage():
    gw, fake = make_gateway([ok_resp()])
    r = asyncio.run(gw.chat(MSGS))
    assert (r.content, r.prompt_tokens, fake.calls) == ("pong", 5, 1)


def test_retry_then_success():
    gw, fake = make_gateway([APITimeoutError(request=REQ), APITimeoutError(request=REQ), ok_resp()])
    assert asyncio.run(gw.chat(MSGS)).content == "pong" and fake.calls == 3


def test_auth_error_not_retried():
    err = AuthenticationError("bad key", response=httpx.Response(401, request=REQ), body=None)
    gw, fake = make_gateway([err])
    with pytest.raises(AppError) as ei:
        asyncio.run(gw.chat(MSGS))
    assert ei.value.code == "llm_auth_failed" and fake.calls == 1


def test_timeout_exhausted_returns_504_without_key():
    gw, fake = make_gateway([APITimeoutError(request=REQ)] * 3)
    app.dependency_overrides[get_gateway] = lambda: gw
    try:
        r = TestClient(app).post("/v1/chat", json={"messages": MSGS})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 504 and r.json()["error"]["code"] == "llm_timeout"
    assert FAKE_KEY not in r.text and fake.calls == 3


@pytest.mark.live
def test_live_deepseek_smoke():
    s = get_settings()
    if not s.llm_api_key.get_secret_value():
        pytest.skip("LLM_API_KEY 未配置")
    r = asyncio.run(LLMGateway(s).chat([{"role": "user", "content": "只回复 pong"}], max_tokens=5))
    assert r.content and r.prompt_tokens > 0
```

```bash
cd ~/lab/workpilot && make test                       # 期望 6 passed, 1 deselected
cd apps/api && uv run pytest -m live -q               # 期望 1 passed（真实调用，约几分钱以内）
```

### Step 6 · 手动验证（P0）

```bash
cd ~/lab/workpilot && make dev                         # 终端 A
curl -s localhost:8000/v1/chat -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用一句话解释什么是 RAG"}]}' | python3 -m json.tool
# 终端 A 日志期望：llm_call status=ok model=deepseek-chat attempts=1 latency_ms=... prompt_tokens=...

# 超时演练：Ctrl+C 停掉后
LLM_TIMEOUT_S=0.001 make dev
curl -s -w '\nHTTP %{http_code}\n' localhost:8000/v1/chat -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
# 期望：{"error":{"code":"llm_timeout","message":"上游模型响应超时"}}  HTTP 504；日志 attempts=3

grep -rn 'sk-' apps/api/app apps/api/tests | grep -v sk-test   # 期望无输出
```

### Step 7 · 切换 provider 验证（P2，Day09 装好 Ollama 后可回头做）

```bash
ollama pull qwen2.5:3b
LLM_BASE_URL=http://localhost:11434/v1 LLM_API_KEY=ollama LLM_MODEL=qwen2.5:3b make dev
# 同样的 curl，返回 model=qwen2.5:3b —— 证明 M1.1「一处配置切换 provider」，代码零改动
```

### Step 8 · 提交

```bash
cd ~/lab/workpilot/apps/api && uv run ruff format . && uv run ruff check --fix .   # 先自动格式化（拆长行、排序 import）
cd ~/lab/workpilot && make lint && make test
git status --short                    # 确认没有 .env
git add apps/api .env.example
git commit -m "feat(llm): add LLM gateway with timeout, retry, error mapping and /v1/chat"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 `AsyncOpenAI(max_retries=0)`？（答：SDK 默认自带 2 次重试，再叠加 tenacity 3 次会变成最多 9 次请求，延迟和费用失控）
2. 401 为什么不重试？（答：鉴权错误是确定性的，重试只会失败得更慢；应直接报配置问题）
3. `_ERROR_MAP` 为什么 `APITimeoutError` 必须在 `APIConnectionError` 前？（答：前者是后者子类，顺序反了会把超时误判为连接失败）
4. 对外为什么不直接返回上游错误信息？（答：可能包含内部地址、请求细节；统一 code 便于前端处理和监控统计）
5. 单测里如何做到「不触网」？（答：构造函数注入假 client；路由层用 `dependency_overrides` 替换 `get_gateway`）
6. lifespan 里创建 gateway 而不是每个请求创建，好处？（答：复用 HTTP 连接池，减少 TLS 握手延迟；退出时统一关闭）

## 8. 对 DA-01 的贡献

WorkPilot 有了唯一、可测试、可切换供应商的 LLM 出口：W3 在它上面加结构化输出、流式和成本记录即达成 v0.1；W4 RAG、W10 Agent、W5 LLM-judge 都复用它。超时 / 重试 / 错误码从第一天起统一，W15 的可观测与预算守卫只需在这一处加钩子。

## 9. 求职映射（D 线）

- 岗位能力：LLM API 集成、可靠性设计（timeout / retry / backoff）、错误处理、可测试性
- 对应岗位：LLM Engineer、AI 应用工程师、GenAI Application Engineer
- 简历 bullet 草稿：实现 OpenAI 兼容的 LLM Gateway（DeepSeek / Ollama 一处配置切换），统一超时、指数退避重试与错误码，单测覆盖 ** 个故障场景且不依赖网络；记录每次调用 token 与延迟，P50 延迟 ** ms。
- 面试可能问：
  - 「LLM 接口偶发超时 / 429 怎么处理？」→ 要点：区分可重试错误；指数退避 + 上限 + 总次数；关闭 SDK 重试避免叠加；返回结构化错误；W11 再加 provider fallback 与熔断。
  - 「为什么要自己包一层 Gateway，不直接在业务里调 SDK？」→ 要点：单点切换供应商、统一可靠性 / 计量 / 日志 / 护栏、测试可替换。

## 10. 卡住时的处理

| 现象                                                        | 处理                                                                                                  |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| curl 返回 502 `llm_auth_failed`                             | `.env` 的 `LLM_API_KEY` 为空或有多余空格 / 引号；改后**重启** `make dev`（`get_settings` 有缓存）     |
| 返回 502 `llm_unavailable`                                  | 网络不通：`curl -I https://api.deepseek.com` 检查；不要给 DeepSeek 走境外代理                         |
| 返回 422                                                    | 请求体不符合 `ChatRequest`（如 role 拼错、messages 为空），看 `detail`                                |
| 测试里 `TypeError: __init__() missing ... 'body'`           | `AuthenticationError` 需要 `response=` 与 `body=` 关键字参数，照 Step 5 写                            |
| `AttributeError: 'State' object has no attribute 'gateway'` | 应用启动时 lifespan 未执行；检查 `FastAPI(..., lifespan=lifespan)`；测试中必须 override `get_gateway` |
| live 测试被 deselected                                      | 需显式 `uv run pytest -m live`；`addopts` 默认排除 live                                               |

## 11. 产出记录（执行时填写）

- DeepSeek 充值金额 / 当前余额：\_\_\_\_
- 首次 `/v1/chat` 的 latency_ms / prompt_tokens / completion_tokens：\_\_\_\_
- 超时演练：HTTP 码 / attempts / 总耗时：\_\_\_\_
- `make test` 结果：\_\_\_\_
- P2 是否完成（Ollama 模型名）：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → 明天进入 Day09 Task 4（MinIO + Qdrant + Ollama bge-m3）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
