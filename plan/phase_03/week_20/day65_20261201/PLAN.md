# Day 65 · 2026-12-01 · Week 20 Task 2：在线反馈闭环 + 评测看板（v1.3）

## 0. 今天只做一件事

把「用户审批前对任务表的编辑」变成隐式反馈，建立 Badcase 候选队列 →（人工确认）→ 回归用例的闭环，并用 EvalRun 表 + 趋势页展示评测历史，产出 P3 评测报告 v1，发布 `v1.3.0`。

不碰：安全攻击集（W21）、badcase 总库合并（W22）、自动重训 / 自动改 prompt、第三方看板工具。

## 1. 资产锚点

- 构建模块：M3.6 在线反馈闭环、M4.4 Ops / Eval 看板、M3.5 回归（数据来源）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v1.3**（场景评测 + 在线反馈闭环）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：每次审批自动记录 edit_ratio；Badcase 队列页按「最差」排序；一键提升 → 导出为 regression 用例；趋势页显示通过率随版本变化
- 今日 AI 实际应用：隐式反馈（编辑 diff）作为生成质量的在线代理指标，接入 W5 起的 badcase → 回归流程

## 2. 起点（前置确认）

- 已有：Day64 数据集 / runner / 报告；W6 Feedback 表（👍👎）；W19 Alembic；W18 resume 接口（拿得到原始草案与批准版）。
- 需确认：

```bash
cd ~/lab/workpilot
grep -n "class Feedback" -A 12 apps/api/app/db/models.py      # 现有字段
ls eval/reports/ | grep -E "baseline|v0.5|v1.0|scenario"       # 可回填趋势的历史报告
cat eval/reports/latest-scenario.json | head -5                # Day64 结果存在
```

## 3. 验收对齐（做完要能勾掉）

- [ ] Feedback 新增 `kind`（explicit / implicit_edit）、`status`（new / promoted / ignored）、`payload`（JSONB）；EvalRun 表；迁移已应用
- [ ] 编辑后批准一次 SP-B → Feedback 出现 implicit_edit 记录，payload 含 deleted / modified / added / edit_ratio
- [ ] `GET /v1/eval/badcase-candidates` 返回 👎 或 edit_ratio ≥ 0.3 的运行，按 edit_ratio 降序
- [ ] `POST /v1/eval/badcase-candidates/{id}/promote`（需勾选 `desensitized=true`，owner 角色）→ status=promoted
- [ ] `scripts/export_regression.py` 导出新用例到 `scenario_spb.jsonl`（tags 含 regression），`git diff` 人工确认后提交
- [ ] runner 结束写 EvalRun；趋势页显示 ≥ 2 个点（含回填历史）
- [ ] `eval/reports/20261201-p3-eval-v1.md` 完成；`v1.3.0` 已部署

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                   |
| ----------- | ------ | ------------------------------------------------------ |
| 0–15 min    | P0     | 模型字段 + EvalRun + 迁移                              |
| 15–35 min   | P0     | diff 计算 + resume 时写 Feedback                       |
| 35–55 min   | P0     | 候选列表 / promote 接口 + 导出脚本                     |
| 55–65 min   | P0     | runner 写 EvalRun + 回填历史                           |
| 65–95 min   | P1     | BadcaseQueuePage + EvalTrendPage                       |
| 95–110 min  | P0     | P3 评测报告 v1                                         |
| 110–120 min | P0     | tag v1.3.0                                             |
| 顺延        | P2     | 显式 👎 原因分类自动聚类、EvalRun 对比详情页 → Backlog |

时间不足时最低保留：diff 入库 + promote 接口 + 导出脚本 + EvalRun 写入 + 报告 + tag。

## 5. 今日学习（只学完成任务必须的）

- **隐式反馈**：用户行为本身就是质量信号——删除的任务 = 多余，修改估时 = 估时不准，新增 = 漏拆。不打扰用户、覆盖率高，但有噪声（用户偏好不等于错误）。
- **edit_ratio** = (删除 + 修改 + 新增) / max(原任务数, 1)；阈值 0.3 只是初始值，看数据再调。
- **人在回路的数据飞轮**：线上数据 → 候选 → 人工确认（含脱敏）→ 回归集 → 修复 → 回归不退化。自动进入评测集会把噪声和敏感数据带进公开仓库。
- **线上服务不写 git**：API 只改 DB 状态；导出脚本在本地把 promoted 用例写入数据集文件，由人提交。
- 资料：https://jsonlines.org/ 、https://alembic.sqlalchemy.org/

## 6. 执行步骤

### Step 1 · 模型 + 迁移（P0）

