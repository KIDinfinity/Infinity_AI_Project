# Week 14 · Agent Evaluation + 回归门禁（Phase 2 · Day49–Day51 · 11-15 → 11-17）

## 1. 本周核心目标

让「Agent 是否变好」从感觉变成数字：

1. `eval/datasets/agent_tasks.jsonl` 30 个任务 + `run_agent_eval.py` 记录完整轨迹。
2. 评测器：工具选择 precision/recall、forbidden 违规、工具成功率、LLM-judge 任务成功率、步数、P50/P95 延迟、平均成本；judge 先用 8 条人工标注校准。
3. RAG + Agent 基线 + `compare_eval.py` 回归判定 + `make eval-smoke` 进 Gitea Actions CI；修复头号失败类别一次并展示提升。

## 2. 资产锚点

| 构建模块         | 版本里程碑     | 本周结束 WorkPilot 能演示什么                                                                                  |
| ---------------- | -------------- | -------------------------------------------------------------------------------------------------------------- |
| M3.3 Agent 指标  | 为 v1.0 做准备 | `make eval-agent` 产出 `eval/reports/YYYYMMDD-agent-v0.9.md`：30 任务的成功率、工具选择准确率、步数、P95、成本 |
| M3.5 回归 + 门禁 | 为 v1.0 做准备 | 故意改坏工具描述 → CI `eval-smoke` 失败；恢复后通过                                                            |
| M3.4 Badcase 库  | —              | Agent badcase 按 6 类失败分类入库                                                                              |

## 3. 为什么这一周存在

- P2 验收硬指标（DA01 §11）：任务成功率 ≥ 0.70、工具选择准确率 ≥ 0.85、平均步数 ≤ 6——没有评测就无法宣称 v1.0。
- W15 要加 Trace / 预算 / Guardrail，这些改动都可能让 Agent 变差；先有回归门禁，后面的改动才安全。
- 面试中「你怎么评测 Agent」是区分 Demo 与工程的必考题。

## 4. 本周在路线中的位置

```text
W13 产出：v0.9 工具集稳定（内置 6 个 + ext.fs.* + MCP 出口），AgentRun/AgentStep 有运行记录
   ↓
W14 本周：30 任务评测集 + 轨迹 runner + 评测器/报告 + 基线 + CI 门禁
   ↓
W15 输入：每次加 Trace/预算/护栏后跑 eval-smoke 证明不退化；评测成本数字给 Ops 看板做对照
```

## 5. 每日安排

| Day   | 日期  | Task                                    | 当日 P0 产出                                                                    | 模块      | 状态 |
| ----- | ----- | --------------------------------------- | ------------------------------------------------------------------------------- | --------- | ---- |
| Day49 | 11-15 | Task 1：Agent 评测集 30 任务 + 轨迹记录 | `agent_tasks.jsonl` 30 条 + runner 跑通并产出轨迹 JSON                          | M3.3      | TODO |
| Day50 | 11-16 | Task 2：Agent 评测器 + 报告             | `judge_agent.v1.md` + 8 条校准 + `eval/reports/YYYYMMDD-agent-v0.9.md`          | M3.3 M3.4 | TODO |
| Day51 | 11-17 | Task 3：回归 + CI 门禁                  | `eval/baseline/*.json` + `compare_eval.py` + CI `eval-smoke` + 一次修复前后对比 | M3.5      | TODO |

## 6. 本周必须留下的资产

| 路径                                                                         | 说明                                                  |
| ---------------------------------------------------------------------------- | ----------------------------------------------------- |
| `eval/datasets/agent_tasks.jsonl`                                            | 30 个 Agent 任务（5 类）                              |
| `eval/datasets/README.md`                                                    | 新增 agent_tasks schema 说明                          |
| `eval/runners/run_agent_eval.py`                                             | 直调 graph、temperature=0、轨迹记录、评测模式自动审批 |
| `eval/runners/agent_metrics.py`                                              | 规则指标计算                                          |
| `prompts/judge_agent.v1.md`                                                  | Agent judge rubric                                    |
| `eval/calibration/agent_judge_human.jsonl`                                   | 8 条人工标注                                          |
| `eval/reports/20261116-agent-v0.9.md`                                        | 首份 Agent 评测报告                                   |
| `eval/badcases/badcases.md`                                                  | 新增 Agent 失败分类与条目                             |
| `eval/baseline/rag.json`、`eval/baseline/agent.json`                         | 基线                                                  |
| `scripts/compare_eval.py`、`Makefile`（eval-smoke / eval-full / eval-agent） | 回归判定                                              |
| `.gitea/workflows/ci.yml`                                                    | 新增 eval-smoke job                                   |
| `eval/runs/`                                                                 | 轨迹明细（gitignore，不提交）                         |

## 7. 本周验收标准

- [ ] PASS / FAIL：30 条任务覆盖 5 类，每类 ≥ 5 条，schema 校验脚本通过
- [ ] PASS / FAIL：runner 对 30 条全部产出轨迹 JSON（含工具调用/参数/结果/tokens/延迟）
- [ ] PASS / FAIL：评测模式下写工具只作用于 mock/沙盒，真实仓库未新增 Issue
- [ ] PASS / FAIL：报告含 7 项指标数值 + 失败分类表；judge 与人工标注一致 ≥ 6/8
- [ ] PASS / FAIL：`compare_eval.py` 在指标下降超阈值时退出码非 0（有演示记录）
- [ ] PASS / FAIL：CI 中 `eval-smoke` 运行，单次成本有估算
- [ ] PASS / FAIL：头号失败类别修复一次，重跑后该类数量下降

## 8. 求职映射

- **本周能力**：Agent 评测设计、轨迹评估、LLM-as-a-judge 校准、回归测试、CI 质量门禁。
- **简历 bullet 草稿**：
  - 设计 30 任务 Agent 评测集（5 类）与轨迹级评测器（工具选择 P/R、违规调用、judge 任务成功率、P95、成本），任务成功率从 ** 提升至 **。
  - 将 RAG + Agent 小样本评测接入 CI 回归门禁（单次成本约 ¥\_\_），指标下降超阈值自动阻断合并。
- **面试题**：
  1. Agent 评测和 RAG 评测有什么不同？你评测哪些维度？
  2. LLM-as-a-judge 怎么保证可靠？你怎么校准的？
  3. 评测放进 CI 怎么控制成本和不稳定性？

## 9. 本周禁止事项

- 不引入第三方评测平台 / 框架（自研 runner + judge 即可）。
- 不扩充到 30 条以上任务；不做多模型横评。
- 评测语料不含公司内容；写工具在评测中绝不指向真实仓库。
- 不为了提高分数而改评测集标准答案（只能修系统或修明显错误的标注，并记录）。
- 不把完整 eval-full 放进每次 CI。

## 10. 时间不够时（最小保留）

- Day49：20 条任务 + runner 跑通 5 条。
- Day50：规则指标（工具 P/R、违规、步数、延迟、成本）+ judge 跑通，校准可减为 5 条。
- Day51：`compare_eval.py` + `make eval-smoke` 本地可用；CI 接入可延到 Day52 开头，「修复一次」可顺延到 W15 但必须记录。

## 11. 周复盘（Day51 填写）

- 完成：\_\_\_\_
- 未完成 / 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示/可测量的东西：\_\_\_\_
- 是否出现无效学习或范围扩张：\_\_\_\_
- Agent 当前离 §11 目标的差距（成功率 / 工具准确率 / 步数）：\_\_\_\_
- 下周调整：\_\_\_\_
