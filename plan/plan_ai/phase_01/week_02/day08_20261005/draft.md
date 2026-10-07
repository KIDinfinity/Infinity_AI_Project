接入大模型

- [✅] DeepSeek 已小额充值，key 只存在于 `~/lab/workpilot/.env`
- [✅] `curl /v1/chat` 返回 JSON 含 `content`、`model`、`prompt_tokens`、`completion_tokens`、`latency_ms`；服务日志有一行 `llm_call status=ok ...`
- [✅] `make test` 通过（≥ 6 passed，不触网，断网也能过）
- [✅] `cd apps/api && uv run pytest -m live -q` 通过（1 passed，真实调用）
- [✅] `LLM_TIMEOUT_S=0.001 make dev` 后 curl 得到 HTTP 504 + `{"error":{"code":"llm_timeout",...}}`
- [✅] `git -C ~/lab/workpilot log -p | grep -c 'sk-'` 输出 0；日志中无 key （先放env后面再放环境变量或者搞个后端接口来）
- [✅] `make lint` 通过，已 push


---

大模型地址：
3.deepseek
apikey:
daily:<DEEPSEEK_API_KEY>  # 真实值只写 ~/lab/workpilot/.env，禁止入库

4.豆包
apikey：
daily：<DOUBAO_API_KEY>  # 真实值只写 ~/lab/workpilot/.env，禁止入库

---

/Users/infinity/lab/workpilot/.env这里的
LLM_PROVIDER来控制使用哪个模型