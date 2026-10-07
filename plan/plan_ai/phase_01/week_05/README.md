# Week 05 · RAG 评测与优化（Phase 1 · Day19–Day21 · 10-26 → 10-28）

## 1. 本周核心目标

把 v0.2 的「20 题人工看」升级为**可重复的量化评测体系**：50 题评测集 + 检索指标 runner（hit@k / MRR / 拒答正确率 / 延迟 / 成本）+ 检索参数实验 + LLM-judge（正确性 / 忠实度 / 引用正确），用数据选定默认配置，交付 **WorkPilot v0.3**。

## 2. 资产锚点

| 项                            | 内容                                                                                                                                                                                                                                                        |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 构建模块                      | M3.1 数据集规范（50 题）、M3.2 RAG 指标（hit@k、MRR、拒答、judge）、M3.4 Badcase 分类统计、M2.2 Chunking 调参、M2.4 Retrieval（top_k / hybrid 实验）                                                                                                        |
| 版本里程碑                    | **v0.3**（tag `v0.3.0`，Day21）                                                                                                                                                                                                                             |
| 本周结束 WorkPilot 能演示什么 | ① `make eval-rag` 一条命令输出带配置快照的 JSON + Markdown 报告；② 实验对比表（chunk × overlap × top_k，P1 hybrid）与 ADR 0003；③ `eval/reports/20261028-rag-v0.3.md`：检索 + 生成指标、judge 与人工一致率、Badcase 分类统计；④ 默认配置写入 `.env.example` |

## 3. 为什么这一周存在

- P1 验收要求「50 题评测报告存在，hit@5、引用正确率、拒答率有基线数值」，蓝图 §11 的指标目标（hit@5 ≥ 0.85 等）需要本周的基线来校准。
- 没有评测的调参是玄学：本周把「chunk 多大、top_k 多少、要不要 hybrid」变成有数据支撑、写进 ADR 的决策——这是面试中最能区分「做过 Demo」和「做过工程」的部分。
- M3 Eval Kit 在 W14（Agent 评测）、W20（场景评测）、W22（Eval v2）持续复用，本周的 runner 与报告格式就是它的骨架。

## 4. 本周在路线中的位置

```text
W4 产出：RAG 链路（ingest/chunk/embed/qdrant/retrieve/answer）+ /v1/kb/* API
        + kb_qa.jsonl 20 题 schema + run_kb_smoke.py + badcases.md（8 类根因）→ v0.2
   ↓
W5（本周）：Day19 50 题 + run_rag_eval.py 基线 → Day20 参数实验 + ADR 0003
        → Day21 LLM-judge + 一致率 + Badcase 统计 + 修复前 2 类 + 定默认配置 → v0.3
   ↓
W6 输入：定版的检索配置（.env.example）、/v1/kb/ask/stream 的事件约定、
        评测报告（作品集素材）、make eval-rag（W7 CI 小样本、W14 Agent 评测复用）
```

## 5. 每日安排

| Day   | 日期  | Task                                      | 当日 P0 产出                                                                                                                                        | 模块             | 状态 |
| ----- | ----- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---- |
| Day19 | 10-26 | Task 1：评测集 50 题 + 检索指标 runner    | `kb_qa.jsonl` 50 题（30/12/8）、`eval/runners/run_rag_eval.py`、`make eval-rag`、基线报告 `eval/reports/20261026-rag-baseline.{json,md}`            | M3.1 M3.2        | TODO |
| Day20 | 10-27 | Task 2：检索实验                          | `eval/configs/*.yaml`、`kb_exp_<variant>` collections、实验对比表、`docs/adr/0003-chunking-retrieval.md`                                            | M2.2 M2.4        | TODO |
| Day21 | 10-28 | Task 3：LLM-judge + Badcase 分类 + 定配置 | `eval/runners/judge.py`、`prompts/judge_answer.v1.md`、人工 10 条一致率、`eval/reports/20261028-rag-v0.3.md`、`.env.example` 默认配置、tag `v0.3.0` | M3.2 M3.4 / v0.3 | TODO |

## 6. 本周必须留下的资产（文件路径级）

