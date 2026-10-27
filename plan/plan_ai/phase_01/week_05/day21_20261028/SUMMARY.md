# Day 21 执行总结 · WorkPilot v0.3

执行计划：[PLAN.md](./PLAN.md)  
DA-01：WorkPilot；阶段一 · 第 5 周；资产锚点 M3.2（RAG 指标 / LLM-judge）、M3.4（Badcase 分类与修复）。

## 执行结果

| Step | 结果 |
|---|---|
| 1. 人工 gold | 已由用户人工标注 10 条，保存至 `~/lab/workpilot/eval/datasets/judge_gold.jsonl`；未由 AI 代标 |
| 2. Judge | 新增 `judge_answer.v1`、`eval/runners/judge.py` 与 `make eval-rag-judge`；correctness 一致率 90%，faithfulness / citation 一致率各 90% |
| 3. 阈值与全量评测 | 50 题全量评测完成；最终 dense `SCORE_THRESHOLD=0.52`，结果见 `~/lab/workpilot/eval/reports/20261028-rag-v0.3.{json,md}` |
| 4. Badcase 修复 | 首轮 14 条质量 badcase；收紧拒答阈值并升级 `qa_answer.v2` 后，correctness_mean 0.790 → 0.850，库内实际误拒率 0.184 → 0.053；仍有 12 条待后续处理，详见 `eval/badcases/badcases.md` |
| 5. 默认配置与 README | 已更新 `.env.example` 与 README；未 commit、未创建 / push `v0.3.0` tag，遵守用户要求 |
| 6. 能力矩阵与周复盘 | 已更新 `~/lab/projects/career/capability-matrix.md` 证据列及 Week 05 第 11 节 |

**当前状态：IN PROGRESS（本地实现和评测已完成；版本发布未完成）。** 不应将未提交工作树称为已发布的 `v0.3.0`。

## 最终指标

| 指标 | 基线 | 最终 v0.3 |
|---|---:|---:|
| hit@1 / hit@3 / hit@5 | 0.737 / 0.789 / 0.921 | 0.737 / 0.789 / 0.921 |
| MRR | 0.789 | 0.789 |
| 库外实际拒答正确率 | 1.000 | 1.000 |
| 库内实际误拒率 | 0.132 | 0.053 |
| 正确性均值（0–1） | — | 0.850 |
| 忠实度 yes 比例 / 非拒答引用正确率 | — | 1.000 / 1.000 |
| Judge 与 10 条人工 gold 一致率 | — | correctness 90%；faithfulness 90%；citation 90% |
| 回答 P95 / 总成本 / 单题均成本 | 2280 ms / ¥0.040968 / — | 2708 ms / ¥0.101336 / ¥0.002027 |

阈值扫描的数学最优候选是 0.60（库外分数自动拒答 12/12、库内自动误拒 1/38），但完整生成评测下库内实际误拒率为 0.184。最终选择 0.52：阈值自动误拒 0/38，且全量生成仍达到库外实际拒答 1.000、库内误拒 0.053。两种“拒答率”分开统计，避免把阈值自动拒答误当成端到端问答结果。

## 验证

- `uv run pytest -m "not llm" -q`：46 passed，2 deselected。
- `ruff check` / `ruff format --check`：评测 runner、Judge 和相关测试通过。
- 本地 API `/health`、库内 `/v1/kb/ask` 和库外拒答 curl 均已实测；分别返回 `status=ok`、带引用答案、拒答文本且 `citations` 为空。
- 评测实际执行成本：最终一轮 ¥0.101336；复跑 Judge 会调用 LLM 并产生额外费用。

## 终端验收命令

依赖服务未运行时，在终端 1 启动：

```bash
cd /Users/infinity/lab/workpilot && make up
```

在另一个终端启动 API：

```bash
cd /Users/infinity/lab/workpilot && make dev
```

在终端 2 验证健康检查：

```bash
curl --fail-with-body --silent --show-error --max-time 5 http://127.0.0.1:8000/health
```

预期包含：`"status":"ok"`。

验证库内问答（应返回带 `citations` 的答案）：

```bash
curl --fail-with-body --silent --show-error --max-time 60 --request POST 'http://127.0.0.1:8000/v1/kb/ask' --header 'Content-Type: application/json' --data '{"question":"给 WorkPilot 打版本 tag 有什么约束？"}'
```

验证库外拒答（应返回“知识库中没有找到”，且 `citations` 为空）：

```bash
curl --fail-with-body --silent --show-error --max-time 60 --request POST 'http://127.0.0.1:8000/v1/kb/ask' --header 'Content-Type: application/json' --data '{"question":"Kubernetes 的 HPA 怎么配置？"}'
```

复跑测试：

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run pytest -m "not llm" -q
```

复跑带 Judge 的 50 题评测（需要 Qdrant、Ollama、LLM 配置可用，会产生 LLM 费用）：

```bash
cd /Users/infinity/lab/workpilot && make eval-rag-judge ARGS="--stamp 20261028"
```

## 未完成项

- 按用户要求，不执行 `git commit`、不 push，也不创建 `v0.3.0` tag；若后续要发布，需用户明确授权并在测试通过后单独完成。
- 报告仍有 12 条 correctness ≤ 1 的 badcase：q003、q004 未召回；9 条部分回答 / 要点遗漏；q036 的期望证据与当前检索内容不匹配。下一步先核对语料与检索上下文，不通过修改评测题来追求分数。
