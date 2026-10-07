# Day 42 · 2026-12-09 · Week 11 Task 3：v0 vs v1 对比 + ADR + JD 追踪

## 0. 今天只做一件事

用 10 个任务给手写 v0 与 LangGraph v1 做一次量化对比，把「为什么用 LangGraph」写成 ADR-0006，并把 `/v1/agent/run` 默认切到 v1（v0 保留开关）。

不碰：新功能（记忆 / 审批在 W12）、Agent 正式评测框架（W14）、提示词大改（对比要控制变量）。

## 1. 资产锚点

- 构建模块：M7 Agent Runtime（v0/v1 收口）、M13.1 JD 追踪（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.8 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`eval/reports/20261209-agent-v0-vs-v1.md`（10 任务 × 2 版本 × 6 维度）；`docs/adr/0006-why-langgraph.md`；Web Agent 页默认运行 v1，`AGENT_VERSION=v0` 一键回退。
- 今日 AI 实际应用：LLM-as-a-judge + 人工抽查的 Agent 结果评估 → 用在 `eval/runners/compare_agents.py`（W14 正式 Agent 评测的雏形）。

## 2. 起点（前置确认）

- 已有：v0 `loop_v0.run_events`、v1 `runner.run_v1_events`、`eval/datasets/agent_smoke.jsonl`（10 任务）、Day39 v0 冒烟报告、phase_01 `eval/judge.py`。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api && uv run pytest -q
wc -l ../../eval/datasets/agent_smoke.jsonl                 # 10
grep -n "def judge\|def score" ../../eval/judge.py          # judge 的入口函数与返回格式
ls ../../docs/adr/                                          # 确认下一个编号是 0006
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `compare_agents.py` 对 10 任务分别跑 v0、v1，记录：成功（judge + 人工）、步数、延迟、tokens、成本、stop_reason、失败类型
- [ ] 报告含汇总表、逐任务表、失败类型分布、已知差异说明、结论（≤5 条）
- [ ] `docs/adr/0006-why-langgraph.md`：背景 / 决策 / 备选方案 / 后果（收益与代价）/ 回退方案
- [ ] `AGENT_VERSION: Literal["v0","v1"] = "v1"`，路由按配置分发；前端在 v1、v0 下各跑通 1 次
- [ ] `career/job-market.md` 第 2 轮追踪 + `capability-matrix.md` 更新
- [ ] 周复盘已填；已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                               |
| ----------- | ------ | -------------------------------------------------- |
| 0–20 min    | P0     | `compare_agents.py`，启动后台运行（约 20–30 分钟） |
| 20–50 min   | P0     | 等待期间写 ADR-0006                                |
| 50–70 min   | P0     | 结果出来后人工抽查 4 个任务，填报告结论            |
| 70–85 min   | P0     | `AGENT_VERSION` 开关 + 路由切换 + 前端冒烟         |
| 85–105 min  | P1     | JD 第 2 轮 + 能力矩阵（严格 20 分钟）              |
| 105–120 min | P0     | 周复盘 + 提交                                      |

时间不足时最低保留：5 任务对比 + ADR 三段（决策 / 理由 / 代价）+ 路由切换。

## 5. 今日学习（只学完成任务必须的）

- **控制变量**：两版共用 steps.py、提示词、工具和模型，差异只来自运行时；否则对比没有意义。
- **成功的定义**：stop_reason 正常（finish / plan_completed）且 judge 判定「报告回答了任务且引用可追溯」；judge 结果需人工抽查校准。
- **ADR**：一页纸记录「当时的上下文、做了什么决定、放弃了什么、代价是什么」，未来推翻决策时有据可查。
- **特性开关**：新旧实现并存一段时间，出问题可回退，是安全迁移的标准做法。
- 资料：
  - https://adr.github.io/
  - https://langchain-ai.github.io/langgraph/ （Why LangGraph / Persistence / Human-in-the-loop 概念页）

## 6. 执行步骤

### Step 1 · compare_agents.py

`eval/runners/compare_agents.py`（样板让 AI 生成，指标定义与成功判定自己写）：

