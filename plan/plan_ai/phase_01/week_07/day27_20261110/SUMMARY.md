# Day 27 · Week 07 Task 2 · 配置 / 健康检查 / JSON 日志 / request_id —— 执行总结

> 依据 [PLAN.md](./PLAN.md) 逐 Step 执行，最终状态：**Task 2 DONE**（§12 完成判定满足）。代码仓库在 `~/lab/workpilot`（Gitea），本文件所在仓库仅保存 PLAN/SUMMARY。

## 一、做了什么（逐 Step 对应）

| Step | 结果 |
| --- | --- |
| Step 1 配置 fail-fast | `app/core/config.py` 新增 `log_json: bool = True` 字段 + `_validate_runtime` model_validator：`app_env=="test"` 跳过；prod 要求真实 `EMBEDDING_API_KEY` 且 embedding 不指向 `:11434`（本机 Ollama）；非 ollama 供应商要求对应 key 非空。缺失即 `ValueError`，进程启动即失败 |
| Step 2 JSON 日志 | 新建 `app/core/logging.py`：`request_id_var`（ContextVar，默认 `-`）、`RequestIdFilter`、`JsonFormatter`（含 `ts/level/logger/msg/request_id` + extra 字段 + exc 只进日志）、`setup_logging()`（禁用 `uvicorn.access`，用自带访问日志） |
| Step 3 request_id 中间件 + 统一错误 | 新建 `app/core/middleware.py`：`RequestIdMiddleware`（`_VALID_RID = ^[A-Za-z0-9._-]{8,64}$`，透传/替换、访问日志、未处理异常兜底 500、finally 里 reset contextvar）；`app/core/errors.py` 重写为 `error_response()` + 统一 handler（AppError / StarletteHTTPException / RequestValidationError），统一 `{"error":{"code","message","request_id"}}` + 响应头 `X-Request-ID` |
| Step 4 健康检查 | `app/routes/health.py` 新增 `/ready`（逐项检查 qdrant / db / llm_key，任一失败 503）；保留 `/health` 存活探针 |
| Step 5 测试 | 新建 `tests/test_observability.py`（3 例：request_id 透传、非法值替换、404 统一错误体）；同步更新 `test_conversations.py` 的 422 断言 |
| Step 6 容器验证 + 提交 | `make up` 全栈 healthy；curl 验证 X-Request-ID、/ready 503、404/422/500 统一格式全部通过；`git commit` + `git push`（`d48f685`） |

### 附带改动（执行中暴露）

- `deploy/Caddyfile`：新增 `handle /ready { reverse_proxy api:8000 }`（仅 dev，避免被 SPA 兜底）。
- `.env.example`：新增 `LOG_JSON=1` 文档行。
- `app/main.py`：`logging.basicConfig` → `setup_logging(...)`，注册 `RequestIdMiddleware`。

## 二、与原 PLAN 的偏差

1. **密钥字段名** → PLAN 示例用单一 `llm_api_key` 字段；现有代码已是 `llm_provider`（deepseek/doubao/ollama）+ `deepseek_api_key`/`doubao_api_key` 分 key + `llm_api_key` 为 **property**（回退供应商预设）。按 PLAN「保留已有字段名」要求，fail-fast 校验适配为「非 ollama 供应商缺对应 key 即失败」。
2. **`embedding_api_key` 保持 `str`** → 未改 `SecretStr`，避免动 `app/rag/embedding.py`（它直接 `AsyncOpenAI(api_key=...)`）。prod 校验用「值为 `""` 或 `ollama` 即判为缺失」表达原意。
3. **`/ready` 用 async + Annotated 依赖注入** → 匹配现有 async 路由风格，且 `Depends(get_session)` 直接作默认值会触发 ruff B008，改为 `Annotated[Session, Depends(get_session)]`。
4. **422 断言更新** → 原 `test_conversations.py` 断言旧 FastAPI 默认格式 `body["detail"]`，改统一格式后同步为 `body["error"]["message"]`。
5. **LLM 调用日志（P1）** → 无需新增：`app/llm/gateway.py` 已自带 `request_id`/`model`/`tokens`/`latency_ms`/`cost`，落盘 `data/logs/llm_calls.jsonl`。
6. **print 清理（P1）** → 未改：9 处 `print` 均在 CLI 脚本（`rag/ingest.py`、`rag/loaders/*.py`），不在请求路径，属可选清理。
7. **前端错误条（P1）** → 无需改：`apps/web/src/api/client.ts` 已读 `x-request-id` 头并解析 `body.error.message`。

