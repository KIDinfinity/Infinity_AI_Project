# 2026-11-30 周一 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_02/week_10/day37_20261130/PLAN.md)

**Day 37 · 2026-11-30 · Week 10 Task 1：手写 plan→act→observe 循环 v0**

### 🎯 今天一件事

不用任何框架，手写 WorkPilot 的第一个 Agent 循环 `loop_v0.py`：先规划、逐步选工具执行、观察、再决策（继续 / 重规划 / 结束），带 4 个停止条件。

不碰：报告结构与来源映射（Day38）、HTTP/SSE 接口（Day38）、前端（Day39）、LangGraph（W11）、记忆（W12）。

### ✅ 验收对齐

- [ ] `schemas.py`：`Plan` / `PlanStep` / `Decision` / `Observation` / `AgentEvent` / `AgentState`
- [ ] `steps.py`：`plan_step` / `choose_action` / `decide_step` / `final_answer`（纯异步函数，不持有状态，W11 节点直接复用）
- [ ] `loop_v0.run_events()`：异步生成器，逐个 yield `AgentEvent`
- [ ] 4 个停止条件：`finish` 决策、`max_steps=8`、token 预算、重复调用检测；另有 `max_replans=2`
- [ ] 单测 4 个停止条件全绿（不调真实 LLM）
- [ ] CLI 跑 3 个任务，trace 贴进产出记录；已 push

### ⏱ 时间块

| 时间        | 优先级 | 内容                                               |
| ----------- | ------ | -------------------------------------------------- |
| 0–15 min    | P0     | `schemas.py`（AI 生成，自己审字段）                |
| 15–30 min   | P0     | 两个提示词文件                                     |
| 30–60 min   | P0     | `steps.py` 四个函数                                |
| 60–85 min   | P0     | `loop_v0.run_events()`（自己写，不让 AI 一把生成） |
| 85–100 min  | P0     | CLI + 3 个任务实跑                                 |
| 100–115 min | P1     | 停止条件单测                                       |
| 115–120 min | P1     | 提交                                               |

时间不足时最低保留：planner + decider + 循环 + max_steps 停止 + 1 个任务实跑。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_02/week_07/day31_2026-11-30/PLAN.md)

**Day 31 · 2026-11-30 · Week 07 · Chorus Rhythm1 m39-42**

### 🎯 今天一件事

聚焦「Chorus Rhythm1 m39-42」：练 第 39-42 小节，达成下面的验收勾选项。

不碰：Solo 旋律、Clean 分解、提速。

### ✅ 验收对齐

- [ ] 当日小节和弦切换干净、闷音到位、节奏对齐节拍器

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Chorus Rhythm1 m39-42（第 39-42 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

### ⚡ 时间不够时

右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_02/week_07/day31_20261130/PLAN.md)

**Day 31 · 2026-11-17 · Week 05 · 第1页左手单独练习**

### 🎯 今天一件事

聚焦「第1页左手单独练习」：练 第1–31小节，达成下面的验收勾选项。

不碰：提速（Phase 3 才碰）、表现力打磨（Week 11 才碰）。

### ✅ 验收对齐

- [ ] 第1–31小节 左手单独弹顺（50bpm，连续 2 遍无错）
- [ ] 第1–31小节 双手极慢合（40-50bpm）对齐拍点
- [ ] 第1–31小节 双手连弹 2 遍无错音错拍

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：Hanon 第1条（左手）+ 右手第1页快过 |
| 5–40 min | P0 | 主练：第1页左手单独练习（第1–31小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：左手音型单独弹顺 + 第1–31小节 前 4 小节双手极慢合对齐。

### ⚡ 时间不够时

左手音型单独弹顺 + 第1–31小节 前 4 小节双手极慢合对齐。

---
