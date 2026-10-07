# Day 51 · 2026-12-30 · Week 14 Task 3：回归 + CI 门禁

## 0. 今天只做一件事

把 RAG + Agent 评测变成「改坏了会被拦下」的回归门禁：固化基线 → `compare_eval.py` 超阈值非零退出 → `make eval-smoke` 进 Gitea Actions；再修复一次头号失败类别，用 `eval-full` 证明提升。

不碰：新指标、新数据集、多模型横评、在 GitHub Actions 上跑带密钥的评测。

## 1. 资产锚点

- 构建模块：M3.5 回归 + 门禁（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v1.0 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：push 到 main 后 CI 自动跑 5 RAG + 5 Agent 小样本评测，退化即红；一份「修复前 vs 修复后」对比报告
- 今日 AI 实际应用：评测驱动开发（Eval-Driven Development）→ 作为 W15 所有生产化改动的安全网

## 2. 起点（前置确认）

- 已有：Day50 `eval/reports/20261229-agent-v0.9.summary.json`；W5 `run_rag_eval.py`；W7 `.gitea/workflows/ci.yml`（lint/test/build）+ act_runner
- 需确认：

```bash
cd ~/lab/workpilot
cat eval/reports/20261229-agent-v0.9.summary.json | jq .
uv run --project apps/api python eval/runners/run_rag_eval.py --help | grep -E "limit|ids|summary|judge"  # 是否支持子集与汇总输出
cat .gitea/workflows/ci.yml | head -30
cat ~/act_runner/config.yaml 2>/dev/null | grep -A5 labels   # runner 标签（路径按 W7 实际）
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `eval/baseline/rag.json`、`eval/baseline/agent.json` 存在，各含 `full` 与 `smoke` 两段指标 + 数据集/模型/commit 元信息
- [ ] `scripts/compare_eval.py`：正常 → 退出 0；故意退化 → 退出 1 并打印哪项超阈值（终端输出截图）
- [ ] `make eval-smoke`、`make eval-full`、`make eval-baseline` 可用
- [ ] Gitea Actions 中 `eval-smoke` job 运行并显示对比结果；LLM key 来自 secrets；单次成本估算写入报告
- [ ] 头号失败类别修复一次，`eval-full` 重跑，对比报告 `eval/reports/20261230-agent-v0.9.1.md` 显示该类数量下降
- [ ] 周复盘已写

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                               |
| ----------- | ------ | -------------------------------------------------- |
| 0–15 min    | P0     | 选 smoke 子集（稳定样本）+ 生成基线                |
| 15–40 min   | P0     | `compare_eval.py` + 退化演示                       |
| 40–65 min   | P0     | Makefile + CI job + secrets                        |
| 65–105 min  | P0     | 修复头号失败类别 → eval-full → 对比报告 → 更新基线 |
| 105–120 min | P0     | 提交 + 周复盘                                      |

时间不足时最低保留：baseline + `compare_eval.py` + 本地 `make eval-smoke`；CI 与修复顺延到 Day52 开头，并在周复盘记录。

## 5. 今日学习（只学完成任务必须的）

- **回归门禁 = 基线 + 阈值 + 非零退出码**：CI 只认退出码。
- **小样本统计陷阱**：5 条任务中 1 条翻转 = 20pt；smoke 门禁要用「硬约束 + 宽阈值」，细粒度阈值（-5pt）只用于 full。
- **smoke 样本要稳定**：选连续 3 次都通过的任务，否则 CI 天天误报。
- **密钥管理**：LLM key 只放 Gitea 仓库 Secrets，日志不打印；公开 GitHub 仓库不跑带密钥的评测。
- **基线只能显式更新**：改基线 = 一次有报告支撑的提交，不允许「为了让 CI 变绿改基线」。
- 资料：https://docs.gitea.com/usage/actions/overview （Gitea Actions，语法兼容 GitHub Actions）

## 6. 执行步骤

### Step 1 · 选 smoke 子集 + 生成基线

```bash
# 每类挑 1 条在 Day49/50 中通过的任务，连续跑 3 次，保留 3/3 通过的 5 条
uv run --project apps/api python eval/runners/run_agent_eval.py --ids kb-01 repo-01 research-02 bd-01 mt-01
```

`eval/baseline/agent.json`：

```json
{
  "version": "v0.9.0",
  "created": "2026-12-30",
  "model": "deepseek-chat",
  "dataset_commit": "<git rev-parse --short HEAD>",
  "smoke_ids": ["kb-01", "repo-01", "research-02", "bd-01", "mt-01"],
  "full": {
    "_copy_from": "Day50 summary：task_success_rate / tool_selection_acc / avg_steps / p95_ms / avg_cost_cny / forbidden_violations / unapproved_writes"
  },
  "smoke": {
    "task_success_rate": 1.0,
    "tool_selection_acc": 1.0,
    "forbidden_violations": 0,
    "unapproved_writes": 0,
    "errors": 0
  }
}
```

`eval/baseline/rag.json` 同结构（`hit_at_5`、`mrr`、`citation_acc`、`refusal_acc`；smoke 用 5 题、不跑 judge，只算检索指标）。数值从报告 summary 复制，不手填。

### Step 2 · `scripts/compare_eval.py`（核心逻辑自己写）

```python
"""对比当前评测汇总与基线，超阈值退出码 1。"""
import argparse, json, sys

