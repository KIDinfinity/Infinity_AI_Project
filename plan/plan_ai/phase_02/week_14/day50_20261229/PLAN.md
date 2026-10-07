# Day 50 · 2026-12-29 · Week 14 Task 2：Agent 评测器 + 报告

## 0. 今天只做一件事

把 Day49 的 30 份轨迹变成一份 Agent 评测报告：规则指标（工具选择 P/R、违规、工具成功率、步数、P50/P95、成本）+ LLM-judge 任务成功率（先人工标 8 条校准），并按 6 类失败分类，Agent badcases 入库。

不碰：修 Agent（Day51 只修头号问题）、基线与 CI（Day51）、扩充数据集。

## 1. 资产锚点

- 构建模块：M3.3 Agent 指标、M3.4 Badcase 库（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v1.0 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`eval/reports/20261229-agent-v0.9.md`——P2 第一组可公开的 Agent 数字；一个可复用的 `summary.json` 给 Day51 做基线
- 今日 AI 实际应用：LLM-as-a-judge + 人工校准 → 判定 WorkPilot Agent 的任务是否真正完成

## 2. 起点（前置确认）

- 已有：`eval/runs/<tag>/` 30 份轨迹；W5 的 RAG judge（`prompts/judge_*.md` + 调用方式）
- 需确认：

```bash
cd ~/lab/workpilot
RUN=$(ls -d eval/runs/eval-* | tail -1); echo $RUN; ls $RUN | wc -l      # 应为 30
jq '{id, n_tools: (.tool_calls|length), err: .error, cost: .cost_cny}' $RUN/kb-01.json
ls prompts/ | grep judge
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `agent_metrics.py` 输出 7 项指标：工具选择准确率（及 macro P/R）、forbidden 违规数、未审批写操作数、工具成功率、任务成功率、平均步数、P50/P95 延迟、平均成本
- [ ] `prompts/judge_agent.v1.md` 存在，judge 输出可解析 JSON，30 条全部打分
- [ ] 8 条人工标注存在，judge 与人工 pass/fail 一致 ≥ 6/8（或记录不一致原因并修订 rubric 后重测）
- [ ] 报告 `eval/reports/20261229-agent-v0.9.md` 含指标表、分类别表、失败分类表、Top 3 问题
- [ ] `eval/badcases/badcases.md` 新增 Agent 条目 ≥ 5；已提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                   |
| ----------- | ------ | -------------------------------------- |
| 0–10 min    | P0     | 定义指标口径（写进报告头部）           |
| 10–40 min   | P0     | `agent_metrics.py` 规则指标            |
| 40–65 min   | P0     | judge prompt + 调用 + 30 条打分        |
| 65–85 min   | P0     | 人工标 8 条 → 一致率 → 必要时修 rubric |
| 85–110 min  | P0     | 报告 + 失败分类 + badcases             |
| 110–120 min | P0     | 提交                                   |

时间不足时最低保留：规则指标 + judge 打分 + 报告指标表；校准减为 5 条；失败分类只标主类别。

## 5. 今日学习（只学完成任务必须的）

- **工具选择**：precision = |调用∩期望| / |调用|，recall = |调用∩期望| / |期望|；「工具选择准确率」口径 = recall=1 且无 forbidden 违规的任务占比（对齐 DA01 §11 ≥ 0.85）。
- **任务成功** 不能只靠规则：答案是否完整、事实是否覆盖、引用是否来自真实工具结果，需要 judge；judge 只看「任务 + 必含事实 + 工具观察 + 答案」，不看期望工具，避免混淆维度。
- **judge 校准**：先人工标少量样本，比较 pass/fail 一致率；不一致时修 rubric（加锚点示例），不改人工标签迁就 judge。
- **P95** 小样本下用最近秩法（nearest-rank），30 条时 P95≈第 29 名，报告中注明样本量。
- 资料：https://langchain-ai.github.io/langgraph/ （评估相关概念可参考 Agent 文档）、W5 自己的 RAG judge 实现

## 6. 执行步骤

### Step 1 · 规则指标 `eval/runners/agent_metrics.py`（核心口径自己写）

```python
import json, math
from pathlib import Path

WRITE_TOOLS = {"gitea_issue_create"}

def pctl(xs, p):
    xs = sorted(xs)
    return xs[max(0, math.ceil(p / 100 * len(xs)) - 1)] if xs else 0

def task_metrics(task: dict, traj: dict) -> dict:
    called = [c["name"] for c in traj.get("tool_calls", [])]
    c, e, f = set(called), set(task["expected_tools"]), set(task["forbidden_tools"])
    precision = len(c & e) / len(c) if c else (1.0 if not e else 0.0)
    recall = len(c & e) / len(e) if e else 1.0
    violations = sorted(c & f)
    writes = sum(1 for n in called if n in WRITE_TOOLS)
    unapproved = max(0, writes - len(traj.get("approvals", [])))
    ok_calls = sum(1 for x in traj.get("tool_calls", []) if x.get("ok"))
    return {
        "id": task["id"], "category": task["category"], "called": called,
        "precision": precision, "recall": recall, "violations": violations,
        "tool_select_ok": recall == 1.0 and not violations,
        "unapproved_writes": unapproved,
        "approval_expected_missing": task["requires_approval"] and not traj.get("approvals"),
        "tool_calls": len(called), "tool_ok": ok_calls,
        "steps": len(called), "step_overrun": len(called) > task["max_steps"],
        "latency_ms": traj.get("latency_ms", 0), "cost_cny": traj.get("cost_cny", 0.0),
        "error": traj.get("error"),
    }

