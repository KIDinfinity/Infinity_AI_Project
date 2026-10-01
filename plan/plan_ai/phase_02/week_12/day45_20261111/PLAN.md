# Day 45 · 2026-11-11 · Week 12 Task 3：HITL 审批 + SP-B 试点 + 简历更新（v0.8）

## 0. 今天只做一件事

给 Agent 加第一个写工具 `gitea_issue_create`，并保证它**只有在人批准后才会执行**：图在写工具前 `interrupt()` 暂停，`POST /v1/agent/runs/{id}/approve` 用 `Command(resume=...)` 继续；用测试证明未批准时 Gitea 写接口调用次数为 0，再用 SP-B 迷你流程（需求 → 任务拆解 → 审批 → 建 Issue）跑通主场景。打 tag `v0.8.0`。

不碰：除 `gitea_issue_create` 外的任何写工具、自动审批规则、MCP（W13）、公司 Gitea / Jira。

## 1. 资产锚点

- 构建模块：M7.4 Human-in-the-loop（interrupt）、M6.2 `gitea_issue_create`(write)、M10 SP-B 试点、M13.3（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.8**（LangGraph Agent + Memory + HITL）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：Agent 页中任务「把这份调研的待确认问题建成 Issue」→ 时间线出现审批卡片（工具名 + 可编辑参数）→ 批准后 sandbox-issues 出现 Issue，拒绝则不出现；`tests/agent/test_hitl.py` 证明中断时 / 拒绝后写接口调用 0 次、批准后 1 次；`scripts/sp_b_pilot.py` 把一段需求拆成任务并在审批后批量建 Issue。
- 今日 AI 实际应用：LangGraph `interrupt()` + `Command(resume=...)` 的人工审批模式、OWASP LLM「过度代理（Excessive Agency）」防护 → 用在 `app/agent/hitl.py`、`registry.execute(approved=...)` 与 SP-B 场景图。

> 若 W3 Day13 选定的主场景不是 SP-B：Step 6 换成主场景的写操作（如 SP-E：周报草稿 → 审批 → 以 Issue 评论形式发布），HITL 机制与测试不变，写工具仍只作用于沙盒仓库。

## 2. 起点（前置确认）

- 已有：Day43–44 的会话 / 长期记忆；W11 AsyncSqliteSaver；W9 Gitea 只读工具；W3 Day11 的 `TaskBreakdown` schema。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api && uv run pytest -q
uv run python -c "from langgraph.types import interrupt, Command; print('ok')"
grep -rn "class TaskBreakdown" app/ | head -1             # 记下路径与字段名
```

- Gitea 准备（Web UI，10 分钟；Gitea token 的 scope 按「类别」授权而不能按仓库限定，所以用**独立 bot 账号 + 只加入沙盒仓库**实现「只对 sandbox-issues 有写权限」）：
  1. 用自己账号新建私有仓库 `sandbox-issues`。
  2. 站点管理 → 用户账户 → 创建 `workpilot-bot`。
  3. `sandbox-issues` → 设置 → 协作者 → 添加 `workpilot-bot`（写权限）。
  4. 以 bot 登录 → 设置 → 应用 → 生成令牌 `workpilot-write`，scope：`issue: Read and Write`、`repository: Read` → `.env` 的 `GITEA_WRITE_TOKEN`。
  5. `.env`：`GITEA_SANDBOX_REPO=<你的用户名>/sandbox-issues`；`.env.example` 同步加键（无值）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `registry.execute(name, args, *, approved=False)`：非 read 工具未审批直接返回 `approval_required`（单测）
- [ ] `gitea_issue_create`：permission=write，仓库固定为 `GITEA_SANDBOX_REPO`（不接受模型传入 repo），使用 `GITEA_WRITE_TOKEN`
- [ ] `hitl.approve_node` 在写工具前 `interrupt()`；路由 act →（write）approve →（批准）tools /（拒绝）decide
- [ ] SSE 新事件 `approval_required`；AgentRun 置 `waiting_approval` + `pending_action`
- [ ] `POST /v1/agent/runs/{id}/approve {decision, edited_args}`：状态校验（非 waiting_approval 返回 409）、审计记录、`Command(resume=...)` 续跑并继续推 SSE
- [ ] `test_hitl.py`：中断时 0 次、拒绝后 0 次、批准后 1 次、修改参数后请求体为修改值
- [ ] 前端 `ApprovalCard`（P1）；SP-B 迷你流程建 ≥2 个 Issue（P1）；简历更新（P1）
- [ ] tag `v0.8.0` 推送；周复盘

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                             |
| ----------- | ------ | ------------------------------------------------ |
| 0–10 min    | P0     | Gitea bot / 沙盒仓库 / 写 token                  |
| 10–25 min   | P0     | `execute(approved)` 门禁 + `gitea_issue_create`  |
| 25–45 min   | P0     | `hitl.py` + 图路由 + runner 处理 `__interrupt__` |
| 45–60 min   | P0     | approve API + `docs/api.md`                      |
| 60–80 min   | P0     | `test_hitl.py`（今天最重要的产出）               |
| 80–85 min   | P0     | tag `v0.8.0` + push                              |
| 85–100 min  | P1     | `ApprovalCard` + hook `decide()`                 |
| 100–112 min | P1     | SP-B 迷你流程 + CLI                              |
| 112–120 min | P1     | 简历更新 + 周复盘                                |

时间不足时最低保留：门禁 + 写工具 + approve 节点 + API + 断言测试 + tag；审批卡片与 SP-B 顺延到 Day46 前 30 分钟（在 draft.md 记录）。

## 5. 今日学习（只学完成任务必须的）

- **interrupt()**：节点内调用即暂停整张图并保存 checkpoint，`interrupt(payload)` 的 payload 交给调用方；必须配置 checkpointer。
- **Command(resume=value)**：以同一 `thread_id` 调用图，`interrupt()` 返回 `value`，节点**从头重新执行**——所以 `interrupt()` 之前不能有副作用。
- **两道闸**：图结构（approve 节点）保证流程，`execute(approved=...)` 保证即使图写错也不能绕过审批——纵深防御。
- **最小权限**：写 token 属于只能访问沙盒仓库的 bot；工具不接收 repo 参数；模型永远无法把 Issue 建到别处。
- 资料：
  - https://langchain-ai.github.io/langgraph/ （Human-in-the-loop：interrupt / Command）
  - https://docs.gitea.com/development/api-usage （`POST /repos/{owner}/{repo}/issues`）
  - https://genai.owasp.org/llm-top-10/ （Excessive Agency）

## 6. 执行步骤

### Step 1 · 执行门禁 + 写工具

`registry.py` 的 `execute` 增加关键字参数，未知工具检查之后立即判断：

```python
async def execute(name: str, raw_args: str | None, *, approved: bool = False) -> ToolResult:
    ...
    if tool.permission != "read" and not approved:
        return done(ok=False, error="approval_required")
