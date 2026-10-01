# Day 11 · 2026-10-08 · Week 03 Task 1：Structured Output + Prompt 版本化

## 0. 今天只做一件事

让 LLM Gateway 能稳定返回「通过 Pydantic 校验的 JSON」，并把 prompt 从代码里搬到带版本号的 `prompts/*.md`。

不碰：流式 / 成本（Day12）、检索、function calling、任何框架（instructor / LangChain）。

## 1. 资产锚点

- 构建模块：M1.3 Structured Output、M1.6 Prompt 版本化（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.1 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`POST /v1/structured/answer`、`POST /v1/structured/breakdown` 返回合法 JSON；5 个真实输入的校验通过率（目标 ≥ 4/5）
- 今日 AI 实际应用：JSON mode + schema 注入 + 校验错误回灌 → 用在 v0 文档助手（`StructuredAnswer`）和 SP-B 预演（`TaskBreakdown`），W5 的 LLM-judge 也直接复用

## 2. 起点（前置确认）

- 已有：`~/lab/workpilot/apps/api`（FastAPI 骨架）、`app/llm/gateway.py` 的 `LLMGateway.chat`（timeout/retry）、`POST /v1/chat`、`.env` 中 DeepSeek key。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
grep -n "async def\|def chat\|return" app/llm/gateway.py   # chat 是否 async？返回 str 还是响应对象？
grep -n "class Settings" -A 15 app/core/config.py         # 现有字段名（如 llm_model / llm_api_key）
uv run pytest -q                                          # Day07/08 测试仍绿
uv run uvicorn app.main:app --reload --port 8000          # 另开终端保持运行
curl -s localhost:8000/health
```

> 下文代码以 `settings.llm_model`、模块级单例 `gateway` 为例；若 Day08 命名不同，按实际改，不要两套并存。

## 3. 验收对齐（做完要能勾掉）

- [ ] `gateway.chat()` 返回 `ChatResult`，`/v1/chat` 仍可用
- [ ] `prompts/structured_answer.v1.md`、`prompts/task_breakdown.v1.md` 存在且带 front matter（id / version / model / changelog）
- [ ] `uv run pytest -m "not llm" -q` 全绿（含 prompt 渲染、结构化重试两个单测）
- [ ] `uv run pytest -m llm -s` 打印「structured pass rate: x/5」，x ≥ 4
- [ ] curl `/v1/structured/answer`、`/v1/structured/breakdown` 均返回 200 且字段合法
- [ ] 已 push 到 Gitea

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                         |
| ------- | ------ | -------------------------------------------- |
| 0–10    | P0     | 前置确认 + 读 DeepSeek JSON Output 文档      |
| 10–25   | P0     | Gateway 返回 `ChatResult`，透传 `**extra`    |
| 25–45   | P0     | prompts 目录 + `prompts.py` + 单测           |
| 45–75   | P0     | schemas + `generate_structured()` + 重试单测 |
| 75–90   | P0     | 路由 + curl                                  |
| 90–105  | P1     | 5 输入 live 测试，记录通过率                 |
| 105–120 | P1     | 提交 + 概念自检                              |

时间不足时最低保留：`ChatResult` + `generate_structured()` + `StructuredAnswer` + `/v1/structured/answer`（breakdown 和 live 测试顺延）。

## 5. 今日学习（只学完成任务必须的）

- JSON mode（`response_format={"type":"json_object"}`）只保证「是合法 JSON」，不保证符合你的 schema；DeepSeek 要求 prompt 中出现「json」字样并给出格式示例，且建议设置足够的 `max_tokens` 防截断。
- `Model.model_json_schema()` 生成 JSON Schema，注入 system prompt 让模型知道字段与枚举；`Model.model_validate_json(raw)` 一步完成解析+校验。
- `ValidationError.errors()` 是结构化错误列表，把它回灌给模型（「上面的 JSON 未通过校验：…请修正」）通常 1 次就能修好。
- Prompt 版本化：prompt 是代码的一部分，改 prompt = 改行为，必须有版本号，评测报告才能对比。
- 资料：https://api-docs.deepseek.com/guides/json_mode 、https://docs.pydantic.dev/latest/concepts/json_schema/ 、https://docs.pydantic.dev/latest/concepts/models/ 、https://fastapi.tiangolo.com/tutorial/body/

## 6. 执行步骤

### Step 1 · Gateway 返回 ChatResult（核心逻辑自己写）

新建 `apps/api/app/llm/schemas.py`：

```python
from typing import Literal
from pydantic import BaseModel, Field

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cache_hit_tokens: int = 0          # DeepSeek: usage.prompt_cache_hit_tokens

