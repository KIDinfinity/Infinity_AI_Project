# Week 06 · TASKS

## Task 1：Web 脚手架 + 聊天页（Day22 · 10-19）

### 做什么

在 `apps/web` 用 Vite 创建 React 18 + TS 项目，接入 Tailwind（官方 Vite 插件）与 react-router；Vite 代理 `/v1` 到后端；用 openapi-typescript 从 `/openapi.json` 生成类型；`src/api/client.ts` 类型化 fetch；`ChatPage` 完成非流式一问一答；Makefile 增加 `make web`。

### 为什么做

Web Console 是 M4 的地基；代理 + 生成类型让前后端契约从第一天就可校验，后面 3 天只在这个骨架上加功能。

### 资产锚点

M4.1（非流式最小切片）· 为 v0.4 做准备

### 前置依赖

W4 `/v1/kb/ask` 可用；W5 已有语料入库；Node ≥ 20.19、pnpm 可用。

### 具体执行步骤（概要，详见 day22 PLAN.md）

1. 确认后端与 `/openapi.json`；记录 ask 响应字段。
2. `pnpm create vite web --template react-ts`，锁定 React 18。
3. Tailwind（`@tailwindcss/vite`）+ react-router + 目录约定。
4. `vite.config.ts` 代理；`gen:api` 生成类型。
5. `client.ts` + `ChatPage.tsx` + `App.tsx` 路由。
6. Makefile `web`；提交。

### 验收标准

- [ ] `make web` 后 http://localhost:5173 可打开，Tailwind 样式生效
- [ ] 输入问题 → 显示答案；后端停掉时显示可读错误而不是白屏
- [ ] `src/types/api.ts` 由命令生成，`pnpm exec tsc --noEmit -p tsconfig.app.json` 0 错误

### 完成后的产出（文件路径）

`apps/web/{vite.config.ts,package.json}`、`apps/web/src/{App.tsx,main.tsx,index.css}`、`src/api/client.ts`、`src/pages/ChatPage.tsx`、`src/types/api.ts`、`Makefile`

### 求职映射

「契约驱动的前后端协作（OpenAPI → TS 类型）」「Vite 代理消除开发期 CORS」。

### 如果时间不够 / 没有必要

Enter 发送、自动滚动到底部、空状态插画 → P2，可删。

---

## Task 2：流式渲染 + 引用面板 + 状态（Day23 · 10-20）

### 做什么

`lib/sse.ts` + `hooks/useStreamingAnswer.ts`：用 fetch + ReadableStream 手动解析 `/v1/kb/ask/stream` 的 SSE（`retrieved → token → done`），AbortController 可取消；`AnswerMarkdown` 用 react-markdown + remark-gfm + rehype-sanitize 渲染，`[n]` 变为引用 chip；`CitationPanel` 显示标题 / 章节 / 片段 / 分数；5 种状态 idle / retrieving / streaming / done / error，拒答样式。

### 为什么做

流式 + 引用溯源是 RAG 产品体验的核心，也是面试最常被追问的前端 AI UX 点。

### 资产锚点

M4.1 · 为 v0.4 做准备

### 前置依赖

Task 1 完成；`curl -N` 能看到后端 SSE 帧。

### 具体执行步骤（概要，详见 day23 PLAN.md）

1. `curl -N` 记录真实事件名与 data 结构。
2. 写 `sse.ts` 帧解析 + `useStreamingAnswer`。
3. 安装 markdown 三件套，写 `AnswerMarkdown`。
4. 写 `CitationPanel`，接入 ChatPage 两栏布局。
5. 状态 / 拒答 / 错误 / 停止按钮；XSS 自测；提交。

### 验收标准

- [ ] 答案逐字出现，首 token 前显示「检索中」
- [ ] 点击 `[2]` → 右侧第 2 条引用高亮并滚动到可见
- [ ] 点「停止」后请求被取消（Network 面板显示 canceled），状态回到 idle
- [ ] 库外问题显示拒答样式；后端 500 显示错误条
- [ ] 手工把 `<img src=x onerror=alert(1)>` 放进答案文本，不弹窗

### 完成后的产出（文件路径）

`src/lib/sse.ts`、`src/hooks/useStreamingAnswer.ts`、`src/components/AnswerMarkdown.tsx`、`src/components/CitationPanel.tsx`、`src/types/ui.ts`

### 求职映射

「手写 SSE 解析器 + 可取消流式请求」「LLM 输出安全渲染」。

### 如果时间不够 / 没有必要

`@tailwindcss/typography` 美化、引用片段关键词高亮 → P2。

---

## Task 3：会话历史（SQLite）+ 反馈（Day24 · 10-21）

### 做什么

