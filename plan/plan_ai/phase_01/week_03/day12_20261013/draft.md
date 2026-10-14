gateway.stream 的 yield + FastAPI + SSE HTTP 一起达成流式输出（让user一点一点看到）

- [✅] `curl -N` 调 `POST /v1/chat/stream`：出现多条 `event: token`，最后 1 条 `event: done`
- [✅] `done` 数据含 `usage.total_tokens > 0`、`cost`（已配置价格时非空）、`latency_ms`、`ttft_ms`、`request_id`
- [✅] 调一次 `/v1/chat` 或 `/v1/chat/stream`，`wc -l data/logs/llm_calls.jsonl` +1
- [✅] `uv run --project apps/api python scripts/chat.py`：3 轮对话 → `/cost` 显示累计 → `/reset` 后模型不记得上文 → `/exit` 退出
- [ ] `test_pricing.py`、`test_sse.py` 通过；`.env.example` 有价格键（无真实值以外的猜测数字）
- [ ] 已 push