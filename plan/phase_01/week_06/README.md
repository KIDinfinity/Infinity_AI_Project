# Week 06 · AI Full-Stack：Web Console（Phase 1 · Day22–Day25 · 10-19 → 10-22）

## 1. 本周核心目标

把 W4–W5 只能用 curl / CLI 调用的 RAG 能力，做成**一个能给别人演示的 Web Console**：流式问答 + 可点击引用面板 + 会话历史 + 👍/👎 反馈入库 + 知识库上传管理，周末打 tag `v0.4.0`。

一句话验收：**浏览器上传一篇 Markdown → 状态变 ready → 提问 → 流式答案带 [n] 引用 → 点开看原文片段 → 给 👎 选原因 → 能导出为 badcase 候选。**

## 2. 资产锚点

| 构建模块                                 | 版本里程碑                | 本周结束 WorkPilot 能演示什么                                         |
| ---------------------------------------- | ------------------------- | --------------------------------------------------------------------- |
| M4.1 Chat（流式 / 引用 / 历史 / 反馈）   | 为 v0.4 做准备 → **v0.4** | 流式答案 + 引用 chip + 右侧引用面板 + 左侧历史会话 + 拒答样式         |
| M3.6 在线反馈闭环（前半段：入库 + 导出） | v0.4                      | 👎 + 原因落 SQLite，`export_feedback.py` 导出 jsonl                   |
| M4.2 知识库管理                          | v0.4                      | 拖拽上传 → pending/processing/ready/failed → 查看分块 → 删除          |
| M2.6 KB API（补齐）                      | v0.4                      | `/v1/kb/upload`、`DELETE /v1/kb/docs/{id}`、`/v1/kb/docs/{id}/chunks` |

## 3. 为什么这一周存在

- **前端是你的主场**：同一个 RAG，有流式、引用、拒答、反馈 UX 的版本，在面试和作品集中的说服力完全不同。AI Full-Stack / GenAI Application Engineer 的 JD 普遍要求「streaming UI、引用展示、用户反馈」。
- **反馈入库是 M3.6 闭环的起点**：W20 在线评测、W22 回归体系都依赖「用户 👎 → badcase → 回归用例」这条数据。
- **上传管理把「运维脚本导入」变成「产品功能」**：W7 部署到云端后，没有上传页就无法在云上换语料、做 Demo。
- 本周首次引入业务库 SQLite（SQLModel），为 W19 Postgres + Alembic 打底。

## 4. 本周在路线中的位置

```text
W5 产出：/v1/kb/ask + /v1/kb/ask/stream（SSE: retrieved → token → done）
         + 50 题评测基线 + badcases.md → v0.3
   ↓
W6 本周：apps/web（Vite + React 18 + TS + Tailwind）
         + SQLite（会话 / 消息 / 反馈 / 文档表）+ 上传 API + 知识库页 → v0.4.0
   ↓
W7 输入：两个可独立构建的应用（apps/api、apps/web）+ SQLite 文件路径可配置
         → Dockerfile / compose / Caddy / 云部署 / CI / 备份
```

## 5. 每日安排

| Day | 日期  | Task                               | 当日 P0 产出                            | 模块        | 状态 |
| --- | ----- | ---------------------------------- | --------------------------------------- | ----------- | ---- |
| 22  | 10-19 | Task 1：Web 脚手架 + 聊天页        | `make web` 打开页面，非流式一问一答可用 | M4.1        | TODO |
| 23  | 10-20 | Task 2：流式渲染 + 引用面板 + 状态 | 逐字输出 + [n] 可点击 → 右侧显示片段    | M4.1        | TODO |
| 24  | 10-21 | Task 3：会话历史（SQLite）+ 反馈   | 刷新后历史仍在；👎 + 原因入库；导出脚本 | M4.1 M3.6   | TODO |
| 25  | 10-22 | Task 4：知识库管理页 + E2E 冒烟    | 上传 → ready → 可问答；tag `v0.4.0`     | M4.2 / v0.4 | TODO |

## 6. 本周必须留下的资产（文件路径级）