```python
# app/db/models.py（增量）
class Feedback(SQLModel, table=True):
    # ...原有字段（message_id 可空化，以支持运行级反馈）
    run_id: uuid.UUID | None = Field(default=None, index=True)
    kind: str = Field(default="explicit")            # explicit | implicit_edit
    status: str = Field(default="new", index=True)  # new | promoted | ignored
    payload: dict = Field(default_factory=dict, sa_column=Column(JSONB))

class EvalRun(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workspace_id: uuid.UUID = Field(index=True)
    suite: str                 # rag | agent | scenario_spb | security
    version: str               # git tag 或 short sha
    metrics: dict = Field(sa_column=Column(JSONB))   # {"pass_rate":0.7,...}
    report_path: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

```bash
cd apps/api && uv run alembic revision --autogenerate -m "feedback kinds and eval runs" && uv run alembic upgrade head
```

> 迁移只加列（带默认值）和加表——保持 expand-only，Day63 的回滚策略继续成立。

### Step 2 · diff 计算（P0，核心逻辑自己写）

```python
# app/eval/feedback.py
def task_diff(draft: list[dict], approved: list[dict]) -> dict:
    by_title = {t["title"]: t for t in draft}
    kept = {t["title"] for t in approved if t["title"] in by_title}
    deleted = [t["title"] for t in draft if t["title"] not in kept]
    added = [t["title"] for t in approved if t["title"] not in by_title]
    modified, est_delta = [], 0.0
    for t in approved:
        o = by_title.get(t["title"])
        if o and (o["estimate_hours"] != t["estimate_hours"]
                  or o["acceptance_criteria"] != t["acceptance_criteria"]):
            modified.append(t["title"])
            est_delta += t["estimate_hours"] - o["estimate_hours"]
    n = max(len(draft), 1)
    return {"deleted": deleted, "added": added, "modified": modified,
            "estimate_delta_hours": round(est_delta, 1),
            "edit_ratio": round((len(deleted) + len(added) + len(modified)) / n, 2)}
```

在 resume 路由批准分支：从 checkpoint 取 `breakdown.tasks`（原始草案）与 `decision.tasks`，写 `Feedback(kind="implicit_edit", run_id=..., payload=task_diff(...))`（经 `WorkspaceRepo.add`）。给 `task_diff` 写 3 个单测（无编辑 / 删 1 / 改估时）。

### Step 3 · 候选队列 + promote + 导出（P0）

```python
# app/routes/eval.py
@router.get("/v1/eval/badcase-candidates")
def candidates(ctx: WsCtx = Depends(get_workspace), s=Depends(get_session)):
    q = select(Feedback).where(Feedback.workspace_id == ctx.workspace_id, Feedback.status == "new",
        or_(Feedback.rating == "down",
            Feedback.payload["edit_ratio"].as_float() >= 0.3))
    rows = sorted(s.exec(q).all(), key=lambda f: f.payload.get("edit_ratio", 1.0), reverse=True)
    return rows[:50]

class PromoteIn(BaseModel):
    desensitized: bool
    must_cover: list[str] = []
    notes: str = ""

@router.post("/v1/eval/badcase-candidates/{fid}/promote")
def promote(fid: uuid.UUID, body: PromoteIn, ctx: WsCtx = Depends(require_role("owner")), s=Depends(get_session)):
    if not body.desensitized:
        raise HTTPException(400, "必须确认已脱敏")
    fb = WorkspaceRepo(s, ctx).get(Feedback, fid)
    if fb is None:
        raise HTTPException(404, "not found")
    fb.status = "promoted"
    fb.payload = {**fb.payload, "case": {"must_cover": body.must_cover, "notes": body.notes}}
    s.add(fb); s.commit()
    return {"ok": True}
```

```python
# scripts/export_regression.py —— 本地执行，读 DB 中 promoted 且未导出的记录
# 1) 取 run 的 requirement（AgentRun / checkpoint）  2) 组装 {"id": "spb-r-0xx", ..., "tags": ["regression"]}
# 3) 追加到 eval/datasets/scenario_spb.jsonl  4) 把 payload.exported=true
# 运行后必须：git diff eval/datasets/scenario_spb.jsonl → 逐条再过脱敏清单 → 再提交
```

### Step 4 · EvalRun 写入 + 历史回填（P0）

runner 末尾追加（Day64 的 `main()`）：

```python
from app.db.session import session_scope
from app.db.models import EvalRun
version = subprocess.check_output(["git", "describe", "--tags", "--always"], text=True).strip()
with session_scope() as s:
    s.add(EvalRun(workspace_id=EVAL_WS, suite="scenario_spb", version=version,
                  metrics={"pass_rate": rate, **dims}, report_path=str(report)))
