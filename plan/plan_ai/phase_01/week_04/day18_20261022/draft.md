跑报告，人工判断对错

- [✅] `eval/datasets/kb_qa.jsonl` 20 行：in_kb 12、out_of_kb 5、confusing 3；脚本启动时 schema 校验全部通过
- [✅] `uv run --project apps/api python scripts/run_kb_smoke.py` 生成 `eval/reports/20261022-rag-v0.2.md`
- [✅] 报告含：来源命中率（in_kb + confusing 共 15 题）、库外拒答率（5 题）、人工正确率（20 题，手填）、平均延迟、总成本
- [✅] `eval/badcases/badcases.md` 升级为完整模板，≥ 5 条（含 v0.1 条目的复测结论）
- [✅] README 有 v0.2 章节（含与 v0.1 对比）
- [✅] `git tag` 有 `v0.2.0` 且已 push；Week 4 README 第 11 节已填写