## 三、产出记录（PLAN §11）

- 一条访问日志样例（脱敏）：
  ```json
  {"ts": "2026-11-10T00:58:33+0800", "level": "INFO", "logger": "access", "msg": "request", "request_id": "def702df44ec40f58507a166cac06d19", "method": "GET", "path": "/health", "status": 200, "latency_ms": 5.4}
  ```
- `/ready` 失败场景输出：
  ```json
  {"status":"not_ready","checks":{"qdrant":"fail: ResponseHandlingException","db":"ok","llm_key":"ok"}}  → HTTP 503
  ```
- 改掉的 `print` 数量：0（剩余 9 处均在 CLI 脚本，非请求路径，P1 可选）。
- 卡点：① Starlette 1.7.0 的 `BaseHTTPMiddleware.call_next` 会透传下游未处理异常，读源码确认 `try/except` 确实能兜底 500；② 旧 422 断言 `detail` → 统一格式 `error.message`；③ `Depends` 默认值触发 ruff B008，改 `Annotated`。
- 用时：约 100 分钟。

## 四、验收对齐（PLAN §3，7 条 —— 逐条完整命令）

> 以下命令全部自带 `cd` 绝对路径，**在任意目录打开终端粘贴即可执行**，都能得到期望结果。前置：全栈已运行（若未运行，先 `cd ~/lab/workpilot && make up`）。

### 1. 缺密钥启动即失败（fail-fast）

现有代码无 `LLM_API_KEY` 单字段，对应字段是 `DEEPSEEK_API_KEY`（偏差见 §二.1）。验证「非 ollama 供应商缺 key → 启动失败，错误指明缺失字段」：

```bash
cd ~/lab/workpilot/apps/api && uv run python -c "from app.core.config import Settings; Settings(_env_file=None, llm_provider='deepseek', deepseek_api_key='')"
```

**期望**：进程立即报错退出，错误信息含
`Value error, LLM_PROVIDER=deepseek 需要 DEEPSEEK_API_KEY`（恢复 `.env` 里的 key 后正常）。

### 2. `APP_ENV=prod` 且 embedding 指向本机 Ollama 时启动失败

```bash
cd ~/lab/workpilot/apps/api && uv run python -c "from app.core.config import Settings; Settings(_env_file=None, app_env='prod', embedding_base_url='http://localhost:11434/v1', embedding_api_key='ollama', deepseek_api_key='sk-test')"
```

**期望**：进程立即报错退出，错误信息含
`Value error, APP_ENV=prod 需要真实的 EMBEDDING_API_KEY（SiliconFlow）`。

### 3. 响应头含 `X-Request-ID`，且与访问日志 `request_id` 一致

第一步 —— 取响应头：

```bash
cd ~/lab/workpilot && curl -si localhost:8080/v1/kb/docs | grep -i 'x-request-id'
```

**期望**：输出一行 `X-Request-Id: <32 位十六进制 id>`（例如 `X-Request-Id: c619b1cafca047f599cc89e4fa532625`）。

第二步 —— 看访问日志（同一请求的 request_id 与上面一致）：

```bash
cd ~/lab/workpilot && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml logs api --tail=30 | grep '"path": "/v1/kb/docs"' | tail -1
```

**期望**：输出一行 JSON，`"logger": "access"`、含 `method/path/status/latency_ms`，且该行的 `request_id` 与第一步响应头里的 id **相同**。

### 4. 合法 request_id 透传；非法值被替换

合法值透传：

```bash
cd ~/lab/workpilot && curl -si -H 'X-Request-ID: my-trace-0001' localhost:8080/health | grep -i 'x-request-id'
```

**期望**：`X-Request-Id: my-trace-0001`（原样透传）。

非法值（含空格 + 引号）被替换为 32 位新 id：

```bash
cd ~/lab/workpilot && curl -si -H 'X-Request-ID: bad id"<>' localhost:8080/health | grep -i 'x-request-id'
```

