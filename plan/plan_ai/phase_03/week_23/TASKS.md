# Week 23 · TASKS

## Task 1：Portfolio 网站（Day70 · 12-06）

### 做什么

`npm create astro@latest` 建站；页面：首页（一句话定位 + 3 项目卡片）、`/projects/p1` `/projects/p2` `/projects/p3`（统一 9 段：Problem → Why AI → Architecture → Implementation → Evaluation → Badcases → Optimization → Deployment → Result）、`/writing`、`/about`（简历下载）；内容取自 `docs/portfolio/p1–p3.md`；部署到 GitHub Pages（或 Cloudflare Pages）。

### 为什么做

总计划 §6.4 / §12.3 的必备求职资产；招聘方入口统一为一个 URL。

### 资产锚点

- 模块：M13.5、M13.2、M12.3
- 版本：v2.0（对外展示）

### 前置依赖

- `docs/portfolio/p1.md`、`p2.md`（W8 / W16）、`p3-notes.md` + Eval v2 报告（W22）
- 架构图（mermaid 导出为 SVG/PNG）

### 具体执行步骤（概要，详见 day70_20261206/PLAN.md）

1. Gitea 建 `portfolio` 仓库 → clone → `npm create astro@latest`。
2. content collection（projects）+ 项目页布局（9 段锚点导航）。
3. 写 p3.md（由 p3-notes + Eval v2 整理），统一 p1/p2 结构。
4. 首页 / writing / about。
5. GitHub Pages workflow 部署。

### 验收标准

- [ ] 公网可访问
- [ ] 三页结构一致，每页有评测数字 + 报告链接
- [ ] 移动端可读（基础响应式）

### 完成后的产出

- `~/lab/portfolio/`、公开 URL
- `docs/portfolio/p3.md`（WorkPilot 仓库）

### 求职映射

简历顶部链接；面试开场「请介绍项目」时的讲稿骨架。

### 如果时间不够 / 没有必要

- 用 Astro minimal 模板 + 系统字体，不做设计打磨。
- Writing 只放已有文章链接（W16 技术文章）。

---

## Task 2：在线 Demo + 演示视频 + 发布前安全检查（Day71 · 12-07）

### 做什么

WorkPilot 开放 Demo：demo 空间（`is_demo=true`，公开语料）+ viewer 演示账号；viewer 在 demo 空间可 dry-run SP-B（停在草案，不能批准）；demo 空间低日预算 + 更严限流；每晚 cron 重置 demo 数据；录 3 段视频（P1 90s、P2 2min、P3 2min）嵌入 Portfolio；gitleaks 扫所有公开仓库；确认 Demo 无法写 Gitea（只指向沙盒或写工具禁用）、无公司数据；写发布前检查清单。

### 为什么做

可点击的 Demo 是最强证据；公开前的安全检查是蓝图 §8 红线。

### 资产锚点

- 模块：M12.4、M11（demo 安全运营）、M13.2
- 版本：v2.0（对外发布）

### 前置依赖

- v2.0 已部署；W19 RBAC；W15 预算守卫；W21 policy
- Day70 Portfolio 已上线

### 具体执行步骤（概要，详见 day71_20261207/PLAN.md）

1. `cli.py reset-demo`：建/清 demo 空间、导入公开语料、建 viewer 账号。
2. dry-run 模式 + demo 预算 / 限流配置。
3. 服务器 cron 夜间重置。
4. 发布前检查清单 + gitleaks × 3。
5. 录制 + 压缩 + 嵌入视频。

### 验收标准

- [ ] 演示账号全流程可用，写工具 0 次成功
- [ ] cron 重置可证
- [ ] 检查清单全绿
- [ ] 视频已嵌入（≥ 1 段 P0）

### 完成后的产出

- `apps/api/app/cli.py`（reset-demo）、`data/sample/demo/`、`deploy/cron/reset-demo`
- `docs/security/release-checklist.md`
- 视频文件或链接；Portfolio 更新

### 求职映射

「公开 Demo 安全运营」体现生产意识；视频用于简历与投递附言。

### 如果时间不够 / 没有必要

- 视频先录 P3 一段；P1/P2 可用已有 W8/W16 录屏剪辑。
- 演示账号密码直接写在 Portfolio 上（它本就是只读、可重置的公开账号）。

---
