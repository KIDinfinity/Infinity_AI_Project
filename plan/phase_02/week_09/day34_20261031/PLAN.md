# Day 34 · 2026-10-31 · Week 09 Task 1：Tool Calling 原理 + Registry

## 0. 今天只做一件事

先用裸 SDK 看清 Function Calling 的消息往返，再把它封装成 WorkPilot 的 Tool Registry（含 `calculator` 教学工具与单测）。

不碰：kb_search / web_search / gitea 等业务工具（Day35）、Agent 循环（Day36）、LangGraph（W11）、任何写工具。

## 1. 资产锚点

- 构建模块：M6.1 Tool Registry（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.6 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`registry.to_openai_tools()` 能输出标准 tools 列表；`await execute("calculator", '{"expression":"(3+5)*2"}')` 返回 `ToolResult(ok=True, content="16", latency_ms=…)`；`pytest tests/tools` ≥ 6 个用例全绿。
- 今日 AI 实际应用：Function Calling 协议（tools / tool_calls / role=tool / tool_call_id）→ 用在 WorkPilot 的 M1 Gateway `chat_with_tools()` 与 M6 Registry。

## 2. 起点（前置确认）

- 已有：WorkPilot v0.5（`apps/api` FastAPI、`app/llm/gateway.py`、`app/core/config.py`），DeepSeek key 在 `apps/api/.env`。
- 需确认：

```bash
cd ~/lab/workpilot && git status && git log --oneline -3 && git tag | tail -3   # 期望看到 v0.5.0
cd apps/api && uv run pytest -q                                                 # 期望全绿
uv run python -c "import openai, pydantic; print(openai.__version__, pydantic.__version__)"  # openai>=1.x, pydantic 2.x
grep -n "def chat\|def structured\|def stream" app/llm/gateway.py              # 确认 Gateway 的入口函数名
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `raw_tool_call.py` 输出：第一轮 `finish_reason=tool_calls` + tool_call 的 id/name/arguments；第二轮给出最终答案
- [ ] `NOTES.md` 有消息序列图（mermaid）+ 3 条观察
- [ ] Gateway 新增 `chat_with_tools()`，仍记录 tokens / 成本
- [ ] `registry.py`：`@register` 重名报错；`to_openai_tools()` 格式正确；`execute()` 非法参数 / 超时 / 未知工具均返回 `ok=False`
- [ ] `calculator` 用 ast 求值，`__import__("os")`、`2**99999` 被拒绝
- [ ] `uv run pytest tests/tools -q` 全绿，已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                          |
| ----------- | ------ | ------------------------------------------------------------- |
| 0–20 min    | P0     | 裸实验 + 序列图                                               |
| 20–35 min   | P0     | Gateway `chat_with_tools()`                                   |
| 35–75 min   | P0     | `registry.py`（AI 生成样板，自己审 `execute()`）              |
| 75–95 min   | P0     | `calculator.py` + 单测                                        |
| 95–105 min  | P1     | 概念自检 + 产出记录                                           |
| 105–120 min | P2     | 试一次 `tool_choice="required"` / `"none"` 的差异，记到 NOTES |

时间不足时最低保留：`registry.py` + `calculator.py` + 3 个单测（schema / 非法参数 / 超时）。

## 5. 今日学习（只学完成任务必须的）

- **tools 参数**：每个工具 = `{"type":"function","function":{name, description, parameters(JSON Schema)}}`，模型只「建议」调用，执行永远在你的代码里。
- **tool_calls 往返**：模型返回 assistant 消息带 `tool_calls[]`；你必须把这条 assistant 消息原样追加，再为每个 call 追加 `{"role":"tool","tool_call_id":..., "content":...}`，否则下一轮报错。
- **description 就是提示词**：工具选得准不准，主要取决于 name + description + 参数描述，而不是代码。
- **Pydantic → JSON Schema**：`Model.model_json_schema()` 直接生成 `parameters`；`Model.model_validate_json(raw)` 做入参校验。
- **超时**：`asyncio.wait_for(coro, timeout)` 超时抛 `TimeoutError`（3.11+ 与 `asyncio.TimeoutError` 同一个类）。
- 资料：https://api-docs.deepseek.com/guides/function_calling · https://platform.openai.com/docs/guides/function-calling · https://docs.pydantic.dev/latest/concepts/json_schema/ · https://docs.python.org/3/library/ast.html

## 6. 执行步骤

### Step 1 · 裸实验（ai-lab，20 分钟）

```bash
mkdir -p ~/lab/projects/ai-lab/tool-calling && cd ~/lab/projects/ai-lab/tool-calling
uv init --bare && uv add openai
export DEEPSEEK_API_KEY=sk-...   # 只在当前终端，不写入文件
```

`raw_tool_call.py`（可让 AI 生成，自己逐行读懂）：

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
tools = [{"type": "function", "function": {
    "name": "calculator", "description": "精确计算算术表达式，涉及数字运算时必须使用",
    "parameters": {"type": "object", "required": ["expression"],
                   "properties": {"expression": {"type": "string", "description": "如 (3+5)*2"}}}}}]
messages = [{"role": "user", "content": "(1234*5678)-999 等于多少？"}]

r1 = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools)
m = r1.choices[0].message
print("finish_reason:", r1.choices[0].finish_reason)
messages.append(m.model_dump(exclude_none=True))          # 1) 原样追加 assistant(tool_calls)
for tc in m.tool_calls or []:
    print("tool_call:", tc.id, tc.function.name, tc.function.arguments)
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": "7005653"})  # 2) 假装执行（不写 eval）
r2 = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools)
print("final:", r2.choices[0].message.content, "| usage:", r1.usage.total_tokens, r2.usage.total_tokens)
```

