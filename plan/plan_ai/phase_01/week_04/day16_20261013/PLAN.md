# Day 16 · 2026-10-13 · Week 04 Task 2：Chunking + Embedding + Qdrant 入库

## 0. 今天只做一件事

把 Day15 的 `Document` 切成带标题路径的分块，用本地 bge-m3 向量化，幂等写入 Qdrant `kb_default`，一条命令（`scripts/ingest.sh`）可重复执行。

不碰：检索接口与回答（Day17）、hybrid / 稀疏向量（W5 Day20）、异步任务队列。

## 1. 资产锚点

- 构建模块：M2.2 Chunking、M2.3 Embedding + 索引（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.2 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：Qdrant Dashboard 中 `kb_default` 有 N 个点（payload 含 section/source/text）；`scripts/ingest.sh` 跑两次点数不变；`data/index_manifest/kb_default.json` 记录本次入库配置
- 今日 AI 实际应用：Embedding + 向量库 → 知识库的「可检索记忆」；分块参数做成可配置，W5 实验直接换参数重建

## 2. 起点（前置确认）

- 已有：Day15 `Document` / `load_dir()` / `ingest --dry-run`；Qdrant(6333)；Ollama bge-m3。
- 需确认：

```bash
curl -s localhost:6333/collections | python -m json.tool          # Qdrant 在线
curl -s localhost:11434/v1/embeddings -H 'Content-Type: application/json' \
  -d '{"model":"bge-m3","input":["你好"]}' | python -c "import sys,json;print(len(json.load(sys.stdin)['data'][0]['embedding']))"
# 期望输出 1024
cd ~/lab/workpilot/apps/api && uv run python -m app.rag.ingest --path ../../data/corpus --dry-run
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `uv run pytest tests/test_chunking.py -q` 通过（标题路径、代码块内 `#` 不当标题、长段落硬切、overlap 存在）
- [ ] `scripts/ingest.sh` 输出 `docs=… chunks=… points=…`，且 `points == chunks`
- [ ] `curl -s localhost:6333/collections/kb_default` 的 `result.points_count` > 0
- [ ] 再跑一次 `scripts/ingest.sh`，`points_count` 不变（幂等）
- [ ] http://localhost:6333/dashboard 中随机打开一个点，payload 含 `doc_id/title/source/section/text/workspace/order`
- [ ] （P1）`data/index_manifest/kb_default.json` 存在
- [ ] 已 push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                 |
| ------- | ------ | ------------------------------------ |
| 0–10    | P0     | 前置确认 + 配置项                    |
| 10–45   | P0     | `chunking.py` + 单测                 |
| 45–60   | P0     | `embedding.py` + 维度冒烟            |
| 60–80   | P0     | `store.py`                           |
| 80–100  | P0     | 管道接入 ingest，正式入库 + 幂等验证 |
| 100–110 | P1     | `scripts/ingest.sh` + manifest       |
| 110–120 | P0     | Dashboard 检查 + 提交                |

时间不足时最低保留：chunking + embedding + upsert + 幂等验证（ingest.sh / manifest 顺延）。

## 5. 今日学习（只学完成任务必须的）

- 分块是「召回粒度」与「上下文完整性」的折中：太小丢上下文，太大稀释相似度并浪费 token；先用 600 / 100，W5 用数据决定。
- 按标题切 + 记录标题路径（`section = "教程 > 查询参数 > 可选参数"`）：引用可读，向量文本前拼「标题 / 章节」能显著改善短块的语义。
- Qdrant 点 ID 只能是无符号整数或 UUID；`uuid5(namespace, f"{doc_id}:{order}")` 让同一块每次得到同一 ID → upsert 覆盖而不是新增。
- 幂等的另一半：文档内容更新后 `doc_id` 变了，旧块不会被覆盖，所以入库前按 `source` 删除旧点。
- 资料：https://qdrant.tech/documentation/concepts/collections/ 、https://qdrant.tech/documentation/concepts/points/ 、https://qdrant.tech/documentation/concepts/indexing/#payload-index 、https://ollama.com/blog/openai-compatibility 、https://ollama.com/library/bge-m3

## 6. 执行步骤

### Step 1 · 配置

```bash
cd ~/lab/workpilot/apps/api && uv add qdrant-client
```

`Settings` 增加（`.env.example` 同步加键）：

```python
qdrant_url: str = "http://localhost:6333"
embed_base_url: str = "http://localhost:11434/v1"
embed_model: str = "bge-m3"
embed_dim: int = 1024
embed_batch: int = 32
chunk_size: int = 600
chunk_overlap: int = 100
workspace: str = "default"
```

### Step 2 · chunking.py（核心逻辑必须自己理解）

````python
import re, uuid
from pydantic import BaseModel
from app.rag.models import Document

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")

class Chunk(BaseModel):
    id: str
    doc_id: str
    text: str
    section: str
    order: int
    metadata: dict

def split_sections(text: str) -> list[tuple[str, str]]:
    stack: list[tuple[int, str]] = []
    out, buf, in_code = [], [], False
    def flush():
        body = "\n".join(buf).strip()
        if body:
            out.append((" > ".join(t for _, t in stack), body))
        buf.clear()
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        m = None if in_code else _HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, m.group(2)))
        else:
            buf.append(line)
    flush()
    return out

