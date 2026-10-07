# Day 27 · 2026-11-10 · Week 07 Task 2：配置 / 健康检查 / JSON 日志 / request_id

## 0. 今天只做一件事

让 api 具备「上线后能被看见」的最小可观测性：配置缺失即启动失败、`/health` 与 `/ready` 分离、JSON 日志每行带 `request_id`、响应头回传 `X-Request-ID`、所有错误统一为 `{"error":{"code","message","request_id"}}`。

不碰：Trace / Span 表（W15）、成本看板（W15）、Prometheus / OpenTelemetry / ELK、日志轮转、告警。

## 1. 资产锚点

- 构建模块：M5.2 配置 / 密钥 / 健康检查 / JSON 日志、M9.1 request_id（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`curl -i` 可见 `X-Request-ID`；`make logs` 是 JSON 行；`/ready` 返回各依赖状态；Qdrant 停掉时 `/ready` = 503；前端错误条能显示 request_id
- 今日 AI 实际应用：LLM 请求慢且贵，一次问答涉及检索 + 生成多步——request_id 把同一次问答的检索日志、LLM 调用日志、错误串起来，是 W15 Trace / 成本账本的地基

## 2. 起点（前置确认）

- 已有：Day26 的 compose；`app/core/config.py`（pydantic-settings）；W3 的 LLM 调用日志（可能是 print 或普通 logging）。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
sed -n '1,80p' app/core/config.py                     # 哪些字段有默认值、哪些是密钥
grep -rn "print(" app/ | grep -v tests | head          # 需要改为 logger 的地方
grep -rn "logging.basicConfig\|getLogger" app/ | head
grep -n "include_router\|add_middleware" app/main.py
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `.env` 删掉 `LLM_API_KEY` 后启动：进程立即退出，错误信息指明缺少的字段（恢复后正常）
- [ ] `APP_ENV=prod` 且 embedding 指向 `11434`（Ollama）时启动失败（prod 约束生效）
- [ ] `curl -i localhost:8080/v1/kb/docs` 响应头含 `X-Request-ID`，`make logs` 中该请求的访问日志 `request_id` 相同
- [ ] 带 `-H 'X-Request-ID: my-trace-0001'` 请求时被透传；带非法值（含空格 / 引号）时被替换为新 id
- [ ] `docker compose -p workpilot stop qdrant` 后 `curl -s localhost:8080/ready` → 503 + `checks.qdrant` 失败；恢复后 200
- [ ] 触发 404 / 422 / 500 时响应体均为统一格式，500 响应不含 Traceback 和密钥
- [ ] `uv run pytest -q` 通过（新增 3 个测试）；已 commit + push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                                           |
| ------- | ------ | ------------------------------------------------------------------------------ |
| 0–10    | P0     | 前置确认                                                                       |
| 10–25   | P0     | config.py fail fast + SecretStr + prod 校验                                    |
| 25–50   | P0     | logging.py（JsonFormatter）+ middleware.py（request_id + 访问日志 + 兜底 500） |
| 50–65   | P0     | errors.py 统一错误格式                                                         |
| 65–80   | P0     | health.py `/health` `/ready`                                                   |
| 80–100  | P0     | 3 个 pytest + compose 中验证 + 提交                                            |
| 100–110 | P1     | 把 `print` 改为 `logger`；LLM 调用日志带 model / tokens / latency              |
| 110–120 | P1     | 前端错误条显示 `request_id`（Day22 的 `ApiError.requestId`）                   |

时间不足时最低保留：request_id 中间件 + 统一错误体 + `/ready`。

## 5. 今日学习（只学完成任务必须的）

- liveness（`/health`）只回答「进程活着吗」，不查依赖，避免依赖抖动导致容器被反复重启；readiness（`/ready`）回答「能接流量吗」，检查依赖。
- `contextvars.ContextVar` 在 asyncio 中按任务隔离，适合保存「当前请求的 request_id」，任意深度的函数都能读到而不用层层传参。
- `logging.Filter` 可以给每条 LogRecord 注入字段；`Formatter` 决定输出格式（JSON）。
- pydantic-settings：无默认值的字段即必填，实例化时缺失即抛 `ValidationError`；`SecretStr` 打印时显示 `**********`。
- 资料：https://docs.python.org/3/library/contextvars.html 、https://docs.python.org/3/howto/logging-cookbook.html 、https://docs.pydantic.dev/latest/concepts/pydantic_settings/ 、https://fastapi.tiangolo.com/tutorial/handling-errors/ 、https://docs.docker.com/reference/compose-file/services/#healthcheck

## 6. 执行步骤

### Step 1 · Fail fast 配置（app/core/config.py，保留你已有字段名，只调整「必填 / 密钥 / 校验」）

