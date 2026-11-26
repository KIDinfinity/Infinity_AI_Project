# SUMMARY · Day 36（2026-11-25）Week 09 Task 3：多工具循环 Demo + 工具选择测试 + JD 追踪

> 执行结果汇总。对应 PLAN 第 3 节「验收对齐」逐条给出**完整、可直接粘贴、任何目录下运行**的验收命令。
> 所有命令都先 `cd` 到绝对路径，无需手动定位目录。
> 按用户要求，**不提交 / 不打 tag**（PLAN Step 7 跳过）。

---

## 0. 一句话结论

落地 `app/agent/tool_loop.py`（LLM ⇄ 工具循环，`asyncio.gather` 并行、`max_steps=5` 兜底、`tool_choice="none"` 强制收尾、每步结构化日志），配 `scripts/tool_demo.py`（3 问，其中 1 问触发 3 个工具并走满 5 步上限）+ 15 条工具选择评测（**初版准确率 100%**）+ JD 追踪第 1 轮 + open-core 草稿。

---

## 1. 改动清单（未提交，按用户要求）

| 文件 | 动作 | 说明 |
|---|---|---|
| `apps/api/app/agent/__init__.py` | 新增 | 空包 |
| `apps/api/app/agent/tool_loop.py` | 新增 | 多工具循环核心（并行 / 步数上限 / 强制收尾 / 结构化日志） |
| `scripts/tool_demo.py` | 新增 | CLI，`python scripts/tool_demo.py "<问题>"` |
| `eval/datasets/tool_selection.jsonl` | 新增 | 15 条工具选择用例（ts-01 ~ ts-15） |
| `eval/runners/run_tool_selection.py` | 新增 | 评测 runner + 报告生成 |
| `eval/reports/20261125-tool-selection.md` | 生成 | 15 条用例报告（准确率 100%） |
| `docs/product/open-core.md` | 新增 | open-core 边界草稿（Step 6，P2） |
| `.env` | 改 | 追加 `GITEA_BASE_URL` / `GITEA_TOKEN` / `GITEA_READ_REPOS`（gitignore，未入库） |
| `~/lab/projects/career/job-market.md` | 改 | 追加「第 1 轮追踪」（10 JD + 关键词频次） |

> 关键实现点：PLAN 示例 `from app.llm.gateway import gateway` 不存在，实际用 `gateway = LLMGateway(settings)` 进程级单例（同 seed_eval.py 模式）；`execute(name, raw_args)` 为 async、入参是 JSON 字符串；`chat_with_tools` 返回 `ToolChatResult`（`.message` / `.total_tokens`）。

---

## 2. 验收对齐（第 3 节，逐条 + 完整命令）

### ✅ 验收 1：`tool_loop.py` 并行执行 + `max_steps=5` + `tool_choice="none"` 强制收尾

```bash
cd /Users/infinity/lab/workpilot && grep -nE "asyncio.gather|max_steps: int = 5|tool_choice=\"none\"|range\(1, max_steps \+ 1\)" apps/api/app/agent/tool_loop.py
```

**期望输出**（命中 4 处关键实现）：

```
...
    max_steps: int = 5,
    for step in range(1, max_steps + 1):
        results: list[ToolResult] = await asyncio.gather(
    res = await gateway.chat_with_tools(messages, tools=tools, tool_choice="none")
```

### ✅ 验收 2：每步输出结构化日志（step / tool / args / ok / latency_ms / tokens）

```bash
cd /Users/infinity/lab/workpilot && grep -nE "log\.info|extra=|step=|latency_ms=|tokens=" apps/api/app/agent/tool_loop.py
```

**期望输出**：`log.info("tool_step", extra={...})` 一行，`extra` 内包含 `step` / `tool` / `ok` / `latency_ms` / `tokens`（`args` 记在 `LoopStep.args` 字段，随 `steps` 一起输出）。

### ✅ 验收 3：`scripts/tool_demo.py` 跑 3 个问题，至少 1 个触发 ≥2 个工具

（1）工具注册自检（6 个工具）：

```bash
cd /Users/infinity/lab/workpilot && PYTHONPATH=apps/api uv run --project apps/api python -c "import app.agent.tool_loop as t; print([x['function']['name'] for x in t.to_openai_tools()])"
```

**期望输出**：`['calculator', 'gitea_repo_read', 'gitea_issue_read', 'http_fetch', 'kb_search', 'web_search']`

（2）问题 1（单工具 · calculator）：

```bash
cd /Users/infinity/lab/workpilot && PYTHONPATH=apps/api uv run --project apps/api python scripts/tool_demo.py "一个 Sprint 10 个工作日，每天有效 1.5 小时，3 个人一共多少小时？"
```

**期望输出**：`[step 1] calculator(...) ok=True`，答案 `45 小时`。

（3）问题 2（单工具 · kb_search，演示一轮内并行 2 次检索）：

```bash
cd /Users/infinity/lab/workpilot && PYTHONPATH=apps/api uv run --project apps/api python scripts/tool_demo.py "我们团队的代码评审有哪些规范要求？"
```

**期望输出**：`[step 1] kb_search(...)` 出现 2 行（同一步并行两次），答案含「前端代码评审规范（团队样例）」。

（4）问题 3（多工具 · 触发 ≥2 个工具，并走满 5 步上限）：

