# Day 39 · 2026-11-05 · Week 10 Task 3：Agent 时间线 UI + 简历 v0（v0.7）

## 0. 今天只做一件事

做出 WorkPilot 的 Agent 页面：输入任务 → 竖向时间线实时展示每一步 → 最终报告与来源；用 10 个任务冒烟留下 v0 基线，建好三版简历骨架，打 tag `v0.7.0`。

不碰：审批卡片（Day45）、Trace / Ops 看板（W15）、LangGraph（W11）、新 UI 组件库。

## 1. 资产锚点

- 构建模块：M4.3 Agent 运行视图、M13.3 简历 ×3（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.7**（Research Agent v0，手写循环）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：浏览器打开 `/agent` 输入任务，时间线逐条出现（计划 / 工具调用 / 结果 / 决策），每条显示耗时与 token 成本，结束后展示报告与可点击来源；`eval/reports/20261105-agent-v0-smoke.md` 给出 10 任务成功数、平均步数、平均 tokens。
- 今日 AI 实际应用：Agent 过程可视化（AI UX：透明度 = 信任）→ 用在 `apps/web/src/pages/AgentPage.tsx`；不可信工具输出纯文本渲染 → 前端侧的注入防护。

## 2. 起点（前置确认）

- 已有：Day38 `POST /v1/agent/run`（SSE）、`docs/api.md` 事件 schema；phase_01 `useStreamingAnswer`、react-markdown + rehype-sanitize、路由与布局。
- 需确认：

```bash
cd ~/lab/workpilot/apps/web && pnpm dev                 # 页面能打开
grep -n "getReader\|TextDecoder" -r src/hooks | head      # 找到 phase_01 的 SSE 解析代码
grep -n "proxy" vite.config.ts                            # 确认 API 代理前缀（下文记作 /api）
curl -s localhost:8000/health
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `src/lib/sse.ts` 抽出通用 `readSSE()`，`useStreamingAnswer` 改为复用它且聊天页仍正常
- [ ] `useAgentRun` hook：start / stop、events、status、汇总 tokens 与成本
- [ ] 时间线：按事件类型显示图标与标题；tool_call + tool_result 合并为一项，参数与结果可折叠；显示耗时与 tokens/成本
- [ ] 工具结果以 `<pre>` 纯文本渲染；报告用 react-markdown + rehype-sanitize；来源 URL 可点击（`rel="noopener noreferrer"`）
- [ ] `eval/datasets/agent_smoke.jsonl` 10 任务 + 冒烟报告
- [ ] `career/resume/` 三份简历骨架，每份 ≥3 条 bullet
- [ ] tag `v0.7.0` 推送 Gitea + GitHub；周复盘已填

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                 |
| ----------- | ------ | -------------------------------------------------------------------- |
| 0–15 min    | P0     | 抽 `readSSE()` + `useAgentRun`                                       |
| 15–55 min   | P0     | `AgentTimeline` / `TimelineItem` / `ReportView` + `AgentPage` + 路由 |
| 55–75 min   | P0     | 10 任务冒烟（脚本跑，边跑边做简历）                                  |
| 60–85 min   | P1     | 三版简历骨架（与冒烟并行）                                           |
| 85–95 min   | P0     | tag `v0.7.0` + push                                                  |
| 95–110 min  | P1     | 录 30–60 秒演示 GIF；周复盘                                          |
| 110–120 min | P2     | 时间线「复制 run_id」「重新运行」按钮                                |

时间不足时最低保留：时间线（不折叠）+ 报告 + 5 任务冒烟 + ai-engineer 一份简历 + tag。

## 5. 今日学习（只学完成任务必须的）

- **fetch 流读取**：`res.body.pipeThrough(new TextDecoderStream()).getReader()`，按 `\n\n` 切事件、取 `data:` 行。
- **AbortController**：页面切换或用户点「停止」时中止请求，服务端生成器随之结束。
- **事件归并**：同一 `step_id` 的 tool_call 与 tool_result 合并显示，状态从「进行中」变为「成功 / 失败」。
- **不可信内容渲染**：工具结果可能含 HTML/脚本，只能作为文本节点渲染；Markdown 报告经 sanitize。
- 资料：
  - https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams
  - https://developer.mozilla.org/en-US/docs/Web/API/AbortController
  - https://react.dev/reference/react/useReducer

## 6. 执行步骤

### Step 1 · 抽出 SSE 解析

`apps/web/src/lib/sse.ts`：

```ts
export async function* readSSE(res: Response): AsyncGenerator<string> {
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += value;
    let idx: number;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const chunk = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      const data = chunk
        .split("\n")
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trimStart())
        .join("\n");
      if (data) yield data;
    }
  }
}
```

把 `useStreamingAnswer` 里的同类循环替换为 `for await (const data of readSSE(res))`，打开聊天页确认仍正常（回归）。

### Step 2 · 类型 + hook

`apps/web/src/api/agent.ts`：

```ts
export type AgentEventType =
  | "plan"
  | "step_start"
  | "tool_call"
  | "tool_result"
  | "decision"
  | "report"
  | "done"
  | "error";
