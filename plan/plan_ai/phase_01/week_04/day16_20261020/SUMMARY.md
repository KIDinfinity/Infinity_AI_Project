# Day 16 执行总结 · 2026-10-20

> 任务：Chunking + Embedding + Qdrant 入库（Week 04 Task 2）
> 结果：**DONE**（§3 全部勾上，P1 项亦完成；按用户要求未 git commit/push）

## 1. 做了哪些事

| Step | 内容 | 产出 |
| --- | --- | --- |
| Step 1 | 安装 `qdrant-client`，`Settings` 增加 embed/qdrant/chunk 配置 | `pyproject.toml`、`uv.lock`、`app/core/config.py` |
| Step 2 | 标题感知分块 + 单测 | `app/rag/chunking.py`、`tests/test_chunking.py` |
| Step 3 | bge-m3 向量化（批处理 + 维度冒烟） | `app/rag/embedding.py` |
| Step 4 | Qdrant 存储（幂等 upsert / 按 source/doc 删除 / 计数） | `app/rag/store.py` |
| Step 5 | 管道接入 `ingest` + manifest | `app/rag/ingest.py` |
| Step 6 | 入库脚本 + 幂等验证 | `scripts/ingest.sh` |
| Step 7 | 提交 | **未执行**（用户要求不提交） |

## 2. 产出文件

- `apps/api/app/rag/chunking.py`（新增）
- `apps/api/app/rag/embedding.py`（新增）
- `apps/api/app/rag/store.py`（新增）
- `apps/api/app/rag/ingest.py`（修改：接入管道 + manifest）
- `apps/api/app/core/config.py`（新增 embed/qdrant/chunk 配置 + 模块级 `settings` 单例）
- `apps/api/tests/test_chunking.py`（新增 6 个单测）
- `scripts/ingest.sh`（新增，已 chmod +x）
- `data/index_manifest/kb_default.json`（运行时生成）

## 3. 验收对齐（§3）—— 逐条命令

### ① 单测通过（标题路径、代码块内 `#` 不当标题、长段落硬切、overlap 存在）

```bash
cd ~/lab/workpilot/apps/api && uv run pytest tests/test_chunking.py -q
```

期望输出末尾：`6 passed in ...`

### ② `scripts/ingest.sh` 输出 `docs=… chunks=… points=…`，且 `points == chunks`

```bash
cd ~/lab/workpilot && scripts/ingest.sh | tail -2
```

期望输出：

```
docs=49 chunks=1077 points=1077 collection=kb_default
manifest=/Users/infinity/lab/workpilot/data/index_manifest/kb_default.json
```

### ③ `kb_default` 的 `points_count` > 0

```bash
curl -s localhost:6333/collections/kb_default | python3 -c "import sys,json;print('points_count =',json.load(sys.stdin)['result']['points_count'])"
```

期望输出：`points_count = 1077`

### ④ 再跑一次，`points_count` 不变（幂等）

```bash
cd ~/lab/workpilot && scripts/ingest.sh | tail -1
curl -s localhost:6333/collections/kb_default | python3 -c "import sys,json;print('points_count after 2nd =',json.load(sys.stdin)['result']['points_count'])"
```

期望输出：第二次 `points_count after 2nd = 1077`（与第一次相同）

### ⑤ Dashboard 抽查点 payload 含 `doc_id/title/source/section/text/workspace/order`

浏览器打开 http://localhost:6333/dashboard → Collections → `kb_default` → 随机点开一个点检查 payload。
命令行等价替代（不依赖 Dashboard）：

```bash
curl -s -X POST localhost:6333/collections/kb_default/points/scroll \
  -H 'Content-Type: application/json' \
  -d '{"limit":1,"with_payload":true,"with_vector":false}' | python3 -m json.tool
```

期望输出：`payload` 中依次出现 `doc_id`、`title`、`source`、`section`、`text`、`order`、`workspace` 字段。

### ⑥（P1）`data/index_manifest/kb_default.json` 存在

```bash
cat ~/lab/workpilot/data/index_manifest/kb_default.json
```

期望输出：JSON 含 `collection / chunk_size / overlap / embed_model / docs / chunks / points / corpus_path / created_at`。

### ⑦ 已 push —— **未执行**（用户明确要求不提交）

```bash
cd ~/lab/workpilot && git status --short
```

期望：上述新增/修改文件仍在工作区未提交（本任务按用户要求不 commit/push）。

## 4. 产出记录（§11）

- docs / chunks / points：**49 / 1077 / 1077**
- 平均块长 / 最大块长：**415 / 702**（min 7）
- 全量入库耗时：**82.5 秒**；第二次后 points：**1077**（不变）
- Dashboard 抽查发现的分块问题：FastAPI/React/Vite 等官方文档标题带 `{#anchor}` 锚点，当前正则未剥离，section 显示为 `查询参数 { #query-parameters }`。W5 建议在标题解析处去掉 `{...}` 锚点。
- 卡点记录：无阻塞；`config.py` 原无模块级 `settings` 单例（只有 `get_settings()` DI），已补 `settings = get_settings()`。
- 用时：约 25 分钟（不含模型下载，bge-m3 已就绪）

## 5. 与 PLAN 的偏离说明

1. **配置键名对齐 `.env` 既有键**：PLAN 写的是 `embed_base_url`/`embed_model`（对应 `EMBED_BASE_URL`/`EMBED_MODEL`），但仓库 `.env`/`.env.example` 已提交的是 `EMBEDDING_BASE_URL`/`EMBEDDING_MODEL`/`EMBEDDING_API_KEY`。为避免重复加键、尊重已提交事实来源，`Settings` 字段采用 `embedding_base_url`/`embedding_model`/`embedding_api_key`，`embedding.py`/`ingest.py` 相应引用。行为一致。
2. **锚点标题未清理**：见 §4，属已知 badcase，留待 W5 分块实验处理。

## 6. 概念自检（§7，附答案）

1. 为什么向量化拼 `title / section`，payload 的 `text` 不拼？→ 拼接增强短块语义利于召回；payload 保持原文用于展示与引用。
2. chunk id 用 uuid5 而非 uuid4？→ uuid5 确定性，同输入同 id，重复入库覆盖不新增。
3. 内容更新后旧块怎么清？→ doc_id 随内容哈希变化，按 `source` 删除旧点后再写入。
4. COSINE 下需要自己归一化吗？→ 不需要，Qdrant 对 Cosine 集合自动归一化。
5. 为何给 `doc_id/source/workspace` 建 payload 索引？→ 删除与过滤按这些字段进行，索引让过滤高效，W19 多空间隔离也依赖它。
