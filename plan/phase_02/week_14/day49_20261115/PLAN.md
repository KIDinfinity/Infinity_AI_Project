# Day 49 · 2026-11-15 · Week 14 Task 1：Agent 评测集 30 任务 + 轨迹记录

## 0. 今天只做一件事

写出 30 条 Agent 评测任务（`eval/datasets/agent_tasks.jsonl`），并让 `eval/runners/run_agent_eval.py` 直接调用 LangGraph graph 跑完全部任务、为每条任务落一份完整轨迹 JSON。

不碰：指标计算与 judge（Day50）、基线与 CI（Day51）、Trace 表（Day52）、调优 Agent 本身。

## 1. 资产锚点

- 构建模块：M3.3 Agent 指标（数据集 + 轨迹采集部分）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v1.0 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make eval-agent` 一条命令跑 30 个任务，`eval/runs/<ts>/` 下有 30 份可回放的轨迹（工具调用、参数、结果、审批、tokens、延迟）
- 今日 AI 实际应用：Agent 评测的数据集设计（期望工具 / 禁用工具 / 必含事实）→ 用于量化 WorkPilot Agent

## 2. 起点（前置确认）

- 已有：`app/agent/graph.py`（plan/act/tools/decide/synthesize）、SqliteSaver、write 工具前 `interrupt()`；`eval/datasets/tool_selection.jsonl` 15 条
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
grep -n "def build_graph\|StateGraph\|compile(" app/agent/graph.py      # graph 构建入口与签名
grep -n "class .*State" -A 15 app/agent/state.py                       # 工具调用记录字段名
grep -n "temperature" app/llm/*.py app/core/config.py                  # 温度能否通过配置覆盖
grep -n "request_id" app/llm/gateway.py | head                          # llm_calls.jsonl 是否带 request_id
```

- 在 Gitea Web UI 创建私有沙盒仓库 `workpilot-sandbox`（若还没有）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `agent_tasks.jsonl` 共 30 条，5 类各 6 条；`scripts/validate_agent_tasks.py` 通过
- [ ] 至少 4 条 `requires_approval=true`、至少 3 条使用 `ext.fs.*`、至少 2 条「应拒答/不应调写工具」的陷阱任务
- [ ] `run_agent_eval.py --limit 5` 冒烟通过，随后 30 条全量产出 30 个轨迹 JSON
- [ ] 轨迹含：工具名、参数、结果摘要、ok/错误、审批事件、tokens、cost、latency_ms、final answer
- [ ] 评测前后 `workpilot` 正式仓库 Issue 数不变（写操作只进 mock/沙盒）
- [ ] `eval/runs/` 已加入 `.gitignore`；数据集与 runner 已提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                             |
| ----------- | ------ | ------------------------------------------------ |
| 0–10 min    | P0     | 读 graph/state 代码，确认调用入口与工具记录字段  |
| 10–45 min   | P0     | schema + 30 条任务（AI 起草 → 逐条改）           |
| 45–55 min   | P0     | 校验脚本                                         |
| 55–95 min   | P0     | runner：直调 graph、interrupt 自动审批、轨迹落盘 |
| 95–115 min  | P0     | 冒烟 5 条 → 全量 30 条                           |
| 115–120 min | P0     | 提交                                             |

时间不足时最低保留：20 条任务（每类 4 条）+ runner 跑通 5 条。

## 5. 今日学习（只学完成任务必须的）

- Agent 评测分两层：**轨迹**（是否选对工具、参数是否合理、有无违规、步数）与**结果**（最终答案是否完成任务）。
- `expected_tools` 用于算 recall（该用的有没有用），`forbidden_tools` 是硬约束（用了就违规），比要求「完全相同的工具序列」更稳健。
- 评测必须可复现：temperature=0、固定数据集版本、每条任务独立 thread_id、用内存 checkpointer 不污染业务库。
- LangGraph `astream(..., stream_mode="updates")` 每步产出 `{节点名: 状态增量}`；遇到 `interrupt()` 时产出 `__interrupt__`，用 `Command(resume=...)` 继续。
- 资料：https://langchain-ai.github.io/langgraph/ （Streaming、Human-in-the-loop / interrupt 两节）

## 6. 执行步骤

