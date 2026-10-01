# Day 61 · 2026-11-27 · Week 18 Task 2：场景页面 + 5 个真实样例（v1.1）

## 0. 今天只做一件事

做出 ScenarioPage（输入 → 时间线 → 可编辑任务表 → 批准 → Issue 链接），用 5 个脱敏样例端到端跑通并记录耗时对比，发布 `v1.1.0`。

不碰：登录 / 空间切换（W19）、评测集（W20）、上传 PDF 解析（只支持粘贴和 .md/.txt）、样式打磨。

## 1. 资产锚点

- 构建模块：M10 场景包 SP-B、M4.3 Agent 运行视图（复用时间线与审批组件）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v1.1**（DA-01 主场景包 MVP）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：2 分钟可演示的 P3 端到端流程；`p3-notes.md` 中 5 个样例「手工 vs WorkPilot」耗时数据
- 今日 AI 实际应用：Human-in-the-loop 的 AI UX——把 LLM 草案变成「人可快速修正」的表格，编辑行为将在 W20 成为隐式反馈信号

## 2. 起点（前置确认）

- 已有：Day60 的 `/v1/scenarios/sp_b/runs` 与 `/runs/{id}/resume`；W10 时间线组件、W12 审批组件；`apps/web` 的 API client 与路由。
- 需确认：

```bash
cd ~/lab/workpilot
uv run --directory apps/api pytest -q tests/scenarios          # Day60 测试仍绿
ls apps/web/src/components | grep -i -E "timeline|approval"    # 找到可复用组件
grep -n "path:" apps/web/src/*.tsx apps/web/src/router* 2>/dev/null | head   # 路由定义位置
pnpm --dir apps/web dev                                        # 前端能起
```

## 3. 验收对齐（做完要能勾掉）

- [ ] 访问 `/scenarios/sp_b`：粘贴需求或选择 .md 文件 → 点「开始拆解」
- [ ] 运行中显示时间线（parse → retrieve → breakdown → self_check → 等待审批）
- [ ] 任务表可：改估时、删任务、改验收标准（至少前两项），底部显示合计工时
- [ ] 「批准」后显示 Gitea Issue 链接列表；「拒绝」后显示 summary
- [ ] 5 个样例端到端完成，`docs/portfolio/p3-notes.md` 有耗时表
- [ ] `v1.1.0` tag 已推送，CI 绿

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                  |
| ----------- | ------ | ----------------------------------------------------- |
| 0–10 min    | P0     | API client 函数 + 路由注册                            |
| 10–35 min   | P0     | ScenarioPage：表单 + 启动 + 时间线复用                |
| 35–65 min   | P0     | TaskTableEditor（改估时 / 删任务 / 合计）             |
| 65–75 min   | P0     | 批准 / 拒绝 → resume → Issue 链接                     |
| 75–105 min  | P0     | 5 个样例端到端 + 计时 → p3-notes.md                   |
| 105–115 min | P1     | 改验收标准编辑、.md 文件上传                          |
| 115–120 min | P0     | tag v1.1.0                                            |
| 顺延        | P2     | 拖拽排序任务、依赖关系可视化、导出 Markdown → Backlog |

时间不足时最低保留：能看到草案 + 删任务 + 批准 + 链接；3 个样例；tag。

## 5. 今日学习（只学完成任务必须的）

- **受控表格编辑**：任务表是本地 state 的副本，提交时把整个编辑后数组发给 resume；原始草案保留用于 W20 计算 diff。
- **AI UX 原则**：展示「AI 做了什么」（时间线）+「哪里可能不对」（self_check problems 显示为黄色提示）+「人有最终决定权」（编辑/拒绝）。
- **长任务交互**：启动后立即返回 run_id，前端用 SSE 或 2 秒轮询显示进度，不要让按钮卡 60 秒。
- 资料：https://langchain-ai.github.io/langgraph/ （Human-in-the-loop：编辑状态后恢复）

## 6. 执行步骤

### Step 1 · API client（P0，可让 AI 生成）

```ts
// apps/web/src/api/scenarios.ts
export type Task = {
  title: string;
  description: string;
  estimate_hours: number;
  acceptance_criteria: string[];
  depends_on?: number[];
};
export type Draft = {
  tasks: Task[];
  risks: string[];
  related_issues: string[];
};
export type StartResp = {
  run_id: string;
  status: "awaiting_approval" | "done";
  interrupt?: { draft: Draft; check: { passed: boolean; problems: string[] } };
};

export async function startRun(
  sp: string,
  requirement: string,
): Promise<StartResp> {
  const r = await fetch(`/api/v1/scenarios/${sp}/runs`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ requirement }),
  });
  if (!r.ok) throw new Error(`start failed: ${r.status}`);
  return r.json();
}

export async function resumeRun(
  runId: string,
  decision: { action: "approve"; tasks: Task[] } | { action: "reject" },
) {
  const r = await fetch(`/api/v1/scenarios/runs/${runId}/resume`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(decision),
  });
  if (!r.ok) throw new Error(`resume failed: ${r.status}`);
  return r.json() as Promise<{
    issues: { url: string; title: string }[];
    summary: string;
  }>;
}
```

