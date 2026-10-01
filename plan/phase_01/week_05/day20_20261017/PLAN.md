# Day 20 · 2026-10-17 · Week 05 Task 2：检索实验

## 0. 今天只做一件事

用 Day19 的 runner 跑一组受控实验（chunk size × overlap、top_k，P1 hybrid），每个分块变体入库到独立 collection，用数据选出默认检索配置并写成 ADR 0003。

不碰：LLM-judge（Day21）、换 embedding 模型/向量库、把 rerank 依赖装进主项目、为指标改评测题。

## 1. 资产锚点

- 构建模块：M2.2 Chunking（参数选型）、M2.4 Retrieval（top_k / hybrid / P2 rewrite·rerank）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.3 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`eval/reports/20261017-retrieval-experiments.md` 对比表（变体 | hit@5 | MRR | 拒答正确率 | P95 | 成本）；`docs/adr/0003-chunking-retrieval.md`；`kb_default` 按选定配置重建
- 今日 AI 实际应用：检索参数与 hybrid（稠密语义 + 稀疏关键词 + RRF 融合）的实证对比 → 决定 WorkPilot 线上检索配置，也是 P1 技术复盘的核心素材

## 2. 起点（前置确认）

- 已有：`run_rag_eval.py`（`--config/--collection/--top-k/--with-answer`）、基线报告、`ingest`（`--collection/--chunk-size/--overlap`）。
- 需确认：

```bash
cd ~/lab/workpilot
ls eval/reports/*rag-baseline*
curl -s localhost:6333/collections/kb_default | python -c "import sys,json;print(json.load(sys.stdin)['result']['points_count'])"   # 记下，实验后应不变
cd apps/api && uv run pytest -m "not llm" -q
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `eval/configs/` 下 ≥ 4 个 YAML 变体
- [ ] 每个分块变体有独立 collection `kb_exp_<variant>`；`kb_default` 点数在选定配置重建前保持不变
- [ ] 每个变体有 `eval/reports/20261017-exp-<variant>.{json,md}`
- [ ] `eval/reports/20261017-retrieval-experiments.md` 汇总表含：变体 | chunks | hit@5 | MRR | 拒答正确率 | P95 延迟 | 成本
- [ ] top_k 3/5/8 在最优分块上带生成跑过（对比拒答、误拒、成本、延迟）
- [ ] `docs/adr/0003-chunking-retrieval.md` 写明决定、数据、代价、放弃方案
- [ ] （P1）hybrid 变体有结果或在 ADR 中写明未完成原因
- [ ] 已 push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                        |
| ------- | ------ | ----------------------------------------------------------- |
| 0–15    | P0     | ingest / runner 支持 `--config`；写 YAML 变体               |
| 15–45   | P0     | `run_experiments.sh` 跑 6 个分块变体（检索指标 + 库外拒答） |
| 45–65   | P0     | 最优分块上跑 top_k 3/5/8（`--with-answer`）                 |
| 65–90   | P1     | hybrid：sparse.py + 集合 + 查询 + 跑分                      |
| 90–105  | P0     | 汇总表 + ADR 0003                                           |
| 105–115 | P0     | 按选定配置重建 `kb_default`                                 |
| 115–120 | P0     | 提交                                                        |

时间不足时最低保留：overlap=100 的 c300/c600/c1000 三个变体 + top_k 3/5/8 + 简版 ADR；hybrid 写进 ADR「待评估」。

## 5. 今日学习（只学完成任务必须的）

- 受控实验：一次只改一个变量（先固定 top_k 比分块，再固定分块比 top_k），每个变体独立 collection，避免互相污染。
- 分块大小的典型权衡：小块 → 精确但上下文碎、块数多；大块 → 上下文完整但相似度被稀释、prompt 更贵。
- Hybrid：稠密向量擅长语义近似，稀疏（BM25）擅长精确关键词（API 名、配置键、报错码）；Qdrant Query API 用 `prefetch` 分别召回，再用 RRF（按名次融合，不看原始分数）合并。
- RRF 分数与余弦分数不可比：hybrid 模式下不能直接沿用基于余弦的 `score_threshold` 做拒答。
- fastembed 的 `Qdrant/bm25` 默认按英文分词与词干处理，对中文切词效果可能较差——结果差时如实记录，中文分词（如 jieba 预分词）作为 Backlog。
- 资料：https://qdrant.tech/documentation/concepts/hybrid-queries/ 、https://qdrant.tech/documentation/concepts/vectors/#sparse-vectors 、https://qdrant.github.io/fastembed/ 、https://pyyaml.org/wiki/PyYAMLDocumentation

## 6. 执行步骤

### Step 1 · 变体配置 + `--config` 支持

`eval/configs/c600_o100.yaml`（其余同结构：`c300_o0`、`c300_o100`、`c600_o0`、`c1000_o0`、`c1000_o100`）：

```yaml
name: exp-c600_o100
collection: kb_exp_c600_o100
chunk_size: 600
chunk_overlap: 100
top_k: 5
retrieval: dense # dense | hybrid
with_answer: false # 分块对比只看检索指标 + 库外拒答，省 LLM 成本
```

`app/rag/ingest.py` 增加 `--config`：读取 YAML，覆盖 `collection / chunk_size / overlap / retrieval`；`run_rag_eval.py` 同样用 YAML 覆盖 `name / collection / top_k / retrieval / with_answer`（CLI 参数优先级最高）。样板让 AI 生成，自己确认「命令行 > YAML > settings」的覆盖顺序。

### Step 2 · 跑分块变体

`scripts/run_experiments.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../apps/api"
for cfg in "$@"; do
  echo "=== $cfg ==="
  uv run python -m app.rag.ingest --path ../../data/corpus --config "$cfg" | tail -1
  PYTHONPATH=. uv run python ../../eval/runners/run_rag_eval.py --config "$cfg"
