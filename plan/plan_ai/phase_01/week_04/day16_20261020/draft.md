文本分块，存进qdrant（有了一个知识库，kb_default）

- [✅] `uv run pytest tests/test_chunking.py -q` 通过（标题路径、代码块内 `#` 不当标题、长段落硬切、overlap 存在）
- [✅] `scripts/ingest.sh` 输出 `docs=… chunks=… points=…`，且 `points == chunks`
- [✅] `curl -s localhost:6333/collections/kb_default` 的 `result.points_count` > 0
- [✅] 再跑一次 `scripts/ingest.sh`，`points_count` 不变（幂等）
- [✅] http://localhost:6333/dashboard 中随机打开一个点，payload 含 `doc_id/title/source/section/text/workspace/order`
- [✅] （P1）`data/index_manifest/kb_default.json` 存在
- [✅] 已 push