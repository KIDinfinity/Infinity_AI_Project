# Day20 执行总结 · 2026-10-26

> 执行对象：`plan/plan_ai/phase_01/week_05/day20_20261027/PLAN.md`（W5 Task 2：检索实验）
> 实际执行日期：2026-10-26（提前一天执行，报告文件名按计划日期 stamp=`20261027`）
> 说明：按用户要求 **未提交 git**（跳过 Step 7 的 commit / push）。

## 一、做了什么（对应 PLAN 各 Step）

| Step | 内容 | 结果 |
|---|---|---|
| 1 | `ingest.py` / `run_rag_eval.py` 支持 `--config <yaml>`，覆盖顺序 CLI > YAML > settings | 完成；`resolve_config()` / runner 的 cfg 合并均按此顺序实现 |
| 1 | `eval/configs/` 写 8 个 YAML 变体（6 个 dense 分块 + 2 个 hybrid） | 完成：`c{300,600,1000}_o{0,100}.yaml` + `hybrid_c600_o100.yaml` / `hybrid_c1000_o0.yaml` |
| 2 | `scripts/run_experiments.sh` 跑 6 个分块变体（独立 collection `kb_exp_<variant>`） | 完成；每个变体产出 `20261027-exp-<variant>.{json,md}` |
| 3 | 最优分块上跑 top_k 3/5/8（`--with-answer`，对比拒答/误拒/成本/延迟） | 完成；k3/5/8 跑在 MRR 最优的 c1000_o0 上，另补 c600_o100-k5 |
| 4 | （P1）Hybrid：`app/rag/sparse.py`（fastembed BM25）+ store 命名向量 + `query_points` prefetch/RRF | 完成；hybrid 两个变体有报告，结论「不启用」 |
| 5 | （P2）Query rewrite / Rerank | 未做（P2，非 P0；rerank 记入 ADR 后续选项） |
| 6 | ADR 0003 + 按决定重建 `kb_default` | 完成；ADR 写入 `docs/adr/0003-chunking-retrieval.md`，`kb_default` 已按 600/100/dense 重建（1077 点） |
| 7 | git 提交 | **跳过（用户要求不提交）** |

改动文件清单（均在 `~/lab/workpilot`，全部未提交）：

- `apps/api/app/core/config.py`（新增 `retrieval_mode` 配置项）
- `apps/api/app/rag/ingest.py`（`--config` + YAML 覆盖 + hybrid 入库）
- `apps/api/app/rag/retrieve.py`（`search` 支持 `mode=dense|hybrid`，hybrid 走 prefetch + RRF）
- `apps/api/app/rag/store.py`（`ensure_collection(hybrid=)` 命名向量 + `upsert` 稀疏向量）
- `apps/api/app/rag/sparse.py`（新增，fastembed `Qdrant/bm25` 稀疏编码）
- `apps/api/pyproject.toml` / `uv.lock`（新增 `fastembed`、`pyyaml` 依赖）
- `eval/runners/run_rag_eval.py`（`--config/--name/--stamp/--retrieval` 覆盖顺序）
- `eval/runners/summarize.py`（新增，汇总 json 报告为 Markdown 对比表）
- `eval/configs/*.yaml`（新增 8 个）
- `eval/reports/20261027-exp-*.json|md`（新增 12 json + 12 md）+ `20261027-retrieval-experiments.md`
- `scripts/run_experiments.sh`（新增）
- `docs/adr/0003-chunking-retrieval.md`（新增）

## 二、验收命令（每条都是完整命令，直接复制到终端可看到结果）

前提：Docker Desktop 已启动（Qdrant / MinIO / Gitea 跑在 Docker 里），Ollama 本地已运行（bge-m3）。
若 Qdrant 未起来，先 `open -a Docker` 等它启动完成。

**0. 前提检查（Qdrant + Ollama 在线）**

```bash
curl -s localhost:6333/healthz
curl -s localhost:11434/api/tags | head -c 200
```

预期：`healthz check passed`；Ollama 返回的 JSON 里含 `bge-m3`。

**1. 验收「eval/configs 下 ≥ 4 个 YAML 变体」**

```bash
cd ~/lab/workpilot
ls -1 eval/configs/
```

预期：8 个文件——`c300_o0 / c300_o100 / c600_o0 / c600_o100 / c1000_o0 / c1000_o100 / hybrid_c600_o100 / hybrid_c1000_o0`（各 `.yaml`）。

**2. 验收「每个分块变体有独立 collection，kb_default 点数 = 1077」**

```bash
cd ~/lab/workpilot
curl -s localhost:6333/collections | python3 -c "import sys,json; print('\n'.join(c['name'] for c in json.load(sys.stdin)['result']['collections']))"
curl -s localhost:6333/collections/kb_default | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print('kb_default points =', d['points_count'], '| status =', d['status'])"
```

预期：列出 `kb_default` + 8 个 `kb_exp_*`（含 2 个 `kb_exp_hybrid_*`）；第二行 `kb_default points = 1077 | status = green`。

**3. 验收「每个变体有 json + md 报告」**

```bash
cd ~/lab/workpilot
ls -1 eval/reports/20261027-exp-*.json | wc -l
ls -1 eval/reports/20261027-exp-*.md  | wc -l
```

