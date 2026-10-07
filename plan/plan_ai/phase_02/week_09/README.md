# Week 09 · Tool Calling + 工具层（Phase 2 · Day34–Day36 · 11-23 → 11-25）

## 1. 本周核心目标

让 WorkPilot 从「只会回答」变成「会调用工具」：建立统一的 Tool Registry（Pydantic 入参 → JSON Schema、权限等级、超时、截断、错误归一化），接入 5 个只读内置工具（`calculator`、`kb_search`、`web_search`、`gitea_repo_read`、`gitea_issue_read`），用一个多工具循环 Demo + 15 条工具选择用例证明「模型能选对工具」，打 tag `v0.6.0`。

## 2. 资产锚点

| 构建模块                 | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                                                         |
| ------------------------ | ---------- | --------------------------------------------------------------------------------------------------------------------- |
| M6.1 Tool Registry       | v0.6       | `uv run python scripts/tool_demo.py "..."` 一条命令，模型自动选工具、并行执行、循环 ≤5 步后给出答案，每步有日志       |
| M6.2 内置工具            | v0.6       | 同一个问题按内容自动走 `kb_search` / `web_search` / `gitea_repo_read` / `calculator`                                  |
| M6.3 执行保护            | v0.6       | 非法参数 / 超时 / 未知工具都返回 `ToolResult(ok=False)` 而非抛异常；外部内容统一包裹 `<tool_output untrusted="true">` |
| M3.3（前置）工具选择评测 | v0.6       | `eval/datasets/tool_selection.jsonl` 15 条 + 准确率报告                                                               |
| M13.1 JD 追踪            | —          | `career/job-market.md` 第 1 轮追踪（10 个新 JD）                                                                      |

## 3. 为什么这一周存在

- Agent = LLM + 工具 + 循环。没有一个可靠的工具层，W10 的手写 Agent 和 W11 的 LangGraph 都无从谈起。
- 工具层是安全的第一道闸门：权限等级（read / write / dangerous）决定了 W12 的人工审批、W15 的护栏能不能落地。
- JD 中 Function Calling / Tool Use 出现频率极高，本周产出可直接写进简历。

## 4. 本周在路线中的位置

```text
上周产出（W8）：WorkPilot v0.5 已部署；M1 Gateway（chat/stream/structured/pricing）；M2 RAG（retrieve.search）；50 题评测基线；GitHub 公开仓库
        ↓
本周（W9）：Gateway 支持 tools 参数 → Tool Registry → 5 个只读工具 → tool_loop 多工具循环 → 15 条工具选择评测 → v0.6.0
        ↓
下周输入（W10）：registry.to_openai_tools() / registry.execute() / ToolResult.sources（来源映射）/ tool_loop 的消息序列经验 → 手写 plan→act→observe 循环
```

## 5. 每日安排

| Day   | 日期  | Task                                             | 当日 P0 产出                                                                     | 模块      | 状态 |
| ----- | ----- | ------------------------------------------------ | -------------------------------------------------------------------------------- | --------- | ---- |
| Day34 | 11-23 | Task 1：Tool Calling 原理 + Registry             | 裸实验脚本 + `app/tools/registry.py` + `calculator` + 单测                       | M6.1      | TODO |
| Day35 | 11-24 | Task 2：内置工具                                 | `kb_search` `web_search` `gitea_repo_read` `gitea_issue_read` + respx 单测       | M6.2 M6.3 | TODO |
| Day36 | 11-25 | Task 3：多工具循环 Demo + 工具选择测试 + JD 追踪 | `app/agent/tool_loop.py` + `scripts/tool_demo.py` + 15 条用例报告 + tag `v0.6.0` | M6 M13.1  | TODO |

## 6. 本周必须留下的资产

