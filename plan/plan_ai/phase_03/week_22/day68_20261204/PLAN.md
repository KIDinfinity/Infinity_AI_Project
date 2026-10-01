# Day 68 · 2026-12-04 · Week 22 Task 1：Badcase 总库 + 回归套件 + Eval v2

## 0. 今天只做一件事

把四类 badcase 合并成一个有分类法和状态的总库，把已修复项全部变成 regression 用例，用 `make eval-all` 生成展示 v0.5 → v1.0 → v2.0 趋势的 Eval v2 报告，并让 CI 门禁覆盖四类冒烟集。

不碰：模板库与 Pro Kit（Day69）、新评测指标、新评测框架、为提分改评测集。

## 1. 资产锚点

- 构建模块：M3.4 Badcase 库、M3.5 回归 + 门禁（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：v2.0（评测部分）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make eval-all` → `eval/reports/20261204-eval-v2.md`（四类指标 + 三版本趋势 + badcase 统计）；CI 对质量回退报红
- 今日 AI 实际应用：Badcase 驱动优化的完整闭环（发现 → 分类 → 根因 → 修复 → 回归 → 门禁）在全部 AI 能力上统一

## 2. 起点（前置确认）

- 已有：`eval/badcases/badcases.md`（W5 起）；`eval/datasets/{kb_qa, tool_selection, agent_tasks, scenario_spb, security}.jsonl`；四个 runner；`compare_eval.py`；EvalRun（含回填的 v0.5 / v1.0）；CI `make eval-smoke`。
- 需确认：

```bash
cd ~/lab/workpilot
wc -l eval/datasets/*.jsonl
grep -c "^|" eval/badcases/badcases.md                      # 旧 badcase 行数（大约）
ls eval/reports/ | grep -iE "baseline|v0\.5|v1\.0"          # 三版本数据来源
grep -n "eval-smoke" -A8 Makefile .gitea/workflows/ci.yml
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `eval/badcases/README.md`：分类法（≥ 10 类，按来源分组）+ 状态机（open → root_caused → fixed → regression_added / wontfix）
- [ ] `eval/badcases/badcases.jsonl`：合并 RAG / Agent / 场景 / 安全，每条有 id、source、category、status、found_in
- [ ] 所有 `status ∈ {fixed, regression_added}` 的条目都有 `regression_case_id`，且该用例在数据集中带 `"regression"` 标签
- [ ] `make eval-all` 运行四类全量评测，生成 `eval/reports/20261204-eval-v2.md`（含 v0.5 / v1.0 / v2.0 对比表）与 `eval/badcases/summary.md`
- [ ] CI `eval-smoke` 覆盖 rag（10）+ agent（5）+ scenario（3）+ security（20），低于阈值失败
- [ ] 故意改坏一个 prompt 的分支 → CI 红（截图或日志链接记录），然后丢弃该分支

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                       |
| ----------- | ------ | ---------------------------------------------------------- |
| 0–15 min    | P0     | 分类法 + 状态机 README                                     |
| 15–40 min   | P0     | 迁移脚本 + 人工补字段 → badcases.jsonl                     |
| 40–55 min   | P0     | fixed 项 → regression 用例（补 tags / 新增用例）           |
| 55–80 min   | P0     | run_all.py + 报告生成（三版本对比）                        |
| 80–95 min   | P0     | 跑 `make eval-all`（后台跑，同时做下一步）                 |
| 95–110 min  | P1     | CI 门禁四类冒烟 + 坏改动验证                               |
| 110–120 min | P0     | 提交                                                       |
| 顺延        | P2     | badcase 看板页面、按类别自动聚类、mermaid 趋势图 → Backlog |

时间不足时最低保留：总库 + regression 标签 + `make eval-all` + 报告；CI 先加 security 冒烟。

## 5. 今日学习（只学完成任务必须的）

- **分类法要可行动**：类别对应「修哪里」（检索 / 分块 / 生成 / 工具 / 流程 / 安全），而不是「看起来哪里怪」。
- **回归集 vs 基准集**：基准集衡量整体水平（base），回归集锁住已修复问题（regression）；两者分开统计，防止「为回归集过拟合」看不出来。
- **冒烟集控成本**：CI 每次跑全量既慢又花钱；冒烟集取每类高风险 + 回归用例子集，全量在发版前 / 每周跑。
- **门禁阈值**：相对基线下降超过容忍值（如通过率 -5%）或安全 < 100% 即失败；阈值写在配置里，变更要提交说明。
- 资料：https://jsonlines.org/ 、https://docs.gitea.com/usage/actions/overview

## 6. 执行步骤

### Step 1 · 分类法 + 状态机（P0）

`eval/badcases/README.md`：

```markdown
# Badcase 分类法 v2（2026-12-04）

| 来源     | category          | 含义                  | 通常修复位置                  |
| -------- | ----------------- | --------------------- | ----------------------------- |
| rag      | retrieval_miss    | 相关片段未召回        | 分块 / hybrid / 查询改写      |
| rag      | chunk_boundary    | 答案被切断在两个块    | chunking 参数                 |
| rag      | hallucination     | 回答含知识库外内容    | prompt / 拒答阈值             |
| rag      | citation_wrong    | 引用编号与内容不符    | answer 组装                   |
| rag      | refuse_wrong      | 应答却拒答 / 应拒却答 | 拒答策略                      |
| agent    | tool_select_wrong | 选错工具              | 工具描述 / planner prompt     |
| agent    | tool_args_wrong   | 参数错误              | schema / 示例                 |
| agent    | loop_or_overrun   | 步数超限 / 循环       | max_steps / 终止条件          |
| scenario | coverage_gap      | 漏需求要点            | breakdown prompt / self_check |
| scenario | granularity       | 任务过大或过碎        | 规范 KB / prompt 规则         |
| scenario | untestable_ac     | 验收标准不可测        | prompt 规则 / self_check      |
| security | injection_bypass  | 注入导致越权行为      | policy / 输出过滤             |
| security | data_leak         | 跨空间 / PII / 外传   | 检索断言 / redact             |
| any      | format_invalid    | 结构化输出失败        | schema / 重试                 |
| any      | cost_latency      | 超预算 / 超时         | 模型路由 / 上下文裁剪         |

状态：open → root_caused → fixed → regression_added（终态）；或 wontfix（必须写理由）。
```

### Step 2 · 合并为 badcases.jsonl（P0）

字段：

```json
{
  "id": "BC-031",
  "source": "scenario",
  "category": "untestable_ac",
  "title": "导出任务的验收标准写成『功能正常』",
  "input_ref": "scenario_spb.jsonl#spb-004",
  "found_in": "v1.1.0",
  "root_cause": "prompt 未要求可观察结果",
  "fix_ref": "commit a1b2c3d (breakdown.v2)",
  "status": "regression_added",
  "regression_case_id": "spb-004"
}
```

可让 AI 写一次性迁移脚本 `scripts/migrate_badcases.py`：解析旧 `badcases.md` 表格 + 安全基线失败清单 + W20 promoted 记录 → JSONL 初稿；**category / root_cause / status 必须人工确认**。旧 `badcases.md` 改为一行说明「已迁移至 badcases.jsonl」。

> 公开仓库：badcase 只描述现象与根因，不含任何原始敏感输入（输入通过 `input_ref` 指向已脱敏数据集）。

### Step 3 · regression 用例（P0）

```bash
# 列出 fixed 但没有回归用例的条目
jq -c 'select((.status=="fixed" or .status=="regression_added") and (.regression_case_id|not))' eval/badcases/badcases.jsonl
```

对每条：若输入已在数据集里 → 给该用例 `tags` 加 `"regression"`；若不在 → 新增一条用例（W20 导出脚本可复用）。完成后把 status 改为 `regression_added`。

各 runner 支持 `--tags regression`（W20 已在场景 runner 实现，照抄到其他三个）。

### Step 4 · run_all + Eval v2 报告（P0，汇总逻辑自己写）

```python
# eval/runners/run_all.py
import json, subprocess, datetime as dt
from pathlib import Path

SUITES = {
    "rag":      ["python", "eval/runners/run_rag_eval.py", "--json-out", "/tmp/rag.json"],
    "agent":    ["python", "eval/runners/run_agent_eval.py", "--json-out", "/tmp/agent.json"],
    "scenario": ["python", "eval/runners/run_scenario_eval.py", "--json-out", "/tmp/scenario.json"],
    "security": ["python", "eval/runners/run_security_eval.py", "--json-out", "/tmp/security.json"],
}
KEYS = {"rag": ["hit@5", "citation_acc", "refusal_acc", "p95_latency_s"],
        "agent": ["task_success", "tool_select_acc", "avg_steps"],
        "scenario": ["pass_rate"], "security": ["block_rate"]}

def load_history():  # 从 EvalRun 取 v0.5.x / v1.0.x 最近一次（W20 已回填）
    ...

def main(smoke: bool = False):
    now = {}
    for name, cmd in SUITES.items():
        subprocess.run(cmd + (["--smoke"] if smoke else []), check=True)
        now[name] = json.loads(Path(f"/tmp/{name}.json").read_text())["metrics"]
    hist = load_history()
    lines = ["# Eval v2 报告（" + dt.date.today().isoformat() + "）", "",
             "| 套件 | 指标 | v0.5 | v1.0 | v2.0 | §11 目标 |", "|---|---|---|---|---|---|"]
    for suite, keys in KEYS.items():
        for k in keys:
            lines.append(f"| {suite} | {k} | {hist.get('v0.5',{}).get(suite,{}).get(k,'—')} | "
                         f"{hist.get('v1.0',{}).get(suite,{}).get(k,'—')} | {now[suite].get(k)} | {TARGETS.get(k,'')} |")
    Path("eval/reports/20261204-eval-v2.md").write_text("\n".join(lines) + "\n" + badcase_summary())
```

> 若现有 runner 输出格式不统一，今天只加一个 `--json-out` 参数输出 `{"metrics": {...}}`，不重构 runner。v0.5 时还没有 Agent / 场景 / 安全，对应格写「—」，这本身就是成长证据。

`badcase_summary()`：按 source × status 计数、按 category Top5 —— 同时写 `eval/badcases/summary.md`。

```make
eval-all:
	uv run --directory apps/api python ../../eval/runners/run_all.py
eval-smoke:
	uv run --directory apps/api python ../../eval/runners/run_all.py --smoke
```

报告末尾人工补 3 段（不超过 15 行）：最大提升来自哪里、仍未达标的指标与原因、下一步（进入 DA-02 / Backlog）。

### Step 5 · CI 门禁（P1）

`eval/gate.yaml`：

```yaml
rag: { "hit@5": { min: 0.80 }, citation_acc: { min: 0.75 } }
agent: { task_success: { min: 0.65 }, tool_select_acc: { min: 0.80 } }
scenario: { pass_rate: { min: 0.67 } } # 冒烟 3 条至少 2 条通过
security: { block_rate: { min: 1.0 } }
```

`compare_eval.py` 读取冒烟结果与 gate.yaml，任一不满足 `exit 1`。`.gitea/workflows/ci.yml` 的 eval 步骤改为 `make eval-smoke && python eval/runners/compare_eval.py --gate eval/gate.yaml`，LLM key 来自 secrets。

验证：

```bash
git switch -c test/break-gate
sed -i '' 's/每个任务至少 1 条可测试的验收标准/验收标准可省略/' apps/api/app/scenarios/sp_b_req_breakdown/prompts/breakdown.v1.md
git commit -am "test: break gate on purpose" && git push -u origin test/break-gate   # 观察 CI 红
git switch main && git push origin --delete test/break-gate && git branch -D test/break-gate
```

### Step 6 · 提交

```bash
git add eval/badcases eval/runners eval/gate.yaml eval/reports/20261204-eval-v2.md eval/datasets Makefile .gitea/workflows/ci.yml scripts/migrate_badcases.py
git commit -m "feat(eval): unified badcase library, regression suites, eval-all v2 report and CI gate"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么分类法要对应「修复位置」？（答：分类的目的是指导行动；按修复位置分类才能统计出该投入优化哪一层）
2. 回归集和基准集为什么分开统计？（答：回归集是已知问题，容易过拟合；分开才能看到整体能力是否真实提升）
3. CI 为什么只跑冒烟集？（答：控制时间和 LLM 成本；全量在发版前/定期跑）
4. 安全冒烟为什么阈值是 1.0 而其他是相对容忍？（答：安全是护栏，任何一条失败都是阻断；质量指标有自然波动）
5. 「为提分改评测集」为什么是禁区？（答：尺子变了，趋势失去意义；只能新增用例或修正明显错误标注，并记录原因）

## 8. 对 DA-01 的贡献

WorkPilot 拥有覆盖全部 AI 能力的评测与回归体系：每次改动都能回答「变好了还是变差了」，且已修复的问题不会悄悄复发。Eval v2 报告是 v2.0 发布与 P1–P3 作品集 Evaluation / Optimization / Result 节的共同数据源。

## 9. 求职映射（D 线）

- 岗位能力：评测体系设计、回归测试、CI 质量门禁、Badcase 驱动优化。
- 对应岗位：AI Engineer、LLM Engineer、AI Platform Engineer。
- 简历 bullet 草稿：「建立四类评测（RAG / Agent / 场景 / 安全）与统一 badcase 库（** 条，** 类），** 条已修复问题转为回归用例并由 CI 门禁守护；v0.5 → v2.0：hit@5 ** → **、任务成功率 ** → **、攻击拦截率 ** → 1.0」
- 面试可能问：
  1. 讲一个你通过 badcase 发现系统性问题的例子。——要点：按类别统计发现某类集中（如 untestable_ac），定位到 prompt 缺规则，修复后该类下降 \_\_，转回归防复发。
  2. LLM 评测结果有波动，门禁怎么设？——要点：temperature 0、固定 judge 版本、冒烟集选稳定用例、阈值留容忍、失败时重跑一次确认。

## 10. 卡住时的处理

| 现象                               | 处理                                                                                            |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- |
| 旧 badcases.md 格式混乱解析失败    | 不写复杂解析；让 AI 一次性转换为 JSONL 草稿，人工逐条校对                                       |
| 历史版本指标缺失                   | 从当时报告手工抄入 EvalRun；确实没有的写「—」并在报告说明                                       |
| `make eval-all` 太慢 / 太贵        | 先 `--smoke` 验证流程；全量放到后台跑，期间做 CI 配置                                           |
| CI 中 LLM 调用失败（无网络 / key） | 确认 runner 能访问外网与 secrets 注入；必要时 scenario 冒烟改为非 CI 的发版前检查，并在报告注明 |
| 门禁在 main 上就红                 | 说明当前指标低于阈值：先如实记录，阈值设为当前基线 - 容忍值，不得为过门禁删用例                 |
| 时间不够                           | CI 只加 security 冒烟（确定性高、便宜），其余顺延                                               |

## 11. 产出记录（执行时填写）

- badcase 总数：**（rag ** / agent ** / scenario ** / security **）；regression_added **；wontfix \_\_
- 新增 regression 用例：\_\_ 条
- Eval v2 关键指标（v0.5 → v1.0 → v2.0）：\_\_\_\_
- CI 门禁验证：红 / 未验证
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day69 · W22 Task 2「抽取模板库 + Pro Kit 打包（v2.0）」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（总库 / regression / eval-all 报告）。
