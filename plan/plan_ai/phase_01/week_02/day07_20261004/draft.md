fastapi接口测试

[✅] uv run python --version（在 apps/api 下）输出 Python 3.12.x
[✅] make dev 后 curl -s localhost:8000/health 返回 {"status":"ok","env":"dev","version":"0.0.1"}
[✅] 浏览器 http://localhost:8000/docs 可见 GET /health
[✅] make test 输出 2 passed
[✅] make lint 无报错（All checks passed! 且格式检查通过）
[✅] uv.lock 已提交，.venv/ 未出现在 git status