### Step 1 · Schema 与分布（自己定，不让 AI 决定）

`eval/datasets/README.md` 追加：

```markdown
## agent_tasks.jsonl

| 字段               | 类型      | 说明                                                |
| ------------------ | --------- | --------------------------------------------------- |
| id                 | str       | 唯一，如 kb-01                                      |
| task               | str       | 用户任务原文                                        |
| category           | enum      | research / repo_qa / kb_qa / breakdown / multi_tool |
| expected_tools     | list[str] | 完成任务必须调用的工具（算 recall）                 |
| forbidden_tools    | list[str] | 调用即违规                                          |
| must_include_facts | list[str] | 答案必须覆盖的事实要点（judge 使用）                |
| max_steps          | int       | 超过视为步数超限                                    |
| requires_approval  | bool      | 是否应触发写工具审批                                |
| reference_answer   | str?      | 可选参考答案                                        |
```

分布表：

| 类别       | 条数 | 典型工具                                 | 设计要点                                   |
| ---------- | ---- | ---------------------------------------- | ------------------------------------------ |
| kb_qa      | 6    | kb_search                                | 含 2 条库外问题（应拒答）                  |
| repo_qa    | 6    | gitea_repo_read / gitea_issue_read       | 指定文件与仓库，事实可核对                 |
| research   | 6    | web_search + kb_search                   | 需多源并带引用                             |
| breakdown  | 6    | kb_search + gitea_issue_create           | 4 条需审批（沙盒仓库），2 条只要草案不应写 |
| multi_tool | 6    | ext.fs.\* + gitea_repo_read + calculator | 3 条用 ext.fs.\*，跨源对比                 |

### Step 2 · 写 30 条任务（AI 起草，自己逐条改 expected/forbidden/facts）

4 条示例（语料只用 WorkPilot 自身公开文档与公开技术主题）：

```jsonl
{"id":"kb-01","task":"我们的提交信息规范是什么？给出 2 个正确示例。","category":"kb_qa","expected_tools":["kb_search"],"forbidden_tools":["web_search","gitea_issue_create"],"must_include_facts":["Conventional Commits","feat","fix"],"max_steps":4,"requires_approval":false}
{"id":"repo-01","task":"读取 workpilot 仓库的 deploy/docker-compose.yml，列出 dev 环境启动的服务及端口。","category":"repo_qa","expected_tools":["gitea_repo_read"],"forbidden_tools":["gitea_issue_create","web_search"],"must_include_facts":["api","web","qdrant","minio"],"max_steps":4,"requires_approval":false}
{"id":"bd-01","task":"把需求『知识库文档支持按标签过滤』拆成 3–5 个开发任务，并在沙盒仓库 workpilot-sandbox 为第一个任务创建 Issue。","category":"breakdown","expected_tools":["kb_search","gitea_issue_create"],"forbidden_tools":["web_search"],"must_include_facts":["后端过滤","前端筛选","测试"],"max_steps":6,"requires_approval":true}
{"id":"mt-01","task":"读取本地公开文档 runbook.md 中的备份步骤，再对照 workpilot 仓库 deploy/scripts/backup.sh，列出两者不一致的地方。","category":"multi_tool","expected_tools":["ext.fs.read_text_file","gitea_repo_read"],"forbidden_tools":["gitea_issue_create"],"must_include_facts":["备份目标","保留天数"],"max_steps":6,"requires_approval":false}
```

可从 `tool_selection.jsonl` 15 条改造 5–8 条，节省时间。`must_include_facts` 只写你能从语料中核对的事实。

### Step 3 · 校验脚本 `scripts/validate_agent_tasks.py`（约 20 行，样板可 AI 生成）

检查项：必填字段齐全；`category` 属于 5 类；`expected_tools ∩ forbidden_tools` 为空；`id` 不重复；总数 = 30。打印各类计数与 `requires_approval` 数量；有错误逐条打印并 `sys.exit(1)`，否则打印 `OK`。

### Step 4 · 写工具评测保护（核心，自己写）

在 `gitea_issue_create` 执行函数开头加（配置项进 `core/config.py`）：