export interface AgentEvent {
  type: AgentEventType;
  run_id: string;
  seq: number;
  ts: string;
  data: Record<string, any>;
  usage?: { tokens: number; cost_cny: number } | null;
}
```

`apps/web/src/hooks/useAgentRun.ts`：

```ts
import { useCallback, useRef, useState } from "react";
import { readSSE } from "../lib/sse";
import type { AgentEvent } from "../api/agent";

type Status = "idle" | "running" | "done" | "error";

export function useAgentRun() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [status, setStatus] = useState<Status>("idle");
  const abortRef = useRef<AbortController | null>(null);

  const start = useCallback(async (task: string) => {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setEvents([]);
    setStatus("running");
    try {
      const res = await fetch("/api/v1/agent/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task }),
        signal: ac.signal,
      });
      for await (const data of readSSE(res)) {
        const ev = JSON.parse(data) as AgentEvent;
        setEvents((prev) => [...prev, ev]);
        if (ev.type === "done") setStatus("done");
        if (ev.type === "error") setStatus("error");
      }
    } catch {
      if (!ac.signal.aborted) setStatus("error");
    }
  }, []);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setStatus("idle");
  }, []);
  const totals = events.reduce(
    (a, e) => ({
      tokens: a.tokens + (e.usage?.tokens ?? 0),
      cost: a.cost + (e.usage?.cost_cny ?? 0),
    }),
    { tokens: 0, cost: 0 },
  );
  return { events, status, start, stop, totals };
}
```

### Step 3 · 时间线组件（结构自己定，样式让 AI 写 Tailwind）

```text
src/components/agent/
├── AgentTimeline.tsx   # 把 events 归并成 TimelineEntry[]：plan / step（含 call+result）/ decision / error
├── TimelineItem.tsx    # 左侧图标 + 竖线；标题、耗时、tokens/成本；<details> 折叠参数与结果
└── ReportView.tsx      # react-markdown + rehype-sanitize 渲染 report.markdown + 来源列表
```

归并逻辑（核心，自己写）：

```ts
export type TimelineEntry =
  | {
      kind: "plan";
      seq: number;
      steps: { id: number; goal: string; suggested_tool?: string }[];
      replan?: number;
      usage?: AgentEvent["usage"];
    }
  | {
      kind: "step";
      stepId: number;
      goal: string;
      tool?: string;
      args?: string;
      ok?: boolean;
      preview?: string;
      error?: string;
      latencyMs?: number;
      usage?: AgentEvent["usage"];
    }
  | {
      kind: "decision";
      seq: number;
      action: string;
      reason: string;
      usage?: AgentEvent["usage"];
    }
  | { kind: "error"; seq: number; message: string };

