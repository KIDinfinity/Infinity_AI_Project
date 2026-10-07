初始化ai-project-template项目的骨架

[✅] 模板中存在 README.md、Makefile、deploy/docker-compose.yml、scripts/bootstrap.sh、docs/adr/0000-template.md
[✅] make help 输出 ≥ 8 个命令及说明
[✅] make up 后 curl -s localhost:8081 | head -3 有 Hostname: 输出；make down 后 docker ps 无该容器
[✅] bash scripts/bootstrap.sh 生成 .env 并列出 docker / uv / node / pnpm 安装状态
[✅] Gitea 中 ai-project-template 为模板仓库，workpilot 由「使用此模板」生成，本地在 ~/lab/workpilot （没看到怎么设置一个项目为模板）
[✅] cd ~/lab/workpilot && git ls-remote --tags origin 含 refs/tags/v0.0.0
[✅] Week 01 README §11 周复盘已填写；PROJECT_CONFIG.md DA-01 路径回填为 ~/lab/workpilot