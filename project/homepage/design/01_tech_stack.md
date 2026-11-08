# 01 — 技术选型

## 1. 选型原则

1. **轻**：不引入重框架、重状态管理、重构建工具链
2. **熟**：优先用你日常技术栈（React/TypeScript），降低维护成本
3. **省**：AI 模型选免费/有免费额度的，部署选免费层
4. **秀**：技术组合本身要体现 AI 工程能力（streaming、token 管理、structured output）

## 2. 前端

| 层       | 选型                                        | 理由                                                                                            |
| -------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 框架     | **React 18** + **TypeScript**               | 你的主技术栈，面试官最可能问                                                                    |
| 构建     | **Vite**                                    | 快、零配置、React 官方推荐                                                                      |
| 样式     | **Tailwind CSS**                            | 原子化 CSS，快速出 UI，面试高频考点                                                             |
| 路由     | **react-router-dom**（仅工具模块用）        | 首页仍是单页滚动不用路由；工具数量会持续增长，需要独立可分享 URL + 按需加载，用最小范围引入路由 |
| 状态管理 | **不需要**                                  | 每个 Demo / 工具内部用 `useState` / `useReducer` 足够                                           |
| 代码高亮 | **Shiki** 或 **highlight.js**（按需加载）   | Demo 2 展示代码用                                                                               |
| 动画     | **CSS transition** + 少量 **framer-motion** | Hero 区微动效，不重                                                                             |
| 图标     | **Lucide React**                            | 轻量、Tree-shakable                                                                             |
| 暗色模式 | **Tailwind dark:** + `prefers-color-scheme` | 零 JS 开销                                                                                      |

### 为什么不选

| 不选             | 理由                             |
| ---------------- | -------------------------------- |
| Next.js          | 不需要 SSR/SSG，单页 Vite 够用   |
| Redux / Zustand  | 没有跨组件共享状态的需求         |
| Ant Design / MUI | 太重，Tailwind 手写更快更轻      |
| shadcn/ui        | 可以但没必要，组件太少不值得引入 |

## 3. AI 层

### 3.1 模型选择

| 模型                        | 免费额度                   | 调用方式               | 推荐           |
| --------------------------- | -------------------------- | ---------------------- | -------------- |
| **Google Gemini Flash 2.0** | 免费 1500 req/day          | Gemini API SDK 或 REST | ⭐ 首选        |
| DeepSeek V3                 | 免费 500 req/day（注册送） | OpenAI 兼容 API        | 备选           |
| Groq (Llama 3.3 70B)        | 免费 tier                  | OpenAI 兼容 API        | 备选（速度快） |
| Ollama 本地                 | 完全免费                   | 本地 localhost         | 本地开发用     |

**推荐方案**：线上用 **Gemini Flash**（免费额度够展示用），本地开发用 **Ollama + qwen2.5:3b**（完全免费、无网络依赖）。

### 3.2 API 封装

```typescript
// 统一 AI 调用接口，屏蔽不同提供商的差异
interface AiRequest {
  model: "gemini-flash" | "deepseek" | "groq" | "ollama";
  messages: { role: "system" | "user" | "assistant"; content: string }[];
  maxTokens?: number; // 默认 1024
  temperature?: number; // 默认 0.7
  stream?: boolean; // 默认 true
}

interface AiResponse {
  content: string;
  usage: { promptTokens: number; completionTokens: number };
  model: string;
}
```

### 3.3 Token 限制策略

```
硬限制：单次请求 input + output ≤ 2048 tokens
  ├── input: 用 tiktoken 或 gpt-tokenizer 估算
  │   └── 超过 1500 时截断用户输入 + 警告提示
  └── output: max_tokens 参数设为 1024
```

## 4. 工具层

工具箱采用「注册表 + 懒加载路由」模式，核心是让后续加工具不用碰架构代码。完整设计见 [05_tools.md](05_tools.md)，这里只列和技术选型相关的决策。

| 层            | 选型                                            | 理由                                                      |
| ------------- | ----------------------------------------------- | --------------------------------------------------------- |
| 路由          | **react-router-dom**                            | 工具需要独立可分享 URL（`/tools/:slug`）                  |
| 代码分割      | **React.lazy + Suspense**                       | 每个工具独立 chunk，不加工具不影响首页加载速度            |
| 工具元数据    | 静态数组 `src/tools/registry.ts`                | 新增工具 = 追加一条数据 + 一个组件文件，不改布局/路由代码 |
| 代码高亮/校验 | 按工具需要各自引入（如 JSON 用 `ajv` 轻量校验） | 避免把所有工具的依赖都打进主 bundle                       |

## 5. 部署

| 层       | 选型                                                | 理由                                          |
| -------- | --------------------------------------------------- | --------------------------------------------- |
| 静态托管 | **Vercel**（免费 Hobby 层）或 **GitHub Pages**      | 零成本、自动 HTTPS、CI/CD                     |
| AI 代理  | **Vercel Serverless Functions** 或 **直接前端调用** | 代理可隐藏 API Key；直接调用更简单但 Key 暴露 |
| 域名     | 可选自定义域名                                      | Vercel 自带 `*.vercel.app` 够用               |

### AI Key 安全方案

```
方案 A（推荐）：Vercel Edge Function 做代理
  前端 → /api/ai  → Gemini API（Key 在服务端环境变量）

方案 B（最简单）：前端直连
  前端 → Gemini API（Key 在 .env，build 时注入）
  风险：Key 暴露在浏览器 Network 面板
  适用：免费 Key、展示用途，泄露也无经济损失
```

**建议先用方案 B（最快上线），后续切方案 A。**

## 6. 开发工具

| 工具              | 用途                                |
| ----------------- | ----------------------------------- |
| pnpm              | 包管理（快、省磁盘）                |
| ESLint + Prettier | 代码规范                            |
| Vitest            | 单元测试（Demo/工具组件的核心逻辑） |
| Playwright        | E2E（可选，验证 Demo/工具交互正常） |