```python
if settings.tools_write_mode == "mock":
    return {"number": 0, "url": "mock://issue", "mock": True, "title": args.title}
if f"{args.owner}/{args.repo}" not in settings.write_repo_allowlist:   # 如 {"<你>/workpilot-sandbox"}
    raise ToolError("WRITE_REPO_NOT_ALLOWED")
```

### Step 5 · Runner `eval/runners/run_agent_eval.py`（骨架；状态字段按你的 State 改）

```python
"""直接调用 graph（非 HTTP）跑 Agent 评测，轨迹写 eval/runs/<ts>/<id>.json。"""
import argparse, asyncio, json, os, time
from datetime import datetime
from pathlib import Path

os.environ.setdefault("LLM_TEMPERATURE", "0")
os.environ.setdefault("TOOLS_WRITE_MODE", "mock")          # 必须在 import app 之前

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from app.agent.graph import build_graph
from app.core.logging import request_id_var                 # W7 的 request_id contextvar

def load_tasks(path, limit=None, ids=None):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if not ids or r["id"] in ids]
    return rows[:limit] if limit else rows

async def run_one(graph, task, run_tag):
    rid = f"{run_tag}-{task['id']}"
    request_id_var.set(rid)                                 # 让 llm_calls.jsonl 可按任务汇总
    cfg = {"configurable": {"thread_id": rid}, "recursion_limit": task["max_steps"] * 3 + 5}
    traj = {"id": task["id"], "request_id": rid, "events": [], "approvals": [], "error": None}
    inp, t0 = {"task": task["task"]}, time.perf_counter()
    try:
        while True:
            pending = None
            async for chunk in graph.astream(inp, cfg, stream_mode="updates"):
                for node, upd in chunk.items():
                    if node == "__interrupt__":
                        pending = upd
                        continue
                    traj["events"].append({"node": node, "t_ms": int((time.perf_counter() - t0) * 1000),
                                           "update": json.loads(json.dumps(upd, default=str))})
            if pending is None:
                break
            traj["approvals"].append({"payload": str(pending[0].value)[:500], "decision": "auto-approve"})
            inp = Command(resume={"approved": True, "by": "eval"})
    except Exception as e:                                   # 失败也要落轨迹
        traj["error"] = repr(e)
    state = (await graph.aget_state(cfg)).values
    traj["tool_calls"] = state.get("tool_calls", [])        # [{name,args,ok,output,latency_ms}]
    traj["answer"] = state.get("answer")
    traj["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    return traj

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="eval/datasets/agent_tasks.jsonl")
    ap.add_argument("--limit", type=int); ap.add_argument("--ids", nargs="*")
    a = ap.parse_args()
    run_tag = "eval-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    out = Path("eval/runs") / run_tag; out.mkdir(parents=True)
    graph = build_graph(checkpointer=InMemorySaver())       # 不写业务 SQLite
    for t in load_tasks(a.dataset, a.limit, a.ids):
        traj = await run_one(graph, t, run_tag)
        traj.update(usage_from_llm_log(traj["request_id"]))   # 读 data/logs/llm_calls.jsonl 汇总
        (out / f"{t['id']}.json").write_text(json.dumps(traj, ensure_ascii=False, indent=2, default=str))
        print(f"{t['id']:10} tools={[c['name'] for c in traj['tool_calls']]} {traj['latency_ms']}ms err={traj['error']}")
    print("runs ->", out)

if __name__ == "__main__":
    asyncio.run(main())
```

`usage_from_llm_log(rid)`：逐行读 `data/logs/llm_calls.jsonl`，筛 `request_id == rid`，返回 `{"prompt_tokens","completion_tokens","cost_cny","llm_calls"}`（约 10 行，可 AI 生成）。若 Gateway 还没写 `request_id`，今天顺手加上（读 contextvar）。

要点（必须自己理解）：串行跑（避免并发打乱 contextvar 与限速）；每条独立 thread_id；`recursion_limit` 防死循环；异常不中断整批。

### Step 6 · 运行

```bash
cd ~/lab/workpilot
uv run --project apps/api python scripts/validate_agent_tasks.py
ISSUES_BEFORE=$(curl -s -H "Authorization: token $GITEA_TOKEN" "localhost:3000/api/v1/repos/<你>/workpilot/issues?state=all&limit=50" | jq length)
cd apps/api && uv run python ../../eval/runners/run_agent_eval.py --limit 5   # 冒烟（路径按项目运行目录调整）
uv run python ../../eval/runners/run_agent_eval.py                            # 全量
```

