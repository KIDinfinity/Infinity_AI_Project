# Day 34 · 2026-11-23 · Week 09 Task 1 执行总结（SUMMARY）

> 对应 PLAN：`PLAN.md`（同目录）。本文件记录「做了什么」+「验收对齐」的逐条完整命令。
> 按你的要求：**未提交任何代码**；验收命令均为可在任意目录下直接复制执行的完整命令（每条都已 `cd` 到绝对路径）。

---

## 一、本次做了什么（总览）

围绕「Tool Calling 原理 + Tool Registry」，完成了 6 个步骤，全部落在 WorkPilot（`~/lab/workpilot`）与裸实验目录（`~/lab/projects/ai-lab/tool-calling`）：

| Step | 内容 | 产物 | 状态 |
| ---- | ---- | ---- | ---- |
| 1 | 裸 SDK 实验 Function Calling 往返 | `~/lab/projects/ai-lab/tool-calling/raw_tool_call.py` + `NOTES.md` | ✅ |
| 2 | Gateway 新增 `chat_with_tools()` | `apps/api/app/llm/gateway.py` | ✅ |
| 3 | Tool Registry 核心逻辑 | `apps/api/app/tools/registry.py` | ✅ |
| 4 | `calculator` 教学工具 + 单测 | `apps/api/app/tools/builtin/calculator.py`、`apps/api/tests/tools/test_registry.py` | ✅ |
| 5 | 提交 | —— | ⏭️ 按你要求**未提交** |
| 6 | 概念自检 | 见 PLAN 第 7 节 5 问（口述答案已在 PLAN 中） | ✅ |

**关键实现细节：**

- `registry.py`：`@register` 装饰器（重名抛 `ValueError`）→ `to_openai_tools()`（Pydantic `model_json_schema()` 生成 parameters）→ `execute()`（`model_validate_json` 校验 → `asyncio.wait_for` 超时 → 异常归一化为 `ok=False` + `error`，**永不抛异常**）。
- `calculator.py`：用 `ast` 白名单（只允许数字 + 运算符）求值，拒绝 `__import__` 等任意代码执行、拒绝超大指数 `2**99999`。
- `chat_with_tools()`：只透传 `tools` / `tool_choice`，复用 `_create()` 的重试/超时/计费/日志，返回 `ToolChatResult`（含 `total_tokens` 与 `cost_cny`）。

---

## 二、验收对齐（逐条对应，命令可直接复制）

> 说明：Day 34 是**纯代码任务**，不涉及部署/HTTP 服务，因此验收命令是 `pytest` / `python`，**没有 curl 命令**。你备注里「公网 IP 8.148.216.61 / Caddyfile 走 HTTP」属于部署相关，本任务不适用（详见第四节）。

### 验收 1 · `raw_tool_call.py` 输出（第一轮 `tool_calls` + 第二轮最终答案）

```bash
cd /Users/infinity/lab/projects/ai-lab/tool-calling && export DEEPSEEK_API_KEY=$(grep -E '^DEEPSEEK_API_KEY=' /Users/infinity/lab/workpilot/.env | cut -d= -f2-) && uv run python raw_tool_call.py
```

**预期输出（expect）：**

```
finish_reason: tool_calls
tool_call: call_00_... calculator {"expression": "(1234*5678)-999"}
final: (1234×5678) − 999 = **7,005,653** | usage: 334 367
```

> 依赖网络 + DeepSeek key（命令已从 `~/lab/workpilot/.env` 自动读取 `DEEPSEEK_API_KEY`，无需手填）。

### 验收 2 · `NOTES.md` 有消息序列图（mermaid）+ 3 条观察

```bash
cat /Users/infinity/lab/projects/ai-lab/tool-calling/NOTES.md
```

**预期输出（expect）：** 文件内含 `sequenceDiagram` mermaid 图（App↔LLM 4 步往返），以及「## 2. 三条观察」小节（执行权在应用 / `tool_call_id` 一一对应 / 工具输出是否被盲信）。

### 验收 3 · Gateway 新增 `chat_with_tools()`，仍记录 tokens / 成本

```bash
cd /Users/infinity/lab/workpilot/apps/api && grep -n "class ToolChatResult\|async def chat_with_tools\|total_tokens\|calc_cost" app/llm/gateway.py
```

