# Week 04 · RAG Pipeline MVP（Phase 1 · Day15–Day18 · 10-12 → 10-15）

## 1. 本周核心目标

手写（不用 LangChain / LlamaIndex）一条完整的 RAG 链路：**语料 → 加载 → 分块 → bge-m3 向量化 → Qdrant 入库 → 检索 → 带引用回答 / 拒答 → KB API**，并用 20 题种子集 + 首批 Badcase 交付 **WorkPilot v0.2**。

## 2. 资产锚点

| 项                            | 内容                                                                                                                                                                                                                                                                                                             |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 构建模块                      | M2.1 Ingest、M2.2 Chunking、M2.3 Embedding + 索引、M2.4 Retrieval（dense）、M2.5 Grounded Answer、M2.6 KB API、M3.1 数据集规范、M3.4 Badcase 库                                                                                                                                                                  |
| 版本里程碑                    | **v0.2**（tag `v0.2.0`，Day18）                                                                                                                                                                                                                                                                                  |
| 本周结束 WorkPilot 能演示什么 | ① `scripts/ingest.sh` 一键把 ≥30 篇文档入库，Qdrant Dashboard 可见点数；② `POST /v1/kb/ask` 对库内问题给出带 `[n]` 引用的答案、对库外问题回答「知识库中没有找到…」；③ `/v1/kb/ask/stream` 先推送检索结果再流式输出；④ 20 题种子报告 + ≥5 条带根因分类的 Badcase；⑤ 与 v0.1 对比：私有知识题从幻觉变为有引用/拒答 |

## 3. 为什么这一周存在

- RAG 是 P1 的核心、AI 应用岗 JD 出现频率最高的能力；Agent 阶段的 `kb_search` 工具（W9）直接复用本周的检索函数。
- v0.1 的 Badcase 已证明「团队私有知识」会被模型编造，本周要用知识库 + 引用 + 拒答把它修掉，并留下可对比的数据。
- 手写链路的目的：面试时能讲清每一步的取舍（分块大小、overlap、阈值、引用解析），而不是「调了框架」。

## 4. 本周在路线中的位置

```text
W3 产出：Gateway（结构化/流式/成本/Prompt 版本）+ da01-definition（主场景 + 语料计划）
        + v0.1 无检索基线 + 幻觉 Badcase
   ↓
W4（本周）：Day15 语料 ≥30 篇 + loaders → Day16 分块/向量/入库（幂等）
        → Day17 检索 + 引用回答 + KB API → Day18 20 题种子集 + Badcase → tag v0.2.0
   ↓
W5 输入：kb_qa.jsonl（20 题 schema）、run_kb_smoke.py、Qdrant collection kb_default、
        可配置 chunk_size/overlap/top_k、badcases.md（含根因分类）
```

## 5. 每日安排

| Day   | 日期  | Task                                       | 当日 P0 产出                                                                                                                                 | 模块             | 状态 |
| ----- | ----- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---- |
| Day15 | 10-12 | Task 1：语料准备 + Ingest                  | `data/corpus/` ≥30 篇 + `SOURCES.md` + 合规检查；`app/rag/models.py`、`loaders/{markdown,pdf,html}.py`；`ingest --dry-run` 统计；loader 单测 | M2.1             | TODO |
| Day16 | 10-13 | Task 2：Chunking + Embedding + Qdrant 入库 | `chunking.py`、`embedding.py`、`store.py`、`ingest` 正式入库（幂等）、`scripts/ingest.sh`                                                    | M2.2 M2.3        | TODO |
| Day17 | 10-14 | Task 3：检索 + 带引用回答 + KB API         | `retrieve.py`、`answer.py`、`prompts/qa_answer.v1.md`、`/v1/kb/ask`、`/v1/kb/search`（P1：`/ask/stream`、`/docs`）                           | M2.4 M2.5 M2.6   | TODO |
| Day18 | 10-15 | Task 4：20 题种子集 + 首批 Badcase         | `eval/datasets/kb_qa.jsonl`(20)、`scripts/run_kb_smoke.py`、`eval/reports/20261015-rag-v0.2.md`、badcases ≥5、tag `v0.2.0`                   | M3.1 M3.4 / v0.2 | TODO |

## 6. 本周必须留下的资产（文件路径级）