```

`builtin/gitea.py` 追加：

```python
class IssueCreateArgs(BaseModel):
    title: str = Field(..., min_length=4, max_length=120)
    body: str = Field("", max_length=4000, description="Markdown 正文：背景、任务、验收标准")

@register(name="gitea_issue_create", args_model=IssueCreateArgs, permission="write", timeout_s=15,
          description="在团队沙盒仓库创建一个 Issue（写操作，执行前需要人工审批）。只在用户明确要求创建任务/Issue 时使用。")
async def gitea_issue_create(args: IssueCreateArgs) -> ToolOutput:
    owner, repo = settings.GITEA_SANDBOX_REPO.split("/")
    token = settings.GITEA_WRITE_TOKEN.get_secret_value()
    async with httpx.AsyncClient(base_url=settings.GITEA_BASE_URL, timeout=10,
                                 headers={"Authorization": f"token {token}"}) as c:
        r = await c.post(f"/api/v1/repos/{owner}/{repo}/issues", json={"title": args.title, "body": args.body})
        r.raise_for_status()
        data = r.json()
    return ToolOutput(text=f"已创建 #{data['number']} {data['html_url']}",
                      sources=[SourceRef(kind="gitea", ref=data["html_url"], title=args.title)])
```

`steps.choose_action` 与 `tool_catalog()` 改为 `to_openai_tools(allow=("read", "write"))`，catalog 中写工具名后标注「（需人工审批）」。

### Step 2 · approve 节点 + 路由

`app/agent/hitl.py`：

```python
import json
from langgraph.types import interrupt
from app.agent.schemas import Observation
from app.tools.registry import get_tool

def route_after_act(st) -> str:
    t = get_tool((st.get("pending_call") or {}).get("tool") or "")
    return "approve" if t and t.permission != "read" else "tools"

def route_after_approve(st) -> str:
    return "tools" if st.get("pending_call") else "decide"