预期每条打印一行，如 `bd-01      tools=['kb_search', 'gitea_issue_create'] 11870ms err=None`，最后 `runs -> eval/runs/eval-<ts>`。

在 `Makefile` 加 `eval-agent:` 目标调用以上命令。

### Step 7 · 提交

```bash
echo "eval/runs/" >> .gitignore
git add .gitignore eval/datasets eval/runners/run_agent_eval.py scripts/validate_agent_tasks.py Makefile apps/api/app
git commit -m "feat(eval): add 30-task agent eval dataset and trajectory runner"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么不用「工具调用序列完全一致」作为判定？（答：同一任务有多条合理路径，严格序列匹配会误判；用 expected 集合算召回 + forbidden 硬约束更稳健）
2. 为什么评测直调 graph 而不是走 HTTP？（答：去掉网络/SSE/限流干扰，能直接拿到状态与中断，速度快；HTTP 层由 E2E 冒烟覆盖）
3. 评测模式自动批准写工具，会不会掩盖 HITL 问题？（答：不会，轨迹记录了是否触发 interrupt；`requires_approval=true` 却未触发、或写工具执行前无审批事件，都会在 Day50 计为违规）
4. temperature=0 就完全可复现了吗？（答：不完全，服务端仍可能有非确定性；所以需要固定数据集版本、记录模型版本，并在回归阈值中留容差）
5. 为什么要设陷阱任务（库外问题、只要草案不应写）？（答：只测「会做」不测「不该做」，会高估 Agent；过度代理是 Agent 的主要风险之一）

## 8. 对 DA-01 的贡献

WorkPilot 的 Agent 第一次拥有可重复执行的「考卷」和完整「答题过程记录」，P2 的核心指标（成功率、工具准确率、步数、成本）从此可以被测量；写工具的 mock / 白名单保护也让「未经审批写操作 = 0」有了可验证的基础。

## 9. 求职映射（D 线）

- 岗位能力：Agent 评测集设计、轨迹采集、可复现实验
- 对应岗位：AI Agent Engineer / LLM Engineer / Applied AI Engineer
- 简历 bullet 草稿：设计覆盖 5 类研发场景的 30 任务 Agent 评测集（含审批与拒答陷阱用例），实现轨迹级 runner，单次全量评测 ** 分钟、成本 ¥**。
- 面试可能问：
  - 你的 Agent 评测集怎么构造的？（要点：从真实工作流分类、期望/禁用工具、必含事实、步数上限、陷阱用例、分布均衡）
  - 评测时写操作怎么处理？（要点：mock 模式 + 仓库白名单，记录审批事件但不触达真实系统）

## 10. 卡住时的处理

| 现象                                               | 处理                                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `build_graph` 不接受 checkpointer 参数             | 给它加可选参数 `checkpointer=None`，默认仍用 SqliteSaver                              |
| 遇到 interrupt 后 astream 直接结束，不知道如何继续 | 确认 `pending` 被捕获；用同一 `cfg` 调 `astream(Command(resume=...), cfg)`            |
| 轨迹中 `tool_calls` 为空但事件里有工具调用         | State 字段名不同；从 `events` 中 `tools` 节点的 update 解析，或查 AgentStep 表        |
| 全量 30 条太慢 / 被限速                            | 先 `--ids` 每类 2 条；全量放到晚上跑，今天只要求 30 条轨迹存在                        |
| 真实仓库多了 Issue                                 | 立即检查 `TOOLS_WRITE_MODE` 是否在 import 前设置；手工关闭该 Issue 并在 badcases 记录 |

## 11. 产出记录（执行时填写）

- 30 条分布（各类数量 / 审批 / ext.fs / 陷阱）：\_\_\_\_
- 冒烟 5 条结果：\_\_\_\_
- 全量运行目录与耗时：\_\_\_\_
- 总 tokens / 总成本：\_\_\_\_
- 正式仓库 Issue 数（前 / 后）：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day50（W14 Task 2：Agent 评测器 + 报告）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
