# Day 70 · 2026-12-06 · Week 23 Task 1：Portfolio 网站

## 0. 今天只做一件事

用 Astro 搭一个静态 Portfolio：首页 + 3 个统一 9 段结构的项目页 + Writing + About（简历下载），内容取自 `docs/portfolio/`，部署到 GitHub Pages 并公网可访问。

不碰：WorkPilot 代码、Demo 账号（Day71）、视频（Day71）、自定义域名、设计打磨、博客系统。

## 1. 资产锚点

- 构建模块：M13.5 Portfolio 网站、M13.2 项目写作（P3 定稿）、M12.3 产品页（共用）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：v2.0（对外展示）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：一个公开 URL，招聘方 1 分钟内看到 WorkPilot 三个里程碑的问题、架构、评测数字和结果
- 今日 AI 实际应用：用 AI 把 p1/p2/p3 的长文压缩为统一 9 段结构（每段 ≤ 120 字 + 1 个数字），人工核对每个数字的来源

## 2. 起点（前置确认）

- 已有：`docs/portfolio/p1.md`、`p2.md`、`p3-notes.md`；`eval/reports/20261204-eval-v2.md`；`docs/architecture-v2.md`；W16 技术文章链接；简历 v1。
- 需确认：

```bash
node -v                     # ≥ 18.17（Astro 要求的最低版本以官方文档为准）
ls ~/lab/workpilot/docs/portfolio/
gh --version 2>/dev/null || echo "无 gh 也可以，用网页建 GitHub 仓库"
```

在 Gitea Web UI 新建仓库 `portfolio`（先建再 clone）；GitHub 新建空仓库 `portfolio`（Public）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `https://<user>.github.io/portfolio/`（或 Cloudflare Pages 地址）公网可访问
- [ ] 首页：一句话定位 + 3 张项目卡片（标题 / 一句话 / 2 个关键数字 / 链接）
- [ ] `/projects/p1` `/projects/p2` `/projects/p3` 均含 9 段：Problem → Why AI → Architecture → Implementation → Evaluation → Badcases → Optimization → Deployment → Result
- [ ] 每个项目页 Evaluation 段至少 1 个数字 + 指向 GitHub 上评测报告的链接
- [ ] `/about` 有简历 PDF 下载（暂用 v1，W24 替换）+ GitHub 链接；`/writing` 有文章列表
- [ ] `docs/portfolio/p3.md` 已在 WorkPilot 仓库提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                   |
| ----------- | ------ | ------------------------------------------------------ |
| 0–15 min    | P0     | 建仓库 + `npm create astro@latest` + 配置 site/base    |
| 15–35 min   | P0     | content collection + 项目页布局（9 段导航）            |
| 35–70 min   | P0     | p3.md 定稿 + p1/p2 统一为 9 段（AI 压缩 + 人工核数字） |
| 70–85 min   | P0     | 首页 + about + writing                                 |
| 85–105 min  | P0     | GitHub Pages workflow + 上线                           |
| 105–120 min | P1     | 架构图图片、移动端检查、OG 描述                        |
| 顺延        | P2     | 自定义域名、暗色模式、英文版 → Backlog                 |

时间不足时最低保留：首页 + 3 个项目页 + 上线。

## 5. 今日学习（只学完成任务必须的）

- **Astro 内容集合**：Markdown 放 `src/content/projects/`，在 `src/content.config.ts` 定义 schema，页面用 `getCollection` / `render` 渲染——内容与布局分离。
- **静态路由**：`src/pages/projects/[id].astro` + `getStaticPaths()` 为每个项目生成一页。
- **GitHub Pages 子路径**：项目站点 URL 是 `/<repo>/`，必须在 `astro.config.mjs` 设置 `site` 和 `base`，站内链接用 `import.meta.env.BASE_URL` 拼接。
- **作品集叙事**：每段回答一个招聘方问题；数字优先、链接为证、不堆技术名词。
- 资料：https://docs.astro.build/ 、https://docs.github.com/en/pages

## 6. 执行步骤

### Step 1 · 建站（P0）

```bash
cd ~/lab && git clone http://localhost:3000/<user>/portfolio.git && cd portfolio
npm create astro@latest . -- --template minimal --no-install --no-git --skip-houston
npm install
git remote add github git@github.com:<user>/portfolio.git
```

`astro.config.mjs`：

```js
import { defineConfig } from "astro/config";
export default defineConfig({
  site: "https://<user>.github.io",
  base: "/portfolio",
});
```