class ChatResult(BaseModel):
    content: str
    model: str
    usage: Usage
    latency_ms: int

class StructuredAnswer(BaseModel):
    answer: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list, max_length=8)
    confidence: Literal["low", "mid", "high"]
    needs_more_context: bool

class TaskItem(BaseModel):
    title: str
    type: Literal["frontend", "backend", "test", "doc"]
    estimate_hours: float = Field(gt=0, le=40)
    acceptance: str

class TaskBreakdown(BaseModel):
    title: str
    tasks: list[TaskItem] = Field(min_length=1, max_length=20)
```

修改 `gateway.py` 的 `chat()`（保留 Day08 的 retry/timeout 包装，只改签名与返回）：

```python
async def chat(self, messages: list[dict], **extra) -> ChatResult:
    t0 = time.perf_counter()
    resp = await self._create(model=self.model, messages=messages, **extra)  # _create = Day08 带重试的调用
    u = resp.usage
    return ChatResult(
        content=resp.choices[0].message.content or "",
        model=resp.model,
        usage=Usage(prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens,
                    total_tokens=u.total_tokens,
                    cache_hit_tokens=getattr(u, "prompt_cache_hit_tokens", 0) or 0),
        latency_ms=int((time.perf_counter() - t0) * 1000),
    )
```

同步改 `/v1/chat` 路由：返回 `result.model_dump()`。`uv run pytest -q` 确认旧测试仍绿（必要时更新断言）。

### Step 2 · prompts 目录 + 加载器

```bash
cd ~/lab/workpilot && mkdir -p prompts
cd apps/api && uv add pyyaml
```

`prompts/structured_answer.v1.md`：

```markdown
---
id: structured_answer
version: 1
model: deepseek-chat
changelog:
  - "v1 2026-10-08: 初版，用于文档助手 v0 的结构化回答"
---

请回答下面的研发技术问题，并只输出一个 json 对象。

问题：{question}
可参考的上下文（可能为空）：{context}

要求：

1. answer 用中文，≤ 300 字，先给结论再给理由。
2. key_points 列 2–5 条要点。
3. 你不确定或问题依赖特定团队/公司内部信息时，confidence 设为 low，needs_more_context 设为 true，不要编造。
```

`prompts/task_breakdown.v1.md`（同样 front matter，id: task_breakdown）：正文要求把 `{requirement}` 按 `{stack}` 拆成 3–10 个任务，每个任务给 type、estimate_hours（0.5–16）、可验证的 acceptance，只输出 json。

`apps/api/app/core/config.py` 增加（`REPO_ROOT` 指向 workpilot 根目录）：

```python
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[4]   # core→app→api→apps→workpilot
# Settings 类内：
prompts_dir: Path = REPO_ROOT / "prompts"
```

`apps/api/app/llm/prompts.py`：

```python
import re
from dataclasses import dataclass
from functools import lru_cache
import yaml
from app.core.config import settings

_FM = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
_VAR = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")   # 只匹配 {标识符}，JSON 示例里的 {"a": 1} 不受影响

@dataclass(frozen=True)
class Prompt:
    id: str
    version: str
    model: str
    body: str

    @property
    def ref(self) -> str:
        return f"{self.id}.v{self.version}"

    def render(self, **values: object) -> str:
        missing = set(_VAR.findall(self.body)) - values.keys()
        if missing:
            raise KeyError(f"prompt {self.ref} 缺少变量: {sorted(missing)}")
        return _VAR.sub(lambda m: str(values[m.group(1)]), self.body)

