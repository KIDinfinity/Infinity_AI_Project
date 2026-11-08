# 05 — 工具箱设计（可扩展小工具系统）

> 背景：个人主页内容分三大支柱（AI 演示 / AI 资讯 / 常用小工具），其中「常用小工具」会持续、不定期新增。本设计的目标只有一个：**让"加一个新工具"始终是一次低成本、低风险的操作**，不需要碰路由、布局、首页代码。

## 1. 为什么做成「注册表 + 懒加载路由」

| 方案                       | 问题                                            |
| -------------------------- | ----------------------------------------------- |
| 每加一个工具就改首页布局   | 首页代码随工具数量线性膨胀，迟早改出 bug        |
| 所有工具打进一个大 bundle  | 工具越多首页越慢，违反「首屏 < 2s」的非功能需求 |
| 工具散落在各处没有统一清单 | 不知道现在有哪些工具、容易重复造轮子            |

**采用方案**：

1. 唯一数据源 `src/tools/registry.ts`，一个数组，一条记录 = 一个工具的全部元信息。
2. 每个工具是一个自包含组件，用 `React.lazy` 动态引入，天然按工具分 chunk。
3. 路由只有 3 条，和工具数量无关：`/`、`/tools`、`/tools/:slug`。

## 2. 目录结构约定

```text
src/tools/
├── registry.ts            # 唯一事实来源：工具元数据数组
├── json-formatter/
│   ├── index.tsx           # 工具组件（default export）
│   └── logic.ts            # 纯函数逻辑（可单测，不含 JSX）
├── regex-tester/
│   ├── index.tsx
│   └── logic.ts
└── markdown-preview/
    └── index.tsx
```

- 每个工具一个子目录，子目录名 = `slug`（kebab-case，和路由一致）。
- 工具内部逻辑和 UI 尽量拆开（`logic.ts` 纯函数 + `index.tsx` 组件），方便 Vitest 单测核心逻辑。
- 工具之间不互相 import，不共享状态，删除一个目录就等于完整移除一个工具。

## 3. ToolMeta 数据结构

```typescript
// src/tools/registry.ts
import type { LucideIcon } from "lucide-react";
import { Braces, Regex, FileText } from "lucide-react";

export type ToolCategory = "dev" | "text" | "convert" | "ai-enhanced" | "misc";

export interface ToolMeta {
  slug: string; // "json-formatter"，对应路由 /tools/:slug
  name: string; // "JSON 格式化 / 校验"
  description: string; // 一句话说明，展示在 ToolCard 上
  category: ToolCategory;
  icon: LucideIcon;
  usesAi: boolean; // true 时必须复用 useAiChat + token 限制（见 §7）
  featured?: boolean; // true 时出现在首页 ToolboxPreview
  component: () => Promise<{ default: React.ComponentType }>; // 懒加载入口
}

export const TOOLS_REGISTRY: ToolMeta[] = [
  {
    slug: "json-formatter",
    name: "JSON 格式化 / 校验",
    description: "粘贴 JSON，自动格式化、校验语法、一键压缩",
    category: "dev",
    icon: Braces,
    usesAi: false,
    featured: true,
    component: () => import("./json-formatter"),
  },
  {
    slug: "regex-tester",
    name: "正则表达式测试器",
    description: "实时测试正则匹配结果，高亮命中片段",
    category: "dev",
    icon: Regex,
    usesAi: false,
    featured: true,
    component: () => import("./regex-tester"),
  },
  {
    slug: "markdown-preview",
    name: "Markdown 实时预览",
    description: "左边写 Markdown，右边实时看渲染效果",
    category: "text",
    icon: FileText,
    usesAi: false,
    featured: true,
    component: () => import("./markdown-preview"),
  },
  // 新增工具只需在此数组追加一项，不需要改任何其他文件
];
```

## 4. 新增一个工具的标准流程（Checklist）

1. 确定 `slug`（kebab-case）、`category`、是否需要 AI（`usesAi`）。
2. 在 `src/tools/<slug>/` 下新建 `index.tsx`（必要时拆 `logic.ts`）。
3. 组件内部状态自包含，不读写任何全局 store。
4. 若 `usesAi: true`：必须通过已有的 `useAiChat` + `src/lib/ai-client.ts` 调用模型，并遵守 §7 的 token 预算，不自建新的 AI 调用路径。
5. 在 `registry.ts` 追加一条 `ToolMeta`；如果想让它出现在首页预览区，设 `featured: true`（**首页最多展示 6 个 `featured`，超过时按数组顺序截取前 6 个**）。
6. 本地跑 `pnpm build`，确认产物里出现独立的 `<slug>-*.js` chunk（验证代码分割生效）。
7. 若逻辑可单测（`logic.ts`），补一个 `logic.test.ts`。
8. 移动端走查一遍（Chrome DevTools 模拟 iPhone），确认可用。

> 不需要改的文件：`App.tsx`、`pages/HomePage.tsx`、`pages/ToolsIndexPage.tsx`、`pages/ToolDetailPage.tsx`、任何路由配置。

