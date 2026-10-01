# Day 22 · 2026-10-19 · Week 06 Task 1：Web 脚手架 + 聊天页

## 0. 今天只做一件事

在 `apps/web` 建好 Vite + React 18 + TS + Tailwind + react-router 前端，经 Vite 代理调用 `/v1/kb/ask`，浏览器里完成一次非流式问答。

不碰：流式 / Markdown / 引用面板（Day23）、数据库与历史（Day24）、上传（Day25）、任何 UI 组件库或状态管理库、登录。

## 1. 资产锚点

- 构建模块：M4.1 Chat（见 plan/DA01_TARGET_ASSET.md §5）——今天完成「非流式聊天」最小切片
- 版本里程碑：为 v0.4 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make web` → http://localhost:5173 输入问题 → 显示 RAG 答案；前端类型由 OpenAPI 生成，后端字段改名时 `tsc` 直接报错
- 今日 AI 实际应用：「OpenAPI 契约 → TS 类型」把 W4 的 RAG API 变成类型安全的前端调用；Copilot 生成 JSX / Tailwind 样板，你只审数据流和错误处理

## 2. 起点（前置确认）

- 已有：`apps/api`（FastAPI，`/v1/kb/ask`、`/v1/kb/ask/stream`），Qdrant 中已有 W5 语料，Ollama bge-m3 运行中。需确认：

```bash
cd ~/lab/workpilot && git status && make dev   # 另开终端启动 API（W2 定义的命令，端口 8000）
curl -s -X POST localhost:8000/v1/kb/ask -H 'Content-Type: application/json' \
  -d '{"question":"FastAPI 如何声明依赖注入？"}' | python3 -m json.tool | head -30
node -v    # 需 ≥ 20.19（以 create-vite 提示为准）；不满足：brew install node@22
pnpm -v    # 没有：npm i -g corepack@latest && corepack enable && corepack prepare pnpm@latest --activate
```

把 ask 的**请求字段名**（如 `question`）和**响应字段名**（如 `answer` / `citations` / `refused`）记到 draft.md，下面代码以此为准。

## 3. 验收对齐（做完要能勾掉）

- [ ] `make web` 启动，http://localhost:5173 能打开，Tailwind 类名生效（按钮有颜色）
- [ ] 输入问题 → 页面显示后端答案；DevTools Network 中请求是 `localhost:5173/v1/kb/ask`（走代理，无 CORS 报错）
- [ ] 停掉 API 再发送 → 显示「请求失败」提示，页面不白屏
- [ ] `src/types/api.ts` 由命令生成；`pnpm exec tsc --noEmit -p tsconfig.app.json` 0 错误
- [ ] 已 commit + push 到 Gitea

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                |
| ------- | ------ | --------------------------------------------------- |
| 0–10    | P0     | 前置确认，记录 ask 字段                             |
| 10–30   | P0     | 创建项目、锁 React 18、Tailwind、react-router、目录 |
| 30–45   | P0     | Vite 代理 + 生成 OpenAPI 类型                       |
| 45–85   | P0     | `client.ts` + `ChatPage.tsx` + 路由，跑通一问一答   |
| 85–95   | P0     | Makefile + 提交                                     |
| 95–115  | P1     | Enter 发送 / Shift+Enter 换行、自动滚动到底部       |
| 115–120 | P2     | 空状态提示文案                                      |

时间不足时最低保留：项目能启动 + 代理通 + 一问一答显示。

## 5. 今日学习（只学完成任务必须的）

- Vite dev server 的 `server.proxy`：浏览器只访问 5173，同源请求由 Node 转发到 8000，开发期无需 CORS。
- Tailwind v4 用 `@tailwindcss/vite` 插件 + CSS 里一行 `@import "tailwindcss";`，不再需要 `tailwind.config.js`。
- openapi-typescript 把 FastAPI 自动生成的 OpenAPI 文档转成 `paths` / `components` 类型，前后端契约可被编译器检查。
- 资料：https://vite.dev/config/server-options.html#server-proxy 、https://tailwindcss.com/docs/installation/using-vite 、https://openapi-ts.dev/introduction 、https://reactrouter.com/home 、https://react.dev/learn

## 6. 执行步骤

### Step 1 · 创建项目并锁定版本

```bash
cd ~/lab/workpilot/apps
pnpm create vite web --template react-ts
cd web && pnpm install
# 模板可能默认 React 19，按固定技术栈锁到 18
pnpm add react@18 react-dom@18 react-router tailwindcss @tailwindcss/vite
pnpm add -D @types/react@18 @types/react-dom@18 openapi-typescript
mkdir -p src/{pages,components,api,hooks,lib,types} && rm -f src/App.css
```

目录约定（写进 `apps/web/README.md`）：`pages/` 路由级页面（ChatPage、Day25 KnowledgePage）· `components/` 纯展示组件，不直接 fetch · `api/` 唯一调用后端的地方（`client.ts`）· `hooks/` 有状态逻辑（Day23 `useStreamingAnswer`）· `lib/` 纯函数（Day23 SSE 解析）· `types/` `api.ts`（生成，勿手改）+ `ui.ts`（手写 UI 类型）。

### Step 2 · Tailwind + 代理（vite.config.ts）

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/v1": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
```

