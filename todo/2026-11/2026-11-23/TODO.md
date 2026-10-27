# 2026-11-23 周一 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_02/week_09/day34_20261123/PLAN.md)

**Day 34 · 2026-11-23 · Week 09 Task 1：Tool Calling 原理 + Registry**

### 🎯 今天一件事

先用裸 SDK 看清 Function Calling 的消息往返，再把它封装成 WorkPilot 的 Tool Registry（含 `calculator` 教学工具与单测）。

不碰：kb_search / web_search / gitea 等业务工具（Day35）、Agent 循环（Day36）、LangGraph（W11）、任何写工具。

### ✅ 验收对齐

- [ ] `raw_tool_call.py` 输出：第一轮 `finish_reason=tool_calls` + tool_call 的 id/name/arguments；第二轮给出最终答案
- [ ] `NOTES.md` 有消息序列图（mermaid）+ 3 条观察
- [ ] Gateway 新增 `chat_with_tools()`，仍记录 tokens / 成本
- [ ] `registry.py`：`@register` 重名报错；`to_openai_tools()` 格式正确；`execute()` 非法参数 / 超时 / 未知工具均返回 `ok=False`
- [ ] `calculator` 用 ast 求值，`__import__("os")`、`2**99999` 被拒绝
- [ ] `uv run pytest tests/tools -q` 全绿，已 push

### ⏱ 时间块

| 时间        | 优先级 | 内容                                                          |
| ----------- | ------ | ------------------------------------------------------------- |
| 0–20 min    | P0     | 裸实验 + 序列图                                               |
| 20–35 min   | P0     | Gateway `chat_with_tools()`                                   |
| 35–75 min   | P0     | `registry.py`（AI 生成样板，自己审 `execute()`）              |
| 75–95 min   | P0     | `calculator.py` + 单测                                        |
| 95–105 min  | P1     | 概念自检 + 产出记录                                           |
| 105–120 min | P2     | 试一次 `tool_choice="required"` / `"none"` 的差异，记到 NOTES |

时间不足时最低保留：`registry.py` + `calculator.py` + 3 个单测（schema / 非法参数 / 超时）。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_02/week_06/day26_2026-11-23/PLAN.md)

**Day 26 · 2026-11-23 · Week 06 · Solo B m50-52 慢速**

### 🎯 今天一件事

聚焦「Solo B m50-52 慢速」：练 第 50-52 小节，达成下面的验收勾选项。

不碰：强力和弦节奏、闷音、提速（Phase 3）。

### ✅ 验收对齐

- [ ] 当日小节每个音按准、节奏对，慢速（60bpm）不断不错

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Solo B m50-52 慢速（第 50-52 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：当日小节 60bpm 连续弹 3 遍无错。

### ⚡ 时间不够时

当日小节 60bpm 连续弹 3 遍无错。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_01/week_06/day26_20261123/PLAN.md)

**Day 26 · 2026-11-12 · Week 04 · 全曲右手分段复习（第4-5页）**

### 🎯 今天一件事

聚焦「全曲右手分段复习（第4-5页）」：练 第80–106小节，达成下面的验收勾选项。

不碰：左手伴奏、双手合奏（Phase 2 才碰）、提速（Phase 3 才碰）。

### ✅ 验收对齐

- [ ] 第80–106小节 右手慢速连续 3 遍无错
- [ ] 全曲右手串联不断、不错（或指定分段）
- [ ] 记录本次串联的 3 个卡点及原因

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：Hanon + 音阶，70bpm |
| 5–40 min | P0 | 主练：全曲右手分段复习（第4-5页）（第80–106小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：完成 第80–106小节 慢练 + 至少一次完整串联并记下 3 个卡点。

### ⚡ 时间不够时

完成 第80–106小节 慢练 + 至少一次完整串联并记下 3 个卡点。

---
