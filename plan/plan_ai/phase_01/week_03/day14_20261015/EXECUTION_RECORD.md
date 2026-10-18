# Day14 执行记录（2026-10-15 · Task 4：LLM 应用 v0 + 10 题冒烟）

## 结论

6 个 Step 全部完成，验收项 **6/7 通过**，1 项（`git tag v0.1.0`）按你的要求**未执行**（不提交代码）。
代码与产物此前已就位，本轮重新执行并复核了每一步，用真实调用重跑了冒烟与验收命令。

## 各 Step 执行情况

| Step | 内容 | 状态 | 关键产物 |
| ---- | ---- | ---- | -------- |
| 1 | `qa_answer.v0.md` + `/v1/ask` + `/v1/ask/stream` | ✅ 已存在并验证 | `prompts/qa_answer.v0.md`、`apps/api/app/routes/ask.py` |
| 2 | 10 题冒烟集 | ✅ 10 行可解析 | `eval/datasets/smoke_v0.jsonl` |
| 3 | 冒烟脚本 + 报告 | ✅ 重跑通过 | `eval/runners/run_smoke.py`、`eval/reports/20261015-smoke-v0.1.md` |
| 4 | 首批 Badcase | ✅ 9 条 | `eval/badcases/badcases.md` |
| 5 | README v0.1 + tag | ⚠️ README ✅ / tag 跳过 | `README.md`（v0.1 章节） |
| 6 | Week 3 复盘 | ✅ 已填写 | `plan/plan_ai/phase_01/week_03/README.md` §11 |

## 前置确认（PLAN §2）

```text
uv run pytest -m "not llm" -q   →  32 passed, 2 deselected
da01-definition.md              →  主场景 SP-A 深化（3.90 / 3.85）已选定
服务                            →  GET /health HTTP 200；LLM_PROVIDER=deepseek，key 已配置
```

## 验收对齐（PLAN §3）——每项附完整命令，直接在终端粘贴可复现

> 前置：服务已在 `~/lab/workpilot` 以 `uv run uvicorn app.main:app --port 8000` 启动（若未启动，先执行）。

**① `/v1/ask` 返回结构化回答 + source_note + usage + cost + latency_ms**

```bash
curl -s http://localhost:8000/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Vite 的 import.meta.env 和 process.env 有什么区别？"}' | python3 -m json.tool
```

预期：JSON 含 `answer`（含 `answer`/`key_points`/`confidence`/`needs_more_context`）、
`source_note: "来源：模型通用知识（未接入知识库）"`、`prompt: "qa_answer.v0"`、`usage`、`cost`、`latency_ms`。
实测：`confidence=high`、`needs_more_context=false`、`cost=0.002153`、`latency_ms=4299`。

**② `/v1/ask/stream` 用 `curl -N` 可见 token 流，`done` 事件含 source_note**

```bash
curl -N -s -X POST http://localhost:8000/v1/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"我们团队的 commit message 规范要求 scope 怎么写？"}'
```

只看结尾统计事件：

```bash
curl -N -s -X POST http://localhost:8000/v1/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"我们团队的 commit message 规范要求 scope 怎么写？"}' | grep -A1 '^event: done'
```

预期：多条 `event: token` 后接 `event: done`，`data` 含 `source_note`、`usage`、`cost`、`latency_ms`、`ttft_ms`。
实测：`source_note` 正常，`ttft_ms=712`。

**③ `smoke_v0.jsonl` 10 行、可逐行 `json.loads`**

```bash
cd ~/lab/workpilot && python3 -c "import json; rows=[json.loads(l) for l in open('eval/datasets/smoke_v0.jsonl',encoding='utf-8') if l.strip()]; print('行数:', len(rows))"
```

预期输出 `行数: 10`（其中 4 道私有题、5 道公开题、1 道库外题）。

**④ 冒烟报告存在**

```bash
cd ~/lab/workpilot && ls -1 eval/reports/20261015-smoke-v0.1.md
```

**⑤ Badcase ≥ 3 条**

```bash
cd ~/lab/workpilot && grep -c '^| BC-' eval/badcases/badcases.md
```

预期 ≥ 3；实测 **9 条**（BC-001 ~ BC-009）。

**⑥ README v0.1 章节 / git tag（tag 本项未执行）**

```bash
cd ~/lab/workpilot && grep -n 'v0.1' README.md | head
cd ~/lab/workpilot && git tag -l
```

README 已含 v0.1 章节；`git tag -l` 当前只有 `v0.0.0`（`v0.1.0` 待你自行打，见下）。

**⑦ Week 3 README 第 11 节已填写**

```bash
grep -n '周复盘' ~/Documents/a_future/plan/plan_ai/phase_01/week_03/README.md
```

## 冒烟实测数据（本次重跑 20261015）

```text
成功 10/10；平均延迟 2692 ms；总成本 0.012473；low 置信占比 40%
私有题 4/4 全部拒答（confidence=low + needs_more_context=true），0 条高置信幻觉
```

人工判定（对照 `expected`）：10 题公开题全对、私有题全部「拒答」（即失败形态为「过度保守」而非「幻觉」）、
库外题正确拒答。与 `eval/badcases/badcases.md` §2 结论一致。

## 未做事项（按你的要求跳过，供你自行补齐）

以下命令**未执行**，你确认后自行在 `~/lab/workpilot` 运行即可补上 tag：

```bash
cd ~/lab/workpilot
git add prompts apps/api eval README.md docs
git commit -m "feat(ask): document assistant v0 with smoke eval and first badcases"
git tag -a v0.1.0 -m "v0.1.0: LLM gateway (structured/stream/cost) + assistant v0"
git push && git push origin v0.1.0
```

若远端已有 `v0.1.0` 报 rejected，不要强推，改用 `v0.1.1` 并在 CHANGELOG 说明。

## 产出文件清单

- `~/lab/workpilot/prompts/qa_answer.v0.md`
- `~/lab/workpilot/apps/api/app/routes/ask.py`（`/v1/ask`、`/v1/ask/stream`）
- `~/lab/workpilot/eval/datasets/smoke_v0.jsonl`
- `~/lab/workpilot/eval/runners/run_smoke.py`
- `~/lab/workpilot/eval/reports/20261015-smoke-v0.1.md`
- `~/lab/workpilot/eval/badcases/badcases.md`（9 条）
- `~/lab/workpilot/README.md`（v0.1 章节）
- `~/Documents/a_future/plan/plan_ai/phase_01/week_03/README.md`（§11 周复盘）
