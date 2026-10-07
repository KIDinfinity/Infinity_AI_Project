# Week 09 · TASKS

## Task 1：Tool Calling 原理 + Registry（Day34 · 11-23）

### 做什么

1. 在 `~/lab/projects/ai-lab/tool-calling/` 用裸 OpenAI SDK 调 DeepSeek 的 `tools` 参数，跑通一次完整的工具调用消息往返，画出消息序列图。
2. 给 M1 Gateway 增加 `chat_with_tools()`（复用已有重试 / 超时 / 计费）。
3. 实现 `apps/api/app/tools/registry.py`：`Tool`、`ToolOutput`、`ToolResult`、`@register`、`to_openai_tools()`、`execute()`。
4. 实现 `builtin/calculator.py`（ast 安全求值，禁止 `eval`），写单测。

### 为什么做

工具层是 Agent 的「手」。先用 20 分钟裸实验看清协议本身，再封装，后续 LangGraph 再怎么包装都能讲清底层发生了什么。

### 资产锚点

M6.1 Tool Registry → v0.6

### 前置依赖

- WorkPilot v0.5：`app/llm/gateway.py`、`app/core/config.py` 可用；DeepSeek key 在 `.env`。
- `uv run pytest` 在 `apps/api` 下是绿的。

### 具体执行步骤（概要，详见 day34_20261031/PLAN.md）

1. 裸实验 `raw_tool_call.py` + `NOTES.md`（序列图）。
2. Gateway 加 `chat_with_tools(messages, tools, tool_choice)`。
3. 写 `registry.py` 骨架；让 AI 生成样板，自己审 `execute()` 的异常路径。
4. 写 `calculator.py`；写 `tests/tools/test_registry.py`（schema / 非法参数 / 超时 / 未知工具）。
5. 提交。

### 验收标准

- [ ] 裸实验输出包含 `tool_calls` 的 id / name / arguments 和第二轮最终答案
- [ ] `to_openai_tools()` 返回 `[{"type":"function","function":{name, description, parameters}}]`
- [ ] `execute()` 对非法参数 / 超时 / 未知工具返回 `ok=False`，不抛异常
- [ ] `calculator` 拒绝 `__import__('os')` 之类表达式
- [ ] `uv run pytest tests/tools -q` 全绿

### 完成后的产出（文件路径）

`ai-lab/tool-calling/raw_tool_call.py`、`ai-lab/tool-calling/NOTES.md`、`apps/api/app/tools/registry.py`、`apps/api/app/tools/builtin/calculator.py`、`apps/api/tests/tools/test_registry.py`、`apps/api/app/llm/gateway.py`（改）

### 求职映射

Function Calling 协议、JSON Schema、Pydantic v2、异步超时控制 → AI Engineer / LLM Application Engineer。

### 如果时间不够 / 没有必要

裸实验压缩到只打印 `tool_calls`；超时测试可放 Day35 开头补。

---

## Task 2：内置工具（Day35 · 11-24）

### 做什么

实现 4 个只读业务工具：`kb_search`（包装 `rag.retrieve`）、`web_search`（Tavily，备选 ddgs）、`gitea_repo_read`（列目录 / 读文件）、`gitea_issue_read`（列出 / 搜索 Issue）；P2 实现 `http_fetch`（SSRF 防护）。统一截断 + 来源标注 + `<tool_output untrusted="true">` 包裹。

### 为什么做

这 4 个工具覆盖 WorkPilot 的三类信息源：团队知识（KB）、公开互联网、代码仓库 / Issue。SP-B（需求→任务拆解→Issue）和 Research Agent 都依赖它们。

### 资产锚点

M6.2 内置工具、M6.3 执行保护 → v0.6

### 前置依赖

- Task 1 的 registry 与 `ToolOutput`。
- Gitea 中已生成**只读** token `GITEA_TOKEN`（scope：`read:repository`、`read:issue`）。
- Tavily 免费 API key（`TAVILY_API_KEY`）；没有也能用 ddgs 兜底。

### 具体执行步骤（概要，详见 day35_20261101/PLAN.md）

