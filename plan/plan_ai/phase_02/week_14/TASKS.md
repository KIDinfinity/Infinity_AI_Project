# Week 14 · TASKS

## Task 1：Agent 评测集 30 任务 + 轨迹记录（Day49 · 12-28）

### 做什么

定义 `agent_tasks.jsonl` schema 并写 30 条任务（research / repo_qa / kb_qa / breakdown / multi_tool 各 6 条）；写 `eval/runners/run_agent_eval.py`：直接调用 LangGraph graph（非 HTTP），temperature=0，记录轨迹到 `eval/runs/<ts>/<id>.json`；评测模式下写工具自动批准但只走 mock / 沙盒仓库。

### 为什么做

Agent 的质量取决于整条轨迹（选什么工具、参数、何时结束），只看最终答案会漏掉大部分问题；轨迹是 Day50 评测器和 W15 Trace 的数据基础。

### 资产锚点

M3.3 · 为 v1.0 做准备

### 前置依赖

v0.9 工具集稳定；`app/agent/graph.py` 可构建 graph；W9 的 `tool_selection.jsonl` 15 条可作为素材；Gitea 有（或今天创建）`workpilot-sandbox` 仓库。

### 具体执行步骤（概要，详见 day49_20261115/PLAN.md）

1. 写 schema + 分布表 + 4 条示例。
2. 补齐 30 条（AI 起草 → 自己逐条改 expected_tools / must_include_facts）。
3. `scripts/validate_agent_tasks.py` 校验。
4. runner：InMemorySaver、`stream_mode="updates"`、interrupt 自动 resume、轨迹落盘。
5. 跑 5 条冒烟，再全量跑 30 条。

### 验收标准

- [ ] 30 条、5 类各 6 条，校验通过
- [ ] 30 个轨迹 JSON，字段齐全
- [ ] 评测期间真实仓库 Issue 数不变

### 完成后的产出（文件路径）

`eval/datasets/agent_tasks.jsonl`、`eval/datasets/README.md`、`scripts/validate_agent_tasks.py`、`eval/runners/run_agent_eval.py`、`.gitignore`（`eval/runs/`）

### 求职映射

评测集设计、轨迹记录、可复现实验 → AI Agent Engineer / LLM Engineer。

### 如果时间不够 / 没有必要

先写 20 条（每类 4 条）+ runner 跑 5 条；剩余 10 条 Day50 开头 20 分钟补。

---

## Task 2：Agent 评测器 + 报告（Day50 · 12-29）

### 做什么

基于轨迹计算：工具选择 precision / recall、forbidden 违规数、工具成功率、步数、P50/P95 延迟、平均成本；写 `prompts/judge_agent.v1.md`（完整性 / 事实覆盖 / 引用可信，各 0–2）判任务成功；先人工标 8 条校准 judge；输出报告 + 失败分类，并把 Agent badcases 入库。

### 为什么做

把 30 条轨迹变成可对比的指标和可行动的失败分类，是 Day51 基线与修复的依据，也是 P2 作品集的核心数字。

### 资产锚点

M3.3 M3.4 · 为 v1.0 做准备

### 前置依赖

Task 1 的 30 个轨迹 JSON；RAG 的 `judge` 实现（W5）可复用调用方式。

### 具体执行步骤（概要，详见 day50_20261116/PLAN.md）

1. `agent_metrics.py` 规则指标。
2. judge prompt + 调用 + 解析。
3. 人工标 8 条 → 对比一致率 → 调 rubric 一次。
4. 生成报告 + 失败分类表 + badcases。

### 验收标准

- [ ] 报告含 7 项指标数值
- [ ] judge 与人工一致 ≥ 6/8（不达标则记录原因并改 rubric 后重测）
- [ ] 每个失败任务有且仅有一个主失败类别
- [ ] badcases.md 新增 Agent 条目 ≥ 5

### 完成后的产出（文件路径）

`eval/runners/agent_metrics.py`、`prompts/judge_agent.v1.md`、`eval/calibration/agent_judge_human.jsonl`、`eval/reports/20261229-agent-v0.9.md`、`eval/badcases/badcases.md`

### 求职映射

LLM-as-a-judge 校准、指标设计、错误分析 → AI Engineer / Applied AI Engineer。

### 如果时间不够 / 没有必要

P0 = 规则指标 + judge + 报告；校准减为 5 条；失败分类只标主类别不写根因细节。

---

## Task 3：回归 + CI 门禁（Day51 · 12-30）

### 做什么

固化 `eval/baseline/{rag,agent}.json`；写 `scripts/compare_eval.py`（任务成功率 -5pt、hit@5 -3pt 等阈值，超阈值非零退出）；`make eval-smoke`（5 RAG + 5 Agent，便宜模型）加入 `.gitea/workflows/ci.yml`，key 用 Gitea Actions secrets，估算单次成本；`make eval-full` 每周手动。修复头号失败类别一次并重跑展示提升。周复盘。

### 为什么做

没有门禁的评测会被遗忘；W15 起的每次改动都必须能自动证明「没变差」。

### 资产锚点

M3.5 · 为 v1.0 做准备

### 前置依赖

Task 2 报告；W5 RAG runner 支持输出 JSON 汇总；W7 CI 已有 lint/test/build job 与 act_runner。

### 具体执行步骤（概要，详见 day51_20261117/PLAN.md）

1. runner 输出统一 summary JSON → 复制为 baseline。
2. `compare_eval.py` + 本地故意退化演示。
3. Makefile + CI job + secrets + 成本估算。
4. 修复头号失败类别 → `eval-full` 重跑 → 报告对比 → 更新 baseline。
5. 周复盘。

### 验收标准

- [ ] 故意退化时 `compare_eval.py` 退出码 1，正常时 0
- [ ] CI 日志可见 eval-smoke 运行与对比结果
- [ ] 修复前后对比表（该失败类别数量下降）
- [ ] 单次 eval-smoke 成本估算写入报告

### 完成后的产出（文件路径）

`eval/baseline/rag.json`、`eval/baseline/agent.json`、`scripts/compare_eval.py`、`Makefile`、`.gitea/workflows/ci.yml`、`eval/reports/20261230-agent-v0.9.1.md`

### 求职映射

评测驱动开发、CI 质量门禁、成本意识 → AI Platform Engineer / MLOps 方向。

### 如果时间不够 / 没有必要

P0 = baseline + compare 脚本 + 本地 `make eval-smoke`；CI 接入与修复可顺延到 Day52 开头，但需在周复盘中记录。

---