export function toEntries(events: AgentEvent[]): TimelineEntry[] {
  const out: TimelineEntry[] = [];
  let cur: Extract<TimelineEntry, { kind: "step" }> | null = null;
  for (const e of events) {
    switch (e.type) {
      case "plan":
        out.push({
          kind: "plan",
          seq: e.seq,
          steps: e.data.steps,
          replan: e.data.replan,
          usage: e.usage,
        });
        break;
      case "step_start":
        cur = { kind: "step", stepId: e.data.step_id, goal: e.data.goal };
        out.push(cur);
        break;
      case "tool_call":
        if (cur)
          Object.assign(cur, {
            tool: e.data.tool,
            args: e.data.args,
            usage: e.usage,
          });
        break;
      case "tool_result":
        if (cur)
          Object.assign(cur, {
            ok: e.data.ok,
            preview: e.data.preview,
            error: e.data.error,
            latencyMs: e.data.latency_ms,
          });
        break;
      case "decision":
        out.push({
          kind: "decision",
          seq: e.seq,
          action: e.data.action,
          reason: e.data.reason,
          usage: e.usage,
        });
        break;
      case "error":
        out.push({ kind: "error", seq: e.seq, message: e.data.message });
        break;
    }
  }
  return out;
}
```

> `toEntries` 每次调用都新建 entry 对象，`Object.assign` 只修改本次新建的对象，不会污染 state；在组件里用 `useMemo(() => toEntries(events), [events])` 调用即可。

`TimelineItem` 关键约束：

- 图标：用文字徽标即可（如 `PLAN` / `TOOL` / `DECIDE` / `ERR`），不依赖图标库。
- 工具参数 / 结果：`<details><summary>参数</summary><pre className="whitespace-pre-wrap text-xs">{args}</pre></details>`——**绝不使用 `dangerouslySetInnerHTML`**。
- 状态色：进行中（灰）/ ok（绿）/ 失败（红）；decision 的 `replan` 用黄色。

`pages/AgentPage.tsx`：顶部 textarea + 「运行 / 停止」按钮 + 右上角汇总（步数、tokens、¥成本）；中间时间线；底部 `ReportView`（取最后一个 `report` 事件）。在路由与导航里加入「Agent」。

### Step 4 · 10 任务冒烟

`eval/datasets/agent_smoke.jsonl`（10 条，W11 Day42 v0/v1 对比复用）：3 条纯 KB、2 条 Web + KB、2 条 Gitea 仓库、2 条 Gitea Issue（SP-B 语境，如「把 sandbox-issues 里未分配的 issue 按模块归类并给出优先级建议」）、1 条信息不足任务（期望报告明确说「信息不足」）。每条：`{"id":"as-01","task":"...","expect":"一句话期望"}`。

`eval/runners/run_agent_smoke.py`（AI 生成）：逐条消费 `run_events()`，记录 stop_reason、steps、tokens、cost、耗时、工具序列、报告 Markdown 存 `eval/reports/agent-v0-smoke/<id>.md`；汇总表写 `eval/reports/20261105-agent-v0-smoke.md`，留「人工判定：可用 Y/N + 原因」一列，跑完后自己填。

### Step 5 · 三版简历骨架（与冒烟并行）

```text
~/lab/projects/career/resume/
├── resume-frontend.md       # 定位：资深前端（AI 产品方向）—— 突出 M4 Web Console、SSE、Agent 时间线
├── resume-ai-fullstack.md   # 定位：AI 全栈 —— P1 完整链路 + P2 Agent + 部署
└── resume-ai-engineer.md    # 定位：AI 应用工程师 —— RAG 评测、Tool Layer、Agent 运行时
```

每份结构：一句话定位 / 技能（按定位排序）/ 项目经历（P1 WorkPilot Knowledge：已完成，带 W5 评测数字；P2 WorkPilot Agent：进行中，用 W9–W10 数字）/ 工作经历（脱敏，只写技术与成果，不写公司内部数据）/ 教育。bullet 用「动作 + 技术 + 量化结果」格式，数字未知时写 `__` 占位。

### Step 6 · 提交 + tag

```bash
cd ~/lab/workpilot
git add apps/web eval/datasets/agent_smoke.jsonl eval/runners/run_agent_smoke.py eval/reports
git commit -m "feat(web): agent timeline page with streaming events and report view"
git tag -a v0.7.0 -m "v0.7.0: research agent v0 (hand-written loop) + timeline UI"
git push && git push origin v0.7.0 && git push github main --tags
cd ~/lab/projects && git add career/resume && git commit -m "docs(career): resume v0 skeletons x3" && git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么不用 `EventSource`？（答：`EventSource` 只支持 GET 且不能带请求体；任务文本较长，用 POST + fetch 流读取。）
2. 用户点「停止」后服务端会发生什么？（答：连接断开，StreamingResponse 的生成器在下次 yield 时被取消，循环随之终止；run 状态需在 finally 里标记，W11 再补。）
3. 为什么工具结果用 `<pre>` 而报告用 Markdown？（答：工具结果是外部不可信原文，只能当文本；报告是我们生成并经 sanitize 的内容，才允许富文本。）
4. 时间线为什么要合并 tool_call 与 tool_result？（答：用户心智是「一步做了一件事」，合并后能直接看到「调用 → 结果 → 耗时」，也减少视觉噪音。）
5. 三版简历的差异在哪？（答：同一项目不同侧重：前端版强调交互与流式 UX，全栈版强调端到端交付，AI 工程版强调评测、工具层与 Agent 运行时。）