def aggregate(rows: list[dict]) -> dict:
    n = len(rows); calls = sum(r["tool_calls"] for r in rows) or 1
    return {
        "n": n,
        "tool_selection_acc": sum(r["tool_select_ok"] for r in rows) / n,
        "tool_precision": sum(r["precision"] for r in rows) / n,
        "tool_recall": sum(r["recall"] for r in rows) / n,
        "forbidden_violations": sum(len(r["violations"]) for r in rows),
        "unapproved_writes": sum(r["unapproved_writes"] for r in rows),
        "tool_success_rate": sum(r["tool_ok"] for r in rows) / calls,
        "task_success_rate": sum(r.get("judge_pass", False) for r in rows) / n,
        "avg_steps": sum(r["steps"] for r in rows) / n,
        "p50_ms": pctl([r["latency_ms"] for r in rows], 50),
        "p95_ms": pctl([r["latency_ms"] for r in rows], 95),
        "avg_cost_cny": sum(r["cost_cny"] for r in rows) / n,
    }
```

### Step 2 · Judge rubric `prompts/judge_agent.v1.md`

```markdown
# judge_agent v1（2026-12-29）

你是严格的评审。根据【任务】【必含事实】【工具观察摘要】【Agent 最终答案】打分，只输出 JSON。
维度（各 0/1/2）：

- completeness：0=未完成或答非所问；1=部分完成；2=完整完成任务所有要求（数量、格式、动作）
- fact_coverage：0=必含事实覆盖 <50%；1=50–99%；2=全部覆盖（同义表达算覆盖）
- citation_faithfulness：0=出现工具观察中不存在的来源或事实；1=有引用但部分无法对应；2=所有关键结论可在工具观察中找到
  锚点：拒答任务中，明确说明「知识库中没有找到」且未编造 → completeness=2。
  输出：{"completeness":0,"fact_coverage":0,"citation_faithfulness":0,"missing_facts":[],"reason":"≤50字"}
```

判定规则（写在报告口径中）：`pass = 总分 ≥ 5 且 fact_coverage ≥ 1 且 无 forbidden 违规 且 无运行错误`。

### Step 3 · 报告脚本 `eval/runners/eval_agent_report.py`（样板 AI 生成，judge 调用复用 Gateway）

```python
# 关键流程（伪代码约 40 行，由 AI 补全）：
# 1. 读 dataset + run 目录下 30 个轨迹
# 2. rows = [task_metrics(t, traj)]
# 3. 对每条：obs = 工具结果前 300 字 × 最多 5 条；调用 gateway.structured(
#        prompt=judge_agent.v1, schema=JudgeOut, temperature=0, model=settings.judge_model)
#    写回 row["judge"], row["judge_pass"]
# 4. row["failure"] = classify(row, traj)（见 Step 5）
# 5. summary = aggregate(rows) → 写 eval/reports/20261229-agent-v0.9.summary.json
# 6. 渲染 Markdown 报告（Step 6 模板）
```

```bash
uv run --project apps/api python eval/runners/eval_agent_report.py --run $RUN --out eval/reports/20261229-agent-v0.9
```

### Step 4 · 人工校准 8 条

挑 8 条（judge 判 pass 4 条 + fail 4 条，覆盖 5 类），**先不看 judge 分数**自己打分，写 `eval/calibration/agent_judge_human.jsonl`：

```jsonl
{"id":"kb-01","human_pass":true,"completeness":2,"fact_coverage":2,"citation_faithfulness":2,"note":""}
{"id":"mt-01","human_pass":false,"completeness":1,"fact_coverage":0,"citation_faithfulness":1,"note":"只读了 runbook，没读 backup.sh"}
```

一致率 = pass/fail 相同的条数 / 8。< 6/8 时：看分歧条目 → 在 rubric 加锚点示例 → 文件头改为 v1.1 并记录 → 只重跑 judge（不重跑 Agent）。

### Step 5 · 失败分类（规则给初判，人工确认）

| 类别              | 代码                   | 初判规则                                                  |
| ----------------- | ---------------------- | --------------------------------------------------------- |
| 选错工具          | wrong_tool             | recall<1 且调用了非期望工具，或有 forbidden 违规          |
| 参数错误          | bad_args               | 有工具调用 ok=False 且错误含 validation / 404 / not found |
| 死循环 / 步数超限 | loop                   | step_overrun 或 error 含 recursion                        |
| 过早结束          | early_stop             | recall<1 且 tool_calls ≤ 1 且有答案                       |
| 引用幻觉          | citation_hallucination | judge.citation_faithfulness = 0                           |
| 工具错误未恢复    | tool_error_unrecovered | 某工具失败后无同名重试/替代工具，且任务 fail              |

每个失败任务只取一个**主类别**（按表中顺序优先）。

### Step 6 · 报告与 badcases

`eval/reports/20261229-agent-v0.9.md` 模板：

```markdown
# Agent 评测报告 · v0.9 · 2026-12-29