async def approve_node(st) -> dict:
    pc = st["pending_call"]
    # interrupt 之前不做任何副作用：恢复时本节点会从头重跑
    resp = interrupt({"kind": "tool_approval", "tool": pc["tool"], "step_id": pc["step_id"],
                      "goal": pc["goal"], "args": json.loads(pc["args_json"] or "{}")})
    decision = (resp or {}).get("decision")
    if decision not in ("approve", "edit"):                      # 未知值一律按拒绝处理（fail-safe）
        obs = Observation(step_id=pc["step_id"], tool=pc["tool"], ok=False, error="rejected_by_user：用户拒绝了该操作")
        return {"pending_call": None, "observations": [obs.model_dump(mode="json")],
                "step_count": st.get("step_count", 0) + 1}
    args_json = pc["args_json"]
    if decision == "edit" and resp.get("edited_args"):
        args_json = json.dumps(resp["edited_args"], ensure_ascii=False)   # 仍会经过 Pydantic 校验
    return {"pending_call": {**pc, "args_json": args_json, "approved": True}}
```

`graph.py`：注册 `approve` 节点；把 `act → tools` 改为 `add_conditional_edges("act", route_after_act, {"approve": "approve", "tools": "tools"})`，再加 `add_conditional_edges("approve", route_after_approve, {"tools": "tools", "decide": "decide"})`。`tools_node` 调用改为 `execute(pc["tool"], pc["args_json"], approved=pc.get("approved", False))`。重新生成 `docs/agent-graph.md`。

### Step 3 · runner 与 API

- `runner.run_v1_events`：`astream` 收到 `"__interrupt__"` 键时，取 `chunk["__interrupt__"][0].value`，产出 `AgentEvent(type="approval_required", data={...value, "run_id": run_id})`，并**不再产出 done**。`EventType` 增加 `approval_required`。
- 新增 `runner.resume_v1_events(run_id, thread_id, resume, graph, start_seq)`：`graph.astream(Command(resume=resume), config, stream_mode="updates")`，其余同上。
- `gen()` 收到 `approval_required` 时：`run.status = "waiting_approval"`，`run.pending_action = json.dumps(e.data)`。

`routes/agent.py`：

```python
class ApproveIn(BaseModel):
    decision: Literal["approve", "reject", "edit"]
    edited_args: dict[str, Any] | None = None