> 若 Day60 已接 SSE 时间线事件，时间线直接复用 W10 的 `useAgentEvents(runId)`；否则今天先显示「运行中…」+ 完成后一次性渲染步骤（P0 足够）。

### Step 2 · TaskTableEditor（P0，核心交互自己写）

```tsx
// apps/web/src/components/TaskTableEditor.tsx
import type { Task } from "../api/scenarios";

export function TaskTableEditor({
  tasks,
  onChange,
}: {
  tasks: Task[];
  onChange: (t: Task[]) => void;
}) {
  const update = (i: number, patch: Partial<Task>) =>
    onChange(tasks.map((t, j) => (j === i ? { ...t, ...patch } : t)));
  const remove = (i: number) => onChange(tasks.filter((_, j) => j !== i));
  const total = tasks.reduce((s, t) => s + (Number(t.estimate_hours) || 0), 0);

  return (
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>#</th>
          <th>任务</th>
          <th>估时(h)</th>
          <th>验收标准</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {tasks.map((t, i) => (
          <tr key={i} className="border-t align-top">
            <td>{i + 1}</td>
            <td>
              <b>{t.title}</b>
              <p className="text-gray-500">{t.description}</p>
            </td>
            <td>
              <input
                type="number"
                min={0.5}
                max={40}
                step={0.5}
                className="w-16 border"
                value={t.estimate_hours}
                onChange={(e) =>
                  update(i, { estimate_hours: Number(e.target.value) })
                }
              />
            </td>
            <td>
              <textarea
                className="w-full border"
                rows={2}
                value={t.acceptance_criteria.join("\n")}
                onChange={(e) =>
                  update(i, {
                    acceptance_criteria: e.target.value
                      .split("\n")
                      .filter(Boolean),
                  })
                }
              />
            </td>
            <td>
              <button onClick={() => remove(i)} aria-label="删除任务">
                删除
              </button>
            </td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td colSpan={2}>合计</td>
          <td>{total} h</td>
          <td colSpan={2} />
        </tr>
      </tfoot>
    </table>
  );
}
```

> 文本一律用 React 默认转义渲染，**不要** `dangerouslySetInnerHTML`（LLM 输出不可信，W21 LLM05）。

### Step 3 · ScenarioPage（P0）

```tsx
// apps/web/src/pages/ScenarioPage.tsx（骨架）
const [req, setReq] = useState("");
const [run, setRun] = useState<StartResp | null>(null);
const [tasks, setTasks] = useState<Task[]>([]);
const [result, setResult] = useState<{
  issues: { url: string; title: string }[];
  summary: string;
} | null>(null);
const [loading, setLoading] = useState(false);

async function onStart() {
  setLoading(true);
  try {
    const r = await startRun("sp_b", req);
    setRun(r);
    setTasks(r.interrupt?.draft.tasks ?? []);
  } finally {
    setLoading(false);
  }
}
async function onApprove() {
  setResult(await resumeRun(run!.run_id, { action: "approve", tasks }));
}
// 文件选择：<input type="file" accept=".md,.txt" onChange={e => e.target.files?.[0]?.text().then(setReq)} />
// check.problems 非空时显示黄色提示条：「AI 自检发现：…」
// result.issues 渲染为 <a href={i.url} target="_blank" rel="noopener noreferrer">
```

注册路由 `/scenarios/sp_b`，在导航栏加「需求拆解」入口。

### Step 4 · 5 个样例端到端 + 计时（P0，30 分钟）

从 `data/scenarios/` 选 5 个（至少含 1 个模糊需求、1 个大需求）。每个样例记录：

- **手工耗时**：Day58 记录的历史估算，或今天对 1 个样例实际手工拆一次计时（只需 1 个实测，其余用估算并标注）。
- **WorkPilot 耗时** = 运行时间 + 人工编辑审批时间。

`docs/portfolio/p3-notes.md`：

