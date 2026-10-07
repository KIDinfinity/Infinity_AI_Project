跑通 minIO存储文件 + bge-m3（模型，ollama管理）将内容转成向量 + Qdrant向量存储

- [✅] `docker compose -f ~/lab/projects/infra/compose/docker-compose.yml ps` 显示 minio、qdrant 均为 running
- [✅] `http://localhost:9001` 能登录 MinIO 控制台，存在 bucket `workpilot-raw`、`backups`
- [✅] `http://localhost:6333/dashboard` 可打开
- [✅] curl Ollama `/v1/embeddings` 返回向量长度 1024
- [✅] `smoke.py` 输出 `[minio] ... sha256 一致`、`[qdrant] top-1 命中预期`、`ALL OK`
- [✅] `infra/compose/.env` 未被提交（`git -C ~/lab/projects check-ignore infra/compose/.env` 有输出）
- [✅] 能口述三类资产各存哪、数据目录在哪、哪类可重建