@router.post("/runs/{run_id}/approve")
async def approve_run(run_id: str, body: ApproveIn, request: Request):
    if body.decision == "edit" and not body.edited_args:
        raise HTTPException(422, "edit 需要 edited_args")
    with get_session_ctx() as db:
        run = db.get(AgentRun, run_id)
        if run is None:
            raise HTTPException(404, "run not found")
        if run.status != "waiting_approval":                    # 防重复审批 / 越序调用
            raise HTTPException(409, f"run status is {run.status}")
        last_seq = db.exec(select(func.max(AgentStep.seq)).where(AgentStep.run_id == run_id)).one() or 0
        db.add(AgentStep(run_id=run_id, seq=last_seq + 1, type="approval",       # 审计：谁在何时做了什么决定
                         payload=body.model_dump_json()))
        run.status, run.pending_action = "running", None
        db.commit()
    events = runner.resume_v1_events(run_id=run_id, thread_id=run.conversation_id or run_id,
                                     resume=body.model_dump(), graph=request.app.state.agent_graph,
                                     start_seq=last_seq + 2)
    return StreamingResponse(gen(run_id, events), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache"})
```

`docs/api.md`：补 `approval_required` 事件（tool / args / step_id / goal）与 approve 接口（请求体、200 SSE、404 / 409 / 422）。

### Step 4 · 核心测试：未批准绝不写

`tests/agent/test_hitl.py`（fixture：monkeypatch `steps.*` 让 plan 1 步、`choose_action` 返回 `gitea_issue_create` 调用、decide 有 1 条观察即 finish；`memory.get_store` 换成 `:memory:` 实例、extractor 返回空）：

```python
ISSUES = "http://localhost:3000/api/v1/repos/me/sandbox-issues/issues"
CREATED = {"number": 1, "html_url": "http://localhost:3000/me/sandbox-issues/issues/1"}

@pytest.mark.asyncio
@respx.mock
async def test_no_write_until_approved(fake_agent, tmp_path):
    route = respx.post(ISSUES).mock(return_value=httpx.Response(201, json=CREATED))
    async with AsyncSqliteSaver.from_conn_string(str(tmp_path / "cp.sqlite")) as saver:
        graph = build_graph(checkpointer=saver)
        cfg = {"configurable": {"thread_id": "t1", "run_id": "r1"}, "recursion_limit": 60}
        await graph.ainvoke(new_turn_input("把待确认问题建成 issue"), cfg)
        assert (await graph.aget_state(cfg)).next == ("approve",)
        assert route.call_count == 0                                  # 中断时：0
        await graph.ainvoke(Command(resume={"decision": "reject"}), cfg)
        assert route.call_count == 0                                  # 拒绝后：0

@pytest.mark.asyncio
@respx.mock
async def test_write_once_after_approve_with_edit(fake_agent, tmp_path):
    route = respx.post(ISSUES).mock(return_value=httpx.Response(201, json=CREATED))
    async with AsyncSqliteSaver.from_conn_string(str(tmp_path / "cp.sqlite")) as saver:
        graph = build_graph(checkpointer=saver)
        cfg = {"configurable": {"thread_id": "t2", "run_id": "r2"}, "recursion_limit": 60}
        await graph.ainvoke(new_turn_input("建 issue"), cfg)
        await graph.ainvoke(Command(resume={"decision": "edit", "edited_args": {"title": "改过的标题"}}), cfg)
        assert route.call_count == 1
        assert json.loads(route.calls.last.request.content)["title"] == "改过的标题"
```

再加：`test_execute_gate`（`execute("gitea_issue_create", '{"title":"abcd"}')` → `error == "approval_required"`，`route.call_count == 0`）；`test_unknown_decision_is_reject`（resume `{"decision": "yes"}` → 0 次）。fixture 中 monkeypatch `GITEA_SANDBOX_REPO="me/sandbox-issues"`、`GITEA_WRITE_TOKEN`。

```bash
uv run pytest tests/agent/test_hitl.py -q && uv run pytest -q
```

### Step 5 ·（P1）前端审批卡片

`components/agent/ApprovalCard.tsx`：

```tsx
export function ApprovalCard({
  tool,
  args,
  busy,
  onDecide,
}: {
  tool: string;
  args: Record<string, unknown>;
  busy: boolean;
  onDecide: (
    d: "approve" | "reject" | "edit",
    edited?: Record<string, unknown>,
  ) => void;
}) {
  const original = JSON.stringify(args, null, 2);
  const [text, setText] = useState(original);
  const [err, setErr] = useState<string | null>(null);
  const approve = () => {
    if (text === original) return onDecide("approve");
    try {
      onDecide("edit", JSON.parse(text));
    } catch {
      setErr("参数不是合法 JSON");
    }
  };
  return (
    <div className="rounded border border-amber-400 bg-amber-50 p-3">
      <div className="font-medium">需要审批：{tool}（写操作）</div>
      <textarea
        className="mt-2 w-full font-mono text-xs"
        rows={8}
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          setErr(null);
        }}
      />
      {err && <div className="text-xs text-red-600">{err}</div>}
      <div className="mt-2 flex gap-2">
        <button disabled={busy} onClick={approve}>
          批准{text !== original ? "（已修改）" : ""}
        </button>
        <button disabled={busy} onClick={() => onDecide("reject")}>
          拒绝
        </button>
      </div>
    </div>
  );
}
```

`useAgentRun`：收到 `approval_required` → `status = 'waiting_approval'` 并保存 `pending`；新增 `decide(decision, edited)` → `POST /api/v1/agent/runs/{runId}/approve`，用 `readSSE` 把后续事件追加到同一时间线。

### Step 6 ·（P1）SP-B 迷你流程

`app/scenarios/sp_b_req_breakdown/graph.py`：节点 `breakdown`（`structured_with_usage(..., TaskBreakdown)`）→ `review`（`interrupt({"kind": "issue_batch_approval", "drafts": [...]})`，resume 支持 approve / reject / `edited_drafts`）→ `create`（逐个 `execute("gitea_issue_create", ..., approved=True)`）→ END；checkpointer 同上。Issue body 由任务的描述 + 验收标准渲染。

`scripts/sp_b_pilot.py`：读取 `data/sample/sp_b_requirement.md`（脱敏样例，如「为 WorkPilot Agent 页增加『导出报告为 Markdown』功能……」）→ 运行到中断 → 终端打印草稿 → `input("全部批准? [y/N]")` → resume → 打印创建结果。

已知限制（写进 draft.md，W17–18 场景包 MVP 再解决）：`create` 节点中途失败恢复时会整节点重跑，可能重复创建——后续按「每个 Issue 一个审批 + 已创建列表写回 state」改造。

### Step 7 ·（P1）简历双周更新 + 提交 + tag

三版简历各加入 1–2 条（LangGraph 迁移与可靠性 / 双层记忆 / HITL 审批），数字用 W11 对比报告与今天测试结果；更新日期。

```bash
cd ~/lab/workpilot
git add apps/api apps/web docs/api.md docs/agent-graph.md scripts/sp_b_pilot.py data/sample/sp_b_requirement.md .env.example
git commit -m "feat(agent): human-in-the-loop approval for write tools and SP-B pilot flow"
git tag -a v0.8.0 -m "v0.8.0: LangGraph agent + memory + HITL approval"
git push && git push origin v0.8.0 && git push github main --tags
cd ~/lab/projects && git add career/resume && git commit -m "docs(career): biweekly resume update (W12)" && git push
```

（`data/sample/` 是 phase_01 约定的公开样例目录；确认样例无任何公司信息再提交。）

## 7. 概念自检（不看资料，口述，附答案）

1. `Command(resume=...)` 后，approve 节点从哪里开始执行？（答：从节点开头重新执行，执行到 `interrupt()` 时直接返回 resume 值；所以 interrupt 之前不能有副作用。）
2. 为什么图里有审批节点，`execute()` 还要再检查 `approved`？（答：纵深防御：图结构写错、新增调用路径或 MCP 暴露工具时，执行层仍然拦截未审批的写操作。）
3. 为什么写工具不接收 `repo` 参数？（答：参数来自模型，可能被注入操纵；把目标仓库固定在配置里，模型无法把写操作指向其他仓库。）
4. Gitea token 为什么要用独立 bot 账号？（答：Gitea token scope 只能按类别授权，无法限定单个仓库；bot 只被加入沙盒仓库，token 泄露也只影响沙盒。）
5. approve 接口为什么要先检查 `waiting_approval` 再改成 `running`？（答：防止重复提交导致同一中断被恢复两次（重复写入），也拒绝对未暂停的运行进行审批。）
6. 拒绝之后 Agent 会怎样？（答：拒绝被记录为一条失败观察进入 decide，Agent 可以换方案或结束，报告中体现「用户拒绝了创建 Issue」。）

## 8. 对 DA-01 的贡献

WorkPilot 达到 v0.8，第一次「替人做事」而且是安全地做：写操作必须经人批准（§11「未经审批的写操作 = 0」有测试证据），主场景 SP-B 首次端到端跑通——从需求文本到沙盒仓库里的真实 Issue，这是 W17–W18 场景包 MVP 的直接原型。

## 9. 求职映射（D 线）

- 岗位能力：Human-in-the-loop、LangGraph interrupt / Command、过度代理防护、最小权限设计、研发效能场景落地。
- 对应岗位：AI Agent Engineer、AI Full-Stack Engineer。
- 简历 bullet 草稿：基于 LangGraph `interrupt()` 实现 Agent 写操作人工审批（批准 / 拒绝 / 改参后批准），图结构 + 执行层双重门禁、专用低权限 bot token，测试证明未审批写操作为 0；落地「需求 → 任务拆解 → 审批 → 自动创建 Issue」流程，单次拆解 \_\_ 个任务。
- 面试可能问：
  - Q：如何让 Agent 安全地执行写操作？要点：权限分级、审批节点、执行层门禁、参数可编辑、目标固定、低权限凭证、审计记录、幂等性。
  - Q：审批等待期间服务重启怎么办？要点：checkpoint 持久化在 SQLite，run 状态在 DB，重启后 approve 接口以同一 thread_id resume 即可。

## 10. 卡住时的处理

| 现象                                | 处理                                                                                                                         |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `interrupt()` 报错需要 checkpointer | 测试和 API 中的 graph 都必须 `build_graph(checkpointer=saver)`                                                               |
| resume 后又停在 approve             | resume 的 `thread_id` 与原运行不一致；或 approve 节点返回后 `pending_call.tool` 仍被判为需要审批——检查 `route_after_approve` |
| astream 中拿不到 `__interrupt__`    | 打印每个 chunk 的键；旧版本可在流结束后 `aget_state(config)`，用 `snap.tasks[0].interrupts[0].value` 取 payload              |
| Gitea 创建返回 403 / 404            | bot 未被加为沙盒仓库协作者，或 token 没有 issue 写 scope；用 curl 单独验证 token                                             |
| 前端审批后时间线不继续              | approve 接口返回的是 SSE，前端需用 `readSSE` 读取，而不是 `res.json()`                                                       |
| 时间不够做审批卡片 / SP-B           | 按第 4 节裁剪：保 P0 + tag；在 draft.md 记顺延，Day46 前 30 分钟补                                                           |

## 11. 产出记录（执行时填写）

- `test_hitl.py` 结果（中断 / 拒绝 / 批准 / 修改 / 门禁）：\_\_\_\_
- 审批卡片演示录屏路径：\_\_\_\_
- SP-B：需求 → 拆解任务数 ** → 批准创建 Issue 数 **（截图）
- v0.8.0 commit：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 12 完成，填写周复盘 → 明天进入 Day46「W13 Task 1：MCP Server（stdio）+ Inspector」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
