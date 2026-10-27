# 2026-11-11 周三 · TODO

> 共 3 个 plan 有今日任务

## AI — plan_ai

📂 [打开源 PLAN.md](../../../plan/plan_ai/phase_01/week_07/day28_20261111/PLAN.md)

**Day 28 · 2026-11-11 · Week 07 Task 3：云部署 + HTTPS + 访问保护**

### 🎯 今天一件事

把 WorkPilot 部署到一台 2C4G 云服务器：Caddy 自动 HTTPS、basic auth 保护 Demo、Qdrant / MinIO 不暴露公网、Embedding 切 SiliconFlow `BAAI/bge-m3`，用 `deploy.sh` 一条命令发布，公网带引用问答可用。

不碰：自动部署（W19）、登录系统（W19）、监控告警、CDN、多台机器、把 `data/corpus` 或任何公司内容传上服务器。

### ✅ 验收对齐

- [ ] `ssh root@<IP>` 与密码登录均被拒绝；`ssh -i ~/.ssh/workpilot_ed25519 deploy@<IP>` 可登录
- [ ] `curl -sI https://wp.<域名> | head -1` 返回 `401`；`curl -vI` 显示证书由 Let's Encrypt 或 ZeroSSL 签发
- [ ] 浏览器输入 basic auth 后：上传样例 → ready → 流式问答带引用 → 👎 反馈成功
- [ ] `nc -zvw3 <IP> 6333 9000 9001 8000` 全部失败，`nc -zvw3 <IP> 443` 成功
- [ ] 服务器 `stat -c %a ~/workpilot/.env` 输出 `600`
- [ ] `docs/runbook.md` 有「部署」章节；已 commit + push（不含任何密钥）

### ⏱ 时间块

| 时间    | 优先级 | 内容                                                                       |
| ------- | ------ | -------------------------------------------------------------------------- |
| 0–10    | P0     | 方案 A / B 确认，记录理由                                                  |
| 10–40   | P0     | 服务器初始化：deploy 用户、SSH 加固、ufw、Docker                           |
| 40–50   | P0     | DNS A 记录；生成 basic auth 哈希                                           |
| 50–75   | P0     | `docker-compose.prod.yml` + `Caddyfile.prod` + `deploy.sh` + 服务器 `.env` |
| 75–100  | P0     | 首次部署、seed 样例、逐项验证                                              |
| 100–115 | P0     | runbook 部署章节 + 提交                                                    |
| 115–120 | P1     | 记录首次构建耗时、内存占用（`docker stats --no-stream`）                   |

时间不足时最低保留：公网 HTTPS + basic auth + 问答一次（加固项中 SSH 禁密码不可省略）。

---

## 🎸吉他 — plan_guitar_rumbling

📂 [打开源 PLAN.md](../../../plan/plan_guitar_rumbling/phase_01/week_04/day18_2026-11-11/PLAN.md)

**Day 18 · 2026-11-11 · Week 04 · Verse A Rhythm1 m21-24**

### 🎯 今天一件事

聚焦「Verse A Rhythm1 m21-24」：练 第 21-24 小节，达成下面的验收勾选项。

不碰：Solo 旋律、Clean 分解、提速。

### ✅ 验收对齐

- [ ] 当日小节和弦切换干净、闷音到位、节奏对齐节拍器

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：Verse A Rhythm1 m21-24（第 21-24 小节） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

### ⚡ 时间不够时

右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍。

---

## 🎹钢琴 — plan_piano

📂 [打开源 PLAN.md](../../../plan/plan_piano/phase_01/week_04/day18_20261111/PLAN.md)

**Day 18 · 2026-11-04 · Week 03 · 第4页 第1-2行 右手慢练**

### 🎯 今天一件事

聚焦「第4页 第1-2行 右手慢练」：练 第64–67小节，达成下面的验收勾选项。

不碰：左手伴奏、双手合奏（Phase 2 才碰）、提速（Phase 3 才碰）。

### ✅ 验收对齐

- [ ] 第64–67小节 右手慢速（50-60bpm）连续 3 遍无错音、无错拍
- [ ] 第64–67小节 指法已固定并用铅笔标注
- [ ] 第64–67小节 能默弹一遍（背谱）

### ⏱ 时间块

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：C 大调 + G 大调音阶，60-70bpm |
| 5–40 min | P0 | 主练：第4页 第1-2行 右手慢练（第64–67小节） |
| 40–50 min | P0 | 复习：昨天/上一周已学段落，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：至少把 第64–67小节 前 4 小节慢速弹顺；其余顺延。

### ⚡ 时间不够时

至少把 第64–67小节 前 4 小节慢速弹顺；其余顺延。

---
