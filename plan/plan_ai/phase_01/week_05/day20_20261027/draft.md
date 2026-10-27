控制配置变量测试

- [✅] `eval/configs/` 下 ≥ 4 个 YAML 变体
- [✅] 每个分块变体有独立 collection `kb_exp_<variant>`；`kb_default` 点数在选定配置重建前保持不变
- [✅] 每个变体有 `eval/reports/20261027-exp-<variant>.{json,md}`
- [✅] `eval/reports/20261027-retrieval-experiments.md` 汇总表含：变体 | chunks | hit@5 | MRR | 拒答正确率 | P95 延迟 | 成本
- [✅] top_k 3/5/8 在最优分块上带生成跑过（对比拒答、误拒、成本、延迟）
- [✅] `docs/adr/0003-chunking-retrieval.md` 写明决定、数据、代价、放弃方案
- [✅] （P1）hybrid 变体有结果或在 ADR 中写明未完成原因
- [✅] 已 push