目录：

```text
portfolio/
├── astro.config.mjs
├── public/{resume.pdf, images/}
├── src/
│   ├── content.config.ts
│   ├── content/projects/{p1.md, p2.md, p3.md}
│   ├── layouts/Base.astro
│   └── pages/{index.astro, writing.astro, about.astro, projects/[id].astro}
└── .github/workflows/deploy.yml
```

### Step 2 · 内容集合 + 项目页（P0，样板可让 AI 生成）

```ts
// src/content.config.ts
import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const projects = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/projects" }),
  schema: z.object({
    title: z.string(),
    tagline: z.string(),
    version: z.string(), // v0.5 / v1.0 / v2.0
    metrics: z.array(z.object({ label: z.string(), value: z.string() })).max(3),
    repo: z.string().url(),
    order: z.number(),
  }),
});
export const collections = { projects };
```

```astro
---
// src/pages/projects/[id].astro
import { getCollection, render } from "astro:content";
import Base from "../../layouts/Base.astro";
export async function getStaticPaths() {
  const items = await getCollection("projects");
  return items.map((p) => ({ params: { id: p.id }, props: { p } }));
}
const { p } = Astro.props;
const { Content } = await render(p);
const sections = ["Problem","Why AI","Architecture","Implementation","Evaluation",
                  "Badcases","Optimization","Deployment","Result"];
---
<Base title={p.data.title}>
  <h1>{p.data.title} <small>{p.data.version}</small></h1>
  <p>{p.data.tagline}</p>
  <ul class="metrics">{p.data.metrics.map((m) => <li><b>{m.value}</b> {m.label}</li>)}</ul>
  <nav>{sections.map((s) => <a href={`#${s.toLowerCase().replace(/ /g, "-")}`}>{s}</a>)}</nav>
  <article><Content /></article>
  <a href={p.data.repo}>GitHub</a>
</Base>
```

> Markdown 中二级标题用 `## Problem`、`## Why AI` …，Astro 自动生成的锚点与上面 nav 一致（小写 + 连字符）。

### Step 3 · 项目内容（P0，数字必须自己核对）

`src/content/projects/p3.md` 骨架（同时复制一份到 WorkPilot `docs/portfolio/p3.md`）：

```markdown
---
title: "WorkPilot Production"
tagline: "需求 → 任务拆解 → Issue：可审批、可评测、多租户安全的研发 AI 工作流"
version: "v2.0"
metrics:
  - { label: "场景 rubric 通过率（20 条）", value: "0.__" }
  - { label: "攻击用例拦截率（20 条）", value: "100%" }
  - { label: "端到端耗时（vs 手工）", value: "-__%" }
repo: "https://github.com/<user>/workpilot"
order: 3
---

## Problem

拿到需求后手工拆任务、写验收标准、建 Issue 平均 \_\_ 分钟，验收标准常不可测……

## Why AI

需要理解自然语言需求 + 检索团队规范与历史 issue + 生成结构化任务；规则引擎做不到，纯 LLM 不可控 → 工作流 + 人审。

## Architecture

（插入 architecture-v2 导出的图：public/images/p3-arch.svg）多空间 · JWT/RBAC · Postgres · worker · LangGraph 场景图

## Implementation

7 节点 LangGraph（自检回边 + interrupt 审批 + 幂等写）；SKIP LOCKED 异步导入；tag 自动部署 + 回滚

## Evaluation

20 条场景集 + 5 维 rubric judge（人审一致率 \_\_）；隐式反馈 edit_ratio；报告：[Eval v2](https://github.com/<user>/workpilot/blob/main/eval/reports/20261204-eval-v2.md)

## Badcases

Top 类别：untestable_ac、coverage_gap……（附 1 个具体例子与根因）

## Optimization

breakdown v1 → v2：通过率 ** → **；安全基线 \_\_/20 → 20/20

## Deployment

2C4G 云服务器 · docker compose · Caddy HTTPS · 恢复演练 \_\_ 分钟

## Result

自己真实使用 \_\_ 次；开源 + Pro Kit；局限与下一步（1–2 条）
```

p1 / p2：把已有 `p1.md` / `p2.md` 交给 AI，「重排为上述 9 个二级标题，每段 ≤ 120 字，保留所有数字并标注来源报告」；**逐个数字对照 `eval/reports/` 核对**，对不上的以报告为准。

### Step 4 · 首页 / about / writing（P0）

