# Day 13 · 2026-10-14 · Task 3 执行记录与验收手册

> 与 `PLAN.md` 同级。实际执行日期 2026-10-11（提前执行 Day13）。
> 结论：**主场景已选定，验收前四条全绿。**（按要求未 commit / 未 push。）

---

## 一、做了什么（改动清单）

| 文件 | 变更 |
| --- | --- |
| `~/lab/projects/product-lab/pain-pool.md` | 末尾新增「评分矩阵（2026-10-14 · 精简版：只打候选 3 条）」：P-02 / P-07 / P-03 的 SP 映射、8 维分数、加权总分、门槛判定、分数依据、**选型结论** |
| `~/lab/workpilot/docs/product/da01-definition.md` | **新增**：DA-01 定义 v1（8 要素 + 成功指标 + 明确不做 8 条 + W4 语料计划 + 合规检查清单 + 选型依据表 + 变更记录） |
| `PROJECT_CONFIG.md` | §2「DA-01 状态」由「方向已定…待 Day13 选出」→「已定义：主场景 SP-A 深化（Score 3.90/3.85）+ 定义文档路径」 |
| 本文件 `EXECUTION_RECORD.md` | 新增 |

### 决策结果

- **打分 3 条**（不是 10 条）：P-02 **3.90**（SP-A）、P-07 **3.85**（SP-A）、P-03 **3.35**（SP-C），全部过门槛（D ≥ 3 且 E ≥ 3）。
- **主场景 = SP-A 深化「团队规范与组件库用法问答（带引用 Grounded Q&A）」**
  - P-02 与 P-07 合并：P-07 的缺口是「AI 不知道团队规范」（知识），不是「不会审查代码」（工具）→ 不做新场景包，M10 骨架不变。
  - P-03（唯一非 SP-A 候选）AI 适配度仅 2 分，是 pre-commit hook 能解决的自动化问题 → 降级，不做主场景。
- **价值量化**：P-02 75 分钟/周 + P-07 40 分钟/周 = 115 分钟/周 × 60% ≈ **节省 69 分钟/周**（definition 取保守下限 **≥ 60 分钟/周**）。
- **W4 语料**：30–80 篇，4 类来源（自有笔记 8–15 / 公开开源文档 20–50 / 自写脱敏团队规范 5–10 / 可选 PDF-HTML 3–5）。

### 未做（按精简版 PLAN 与用户要求）

- 未 commit / 未 push（用户明确要求）。
- 未做辅场景选型、Backlog 表、`DA01_TARGET_ASSET.md` M10 标注「已选」、`plan/CHANGELOG.md` 追加 → 留到下次一并处理。
- 未收集语料、未写代码、未调模型。

---

## 二、验收对齐（PLAN 第 3 节勾选结果）

- [x] `pain-pool.md` 新增评分矩阵表：3 条痛点有 SP 映射 + 8 维分数 + 加权总分
- [x] 主场景已选定，理由对应到分数与硬门槛（D ≥ 3 且 E ≥ 3）
- [x] `da01-definition.md` 含 8 要素 + 成功指标 + 明确不做（8 条 ≥ 5）+ W4 语料计划（4 类 ≥ 3，30–80 篇）
- [x] `PROJECT_CONFIG.md` §2「DA-01 状态」已回填主场景
- [x] 本文件已写出「做了什么 + 可直接复制的验收命令」
- [ ] 未 commit / 未 push（跳过，符合要求）

---

## 三、详细验收操作（完整命令，可直接复制到终端）

> 本次是**纯文档日**，没有新增 HTTP 接口，所以验收以文件 / 计算 / 状态检查为主；
> 最后附一个**可选回归**（用 curl 确认 v0.1 链路没被破坏）。

### 验收 1：评分矩阵存在且只打了 3 条

```bash
cd ~/lab/projects
grep -n "评分矩阵" product-lab/pain-pool.md
sed -n '/## 评分矩阵/,$p' product-lab/pain-pool.md
```

预期：打印出 `## 评分矩阵（2026-10-14 · 精简版：只打候选 3 条）` 以及含 P-02 / P-07 / P-03 三行的表格 + 「选型结论」小节。