done
```

```bash
cd ~/lab/workpilot && chmod +x scripts/run_experiments.sh
time scripts/run_experiments.sh eval/configs/c{300,600,1000}_o{0,100}.yaml
```

汇总：写 `eval/runners/summarize.py`（AI 生成样板）读取 `eval/reports/20261017-exp-*.json`，输出 Markdown 表：

```text
| 变体 | chunks | hit@1 | hit@5 | MRR | 拒答正确率 | 检索P95 | 回答P95 | 成本 |
|---|---|---|---|---|---|---|---|---|
| c300_o100 | 612 | ... |
| c600_o100 | 341 | ... |
```

（`chunks` 从 `data/index_manifest/<collection>.json` 读取。）

### Step 3 · top_k 对比（在最优分块上）

hit@k 由固定 top10 算出，**不随 top_k 变化**；top_k 影响的是生成：上下文多少 → 拒答、误拒、成本、延迟。所以 top_k 实验必须 `--with-answer`：

```bash
cd ~/lab/workpilot/apps/api
for k in 3 5 8; do
  PYTHONPATH=. uv run python ../../eval/runners/run_rag_eval.py --config ../../eval/configs/c600_o100.yaml \
    --top-k $k --with-answer --name exp-c600_o100-k$k
done
```

（把 `c600_o100` 换成 Step 2 的最优变体。）对比：库外拒答正确率、库内误拒率、平均成本、回答 P95。

### Step 4 · （P1）Hybrid

```bash
cd ~/lab/workpilot/apps/api && uv add fastembed
```

`app/rag/sparse.py`：

```python
from functools import lru_cache
from fastembed import SparseTextEmbedding
from qdrant_client import models

@lru_cache
def _bm25() -> SparseTextEmbedding:
    return SparseTextEmbedding(model_name="Qdrant/bm25")      # 首次会下载小模型文件，需要网络/代理

def _to_qdrant(e) -> models.SparseVector:
    return models.SparseVector(indices=e.indices.tolist(), values=e.values.tolist())

def sparse_docs(texts: list[str]) -> list[models.SparseVector]:
    return [_to_qdrant(e) for e in _bm25().embed(texts)]

def sparse_query(text: str) -> models.SparseVector:
    return _to_qdrant(next(iter(_bm25().query_embed(text))))
```

`store.ensure_collection(name, size, hybrid=True)` 时：

```python
await self.client.create_collection(
    name,
    vectors_config={"dense": models.VectorParams(size=size, distance=models.Distance.COSINE)},
    sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)})
```

`upsert` 在 hybrid 时 `vector={"dense": v, "bm25": sv}`；`retrieve.search` 增加 `mode` 参数：

```python
if mode == "hybrid":
    res = await store.client.query_points(
        name,
        prefetch=[models.Prefetch(query=vec, using="dense", limit=20, filter=flt),
                  models.Prefetch(query=sparse_query(query), using="bm25", limit=20, filter=flt)],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=k, with_payload=True)          # RRF 分数不可与余弦阈值比较，hybrid 下不传 score_threshold
```

`eval/configs/hybrid_c600_o100.yaml`：`retrieval: hybrid`、`collection: kb_exp_hybrid_c600_o100`，跑 `scripts/run_experiments.sh eval/configs/hybrid_c600_o100.yaml`。重点看「含 API 名/配置键」的题是否改善（按 `tags` 过滤对比）。

### Step 5 · （P2，仅在以上全部完成后）

- Query rewrite：用 `generate_structured` 把问题改写为 1–3 个检索查询，分别检索后合并去重；记录额外 1 次 LLM 调用的成本与延迟。
- Rerank：bge-reranker 需要 PyTorch / sentence-transformers，**不进主项目**；如要试，放 `~/lab/projects/ai-lab/rerank-exp/`，用同一评测集跑 hit@5/MRR，结论写进 ADR「后续选项」。

### Step 6 · ADR 0003 + 重建 kb_default

`docs/adr/0003-chunking-retrieval.md`：

```markdown
# ADR 0003：分块与检索配置（2026-10-17）

## 状态

已接受（v0.3）

## 背景

v0.2 默认 chunk 600 / overlap 100 / top_k 5 / dense。基线：hit@5 **、MRR **、拒答 \_\_（eval/reports/20261016-rag-baseline.md）。