1. `common.py`：`clip()`、`wrap_untrusted()`、`SourceRef`。
2. 配置项：`GITEA_BASE_URL`、`GITEA_TOKEN`、`GITEA_READ_REPOS`、`TAVILY_API_KEY`。
3. 依次实现 4 个工具；每个工具 1 个 mock 单测 + 1 个 `@pytest.mark.live` 冒烟。
4. P2：`http_fetch` + SSRF 单测。
5. 提交。

### 验收标准

- [ ] 4 个工具已注册，`to_openai_tools()` 能看到 5 个工具（含 calculator）
- [ ] mock 单测全绿；`uv run pytest -m live` 至少 3 个通过
- [ ] 工具输出带 `untrusted="true"` 包裹与 `sources`
- [ ] `gitea_repo_read` 拒绝白名单外仓库与 `..` 路径

### 完成后的产出（文件路径）

`apps/api/app/tools/common.py`、`apps/api/app/tools/builtin/{kb_search,web_search,gitea,http_fetch}.py`、`apps/api/tests/tools/test_builtin_tools.py`、`.env.example`（加键）

### 求职映射

外部系统集成（REST API / token 鉴权）、Mock 测试（respx）、SSRF 与间接注入防护意识 → AI Engineer / AI Agent Engineer。

### 如果时间不够 / 没有必要

`http_fetch` 进 Backlog（W15 护栏时再做）；`gitea_issue_read` 可推到 Day36 第一个 20 分钟。

---

## Task 3：多工具循环 Demo + 工具选择测试 + JD 追踪（Day36 · 11-25）

### 做什么

1. `app/agent/tool_loop.py`：LLM(tools) → 并行执行 tool_calls → 追加消息 → 循环（max_steps=5）→ 最终答案，每步结构化日志；CLI `scripts/tool_demo.py`。
2. `eval/datasets/tool_selection.jsonl` 15 条 + `eval/runners/run_tool_selection.py` 算准确率，报告写入 `eval/reports/`。
3. D 线：`career/job-market.md` 第 1 轮 JD 追踪（10 个新 JD）。A 线（P2）：`docs/product/open-core.md` 草稿。
4. tag `v0.6.0`，周复盘。

### 为什么做

`tool_loop` 是最朴素的「ReAct 式」循环，是 W10 手写 Agent 的前身；工具选择准确率是 §11 半年指标（≥0.85）的第一份基线。

### 资产锚点

M6（整体）、M3.3 前置、M13.1 → v0.6

### 前置依赖

Task 1、Task 2 完成；至少 `kb_search` + `gitea_repo_read` + `calculator` 可用。

### 具体执行步骤（概要，详见 day36_20261102/PLAN.md）

1. 写 `tool_loop.py` 与 CLI，跑 3 个问题看日志。
2. 写 15 条用例（4 条示例 + 11 条自编），跑 runner 出报告。
3. JD 追踪 20 分钟。
4. tag + push + 周复盘。

### 验收标准

- [ ] 至少 1 个问题在同一轮触发 ≥2 个工具调用（并行）并给出答案
- [ ] 达到 max_steps 时能强制收尾而非死循环
- [ ] 工具选择准确率报告存在，含错选明细
- [ ] `v0.6.0` 推送 Gitea + GitHub
- [ ] `job-market.md` 新增第 1 轮追踪段落（10 个 JD + 频次变化）

### 完成后的产出（文件路径）

`apps/api/app/agent/tool_loop.py`、`scripts/tool_demo.py`、`eval/datasets/tool_selection.jsonl`、`eval/runners/run_tool_selection.py`、`eval/reports/20261125-tool-selection.md`、`~/lab/projects/career/job-market.md`、（P2）`docs/product/open-core.md`

### 求职映射

Agent 循环、并行工具调用、评测驱动开发、JD 分析 → AI Agent Engineer。

### 如果时间不够 / 没有必要

用例先写 8 条，周末补齐；JD 追踪压缩到 5 个；`open-core.md` 推迟到 W16 Day56。

---
