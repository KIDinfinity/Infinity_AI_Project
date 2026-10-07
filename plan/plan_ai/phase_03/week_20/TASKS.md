# Week 20 · TASKS

## Task 1：场景评测集 + rubric + 人审表（Day64 · 02-08）

### 做什么

把 `data/scenarios/` 中二次脱敏的 20 个样例转成 `eval/datasets/scenario_spb.jsonl`（`{id, requirement, context_docs, expected_tasks_min, must_cover[], forbidden[], notes}`）；写 `prompts/judge_scenario.v1.md`（覆盖度 / 粒度 / 验收标准可测性 / 估时合理性 / 规范符合度，各 0–2，≥ 7/10 通过）；写 `eval/runners/run_scenario_eval.py`（只跑到审批前）；人审 10 条写 `eval/human_review/20270208.csv` 并算一致率；出报告。

### 为什么做

蓝图 §11 P3 场景指标的测量工具；没有它，W21–W22 的优化无法证明「变好了」。

### 资产锚点

- 模块：M3.1、M3.2/M3.3（场景 rubric）、M3.5（为回归准备）
- 版本：为 v1.3 做准备

### 前置依赖

- W18 SP-B 场景图（可只跑到 interrupt）
- W5 LLM-judge 与 W14 runner / compare_eval.py 代码可复用
- Day58 样例 + Day61 p3-notes 中的候选 badcase

### 具体执行步骤（概要，详见 day64_20261130/PLAN.md）

1. 二次脱敏检查 → 写 20 条 JSONL。
2. 写 judge prompt（含评分锚点）。
3. runner：确定性检查（must_cover / forbidden / 任务数）+ judge 打分 + 汇总。
4. 跑评测 → 报告。
5. 人审 10 条 → 一致率 → 写入报告。

### 验收标准

- [ ] 20 条数据集，`jq` 校验全部合法
- [ ] 报告含通过率 / 维度均分 / 失败列表 / 成本
- [ ] 一致率已计算，结论已写

### 完成后的产出

- `eval/datasets/scenario_spb.jsonl`、`prompts/judge_scenario.v1.md`、`eval/runners/run_scenario_eval.py`
- `eval/human_review/20270208.csv`、`eval/reports/20270208-scenario-spb.md`

### 求职映射

「LLM judge + 人审校准」是 AI Engineer 面试评测题的标准高分回答。

### 如果时间不够 / 没有必要

- 人审压到 5 条；context_docs 先为空（用 KB 实时检索）。
- 不做 Cohen's Kappa（简单一致率即可）。

---

## Task 2：在线反馈闭环 + 评测看板（v1.3）（Day65 · 02-09）

### 做什么

审批 resume 时对比「原始草案 vs 批准版」，计算编辑 diff（删除 / 修改 / 新增任务数、估时变化、edit_ratio）写入 Feedback（kind=implicit_edit）；Badcase 候选队列页（👎 或 edit_ratio ≥ 0.3）+「提升为回归用例」（勾选已脱敏确认）；`scripts/export_regression.py` 导出到数据集（`tags:["regression"]`），人工 review diff 后提交；EvalRun 表 + 趋势页；P3 评测报告 v1；tag `v1.3.0`。

### 为什么做

把真实使用变成评测数据（数据飞轮）；趋势页是 W22 Eval v2「v0.5 → v1.0 → v2.0」展示的基础。

### 资产锚点

- 模块：M3.6、M4.4
- 版本：**v1.3**

### 前置依赖

- Day64 数据集与 runner
- W6 Feedback 表、W19 Postgres + Alembic

### 具体执行步骤（概要，详见 day65_20261201/PLAN.md）

1. Feedback 加 `kind`、`status`、`payload` 字段；EvalRun 表；迁移。
2. resume 时计算 diff 写 Feedback。
3. 接口：badcase 候选列表、promote、EvalRun 列表。
4. 前端：BadcaseQueuePage、EvalTrendPage。
5. 导出脚本 + runner 写 EvalRun。
6. P3 评测报告 v1 + tag v1.3.0。

### 验收标准

- [ ] 一次编辑审批后 Feedback 出现 implicit_edit 记录
- [ ] promote → 导出 → 人工确认 → 数据集多 1 条 regression 用例
- [ ] 趋势页显示 ≥ 2 次 EvalRun
- [ ] `v1.3.0` 已部署

### 完成后的产出

- `apps/api/app/eval/feedback.py`、`apps/api/app/routes/eval.py`
- `apps/web/src/pages/BadcaseQueuePage.tsx`、`EvalTrendPage.tsx`
- `scripts/export_regression.py`、`eval/reports/20270209-p3-eval-v1.md`
- tag `v1.3.0`

### 求职映射

「隐式反馈 + 数据飞轮」——AI 产品工程与 AI Full-Stack 面试的加分项。

### 如果时间不够 / 没有必要

- 趋势页用报告中的表格代替，页面进 Backlog。
- promote 只做后端接口 + 导出脚本，页面按钮顺延。

---