预期：两个都输出 `12`。

**4. 验收「汇总表含要求列（变体 | chunks | hit@5 | MRR | 拒答正确率 | P95 | 成本）」**

```bash
cd ~/lab/workpilot
cat eval/reports/20261027-retrieval-experiments.md
```

预期：见「① 分块变体 / ② top_k 变体 / ③ Hybrid 变体 / ④ 结论」四张表，表头含 `chunks | hit@5 | MRR | 拒答正确率 | 检索P95 | 回答P95 | 成本`。

**5. 验收「top_k 3/5/8 在最优分块上带生成跑过」**

```bash
cd ~/lab/workpilot
ls -1 eval/reports/20261027-exp-c1000_o0-k3.json eval/reports/20261027-exp-c1000_o0-k5.json eval/reports/20261027-exp-c1000_o0-k8.json
ls -1 eval/reports/20261027-exp-c600_o100-k5.json
```

预期：4 个文件都打印出来（前 3 个是 k3/5/8 扫描，最后是最终选定分块在 k5 的复核）。

**6. 验收「ADR 0003 写明决定/数据/代价/放弃方案」**

```bash
cd ~/lab/workpilot
cat docs/adr/0003-chunking-retrieval.md
```

预期：标题含「chunk 600/100 + dense + top_k=5（不启用 hybrid）」，正文含数据表、理由、代价与风险、放弃的方案、后续动作。

**7. 验收「pytest 非 LLM 用例全绿（代码改动没破坏既有功能）」**

```bash
cd ~/lab/workpilot/apps/api
uv run pytest -m "not llm" -q
```

预期：`46 passed, 2 deselected`。

**8. 验收「线上 kb_default 已按选定配置重建」**

```bash
cd ~/lab/workpilot
cat data/index_manifest/kb_default.json
```

预期：`"chunk_size": 600`、`"overlap": 100`、`"retrieval": "dense"`、`"chunks": 1077`、`"points": 1077`。

**9. 可选功能验证（走 HTTP，需先另起服务）**

先起 API（另开一个终端，保持运行）：

```bash
cd ~/lab/workpilot
make dev
```

再在新终端依次执行：

```bash
# 检索（应命中「可选参数」一节）
curl -s http://localhost:8000/v1/kb/search -H 'Content-Type: application/json' -d '{"query":"FastAPI 里怎么让一个查询参数变成可选的？","top_k":5}'
```

```bash
# 库内问答（应 refused=false 且带 citations）
curl -s http://localhost:8000/v1/kb/ask -H 'Content-Type: application/json' -d '{"question":"FastAPI 里怎么让一个查询参数变成可选的？","top_k":5}'
```

```bash
# 库外拒答（应 refused=true）
curl -s http://localhost:8000/v1/kb/ask -H 'Content-Type: application/json' -d '{"question":"今天北京的天气怎么样？","top_k":5}'
```

预期：第一条返回 top5 结果且第一名是「可选参数」小节；第二条 `"refused": false` 且 `citations` 非空；第三条 `"refused": true`（知识库外拒答）。

## 三、产出记录（对应 PLAN 第 11 节）

- 最优分块变体：**c600_o100**（hit@5 **0.921** / MRR **0.789** / 误拒 **0.132**）
- top_k 选择：**k=5**（k=3 误拒 0.211 不可接受；k=8 与 k=5 误拒持平但成本 +42%；k=5 平均成本 **¥0.0407**）
- hybrid 结果：**不启用**（hit@5 0.921→0.816、hit@1 0.737→0.605、MRR -0.085，0 题变好；fastembed `Qdrant/bm25` 英文分词对中文无效，RRF 反而稀释 dense 的强排序）
- ADR 决定：**chunk_size=600 / overlap=100 / retrieval=dense / top_k=5**
- 卡点记录：无阻塞卡点。Docker Desktop 需手动 `open -a Docker` 启动后 Qdrant 才在线；fastembed 模型已本地缓存。
- 用时：约 20 分钟（8 组实验跑批）+ ADR/汇总编写，合计约 50–60 分钟（估计）。

## 四、与蓝图目标的差距

- 检索质量：hit@5 **0.921**、拒答正确率 **1.0**，满足蓝图 §11（hit@5 ≥ 0.85、拒答 ≥ 0.80）。
- 本次价值不在「指标提升」，而在「参数可配置 + 决策有数据背书 + 排除 hybrid」：默认 600/100 本身 MRR 与基线持平，说明线上没有变好，但四个参数已从代码常量外置为配置项，且决策已写入 ADR 0003。
- 已知不足（写入 ADR 后续）：
  1. 评测集区分度不足——6 个分块变体 hit@1 全部 0.737，MRR 差异都在一个名次位内，本次结论置信度受限。→ Day21 补难题（多跳 / 精确 API 名 / 跨文档对比）。
  2. hybrid 当前实现（英文 BM25 + RRF）对中文无效，属「有代码无收益」，W6 需换中文分词 sparse 编码器（jieba 前置 / bge-m3 自带 sparse）并改用加权分数融合后再评估。
  3. rerank（bge-reranker）能同时提 MRR 和压误拒，但需额外模型服务，不在 W5 范围，记入 W6 候选。
