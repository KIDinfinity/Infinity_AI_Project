# Day 23 · 2026-11-03 · 执行总结（SUMMARY）

> 对应计划：[PLAN.md](./PLAN.md)
> 今日目标：Task 2 —— 流式渲染 + 引用面板 + 状态（fetch + ReadableStream 手动解析 SSE）

---

## 一、结论一句话

用 `fetch + ReadableStream` 手动解析 `/v1/kb/ask/stream` 的 SSE，前端已完成「检索中 → 逐字输出 → `[n]` 引用 chip 可点击 → 右侧原文片段面板 → 拒答 / 错误 / 停止」五种状态，且通过 XSS 自测。**代码已写完、已 typecheck、已 build、已浏览器端到端验证通过，但按你的要求没有 commit / push。**

---

## 二、做了什么（按计划 Step 逐条）

### Step 0 · 确认真实帧格式（关键差异点）

计划里假设 `retrieved` 事件是 `citations`（字段 `index / doc_id / title / section / text / score`），但**真实后端（Day22 已有代码）实际返回的不是这样**。实测帧格式如下：

```text
event: retrieved
data: {"hits":[{"chunk_id":"...","score":0.5321,"doc_id":"...","title":"在组件间共享状态","section":"...","source":"...","snippet":"..."}]}

event: token
data: {"text":"Qdrant"}

event: done
data: {"refused":false,"prompt":"qa_answer.v1","citations":[{"n":1,"doc_title":"渲染列表","section":"...","source":"...","snippet":"...","score":0.697}],"usage":{...},"cost":0.002405,"latency_ms":2368,"ttft_ms":827}
```

两个必须适配的点：
1. **`retrieved` 给的是 `hits`**，每项字段是 `snippet`（不是 `text`），没有 `index`——前端按 `hits` 数组顺序（1..n）补上 `index`（与后端 prompt 里的引用编号一致）。
2. **`done` 里的 `citations` 字段名是 `n`、`doc_title`、`snippet`**（不是计划的 `index / title / text`）。后端 `done` 里**已经带 `refused`**，无需像计划里说的那样「顺手在后端补 P0」。

### Step 1 · SSE 帧解析 — [src/lib/sse.ts](/Users/infinity/lab/workpilot/apps/web/src/lib/sse.ts)

- `readSSE(body)` 异步生成器：按 `\n\n` 分帧、`data:` 多行拼接、`:开头` 心跳注释跳过、末尾半帧兜底解析。
- 用 `TextDecoderStream` 处理中文多字节 UTF-8 拆包（计划强调的重点）。
- `parseFrame` 解析 `event` / `data` 字段。

### Step 2 · 流式 Hook — [src/hooks/useStreamingAnswer.ts](/Users/infinity/lab/workpilot/apps/web/src/hooks/useStreamingAnswer.ts)

- 状态机 `idle / retrieving / streaming / done / error`；`AbortController` 管理取消。
- `retrieved` → `toCitations(hits)` 把真实 `hits` 映射成 `Citation{index,doc_id,title,section,text,score}`。
- `token` → 累加 `answer`；`error` → 抛错；`done` → 返回 `{answer,citations,refused,done}`。
- 用户点停止（`signal.aborted`）不算错误，回 `idle`；真实异常回 `error`。

### Step 3 · 安全 Markdown + 引用 chip — [src/components/AnswerMarkdown.tsx](/Users/infinity/lab/workpilot/apps/web/src/components/AnswerMarkdown.tsx)

- `react-markdown + remark-gfm + rehype-sanitize`（白名单清洗）。
- `toCiteLinks` 把 `[3]` 改写为 `[3](#cite-3)`，`components.a` 正则 `#cite-(\d+)` 命中则渲染成 `<button data-testid="citation-chip">`。

### Step 4 · 引用面板 + 接入 ChatPage

