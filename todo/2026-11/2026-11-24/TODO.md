# 2026-11-24 周二 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_02/week_09/day35_20261124/PLAN.md)

**Day 35 · 2026-11-24 · Week 09 Task 2：内置工具**

### 🎯 今天一件事

把 WorkPilot 的三类信息源接成只读工具：`kb_search`、`web_search`、`gitea_repo_read`、`gitea_issue_read`，统一截断 + 来源标注 + 不可信内容包裹，并用 mock 单测与 live 冒烟证明可用。

不碰：任何写工具（`gitea_issue_create` 在 Day45）、Agent 循环（Day36）、前端。

### ✅ 验收对齐

- [ ] `common.py`：`clip()`、`wrap_untrusted()`（转义 `</tool_output>`）
- [ ] 4 个工具注册成功，`to_openai_tools()` 共 5 个
- [ ] 每个工具都返回 `ToolOutput(text=wrap_untrusted(...), sources=[...])`
- [ ] `gitea_repo_read` 拒绝白名单外仓库、拒绝 `..` 路径（单测）
- [ ] mock 单测全绿（Gitea 用 respx，Tavily 用 monkeypatch）；`uv run pytest -m live` ≥ 3 个通过
- [ ] `.env.example` 已加 4 个键（无真实值），已 push

### ⏱ 时间块

| 时间        | 优先级 | 内容                                             |
| ----------- | ------ | ------------------------------------------------ |
| 0–10 min    | P0     | 配置项 + `common.py`                             |
| 10–30 min   | P0     | `kb_search` + 单测                               |
| 30–65 min   | P0     | `gitea.py`（repo_read + issue_read）+ respx 单测 |
| 65–90 min   | P0     | `web_search`（Tavily + ddgs 兜底）+ 单测         |
| 90–105 min  | P1     | live 冒烟 + 提交                                 |
| 105–120 min | P2     | `http_fetch` + SSRF 单测（做不完直接进 Backlog） |

时间不足时最低保留：`kb_search` + `gitea_repo_read` + 各 1 个单测。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_02/week_06/day27_2026-11-24/PLAN.md)

**Day 27 · 2026-11-24 · Week 06 · Solo B m53-55 慢速**

### 🎯 今天一件事

聚焦「Solo B m53-55 慢速」：练 第 53-55 小节，达成下面的验收勾选项。

不碰：强力和弦节奏、闷音、提速（Phase 3）。

### ✅ 验收对齐

- [ ] 当日小节每个音按准、节奏对，慢速（60bpm）不断不错

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Solo B m53-55 慢速（第 53-55 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：当日小节 60bpm 连续弹 3 遍无错。

### ⚡ 时间不够时

当日小节 60bpm 连续弹 3 遍无错。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_01/week_06/day27_20261124/PLAN.md)

**Day 27 · 2026-11-13 · Week 04 · 全曲右手完整串联（慢速）**

### 🎯 今天一件事

聚焦「全曲右手完整串联（慢速）」：练 第1–106小节，达成下面的验收勾选项。

不碰：左手伴奏、双手合奏（Phase 2 才碰）、提速（Phase 3 才碰）。

### ✅ 验收对齐

- [ ] 第1–106小节 右手慢速连续 3 遍无错
- [ ] 全曲右手串联不断、不错（或指定分段）
- [ ] 记录本次串联的 3 个卡点及原因

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：Hanon + 音阶，70bpm |
| 5–40 min | P0 | 主练：全曲右手完整串联（慢速）（第1–106小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：完成 第1–106小节 慢练 + 至少一次完整串联并记下 3 个卡点。

### ⚡ 时间不够时

完成 第1–106小节 慢练 + 至少一次完整串联并记下 3 个卡点。

---