```text
~/lab/workpilot/
├── Makefile                              # + web / web-build / web-types
├── apps/web/
│   ├── vite.config.ts                    # Tailwind 插件 + /v1 代理
│   └── src/
│       ├── App.tsx main.tsx index.css
│       ├── pages/ChatPage.tsx            # Day22–24
│       ├── pages/KnowledgePage.tsx       # Day25
│       ├── components/{AnswerMarkdown,CitationPanel,FeedbackBar,ConversationList}.tsx
│       ├── api/client.ts                 # 唯一调用后端的地方
│       ├── hooks/useStreamingAnswer.ts   # fetch + ReadableStream 解析 SSE
│       ├── lib/sse.ts
│       └── types/{api.ts(生成),ui.ts}
│   └── e2e/kb-flow.spec.ts               # P1：Playwright
├── apps/api/
│   ├── app/db/{models.py,session.py,crud.py}
│   ├── app/routes/{conversations.py,kb.py(扩展)}
│   ├── app/rag/jobs.py                   # 后台导入任务
│   └── scripts/export_feedback.py
└── eval/badcases/candidates-YYYYMMDD.jsonl
```

## 7. 本周验收标准

- [ ] PASS / FAIL：`make web` 后浏览器能流式问答，首 token 前显示「检索中」状态
- [ ] PASS / FAIL：答案中的 `[n]` 渲染为可点击 chip，右侧面板显示标题 / 章节 / 片段 / 分数
- [ ] PASS / FAIL：库外问题显示拒答样式（不是普通答案样式）；后端报错时有可读错误提示
- [ ] PASS / FAIL：答案 Markdown 中写入 `<script>` / `<img onerror>` 不会执行（rehype-sanitize 生效）
- [ ] PASS / FAIL：刷新页面后左侧会话历史仍在，可继续追问
- [ ] PASS / FAIL：👎 + 原因写入 SQLite；`export_feedback.py` 产出 jsonl
- [ ] PASS / FAIL：上传 md → ready → 能基于它回答；删除后 Qdrant 中该文档的点为 0
- [ ] PASS / FAIL：非法扩展名 / >10MB 被拒绝（415 / 413）
- [ ] PASS / FAIL：E2E（Playwright 或手工清单）通过一次并记录
- [ ] PASS / FAIL：tag `v0.4.0` 已推送到 Gitea

## 8. 求职映射

- **本周能力**：React + TS 的 AI UX（SSE 流式、引用溯源、拒答态、反馈采集）；契约驱动（OpenAPI → TS 类型）；FastAPI 文件上传与后台任务；SQLModel 数据建模。
- **简历 bullet 草稿**：
  - 基于 React 18 + TypeScript 实现 RAG 知识助手 Web Console，使用 fetch + ReadableStream 手动解析 SSE 实现流式渲染（首字延迟 ~\_\_s），答案段落级引用可点击溯源到原文片段。
  - 设计用户反馈闭环：👍/👎 + 5 类原因入库，差评一键导出为评测 badcase 候选，上线首周收集 ** 条反馈、转化 ** 条回归用例。
  - 实现文档上传 → 异步解析 → 分块 → 向量化入库的管理页，支持状态轮询、失败原因展示与级联删除（SQLite + Qdrant + MinIO）。
- **面试题**：
  1. 为什么不用 EventSource？fetch 解析 SSE 要注意什么？（POST + 自定义 header；按 `\n\n` 分帧；TextDecoderStream 处理多字节中文被拆包；AbortController 取消）
  2. 渲染 LLM 输出的 Markdown 有哪些安全风险？（XSS：原始 HTML、`javascript:` 链接；react-markdown 默认不渲染 HTML + rehype-sanitize 白名单）
  3. 用户反馈数据怎么用于改进 RAG？（分类 → 根因（检索 / 生成 / 语料）→ 加入评测集 → 修复后回归）

## 9. 本周禁止事项

- 不引入 UI 组件库（MUI / Ant Design）、状态管理库（Redux / Zustand）、Next.js、WebSocket。
- 不做登录 / 多用户 / 多空间（W19）、不上 Postgres / Alembic（W19）。
- 不做暗黑模式、国际化、移动端适配、动画打磨。
- 不引入 Celery / Redis 做任务队列（BackgroundTasks 足够，W19 再评估）。
- 不在页面上传任何公司文档（合规红线，DA01 §8）。

## 10. 时间不够时（最小保留）

1. Day23 流式 + 引用 chip（M4.1 核心卖点）
2. Day24 反馈入库（M3.6 起点）——历史列表可以只做「当前会话」不做侧栏
3. Day25 上传 + 状态（删除 / 分块查看 / Playwright 可顺延到 W7 第一天前 30 分钟）

## 11. 周复盘（Day25 末尾填写）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（录一段 30 秒屏幕录制留档）
- 是否出现无效学习 / 范围扩张（例如调样式超过 20 分钟）：\_\_\_\_
- 下周调整：\_\_\_\_