# (指标, 规则, 阈值)：drop_pt=下降超过 N 个百分点；rise_pct=上升超过 N%；max=不得超过
RULES = {
    ("agent", "full"):  [("task_success_rate", "drop_pt", 5), ("tool_selection_acc", "drop_pt", 5),
                         ("avg_steps", "rise_pct", 30), ("p95_ms", "rise_pct", 30), ("avg_cost_cny", "rise_pct", 30),
                         ("forbidden_violations", "max", 0), ("unapproved_writes", "max", 0)],
    ("agent", "smoke"): [("task_success_rate", "drop_pt", 20), ("forbidden_violations", "max", 0),
                         ("unapproved_writes", "max", 0), ("errors", "max", 0)],
    ("rag", "full"):    [("hit_at_5", "drop_pt", 3), ("citation_acc", "drop_pt", 5), ("refusal_acc", "drop_pt", 5)],
    ("rag", "smoke"):   [("hit_at_5", "drop_pt", 20)],
}

def check(rule, base, cur, th):
    if rule == "drop_pt":  return (base - cur) * 100 <= th
    if rule == "rise_pct": return base == 0 or (cur - base) / base * 100 <= th
    if rule == "max":      return cur <= th

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["agent", "rag"]); ap.add_argument("--mode", choices=["full", "smoke"])
    ap.add_argument("--current", required=True)
    a = ap.parse_args()
    base = json.load(open(f"eval/baseline/{a.kind}.json"))[a.mode]
    cur = json.load(open(a.current))
    failed = 0
    for metric, rule, th in RULES[(a.kind, a.mode)]:
        ok = check(rule, base.get(metric, 0), cur.get(metric, 0), th)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {a.kind}.{a.mode}.{metric}: base={base.get(metric)} cur={cur.get(metric)} rule={rule}({th})")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
```

退化演示：临时把 `kb_search` 的 description 改成「用于数学计算」→ `make eval-smoke` → 应看到 `FAIL agent.smoke.task_success_rate` 且 `echo $?` 为 2（make 包装后的非零码）→ `git checkout` 恢复。截图保存。

### Step 3 · Makefile

```makefile
SMOKE_AGENT_IDS := kb-01 repo-01 research-02 bd-01 mt-01
SMOKE_RAG_IDS   := q01 q07 q15 q23 q41
PY := uv run --project apps/api python

eval-smoke:
	$(PY) eval/runners/run_rag_eval.py --ids $(SMOKE_RAG_IDS) --no-judge --summary eval/reports/latest/rag.smoke.json
	$(PY) eval/runners/run_agent_eval.py --ids $(SMOKE_AGENT_IDS) --summary eval/reports/latest/agent.smoke.json
	$(PY) scripts/compare_eval.py --kind rag --mode smoke --current eval/reports/latest/rag.smoke.json
	$(PY) scripts/compare_eval.py --kind agent --mode smoke --current eval/reports/latest/agent.smoke.json

