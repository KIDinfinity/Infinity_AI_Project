# 2026-11-09 周一 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_01/week_07/day26_20261109/PLAN.md)

**Day 26 · 2026-11-09 · Week 07 Task 1：Dockerfile + compose 全栈**

### 🎯 今天一件事

写出 api / web 两个 Dockerfile、Caddyfile 和 dev compose，让 `make up` 一条命令在本机起 api + web(Caddy) + qdrant + minio，浏览器 http://localhost:8080 完成上传 → 流式问答。

不碰：云服务器（Day28）、JSON 日志 / `/ready`（Day27）、CI（Day29）、镜像推送到 Registry、K8s。

### ✅ 验收对齐

- [ ] `make up` 成功；`make ps` 显示 api / qdrant / minio 为 healthy，web 为 running
- [ ] http://localhost:8080 上传样例 md → ready → 流式问答（逐字）带引用
- [ ] 直接访问 http://localhost:8080/kb 并刷新，不出现 404
- [ ] `docker compose -p workpilot exec api id` 显示 `uid=10001(app)`（非 root）
- [ ] `make down && make up` 后会话历史与文档仍在
- [ ] 镜像中不含 `.env`：`docker compose -p workpilot exec api ls -a /app | grep -c '^.env$'` 输出 0
- [ ] 已 commit + push

### ⏱ 时间块

| 时间    | 优先级 | 内容                                                   |
| ------- | ------ | ------------------------------------------------------ |
| 0–10    | P0     | 前置确认，记录变量名                                   |
| 10–35   | P0     | api Dockerfile + `.dockerignore`，单独 build 验证      |
| 35–55   | P0     | web Dockerfile + Caddyfile                             |
| 55–85   | P0     | compose + Makefile，`make up` 排错到全绿               |
| 85–105  | P0     | 浏览器全流程 + 持久化验证 + 提交                       |
| 105–115 | P1     | `data/sample` + `scripts/seed_sample.sh` + `make seed` |
| 115–120 | P2     | 记录镜像大小，尝试 BuildKit cache mount                |

时间不足时最低保留：api + web + qdrant + minio 能起，浏览器能问答一次。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_01/week_04/day16_2026-11-09/PLAN.md)

**Day 16 · 2026-11-09 · Week 04 · Verse A Rhythm1 m13-16**

### 🎯 今天一件事

聚焦「Verse A Rhythm1 m13-16」：练 第 13-16 小节，达成下面的验收勾选项。

不碰：Solo 旋律、Clean 分解、提速。

### ✅ 验收对齐

- [ ] 当日小节和弦切换干净、闷音到位、节奏对齐节拍器

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Verse A Rhythm1 m13-16（第 13-16 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

### ⚡ 时间不够时

右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_01/week_04/day16_20261109/PLAN.md)

**Day 16 · 2026-11-02 · Week 03 · 第3页 第3-4行 右手慢练**

### 🎯 今天一件事

聚焦「第3页 第3-4行 右手慢练」：练 第56–59小节，达成下面的验收勾选项。

不碰：左手伴奏、双手合奏（Phase 2 才碰）、提速（Phase 3 才碰）。

### ✅ 验收对齐

- [ ] 第56–59小节 右手慢速（50-60bpm）连续 3 遍无错音、无错拍
- [ ] 第56–59小节 指法已固定并用铅笔标注
- [ ] 第56–59小节 能默弹一遍（背谱）

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：C 大调 + G 大调音阶，60-70bpm |
| 5–40 min | P0 | 主练：第3页 第3-4行 右手慢练（第56–59小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：至少把 第56–59小节 前 4 小节慢速弹顺；其余顺延。

### ⚡ 时间不够时

至少把 第56–59小节 前 4 小节慢速弹顺；其余顺延。

---