`uv run python raw_tool_call.py` 预期：`finish_reason: tool_calls` → `tool_call: call_xxx calculator {"expression":"(1234*5678)-999"}` → `final: … 7,005,653`。

小实验（2 分钟）：把 tool 消息的 content 改成 `"42"`，观察模型是否盲信工具结果 → 写进 NOTES（「工具输出决定答案」，也是间接注入的根源）。`NOTES.md` 用 mermaid `sequenceDiagram` 画 4 步：App→LLM（user + tools）→ LLM→App（assistant.tool_calls）→ App 执行工具 → App→LLM（user, assistant(tool_calls), tool{tool_call_id}）→ 最终答案。

### Step 2 · Gateway 增加 `chat_with_tools()`

打开 `apps/api/app/llm/gateway.py`，找到 phase_01 已有的「带重试 / 超时 / 计费」的内部调用函数（名字以你仓库为准，下面记作 `_create()`），新增一个对外方法，**只透传 tools 参数，不重写重试逻辑**：

```python
@dataclass
class ToolChatResult:
    message: ChatCompletionMessage          # openai.types.chat；含 .content / .tool_calls
    total_tokens: int
    cost_cny: float

async def chat_with_tools(self, messages: list[dict], tools: list[dict], tool_choice: str = "auto", **kw):
    resp = await self._create(messages=messages, tools=tools, tool_choice=tool_choice, **kw)
    u = resp.usage
    return ToolChatResult(resp.choices[0].message, u.total_tokens if u else 0, self._cost(u))  # 复用 pricing.py
```

若 phase_01 的 Gateway 是同步实现，保持同步签名，Agent 循环里用 `await asyncio.to_thread(...)` 包一层。

### Step 3 · Registry（核心逻辑自己审）

目录：`apps/api/app/tools/{__init__.py, registry.py, builtin/__init__.py, builtin/calculator.py}`；`builtin/__init__.py` 写 `from . import calculator`（导入即注册）。

`registry.py` 数据结构（让 AI 按此生成）：`Permission = Literal["read","write","dangerous"]`；`MAX_CONTENT_CHARS = 6000`；`SourceRef(kind: Literal["kb","web","gitea"], ref, title="")`（Day35 起填，W10 报告做 [S1] 映射）；`ToolOutput(text, sources=[])`；`ToolResult(ok, content="", error=None, latency_ms=0, truncated=False, sources=[])`；`@dataclass(frozen=True) Tool(name, description, args_model, permission, func, timeout_s=10.0)`；`_REGISTRY: dict[str, Tool]`。