```python
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["dev", "prod"] = "dev"
    log_level: str = "INFO"
    log_json: bool = True

    llm_base_url: str                      # 无默认值 = 必填
    llm_api_key: SecretStr                 # 打印 / repr 时自动打码
    llm_model: str = "deepseek-chat"
    embedding_base_url: str
    embedding_api_key: SecretStr | None = None
    embedding_model: str = "bge-m3"
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "sqlite:///data/workpilot.db"

    @model_validator(mode="after")
    def _prod_guard(self) -> "Settings":
        if self.app_env == "prod":
            if self.embedding_api_key is None:
                raise ValueError("APP_ENV=prod 需要 EMBEDDING_API_KEY（SiliconFlow）")
            if ":11434" in self.embedding_base_url:
                raise ValueError("APP_ENV=prod 不能使用本机 Ollama 作为 embedding")
        return self


settings = Settings()   # 模块导入即校验：缺字段 → 进程启动失败（fail fast）
```

同步更新 `.env.example`：每个键一行注释说明，**无真实值**。

### Step 2 · JSON 日志（app/core/logging.py）

```python
import json
import logging
import sys
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
_EXTRA_KEYS = ("method", "path", "status", "latency_ms", "model", "tokens", "doc_id")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        payload.update({k: getattr(record, k) for k in _EXTRA_KEYS if hasattr(record, k)})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)   # 堆栈只进日志，不进响应
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_logs: bool = True) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(JsonFormatter() if json_logs else
                         logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    logging.getLogger("uvicorn.access").disabled = True     # 用我们自己的访问日志替代
```

### Step 3 · request_id 中间件 + 统一错误（app/core/middleware.py、app/core/errors.py）——必须自己理解

```python
# app/core/errors.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import request_id_var

_CODES = {400: "bad_request", 401: "unauthorized", 403: "forbidden", 404: "not_found",
          413: "payload_too_large", 415: "unsupported_media_type", 422: "validation_error",
          429: "rate_limited", 503: "unavailable"}


def error_response(status: int, message: str, code: str | None = None) -> JSONResponse:
    rid = request_id_var.get()
    return JSONResponse(status_code=status, headers={"X-Request-ID": rid},
                        content={"error": {"code": code or _CODES.get(status, "error"),
                                           "message": message, "request_id": rid}})


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        return error_response(exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        fields = ", ".join(".".join(str(p) for p in e["loc"]) for e in exc.errors())
        return error_response(422, f"invalid request fields: {fields}")   # 不回显用户输入值
```

```python
# app/core/middleware.py
import logging, re, time, uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.errors import error_response
from app.core.logging import request_id_var

_VALID_RID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")   # 拒绝换行 / 引号，防日志注入
access_log = logging.getLogger("access")
logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        incoming = request.headers.get("x-request-id", "")
        rid = incoming if _VALID_RID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(rid)
        start, status = time.perf_counter(), 500
        try:
            try:
                response = await call_next(request)
            except Exception:                                # 未处理异常：记堆栈，回通用 500
                logger.exception("unhandled error")
                response = error_response(500, "internal server error", "internal_error")
            status = response.status_code
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            access_log.info("request", extra={"method": request.method, "path": request.url.path,
                            "status": status, "latency_ms": round((time.perf_counter() - start) * 1000, 1)})
            request_id_var.reset(token)
```

`main.py`：`setup_logging(settings.log_level, settings.log_json)` → `install_error_handlers(app)` → `app.add_middleware(RequestIdMiddleware)`。SSE 的 latency 是「到响应头」的时间；流中途出错仍按 W3 约定发 `event: error`。

### Step 4 · 健康检查（app/routes/health.py）

```python
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel import Session

from app.core.config import settings
from app.db.session import get_session
from app.rag.store import get_qdrant            # 换成你 W4 的 Qdrant 客户端获取方式

router = APIRouter(tags=["health"])


@router.get("/health")
def health():                                    # liveness：不查依赖
    return {"status": "ok", "env": settings.app_env}


@router.get("/ready")
def ready(s: Session = Depends(get_session)):    # readiness：逐项检查依赖
    checks: dict[str, str] = {}
    try:
        get_qdrant().get_collections(); checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"fail: {type(e).__name__}"      # 只给异常类型，不给连接串
    try:
        s.execute(text("SELECT 1")); checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"fail: {type(e).__name__}"
    checks["llm_key"] = "ok" if settings.llm_api_key.get_secret_value() else "missing"
    ok = all(v == "ok" for v in checks.values())
    return JSONResponse(status_code=200 if ok else 503,
                        content={"status": "ready" if ok else "not_ready", "checks": checks})
```

compose 的 healthcheck 继续用 `/health`（Day26 已配）；`/ready` 给部署脚本和人工排障用，Day28 生产 Caddy **不对外暴露** `/ready`。

### Step 5 · 测试（tests/test_observability.py）

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_request_id_roundtrip():
    r = client.get("/health", headers={"X-Request-ID": "trace-12345678"})
    assert r.headers["X-Request-ID"] == "trace-12345678"