## 选项与数据

（粘贴汇总表；注明数据集 50 题、git sha、日期）

## 决定

chunk_size=**、overlap=**、top_k=**、retrieval=**。

## 理由

- hit@5 / MRR 提升 **；拒答正确率 **；成本/延迟变化 \_\_。

## 代价与风险

- 例：小块导致块数 ×1.8、入库时间 +\_\_s；hybrid 依赖 fastembed 模型下载；中文 BM25 分词弱。

## 放弃的方案

- 例：c1000（hit@5 下降 **）；top_k=8（成本 +**%，拒答下降）；rerank（依赖过重，见 ai-lab 实验）。

## 后续

- Day21 用 judge 验证生成质量；W6 起线上默认使用此配置。
```

按决定更新 `apps/api/.env`（`CHUNK_SIZE / CHUNK_OVERLAP / TOP_K / RETRIEVAL_MODE`），然后重建 `kb_default`：

```bash
cd ~/lab/workpilot
# 若决定改为 hybrid，需要先删除旧的 dense 结构 kb_default（可随时重建）：
# curl -X DELETE localhost:6333/collections/kb_default
scripts/ingest.sh
```

### Step 7 · 提交

```bash
git add eval/configs eval/reports eval/runners scripts/run_experiments.sh docs/adr/0003-chunking-retrieval.md apps/api
git commit -m "feat(eval): retrieval experiments (chunk/overlap/top_k/hybrid) and ADR 0003"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么每个分块变体要独立 collection？（答：避免不同配置的块混在一起污染结果，也不破坏线上 `kb_default`。）
2. top_k 从 5 改到 8，hit@5 会变吗？（答：不会，hit@k 用固定 top10 计算；变的是生成侧的拒答、成本、延迟。）
3. RRF 怎么融合两个结果列表？（答：按每个文档在各列表中的名次计算 1/(k+rank) 求和，不依赖原始分数尺度。）
4. 为什么 hybrid 下不能沿用余弦阈值？（答：融合后分数是名次分，与余弦相似度尺度不同。）
5. 什么情况下 BM25 比稠密向量强？（答：精确关键词、API 名、配置键、错误码等字面匹配场景。）

## 8. 对 DA-01 的贡献

WorkPilot 的检索配置从「拍脑袋的默认值」变成「有 50 题数据支撑、写进 ADR 的决策」，`kb_default` 按最优配置重建。P1 技术复盘的「我怎么优化 RAG」有了完整的实验证据链。

## 9. 求职映射（D 线）

- 岗位能力：检索调优、Hybrid Search、实验设计、技术决策记录（ADR）。
- 对应岗位：RAG Engineer、AI Engineer、Search / Retrieval Engineer。
- 简历 bullet 草稿：「设计 ** 组受控检索实验（chunk 300/600/1000 × overlap 0/100、top_k 3/5/8、dense vs hybrid RRF），以 50 题评测集选定配置：hit@5 ** → **，MRR ** → **，单次成本变化 **%，决策记录为 ADR。」
- 面试可能问：
  1. 「Hybrid Search 你是怎么做的？效果如何？」——要点：Qdrant 稀疏 + 稠密命名向量、prefetch + RRF、关键词类问题改善、中文分词局限、用数据决定是否上线。
  2. 「chunk size 最后选了多少？为什么？」——要点：给出实验表数字与取舍（召回 vs 成本 vs 上下文完整性）。

## 10. 卡住时的处理

| 现象                                                 | 处理                                                                                                |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `fastembed` 下载模型超时                             | 设置代理 `export HTTPS_PROXY=http://127.0.0.1:7890` 后重跑；仍失败则 hybrid 记为「待评估」          |
| `Wrong input: Not existing vector name error: dense` | 在 dense 结构（无命名向量）的 collection 上用了 hybrid 查询；hybrid 必须用新建的命名向量 collection |
| `Unexpected Response: 400 ... sparse`                | 稀疏向量 `indices/values` 需为 Python list，确认用了 `.tolist()`                                    |
| 实验后 `kb_default` 点数变了                         | 某个 YAML 漏写 `collection`，回退到默认；修正后用 `scripts/ingest.sh` 重建                          |
| 各变体指标几乎一样                                   | 评测集过易或语料过小；在报告中如实写明，选成本最低的配置，并把「补难题」列入 Day21 待办             |
| 6 个变体跑太久                                       | 只跑 overlap=100 的 3 个；或调大 `EMBED_BATCH`                                                      |

## 11. 产出记录（执行时填写）

- 最优分块变体：\_**\_（hit@5 ** / MRR \_\_）
- top_k 选择：\_**\_（拒答 ** / 误拒 ** / 平均成本 ¥**）
- hybrid 结果：\_**\_（关键词类题变化：\_\_**）
- ADR 决定：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上（P1 项除外）→ Task 2 DONE → 明天进入 Day21（LLM-judge + Badcase 分类 + 定配置，tag v0.3.0）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（至少 3 个分块变体 + ADR）。