```bash
cd ~/lab/projects
sed -n '/## 评分矩阵/,$p' product-lab/pain-pool.md | grep -c "^| P-"
```

预期输出：`3`

### 验收 2：加权总分可复算（不手算）

```bash
cd ~/lab/projects
uv run --with nothing python - <<'PY'
W = dict(F=.20, T=.15, AI=.15, D=.15, E=.10, J=.10, B=.05, C=.10)
rows = {
    "P-02": dict(F=5, T=3, AI=4, D=3, E=4, J=4, B=4, C=2),
    "P-07": dict(F=5, T=2, AI=4, D=4, E=4, J=5, B=3, C=3),
    "P-03": dict(F=4, T=3, AI=2, D=4, E=4, J=2, B=2, C=1),
}
for k, r in rows.items():
    s = sum(W[d] * (6 - r[d] if d == "C" else r[d]) for d in W)
    print(k, round(s, 2), "PASS" if (r["D"] >= 3 and r["E"] >= 3) else "BLOCKED")
PY
```

预期输出（已实测）：

```text
P-02 3.9 PASS
P-07 3.85 PASS
P-03 3.35 PASS
```

与 `pain-pool.md` 矩阵表中的 Score 列一致 → 分数可追溯。

### 验收 3：主场景选定理由可追溯

```bash
cd ~/lab/projects
grep -n "主场景" product-lab/pain-pool.md
cd ~/lab/workpilot/docs/product
grep -n "主场景\|裁决" da01-definition.md
```

预期：能看到「主场景 = SP-A 深化」（pain-pool 选型结论）与 definition §5「选型依据」中的裁决说明（P-07 由「新」改判为 SP-A）。

### 验收 4：definition 的 8 要素齐全

```bash
cd ~/lab/workpilot/docs/product
sed -n '/## 1. 八要素/,/## 2\./p' da01-definition.md | grep -cE "^\| (问题|用户|场景|价值|验证方式|交付形态|商业模式|技术组合) "
```

预期输出：`8`

### 验收 5：「明确不做」≥ 5 条

```bash
cd ~/lab/workpilot/docs/product
sed -n '/## 3. 明确不做/,/## 4\./p' da01-definition.md | grep -c "^[0-9]\+\. "
```

预期输出：`8`

### 验收 6：W4 语料计划 ≥ 3 类来源 + 篇数 + 合规清单

```bash
cd ~/lab/workpilot/docs/product
sed -n '/## 4. W4 语料计划/,/### 合规检查清单/p' da01-definition.md | grep -cE "^\| [①②③④]"
```

预期输出：`4`

```bash
cd ~/lab/workpilot/docs/product
grep -n "30–80\|data/corpus/SOURCES.md\|\.gitignore" da01-definition.md
```

预期：能看到「目标 30–80 篇」「记录仓库地址 + commit + 许可证」「`data/corpus/` 已写入 `.gitignore`」。

### 验收 7：成功指标可量化

```bash
cd ~/lab/workpilot/docs/product
grep -nE "≥ 60 分钟|hit@5|引用正确率|库外拒答率|P95|¥0.02" da01-definition.md
```

预期：`≥ 60 分钟`、`hit@5 ≥ 0.85`、`引用正确率 ≥ 0.80`、`库外拒答率 ≥ 0.80`、`P95 < 8s`、`< ¥0.02` 全部出现。

### 验收 8：PROJECT_CONFIG 状态已回填

```bash
cd /Users/infinity/Documents/a_future
grep -n "DA-01 状态" PROJECT_CONFIG.md
sed -n '/^## 2\. 当前状态/,/^---/p' PROJECT_CONFIG.md
```

预期：「DA-01 状态」行含 `已定义：WorkPilot；主场景 SP-A 深化`、`Score 3.90 / 3.85`、`da01-definition.md`。

### 验收 9：合规预检命令可用（今天语料为空，Day15 才真有内容）

```bash
cd ~/lab/workpilot
grep -rniE "公司名|同事姓名|内部域名|内网IP|token|password|secret" data/corpus/ ; echo "grep exit=$?"
```

