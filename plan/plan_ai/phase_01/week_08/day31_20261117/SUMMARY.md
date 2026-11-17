# SUMMARY · Day 31（2026-11-17）· Demo 录制 + 技术复盘 8 问

执行入口：[day_plsn_prompt.md](../../../prompt/day_plsn_prompt.md) → 本目录 [PLAN.md](./PLAN.md)

## 一、本次做了什么

按 PLAN §6 执行步骤，完成可自动化的部分；Demo GIF 录制（Step 2）是**纯手工录屏**，无法由 AI 代为完成，已写好脚本与导出命令，等你录。

| Step | 内容 | 状态 |
| --- | --- | --- |
| Step 1 | 90 秒 Demo 脚本（5 镜头，照着录） | ✅ 已写（见下方「Demo 脚本」） |
| Step 2 | 录制 + 导出 GIF | ⚠️ 手工，未执行（命令见下方） |
| Step 3 | `docs/portfolio/p1.md` 8 问 | ✅ 已写（每个数字都来自评测报告/ADR，附证据链接） |
| Step 4 | 3 分钟讲稿（750–850 字） | ✅ 已写进 p1.md 末尾（约 800 字） |
| Step 5 | README 加「完整复盘」链接 | ✅ 已改 [README.md](../../../../lab/workpilot/README.md)（未 commit） |

产出文件（都在本地 `~/lab/workpilot`，**未提交**）：

- [docs/portfolio/p1.md](/Users/infinity/lab/workpilot/docs/portfolio/p1.md) —— 8 问 + 反思 + 3 分钟讲稿
- [README.md](/Users/infinity/lab/workpilot/README.md) —— 评测结果下新增「完整复盘：docs/portfolio/p1.md」
- `docs/assets/demo.gif` —— 仍是 1×1 占位（等你录完覆盖）

## 二、验收对齐（§3）逐项

| §3 验收项 | 状态 | 证据 |
| --- | --- | --- |
| demo.gif < 10MB，≤ 90 秒，5 镜头 | ⚠️ 待录 | 见「三、Demo 录制」 |
| README GIF 占位已替换 | ⚠️ 待录完覆盖 demo.gif | 链接行已加 |
| p1.md 8 问全部完成，每问「结论 + 数字/证据链接」 | ✅ | `grep -c "^## " p1.md` → 8 问 + 反思 + 讲稿 |
| p1.md 含 3 分钟讲稿，时长 2:30–3:15 | ⚠️ 待你朗读计时 | 讲稿约 800 字，读一遍约 2:40 |
| Demo 画面无公司信息/姓名/本机路径/API key | ⚠️ 录制时注意 | 终端 `PS1='$ '`、访客窗口 |
| 已 commit + push | ❌ 按你的要求未提交 | 见「四、未提交说明」 |

### p1.md 8 问速查（每问结论一句话）

1. 需要 RAG：知识分散、查找 10–30 分钟/次、周损 115 分钟，微调跟不上、长上下文贵且不溯源。
2. 选 Qdrant：payload 过滤 + 命名向量 hybrid + snapshot 快照，单容器运维轻，RTO 1 分钟。
3. Chunk：按标题切分 + 定长兜底，600/100/top5/dense，hit@5 = 0.921。
4. 评估：50 题（库内 30/库外 20），hit@k + MRR + 引用正确率 + LLM-judge。
5. Badcase：12 条，召回排序靠后 3 / 数据缺失 5 / 生成幻觉 1 / 过度拒答 1。
6. 降幻觉：检索隔离 + 引用约束 prompt + 阈值拒答 + 引用编号校验，引用正确率 1.0、拒答 1.0。
7. 控成本：逐调用计量，单次 ¥0.0020、50 题 ¥0.10、月约 ¥2.2。
8. 部署：Compose + Caddy（SSE 不缓冲）+ 2C4G + 备份 RTO 1 分钟。

## 三、Demo 录制（Step 1 脚本 + Step 2 命令）

### 90 秒 Demo 脚本（照着录）

| 秒 | 镜头 | 操作 | 画面必须出现 |
| --- | --- | --- | --- |
| 0–15 | ① 上传 | 打开 `/kb` → 拖入 `data/sample` 一篇 md | pending → processing → ready + 分块数 |
| 15–40 | ② 库内提问 | `/` 问「Vite 相比传统打包工具为什么更快？」 | 「检索中」→ 逐字输出 → `[1]` chip → 右侧片段高亮 |
| 40–55 | ③ 库外提问 | 问「明天上海天气怎样」 | 拒答文案「知识库中没有找到相关内容」 |
| 55–70 | ④ 反馈 | 对答案 👎 → 选 no_citation → 提交 | 「已反馈」 |
| 70–90 | ⑤ 评测 | VS Code 打开 `eval/reports/20261028-rag-v0.3.md` | hit@5=0.921 / 引用正确率 1.0 / 拒答 1.0 |