eval-full:   ## 每周手动
	$(PY) eval/runners/run_rag_eval.py --summary eval/reports/latest/rag.full.json
	$(PY) eval/runners/run_agent_eval.py --summary eval/reports/latest/agent.full.json
	$(PY) scripts/compare_eval.py --kind rag --mode full --current eval/reports/latest/rag.full.json
	$(PY) scripts/compare_eval.py --kind agent --mode full --current eval/reports/latest/agent.full.json

eval-baseline:  ## 只在有报告支撑时手动执行
	$(PY) scripts/update_baseline.py --from eval/reports/latest
```

（`--summary` 参数：让 runner 在结束时调用 Day50 的 `aggregate()` 写汇总；`update_baseline.py` 约 15 行，AI 生成。`eval/reports/latest/` 加入 `.gitignore`。）

### Step 4 · CI job（`.gitea/workflows/ci.yml` 追加）

```yaml
eval-smoke:
  needs: [test]
  if: github.ref == 'refs/heads/main'
  runs-on: workpilot-host # act_runner 的 host 模式标签：能访问本机 Qdrant/Ollama 与已索引知识库
  timeout-minutes: 15
  env:
    LLM_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    LLM_MODEL: deepseek-chat # smoke 用便宜模型
    TOOLS_WRITE_MODE: mock
    LLM_TEMPERATURE: "0"
  steps:
    - uses: actions/checkout@v4
    - run: make eval-smoke
    - if: always()
      uses: actions/upload-artifact@v3 # Gitea 目前不支持 v4
      with: { name: eval-smoke, path: eval/reports/latest/ }
```

- Secrets：Gitea 仓库 → 设置 → Actions → Secrets 新增 `DEEPSEEK_API_KEY`（变量名按 Gateway 实际读取的 env 改）。
- Runner 标签：在 act_runner `config.yaml` 的 `labels` 增加 `workpilot-host:host` 后重启 runner。
- 成本估算（写进 Day51 报告）：`单次 ≈ 5×Agent 平均成本 + 5×judge(≈1.5k tokens) + 5×RAG 检索(仅 embedding，本地 0 元)`，按 Day50 报告平均成本代入，预计 ¥**/次；每周 push 约 ** 次 → ¥\_\_/周。

### Step 5 · 修复头号失败类别（自己判断，AI 辅助改）

| 头号类别               | 典型修复（选 1 个，最小改动）                                                          |
| ---------------------- | -------------------------------------------------------------------------------------- |
| wrong_tool             | 改工具 description：写清「何时用 / 何时不用」，`ext.fs.*` 前缀明确「本机公开文档目录」 |
| bad_args               | 参数加 enum/pattern/默认值；错误信息返回可行动提示（如「path 应相对仓库根」）          |
| early_stop             | planner prompt 要求「对照任务要求逐项检查后再结束」→ `prompts/planner.v2.md`           |
| loop                   | decide 节点加「同一工具同参数重复 2 次即结束」规则                                     |
| citation_hallucination | synthesize 只允许引用 observations 中的来源 id                                         |
| tool_error_unrecovered | 工具错误时把错误信息作为 observation 交回 planner，允许 1 次换参重试                   |

```bash
make eval-full        # 重跑全量（约 __ 分钟）
uv run --project apps/api python eval/runners/eval_agent_report.py --run $(ls -d eval/runs/eval-* | tail -1) \
  --out eval/reports/20261230-agent-v0.9.1 --compare eval/reports/20261229-agent-v0.9.summary.json
make eval-baseline    # 只有指标确实变好时才更新
```

对比报告至少包含：头号类别数量（前→后）、任务成功率、工具选择准确率、平均成本（前→后）。

### Step 6 · 提交

```bash
git add eval/baseline scripts/compare_eval.py scripts/update_baseline.py Makefile .gitea/workflows/ci.yml \
  eval/reports/20261230-agent-v0.9.1.md prompts apps/api .gitignore