```

回填：写一个一次性脚本把 `eval/reports/` 中 v0.5（RAG）与 v1.0（Agent）基线的关键指标插入 EvalRun（suite 分别为 rag / agent），供 W22 的趋势展示使用。

### Step 5 · 页面（P1，样板可让 AI 生成）

- `BadcaseQueuePage.tsx`：表格列「运行时间 / 需求摘要 / edit_ratio / 删 / 改 / 增 / 👎」+ 操作「查看运行（跳时间线）/ 提升 / 忽略」；提升弹窗必须勾选「已脱敏」并可填 must_cover。
- `EvalTrendPage.tsx`：按 suite 分组的折线（可用已有图表库；没有就用简单 SVG 或表格），x 轴 version，y 轴 pass_rate。

### Step 6 · P3 评测报告 v1 + 发布（P0）

`eval/reports/20261201-p3-eval-v1.md`：

```markdown
# P3 评测报告 v1（v1.3.0）

## 1. 离线：场景评测（20 条）—— 通过率 **，维度均分 …，judge 一致率 **

## 2. 在线：隐式反馈（W18 以来 ** 次审批）—— 平均 edit_ratio **；最常删除的任务类型 **；估时平均偏差 ** h

## 3. Badcase：候选 ** 条 → 提升 ** 条 → 已进回归集 \_\_ 条

## 4. 结论与下一步（不超过 3 条，进入 W21/W22）
```

```bash
git add apps/api apps/web/src scripts/export_regression.py eval/reports/20261201-p3-eval-v1.md eval/datasets
git commit -m "feat(eval): implicit edit feedback, badcase promotion flow and eval run trend"
git push && git tag -a v1.3.0 -m "v1.3.0: scenario eval + online feedback loop" && git push origin v1.3.0
```

推 tag 后观察 Day63 的自动部署与冒烟。

## 7. 概念自检（不看资料，口述，附答案）

1. 隐式反馈相比 👍👎 的优点和缺点？（答：优点是无打扰、覆盖率高、信息更具体；缺点是噪声大——个人偏好也会编辑，需人工确认）
2. 为什么 promote 需要「已脱敏」确认且仅 owner 可操作？（答：线上数据可能含敏感信息，数据集会公开；最小权限降低误操作）
3. 为什么不让 API 直接写数据集文件？（答：生产容器内的文件不是 git 工作区；数据集变更必须可审查、可追溯，由人提交）
4. edit_ratio 阈值为什么不是固定真理？（答：初始经验值；应结合人审结果调整，使候选队列的 precision 可接受）
5. EvalRun 为什么要存 version？（答：把指标与代码版本绑定，才能做趋势与回归归因）

## 8. 对 DA-01 的贡献

WorkPilot 形成了完整的「使用 → 反馈 → badcase → 回归」数据飞轮（蓝图 §4 闭环中的「反馈 / 评测 / 优化」环节在 P3 场景上落地）。v1.3 让「越用越好」有了机制和证据，也是 Pro Kit「评测模板」的核心组成。

## 9. 求职映射（D 线）

- 岗位能力：反馈系统设计、数据飞轮、评测基础设施、AI 产品指标。
- 对应岗位：AI Full-Stack Engineer、AI Product Engineer、AI Engineer。
- 简历 bullet 草稿：「设计隐式反馈信号（审批编辑 diff → edit_ratio），构建 badcase 候选 → 人工确认 → 回归用例闭环，上线后 ** 天沉淀 ** 条回归用例」
- 面试可能问：
  1. 你怎么知道线上 AI 质量在变差？——要点：隐式/显式反馈趋势、离线回归、成本延迟监控、抽样人审。
  2. 线上数据进评测集有什么风险？——要点：隐私/合规、分布偏移、过拟合回归集；对策：脱敏确认、分层抽样、保留 base 集。

## 10. 卡住时的处理

| 现象                                               | 处理                                                                                                       |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| JSONB 字段 `payload["edit_ratio"].as_float()` 报错 | 用 `sa.cast(Feedback.payload["edit_ratio"].astext, sa.Float)`；或先查全部再在 Python 过滤（数据量小）      |
| 拿不到原始草案                                     | 从 `graph.get_state(cfg).values["breakdown"]` 读（resume 前读取）；或在 human_review 前写 AgentStep 存草案 |
| 编辑改了标题导致 diff 判为「删+增」                | 接受该近似（记录在报告局限性）；P2 再按相似度匹配                                                          |
| 迁移把 Feedback.message_id 改可空失败              | 手写 `op.alter_column(..., nullable=True)`，autogenerate 不一定识别                                        |
| 趋势页没时间做                                     | 报告里放表格 + 截图，页面进 Backlog（验收用报告代替）                                                      |
| 自动部署失败                                       | 按 Day63 runbook 查看 workflow 日志；先手动 `deploy.sh v1.3.0`                                             |

## 11. 产出记录（执行时填写）

- implicit_edit 记录数：**；平均 edit_ratio：**
- 候选 ** / 提升 ** / 导出 \_\_
- EvalRun 点数：**（含回填 **）
- v1.3.0 部署：成功 / 失败（原因 \_\_）
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day66 · W21 Task 1「威胁建模 + 攻击集」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（diff 入库 / promote + 导出 / EvalRun / 报告 / tag）。