```markdown
# P3 Notes · SP-B 样例记录（v1.1.0）

| 样例    | 类型    | 手工耗时(min) | 运行(s) | 编辑审批(min) | WP 总耗时(min) | 删除/修改任务数 | 备注               |
| ------- | ------- | ------------- | ------- | ------------- | -------------- | --------------- | ------------------ |
| spb_001 | feature | 25（实测）    | 42      | 4             | 4.7            | 1/2             | 漏了导出上限的验收 |
| spb_00x | ...     | 20（估算）    |         |               |                |                 |                    |
| 平均    |         | \_\_          | \_\_    | \_\_          | \_\_           |                 |                    |

## 观察（写给 W20 评测与 W23 Portfolio）

- 最常被我修改的地方：\_\_\_\_
- AI 明显做得好的地方：\_\_\_\_
- 候选 badcase：\_\_\_\_（写入 eval/badcases/badcases.md）
```

> 只用脱敏样例；Issue 建在沙盒仓库（如 `workpilot-sandbox`），演示完可批量关闭。

### Step 5 · 发布 v1.1.0

```bash
cd ~/lab/workpilot
pnpm --dir apps/web build && uv run --directory apps/api pytest -q
git add apps/web/src docs/portfolio/p3-notes.md
git commit -m "feat(web): add SP-B scenario page with editable task approval"
git push
git tag -a v1.1.0 -m "v1.1.0: SP-B scenario pack MVP (graph + page + 5 samples)"
git push origin v1.1.0
```

在 Gitea 仓库 Releases 页面基于 tag 写 3 行 Release notes（功能 / 样例数据 / 已知问题）。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么前端提交的是「整个编辑后任务表」而不是 patch？（答：简单、可校验；后端按 schema 整体验证，原始草案已在 checkpoint 中，W20 再算 diff）
2. 为什么 LLM 生成的文本不能用 `dangerouslySetInnerHTML`？（答：LLM 输出可能被注入恶意 HTML/脚本，属于 OWASP LLM05 不当输出处理）
3. 长耗时 Agent 运行为什么要先返回 run_id？（答：避免 HTTP 超时与界面卡死；进度可通过 SSE/轮询获取，刷新页面后能恢复）
4. 「WorkPilot 总耗时」为什么要包含人工编辑时间？（答：真实价值是端到端省时，只算模型时间会高估收益）
5. self_check problems 为什么要展示给用户？（答：提示 AI 自知的不确定点，引导人工重点审查，提升信任与修正效率）

## 8. 对 DA-01 的贡献

DA-01 第一次具备完整的「业务价值演示」：用户能独立在 Web 上完成需求拆解并落到 Issue。v1.1 是 P3 作品集的第一个可演示版本；p3-notes.md 的耗时数据是 P3 Result 节和简历量化 bullet 的原始证据。

## 9. 求职映射（D 线）

- 岗位能力：AI UX（人机协作审批）、React 表格交互、前后端联调、发布管理。
- 对应岗位：AI Full-Stack Engineer、Frontend Engineer（AI 产品方向）。
- 简历 bullet 草稿：「设计『可编辑审批』交互：用户可在 AI 草案上改估时 / 删任务后一键写入 Issue，5 个样例端到端平均耗时由 ** 分钟降至 ** 分钟（-\_\_%）」
- 面试可能问：
  1. 你如何设计 AI 产品的信任感？——要点：过程可见（时间线）、不确定性可见（自检提示）、人有最终控制（编辑/拒绝）、结果可追溯（Issue 链接 + trace）。
  2. 前端怎么处理 LLM 输出安全？——要点：默认转义、禁 raw HTML、外链 `rel="noopener noreferrer"`、图片白名单（W21）。

## 10. 卡住时的处理

| 现象               | 处理                                                                   |
| ------------------ | ---------------------------------------------------------------------- |
| 前端请求 404       | 检查 Vite proxy `/api` → `localhost:8000` 是否去掉前缀，与 W6 配置一致 |
| 启动后页面卡很久   | 先加 loading 状态；后端若是同步 invoke，P2 再改后台任务 + 轮询         |
| resume 返回 422    | 编辑后估时为空 / 0；输入框 min=0.5 并在提交前过滤空验收标准            |
| Issue 链接为空     | 检查 `gitea_issue_create` 返回结构，统一为 `{url, title}`              |
| 样例运行质量很差   | 不在今天调 prompt（W20 有评测再调）；记录到 p3-notes「候选 badcase」   |
| CI 红（前端 lint） | 只修本次新增文件的报错；与本任务无关的历史问题记 Backlog               |

## 11. 产出记录（执行时填写）

- 5 样例平均：手工 ** min / WorkPilot ** min / 节省 \_\_%
- 平均删除任务 ** 个，修改 ** 个
- 候选 badcase：\_\_ 条
- v1.1.0 Release 链接：\_\_\_\_
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day62 · W19 Task 1「Postgres + Alembic + 认证 + 空间隔离」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（页面闭环 + 3 样例 + tag）。