```text
eval/datasets/kb_qa.jsonl                 # 50 题
eval/datasets/judge_gold.jsonl            # 人工标注 10 条
eval/configs/{c300_o0,c300_o100,c600_o0,c600_o100,c1000_o0,c1000_o100,hybrid_c600_o100}.yaml
eval/runners/run_rag_eval.py
eval/runners/judge.py
eval/reports/20261026-rag-baseline.{json,md}
eval/reports/20261027-retrieval-experiments.md
eval/reports/20261028-rag-v0.3.{json,md}
eval/badcases/badcases.md                 # 分类统计 + 前 2 类修复状态
prompts/judge_answer.v1.md
prompts/seed_question.v1.md
scripts/seed_eval.py
scripts/run_experiments.sh
docs/adr/0003-chunking-retrieval.md
Makefile（eval-rag / eval-rag-judge）
.env.example（CHUNK_SIZE / CHUNK_OVERLAP / TOP_K / SCORE_THRESHOLD / RETRIEVAL_MODE / ANSWER_PROMPT）
README.md（v0.3 评测结果）  git tag v0.3.0
~/lab/projects/career/capability-matrix.md（RAG / Eval 证据列）
```

## 7. 本周验收标准（PASS/FAIL 勾选）

- [ ] `kb_qa.jsonl` 50 题（in_kb 30 / out_of_kb 12 / confusing 8），LLM 生成的候选全部经过人工审核（`tags` 含 `llm_seed` 的题有审核记录）
- [ ] `make eval-rag` 产出 JSON + MD 报告，报告头含配置快照（chunk_size / overlap / top_k / embedding / prompt 版本 / git sha）
- [ ] 基线报告有 hit@1/3/5、MRR、库外拒答正确率、P50/P95 延迟、总成本
- [ ] 实验表 ≥ 4 个变体，选定配置写进 ADR 0003（含理由与放弃方案）
- [ ] judge 与人工一致率（correctness）≥ 80%，或已记录未达标原因与 prompt 改进
- [ ] v0.3 报告含检索 + 生成指标（正确性、忠实度、引用正确率）与 Badcase 分类统计
- [ ] 前 2 类 Badcase 已有修复动作并回归验证
- [ ] `.env.example` 默认配置已更新；tag `v0.3.0` 已 push；能力矩阵已更新

## 8. 求职映射

- 本周能力：RAG Evaluation（检索指标 + LLM-as-a-judge + 人工校准）、实验设计与对照、ADR 技术决策记录、数据驱动优化。
- 简历 bullet 草稿：
  - 「搭建 RAG 评测体系：50 题三类评测集 + 检索指标（hit@k / MRR）+ LLM-judge（正确性/忠实度/引用），judge 与人工标注一致率 \_\_%；报告自动记录配置快照与 git sha，可复现对比。」
  - 「通过 ** 组分块/检索参数实验将 hit@5 从 ** 提升至 **、MRR 从 ** 提升至 **，库外拒答正确率达 **，P95 延迟 **s，单次成本 ¥**。」
- 面试题：
  1. hit@k 和 MRR 分别衡量什么？为什么两个都要看？
  2. LLM-as-a-judge 有哪些偏差？你怎么验证 judge 可信？
  3. chunk size 实验你是怎么设计的？怎么避免实验之间互相污染？

## 9. 本周禁止事项

- 不换 embedding 模型、不换向量库、不引入 RAGAS / TruLens / LangSmith 等评测框架（手写 runner 更利于理解与讲解）。
- rerank、query rewrite 只作为 P2，且只在 P0/P1 全部完成后尝试；不为 rerank 引入 PyTorch 重依赖进主项目（如需尝试放 `ai-lab/`）。
- 不为追求指标去改测试题（禁止「看答案改题」）；题目修改必须记录原因。
- 不做前端评测看板（W20）。
- 不把评测语料或报告中的敏感内容提交（报告只含问题与来源路径）。

## 10. 时间不够时（最小保留）

1. Day19：50 题 + runner（hit@k / MRR / 拒答）+ 基线报告（Makefile、seed 脚本可延期）。
2. Day20：chunk 300 / 600 / 1000（overlap 100）3 个变体 + top_k 3/5/8 + 简版 ADR（overlap 0、hybrid 延期为 Backlog）。
3. Day21：judge + 10 条人工一致率 + v0.3 报告 + `.env.example` + tag（修复只做第 1 类）。

## 11. 周复盘（周末填写）

- 完成：\_\_\_\_
- 未完成及原因：\_\_\_\_
- WorkPilot 本周多了什么可演示/可测量的东西：\_\_\_\_
- 基线 → v0.3：hit@5 ** → **；MRR ** → **；拒答 ** → **；正确性 **；忠实度 **；P95 **s；单次成本 ¥**
- 与蓝图 §11 目标的差距（是否需要调整目标并记 CHANGELOG）：\_\_\_\_
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整（W6 Web Console）：\_\_\_\_