**期望**：`X-Request-Id: <32 位新 id>`（**不是** `bad id"<>`，长度 32 的十六进制）。

### 5. 停掉 Qdrant 后 `/ready` 返回 503，恢复后 200

触发 503（停 qdrant → 请求 /ready）：

```bash
cd ~/lab/workpilot && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml stop qdrant && sleep 2 && curl -s -w '\nHTTP %{http_code}\n' localhost:8080/ready
```

**期望**：响应体 `{"status":"not_ready","checks":{"qdrant":"fail: ...","db":"ok","llm_key":"ok"}}`，末行 `HTTP 503`（`checks.qdrant` 为 `fail`，其余 `ok`）。

恢复 200（启动 qdrant → 请求 /ready）：

```bash
cd ~/lab/workpilot && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml start qdrant && sleep 3 && curl -s -w '\nHTTP %{http_code}\n' localhost:8080/ready
```

**期望**：响应体 `{"status":"ready","checks":{"qdrant":"ok","db":"ok","llm_key":"ok"}}`，末行 `HTTP 200`。

### 6. 404 / 422 / 500 响应体均为统一格式，500 不含 Traceback 和密钥

404（路由不存在）：

```bash
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/v1/route-does-not-exist
```

**期望**：`{"error":{"code":"not_found","message":"Not Found","request_id":"..."}}` + `HTTP 404`。

422（`/v1/conversations` 传错误类型 body）：

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:8080/v1/conversations -H 'Content-Type: application/json' -d '{"title": 123}'
```

**期望**：`{"error":{"code":"validation_error","message":"invalid request fields: body.title","request_id":"..."}}` + `HTTP 422`（只回显字段路径，不回显输入值）。

500（停 qdrant 后调用 `/v1/kb/search`，末尾自动恢复 qdrant）：

```bash
cd ~/lab/workpilot && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml stop qdrant && sleep 2 && curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:8080/v1/kb/search -H 'Content-Type: application/json' -d '{"query": "test"}' && docker compose -p workpilot --env-file .env -f deploy/docker-compose.yml start qdrant
```

**期望**：`{"error":{"code":"internal_error","message":"internal server error","request_id":"..."}}` + `HTTP 500`。`message` 固定为 `internal server error`，**不含 Traceback / 堆栈 / 密钥**（堆栈只进 api 容器日志，用 `request_id` 关联）。

### 7. 测试通过 + 已提交

```bash
cd ~/lab/workpilot/apps/api && uv run pytest -q
```

**期望**：`53 passed`（含新增 `tests/test_observability.py` 3 例，`test_request_id_roundtrip` / `test_invalid_request_id_replaced` / `test_404_unified_error`）。

提交状态：workpilot 仓库已 commit + push（`d48f685`，上一轮完成）；本次按要求**未再提交**，`a_future` 仓库的 PLAN.md / SUMMARY.md 更新保持未提交。

## 五、概念自检（PLAN §7 答案摘要）

1. **healthcheck 用 `/health` 不用 `/ready`**：Qdrant 短暂抖动时 `/ready` 失败会让 api 被标记 unhealthy 甚至被反复重启，扩大故障；liveness（进程活着）与 readiness（能接流量）必须分开。
2. **为何校验传入 `X-Request-ID`**：头部可被客户端控制，含换行 / 引号会伪造日志行或破坏 JSON 解析，属日志注入。
3. **为何 500 只回 `internal server error`**：堆栈会暴露路径、依赖版本、甚至密钥片段；详细信息只写日志，用 request_id 关联。
4. **contextvar 为何在 `finally` 里 reset**：恢复到进入前的值，避免同一 asyncio 任务后续逻辑读到上一个请求的 id。
5. **`SecretStr` 防什么**：防止密钥在日志、异常信息、`repr(settings)` 中被意外打印；取值必须显式 `get_secret_value()`。

## 六、对 DA-01 的贡献（PLAN §8）

F8 运维能力与 M9 可观测性起步：WorkPilot 从「出问题只能本地复现」变成「凭 request_id 可在线定位」。W15 的 trace / span 表、成本账本会直接复用 `request_id_var` 作为 trace_id。
