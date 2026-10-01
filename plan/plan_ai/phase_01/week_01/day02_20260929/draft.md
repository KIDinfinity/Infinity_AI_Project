- [✅] 自托管 Git 服务可访问（浏览器能打开 Web UI，能登录）
- [✅] 能独立在 Web UI 创建新仓库（不看教程）
- [✅] 本地 `clone / commit / push` 跑通一次
- [✅] `projects/{product-lab, ai-lab, infra}` 三目录结构已落到远端仓库
- [✅] 产出：可用的 Git 服务 + 测试仓库 + 三目录结构

---

注意必须要是docker里面gitea创建的仓库，才能正常在本机里面对应mount的仓库目录
git add/commit/push
不是同一个container创建的仓库，即使mount的目录一致，目录里面的仓库会识别不到
localhost:3000里面会看不到对应的仓库