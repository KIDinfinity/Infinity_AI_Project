上下文检索，减少幻觉

- [✅] `/v1/kb/search` 返回 top-k，按 `score` 降序，含 `source/section/score`
- [✅] 库内问题：`/v1/kb/ask` 答案含 `[n]`，`citations` 非空且每个 `n` 对应 `retrieved[n-1]`
- [✅] 库外问题：`refused=true`，答案以「知识库中没有找到」开头
- [✅] 易混淆问题：结果已记录（对/错都可以，错的明天进 badcase）
- [✅] `uv run pytest tests/test_answer.py -q` 通过（引用解析、越界编号过滤、拒答判断、空检索直接拒答不调 LLM）
- [✅] （P1）`curl -N` 调 `/v1/kb/ask/stream`：先 `event: retrieved`，再 `event: token`，最后 `event: done`（含 citations）
- [✅] （P1）`GET /v1/kb/docs` 返回文档列表与分块数
- [✅] 已 push