```text
data/corpus/{notes,oss,team,pdf,html}/...   # gitignore
data/corpus/SOURCES.md                      # 来源/许可/commit（gitignore 目录内，另复制一份到 docs/product/corpus-sources.md）
data/sample/                                # ≤5 篇公开样例，可提交
apps/api/app/rag/models.py                  # Document / Chunk
apps/api/app/rag/loaders/{__init__,markdown,pdf,html}.py
apps/api/app/rag/chunking.py
apps/api/app/rag/embedding.py
apps/api/app/rag/store.py
apps/api/app/rag/ingest.py                  # CLI：--dry-run / --collection / --chunk-size / --overlap
apps/api/app/rag/retrieve.py
apps/api/app/rag/answer.py
apps/api/app/routes/kb.py
apps/api/tests/test_loaders.py  test_chunking.py  test_answer.py
prompts/qa_answer.v1.md
scripts/ingest.sh  scripts/run_kb_smoke.py
data/index_manifest/kb_default.json         # 入库配置快照（gitignore）
eval/datasets/kb_qa.jsonl
eval/reports/20261015-rag-v0.2.md
eval/badcases/badcases.md                   # 完整模板 + ≥5 条
README.md（v0.2 章节）  git tag v0.2.0
```

## 7. 本周验收标准（PASS/FAIL 勾选）

- [ ] 语料 ≥ 30 篇，合规检查清单全部勾选，`git status` 中看不到 `data/corpus`
- [ ] `ingest --dry-run` 输出文档数 / 字符数 / 类型分布；`pytest -m "not llm"` 全绿
- [ ] `curl localhost:6333/collections/kb_default` 的 `points_count` > 0；连续运行两次 `scripts/ingest.sh` 点数不变（幂等）
- [ ] `/v1/kb/ask` 库内问题答案含 `[n]` 且 `citations` 非空；库外问题返回「知识库中没有找到…」
- [ ] `/v1/kb/search` 返回带 `score/source/section` 的 top-k
- [ ] `kb_qa.jsonl` 20 题（12 库内 / 5 库外 / 3 易混淆），报告存在
- [ ] `badcases.md` ≥ 5 条，每条有根因分类
- [ ] `v0.2.0` tag 已 push；README 有 v0.2 章节

## 8. 求职映射

- 本周能力：RAG 全链路（Ingest / Chunking / Embedding / Vector DB / Retrieval / Grounded Generation / Citation）、Qdrant、FastAPI SSE。
- 简历 bullet 草稿：
  - 「不依赖框架手写 RAG 链路：Markdown/PDF/HTML 解析 → 标题感知分块 → bge-m3 本地向量化 → Qdrant 检索 → 带段落级引用的生成与拒答；导入 ** 篇文档 / ** 个分块，入库幂等。」
  - 「相对无检索基线，私有知识问题的幻觉从 **/** 降至 **/**，库外问题拒答 \_\_/5。」
- 面试题：
  1. 你的分块策略是什么？为什么按标题切？overlap 的作用？
  2. 怎么让模型「只依据上下文」并给出引用？引用编号怎么映射回原文？
  3. 怎么保证重复导入不产生重复数据？

## 9. 本周禁止事项

- 不引入 LangChain / LlamaIndex / Haystack；不换向量库；不试第二个 embedding 模型。
- 不做 hybrid / rerank / query rewrite（W5 Day20 的实验内容）。
- 不做上传接口和前端（W6）；入库走 CLI。
- 不放任何公司原文进 `data/corpus/`；不提交 `data/corpus/`。
- 不为「完整」去写异步任务队列、数据库文档表（W19）。

## 10. 时间不够时（最小保留）

1. Day15：Markdown loader + ≥30 篇 md（PDF/HTML loader 与 MinIO 可延期）。
2. Day16：chunking + embedding + upsert + 幂等（`ingest.sh`、manifest 可延期）。
3. Day17：`search()` + `/v1/kb/ask`（非流式）+ 拒答（stream / docs 接口可延期到 W6 Day23 前）。
4. Day18：20 题 + 报告 + 5 条 badcase + tag（README 简写）。

## 11. 周复盘（周末填写）

- 完成：\_\_\_\_
- 未完成及原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_
- 文档数 / 分块数 / 平均分块长度：\_**\_ / \_\_** / \_\_\_\_
- 20 题：来源命中 **/15、库外拒答 **/5、人工判对 \_\_/20
- v0.1 → v0.2 私有知识题对比：\_\_\_\_
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
