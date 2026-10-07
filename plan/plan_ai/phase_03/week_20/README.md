# Week 20 · 场景评测 + 反馈闭环（Phase 3 · Day64–Day65 · 02-08 → 02-09）

## 1. 本周核心目标

给 SP-B 建立「离线评测 + 在线反馈」双闭环：20 条场景评测集 + LLM judge rubric（5 维 × 0–2 分，≥ 7/10 通过）+ 10 条人审校准一致率；把审批前的编辑 diff 作为隐式反馈，建立 Badcase 候选队列与「提升为回归用例」流程，加 EvalRun 表与评测趋势页，产出 P3 评测报告 v1，发布 **v1.3.0**。

## 2. 资产锚点

| 构建模块                                                                      | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                                                                                                  |
| ----------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M3.1 数据集、M3.2/M3.3 指标（场景 rubric）、M3.6 在线反馈闭环、M4.4 Eval 看板 | **v1.3**   | `make eval-scenario` 产出报告（通过率、各维度均分、judge 与人审一致率）；Badcase 队列页看到「编辑最多」的运行，一键提升为回归候选；趋势页显示多次 EvalRun 折线 |

## 3. 为什么这一周存在

- 蓝图 §11 的 P3 指标「20 个场景用例 rubric 通过率 ≥ 0.75」需要可重复的测量工具。
- 生成类任务（任务拆解）没有唯一标准答案，必须用 rubric + LLM judge，并用人审校准 judge，否则指标不可信——这是 AI Engineer 面试的核心区分点。
- 在线反馈把「真实使用」变成「评测数据」，形成 badcase → 回归的闭环。

## 4. 本周在路线中的位置

```text
上周产出（W19）：v1.2（Postgres、认证、多空间、异步导入、自动部署）；data/scenarios/ 20 样例
        ↓
本周（W20）：scenario_spb.jsonl 20 条 + judge_scenario.v1.md + human_review CSV + run_scenario_eval.py
             隐式反馈（编辑 diff）+ Badcase 队列 + EvalRun 表 + 趋势页 + P3 评测报告 v1 → v1.3.0
        ↓
下周输入（W21）：安全攻击集复用同一 runner 框架与 EvalRun；badcase 分类法在 W22 合并
```

## 5. 每日安排

| Day   | 日期  | Task                                    | 当日 P0 产出                                                                      | 模块      | 状态 |
| ----- | ----- | --------------------------------------- | --------------------------------------------------------------------------------- | --------- | ---- |
| Day64 | 02-08 | Task 1：场景评测集 + rubric + 人审表    | `scenario_spb.jsonl` 20 条 + `judge_scenario.v1.md` + 评测报告 + 人审 10 条一致率 | M3        | TODO |
| Day65 | 02-09 | Task 2：在线反馈闭环 + 评测看板（v1.3） | 编辑 diff 入 Feedback + Badcase 队列页 + EvalRun + 趋势页 + tag `v1.3.0`          | M3.6 M4.4 | TODO |

## 6. 本周必须留下的资产

- `eval/datasets/scenario_spb.jsonl`
- `prompts/judge_scenario.v1.md`
- `eval/runners/run_scenario_eval.py`
- `eval/human_review/20270208.csv`
- `eval/reports/20270208-scenario-spb.md`、`eval/reports/20270209-p3-eval-v1.md`
- `apps/api/app/eval/feedback.py`（diff 计算）、`apps/api/app/routes/eval.py`（EvalRun / badcase 接口）
- `apps/web/src/pages/BadcaseQueuePage.tsx`、`apps/web/src/pages/EvalTrendPage.tsx`
- `scripts/export_regression.py`
- tag `v1.3.0`

## 7. 本周验收标准

- [ ] PASS / FAIL：数据集 20 条，字段齐全，全部来自已脱敏样例（二次检查通过）
- [ ] PASS / FAIL：评测只跑到 human_review 之前，**不创建任何 Issue**
- [ ] PASS / FAIL：报告含通过率、5 维度均分、失败用例列表、成本与耗时
- [ ] PASS / FAIL：人审 10 条，judge 一致率已计算（目标 ≥ 0.8；不达标需写调整措施）
- [ ] PASS / FAIL：审批编辑 diff 写入 Feedback（kind=implicit_edit）；Badcase 队列页可「提升」，导出脚本生成带 `regression` 标签的用例并经人工确认后提交
- [ ] PASS / FAIL：EvalRun 记录 ≥ 2 次，趋势页可见；`v1.3.0` 已部署

## 8. 求职映射

- 本周能力：生成式任务评测设计、LLM-as-a-judge、judge 校准、隐式反馈、数据飞轮。
- 简历 bullet 草稿：
  - 「为需求拆解场景设计 5 维 rubric 与 LLM judge，以 10 条人审校准，judge 一致率 **；20 条评测集通过率由 ** 提升到 \_\_」
  - 「将用户审批前的编辑 diff 作为隐式反馈信号，构建 badcase → 人工确认 → 回归用例闭环」
- 面试题：
  1. LLM judge 可信吗？怎么验证？（答要点：人审样本算一致率/Kappa；固定 judge 模型与 prompt 版本；给评分锚点示例；judge 不可信时降级为人审）
  2. 没有标准答案的生成任务怎么评？（答要点：must_cover / forbidden 硬规则 + rubric 软评分 + 人审抽样）
  3. 用户反馈怎么转化为改进？（答要点：显式 👍👎 + 隐式编辑；候选队列；人工确认脱敏后进回归集；修复后回归不退化）

## 9. 本周禁止事项

- 不引入 Ragas / DeepEval / Langfuse 等新评测平台（自研 runner 已够用）。
- 不为提高通过率而修改评测集标准（改 prompt / 流程，不改尺子）。
- 不让线上 API 直接写 git 仓库中的数据集文件。
- 评测运行不得调用写工具。

## 10. 时间不够时（最小保留）

- Day64：数据集 20 条 + judge prompt + 跑一次报告；人审可压到 5 条。
- Day65：编辑 diff 入库 + 导出脚本 + EvalRun 记录；页面只做 Badcase 队列（趋势页用报告表格代替）。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（预期：一键场景评测 + badcase 队列）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
