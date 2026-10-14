response格式化

- [✅] `gateway.chat()` 返回 `ChatResult`，`/v1/chat` 仍可用
curl -s --noproxy '*' localhost:8000/v1/chat -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"只回复 pong"}],"max_tokens":8}' | python3 -m json.tool
- [✅] `prompts/structured_answer.v1.md`、`prompts/task_breakdown.v1.md` 存在且带 front matter（id / version / model / changelog）
- [✅] `uv run pytest -m "not llm" -q` 全绿（含 prompt 渲染、结构化重试两个单测）
进入
cd ~/lab/workpilot/apps/api && uv run pytest -m "not llm" -q

- [✅] `uv run pytest -m llm -s` 打印「structured pass rate: x/5」，x ≥ 4
cd ~/lab/workpilot/apps/api && uv run pytest -m llm -s
- [✅] curl `/v1/structured/answer`、`/v1/structured/breakdown` 均返回 200 且字段合法
- [✅] 已 push 到 Gitea → ⏭️ **按用户要求未提交**（改动保留在工作区）