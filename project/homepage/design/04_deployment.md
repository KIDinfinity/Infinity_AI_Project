# 04 — 部署与成本

## 1. 部署方案

### 1.1 推荐：Vercel（免费 Hobby 层）

```bash
# 安装 Vercel CLI
pnpm i -g vercel

# 部署
cd project/homepage
vercel --prod
```

**免费层限制**：

- 带宽：100 GB/月
- Serverless Function 执行：100 GB-hours/月（如果后续加 API 代理）
- 构建：100 次/天
- **对展示站绰绰有余**

### 1.2 备选：GitHub Pages

```bash
# vite.config.ts 中配置 base
export default defineConfig({
  base: '/homepage/',  // 仓库名
})

# 部署（用 gh-pages 包）
pnpm add -D gh-pages
pnpm build
pnpm gh-pages -d dist
```

**限制**：纯静态，不能做 API 代理（AI Key 只能前端直连）。

### 1.3 部署架构

```
方案 A（Vercel + API 代理，推荐）：
  用户浏览器
    ↓
  Vercel CDN（静态资源）
    ↓ (AI 请求)
  Vercel Edge Function (/api/ai)
    ↓
  Gemini API

方案 B（纯静态，最简单）：
  用户浏览器
    ↓ (静态资源)
  GitHub Pages / Vercel
    ↓ (AI 请求，前端直连)
  Gemini API
```

## 2. 成本估算

### 2.1 托管成本

| 项目                 | 费用                       |
| -------------------- | -------------------------- |
| Vercel 静态托管      | $0（Hobby 层）             |
| Vercel Edge Function | $0（Hobby 层 100GB-hours） |
| 域名（可选）         | $0（用 `*.vercel.app`）    |
| **合计**             | **$0**                     |

### 2.2 AI 调用成本

| 模型             | 免费额度    | 超出后单价             | 预估月消耗 |
| ---------------- | ----------- | ---------------------- | ---------- |
| Gemini Flash 2.0 | 1500 req/天 | $0.075/1M input tokens | 免费额度内 |
| DeepSeek V3      | 500 req/天  | ¥1/1M tokens           | 免费额度内 |

**假设**：每天 20 个访客，每人试用 3 个 Demo 各 1 次 = 60 次请求/天，远低于免费额度。

**结论：零成本运行。**

### 2.3 最坏情况

如果有人恶意刷 API：

- Gemini 免费层有 15 RPM 硬限制，刷不动
- 前端可以做简单防刷（同一 session 每分钟最多 10 次请求）
- 即使被刷爆，免费 Key 也没有经济损失

## 3. CI/CD

### 3.1 Vercel 自动部署

推送 `main` 分支 → Vercel 自动构建部署。无需额外配置 GitHub Actions。

### 3.2 环境变量管理

```bash
# Vercel Dashboard → Settings → Environment Variables
VITE_AI_PROVIDER=gemini
VITE_AI_API_KEY=your_key_here
```

### 3.3 构建命令

```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .ts,.tsx",
    "test": "vitest run"
  }
}
```

## 4. 上线检查清单

- [ ] `.env.example` 已提交，`.env` 在 `.gitignore`
- [ ] `vite.config.ts` 中 `base` 配置正确
- [ ] 所有 Demo 在本地用 Ollama 测试通过
- [ ] 移动端响应式验证（Chrome DevTools 模拟 iPhone 14 / iPad）
- [ ] Lighthouse 评分 ≥ 90（Performance / Accessibility / Best Practices）
- [ ] AI Key 已配置到 Vercel 环境变量
- [ ] 生产环境用 Gemini Flash 测试 3 个 Demo 各一次
- [ ] `README.md` 中更新了在线地址
- [ ] GitHub 仓库设为公开（或至少 README 可见）

## 5. 监控（可选，后续加）

| 监控项    | 工具                       | 成本 |
| --------- | -------------------------- | ---- |
| 访问量    | Vercel Analytics（免费层） | $0   |
| AI 调用量 | Gemini API Console         | $0   |
| 错误追踪  | 浏览器 console + 手动检查  | $0   |

> 展示站不需要复杂监控，上线后每周看一眼 Gemini Console 确认用量正常即可。

## 6. 域名（可选）

如果后续想绑自定义域名：

1. 买域名（Namecheap / Cloudflare，约 $10/年）
2. Vercel Dashboard → Domains → 添加自定义域名
3. 配置 DNS（Vercel 自动生成 SSL 证书）

> 建议先用 `*.vercel.app` 上线，有需要再绑域名。