预期（今天）：`data/corpus/` 尚不存在 → 无匹配输出，`grep exit=2`（表示路径不存在，等同「通过」）。
Day15 语料放进去后重跑，预期为**无任何匹配行**且 `grep exit=1`。

### 验收 10（可选回归）：确认 v0.1 链路没被今天改动破坏

终端 A — 启动服务：

```bash
cd ~/lab/workpilot/apps/api
uv run uvicorn app.main:app --reload --port 8000
```

终端 B — 完整 curl 命令：

```bash
curl -s http://localhost:8000/health
```

预期：`{"status":"ok",...}`

```bash
curl -s -X POST http://localhost:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用一句话解释什么是 RAG"}]}' \
  | python3 -m json.tool
```

预期：返回 JSON，含模型回答内容与 usage（`.env` 当前 `LLM_PROVIDER=deepseek`，key 可用）。

流式（Day12 成果，确认 SSE 未受影响）：

```bash
curl -sN -X POST http://localhost:8000/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用一句话解释什么是向量检索"}]}'
```

预期：多条 `event: token`，最后一条 `event: done`（含 `usage.total_tokens`、`cost`、`latency_ms`、`ttft_ms`）。

结束验收后 `Ctrl+C` 停掉服务。

### 验收 11：今日改动文件清单

```bash
cd /Users/infinity/Documents/a_future && git status --short
cd ~/lab/projects && git status --short
cd ~/lab/workpilot && git status --short
```

预期（本次执行后实测，含此前未提交的 Day10–12 遗留改动）：

```text
# a_future
 M PROJECT_CONFIG.md
 M plan/plan_ai/phase_01/week_02/day10_20261007/draft.md
 M plan/plan_ai/phase_01/week_03/day11_20261012/PLAN.md
 M plan/plan_ai/phase_01/week_03/day13_20261014/PLAN.md
 M prompt/day_plsn_prompt.md
?? plan/plan_ai/phase_01/week_03/day11_20261012/REPORT.md
?? plan/plan_ai/phase_01/week_03/day11_20261012/draft.md
?? plan/plan_ai/phase_01/week_03/day12_20261013/EXECUTION_RECORD.md
?? plan/plan_ai/phase_01/week_03/day12_20261013/draft.md
?? plan/plan_ai/phase_01/week_03/day13_20261014/EXECUTION_RECORD.md
?? plan/plan_ai/phase_01/week_03/day13_20261014/draft.md

# ~/lab/projects
?? product-lab/pain-pool.md
?? infra/backup-drill.md
?? infra/scripts/

# ~/lab/workpilot
?? docs/product/da01-definition.md
```

> **今天新增/修改的只有 4 个文件**：`PROJECT_CONFIG.md`、`day13_20261014/PLAN.md`（精简版）、
> `product-lab/pain-pool.md`（+评分矩阵）、`docs/product/da01-definition.md`（新增）；
> 其余条目是前几天的遗留未提交内容。

---

## 四、产出记录（PLAN 第 9 节）

- 打分条数 / 过门槛数：**3 / 3**
- 主场景（Score）：**SP-A 深化（P-02 3.90，P-07 3.85）**
- 预计每周节省：**≥ 60 分钟**（实际推算 69 分钟）
- 语料计划篇数（①/②/③/④）：**8–15 / 20–50 / 5–10 / 3–5（合计 30–80）**
- 是否触发 §12.5（替换场景包）：**否**（骨架 M0–M9/M11 未变，M10 只是明确为 SP-A 深化）
- 卡点记录：无（未出现返工，未重打全表）
- 用时：约 **25 分钟**（AI 辅助，远低于 90 分钟上限）

---

## 五、遗留（下次一起做，不占今天）

1. `plan/plan_ai/DA01_TARGET_ASSET.md` §5 M10 表：给 SP-A 行加「**（已选·主，2026-10-14）**」。
2. `plan/CHANGELOG.md` 追加一条（模板见 PLAN 原文 §Step 5）。
3. 辅场景选型 + Backlog 表（Day14 之后）。
4. 两个仓库 commit / push；Infinity_AI_Project 若在 Git 下同样提交。
