# Day 11 · 执行报告（2026-10-12）

> 对应 `PLAN.md`（Week 03 · Task 1：Structured Output + Prompt 版本化）。
> 主产出仓库：`~/lab/workpilot`。
> **按用户要求：不提交、不 push**（PLAN §6 Step 6 整体跳过）。所有改动保留在工作区，清单见第三节。

## 一、逐步执行记录

| Step | 内容 | 结果 |
| --- | --- | --- |
| 0 | 前置确认 | 完成。`gateway.chat()` 原为 async、返回 `ChatResult`（字段为平铺的 `prompt_tokens`/`completion_tokens`）；`Settings` 已有 `llm_provider`/`llm_api_key` 等字段。Day07/08 测试基线 14 passed。 |
| 1 | Gateway 返回 `ChatResult` | 完成。新增 `Usage` 嵌套模型，`ChatResult.usage` 改为嵌套对象；`/v1/chat` 仍 200。**破坏性变更**：`usage` 由平铺改嵌套，旧测试 3 处断言同步更新。 |
| 2 | prompts 目录 + 加载器 | 完成。`prompts/structured_answer.v1.md`、`prompts/task_breakdown.v1.md`（含 front matter）；`app/llm/prompts.py`（front matter 解析 + `{标识符}` 占位渲染）；`uv add pyyaml`。 |
| 3 | schemas + `generate_structured()` | 完成。`StructuredAnswer`/`TaskItem`/`TaskBreakdown`；`structured.py`（JSON mode + schema 注入 + `model_validate_json` + 校验错误回灌重试 1 次）。加 `pytest-asyncio`。 |
| 4 | 路由 + curl | 完成。`POST /v1/structured/answer`、`POST /v1/structured/breakdown` 均 200 且字段合法（详见 §二）。 |
| 5 | 5 输入 live 通过率 | 完成。`uv run pytest -m llm -s` → **structured pass rate: 5/5, first-try: 5/5**（0 次重试）。 |
| 6 | 提交 | ⏭️ **按用户要求未提交**。 |

## 二、验收对齐（PLAN §3）

- [x] `gateway.chat()` 返回 `ChatResult`，`/v1/chat` 仍可用 → `POST /v1/chat {"messages":[{"role":"user","content":"只回复 pong"}],"max_tokens":8}` → 200，`content="pong"`、`model=deepseek-flash`、`usage={8,2,10,cache_hit:0}`、`latency_ms=585`
- [x] `prompts/structured_answer.v1.md`、`prompts/task_breakdown.v1.md` 存在且带 front matter（id / version / model / changelog）
- [x] `uv run pytest -m "not llm" -q` 全绿 → **21 passed, 2 deselected**（含 prompt 渲染、结构化重试单测）
- [x] `uv run pytest -m llm -s` 打印「structured pass rate: 5/5, first-try: 5/5」，x ≥ 4
- [x] curl `/v1/structured/answer`、`/v1/structured/breakdown` 均返回 200 且字段合法 → answer `prompt=structured_answer.v1`、`confidence=high`、5 个 key_points、`usage={326,244,570,cache_hit:128}`；breakdown `prompt=task_breakdown.v1`、9 tasks、`types=['backend','doc','frontend','test']`、`usage={476,900,1376,cache_hit:256}`
- [ ] 已 push 到 Gitea → ⏭️ **按用户要求未提交**

补充：`uv run ruff check .` → **All checks passed!**

## 三、产出物清单

### 新增（`~/lab/workpilot`，未提交）

| 文件 | 说明 |
| --- | --- |
| `prompts/structured_answer.v1.md` | 文档助手 v0 结构化回答 prompt（front matter + `{question}`/`{context}` 占位） |
| `prompts/task_breakdown.v1.md` | SP-B 需求拆解 prompt（`{requirement}`/`{stack}`，3–10 任务、0.5–16h、四类 type） |
| `apps/api/app/llm/prompts.py` | 版本化 prompt 加载器：front matter 解析、`{标识符}` 渲染（避开 `str.format` 花括号陷阱）、`lru_cache` |
| `apps/api/app/llm/structured.py` | `generate_structured()`：JSON mode + schema 注入 + Pydantic 校验 + 错误回灌重试 1 次 + `StructuredError` |
| `apps/api/app/routes/structured.py` | `/v1/structured/answer`、`/v1/structured/breakdown`；`_envelope` 统一契约；`StructuredError` → `AppError(502)` 不外泄模型原文 |
| `apps/api/tests/test_prompts.py` | 7 用例：加载 / ref / 缺变量抛 `KeyError` / 含 `{"a":1}` 渲染不报错 等 |
| `apps/api/tests/test_structured.py` | 8 用例：假 Gateway 验证「缺字段→重试→成功」与「两次失败→抛 `StructuredError`」 |
| `apps/api/tests/test_structured_live.py` | `@pytest.mark.llm`，5 输入通过率统计 |

### 修改

