# Day 22 · 2026-11-02 · SUMMARY

> 对应 [PLAN.md](./PLAN.md) 的执行结果。结论：**Task 1 全部 P0 完成，P1/P2 一并实现**；按用户要求**未提交代码**。

## 一、做了什么（按 Step 对照）

| Step | 内容 | 结果 |
| --- | --- | --- |
| Step 1 | 建 Vite + React 18 + TS + Tailwind + react-router 项目，锁 React 18，建目录约定 | ✅ 完成（未用交互式 `pnpm create vite`，改为手写等价脚手架后 `pnpm install`，避免交互卡住） |
| Step 2 | Tailwind v4（`@tailwindcss/vite`）+ Vite 代理 `/v1` → `127.0.0.1:8000` | ✅ 完成，`vite.config.ts` 代理目标直接用 `127.0.0.1`（规避 IPv6 坑） |
| Step 3 | 生成 API 类型 `src/types/api.ts` | ✅ 完成，`pnpm gen:api` 成功（22365 字节） |
| Step 4 | `api/client.ts` 类型化 fetch，错误统一为 `ApiError` | ✅ 完成 |
| Step 5 | `ChatPage.tsx` + 路由（`main.tsx`/`App.tsx`） | ✅ 完成，含 Enter 发送 / Shift+Enter 换行、自动滚动、空状态文案 |
| Step 6 | Makefile 加 `web` / `web-build` / `web-types` | ✅ 完成（**未 commit / push**） |

## 二、关键实现决策（偏离计划的 3 处，均有必要）

1. **真实 schema 名与计划示例不同**：OpenAPI 里有两个同名 `AskReq`（`/v1/ask` 与 `/v1/kb/ask`），FastAPI 用模块路径消歧义，生成名是 `app__routes__kb__AskReq`；响应是 `KBAnswer`。`client.ts` 据此写成：
   - 请求：`components["schemas"]["app__routes__kb__AskReq"]`（字段 `question`）
   - 响应：`components["schemas"]["KBAnswer"]`（字段 `answer` / `citations` / `refused` / `retrieved` / `usage` / `cost` / `latency_ms`）
2. **react-router 必须锁 v7**：`pnpm add react-router` 默认解析到 v8.5.1，它要求 React ≥ 19（用 `useOptimistic`），与计划的 React 18 冲突。已改锁 `react-router@7`（7.18.5）。
3. **TypeScript 必须锁 5.x**：默认解析到 TS 7.0.2，而 `openapi-typescript@7.13.0` 依赖 TS `^5.x`（TS 7 移除 `ts.factory` API 会崩溃）。已改锁 `typescript@5`（5.9.3）。

## 三、变更文件清单

**新增**（`apps/web/`，均已 gitignore `node_modules`/`dist`）：
- `package.json`、`pnpm-lock.yaml`
- `vite.config.ts`、`index.html`、`.gitignore`
- `tsconfig.json`、`tsconfig.app.json`、`tsconfig.node.json`
- `src/main.tsx`、`src/App.tsx`、`src/index.css`、`src/vite-env.d.ts`
- `src/pages/ChatPage.tsx`、`src/api/client.ts`
- `src/types/api.ts`（由 `pnpm gen:api` 生成，勿手改）

**修改**：
- `Makefile`（新增 `web` / `web-build` / `web-types` 三个 recipe 及 `.PHONY` 声明）
- `apps/web/README.md`（写入目录约定与常用命令）

## 四、验收（每一条：完整命令 + 预期结果）

> 前置：先起两个进程（两个终端）——
> ```bash
> cd ~/lab/workpilot && make dev    # 终端 A：API，监听 127.0.0.1:8000
> cd ~/lab/workpilot && make web    # 终端 B：前端，监听 localhost:5173
> ```
> 注意：Vite 绑定在 `localhost`（IPv6 ::1），所以前端用 `localhost:5173`；API 用 `127.0.0.1:8000`。两者不能互换（`127.0.0.1:5173` 会连不上）。

### 验收 1 — `make web` 启动 + Tailwind 类名生效

```bash
# 页面返回 HTML（含 <div id="root">）
curl -s http://localhost:5173/ | grep -o '<div id="root"></div>'

# Tailwind 编译出按钮蓝色工具类（有输出即说明 Tailwind 生效）
curl -s http://localhost:5173/src/index.css | grep -o 'bg-blue-600'
```

预期：第一条输出 `<div id="root"></div>`；第二条输出 `bg-blue-600`。浏览器打开 http://localhost:5173 可见蓝色「发送」按钮。

### 验收 2 — 输入问题 → 显示后端答案（走代理，无 CORS）

```bash
curl -s -X POST http://localhost:5173/v1/kb/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"FastAPI 请求体里怎么声明嵌套模型？"}' | python3 -m json.tool
```

预期：返回 JSON，`answer` 是带 `[1]` 引用的自然语言回答，`citations` 数组非空，`refused` 为 `false`。该请求走 `localhost:5173/v1/kb/ask` → Vite 代理 → `127.0.0.1:8000`，同源无 CORS 报错。

（验证确实没跨域：请求头里没有 `Origin` 校验失败的迹象，响应可直接拿到；前端代码只写相对路径 `/v1/kb/ask`。）

### 验收 3 — 停掉 API 再发送 → 显示「请求失败」，不白屏

```bash
# 第 1 步：在终端 A（make dev）按 Ctrl+C 停掉 API，然后确认已停（输出 000）
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health

# 第 2 步：再走代理发请求，Vite 代理返回 502
curl -s -o /dev/null -w "proxy: %{http_code}\n" \
  -X POST http://localhost:5173/v1/kb/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"测试"}'
```

预期：第一步输出 `000`（API 已停）；第二步输出 `proxy: 502`。此时浏览器里点「发送」，页面显示红底提示 `请求失败（502）：Bad Gateway`，而不是白屏（前端 `ChatPage.tsx` 的 `try/catch` 捕获 `ApiError` 后渲染 `error` 消息）。

### 验收 4 — 类型由命令生成 + `tsc` 0 错误

```bash
cd ~/lab/workpilot/apps/web

# 4a. 重新生成类型（需 API 已运行；会覆盖 src/types/api.ts）
pnpm gen:api

# 4b. 类型检查（无输出、exit 0 即通过）
pnpm exec tsc --noEmit -p tsconfig.app.json && echo "tsc OK"

# （可选）完整生产构建也应通过
pnpm build && echo "build OK"
```

预期：`pnpm gen:api` 打印 `openapi.json → src/types/api.ts`；`tsc` 无任何输出并打印 `tsc OK`；`pnpm build` 打印 `✓ built` 并打印 `build OK`。

### 验收 5 — commit + push

按用户要求**跳过**（未执行 `git add` / `git commit` / `git push`）。若之后要提交：

```bash
cd ~/lab/workpilot
git add apps/web Makefile
git commit -m "feat(web): scaffold vite react console with non-streaming chat page"
git push
```

## 五、产出记录

- ask 请求字段：`question`（必填，2–2000 字）；可选 `top_k`、`filters`
- ask 响应字段：`answer`（string）、`citations`、`retrieved`、`refused`、`prompt`、`usage`、`cost`、`latency_ms`
- 依赖锁定：`react@18.3.1`、`react-dom@18.3.1`、`react-router@7.18.5`、`tailwindcss@4.3.3`、`@tailwindcss/vite@4.3.3`、`typescript@5.9.3`、`vite@8.3.5`、`openapi-typescript@7.13.0`
- 卡点与处理：3 处版本/schema 名偏差，均已修复（见「二」）