def split_body(body: str, size: int, overlap: int) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    step = max(size - overlap, 1)
    pieces: list[str] = []
    for p in paras:                                   # 超长段落先按 size 硬切（带 overlap）
        pieces += [p[i:i + size] for i in range(0, len(p), step)] if len(p) > size else [p]
    chunks, cur = [], ""
    for p in pieces:
        if cur and len(cur) + len(p) + 2 > size:
            chunks.append(cur)
            cur = (cur[-overlap:] + "\n\n" + p) if overlap else p   # 带上前一块尾部作为 overlap
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks

def chunk_document(doc: Document, size: int = 600, overlap: int = 100) -> list[Chunk]:
    out: list[Chunk] = []
    for section, body in split_sections(doc.text):
        for piece in split_body(body, size, overlap):
            order = len(out)
            out.append(Chunk(id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc.id}:{order}")),
                             doc_id=doc.id, text=piece, section=section or doc.title, order=order,
                             metadata={"source": doc.source, "title": doc.title,
                                       "workspace": doc.metadata.workspace}))
    return out
````

> 必须自己读懂的三处：标题栈的弹出条件（`>= level`）、代码块开关 `in_code`、overlap 取前一块尾部。块的最大长度约为 `size + overlap`，这是有意的（测试断言按 `≤ size + overlap + 2` 写）。

`tests/test_chunking.py`（AI 生成样板，断言自己定）：

- `# A\n## B\n内容` → section == `"A > B"`；
- 代码块中的 `# comment` 不产生新 section；
- 2000 字单段 + size=600 → 至少 3 块，每块 ≤ 702（size + overlap + 分隔符 2 字符）；
- 相邻两块存在 overlap（后一块开头 50 字出现在前一块结尾）；
- 同一文档两次 `chunk_document` 的 id 列表完全相同。

### Step 3 · embedding.py

```python
from openai import AsyncOpenAI
from app.core.config import settings

class Embedder:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(base_url=settings.embed_base_url, api_key="ollama")  # Ollama 忽略 key，但 SDK 必填
        self.model, self.batch, self.dim = settings.embed_model, settings.embed_batch, settings.embed_dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch):
            resp = await self.client.embeddings.create(model=self.model, input=texts[i:i + self.batch])
            out.extend(d.embedding for d in resp.data)
        if any(len(v) != self.dim for v in out):
            raise ValueError(f"embedding 维度不是 {self.dim}，检查模型是否为 bge-m3")
        return out

embedder = Embedder()
```

### Step 4 · store.py

```python
from qdrant_client import AsyncQdrantClient, models
from app.core.config import settings
from app.rag.chunking import Chunk
from app.rag.models import Document

class QdrantStore:
    def __init__(self, url: str = settings.qdrant_url) -> None:
        self.client = AsyncQdrantClient(url=url)

    async def ensure_collection(self, name: str, size: int = 1024) -> None:
        if await self.client.collection_exists(name):
            return
        await self.client.create_collection(
            name, vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE))
        for key in ("doc_id", "source", "workspace"):
            await self.client.create_payload_index(name, field_name=key,
                                                   field_schema=models.PayloadSchemaType.KEYWORD)

    async def upsert(self, name: str, doc: Document, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        points = [models.PointStruct(id=c.id, vector=v, payload={
            "doc_id": c.doc_id, "title": doc.title, "source": doc.source, "section": c.section,
            "text": c.text, "order": c.order, "workspace": doc.metadata.workspace})
            for c, v in zip(chunks, vectors, strict=True)]
        await self.client.upsert(name, points=points, wait=True)

    async def _delete(self, name: str, key: str, value: str) -> None:
        flt = models.Filter(must=[models.FieldCondition(key=key, match=models.MatchValue(value=value))])
        await self.client.delete(name, points_selector=models.FilterSelector(filter=flt), wait=True)

    async def delete_by_doc(self, name: str, doc_id: str) -> None:
        await self._delete(name, "doc_id", doc_id)

    async def delete_by_source(self, name: str, source: str) -> None:
        await self._delete(name, "source", source)

    async def count(self, name: str) -> int:
        return (await self.client.count(name, exact=True)).count

store = QdrantStore()
```

### Step 5 · 管道接入 ingest.py

`parse_args()` 增加 `--collection`（默认 `kb_{workspace}`）、`--chunk-size`、`--overlap`（默认取 settings）。`main()` 中 dry-run 之后：

```python
    name = a.collection or f"kb_{a.workspace}"
    await store.ensure_collection(name, settings.embed_dim)
    total = 0
    for i, doc in enumerate(docs, 1):
        chunks = chunk_document(doc, a.chunk_size, a.overlap)
        if not chunks:
            continue
        vecs = await embedder.embed([f"{doc.title} / {c.section}\n{c.text}" for c in chunks])  # 向量文本拼标题
        await store.delete_by_source(name, doc.source)     # 先算完向量再删旧点：失败时不丢旧数据
        await store.upsert(name, doc, chunks, vecs)
        total += len(chunks)
        print(f"[{i}/{len(docs)}] {doc.source} → {len(chunks)} chunks")
    print(f"docs={len(docs)} chunks={total} points={await store.count(name)} collection={name}")
```