- 数据集：agent_tasks.jsonl（30 条，commit **）｜模型：**（temperature=0）｜judge：judge_agent.v1，人工一致率 \_\_/8

## 1. 总体

| 指标                          | 值              | 目标(DA01 §11) |
| ----------------------------- | --------------- | -------------- |
| 任务成功率                    | \_\_            | ≥ 0.70         |
| 工具选择准确率（macro P / R） | **（** / \_\_） | ≥ 0.85         |
| forbidden 违规 / 未审批写操作 | ** / **         | 0 / 0          |
| 工具成功率                    | \_\_            | —              |
| 平均步数                      | \_\_            | ≤ 6            |
| P50 / P95 延迟                | **s / **s       | —              |
| 平均成本                      | ¥\_\_           | —              |

## 2. 分类别（5 类 × 成功率/工具准确率/步数）

## 3. 失败分类（类别 | 数量 | 任务 id | 典型根因）

## 4. Top 3 问题与下一步（Day51 修复头号类别）
```

`eval/badcases/badcases.md` 追加 Agent 条目（≥ 5）：`| id | 类别 | 现象 | 根因假设 | 修复状态 | 回归用例 |`。

### Step 7 · 提交

```bash
git add eval/runners prompts/judge_agent.v1.md eval/calibration eval/reports eval/badcases
git commit -m "feat(eval): agent metrics, calibrated LLM judge and v0.9 agent eval report"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 工具选择 precision 低、recall 高说明什么？（答：该用的工具都用了，但调用了多余工具，通常是成本/步数问题而非正确性问题）
2. 为什么 judge 不看 expected_tools？（答：judge 评结果质量，工具选择由规则评；混在一起会让 judge 惩罚合理的替代路径）
3. judge 和人工不一致时，该改哪边？（答：先确认人工标注是否合理，然后改 rubric（锚点、定义），不为迁就 judge 改人工标签）
4. 30 条样本的 P95 有多可靠？（答：只有约 1–2 个样本决定 P95，波动大；报告需注明样本量，回归阈值要留容差）
5. 「未审批写操作」怎么从轨迹判断？（答：写工具调用次数 > 审批事件数，或写工具执行前没有 interrupt 事件）

## 8. 对 DA-01 的贡献

WorkPilot 第一次有了 Agent 的「体检报告」：P2 三个硬指标（成功率、工具准确率、步数）有了真实数值，失败被分类成可行动的问题；`summary.json` 是 Day51 回归门禁的基线输入，也是 Day55 作品集评测表的数据来源。

## 9. 求职映射（D 线）

- 岗位能力：Agent 指标设计、LLM-as-a-judge 校准、错误分析
- 对应岗位：AI Agent Engineer / Applied AI Engineer / LLM Evaluation 方向
- 简历 bullet 草稿：构建轨迹级 Agent 评测器（工具选择 P/R、违规调用、任务成功率、P95、成本）与经人工校准（一致率 **/8）的 LLM-judge，定位 ** 类主要失败模式。
- 面试可能问：
  - LLM-as-a-judge 有哪些偏差？怎么缓解？（要点：位置/冗长/自我偏好偏差；rubric 锚点、结构化输出、temperature=0、人工校准、必要时换不同模型做 judge）
  - Agent 失败最常见的原因是什么？（要点：用自己的失败分类表数据回答，并说出修复方式）

## 10. 卡住时的处理

| 现象                    | 处理                                                                             |
| ----------------------- | -------------------------------------------------------------------------------- |
| judge 输出不是合法 JSON | 用 Gateway 的 structured 输出 + Pydantic schema；失败重试 1 次后记为 judge_error |
| judge 普遍打高分        | rubric 中加入 0 分锚点示例；把「工具观察摘要」作为唯一可信来源强调               |
| 轨迹中 cost 全是 0      | Day49 的 request_id 未写入 llm_calls.jsonl；先补 Gateway 记录，再只重算 usage    |
| 人工标注耗时太久        | 只标 pass/fail + 一句理由，维度分可省                                            |
| 失败类别难以判断        | 先按规则初判，标「待确认」，Day51 修复前再看 3 条最典型的                        |
| 报告数字很难看          | 照实写；v0.9 是基线，Day51 和 W15 的价值就是让它变好                             |

## 11. 产出记录（执行时填写）

- 任务成功率 / 工具选择准确率 / 平均步数：\_\_\_\_
- P50 / P95 / 平均成本：\_\_\_\_
- 未审批写操作：\_\_\_\_
- judge 人工一致率：\_\_\_\_
- 头号失败类别及数量：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day51（W14 Task 3：回归 + CI 门禁）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