## 8. 对 DA-01 的贡献

WorkPilot 达到 v0.7：F3 Agent 任务中心第一次有了用户界面，Agent 的每一步对用户透明可查；10 任务冒烟数据成为 W11 迁移与 W14 正式评测的基线；求职线有了可迭代的三版简历。

## 9. 求职映射（D 线）

- 岗位能力：AI UX（流式、过程可视化、可解释性）、React + TS 状态归并、前端安全渲染。
- 对应岗位：AI Full-Stack Engineer、Frontend Engineer（AI 产品）。
- 简历 bullet 草稿：设计并实现 Agent 运行时间线（React + TS），基于 SSE 实时展示规划 / 工具调用 / 决策，单次运行 tokens 与成本可视化；不可信工具输出纯文本隔离渲染。
- 面试可能问：
  - Q：AI 产品的前端和普通前端有什么不同？要点：流式与中断、过程透明、不确定性表达（来源 / 置信 / 待确认）、成本可见、不可信内容渲染。
  - Q：SSE 流断了怎么办？要点：AbortController、seq 断点、`GET /runs/{id}` 回放、后端状态最终一致。

## 10. 卡住时的处理

| 现象                      | 处理                                                                                                                         |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 事件一次性全部到达        | 检查 Vite 代理是否缓冲：dev 下直连 `http://localhost:8000` 对比；Caddy 环境确认 `flush_interval -1` 或 event-stream 自动刷新 |
| `JSON.parse` 报错         | 打印原始 data；多半是一个事件被拆成两段 → 确认按 `\n\n` 切分且保留残余 buf                                                   |
| 抽 `readSSE` 后聊天页坏了 | 先回滚 `useStreamingAnswer` 改动，Agent 页单独用 `readSSE`，周末再统一                                                       |
| 时间线顺序错乱 / 重复     | 用 `seq` 排序去重；React key 用 `run_id-seq`                                                                                 |
| 冒烟脚本太慢、成本偏高    | 只跑 5 条，其余 Day40 前补；记录单条 tokens，超 2 万的任务列入 badcase                                                       |
| 简历写不出数字            | 先用 `__` 占位，W14 评测后回填；不编造数字                                                                                   |

## 11. 产出记录（执行时填写）

- 冒烟：成功 **/10，平均步数 **，平均 tokens **，平均耗时 **s，总成本 ¥\_\_
- 主要失败类型：\_\_\_\_
- 演示 GIF 路径：\_\_\_\_
- v0.7.0 commit：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 10 完成，填写周复盘 → 明天进入 Day40「W11 Task 1：LangGraph 迁移」。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