`src/index.css` 全部内容替换为一行：`@import "tailwindcss";`。生产环境由 Caddy 做同样的 `/v1` 反代（Day26）。

### Step 3 · 生成 API 类型

在 `package.json` 的 `scripts` 加：`"gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts"`，运行 `pnpm gen:api`，在生成的 `src/types/api.ts` 里搜 `Ask`，找到 ask 请求 / 响应在 `components["schemas"]` 中的真实名字（= Pydantic 类名），替换下文的 `AskRequest` / `AskResponse`。

### Step 4 · 类型化 fetch（src/api/client.ts）——理解：错误统一为 `ApiError`（页面只处理一种错误），所有 fetch 只在 `api/`

```ts
import type { components } from "../types/api";
// 名字以生成文件为准：FastAPI 用 Pydantic 模型类名作为 schema 名
export type AskRequest = components["schemas"]["AskRequest"];
export type AskResponse = components["schemas"]["AskResponse"];

export class ApiError extends Error {
  status: number;
  requestId?: string;
  constructor(status: number, message: string, requestId?: string) {
    super(message);
    this.status = status;
    this.requestId = requestId;
  }
}

export async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      const raw = body?.error?.message ?? body?.detail ?? message;
      message = typeof raw === "string" ? raw : JSON.stringify(raw);
    } catch {
      /* 响应不是 JSON，保留 statusText；上面兼容 Day27 的 {error:{message}} 与 FastAPI 默认 {detail} */
    }
    throw new ApiError(
      res.status,
      message,
      res.headers.get("x-request-id") ?? undefined,
    );
  }
  return (await res.json()) as T;
}

export const api = {
  ask: (body: AskRequest) =>
    request<AskResponse>("/v1/kb/ask", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
```

### Step 5 · 聊天页（src/pages/ChatPage.tsx）

```tsx
import { useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  error?: boolean;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const push = (m: Omit<ChatMessage, "id">) =>
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), ...m }]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    setInput("");
    push({ role: "user", content: question });
    setLoading(true);
    try {
      const res = await api.ask({ question });
      push({ role: "assistant", content: res.answer }); // 字段名以 Step 0 记录为准
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? `请求失败（${err.status}）：${err.message}`
          : "网络错误，请确认 API 已启动";
      push({ role: "assistant", content: msg, error: true });
    } finally {
      setLoading(false);
    }
  }
  // return (...)：JSX 按下方要点让 Copilot 生成
}
```

JSX 要点：外层 `mx-auto flex h-full max-w-3xl flex-col p-4`；`<ul className="flex-1 overflow-y-auto">` 渲染消息（用户右对齐蓝底、助手灰底、`error` 红底，`whitespace-pre-wrap`）；`loading` 时显示「思考中…」；底部 `<form onSubmit>` 内 `<textarea placeholder="输入问题">` + `<button disabled={loading}>发送</button>`（Day25 E2E 依赖这两个文案）。

