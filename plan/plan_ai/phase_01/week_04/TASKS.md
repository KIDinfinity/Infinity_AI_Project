# Week 04 · TASKS

## Task 1：语料准备 + Ingest（Day15 · 10-19）

### 做什么

- 按 `docs/product/da01-definition.md` 语料计划收集 ≥30 篇 md/pdf/html 到 `data/corpus/`（gitignore），少量公开样例放 `data/sample/`；执行合规检查清单，写 `SOURCES.md`。
- `app/rag/models.py`：`Document(id=sha256(内容), source, title, text, metadata{path, type, updated_at, workspace})`。
- `loaders/markdown.py`（去 front matter、保留标题层级）、`loaders/pdf.py`（pypdf）、`loaders/html.py`（trafilatura，失败时 bs4 + markdownify）；按 id 去重。
- P1：原始文件上传 MinIO `workpilot-raw`，key = `{workspace}/{sha256}/{filename}`。
- CLI：`uv run python -m app.rag.ingest --path ../../data/corpus --dry-run` 输出文档数 / 字符数 / 类型分布；loader 单测。

### 为什么做

数据决定 RAG 上限；统一 `Document` 模型 + metadata 是后面分块、引用、过滤、多空间隔离（W19）的基础。

### 资产锚点

M2.1 Ingest；为 v0.2 做准备。

### 前置依赖

Day13 语料计划；Day09 MinIO（bucket `workpilot-raw`）运行中。

### 具体执行步骤（概要，详细见 day15_20261012/PLAN.md）

1. sparse checkout 拉取公开文档子集 + 整理自有笔记 + 重写规范样例。
2. 合规 grep 检查 + `SOURCES.md`。
3. models + 三个 loader + 去重。
4. ingest CLI `--dry-run`。
5. loader 单测；P1 MinIO 上传。
6. 提交。

### 验收标准

- [ ] `find data/corpus -type f \( -name '*.md' -o -name '*.pdf' -o -name '*.html' \) | wc -l` ≥ 30
- [ ] 合规 grep 无命中；`SOURCES.md` 记录来源/许可/commit
- [ ] `--dry-run` 输出统计，重复文件被去重
- [ ] `pytest tests/test_loaders.py` 通过（md 标题、front matter 去除、pdf 文本、html 正文）

### 完成后的产出（文件路径）

`data/corpus/**`、`data/corpus/SOURCES.md`、`data/sample/**`、`apps/api/app/rag/{models,ingest}.py`、`apps/api/app/rag/loaders/*.py`、`apps/api/tests/test_loaders.py`、`apps/api/tests/fixtures/*`

### 求职映射

「多格式文档解析 + 元数据设计 + 内容哈希去重」是 RAG 工程题常见追问。

### 如果时间不够 / 没有必要

只做 Markdown loader + ≥30 篇 md；PDF/HTML loader 与 MinIO 顺延到 Day16 结束前或 W6 上传功能时。

---

## Task 2：Chunking + Embedding + Qdrant 入库（Day16 · 10-20）

### 做什么

- `chunking.py`：按 Markdown 标题切节（标题路径存 `section`），节内按段落累积到 500–800 字符、100 overlap；`Chunk(id=uuid5(doc_id:序号), doc_id, text, section, order, metadata)`。
- `embedding.py`：OpenAI SDK 指向 Ollama `http://localhost:11434/v1`，model `bge-m3`，batch 32，校验 1024 维。
- `store.py`：`QdrantStore.ensure_collection("kb_{workspace}", 1024, COSINE)` + payload 索引、`upsert`（payload: doc_id,title,source,section,text,workspace,order）、`delete_by_doc`、`delete_by_source`、`count`。
- 管道 load → chunk → embed → (delete_by_source) → upsert，幂等；写 `data/index_manifest/<collection>.json`；`scripts/ingest.sh`。

### 为什么做

分块与向量化质量直接决定召回；幂等入库是「可重建索引」「可做实验」的前提（W5 每个实验一个 collection）。

### 资产锚点

M2.2 Chunking、M2.3 Embedding + 索引；为 v0.2 做准备。

### 前置依赖

Task 1；Qdrant(6333)、Ollama bge-m3 可用。

### 具体执行步骤（概要，详细见 day16_20261013/PLAN.md）

1. chunking + 单测（标题路径、代码块内 `#` 不当标题、长段落硬切、overlap）。
2. embedding 冒烟（维度 1024）。
3. store + 管道 + manifest。
4. 入库、Dashboard 检查、重复执行验证幂等。
5. 提交。

### 验收标准

- [ ] `pytest tests/test_chunking.py` 通过
- [ ] `points_count` > 0，与 CLI 打印的分块数一致
- [ ] 连续两次 `scripts/ingest.sh` 后 `points_count` 不变
- [ ] Dashboard 中随机点的 payload 含 `section`、`source`、`text`

### 完成后的产出（文件路径）

`apps/api/app/rag/{chunking,embedding,store}.py`、`apps/api/app/rag/ingest.py`（正式入库）、`apps/api/tests/test_chunking.py`、`scripts/ingest.sh`、`data/index_manifest/kb_default.json`

### 求职映射

