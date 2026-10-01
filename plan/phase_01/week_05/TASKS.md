# Week 05 · TASKS

## Task 1：评测集 50 题 + 检索指标 runner（Day19 · 10-16）

### 做什么

- 评测集从 20 扩到 50 题：in_kb 30 / out_of_kb 12 / confusing 8。
- `scripts/seed_eval.py`：从 Qdrant 抽样 chunk，用 LLM（M1.3 结构化输出 + `prompts/seed_question.v1.md`）生成候选题，写入 `eval/datasets/kb_qa.candidates.jsonl`；**人工审核改写后**再并入 `kb_qa.jsonl`（标注 `llm_seed`）。
- `eval/runners/run_rag_eval.py`：每题检索 top10 → hit@1/3/5、MRR（按 `expected_sources` 匹配）；库外题拒答正确率；P50/P95 延迟；成本；输出 JSON + Markdown，报告头含配置快照（chunk size / overlap / top_k / embedding / prompt 版本 / git sha）。
- `Makefile`：`make eval-rag`；产出基线报告。

### 为什么做

没有固定评测集和自动指标，后续每次调参都只能凭感觉；P1 验收要求 50 题基线。

### 资产锚点

M3.1 数据集规范、M3.2 RAG 指标；为 v0.3 做准备。

### 前置依赖

W4 的 `kb_qa.jsonl`（20 题）、`retrieve.search`、`answer.ask`、`data/index_manifest/kb_default.json`。

### 具体执行步骤（概要，详细见 day19_20261016/PLAN.md）

1. `seed_eval.py` 生成 40 道候选。
2. 人工审核：改写措辞、补 expected_sources，选入 30 道。
3. 写 runner（匹配 / 指标 / 快照 / 报告）。
4. Makefile + 跑基线。
5. 提交。

### 验收标准

- [ ] 50 题、比例正确、schema 校验通过、无重复问题
- [ ] `make eval-rag` 输出 `eval/reports/20261016-rag-baseline.{json,md}`
- [ ] 报告含 hit@1/3/5、MRR、拒答正确率、P50/P95、成本、配置快照（含 git sha）
- [ ] 每题记录 top1 分数（Day21 定阈值用）

### 完成后的产出（文件路径）

`eval/datasets/kb_qa.jsonl`、`prompts/seed_question.v1.md`、`scripts/seed_eval.py`、`eval/runners/run_rag_eval.py`、`Makefile`、`eval/reports/20261016-rag-baseline.{json,md}`

### 求职映射

「hit@k / MRR / 拒答率」是 RAG 面试必问指标；「LLM 生成评测题的偏差」是加分点。

### 如果时间不够 / 没有必要

seed 脚本可省（手写 30 题）；runner 中生成相关指标（拒答）用 `--with-answer` 开关，时间不够只跑检索指标 + 库外题生成。

---

## Task 2：检索实验（Day20 · 10-17）

### 做什么

- `eval/configs/*.yaml` 定义变体：chunk 300/600/1000 × overlap 0/100；top_k 3/5/8；P1：hybrid（Qdrant 稀疏 + 稠密，Query API prefetch + RRF；稀疏用 fastembed `Qdrant/bm25`）；P2：query rewrite、bge-reranker。
- 每个分块变体入库到独立 collection `kb_exp_<variant>`，不覆盖 `kb_default`。
- 结果表：变体 | hit@5 | MRR | 拒答正确率 | P95 延迟 | 成本；选最优写 `docs/adr/0003-chunking-retrieval.md`。

### 为什么做

用数据回答「chunk 多大、top_k 多少、hybrid 值不值」，并把决策沉淀为 ADR（作品集与面试素材）。

### 资产锚点

M2.2 Chunking、M2.4 Retrieval；为 v0.3 做准备。

### 前置依赖

Task 1 runner 支持 `--config`；ingest 支持 `--collection/--chunk-size/--overlap`。

### 具体执行步骤（概要，详细见 day20_20261017/PLAN.md）