@lru_cache
def load_prompt(name: str) -> Prompt:          # name 形如 "structured_answer.v1"
    path = settings.prompts_dir / f"{name}.md"
    m = _FM.match(path.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{path} 缺少 front matter")
    meta = yaml.safe_load(m.group(1))
    return Prompt(id=meta["id"], version=str(meta["version"]),
                  model=meta.get("model", ""), body=m.group(2).strip())
```

为什么不用 `str.format`：prompt 里一旦出现 JSON 示例的 `{`，`format` 会直接报 `KeyError`/`ValueError`。

`tests/test_prompts.py`（让 AI 生成，自己审）：加载 `structured_answer.v1` → `ref == "structured_answer.v1"`；缺变量时抛 `KeyError`；body 含 `{"a": 1}` 时渲染不报错。

### Step 3 · generate_structured()（核心逻辑必须自己理解）

`apps/api/app/llm/structured.py`：

```python
import json
from typing import TypeVar
from pydantic import BaseModel, ValidationError
from app.llm.gateway import gateway
from app.llm.schemas import ChatResult

T = TypeVar("T", bound=BaseModel)

SYSTEM = (
    "你是 WorkPilot 的结构化输出模块。只输出一个 json 对象，不要 Markdown 代码块，不要解释。\n"
    "json 必须符合以下 JSON Schema：\n{schema}"
)

class StructuredError(Exception):
    pass

async def generate_structured(model_cls: type[T], messages: list[dict],
                              max_retries: int = 1, **extra) -> tuple[T, ChatResult]:
    schema = json.dumps(model_cls.model_json_schema(), ensure_ascii=False)
    msgs = [{"role": "system", "content": SYSTEM.format(schema=schema)}, *messages]
    extra.setdefault("temperature", 0.2)        # 调用方可覆盖（W5 judge 传 temperature=0）
    extra.setdefault("max_tokens", 1500)
    last_err: Exception | None = None
    for _ in range(max_retries + 1):
        res = await gateway.chat(msgs, response_format={"type": "json_object"}, **extra)
        try:
            return model_cls.model_validate_json(res.content), res
        except ValidationError as e:          # 空字符串 / 非法 JSON / 字段不合法 都会进这里
            last_err = e
            msgs += [
                {"role": "assistant", "content": res.content or "(空)"},
                {"role": "user", "content": "上面的 json 未通过校验，错误如下，请修正后只输出完整 json：\n"
                    + json.dumps(e.errors(include_url=False), ensure_ascii=False, default=str)},
            ]
    raise StructuredError(f"{model_cls.__name__} 校验失败：{last_err}")
```

`pyproject.toml` 增加：

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
markers = ["llm: 需要真实 LLM API（默认跳过：pytest -m 'not llm'）"]
```

```bash
uv add --dev pytest-asyncio
```

`tests/test_structured.py`（假 Gateway：第一次返回缺字段 JSON，第二次返回合法 JSON）：

```python
from app.llm import structured
from app.llm.schemas import ChatResult, StructuredAnswer, Usage

class FakeGW:
    def __init__(self, outputs): self.outputs, self.calls = list(outputs), []
    async def chat(self, msgs, **kw):
        self.calls.append(msgs)
        return ChatResult(content=self.outputs.pop(0), model="fake", usage=Usage(), latency_ms=1)

async def test_retry_then_ok(monkeypatch):
    fake = FakeGW(['{"answer": "x"}',
                   '{"answer":"x","key_points":[],"confidence":"low","needs_more_context":true}'])
    monkeypatch.setattr(structured, "gateway", fake)
    data, _ = await structured.generate_structured(StructuredAnswer, [{"role": "user", "content": "q"}])
    assert data.confidence == "low" and len(fake.calls) == 2
    assert "未通过校验" in fake.calls[1][-1]["content"]
```

再补一条：两次都非法 → `pytest.raises(structured.StructuredError)`。

### Step 4 · 路由

`apps/api/app/routes/structured.py`（样板让 AI 生成）：`AnswerReq{question, context=""}`、`BreakdownReq{requirement, stack="React + FastAPI"}`；渲染 prompt → `generate_structured` → 返回 `{"data": ..., "prompt": p.ref, "usage": ..., "latency_ms": ...}`；`StructuredError` → `HTTPException(502, "structured output failed")`（不把模型原文回给前端）。在 `main.py` `include_router`。

```bash
curl -s localhost:8000/v1/structured/answer -H 'Content-Type: application/json' \
  -d '{"question":"React 的 useEffect 依赖数组为空时什么时候执行？"}' | python -m json.tool
curl -s localhost:8000/v1/structured/breakdown -H 'Content-Type: application/json' \
  -d '{"requirement":"给知识库页面加文档上传：支持 md/pdf，显示处理状态，失败可重试"}' | python -m json.tool
```

预期：`data.confidence` 为 low/mid/high 之一；`data.tasks[*].type` 只出现四种值。

### Step 5 · 5 输入通过率（P1）

`tests/test_structured_live.py`：`@pytest.mark.llm`，5 个输入（3 个 answer：通用问题 / 团队内部问题 / 模糊问题；2 个 breakdown），逐个调用，统计「最终校验通过」与「首次即通过」数，`print(f"structured pass rate: {ok}/5, first-try: {first}/5")`，`assert ok >= 4`。

```bash
uv run pytest -m llm -s -q
```

把两个数写进第 11 节。

### Step 6 · 提交

```bash
cd ~/lab/workpilot
uv run --project apps/api ruff check apps/api && uv run --project apps/api ruff format apps/api
git add prompts apps/api
git commit -m "feat(llm): structured output with pydantic validation and versioned prompts"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. JSON mode 能保证输出符合 schema 吗？（答：不能，只保证合法 JSON；schema 靠 prompt 注入 + Pydantic 校验 + 重试保证。）
2. 为什么把校验错误回灌给模型而不是直接重发同一请求？（答：同样输入大概率同样错误；把具体错误字段告诉模型，修复成功率高且只多一次调用。）
3. `Literal["low","mid","high"]` 在 JSON Schema 里变成什么？（答：`enum`，模型能看到合法取值。）
4. 为什么 prompt 渲染不用 `str.format`？（答：JSON 示例中的花括号会被当成占位符导致报错。）
5. prompt 改了一个词也要升版本吗？（答：要；行为可能改变，评测报告需要能追溯到具体版本。）

## 8. 对 DA-01 的贡献

WorkPilot 从「能聊天」变成「能产出可被程序消费的结构化结果」：v0 文档助手、SP-B 需求拆解、W5 judge、W9 工具参数都基于这层。Prompt 版本化让后续每份评测报告都能记录「用的是哪个 prompt」。

## 9. 求职映射（D 线）

- 岗位能力：LLM Structured Output、Prompt Engineering 工程化、Pydantic 数据校验。
- 对应岗位：AI Engineer、LLM Application Engineer、AI Full-Stack Engineer。
- 简历 bullet 草稿：「实现基于 Pydantic v2 的 LLM 结构化输出层（JSON mode + schema 注入 + 校验失败自动修复重试），结构化调用最终通过率 **/5（首次通过 **/5），并建立带版本号与变更记录的 Prompt 管理机制。」
- 面试可能问：
  1. 「模型偶尔返回非法 JSON / 缺字段，你怎么处理？」——要点：JSON mode → schema 注入 → Pydantic 校验 → 错误回灌重试 1 次 → 仍失败返回 502 并记录 badcase；不无限重试（成本）。
  2. 「Prompt 怎么管理？」——要点：文件化 + front matter 版本 + changelog + 代码只按 `id.vN` 引用 + 评测报告记录版本。

## 10. 卡住时的处理

| 现象                                                                           | 处理                                                                                                        |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `openai.BadRequestError: ... response_format ... must contain the word "json"` | prompt / system 中加入小写「json」字样（SYSTEM 已含），确认消息确实传进去了                                 |
| 返回 `content` 为空字符串                                                      | DeepSeek 文档提到 JSON 模式偶发空内容：调大 `max_tokens`、prompt 给示例；`generate_structured` 的重试会兜底 |
| `pydantic_core.ValidationError: Invalid JSON: EOF while parsing`               | 输出被截断，`max_tokens` 调大到 2000，或要求 answer ≤ 300 字                                                |
| `KeyError: prompt structured_answer.v1 缺少变量`                               | 路由调用 `render()` 时漏传变量（如 `context`），传空字符串也要传                                            |
| `FileNotFoundError: .../prompts/structured_answer.v1.md`                       | `REPO_ROOT` 层级算错：在 Python 里 `print(settings.prompts_dir)` 检查                                       |
| 测试报 `async def functions are not natively supported`                        | 未装 pytest-asyncio 或未设 `asyncio_mode = "auto"`                                                          |

## 11. 产出记录（执行时填写）

- `ChatResult` 改造后 `/v1/chat` 是否正常：\_\_\_\_
- 结构化通过率（最终 / 首次）：\_**\_ / \_\_**
- 一次典型调用的 tokens / 延迟：\_**\_ / \_\_** ms
- 发现的 schema 设计问题（如字段太多、枚举不清）：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day12（Streaming SSE + 成本记录 + CLI 聊天）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
