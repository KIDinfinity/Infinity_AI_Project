# Day 18 执行总结 · 2026-10-22

> 任务：20 题种子集 + 首批 Badcase（Week 04 Task 4，v0.2）
> 结果：**DONE**（§3 除 git tag 外全部勾上；tag 按用户要求未执行，命令已备好）

## 1. 做了哪些事

| Step | 内容 | 产出 |
| --- | --- | --- |
| Step 1 | 20 题种子集（12 in_kb / 5 out_of_kb / 3 confusing，覆盖 notes/oss/team，含 v0.1 私有题复测） | `eval/datasets/kb_qa.jsonl` |
| Step 2 | 冒烟脚本（pydantic schema 校验 + 调 `/v1/kb/ask` + 来源命中/拒答统计 + 报告） | `scripts/run_kb_smoke.py` |
| Step 3 | 跑报告 + 人工判对错 | `eval/reports/20261022-rag-v0.2.md`、`eval/runs/20261022-rag-v0.2.jsonl` |
| Step 4 | Badcase 库升级为完整模板（8 类根因 + 12 条） | `eval/badcases/badcases.md` |
| Step 5 | README v0.2 章节 | `README.md` |
| Step 6 | tag `v0.2.0` + Week 4 复盘 | **未提交（用户要求）**；Week 4 README §11 已填 |

## 2. 产出文件

- `eval/datasets/kb_qa.jsonl`（新增，20 行）
- `scripts/run_kb_smoke.py`（新增）
- `eval/reports/20261022-rag-v0.2.md`（新增）
- `eval/runs/20261022-rag-v0.2.jsonl`（新增，运行明细）
- `eval/badcases/badcases.md`（重写：完整模板 + 12 条）
- `README.md`（新增 v0.2 章节 + 更新路线图）
- `plan/plan_ai/phase_01/week_04/README.md`（Day15–18 状态 + §7 验收 + §11 周复盘）

## 3. 验收对齐（§3）—— 逐条完整命令

以下命令均在 `cd ~/lab/workpilot` 之后执行（API 已在 8000 端口运行）。

### ① `eval/datasets/kb_qa.jsonl` 20 行：in_kb 12、out_of_kb 5、confusing 3，schema 校验通过

```bash
cd ~/lab/workpilot && python3 -c "import json;lines=[json.loads(l) for l in open('eval/datasets/kb_qa.jsonl') if l.strip()];from collections import Counter;print('total=',len(lines),dict(Counter(q['type'] for q in lines)))"
```

期望输出：`total= 20 {'in_kb': 12, 'out_of_kb': 5, 'confusing': 3}`

schema 校验（pydantic，不合法直接报错）——直接跑脚本，开头会打印：

```bash
cd ~/lab/workpilot && uv run --project apps/api python scripts/run_kb_smoke.py
```

期望输出首行：`schema 校验通过：20 题 (in_kb=12, out_of_kb=5, confusing=3)`

### ② `run_kb_smoke.py` 生成报告

```bash
cd ~/lab/workpilot && uv run --project apps/api python scripts/run_kb_smoke.py
```

期望：脚本打印统计行，并在 `eval/reports/20261022-rag-v0.2.md` 生成报告、`eval/runs/20261022-rag-v0.2.jsonl` 生成明细。

### ③ 报告含来源命中率 / 库外拒答率 / 人工正确率 / 平均延迟 / 总成本

```bash
cd ~/lab/workpilot && head -7 eval/reports/20261022-rag-v0.2.md
```

期望输出（数值为本次实测）：

```
# RAG v0.2 种子集报告 · 20261022
- 来源命中：13/15
- 库外拒答：5/5
- 平均延迟：1253 ms；总成本：0.015486
- 人工正确：16/20（错：q003、q004、q005、q019）
```

查看逐题明细：

```bash
cd ~/lab/workpilot && cat eval/reports/20261022-rag-v0.2.md
```

### ④ Badcase 库升级为完整模板，≥5 条

```bash
cd ~/lab/workpilot && grep -c '^| BC-' eval/badcases/badcases.md && echo "---根因分布---" && sed -n '/根因分布/,/v0.1 → v0.2/p' eval/badcases/badcases.md
```

期望：`| BC-` 开头的表格行 ≥ 5（本次 12 条），且有「根因分布」小节。

### ⑤ README 有 v0.2 章节

```bash
cd ~/lab/workpilot && grep -n 'v0.2（2026-10-22）· RAG MVP' README.md && grep -n '/v1/kb/ask' README.md | head -3
```

