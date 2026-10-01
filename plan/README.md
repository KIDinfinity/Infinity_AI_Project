# plan — 多项目计划执行目录

> 本目录是**所有 project 的计划执行工作空间**。每个 project 有独立的子目录，包含各自的阶段/周/日计划。
> 历史/总计划在 `history/`，本目录只放当前可执行、可验收、可持续迭代的计划。

---

## 1. 项目列表

| 项目目录 | 代号 | 描述 | 状态 |
| -------- | ---- | ---- | ---- |
| [plan_ai/](plan_ai/) | WorkPilot | 半年 AI 智能解决方案孵化（DA-01） | 执行中（W1） |

> 新增 project 时：在 `plan/` 下新建 `plan_<name>/`，按 `phase_XX/week_XX/dayNN_YYYYMMDD/` 三级结构组织。

---

## 2. 通用目录结构

每个 project 子目录遵循统一结构：

```text
plan/<project>/
  README.md              ← 该 project 的总计划/路线图
  phase_01/
    README.md            ← 阶段目标、版本推进、进出条件
    week_01/
      README.md          ← 本周模块、每日安排、验收
      TASKS.md           ← 本周任务细节
      day01_YYYYMMDD/
        PLAN.md          ← 当天可直接执行的步骤
        draft.md         ← 执行笔记/勾选结果
      day02_YYYYMMDD/
        ...
    week_02/
      ...
  phase_02/
    ...
```

---

## 3. 全局共享文件

| 文件 | 用途 |
| ---- | ---- |
| [plan_ai/DA01_TARGET_ASSET.md](plan_ai/DA01_TARGET_ASSET.md) | DA-01（WorkPilot）目标数字资产蓝图 |
| [CHANGELOG.md](CHANGELOG.md) | 计划演化记录 |

---

## 4. Agent 执行约定

Agent 执行任务时**按最小必要上下文逐层加载**：

```text
GLOBAL_CONTEXT.md                         → 长期原则 / 防偏航
PROJECT_CONFIG.md                         → 路径 / 当前状态
plan/<project>/README.md                  → 该 project 总路线
plan/<project>/phase_XX/README.md         → 阶段目标
plan/<project>/phase_XX/week_XX/README.md → 本周模块
plan/<project>/phase_XX/week_XX/TASKS.md  → 本周任务细节
plan/<project>/phase_XX/week_XX/dayNN_*/PLAN.md → 当天步骤
```

不要一次性读取全部文件。

### 每日文件约定

- `PLAN.md`：当天计划（计划生成后不随意改动）。
- `draft.md`：执行时自己的笔记 / 勾选结果。
- 当天未完成：次日 PLAN 不改，只在 `draft.md` 记录「顺延项」，并优先完成 P0。

---

## 5. 计划演化机制

计划变化记录在 `plan/CHANGELOG.md`：为什么改、改了什么、哪一周受影响、DA-01 / 目标资产是否变化。
