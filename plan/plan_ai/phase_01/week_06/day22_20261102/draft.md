搭建问答前端

- [✅] `make web` 启动，http://localhost:5173 能打开，Tailwind 类名生效（按钮有颜色）
- [✅] 输入问题 → 页面显示后端答案；DevTools Network 中请求是 `localhost:5173/v1/kb/ask`（走代理，无 CORS 报错）
- [✅] 停掉 API 再发送 → 显示「请求失败」提示，页面不白屏
- [✅] `src/types/api.ts` 由命令生成；`pnpm exec tsc --noEmit -p tsconfig.app.json` 0 错误
- [✅] 已 commit + push 到 Gitea