```python
import asyncio, json, pathlib, time, uuid
from app.agent import loop_v0, runner
from eval.judge import judge_report            # 以 phase_01 实际函数为准：输入任务 + 报告，输出 {pass: bool, reason: str}

DATA = pathlib.Path("eval/datasets/agent_smoke.jsonl")
OUT = pathlib.Path("eval/reports/agent-v0-vs-v1")

async def run_one(version: str, task: str) -> dict:
    gen = loop_v0.run_events if version == "v0" else runner.run_v1_events
    t0, tools, report_md, done, err = time.perf_counter(), [], "", {}, None
    try:
        async for e in gen(task, run_id=uuid.uuid4().hex):
            if e.type == "tool_call": tools.append(e.data["tool"])
            if e.type == "report":    report_md = e.data["markdown"]
            if e.type == "done":      done = e.data
    except Exception as ex:
        err = type(ex).__name__
    return {"version": version, "latency_s": round(time.perf_counter() - t0, 1), "tools": tools,
            "steps": done.get("steps"), "tokens": done.get("tokens"), "cost_cny": done.get("cost_cny"),
            "stop_reason": done.get("stop_reason"), "error": err, "report_md": report_md}

def classify(r: dict, judged: dict) -> str:
    if r["error"]: return f"exception:{r['error']}"
    if r["stop_reason"] in ("max_steps", "token_budget", "repeated_calls"): return r["stop_reason"]
    if not judged["pass"]: return "low_quality"
    return "ok"

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for line in DATA.read_text().splitlines():
        case = json.loads(line)
        for v in ("v0", "v1"):
            r = await run_one(v, case["task"])
            j = await judge_report(case["task"], r["report_md"]) if r["report_md"] else {"pass": False, "reason": "no report"}
            r |= {"id": case["id"], "judge": j, "failure": classify(r, j)}
            (OUT / f"{case['id']}-{v}.md").write_text(r["report_md"] or "(no report)")
            rows.append(r)
            print(case["id"], v, r["failure"], r["steps"], r["tokens"])
    (OUT / "raw.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))

asyncio.run(main())
```

```bash
cd ~/lab/workpilot && PYTHONPATH=apps/api uv run --project apps/api python eval/runners/compare_agents.py | tee /tmp/compare.log
```

预计 20 次运行、总成本约 ¥0.2–0.5；跑的同时去写 ADR。

### Step 2 · 报告

`eval/reports/20261209-agent-v0-vs-v1.md`（用 raw.json 让 AI 生成表格，结论自己写）：

```markdown
# Agent v0（手写）vs v1（LangGraph）· 2026-12-09

- 数据集：eval/datasets/agent_smoke.jsonl（10 任务）；模型 deepseek-chat；提示词 planner.v1 / decider.v1.1 / synthesizer.v1

## 汇总

| 指标                           | v0                          | v1    |
| ------------------------------ | --------------------------- | ----- |
| 成功率（judge 通过且正常停止） | \_/10                       | \_/10 |
| 平均步数                       | \_                          | \_    |
| 平均延迟 / P95 延迟（s）       | _ / _                       | _ / _ |
| 平均 tokens                    | \_                          | \_    |
| 平均成本（¥）                  | \_                          | \_    |
| 失败类型分布                   | max*steps×* low*quality×* … | …     |

## 逐任务

| id | v0 结果 / 步数 / tokens | v1 结果 / 步数 / tokens | 工具序列是否一致 | 备注 |

## 已知差异

- v1 在达到上限时不再调用 decider（少 1 次 LLM 调用）
- v1 具备 checkpoint、节点重试与 provider fallback；v0 没有

## 人工抽查（4 个任务）：judge 与人工结论是否一致？不一致的原因

## 结论（≤5 条）
```

预期：两者成功率与步数接近（同一套 steps.py），v1 的价值主要在可靠性与可扩展性而非单次质量——如果数据显示如此，就如实写，这正是 ADR 的论据。

### Step 3 · ADR-0006

`docs/adr/0006-why-langgraph.md`：

```markdown
# ADR-0006：Agent 运行时采用 LangGraph（保留手写 v0 作为对照）

- 状态：已接受 · 日期：2026-12-09 · 关联：M7.2、M7.3、M7.4

## 背景

W10 手写 v0 能完成调研任务，但：状态只在内存；无法中断等待人工审批；无法断点续跑；流程只存在于 if/else 中，难以向他人解释。W12 需要会话记忆与写操作审批。

## 决策

采用 LangGraph StateGraph；节点内部继续调用自研 M1 Gateway（不引入 LangChain 模型类）；checkpointer 使用 langgraph-checkpoint-sqlite；HITL 使用 interrupt() + Command(resume)。

## 备选方案

1. 继续手写：自己实现持久化、中断、可视化 —— 工作量大且易错。
2. LangChain AgentExecutor / 预置 ReAct agent：黑盒循环，难以插入审批与自定义停止条件。
3. 其他 Agent 框架（多 Agent 协作类）：超出范围（DA01 明确不做 Multi-Agent）。

## 后果

- 收益：显式状态与 reducer；checkpoint / 恢复；interrupt 原生支持审批；draw_mermaid 可视化；JD 高频。
- 代价：新增依赖与版本变动风险（API 参数名变化）；state 需可序列化（全部存 dict）；调试多了一层抽象；recursion_limit 等框架概念。
- 数据：见 eval/reports/20261209-agent-v0-vs-v1.md（成功率 _ vs _，平均成本 ¥* vs ¥*）。

## 回退方案

AGENT_VERSION=v0 立即回退；steps.py 为两版共享，框架可替换。
```

### Step 4 · 版本开关 + 路由切换

`config.py`：`AGENT_VERSION: Literal["v0", "v1"] = "v1"`。

`routes/agent.py` 的 `gen()` 中：