- [src/components/CitationPanel.tsx](/Users/infinity/lab/workpilot/apps/web/src/components/CitationPanel.tsx)：卡片 `id=cite-card-N`，`active===index` 时 `ring-2 ring-blue-500`，`useEffect` `scrollIntoView({block:'nearest'})`；标题 / 章节 / 片段（`line-clamp-6`）/ 分数（`toFixed(2)`）；附「在答案中被引用 x 次」（P2）。
- [src/pages/ChatPage.tsx](/Users/infinity/lab/workpilot/apps/web/src/pages/ChatPage.tsx)：两栏布局 `grid-cols-[minmax(0,1fr)_320px]`；`retrieving` 显示「正在检索知识库…」；`streaming` 逐字渲染 + 闪烁光标；`refused` 琥珀色边框 + 拒答提示；`error` 红色条 + 重试按钮；发送按钮在 streaming/retrieving 时变「停止」。

### Step 5 · XSS 自测 + 排版

- `index.css` 第二行加 `@plugin "@tailwindcss/typography";`（P1，`prose` 类生效，package.json 里已有该依赖）。
- XSS 自测用临时页 + 覆盖 `window.alert`，**结果通过**（见下），测完已删除临时文件。

---

## 三、改动文件清单

| 文件 | 动作 |
| --- | --- |
| `apps/web/src/types/ui.ts` | 新增：`Citation`、`StreamStatus` |
| `apps/web/src/lib/sse.ts` | 新增：SSE 解析器 |
| `apps/web/src/hooks/useStreamingAnswer.ts` | 新增：流式 Hook |
| `apps/web/src/components/AnswerMarkdown.tsx` | 新增：安全 Markdown + 引用 chip |
| `apps/web/src/components/CitationPanel.tsx` | 新增：引用面板 |
| `apps/web/src/pages/ChatPage.tsx` | 改写：两栏布局 + 流式 + 五种状态 |
| `apps/web/src/index.css` | 加 `@plugin "@tailwindcss/typography"` |
| `apps/web/package.json` + `pnpm-lock.yaml` | 依赖变化（react-markdown / remark-gfm / rehype-sanitize 原计划已装，typography 已在 devDeps，本次锁文件同步） |

---

## 四、验收结果（逐条对照计划第 3 节）

| # | 验收项 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 先「正在检索知识库…」，随后答案逐字出现 | ✅ | 浏览器实测：4ms 出现「正在检索知识库…」→ 794ms 首字 → 文本长度按 41→102→… 递增 |
| 2 | `[n]` 显示为 chip，点击后右侧第 n 条高亮并滚动 | ✅ | 生成 9 个 chip；点 `[3]` 后 `cite-card-3` 带 `ring-2`，面板 `scrollTop` 从 0 → 364，URL 无 `#cite-N` 跳转 |
| 3 | 卡片显示标题/章节/片段/分数(2位) | ✅ | 卡片含 `[1] 渲染列表 0.73` + 章节 + `line-clamp-6` 片段 |
| 4 | 点「停止」→ 请求 canceled，回 idle | ✅ | 捕获到 `requestFailed net::ERR_ABORTED`，停止后按钮回到「发送」 |
| 5 | 库外问题拒答；停 API 后错误条 + 重试 | ✅ | 「今天上海天气怎么样」→ 琥珀色「知识库中没有找到可靠依据」；拦截 API 后显示「无法连接后端 API…重试」，点重试恢复流式 |
| 6 | `<img onerror=alert(1)>` 不弹窗 | ✅ | 注入后 `window.alert` 调用次数 0，`<img>` 被移除，`javascript:` 链接被清洗，`[1]` 正常变 chip |
| 7 | 已 commit + push | ⏸️ 未执行 | **按你的要求「不用帮我提交代码」，已跳过** |

---

## 五、验收命令（完整命令，任何目录下都可直接复制运行）

> 前置：确认后端已启动（`make dev` 或 FastAPI :8000）。下面所有命令都是完整命令，无需 cd 到项目目录。

### 1. 后端健康检查（应返回 `{"status":"ok",...}`）

```bash
curl -s http://localhost:8000/health
```

### 2. 知识库文档列表（应返回非空数组，含 title/chunks）

```bash
curl -s http://localhost:8000/v1/kb/docs
```

### 3. 流式回答（核心验收：应看到 `event: retrieved` → 多条 `event: token` 逐字 → `event: done` 带 citations）