函数骨架（`execute()` 必须自己逐行审）：

```python
def register(*, name, description, args_model, permission: Permission = "read", timeout_s=10.0):
    def deco(func):
        if name in _REGISTRY:
            raise ValueError(f"duplicate tool: {name}")
        _REGISTRY[name] = Tool(name, description, args_model, permission, func, timeout_s)
        return func
    return deco

def get_tool(name: str) -> Tool | None:
    return _REGISTRY.get(name)

def to_openai_tools(names: list[str] | None = None, allow: tuple[Permission, ...] = ("read",)) -> list[dict]:
    return [{"type": "function", "function": {"name": t.name, "description": t.description,
             "parameters": t.args_model.model_json_schema()}}
            for t in _REGISTRY.values() if t.permission in allow and (names is None or t.name in names)]

async def execute(name: str, raw_args: str | None) -> ToolResult:
    start = time.perf_counter()
    def done(**kw) -> ToolResult:
        return ToolResult(latency_ms=int((time.perf_counter() - start) * 1000), **kw)
    tool = _REGISTRY.get(name)
    if tool is None:
        return done(ok=False, error=f"unknown_tool: {name}")
    try:
        args = tool.args_model.model_validate_json(raw_args or "{}")
    except ValidationError as e:
        return done(ok=False, error=f"invalid_args: {e.errors(include_url=False)}")
    try:
        out = await asyncio.wait_for(tool.func(args), timeout=tool.timeout_s)
    except TimeoutError:
        return done(ok=False, error=f"timeout after {tool.timeout_s}s")
    except Exception as e:                       # 错误归一化：交给 Agent 当作观察
        return done(ok=False, error=f"{type(e).__name__}: {e}")
    out = out if isinstance(out, ToolOutput) else ToolOutput(text=str(out))
    text = out.text
    return done(ok=True, content=text[:MAX_CONTENT_CHARS],
                truncated=len(text) > MAX_CONTENT_CHARS, sources=out.sources)
```

必须自己理解的点：① 为什么 `execute` 永不抛异常；② `allow` 默认只给 read（W12 审批前不暴露写工具）；③ `ValidationError` 信息会回给模型，模型能据此自我修正参数。

### Step 4 · calculator + 单测

`builtin/calculator.py`：

```python
import ast, operator
from pydantic import BaseModel, Field
from app.tools.registry import register

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}

class CalcArgs(BaseModel):
    expression: str = Field(..., max_length=200, description="算术表达式，如 (3+5)*2/7")

def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError(f"unsupported: {type(node).__name__}")

@register(name="calculator", args_model=CalcArgs, timeout_s=2,
          description="精确计算算术表达式（+ - * / // % ** 括号）。任何数字计算都必须用它，不要心算。")
async def calculator(args: CalcArgs) -> str:
    return str(_eval(ast.parse(args.expression, mode="eval")))
```

`apps/api/tests/tools/test_registry.py`（让 AI 补全样板）：

- `test_openai_schema`：`to_openai_tools(["calculator"])[0]` 的 `type == "function"`，`parameters.required == ["expression"]`。
- `test_ok`：`execute("calculator", '{"expression":"(3+5)*2"}')` → `ok and content == "16"`。
- `test_bad_args_return_error`（参数化 4 例）：`'{"expr":"1+1"}'`、`"not json"`、`__import__('os')`、`2**99999` → 均 `ok=False` 且有 `error`。
- `test_unknown_tool`：`error.startswith("unknown_tool")`。
- `test_timeout`：测试内 `@R.register(name="_slow", timeout_s=0.05)` 注册一个 `await asyncio.sleep(1)` 的工具 → `"timeout" in error`；`finally: R._REGISTRY.pop("_slow")`。
- 所有 async 测试加 `@pytest.mark.asyncio`；文件头 `import app.tools.builtin  # noqa: F401` 触发注册。
- 运行：`cd ~/lab/workpilot/apps/api && uv add --dev pytest-asyncio`（已装则跳过）`&& uv run pytest tests/tools -q`，预期 8 passed。