| 文件 | 变更 |
| --- | --- |
| `apps/api/app/llm/schemas.py` | 新增 `Usage`；`ChatResult.usage` 改嵌套对象；新增 `StructuredAnswer`/`TaskItem`/`TaskBreakdown` |
| `apps/api/app/llm/gateway.py` | `chat()` 返回嵌套 `Usage`（含 `cache_hit_tokens` 透传 `prompt_cache_hit_tokens`） |
| `apps/api/app/main.py` | `include_router(structured.router)` |
| `apps/api/app/core/config.py` | `Settings.prompts_dir` 指向仓库根 `prompts/` |
| `apps/api/pyproject.toml` | 加 `pyyaml`；dev 加 `pytest-asyncio`；marker `live` → `llm`；`addopts` 改 `-m 'not llm'`；加 `asyncio_mode="auto"` |
| `apps/api/tests/test_llm_gateway.py` | fake usage 补 `total_tokens`；断言改 `r.usage.prompt_tokens` |
| `docs/runbook.md` | 新增「技术债」：MinIO root 凭据复用，W7 需独立收敛 |

## 四、与 PLAN 的偏差与原因

1. **marker 二义性**：项目原有 `live` marker，PLAN Step 3 要求 `llm`。统一改为 `llm`（`pyproject` + `test_llm_gateway.py` 同名改造），避免两套并存。
2. **gateway 单例形态**：PLAN 示例用模块级单例 `gateway`，项目实际是 `app.state.gateway` + `Depends(get_gateway)`。按 PLAN §2 授权「按实际改，不要两套并存」，`generate_structured` 采用 `*, gw: LLMGateway` 显式传参（不走全局 monkeypatch），单测直接传 `FakeGW`。
3. **错误码**：PLAN 说 `HTTPException(502, ...)`，项目已有 `AppError(code, message, status)` + 统一 handler，改用 `AppError("structured_output_failed", "结构化输出校验失败", 502)`，与 Day07/08 一致，同样不外泄模型原文。
4. **ruff UP047**：`TypeVar("T", bound=BaseModel)` 被判应使用类型参数，改为 PEP 695 `async def generate_structured[T: BaseModel](...)`。

## 五、发现的 schema 设计问题

schema 比 prompt 松，约束只写在自然语言里，越界不会被拦，共 3 处：

1. `key_points` 只写 `max_length=8`，无下限；prompt 说「列 2–5 条」→ 模型返回 0 条也能通过。建议 v2 改 `Field(min_length=2, max_length=5)`。
2. `estimate_hours: Field(gt=0, le=40)` vs prompt「0.5–16」→ 实测 2–6 落在 prompt 内，但 schema 拦不住 30。建议两边对齐 `ge=0.5, le=16`。
3. `StructuredAnswer.answer` 的「≤ 300 字」只在 prompt，schema 无 `maxLength`（实测 179–259 字未超标）；`TaskItem.title` 无 `min_length=1`，空标题可过校验。

反向结论：`Literal[...]` → JSON Schema `enum` 是最有效的一条，5 个输入的 `confidence` 与 `type` 全部合规、0 次枚举违规。

## 六、5 输入明细（`uv run pytest -m llm -s`，14.36 s，0 次重试）

| 输入 | 结果 | calls | tokens | 关键字段 |
| --- | --- | --- | --- | --- |
| answer-通用 | OK | 1 | 332+216 | confidence=high need_ctx=False points=5 ans_len=179 |
| answer-团队内部 | OK | 1 | 326+205 | confidence=low need_ctx=True points=4 ans_len=259 |
| answer-模糊 | OK | 1 | 321+198 | confidence=low need_ctx=True points=4 ans_len=212 |
| breakdown-文档上传 | OK | 1 | 476+968 | tasks=9 types=backend/doc/frontend/test |
| breakdown-JWT | OK | 1 | 482+563 | tasks=6 types=backend/doc/test |

一次典型调用 tokens / 延迟：answer **570 tok / 2026 ms**；breakdown **1376 tok / 4701 ms**。

## 七、未提交改动清单（`~/lab/workpilot`）

修改：`apps/api/app/core/config.py`、`apps/api/app/llm/gateway.py`、`apps/api/app/llm/schemas.py`、`apps/api/app/main.py`、`apps/api/pyproject.toml`、`apps/api/tests/test_llm_gateway.py`、`apps/api/uv.lock`、`docs/runbook.md`。
新增：`prompts/structured_answer.v1.md`、`prompts/task_breakdown.v1.md`、`apps/api/app/llm/prompts.py`、`apps/api/app/llm/structured.py`、`apps/api/app/routes/structured.py`、`apps/api/tests/test_prompts.py`、`apps/api/tests/test_structured.py`、`apps/api/tests/test_structured_live.py`。

## 八、完成判定

第 3 节除「已 push」外全部勾上（push 按用户要求跳过）→ **Task 1 DONE**，明天进入 Day12（Streaming SSE + 成本记录 + CLI 聊天）。