后端：`uv add sqlmodel`；`app/db/models.py`（Conversation / Message / Feedback）、`app/db/session.py`（`sqlite:///data/workpilot.db`，启动 `create_all`）；路由 `GET/POST /v1/conversations`、`GET /v1/conversations/{id}/messages`、`POST /v1/messages/{id}/feedback`；`/v1/kb/ask(/stream)` 接收 `conversation_id` 并落库。前端：左侧历史、👍/👎 + 原因下拉。脚本：`apps/api/scripts/export_feedback.py` 导出差评为 badcase 候选。

### 为什么做

没有历史就不是「产品」；反馈是 M3.6 在线闭环的数据源，W20 依赖它。

### 资产锚点

M4.1 M3.6 · 为 v0.4 做准备

### 前置依赖

Task 2 完成；流式 `done` 事件可携带额外字段。

### 具体执行步骤（概要，详见 day24 PLAN.md）

1. 模型 + session + lifespan 建表。
2. `crud.save_turn()`；ask / stream 落库，`done` 返回 `conversation_id`、`message_id`。
3. 会话 / 消息 / 反馈路由 + pytest。
4. 前端历史侧栏 + FeedbackBar。
5. 导出脚本；提交。

### 验收标准

- [ ] 刷新页面，左侧仍显示历史会话，点击可恢复消息并继续追问
- [ ] 👎 必须选原因；`sqlite3 apps/api/data/workpilot.db "select rating,reason from feedback"` 能看到
- [ ] `uv run python -m scripts.export_feedback` 生成 `eval/badcases/candidates-*.jsonl`
- [ ] `uv run pytest` 新增测试通过

### 完成后的产出（文件路径）

`apps/api/app/db/{models,session,crud}.py`、`app/routes/conversations.py`、`scripts/export_feedback.py`、`tests/test_conversations.py`、`apps/web/src/components/{ConversationList,FeedbackBar}.tsx`

### 求职映射

「设计会话 / 消息 / 反馈数据模型，差评自动进入 badcase 池」。

### 如果时间不够 / 没有必要

会话重命名、删除会话、按时间分组 → P2，删。

---

## Task 4：知识库管理页 + E2E 冒烟（Day25 · 10-22）

### 做什么

后端：`POST /v1/kb/upload`（multipart、≤10MB、扩展名白名单 md/pdf/html/txt、文件名清洗）→ 存 MinIO → BackgroundTasks 导入；`KBDocument` 表（status / error / chunks）；`GET /v1/kb/docs`、`DELETE /v1/kb/docs/{id}`（删 Qdrant 点 + MinIO 对象）、`GET /v1/kb/docs/{id}/chunks`。前端 `KnowledgePage`：拖拽上传、状态轮询、删除、查看分块。P1：Playwright E2E。tag `v0.4.0` + 周复盘。

### 为什么做

把导入从 CLI 变成产品功能，W7 云端 Demo 依赖它；E2E 是之后每次改动的安全网。

### 资产锚点

M4.2 M2.6 · **v0.4**

### 前置依赖

Task 3 完成（SQLite 已接入）；MinIO bucket 可写；W4 的 loader / chunk / embed / upsert 函数可复用，Qdrant payload 含 `doc_id`。

### 具体执行步骤（概要，详见 day25 PLAN.md）

1. `uv add python-multipart`；KBDocument 模型。
2. upload 路由（校验）+ `rag/jobs.py` 后台导入。
3. docs 列表 / 删除 / chunks 路由。
4. KnowledgePage + 轮询。
5. P1 Playwright（或手工清单）；tag + 复盘。

### 验收标准

- [ ] 上传 sample.md → 2 分钟内 ready → 提问能引用它
- [ ] `.exe` → 415；11MB → 413；文件名 `../../etc/passwd.md` 被清洗
- [ ] 删除后该 `doc_id` 在 Qdrant 中 count = 0，MinIO 对象不存在
- [ ] E2E 通过一次（截图或 `playwright show-report`）
- [ ] `git tag v0.4.0` 已推送

### 完成后的产出（文件路径）

`apps/api/app/routes/kb.py`、`app/rag/jobs.py`、`app/db/models.py`（KBDocument）、`apps/web/src/pages/KnowledgePage.tsx`、`apps/web/e2e/kb-flow.spec.ts`、`apps/web/e2e/fixtures/sample.md`

### 求职映射

「文件上传安全（大小 / 类型 / 路径穿越）」「异步导入状态机」「E2E 冒烟测试」。

### 如果时间不够 / 没有必要

Playwright → 改手工清单（写进 draft.md）；分块查看 → 顺延到 Day26 前 20 分钟；拖拽 → 只保留 `<input type="file">`。

---