```python
events = (runner.run_v1_events(body.task, run_id=run_id, graph=request.app.state.agent_graph)
          if settings.AGENT_VERSION == "v1" else loop_v0.run_events(body.task, run_id=run_id))
async for e in events:
    ...
```

创建 `AgentRun` 时写入 `agent_version=settings.AGENT_VERSION`。前端 Agent 页跑一次；`.env` 改 `AGENT_VERSION=v0` 重启再跑一次，确认两者时间线都正常。

### Step 5 · JD 追踪第 2 轮 + 能力矩阵（D 线，20 分钟）

- `job-market.md` 追加「第 2 轮追踪 · 2026-12-09（W11）」：再收集 10 个 JD（与第 1 轮不重复），沿用同一表格；重点记录 LangGraph / MCP / Agent 评测 / 可观测 四个关键词的出现次数变化。
- `capability-matrix.md`：更新 Tool Calling、Agent Workflow、LangGraph 三行的自评分与证据链接（指向 WorkPilot 文件 / tag），更新日期。

### Step 6 · 提交 + 周复盘

```bash
cd ~/lab/workpilot
git add eval/runners/compare_agents.py eval/reports docs/adr/0006-why-langgraph.md apps/api
git commit -m "docs(agent): v0 vs v1 comparison, ADR-0006 and switch default runtime to LangGraph"
git push
cd ~/lab/projects && git add career && git commit -m "docs(career): JD tracking round 2 and capability matrix update" && git push
```

填写 `plan/phase_02/week_11/README.md` §11 周复盘。

## 7. 概念自检（不看资料，口述，附答案）

1. 你的 v0/v1 对比控制了哪些变量？（答：同一数据集、模型、提示词、工具与 steps.py 业务函数，差异只在运行时实现。）
2. 如果 v1 的成功率并不比 v0 高，迁移还值得吗？（答：值得；迁移目标是可靠性与可扩展性（checkpoint / interrupt / 可视化），不是单次质量；ADR 中如实记录。）
3. LLM-as-a-judge 的结果为什么要人工抽查？（答：judge 本身有偏差（偏好长答案、漏看引用错误），抽查用于校准，并记录 judge 与人工不一致的模式。）
4. ADR 中「后果」为什么必须写代价？（答：只写收益的决策记录无法帮助未来判断是否推翻；代价是重新评估的触发条件。）
5. 为什么保留 v0 开关而不是直接删除？（答：安全回退；作为对照组用于后续回归；面试演示「框架替我做了什么」。）

## 8. 对 DA-01 的贡献

WorkPilot 的 Agent 运行时正式切换到 LangGraph，并有一份数据支撑的决策记录；这让 P2 作品集可以回答「为什么这么设计」，也为 W14 正式 Agent 评测（30 任务）提供了 runner 雏形与失败分类法。

## 9. 求职映射（D 线）

- 岗位能力：技术选型方法论、评测驱动决策、LLM-as-a-judge、ADR、特性开关迁移。
- 对应岗位：AI Agent Engineer、AI Engineer（中高级）。
- 简历 bullet 草稿：以 10 任务对比评测（成功率 / 步数 / 延迟 / tokens / 成本 / 失败类型）驱动 Agent 运行时从手写循环迁移至 LangGraph，形成 ADR 并通过特性开关实现可回退上线。
- 面试可能问：
  - Q：你为什么选 LangGraph？要点：先手写理解原理 → 列出痛点（持久化 / 中断 / 可视化）→ 对比数据 → ADR 记录代价 → 可回退。
  - Q：怎么评估一个 Agent 好不好？要点：任务成功率、工具选择准确率、步数、延迟、成本、失败类型；judge + 人工抽查；固定数据集回归（W14）。

## 10. 卡住时的处理

| 现象                                              | 处理                                                                                   |
| ------------------------------------------------- | -------------------------------------------------------------------------------------- |
| compare 脚本跑太久                                | 先跑 5 个任务出报告；剩余任务后台继续，结果出来补表                                    |
| judge 打分全部通过 / 全部不通过                   | judge 提示词里加入「报告是否回答任务」「引用是否存在」两个明确判据；人工抽查校准后记录 |
| v1 在 FastAPI 里报 `app.state.agent_graph` 不存在 | lifespan 未生效；确认 `FastAPI(lifespan=lifespan)` 且 Day41 改动已合并                 |
| v0/v1 结果差异很大                                | 先查两边提示词版本与 Gateway 配置是否一致；再看已知差异（强制停止时机）是否影响        |
| JD 追踪超时                                       | 只收 5 个，频次表照填；不为追踪去学新技术                                              |
| ADR 不知道写多长                                  | 一页以内；数据引用报告，不复制表格                                                     |

## 11. 产出记录（执行时填写）

- 成功率 v0 / v1：\_**\_ / \_\_**；平均成本 v0 / v1：¥\_**\_ / ¥\_\_**
- judge 与人工不一致的任务：\_\_\_\_
- 本轮 JD 关键词变化最大的：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 11 完成，填写周复盘 → 明天进入 Day43「W12 Task 1：会话记忆 + 上下文压缩」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