```bash
cd /Users/infinity/lab/workpilot && PYTHONPATH=apps/api uv run --project apps/api python scripts/tool_demo.py "对比 infinity/workpilot 仓库 README 里的本地启动方式与 FastAPI 官方推荐的启动方式，有什么差异？"
```

**期望输出**：`gitea_repo_read` + `web_search` + `http_fetch` 至少 3 个工具被调用，且结尾 `max_steps_hit=True`（演示 `tool_choice="none"` 强制收尾）。

> 注：`web_search` 走 ddgs 兜底（无 Tavily key），偶发 `DDGSException: No results found`，但循环会自我修正（改走 http_fetch），不影响验收。

### ✅ 验收 4：15 条用例 + runner 输出准确率与错选明细到报告

```bash
cd /Users/infinity/lab/workpilot && PYTHONPATH=apps/api uv run --project apps/api python eval/runners/run_tool_selection.py
```

**期望输出**：`accuracy=100.00% -> .../eval/reports/20261125-tool-selection.md`

查看报告明细：

```bash
cat /Users/infinity/lab/workpilot/eval/reports/20261125-tool-selection.md
```

**期望输出**：15 行 `| ts-XX | ✓ | ... |  |`，无「✗」。ts-15（闲聊）实际调用为 `-`（正确不调用）。

### ⏭️ 验收 5（跳过）：tag v0.6.0 + 推送

按用户要求「不用帮我提交代码」，PLAN Step 7 的 `git add / commit / tag v0.6.0 / push` 全部跳过。如需打 tag，命令为：

```bash
cd /Users/infinity/lab/workpilot && git add apps/api/app/agent scripts/tool_demo.py eval/datasets/tool_selection.jsonl eval/runners eval/reports docs/product && git commit -m "feat(agent): add multi-tool loop demo and tool selection eval" && git tag -a v0.6.0 -m "v0.6.0: tool layer + multi-tool loop + tool selection eval"
```

（不执行，仅供后续手动参考。）

### ✅ 验收 6：`career/job-market.md` 第 1 轮 JD 追踪（10 个 JD + 关键词频次变化）

```bash
sed -n '/第 1 轮追踪/,$p' /Users/infinity/lab/projects/career/job-market.md
```

**期望输出**：`第 1 轮追踪 · 2026-11-25（W9）` 段落，含 10 行 JD 汇总表 + `关键词频次变化（对比 W2 基线）` 表（RAG 18 / Agent 13 / Tool Calling 4 / MCP 5 / LangGraph·LangChain 6 …）+ 3 条结论。

---

## 3. 产出记录（对应 PLAN 第 11 节）

- **Demo 中触发多工具的问题**：`对比 infinity/workpilot 仓库 README 里的本地启动方式与 FastAPI 官方推荐的启动方式，有什么差异？` —— 触发 gitea_repo_read + web_search + http_fetch，走满 5 步上限（`hit_max_steps=True`）。
- **工具选择准确率（初版 / 改描述后）**：**100% / （无需改，初版即 100%）**。
- **15 条用例总 tokens / 估算成本**：**95551 / 约 ¥0.1**（deepseek 定价：未命中输入 ¥1/M、输出 ¥4/M）。
- **JD 追踪最显著的变化**：首轮为基线建立，无新增 JD；LangGraph/LangChain 在 8/10 JD 中要求，确认 W11 排期值得做。
- **v0.6.0 commit**：未提交（按用户要求跳过）。
- **用时**：约 60 分钟。

---

## 4. 附加说明

### 4.1 关键接口与 PLAN 差异

1. **无 `gateway` 单例**：PLAN 示例 `from app.llm.gateway import gateway` 不存在，实际 `from app.llm.gateway import LLMGateway` + `gateway = LLMGateway(settings)`。
2. **`execute` 签名**：`await execute(name, raw_args)`，`raw_args` 是 JSON 字符串（非 dict），返回 `ToolResult(ok/content/error/latency_ms/sources)`。
3. **assistant 消息回填**：不用 `msg.model_dump(exclude_none=True)`（避免 refusal/audio 多余字段被上游 400），改手动构造 `role/content/tool_calls`（PLAN §10 兜底方案）。
4. **demo/eval 用例里 repo 全名**：gitea 白名单只有 `infinity/workpilot`，故用例显式写 `infinity/workpilot`，否则模型猜 `workpilot/workpilot` 会 `repo not allowed`。

### 4.2 依赖与公网

- 无新增依赖（httpx/ddgs 等均 Day35 已装）；`uv` 已配清华镜像。
- 本任务为**库级 + 脚本级**能力，用本地 `python` 验收，不涉及公网 8.148.216.61 部署变更。

### 4.3 未提交（按用户要求）

- 所有改动保留在工作区未提交，见第 1 节改动清单。
- `.env` 内的 Gitea token 属敏感信息，已 gitignore，不入库。

### 4.4 已知遗留（Backlog）

- 工具选择虽 100%，但个别用例存在「多调」（如 ts-14 多次 http_fetch、ts-08 顺带 calculator），属成本优化项，非正确性缺陷；W10 手写 Agent 时再约束。
- `web_search` ddgs 兜底偶发无结果（网络/配额），建议 W10 前补 Tavily key 提升稳定性。