```text
~/lab/projects/ai-lab/tool-calling/
├── raw_tool_call.py                 # 裸 OpenAI SDK 调 DeepSeek tools 实验
└── NOTES.md                         # 消息序列图 + 观察
~/lab/workpilot/
├── apps/api/app/llm/gateway.py      # 新增 chat_with_tools()
├── apps/api/app/tools/
│   ├── __init__.py
│   ├── registry.py                  # Tool / ToolOutput / ToolResult / register / to_openai_tools / execute
│   ├── common.py                    # clip() / wrap_untrusted() / SourceRef
│   └── builtin/
│       ├── __init__.py
│       ├── calculator.py
│       ├── kb_search.py
│       ├── web_search.py
│       ├── gitea.py                 # gitea_repo_read / gitea_issue_read
│       └── http_fetch.py            # P2：SSRF 防护
├── apps/api/app/agent/tool_loop.py
├── apps/api/tests/tools/            # test_registry.py test_calculator.py test_builtin_tools.py
├── scripts/tool_demo.py
├── eval/datasets/tool_selection.jsonl
├── eval/runners/run_tool_selection.py
├── eval/reports/20261125-tool-selection.md
└── docs/product/open-core.md        # P2 草稿
~/lab/projects/career/job-market.md  # 第 1 轮 JD 追踪
```

## 7. 本周验收标准

- [ ] PASS / FAIL：裸实验能打印 `tool_calls` 并完成「assistant(tool_calls) → tool(tool_call_id) → assistant(最终答案)」三段消息
- [ ] PASS / FAIL：`to_openai_tools()` 输出符合 OpenAI tools 格式，`parameters` 来自 `model_json_schema()`
- [ ] PASS / FAIL：非法参数、超时、未知工具三种情况均返回 `ok=False`，单测覆盖
- [ ] PASS / FAIL：4 个业务工具 respx/monkeypatch 单测全部通过；`-m live` 冒烟至少 3 个通过
- [ ] PASS / FAIL：所有外部内容包裹 `<tool_output source="..." untrusted="true">`
- [ ] PASS / FAIL：`tool_demo.py` 至少 1 个问题触发 ≥2 个工具并给出最终答案
- [ ] PASS / FAIL：15 条工具选择用例有准确率数字（目标 ≥ 0.80）
- [ ] PASS / FAIL：tag `v0.6.0` 已推送 Gitea + GitHub
- [ ] PASS / FAIL：`job-market.md` 第 1 轮追踪 10 个 JD

## 8. 求职映射

- 本周能力：Function Calling / Tool Use、JSON Schema 驱动的工具定义、工具执行安全（超时 / 截断 / SSRF / 不可信内容隔离）、工具选择评测。
- 简历 bullet 草稿：
  - 设计并实现 Agent 工具层（Tool Registry）：Pydantic v2 自动生成 JSON Schema、read/write/dangerous 三级权限、统一超时与结果截断，接入知识库 / Web 搜索 / Gitea 等 ** 个工具，单测覆盖率 **%。
  - 建立工具选择评测集（15 条，含禁止工具约束），工具选择准确率 \_\_%，为 Agent 迭代提供回归基线。
- 面试题：
  1. Function Calling 的完整消息流是怎样的？`tool_call_id` 有什么作用？
  2. 工具返回的网页内容里含有「忽略以上指令」怎么办？（间接注入：不可信标记、只读权限、写操作审批）
  3. 工具调用失败时为什么不应该直接抛异常给 Agent 循环？

## 9. 本周禁止事项

- 不引入 LangChain / LangGraph（W11 才引入），不写 Agent 规划逻辑（W10）。
- 不做任何写工具（`gitea_issue_create` 在 W12 与审批一起做）。
- 不为工具层引入插件系统、动态加载、数据库存储工具定义等过度设计。
- 不把公司仓库 / 公司 Gitea 接入；只读 token 只对自己 Gitea 的个人仓库授权。

## 10. 时间不够时（最小保留）

- Day34：registry + calculator + 3 个单测（裸实验可压缩到 10 分钟）。
- Day35：`kb_search` + `gitea_repo_read` 两个工具 + 单测；`web_search` 可推迟到 Day36 开头；`http_fetch` 直接进 Backlog。
- Day36：`tool_loop.py` + 4 条工具选择用例 + tag；JD 追踪压缩为 5 个 JD；`open-core.md` 推迟到 W16。

## 11. 周复盘（Day36 结束时填写）

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（录一段 30 秒终端 GIF / 截图）
- 工具选择准确率：\_**\_ / 15；主要错选类型：\_\_**
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