### Step 5 · 提交

```bash
cd ~/lab/workpilot
git add apps/api/app/tools apps/api/app/llm/gateway.py apps/api/tests/tools apps/api/pyproject.toml apps/api/uv.lock
git commit -m "feat(tools): add tool registry, calculator and gateway chat_with_tools"
git push
cd ~/lab/projects && git add ai-lab/tool-calling && git commit -m "docs(ai-lab): tool calling raw experiment" && git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 模型会直接执行工具吗？（答：不会。模型只输出「想调用哪个工具 + JSON 参数」，执行、权限、超时全在应用代码里。）
2. `tool_call_id` 有什么用？（答：把 tool 结果与 assistant 的某个 tool_call 一一对应；一轮多个并行调用时靠它区分。）
3. 为什么要把 assistant(tool_calls) 原样追加到 messages？（答：协议要求 tool 消息前必须有对应的 tool_calls；缺失会报 400，模型也会丢失「自己调过什么」的上下文。）
4. 为什么 `execute()` 不抛异常而返回 `ok=False`？（答：错误是 Agent 的一种观察，模型可以据此换参数或换工具；抛异常会中断整个循环。）
5. 为什么 calculator 不能用 `eval`？（答：参数来自模型、模型输入可能被注入，`eval` 等于远程代码执行；ast 白名单只允许数字和运算符。）

## 8. 对 DA-01 的贡献

WorkPilot 有了统一的「工具插座」：之后每个能力（KB、Web、Gitea、MCP 外部工具、场景包写操作）都以同一种方式注册、校验、限时、截断、带权限，这是 F3 Agent 任务中心与 F7 工具权限白名单的地基。

## 9. 求职映射（D 线）

- 岗位能力：Function Calling / Tool Use、JSON Schema、Python asyncio、防御式编程。
- 对应岗位：AI Engineer、LLM Application Engineer、AI Agent Engineer。
- 简历 bullet 草稿：基于 Pydantic v2 设计 Agent 工具注册中心，自动生成 JSON Schema、三级权限控制、统一超时与错误归一化，工具异常不再中断 Agent 流程（单测 N 个，覆盖率 X%）。
- 面试可能问：
  - Q：Function Calling 和让模型输出 JSON 再自己解析有什么区别？要点：协议层支持、参数 schema 约束、多工具并行、`tool_call_id` 对应、模型针对性训练使选择更稳。
  - Q：工具参数校验失败怎么处理？要点：返回结构化错误给模型自我修正，设上限防死循环，记录日志。

## 10. 卡住时的处理

| 现象                                           | 处理                                                                                                                                |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 第一轮没有 `tool_calls`，模型直接心算          | 加强 description（「必须使用」）；或临时 `tool_choice="required"` 观察差异                                                          |
| 第二轮 400：messages 格式错误                  | 检查是否追加了 assistant(tool_calls) 消息、`tool_call_id` 是否一致；用 `model_dump(exclude_none=True)`                              |
| `model_json_schema()` 里出现 `$defs` / `title` | 正常，DeepSeek 可接受；嵌套模型过深时改为扁平参数                                                                                   |
| `pytest` 报 async 函数未执行 / skipped         | 未装或未启用 pytest-asyncio；在 `pyproject.toml` 加 `[tool.pytest.ini_options] asyncio_mode = "auto"` 或保留 `@pytest.mark.asyncio` |
| 重复运行测试报 `duplicate tool`                | 测试注册的临时工具要在 finally 里 `pop`；不要在测试里重复 import 注册模块的副本                                                     |
| Gateway 内部函数名对不上                       | 先 `grep -n "chat.completions.create" app/llm/gateway.py` 找到唯一调用点，在那里加 `**kw` 透传                                      |

## 11. 产出记录（执行时填写）

- 裸实验第一轮 / 第二轮 tokens：（待填）；工具结果改成错误值后模型表现：（待填）
- registry 单测数量 / 通过：（待填）
- 卡点 / 用时：（待填）

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day35「内置工具：kb_search / web_search / gitea_read」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