准备：访客窗口（无书签/扩展）、勿扰模式、终端 `PS1='$ '`、浏览器缩放 110%、窗口 1280×800。

### Step 2 导出 GIF

```bash
# 方案 A（推荐）Kap：选区录 1280×800 → 导出 GIF，FPS 12，宽度 960

# 方案 B QuickTime 录成 demo.mov 后转 GIF：
cd ~/lab/workpilot && mkdir -p docs/assets
ffmpeg -i ~/Desktop/demo.mov \
  -vf "fps=10,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  -loop 0 docs/assets/demo.gif
ls -lh docs/assets/demo.gif   # > 10MB 就把 fps 降到 8 或 scale 降到 800:-1
```

## 四、未提交说明

按你的要求**没有 commit/push**。当前 `~/lab/workpilot` 已有大量 Day30 未提交改动（含 `docs/assets/`、4 篇 ADR、deploy 脚本等），本次新增 p1.md、README 改动与它们混在同一工作区。等你录完 demo.gif，Step 5 的提交命令是：

```bash
cd ~/lab/workpilot
git add docs/assets/demo.gif docs/portfolio/p1.md README.md
git commit -m "docs: add 90s demo gif and P1 technical retrospective (8 questions)"
git push
```

## 五、服务验收 · 完整可运行 curl 命令（一验收点一条）

> 部署地址：`http://8.148.216.61`（公网 IP，HTTP 无 TLS），入口加了 basic_auth：用户名 `infinity`、密码 `123456`。
> 以下命令**任何目录**直接复制运行，无需 cd。

### 验收点 1 · 服务存活（health / ready）

```bash
curl -sS -u 'infinity:123456' http://8.148.216.61/health
# 期望：{"status":"ok","env":"prod","version":"0.0.1"}

curl -sS -u 'infinity:123456' http://8.148.216.61/ready
# 期望：{"status":"ready","checks":{"qdrant":"ok","db":"ok","llm_key":"ok"}}
```

### 验收点 2 · 知识库已入库（列出文档）

```bash
curl -sS -u 'infinity:123456' http://8.148.216.61/v1/kb/docs
# 期望：返回 JSON 数组，每项含 id / filename / status(ready) / chunks(分块数)
```

### 验收点 3 · 库内提问返回带引用答案（核心）

```bash
curl -sS -u 'infinity:123456' \
  -H 'Content-Type: application/json' \
  -d '{"question":"Vite 相比传统打包工具为什么更快？"}' \
  http://8.148.216.61/v1/kb/ask
# 期望：answer 非空、citations[] 非空、refused=false，附 usage/cost/latency_ms/message_id
```

### 验收点 4 · 库外提问正确拒答（防幻觉）

```bash
curl -sS -u 'infinity:123456' \
  -H 'Content-Type: application/json' \
  -d '{"question":"明天上海天气怎样"}' \
  http://8.148.216.61/v1/kb/ask
# 期望：{"answer":"知识库中没有找到与该问题相关的内容。","refused":true,"citations":[]}
```

### 验收点 5 · 反馈闭环（👎 + 原因入库）

先从上一步「验收点 3」的返回里取 `message_id`，替换下面 `<MESSAGE_ID>`：

```bash
curl -sS -u 'infinity:123456' \
  -H 'Content-Type: application/json' \
  -d '{"rating":"down","reason":"no_citation","comment":"引用与答案不对应"}' \
  http://8.148.216.61/v1/messages/<MESSAGE_ID>/feedback
# 期望：HTTP 201，反馈成功落库
```

> 注：`rating` 取 `up|down`；`down` 时 `reason` 必填，取 `wrong|no_citation|irrelevant|incomplete|other`。

### 验收点 6 · 流式回答（SSE 逐 token）

```bash
curl -sS -N -u 'infinity:123456' \
  -H 'Content-Type: application/json' \
  -d '{"question":"Vite 相比传统打包工具为什么更快？"}' \
  http://8.148.216.61/v1/kb/ask/stream
# 期望：逐行下发 SSE 事件，最后一条 done 事件携带 citations
```

---

## 六、遗留 / 待办

- **Demo GIF**：唯一未完成的 Step 2，需你本机录屏（Kap 或 QuickTime + ffmpeg）。
- **讲稿计时**：p1.md 讲稿需你朗读计时一次，确认落在 2:30–3:15。
- **badcase 条数口径**：PLAN §2 的 `grep -c "^## " badcases.md` 数的是二级标题（返回 3），不是 badcase 条数；真实 badcase 是 12 条（BC-001~BC-012），p1.md 已按 12 条写。
- **ADRs 命名**：仓库里 ADR 文件名是 `0001-llm-gateway / 0002-qdrant / 0004-handwritten-rag / 0005-compose-caddy`，README/PLAN 提到的 `0003-chunking-retrieval` 未在 `docs/adr/` 下（分块/检索决策记录在 0004 与实验报告里），p1.md 已据此链接。