- 首页：`<h1>` 一句话定位（例：「5 年全栈 → AI 应用工程：我把 RAG、Agent、评测和安全做成可上线的系统」）+ `getCollection("projects")` 按 order 渲染 3 张卡片（链接用 `${import.meta.env.BASE_URL}/projects/${p.id}`，注意 BASE_URL 末尾斜杠，统一处理）。
- about：简短经历（不含公司机密）、技能矩阵 Top 8（来自 capability-matrix）、`resume.pdf` 下载、GitHub、邮箱（可选，用于被动联系）。
- writing：W16 技术文章 + 各版本 Release notes 链接。

### Step 5 · 部署 GitHub Pages（P0）

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: withastro/action@v3 # 版本以 Astro 官方部署文档为准
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

GitHub 仓库 → Settings → Pages → Source 选「GitHub Actions」。

```bash
npm run build && npx astro preview        # 本地确认无死链
git add . && git commit -m "feat: portfolio site with three project pages" && git push && git push github main
```

> 备选 Cloudflare Pages：连接 GitHub 仓库，构建命令 `npm run build`，输出目录 `dist`，此时 `base` 改为 `/`。

### Step 6 · 提交 WorkPilot 侧

```bash
cd ~/lab/workpilot && git add docs/portfolio/p3.md && git commit -m "docs(portfolio): add P3 write-up" && git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么用静态站点而不是 Next.js？（答：纯内容展示无需服务端；免费托管、零运维、加载快）
2. GitHub Pages 子路径为什么要配 `base`？（答：站点不在域名根目录，资源与链接需加 `/<repo>/` 前缀，否则 404）
3. 9 段结构中你认为最能区分候选人的是哪几段？（答：Evaluation、Badcases、Optimization——证明能判断 AI 是否变好）
4. 作品集中的数字如何保证可信？（答：每个数字链接到仓库中的评测报告；facts.md 统一来源，不手写估算）
5. 为什么 P1/P2/P3 要同一结构？（答：降低阅读成本，体现同一系统的演进，便于招聘方横向比较）

## 8. 对 DA-01 的贡献

DA-01 第一次有了统一的对外展示面：WorkPilot 的三个里程碑被讲成一条连续的成长线，同时作为 Pro Kit 的产品介绍入口（蓝图 §10 内容层「作品集与 SEO」）。

## 9. 求职映射（D 线）

- 岗位能力：技术写作、叙事结构化、前端工程（Astro / 静态部署）。
- 对应岗位：全部目标岗位（Frontend / AI Full-Stack / AI Engineer）。
- 简历 bullet 草稿：「个人作品集：3 个 AI 项目（RAG / Agent / Production）统一展示问题、架构、评测与结果，含在线 Demo 与视频：<URL>」
- 面试可能问：
  1. 你的三个项目有什么关系？——要点：同一个系统的三个版本里程碑，每一步解决上一版的局限（知识 → 行动 → 生产）。
  2. 你最不满意项目的哪一部分？——要点：诚实指出一个仍未达标的指标 + 原因 + 下一步计划（来自 Eval v2 报告）。

## 10. 卡住时的处理

| 现象                               | 处理                                                                                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `npm create astro` 交互卡住        | 去掉参数手动按提示选择 minimal / 不装依赖 / 不初始化 git                                               |
| 页面样式与链接 404                 | 检查 `base` 与链接是否拼接了 BASE_URL                                                                  |
| Pages 部署失败：权限               | Settings → Pages 选 GitHub Actions；workflow 中 `permissions` 需包含 `pages: write`、`id-token: write` |
| Gitea 也触发了 `.github/workflows` | 在 Gitea 仓库设置中关闭该仓库的 Actions（Gitea 在无 `.gitea/workflows` 时会读取 `.github/workflows`）  |
| p1/p2 数字对不上报告               | 以报告为准修改网站，并在 W24 facts.md 中记录来源                                                       |
| 写作耗时过长                       | 每段只写 2–3 句 + 1 个数字；精修放到 W24/W25 碎片时间                                                  |

## 11. 产出记录（执行时填写）

- Portfolio URL：\_\_\_\_
- 每个项目页的关键数字及来源：p1 \_**\_ / p2 \_\_** / p3 \_\_\_\_
- 构建 / 部署耗时：\_\_
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day71 · W23 Task 2「在线 Demo + 演示视频 + 发布前安全检查」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（首页 + 3 个项目页 + 上线）。
