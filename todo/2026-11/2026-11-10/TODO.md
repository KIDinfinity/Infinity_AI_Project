# 2026-11-10 周二 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_01/week_07/day27_20261110/PLAN.md)

**Day 27 · 2026-11-10 · Week 07 Task 2：配置 / 健康检查 / JSON 日志 / request_id**

### 🎯 今天一件事

让 api 具备「上线后能被看见」的最小可观测性：配置缺失即启动失败、`/health` 与 `/ready` 分离、JSON 日志每行带 `request_id`、响应头回传 `X-Request-ID`、所有错误统一为 `{"error":{"code","message","request_id"}}`。

不碰：Trace / Span 表（W15）、成本看板（W15）、Prometheus / OpenTelemetry / ELK、日志轮转、告警。

### ✅ 验收对齐

- [ ] `.env` 删掉 `LLM_API_KEY` 后启动：进程立即退出，错误信息指明缺少的字段（恢复后正常）
- [ ] `APP_ENV=prod` 且 embedding 指向 `11434`（Ollama）时启动失败（prod 约束生效）
- [ ] `curl -i localhost:8080/v1/kb/docs` 响应头含 `X-Request-ID`，`make logs` 中该请求的访问日志 `request_id` 相同
- [ ] 带 `-H 'X-Request-ID: my-trace-0001'` 请求时被透传；带非法值（含空格 / 引号）时被替换为新 id
- [ ] `docker compose -p workpilot stop qdrant` 后 `curl -s localhost:8080/ready` → 503 + `checks.qdrant` 失败；恢复后 200
- [ ] 触发 404 / 422 / 500 时响应体均为统一格式，500 响应不含 Traceback 和密钥
- [ ] `uv run pytest -q` 通过（新增 3 个测试）；已 commit + push

### ⏱ 时间块

| 时间    | 优先级 | 内容                                                                           |
| ------- | ------ | ------------------------------------------------------------------------------ |
| 0–10    | P0     | 前置确认                                                                       |
| 10–25   | P0     | config.py fail fast + SecretStr + prod 校验                                    |
| 25–50   | P0     | logging.py（JsonFormatter）+ middleware.py（request_id + 访问日志 + 兜底 500） |
| 50–65   | P0     | errors.py 统一错误格式                                                         |
| 65–80   | P0     | health.py `/health` `/ready`                                                   |
| 80–100  | P0     | 3 个 pytest + compose 中验证 + 提交                                            |
| 100–110 | P1     | 把 `print` 改为 `logger`；LLM 调用日志带 model / tokens / latency              |
| 110–120 | P1     | 前端错误条显示 `request_id`（Day22 的 `ApiError.requestId`）                   |

时间不足时最低保留：request_id 中间件 + 统一错误体 + `/ready`。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_01/week_04/day17_2026-11-10/PLAN.md)

**Day 17 · 2026-11-10 · Week 04 · Verse A Rhythm1 m17-20**

### 🎯 今天一件事

聚焦「Verse A Rhythm1 m17-20」：练 第 17-20 小节，达成下面的验收勾选项。

不碰：Solo 旋律、Clean 分解、提速。

### ✅ 验收对齐

- [ ] 当日小节和弦切换干净、闷音到位、节奏对齐节拍器

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Verse A Rhythm1 m17-20（第 17-20 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

### ⚡ 时间不够时

右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_01/week_04/day17_20261110/PLAN.md)

**Day 17 · 2026-11-03 · Week 03 · 第3页全页右手串联**

### 🎯 今天一件事

聚焦「第3页全页右手串联」：练 第60–63小节，达成下面的验收勾选项。

不碰：左手伴奏、双手合奏（Phase 2 才碰）、提速（Phase 3 才碰）。

### ✅ 验收对齐

- [ ] 第60–63小节 右手慢速（50-60bpm）连续 3 遍无错音、无错拍
- [ ] 第60–63小节 指法已固定并用铅笔标注
- [ ] 第60–63小节 能默弹一遍（背谱）

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：C 大调 + G 大调音阶，60-70bpm |
| 5–40 min | P0 | 主练：第3页全页右手串联（第60–63小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：至少把 第60–63小节 前 4 小节慢速弹顺；其余顺延。

### ⚡ 时间不够时

至少把 第60–63小节 前 4 小节慢速弹顺；其余顺延。

---