（P1）结尾写 manifest：`data/index_manifest/{name}.json` = `{"collection", "chunk_size", "overlap", "embed_model", "docs", "chunks", "created_at", "corpus_path"}`——W5 评测报告的配置快照从这里读。

### Step 6 · 入库 + 幂等验证

`scripts/ingest.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../apps/api"
uv run python -m app.rag.ingest --path ../../data/corpus "$@"
```

```bash
cd ~/lab/workpilot && chmod +x scripts/ingest.sh
time scripts/ingest.sh
curl -s localhost:6333/collections/kb_default | python -c "import sys,json;print(json.load(sys.stdin)['result']['points_count'])"
scripts/ingest.sh | tail -1        # 第二次：points 应与第一次相同
```

打开 http://localhost:6333/dashboard → Collections → `kb_default` → 随机看 3 个点的 payload，检查 section 是否合理、text 是否被切断在奇怪的位置（记到第 11 节，Day18 可能成为「分块切断」类 badcase）。

### Step 7 · 提交

```bash
git add apps/api scripts/ingest.sh .env.example
git commit -m "feat(rag): heading-aware chunking, bge-m3 embedding and idempotent qdrant ingest"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么向量化时拼 `title / section`，而 payload 里的 `text` 不拼？（答：拼接增强短块语义利于召回；payload 保持原文用于展示与引用。）
2. 为什么 chunk id 用 uuid5 而不是 uuid4？（答：uuid5 确定性，同输入同 id，重复入库覆盖不新增。）
3. 文档内容更新后，怎么保证旧块被清掉？（答：doc_id 会变，所以按 `source` 删除旧点后再写入。）
4. COSINE 距离下需要自己归一化向量吗？（答：不需要，Qdrant 对 Cosine 集合会自动归一化。）
5. 为什么要给 `doc_id/source/workspace` 建 payload 索引？（答：删除与过滤按这些字段进行，索引让过滤高效，W19 多空间隔离也依赖它。）

## 8. 对 DA-01 的贡献

WorkPilot 拥有了可检索的知识库索引，且入库可重复、参数可配置。W5 的分块实验只需换参数换 collection，W6 的上传功能只需调用同一个管道。

## 9. 求职映射（D 线）

- 岗位能力：Chunking 策略、Embedding、向量数据库（Qdrant collection / payload / index）、幂等数据管道。
- 对应岗位：RAG Engineer、AI Engineer、AI Platform Engineer。
- 简历 bullet 草稿：「实现标题感知分块（保留章节路径、段落边界、可配置 size/overlap）+ bge-m3 本地向量化（零 API 成本）+ Qdrant 幂等入库（uuid5 确定性 ID + 按来源替换），** 篇文档生成 ** 个分块，全量重建耗时 \_\_ 秒。」
- 面试可能问：
  1. 「chunk size 你怎么选的？」——要点：先经验值 600/100 建基线，再用评测集对比 300/600/1000 × overlap（W5 有数据）。
  2. 「增量更新怎么做？」——要点：内容哈希判断变化 + 按 source 删除旧块 + 确定性 ID；更大规模时加文档表记录版本。

## 10. 卡住时的处理

| 现象                                                                                 | 处理                                                                                                                  |
| ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `openai.NotFoundError: model "bge-m3" not found`                                     | `ollama pull bge-m3`；`ollama list` 确认名称（可能是 `bge-m3:latest`），与 `EMBED_MODEL` 一致                         |
| `httpx.ConnectError` 连 11434 失败                                                   | Ollama 未启动：打开 Ollama App 或 `ollama serve`                                                                      |
| `qdrant_client ... Unexpected Response: 400 ... Wrong input: Vector dimension error` | collection 维度与向量不一致：删除测试 collection 后重建（`DELETE /collections/kb_default`，只删实验集合，先确认名字） |
| `ValueError: ... is not a valid point ID`                                            | 点 ID 必须是 UUID 字符串或无符号整数，确认用的是 `str(uuid.uuid5(...))`                                               |
| `ValueError: zip() argument 2 is shorter`                                            | embedding 返回数量少于输入：检查是否有空字符串块，在 chunking 中过滤空块                                              |
| 入库很慢（>5 分钟）                                                                  | 调大 `EMBED_BATCH` 到 64；确认 Ollama 用的是 Apple Silicon GPU（Activity Monitor 看 GPU 占用）                        |

## 11. 产出记录（执行时填写）

- docs / chunks / points：\_**\_ / \_\_** / \_\_\_\_
- 平均块长 / 最大块长：\_**\_ / \_\_**
- 全量入库耗时：\_**\_ 秒；第二次后 points：\_\_**
- Dashboard 抽查发现的分块问题：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上（P1 项除外）→ Task 2 DONE → 明天进入 Day17（检索 + 带引用回答 + KB API）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（幂等入库优先）。
