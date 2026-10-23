给题目和标准答案，然后评价大模型表现

- [ ] `kb_qa.jsonl` 50 行：in_kb 30 / out_of_kb 12 / confusing 8；schema 校验通过；`question` 无重复
- [ ] LLM 生成并入选的题 `tags` 含 `llm_seed`，且每道都经过人工改写/核对（第 11 节记录改写数）
- [ ] `make eval-rag` 成功，生成 `eval/reports/20261026-rag-baseline.json` 与 `.md`
- [ ] 报告头含：dataset 行数、collection、chunk_size、overlap、top_k、embed_model、answer_prompt、git sha
- [ ] 报告含：hit@1/3/5、MRR（38 道有来源的题）、库外拒答正确率（12 题）、库内误拒率、检索与回答 P50/P95、总成本
- [ ] 每题记录 `top1_score`；报告给出 in_kb 与 out_of_kb 的 top1 分数均值
- [ ] 已 push