```bash
curl -N -s -X POST http://localhost:8000/v1/kb/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"React 组件里怎么过滤列表？"}'
```

**期望效果**：终端先打印 `event: retrieved`（`data` 里有 `hits` 数组、每项带 `snippet`/`score`），随后连续打印多条 `event: token`（`data` 里 `text` 逐字增长），最后打印 `event: done`（`data` 里 `refused:false`、`citations` 数组每项含 `n`/`doc_title`/`snippet`/`score`、`usage`、`ttft_ms`）。

### 4. 拒答场景（库外问题，应返回 `refused:true` 且 citations 为空）

```bash
curl -N -s -X POST http://localhost:8000/v1/kb/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"今天上海天气怎么样？"}'
```

**期望效果**：`event: retrieved` 的 `hits` 为空 → 一条 `event: token`（`text` 以「知识库中没有找到」开头）→ `event: done`（`data` 里 `refused:true`、`citations:[]`）。

### 5. 前端类型检查（应无输出、退出码 0）

```bash
cd ~/lab/workpilot/apps/web && pnpm exec tsc --noEmit -p tsconfig.app.json
```

### 6. 前端生产构建（应看到 `✓ built in`）

```bash
cd ~/lab/workpilot/apps/web && pnpm build
```

### 7. 前端浏览器验收（浏览器手动，完整步骤）

1. 打开 http://localhost:5173/ （Vite 已把 `/v1` 代理到 `:8000`）。
2. 输入「React 组件里怎么过滤列表？」回车：
   - 期望：先「● 正在检索知识库…」→ 答案逐字出现；答案里出现蓝色小方块 `[1]`~`[5]` 引用 chip；右侧「引用来源(5)」显示卡片（标题/章节/片段/分数）。
3. 点某个 chip（如 `[3]`）：
   - 期望：右侧第 3 张卡片出现蓝色描边 `ring-2` 并滚动到可见，页面不跳转、URL 不变。
4. 提问后立刻点「停止」：
   - 期望：按钮回到「发送」，Network 面板里 `ask/stream` 请求显示 `canceled`。
5. 输入「今天上海天气怎么样？」：
   - 期望：答案气泡呈琥珀色，顶部「知识库中没有找到可靠依据」。
6. 错误/重试：临时停掉后端（Ctrl+C 结束 uvicorn）再提问：
   - 期望：出现红色错误条「无法连接后端 API…重试」；重启后端后点「重试」可正常出答案。

---

## 六、真实帧格式与关键数字（产出记录回填）

| 项目 | 值 |
| --- | --- |
| `retrieved` 事件字段 | `hits[]`（字段 `chunk_id / score / doc_id / title / section / source / snippet`，无 `index`） |
| `done` 事件 citations 字段 | `n / doc_title / section / source / snippet / score`（无 `index / title / text`） |
| 首 token 延迟（后端 `ttft_ms`） | 827 ms（dense 检索 + DeepSeek 流式首字） |
| 前端首次可见文字延迟 | 约 794 ms（浏览器实测，与后端 ttft 一致） |
| XSS 自测 | `window.alert` 调用 0 次；`<img>`/`<script>` 被移除；`javascript:` 链接被清洗；`[1]` 正常变 chip |

---

## 七、卡点与备注

1. **计划假设字段与真实后端不符**（`retrieved.citations` vs 实际 `hits`，`done.citations[].index` vs 实际 `n`）。已按真实字段适配，前端 `Citation` 类型对上层屏蔽差异（统一为 `index/title/text/score`）。
2. **TS 类型问题**：`TextDecoderStream` 的 `writable` 类型是 `BufferSource`，比 `Uint8Array` 宽，`pipeThrough` 直接传会报 TS2345。已用 `as unknown as ReadableWritablePair<string, Uint8Array>` 断言解决。
3. 后端 `done` 已带 `refused`，无需 Step 2 里计划说的「P0 顺手在后端补」。
4. **未提交代码**：按你的要求跳过 `git add / commit / push`。当前工作区改动为 `M apps/web/*` + 新增 `components/hooks/lib/types` 目录，随时可提交。
