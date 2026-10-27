# 2026-11-25 周三 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_02/week_09/day36_20261125/PLAN.md)

**Day 36 · 2026-11-25 · Week 09 Task 3：多工具循环 Demo + 工具选择测试 + JD 追踪（v0.6）**

### 🎯 今天一件事

写出 WorkPilot 的第一个工具循环 `tool_loop.py`（LLM ⇄ 工具，最多 5 步），用 15 条工具选择用例量化「选得准不准」，打 tag `v0.6.0`。

不碰：规划器 / 决策器（Day37）、SSE 接口与前端（Day38–39）、LangGraph（W11）。

### ✅ 验收对齐

- [ ] `tool_loop.py`：同一轮多个 tool_calls 用 `asyncio.gather` 并行执行；`max_steps=5`；达到上限后用 `tool_choice="none"` 强制收尾
- [ ] 每步输出结构化日志（step、tool、args、ok、latency_ms、tokens）
- [ ] `scripts/tool_demo.py` 跑 3 个问题，至少 1 个触发 ≥2 个工具
- [ ] `eval/datasets/tool_selection.jsonl` 15 条；`run_tool_selection.py` 输出准确率与错选明细到 `eval/reports/20261125-tool-selection.md`
- [ ] tag `v0.6.0` 推送到 Gitea 与 GitHub
- [ ] `career/job-market.md` 新增第 1 轮 JD 追踪（10 个 JD + 关键词频次变化）

### ⏱ 时间块

| 时间        | 优先级 | 内容                                         |
| ----------- | ------ | -------------------------------------------- |
| 0–35 min    | P0     | `tool_loop.py` + `tool_demo.py`，跑 3 个问题 |
| 35–70 min   | P0     | 15 条用例 + runner + 报告                    |
| 70–80 min   | P0     | tag `v0.6.0` + push                          |
| 80–100 min  | P1     | JD 追踪第 1 轮（严格计时 20 分钟）           |
| 100–110 min | P1     | 周复盘（week_09/README.md §11）              |
| 110–120 min | P2     | `docs/product/open-core.md` 草稿             |

时间不足时最低保留：`tool_loop.py` + 8 条用例 + tag；JD 追踪压缩为 5 个。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_02/week_06/day28_2026-11-25/PLAN.md)

**Day 28 · 2026-11-25 · Week 06 · Solo B m56-58 慢速**

### 🎯 今天一件事

聚焦「Solo B m56-58 慢速」：练 第 56-58 小节，达成下面的验收勾选项。

不碰：强力和弦节奏、闷音、提速（Phase 3）。

### ✅ 验收对齐

- [ ] 当日小节每个音按准、节奏对，慢速（60bpm）不断不错

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Solo B m56-58 慢速（第 56-58 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：当日小节 60bpm 连续弹 3 遍无错。

### ⚡ 时间不够时

当日小节 60bpm 连续弹 3 遍无错。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_01/week_06/day28_20261125/PLAN.md)

**Day 28 · 2026-11-14 · Week 04 · M1 验收：右手全曲演奏 + 录音**

### 🎯 今天一件事

聚焦「M1 验收：右手全曲演奏 + 录音」：练 第1–106小节，达成下面的验收勾选项。

不碰：左手伴奏、双手合奏（Phase 2 才碰）、提速（Phase 3 才碰）。

### ✅ 验收对齐

- [ ] 第1–106小节 右手慢速连续 3 遍无错
- [ ] 全曲右手串联不断、不错（或指定分段）
- [ ] 记录本次串联的 3 个卡点及原因

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：Hanon + 音阶，70bpm |
| 5–40 min | P0 | 主练：M1 验收：右手全曲演奏 + 录音（第1–106小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：完成 第1–106小节 慢练 + 至少一次完整串联并记下 3 个卡点。

### ⚡ 时间不够时

完成 第1–106小节 慢练 + 至少一次完整串联并记下 3 个卡点。

---