## 5. 路由设计

| 路径           | 页面             | 说明                                                                                                                      |
| -------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `/`            | `HomePage`       | 单页滚动主页，`ToolboxPreview` 只展示 `featured` 工具                                                                     |
| `/tools`       | `ToolsIndexPage` | 展示 `TOOLS_REGISTRY` 全部工具，支持按 `category` 筛选                                                                    |
| `/tools/:slug` | `ToolDetailPage` | 按 `slug` 从 registry 查找 `ToolMeta`，`React.lazy` 懒加载对应组件渲染；`slug` 找不到时显示 404 提示 + 返回 `/tools` 链接 |

```typescript
// src/pages/ToolDetailPage.tsx（核心逻辑示意）
import { lazy, Suspense } from 'react';
import { useParams, Link } from 'react-router-dom';
import { TOOLS_REGISTRY } from '../tools/registry';

export function ToolDetailPage() {
  const { slug } = useParams();
  const meta = TOOLS_REGISTRY.find(t => t.slug === slug);

  if (!meta) {
    return (
      <div>
        <p>工具不存在</p>
        <Link to="/tools">返回工具箱 →</Link>
      </div>
    );
  }

  const LazyTool = lazy(meta.component);

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <LazyTool />
    </Suspense>
  );
}
```

## 6. 分类体系

| category      | 含义        | 示例                             |
| ------------- | ----------- | -------------------------------- |
| `dev`         | 开发辅助    | JSON 格式化、正则测试、Cron 解析 |
| `text`        | 文本处理    | Markdown 预览、文本去重          |
| `convert`     | 格式转换    | Base64/URL 编解码、时间戳转换    |
| `ai-enhanced` | 需要调用 AI | Commit Message 生成器            |
| `misc`        | 其他        | 颜色对比度检查                   |

`ToolsIndexPage` 按 `category` 做纯前端筛选（`Array.filter`），不需要后端或 URL query 参数（工具量级不大，没必要做复杂筛选状态管理）。

## 7. AI 增强工具的特殊规则

凡 `usesAi: true` 的工具，必须满足：

1. **复用而非重建**：调用方式必须走 `src/lib/ai-client.ts` 的 `createAiClient()` 和 `src/hooks/useAiChat.ts`，与 3 个 Demo 共用同一套客户端和 token 限制逻辑（见 [03_ai_integration.md](03_ai_integration.md) §2）。
2. **Token 预算不可突破**：沿用全局 `AI_CONFIG`（`MAX_INPUT_TOKENS` / `MAX_OUTPUT_TOKENS` / `MAX_TOTAL_TOKENS`），不允许为某个工具单独放宽。
3. **各自的 system prompt**：放在 `src/lib/prompts.ts`，命名约定 `<SLUG>_SYSTEM_PROMPT`（下划线大写），和 Demo 的 prompt 放在一起，便于统一审查。
4. **错误处理复用**：直接使用 Demo 区已定义的 `AiError` 类型和 `ErrorDisplay` 组件，不重复实现。

## 8. 候选工具清单

> 产品侧优先级见 [00_overview.md](00_overview.md) §5，这里只做技术侧备注。

| 工具                  | 需要的额外依赖                          | 备注                                                                         |
| --------------------- | --------------------------------------- | ---------------------------------------------------------------------------- |
| JSON 格式化 / 校验    | `ajv`（轻量 JSON Schema 校验，可选）    | 原生 `JSON.parse` 已能覆盖格式化+报错                                        |
| 正则表达式测试器      | 无（原生 `RegExp`）                     | 注意处理无效正则的 try/catch                                                 |
| Markdown 实时预览     | `marked` 或 `markdown-it`（轻量二选一） | 渲染结果需 `DOMPurify` 消毒，防 XSS                                          |
| 时间戳 ⇄ 日期转换     | 无（原生 `Date`）                       | 支持秒级/毫秒级自动识别                                                      |
| Base64 / URL 编解码   | 无（原生 `atob`/`encodeURIComponent`）  | —                                                                            |
| Commit Message 生成器 | 复用 `ai-client`                        | `usesAi: true`，输入 diff 摘要，输出符合 Conventional Commits 格式的 message |

## 9. 安全与验收标准

- **XSS 防护**：任何把用户输入渲染为 HTML 的工具（如 Markdown 预览）必须过 `DOMPurify` 消毒，不使用未过滤的 `dangerouslySetInnerHTML`。
- **纯前端工具不发网络请求**：除 AI 增强工具外，其余工具的所有计算必须在浏览器本地完成，不依赖任何第三方 API（保证零成本、零隐私风险）。
- **bundle 体积**：单个工具新增依赖的 gzip 体积增量 < 50KB（对应 [00_overview.md](00_overview.md) 非功能需求）。
- **移动端可用**：输入框/按钮在 375px 宽度下不溢出、可正常点击。
- **可独立删除**：删除 `src/tools/<slug>/` 目录 + `registry.ts` 里的一行，工具应完整消失，不留死链接或报错。