`src/main.tsx` 用 `<BrowserRouter>`（`import { BrowserRouter } from 'react-router'`）包住 `<App />`；`src/App.tsx`：顶部导航 `NavLink` 到 `/` 与 `/kb`，`<Routes><Route path="/" element={<ChatPage />} /></Routes>`，外层 `h-screen flex flex-col`。这部分让 Copilot 生成，你只检查路由表。

### Step 6 · Makefile（recipe 行必须以 Tab 开头）+ 提交

```makefile
.PHONY: web web-build web-types
web:
	cd apps/web && pnpm dev
web-build:
	cd apps/web && pnpm build
web-types:
	cd apps/web && pnpm gen:api
```

```bash
make web            # 浏览器打开 http://localhost:5173 提问
pnpm --dir apps/web exec tsc --noEmit -p tsconfig.app.json
git status          # 确认 apps/web/node_modules、dist 未出现（模板自带 .gitignore）
git add apps/web Makefile
git commit -m "feat(web): scaffold vite react console with non-streaming chat page"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么用 Vite 代理而不是在 FastAPI 开 CORS？（答：浏览器视角同源，开发期免 CORS；生产由 Caddy 反代同样同源，前端代码在两种环境下都只写相对路径 `/v1/...`）
2. `src/types/api.ts` 为什么不能手改？（答：它是 OpenAPI 的派生物，下次 `gen:api` 会覆盖；改契约要改后端 Pydantic 模型再重新生成）
3. `BrowserRouter` 下直接刷新 `/kb` 为什么在生产可能 404？（答：服务器上不存在 `/kb` 文件，需要把未知路径回退到 `index.html`，即 Day26 的 `try_files {path} /index.html`）
4. `ApiError` 里为什么带 `requestId`？（答：Day27 后端会回传 `X-Request-ID`，前端报错时展示它，就能在日志里一键定位）

## 8. 对 DA-01 的贡献

WorkPilot 第一次有了「非工程师也能用」的入口。M4 后续所有页面（引用面板、知识库、W10 Agent 时间线、W15 Ops 看板）都长在今天的目录约定和 `api/client.ts` 上。

## 9. 求职映射（D 线）

- 岗位能力：React + TS 工程化、契约驱动开发、前后端联调
- 对应岗位：AI Full-Stack Engineer / GenAI Application Engineer
- 简历 bullet 草稿：基于 Vite + React 18 + TypeScript 搭建 RAG 助手 Web Console，通过 OpenAPI 自动生成前端类型，实现前后端契约编译期校验（接口改动 {x} 次，0 次线上字段不一致）。
- 面试可能问：
  - 「前后端类型怎么保持一致？」要点：后端 Pydantic 是唯一事实源 → OpenAPI → openapi-typescript → `tsc` 在 CI 中检查（Day29）。
  - 「开发环境跨域怎么处理？」要点：dev 用 Vite proxy、prod 用同域反代；不要在生产开 `allow_origins=["*"]`。

## 10. 卡住时的处理

| 现象                                                                | 处理                                                                                                                                 |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `You are using Node.js 18.x. Vite requires Node.js version 20.19+`  | `brew install node@22` 并按提示加 PATH，或用 nvm 切版本                                                                              |
| 代理报 `connect ECONNREFUSED ::1:8000`                              | Node 优先解析 `localhost` 为 IPv6，而 uvicorn 绑在 127.0.0.1：target 改为 `http://127.0.0.1:8000`                                    |
| Tailwind 类名没效果                                                 | 检查 `vite.config.ts` 是否加了 `tailwindcss()`、`index.css` 是否是 `@import "tailwindcss";`、`main.tsx` 是否 import 了 `./index.css` |
| 降级 React 18 后报 `Type 'X' is not assignable to type 'ReactNode'` | `@types/react` / `@types/react-dom` 也要降到 18，然后 `rm -rf node_modules && pnpm install`                                          |
| `Property 'answer' does not exist on type ...`                      | 生成类型与你写的字段名不一致——这正是类型生成的价值，按 `api.ts` 改前端                                                               |

## 11. 产出记录（执行时填写）

- ask 字段 / schema 名：{待填}；一次问答耗时（Network 面板）：{待填} s
- 卡点：{待填}；用时：{待填} 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day23（流式渲染 + 引用面板 + 状态）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