git commit -m "ci(eval): add eval baselines, regression compare and eval-smoke gate"
git push      # 观察 Gitea Actions 中 eval-smoke 结果
```

### Step 7 · 周复盘

填写 `plan/phase_02/week_14/README.md` 第 11 节与第 7 节 PASS/FAIL。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 smoke 门禁阈值比 full 宽？（答：5 条样本 1 条翻转就是 20pt，细阈值会导致大量误报；smoke 负责拦截「明显坏掉」，细粒度回归交给每周 full）
2. 哪些指标是硬约束（阈值 0）？（答：未审批写操作、forbidden 违规、运行错误——这些是安全与可用性红线，不允许任何退化）
3. 什么时候可以更新基线？（答：有完整 eval-full 报告证明整体变好或有意取舍（如成本换质量）并写明原因时，显式执行并单独提交）
4. 为什么不在公开 GitHub 仓库的 Actions 上跑评测？（答：需要 LLM 密钥且依赖本地向量库；公开仓库的 fork PR 等场景存在密钥泄露与成本滥用风险）
5. 评测驱动开发的循环是什么？（答：看失败分类 → 选头号类别 → 最小改动 → 重跑评测 → 对比 → 更新基线 → 门禁保护）

## 8. 对 DA-01 的贡献

WorkPilot 拥有自动化质量门禁（M3.5）：W15 的 Trace、预算、限流、护栏等改动都能被证明「没有让 Agent 变差」；第一次「修复 → 重跑 → 数字提升」的闭环，是 P2 作品集与技术文章最有说服力的故事。

## 9. 求职映射（D 线）

- 岗位能力：回归测试、CI 质量门禁、评测成本控制、评测驱动优化
- 对应岗位：AI Platform Engineer / AI Agent Engineer / LLMOps
- 简历 bullet 草稿：将 RAG + Agent 小样本评测接入 Gitea Actions 回归门禁（单次约 ¥**、** 分钟），基于失败分类修复「**」问题，Agent 任务成功率由 ** 提升至 \_\_。
- 面试可能问：
  - LLM 应用的 CI 怎么做才不 flaky？（要点：temperature=0、稳定样本、硬约束 + 宽阈值、full 定期跑、失败时上传轨迹便于排查）
  - 你怎么平衡评测成本与覆盖？（要点：分层：每次 push smoke、每周 full、发布前 full + 人工抽查；便宜模型跑 smoke）

## 10. 卡住时的处理

| 现象                             | 处理                                                                                       |
| -------------------------------- | ------------------------------------------------------------------------------------------ |
| CI job 一直 pending              | runner 没有 `workpilot-host` 标签；检查 `config.yaml` labels 并重启 act_runner             |
| CI 中连不上 Qdrant               | runner 是 docker 模式时 `localhost` 指向容器，改 host 模式或用 `host.docker.internal:6333` |
| `upload-artifact` 报不支持       | Gitea 用 `actions/upload-artifact@v3`；仍报错则删掉该步，改为 `cat` 汇总 JSON              |
| smoke 本地通过、CI 偶发失败      | 看上传的轨迹；把不稳定任务换掉，记录到 badcases，而不是放宽硬约束                          |
| 修复后头号类别下降但其他类别上升 | 照实写进对比报告；整体退化则不更新基线，回滚修改                                           |
| 超过 120 分钟                    | CI 接入与修复顺延 Day52 开头 30 分钟，周复盘写明                                           |

## 11. 产出记录（执行时填写）

- smoke 子集与 3 次稳定性结果：\_\_\_\_
- 退化演示截图 / 退出码：\_\_\_\_
- CI 运行链接 / 耗时 / 单次成本：\_\_\_\_
- 修复的类别、改动、前后数字：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 14 DONE → 明天进入 Day52（W15 Task 1：Trace / Span + Trace 查看）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