def test_invalid_request_id_replaced():
    r = client.get("/health", headers={"X-Request-ID": "bad id\"<>"})
    assert r.headers["X-Request-ID"] != "bad id\"<>" and len(r.headers["X-Request-ID"]) == 32


def test_404_unified_error():
    r = client.get("/v1/route-does-not-exist")          # 不依赖数据库，路由不存在即 404
    body = r.json()
    assert r.status_code == 404 and body["error"]["code"] == "not_found"
    assert body["error"]["request_id"] == r.headers["X-Request-ID"]
```

### Step 6 · 在容器中验证 + 提交

```bash
cd ~/lab/workpilot && make up
curl -si localhost:8080/v1/kb/docs | grep -i x-request-id
make logs | grep '"path": "/v1/kb/docs"' | tail -1
docker compose -p workpilot stop qdrant && curl -s -w "\n%{http_code}\n" localhost:8080/ready
docker compose -p workpilot start qdrant
git add apps/api .env.example
git commit -m "feat(api): fail-fast settings, json logging with request id, unified errors, readiness probe"
git push
```

（`/ready` 若被 Caddy 的 SPA 兜底吃掉，在 dev Caddyfile 里加 `handle /ready { reverse_proxy api:8000 }`，仅限 dev。）

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 compose healthcheck 用 `/health` 不用 `/ready`？（答：Qdrant 短暂抖动时 `/ready` 失败会让 api 被标记 unhealthy 甚至被重启，扩大故障；存活与就绪要分开）
2. 为什么要校验传入的 `X-Request-ID`？（答：头部可被客户端控制，含换行 / 引号会伪造日志行或破坏 JSON 解析，属于日志注入）
3. 为什么 500 响应只给 `internal server error`？（答：堆栈会暴露路径、依赖版本、甚至密钥片段；详细信息只写日志，用 request_id 关联）
4. contextvar 为什么在 `finally` 里 reset？（答：恢复到进入前的值，避免同一任务后续逻辑读到上一个请求的 id）
5. `SecretStr` 防的是什么？（答：防止密钥在日志、异常信息、`repr(settings)` 中被意外打印；取值必须显式 `get_secret_value()`）

## 8. 对 DA-01 的贡献

F8 运维能力与 M9 可观测性起步：WorkPilot 从「出问题只能本地复现」变成「凭 request_id 可在线定位」。W15 的 trace / span 表、成本账本会直接复用 `request_id_var` 作为 trace_id。

## 9. 求职映射（D 线）

- 岗位能力：可观测性、生产配置管理、错误处理规范
- 对应岗位：AI Engineer / AI Platform Engineer / Backend
- 简历 bullet 草稿：为 LLM 服务实现基于 contextvars 的 request_id 全链路透传与 JSON 结构化日志，区分 liveness / readiness 健康检查，统一错误响应规范（不泄漏堆栈 / 密钥），配置缺失启动即失败。
- 面试可能问：
  - 「LLM 应用的可观测性和普通 Web 服务有什么不同？」要点：除了延迟 / 错误率还要记录 tokens、成本、模型、检索命中、prompt 版本；一次请求多次 LLM 调用需要 trace 串联（W15）。
  - 「配置怎么管理？」要点：12-Factor 环境变量、`.env.example` 文档化、密钥不入库、启动即校验、dev / prod 约束不同。

## 10. 卡住时的处理

| 现象                                                                 | 处理                                                                                                                |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 测试导入 `app.main` 时 `ValidationError: llm_api_key Field required` | 预期行为（fail fast）：在 `tests/conftest.py` 顶部 `os.environ.setdefault("LLM_API_KEY", "test")` 等，再 import app |
| 日志里同时有 JSON 和普通文本行                                       | uvicorn 自带 handler：确认 `setup_logging` 在创建 app 前调用、`uvicorn.access` 已禁用；`uvicorn.error` 可保留       |
| `request_id` 在后台任务（Day25 导入）日志里是 `-`                    | BackgroundTasks 在响应后执行、上下文已 reset：把 `rid` 作为参数传入任务并在任务开头 `request_id_var.set(rid)`       |
| 中间件加了但 404 响应没有 `X-Request-ID`                             | 检查 `error_response` 是否设置了 header、`install_error_handlers(app)` 是否被调用；`curl -si` 看原始响应头          |
| `/ready` 返回 HTML                                                   | 请求被 Caddy 的 SPA `handle` 接住：dev Caddyfile 加 `/ready` 反代，或直接 `docker compose exec api` 内部请求        |

## 11. 产出记录（执行时填写）

- 一条访问日志样例（脱敏后贴这里）：\_\_\_\_
- `/ready` 失败场景输出：\_\_\_\_
- 改掉的 `print` 数量：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day28（云部署 + HTTPS + 访问保护）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
