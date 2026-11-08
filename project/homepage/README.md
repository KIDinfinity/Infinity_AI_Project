# 个人主页 · AI 技术展示站

> 轻量展示项目，面向潜在雇主/合作方，展示 AI 相关技术栈能力。
> **不是 DA-01（WorkPilot）**，不占用 DA-01 开发时间预算。

## 一句话定位

一个 React 个人主页，内置几个「活的」AI 交互 Demo（用免费小模型 / 严格限 token）、每日自动更新的 AI 资讯，以及持续新增的免费小工具，让访客直观感受你的 AI 工程能力。

## 目标用户

| 用户       | 想看什么                        | 本站给什么                  |
| ---------- | ------------------------------- | --------------------------- |
| 技术面试官 | 代码质量、架构能力、AI 落地经验 | 源码可查 + 在线 Demo 可交互 |
| HR/猎头    | 快速了解技术方向                | 首页一句话定位 + 技能标签云 |
| 潜在合作方 | 能不能做 AI 相关项目            | 3 个可交互 Demo 证明能力    |

## 设计原则

1. **极简**：单页滚动 + 3 个 Demo 卡片 + AI 资讯速览，不搞多页面重架构
2. **活的**：Demo 不是截图/录屏，是真的能跑、能交互
3. **省钱**：AI 调用走免费模型（Gemini Flash / DeepSeek 免费额度），前端做 token 硬限制
4. **快**：静态部署（Vercel/GitHub Pages），首屏 < 2s
5. **源码可见**：GitHub 链接放页脚，代码即简历
6. **内容驱动**：集成 `project/aiNews` 每日资讯产出，展示 AI 自动化工作流能力
7. **可扩展**：工具箱走「注册表 + 懒加载路由」模式，后续加小工具只需新增文件，不改架构

## 先看设计

实现前请先完整阅读 `design/`：

1. [design/00_overview.md](design/00_overview.md) — 项目定位、信息架构、页面结构
2. [design/01_tech_stack.md](design/01_tech_stack.md) — 技术选型与理由
3. [design/02_pages_and_components.md](design/02_pages_and_components.md) — 页面与组件树
4. [design/03_ai_integration.md](design/03_ai_integration.md) — AI 集成方案（模型选择、token 限制、prompt 设计）
5. [design/04_deployment.md](design/04_deployment.md) — 部署与成本
6. [design/05_tools.md](design/05_tools.md) — 工具箱设计（可扩展小工具系统、新增工具流程）

## 快速开始

```bash
cd project/homepage
pnpm install        # 安装依赖
cp .env.example .env   # 按需填入 AI API Key，不填也能跑（Demo 会提示未配置）
pnpm dev            # 本地开发
pnpm build          # 生产构建
```

## 每日更新 AI 资讯（最简便方式）

```bash
pnpm news:add
```

交互式命令行会依次问你：日期（默认今天）、一句话概括、Top 3（标题/来源/链接/理由，回车可提前结束）。
填完直接写入 `public/data/ainews.json`，自动按日期倒序、只保留最近 14 天，首页资讯区立刻能看到。

## 目录结构

```text
project/homepage/
├── README.md              # 本文件
├── design/                # 设计文档
│   ├── 00_overview.md
│   ├── 01_tech_stack.md
│   ├── 02_pages_and_components.md
│   ├── 03_ai_integration.md
│   ├── 04_deployment.md
│   └── 05_tools.md
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── pages/             # 路由页面（HomePage / ToolsIndexPage / ToolDetailPage）
│   ├── components/        # UI 组件
│   ├── demos/             # 3 个 AI Demo 组件
│   ├── tools/             # 工具箱：registry.ts + 各工具组件（持续新增）
│   ├── hooks/             # 自定义 hooks（含 AI 调用 hook、资讯加载 hook）
│   ├── lib/               # 工具函数（token 计数、API 封装）
│   └── styles/
├── public/
│   └── data/
│       └── ainews.json    # AI 资讯数据（用 `pnpm news:add` 更新）
├── scripts/
│   └── add-news.mjs       # 每日资讯更新 CLI
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 当前进度

- [x] 设计文档完成
- [x] 项目骨架搭建
- [x] 首页 + 关于我
- [x] Demo 区骨架（UI 已搭好，AI Key 配置后可直接用）
- [x] AI 资讯速览（NewsFeed + ainews.json + `pnpm news:add`）
- [x] 工具箱骨架（路由 + registry.ts + ToolCard，含 1 个示例工具）
- [ ] 补全剩余首批工具（正则测试 / Markdown 预览）
- [ ] 部署上线
