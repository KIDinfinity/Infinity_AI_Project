# Day 12 · 2026-10-13 · Task 2 执行记录与验收手册

> 本文档与 `PLAN.md` 同级。实际执行日期 2026-10-11（提前拆解 Day12）。
> 结论：**Task 2 全部完成，验收全绿。**（未 commit / 未 push，按要求跳过提交。）

---

## 一、做了什么（改动清单）

### 代码（`~/lab/workpilot`）

| 文件 | 变更 |
| --- | --- |
| `apps/api/app/core/config.py` | `Settings` 新增价格 4 键 + `llm_log_path` |
| `apps/api/app/llm/schemas.py` | `ChatResult` 新增 `request_id` / `cost` / `ttft_ms` / `usage_estimated` |
| `apps/api/app/llm/pricing.py` | 新增：`calc_cost()` + `estimate_tokens()` |
| `apps/api/app/llm/usage_log.py` | 新增：`log_call()`，追加写 `data/logs/llm_calls.jsonl` |
| `apps/api/app/llm/gateway.py` | `chat()` 补 `request_id`/`cost`/日志；新增 `stream()` |
| `apps/api/app/routes/chat.py` | 新增 `POST /v1/chat/stream`（SSE） |
| `scripts/chat.py` | 新增：CLI 多轮聊天（`/cost` `/reset` `/exit`） |
| `tests/test_pricing.py` | 新增：成本计算单测 |
| `tests/test_sse.py` | 新增：SSE 路由单测 |

### 配置

- `.env.example`：追加 4 个价格键（只键 + 注释，无猜测数字）。
- `.env`（本地，已 gitignore）：填入真实价格（见下方「第 11 节产出」）。

### 未做（按要求）

- 未 `git commit` / 未 `git push`（用户明确要求不提交）。
- 未改前端 / 未引入 WebSocket / 未做预算守卫（均不在今日范围）。

---

## 二、验收对齐（第 3 节勾选结果）

- [x] `curl -N` 调 `POST /v1/chat/stream`：多条 `event: token` + 最后 1 条 `event: done`
- [x] `done` 含 `usage.total_tokens > 0`、`cost`、`latency_ms`、`ttft_ms`、`request_id`
- [x] 调一次接口后 `data/logs/llm_calls.jsonl` 行数 +1
- [x] `scripts/chat.py`：3 轮对话 → `/cost` 累计 → `/reset` 失忆 → `/exit`
- [x] `test_pricing.py`、`test_sse.py` 通过；`.env.example` 有价格键
- [ ] 已 push（跳过，未提交）

---

## 三、详细验收操作（可直接复制到终端执行）

### 前提：启动服务

```bash
cd ~/lab/workpilot/apps/api
uv run uvicorn app.main:app --reload --port 8000
```

> 另开一个终端做下面的验收。若 8000 已被占用，先停掉旧进程。

### 验收 1：SSE 流式输出（能看到「逐字」输出 + done）

```bash
curl -sN --noproxy '*' -X POST localhost:8000/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用一句话解释什么是 SSE"}]}'
```

预期：屏幕上出现多条 `event: token`（逐 token 输出），最后一条 `event: done`，其 `data` 里包含：

```text
"usage": {"prompt_tokens": ..., "completion_tokens": ..., "total_tokens": ..., "cache_hit_tokens": ...}
"cost": 一个非空数字
"latency_ms": 数字
"ttft_ms": 数字
"request_id": "12位hex"
"usage_estimated": false
```

### 验收 2：调用日志 +1（每次调用多一行）

```bash
cd ~/lab/workpilot
wc -l data/logs/llm_calls.jsonl
curl -sN --noproxy '*' -X POST localhost:8000/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"hi"}]}' > /dev/null
wc -l data/logs/llm_calls.jsonl
```

预期：第二次 `wc -l` 比第一次大 1；`tail -n 1` 能看到带 `request_id`、`cost`、`ttft_ms` 的 JSON 行。

```bash
tail -n 1 data/logs/llm_calls.jsonl
```

### 验收 3：非流式 `/v1/chat` 也带成本与 request_id

```bash
curl -s --noproxy '*' -X POST localhost:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"只回两个字：收到"}]}' | python3 -m json.tool
```

预期：返回 JSON 含 `request_id`、`cost`、`usage`；`ttft_ms` 为 `null`（非流式无首 token 延迟）。

### 验收 4：CLI 多轮聊天

```bash
cd ~/lab/workpilot
uv run --project apps/api python scripts/chat.py
```

交互式执行以下输入，逐条回车：

1. `我叫小王` —— 模型正常回复
2. `我刚才说我叫什么？` —— 应能答出「小王」
3. `/reset` —— 提示 `[history 已清空]`
4. `我刚才说我叫什么？` —— 应表示不知道（上文已清空）
5. `/cost` —— 显示「N 次调用，累计成本 X.XXXXXX」
6. `/exit` —— 退出

> 也可以一条命令非交互演示（效果同上）：

```bash
cd ~/lab/workpilot && printf '我叫小王\n我刚才说我叫什么？\n/reset\n我刚才说我叫什么？\n/cost\n/exit\n' | uv run --project apps/api python scripts/chat.py
```

### 验收 5：单测全绿

```bash
cd ~/lab/workpilot/apps/api
uv run pytest -m "not llm" -q
uv run ruff check app/ tests/
```

预期：`27 passed`；ruff `All checks passed!`。

---

## 四、第 11 节产出记录（填写）

- DeepSeek 是否支持 include_usage：**支持**（`stream_options: {"include_usage": true}` 生效）
- cache 字段名：**`prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`**
- 定价抄写日期：**2026-10-11**，来源 https://api-docs.deepseek.com/zh-cn/quick_start/pricing/
  - `deepseek-chat` 实为 `deepseek-flash`（DeepSeek-V4.1-Flash）别名，空闲时段价：
    - 缓存命中输入 0.02 元 / 百万 tokens
    - 缓存未命中输入 1 元 / 百万 tokens
    - 输出 4 元 / 百万 tokens
  - 注意：价格页已区分「空闲 / 高峰」两档，`.env` 当前按空闲时段抄录（成本为近似值，未做时段区分）。
- 一次流式调用 ttft / 总延迟 / tokens / 成本：**459ms / 553ms / 21 tokens / ¥0.000057**
- CLI 3 轮对话累计成本：**¥0.000455**
- 卡点记录：
  1. PLAN 示例 `from app.core.config import settings` 与现有代码不一致——本仓库 config 无模块级 `settings`，只有 `get_settings()`；已改为 `get_settings()`（`pricing.py` / `usage_log.py` 及测试同步调整）。
  2. 测试中 `calc_cost` 边界断言笔误（cache_hit 超 prompt 时成本应为 0.00015 而非 0.0001），已修正。
  3. ruff UP035：`AsyncIterator` 应从 `collections.abc` 导入，已改。
- 用时：约 60 分钟（含文档与验证）

---

## 五、完成判定

第 3 节除「已 push」外全部勾上 → **Task 2 DONE**。
下一步 Day13：DA-01 决策（主场景包 M10 选型）。提交由用户后续自行处理。