**预期输出（expect）：** 能 grep 到 `class ToolChatResult`（第 44 行附近）、`async def chat_with_tools`（第 131 行附近），且函数体内出现 `usage.total_tokens` 与 `calc_cost`（说明仍计费）。

### 验收 4 · `registry.py`（重名报错 / `to_openai_tools` 格式 / `execute` 非法·超时·未知 → `ok=False`）

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run python -c "
import app.tools.builtin  # noqa: F401
import app.tools.registry as R
import asyncio
# ① 重名报错
try:
    @R.register(name='calculator')
    async def _dup(args): return 'x'
except ValueError as e:
    print('[duplicate]', e)
# ② to_openai_tools 格式
t = R.to_openai_tools(['calculator'])[0]
print('[schema]', t['type'], 'required =', t['function']['parameters']['required'])
# ③ execute 三种失败均 ok=False
async def main():
    r1 = await R.execute('calculator', '{\"expr\":\"1+1\"}')
    print('[bad_args]', r1.ok, '|', (r1.error or '')[:40])
    r2 = await R.execute('no_such', '{}')
    print('[unknown]', r2.ok, '|', r2.error)
    @R.register(name='_slow', timeout_s=0.05)
    async def _slow(args): await asyncio.sleep(1)
    try:
        r3 = await R.execute('_slow', '{}')
        print('[timeout]', r3.ok, '|', r3.error)
    finally:
        R._REGISTRY.pop('_slow', None)
asyncio.run(main())
"
```

**预期输出（expect）：**

```
[duplicate] duplicate tool: calculator
[schema] function required = ['expression']
[bad_args] False | invalid_args: [{'type': 'missing', 'loc': (...
[unknown] False | unknown_tool: no_such
[timeout] False | timeout after 0.05s
```

### 验收 5 · `calculator` 用 ast 求值，`__import__('os')`、`2**99999` 被拒绝

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run python -c "
import app.tools.builtin  # noqa: F401
import app.tools.registry as R
import asyncio
async def main():
    ok  = await R.execute('calculator', '{\"expression\":\"(3+5)*2\"}')
    inj = await R.execute('calculator', '{\"expression\":\"__import__(\\\"os\\\")\"}')
    big = await R.execute('calculator', '{\"expression\":\"2**99999\"}')
    print('[ok ]', ok.ok, ok.content)
    print('[inj]', inj.ok, '|', inj.error)
    print('[big]', big.ok, '|', big.error)
asyncio.run(main())
"
```

**预期输出（expect）：**

```
[ok ] True 16
[inj] False | ValueError: unsupported: Call
[big] False | ValueError: exponent too large
```

### 验收 6 · `uv run pytest tests/tools -q` 全绿

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run pytest tests/tools -q
```

**预期输出（expect）：** `8 passed in …`（8 个用例：schema / 正常执行 / 4 个非法参数 / 未知工具 / 超时）。

全量回归（可选）：

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run pytest -q
```

**预期输出（expect）：** `61 passed, 2 deselected`。

---

## 三、产出记录（PLAN 第 11 节）

- 裸实验第一轮 / 第二轮 tokens：`334 / 367`（累计 701）。
- 工具结果改成错误值（`42`）后模型表现：deepseek-chat **没有盲信**，而是自己验算并指出「42 是错误的，正确答案是 7,005,653」（详见 NOTES 观察 3；说明工具输出强引导、但「错得离谱」会被纠偏）。
- registry 单测数量 / 通过：`8 / 8`（`tests/tools/test_registry.py`）。
- 卡点 / 用时：`ruff` 报 `UP035`（`Callable` 应从 `collections.abc` 导入），已修正；无阻塞卡点。

---

## 四、关于你备注的两点说明

1. **公网 IP 8.148.216.61 / Caddyfile 走 HTTP**：Day 34 是纯代码任务（Registry + calculator + 单测），**没有任何部署 / HTTP 暴露**，所以本次验收里没有需要打到公网 IP 的 curl。这条备注我已保留，等到涉及部署的那一天（有真实 HTTP 端点时）再按「公网 IP + HTTP、域名后置」给出对应的完整 curl 验收命令。
2. **未提交代码**：已按要求跳过 PLAN Step 5 的 `git commit` / `git push`。当前 `~/lab/workpilot` 的改动停留在工作区（`modified: apps/api/app/llm/gateway.py` + `untracked: apps/api/app/tools/`、`apps/api/tests/tools/`），随时可由你自行提交。