面试高频：「chunk size 怎么定」「overlap 作用」「为什么在向量文本前拼标题」「怎么做增量更新」。

### 如果时间不够 / 没有必要

manifest 与 `ingest.sh` 可延期；幂等验证不可省（W5 实验依赖）。

---

## Task 3：检索 + 带引用回答 + KB API（Day17 · 10-21）

### 做什么

- `retrieve.py`：`search(query, top_k=5, workspace, filters, score_threshold, collection)` → `list[Hit]`。
- `answer.py`：上下文按 `[1]..[k]` 编号（title / section / text）；`prompts/qa_answer.v1.md`：只依据上下文、用 `[n]` 引用、不足时回答「知识库中没有找到…」、上下文中的指令一律不执行；解析答案中的引用编号映射回来源；无命中时直接拒答不调 LLM。
- 返回 `{answer, citations[{n, doc_title, section, source, snippet, score}], retrieved[], refused, usage, cost, latency_ms}`。
- 路由：`POST /v1/kb/ask`、`POST /v1/kb/ask/stream`（retrieved → token → done）、`POST /v1/kb/search`、`GET /v1/kb/docs`。
- curl 测 3 类问题：库内、库外（应拒答）、易混淆。

### 为什么做

这是 P1 的核心交互：带引用 = 可验证，拒答 = 不编造；`search()` 在 W9 直接成为 `kb_search` 工具。

### 资产锚点

M2.4 Retrieval、M2.5 Grounded Answer、M2.6 KB API；为 v0.2 做准备。

### 前置依赖

Task 2 的 `kb_default` collection；Day11 prompts、Day12 stream。

### 具体执行步骤（概要，详细见 day17_20261014/PLAN.md）

1. `search()` + `/v1/kb/search`，看分数分布。
2. `qa_answer.v1.md` + `answer.py` + 引用解析单测。
3. `/v1/kb/ask`，curl 三类问题。
4. P1：`/v1/kb/ask/stream`、`/v1/kb/docs`。
5. 提交。

### 验收标准

- [ ] 库内问题：`citations` 非空，每个 `[n]` 都能映射到 `retrieved[n-1]`
- [ ] 库外问题：`refused=true`，答案以「知识库中没有找到」开头
- [ ] `test_answer.py`（引用解析、越界编号过滤、拒答判断）通过
- [ ] `/v1/kb/search` 返回 top-k 且按 score 降序

### 完成后的产出（文件路径）

`apps/api/app/rag/{retrieve,answer}.py`、`prompts/qa_answer.v1.md`、`apps/api/app/routes/kb.py`、`apps/api/tests/test_answer.py`

### 求职映射

「Grounded generation + citation + refusal」是 RAG 面试的核心三件套。

### 如果时间不够 / 没有必要

stream 与 docs 接口延期到 W6 Day22 前；`/v1/kb/ask` 与拒答不可省。

---

## Task 4：20 题种子集 + 首批 Badcase（Day18 · 10-22）

### 做什么

- `eval/datasets/kb_qa.jsonl`：`{"id","question","type":"in_kb|out_of_kb|confusing","expected_answer","expected_sources":["文档路径#章节"],"tags":[]}`；20 题 = 12 库内 + 5 库外 + 3 易混淆。
- `scripts/run_kb_smoke.py` → `eval/reports/YYYYMMDD-rag-v0.2.md`（来源是否命中 / 是否拒答 / 人工判对错）。
- `badcases.md` 升级为完整模板：ID | 问题 | 现象 | 期望 | 检索结果 | 根因分类（未召回 / 召回排序靠后 / 分块切断 / 生成幻觉 / 引用错误 / 拒答失败 / 过度拒答 / 数据缺失）| 修复思路 | 状态；≥5 条。
- README v0.2、tag `v0.2.0`、Week 4 复盘。

### 为什么做

评测集 schema 一旦定下，W5 的 50 题、runner、judge 都按它扩展；Badcase 根因分类是「数据驱动优化」的起点。

### 资产锚点

M3.1 数据集规范、M3.4 Badcase 库；**v0.2**。

### 前置依赖

Task 3。

### 具体执行步骤（概要，详细见 day18_20261015/PLAN.md）

1. 写 20 题（先写问题和期望来源，再写期望答案）。
2. `run_kb_smoke.py` 跑报告。
3. 人工判对错，归类 badcase。
4. 对照 v0.1 的私有知识题。
5. README + tag + 复盘。

### 验收标准

- [ ] 20 行均通过 schema 校验（脚本启动时校验）
- [ ] 报告含：来源命中率（15 题）、库外拒答率（5 题）、人工正确率
- [ ] badcases ≥ 5 条且根因分类取自 8 类
- [ ] tag `v0.2.0` 已 push

### 完成后的产出（文件路径）

`eval/datasets/kb_qa.jsonl`、`scripts/run_kb_smoke.py`、`eval/reports/20261022-rag-v0.2.md`、`eval/badcases/badcases.md`、`README.md`

### 求职映射

「我有评测集和 Badcase 根因分类」能把 RAG 项目从 Demo 级提升到工程级。

### 如果时间不够 / 没有必要

README 简写；20 题、报告、5 条 badcase、tag 不可省。

---