期望：命中 v0.2 章节标题与 KB API 描述。

### ⑥ git tag `v0.2.0` 且已 push（**本次未执行**：用户要求不提交）

> 你后续要打 tag 时，用下面这条完整命令（确保先 commit 后再跑）：

```bash
cd ~/lab/workpilot && git add eval scripts/run_kb_smoke.py README.md && \
git commit -m "feat(eval): kb_qa seed set (20), smoke runner, badcase taxonomy; release v0.2" && \
git tag -a v0.2.0 -m "v0.2.0: RAG MVP with citations and refusal" && \
git push && git push origin v0.2.0
```

当前状态确认（应为未提交）：

```bash
cd ~/lab/workpilot && git status --short && git tag -l
```

期望：`eval/datasets/kb_qa.jsonl`、`scripts/run_kb_smoke.py`、`eval/reports/20261022-rag-v0.2.md`、`eval/badcases/badcases.md`、`README.md` 处于未提交；`git tag -l` 无 `v0.2.0`。

### ⑦ 单元测试无回归

```bash
cd ~/lab/workpilot/apps/api && uv run pytest -m "not llm" -q
```

期望输出末尾：`46 passed, 2 deselected in ...`

### ⑧ lint 干净

```bash
cd ~/lab/workpilot && uv run --project apps/api ruff check scripts/run_kb_smoke.py
```

期望输出：`All checks passed!`

## 4. 产出记录（§11）

- 来源命中 / 库外拒答 / 人工正确：**13/15、5/5、16/20**（错：q003、q004、q005、q019）
- 平均延迟 / 总成本：**1253 ms / ¥0.015486**
- Badcase 新增编号与根因分布：新增 BC-010（过度拒答）、BC-011（生成幻觉/引用错误）、BC-012（召回排序靠后）；迁移 v0.1 的 BC-001~009 并补复测结论。根因分布见 `eval/badcases/badcases.md`。
- v0.1 → v0.2 私有知识题对比：v0.1 的 8 道私有题全「拒答/编造」；v0.2 复测 6 道（BC-001~006）→ 1 修复（BC-004 已能正确引用 §4）、2 召回排序靠后（BC-001/003）、3 数据缺失（BC-002/005/006，`.env.example`/`llm_providers.py`/`routes` 尚未入库）。
- 卡点记录：① 脚本 `json.dumps` 遇到 pydantic 模型报 `TypeError`（已改为 `q.model_dump()`）；② ruff BLE001 盲捕获 `Exception`（已改为 `httpx.HTTPError, ValueError`）。均无阻塞。
- 用时：约 45 分钟（含 3 类问题实测、人工判定、badcase 复测）。

## 5. 与 PLAN 的偏离说明

1. **未打 tag / 未提交**：按用户要求「不用帮我提交代码」，Step 6 的 git add/commit/tag/push 全部跳过，等价命令在 §3⑥ 备好。因此 §3 的「tag 已 push」一项保留未勾。
2. **人工正确率按真实判定填 16/20**：PLAN 示例里 BC-001 预期「v0.2 正确引用 [1]」，但实测「WorkPilot 仓库的提交信息规范是什么？」仍过度拒答（top1 为 `da01-definition`，正确来源 `PROJECT_STANDARD`/`git-branching` 未进 top5）——这是真实 badcase，如实记录为「召回排序靠后」而非照抄 PLAN 的乐观预期。
3. **语料覆盖边界**：`.env.example`、`llm_providers.py`、`routes/` 清单未入库（Day15 语料只到 `data/corpus/` 的自写笔记/团队样例/公开文档），导致 BC-002/005/006 仍为「数据缺失」，留 W5 补齐。

## 6. 概念自检（§7，附答案）

1. 为什么评测集里必须有库外题？→ 只测库内题无法发现「拒答失败」，而编造是 RAG 最严重的问题。
2. 为什么提问不能照抄原文？→ 照抄会让向量相似度虚高、高估召回；真实用户措辞与文档不同。
3. 「未召回」和「召回排序靠后」修复手段有何不同？→ 前者改分块/语料/检索方式（hybrid）；后者调 top_k、rerank、标题加权。
4. 来源命中但答案错，说明问题在哪一层？→ 生成层或分块层——看关键句是否在命中块内，区分生成幻觉与分块切断。
5. 为什么 v0.1 的 badcase 要复测？→ 形成「修复→回归」闭环，证明改进有效，也是回归用例的雏形。
