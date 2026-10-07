收集职业jd需要哪些技术（适当多强化这些技术，看是否偏离主线）

- [✅] `career/` 下存在 `capability-matrix.md`、`job-market.md`、`interview-questions.md`、`resume/README.md`
- [✅] `grep -c '^## JD-' career/job-market.md` = 10，每条 7 个字段齐全（公司类型 / 岗位 / 城市 / 薪资 / 必需技能 / 加分技能 / 链接）
- [✅] `career/jd-skills.jsonl` 10 行，`python3 career/tally.py` 输出频次表
- [✅] 矩阵 Top-12 能力每行 7 列填满（「不做」的能力在证明模块写「不做（理由）」）
- [✅] 差距清单 ≥ 3 项，并已核对计划周与蓝图附录 A 一致
- [✅] 已 push