1. 写 YAML 变体 + `scripts/run_experiments.sh`。
2. 跑分块变体（检索指标，零 LLM 成本）。
3. 在最优分块上跑 top_k 3/5/8（带生成，看拒答/成本/延迟）。
4. P1 hybrid；P2 rewrite/rerank。
5. 汇总表 + ADR 0003 + 提交。

### 验收标准

- [ ] ≥ 4 个变体有完整结果
- [ ] 实验对比表 `eval/reports/20261017-retrieval-experiments.md`
- [ ] ADR 0003：背景 / 选项 / 数据 / 决定 / 代价 / 放弃方案
- [ ] `kb_default` 未被实验覆盖（points_count 与实验前一致）

### 完成后的产出（文件路径）

`eval/configs/*.yaml`、`scripts/run_experiments.sh`、`eval/reports/20261017-retrieval-experiments.md`、`docs/adr/0003-chunking-retrieval.md`、（P1）`apps/api/app/rag/sparse.py`

### 求职映射

「用评测驱动参数选择 + ADR」可以直接写进 P1 技术复盘。

### 如果时间不够 / 没有必要

只做 overlap=100 的 3 个 chunk 变体 + top_k 3/5/8；hybrid 写进 ADR「待评估」。

---

## Task 3：LLM-judge + Badcase 分类 + 定配置（Day21 · 10-18）

### 做什么

- `eval/runners/judge.py` + `prompts/judge_answer.v1.md`：correctness（0/1/2 对照 expected）、faithfulness（yes/partial/no：是否全部有上下文支持）、citation_correct（bool），用 M1.3 结构化输出。
- 先人工标 10 条（`eval/datasets/judge_gold.jsonl`），计算 judge 与人工一致率（目标 ≥ 80%）。
- 完整报告 `eval/reports/20261018-rag-v0.3.{json,md}`（检索 + 生成指标）；Badcase 分类统计，修复前 2 类并回归。
- 默认配置写入 `.env.example`（含 `SCORE_THRESHOLD`）；README v0.3；tag `v0.3.0`；更新 `career/capability-matrix.md` 的 RAG/Eval 证据列；Week 5 复盘。

### 为什么做

检索指标只说明「找没找到」，judge 才能衡量「答得对不对、有没有编」；人工校准让 judge 可信。v0.3 是 P1 评测部分的定稿。

### 资产锚点

M3.2 RAG 指标（judge）、M3.4 Badcase 库；**v0.3**。

### 前置依赖

Task 1 runner、Task 2 选定配置。

### 具体执行步骤（概要，详细见 day21_20261018/PLAN.md）

1. 人工标 10 条 gold。
2. judge prompt + judge.py，计算一致率，必要时 v2。
3. 用选定配置跑完整评测（检索 + 生成 + judge）。
4. Badcase 统计 → 修复前 2 类 → 回归。
5. `.env.example`、README、tag、能力矩阵、复盘。

### 验收标准

- [ ] 一致率（correctness）≥ 80% 或有未达标分析
- [ ] v0.3 报告含正确性均值、忠实度 yes 比例、引用正确率、检索指标、延迟、成本
- [ ] Badcase 分类统计表 + 前 2 类修复前后对比
- [ ] tag `v0.3.0` 已 push

### 完成后的产出（文件路径）

`prompts/judge_answer.v1.md`、`eval/runners/judge.py`、`eval/datasets/judge_gold.jsonl`、`eval/reports/20261018-rag-v0.3.{json,md}`、`eval/badcases/badcases.md`、`.env.example`、`README.md`、`~/lab/projects/career/capability-matrix.md`

### 求职映射

「LLM-as-a-judge + 人工一致率校准」是 LLM Evaluation 岗位与高级 AI Engineer 面试的高频深挖点。

### 如果时间不够 / 没有必要

修复只做第 1 类；能力矩阵更新可放到 W8 作品集周，但 tag 与报告不可省。

---
