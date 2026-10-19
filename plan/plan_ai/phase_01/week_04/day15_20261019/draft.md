minio 文档读取存储

- [✅] `find ../../data/corpus -type f \( -name '*.md' -o -name '*.pdf' -o -name '*.html' \) | wc -l` ≥ 30
- [✅] 合规 grep 无命中；`data/corpus/SOURCES.md` 记录每类来源、仓库地址、commit、许可证
- [✅] `git status` 中看不到 `data/corpus`
- [✅] `uv run python -m app.rag.ingest --path ../../data/corpus --dry-run` 输出统计，且重复文件被计入「去重」
- [✅] `uv run pytest tests/test_loaders.py -q` 通过
- [✅] （P1）`--upload-raw` 后 MinIO Console 中可见 `default/<sha256>/<filename>` 对象
- [✅] 已 push