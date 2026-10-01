# Day 57 · 2026-11-23 · Week 16 Task 3：简历 v1 + 面试题 + Phase 2 复盘

## 0. 今天只做一件事

把 Phase 2 的成果转成求职资产并正式收尾：用评测报告里的真实数字写两版简历 v1（ai-fullstack、ai-engineer），面试题新增 15 道使总数 ≥ 25，逐项勾选 phase_02 README 第 8 节，写 Phase 2 复盘，并把 `PROJECT_CONFIG.md` 推进到阶段三 · 第 17 周。

不碰：投递简历（W24）、第三版 Frontend 简历（W24）、phase_03 的任何开发、新功能。

## 1. 资产锚点

- 构建模块：M13.3 简历（v1）、M13.4 面试题库（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：v1.0 / P2 收尾（Phase 2 验收）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：P1+P2 的数字被沉淀为两版简历 bullets 与 ≥ 25 道带项目证据的面试题；Phase 2 验收结论（8 项 PASS/FAIL）有据可查
- 今日 AI 实际应用：用 AI 对照 JD 改写 bullet 措辞与生成面试追问，自己负责每个数字的真实性与回答要点

## 2. 起点（前置确认）

- 已有：`eval/reports/20261121-v1.0.md`、`docs/portfolio/p1.md`、`p2.md`；W10 简历 v0（`career/resume/` 三版骨架）；`interview-questions.md`（约 10 道 RAG + W13 5 道 MCP）；`job-market.md` 3 轮
- 需确认：

```bash
cd ~/lab/projects/career
ls resume/ && grep -c "^### " interview-questions.md     # 当前题数（按你的标题格式）
cd ~/lab/workpilot && git tag | grep v1.0.0 && ls eval/reports/ | tail -5
ls ~/lab/projects/product-lab/reviews/ 2>/dev/null || mkdir -p ~/lab/projects/product-lab/reviews
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `resume/ai-engineer-v1.md`、`resume/ai-fullstack-v1.md` 完成；每版 P1、P2 各 ≥ 3 条量化 bullet，所有数字能在报告中找到
- [ ] `interview-questions.md` 新增 15 道（Agent 4 / Tool 3 / MCP 2 / Eval 3 / Observability 3），总数 ≥ 25，每题有要点 + 项目证据
- [ ] phase_02 README 第 8 节 8 项全部标 PASS/FAIL 并附证据路径；FAIL 项有补救计划
- [ ] `product-lab/reviews/phase02-review.md` 完成
- [ ] `PROJECT_CONFIG.md` 当前状态更新为阶段三 · 第 17 周；Week 16 周复盘已写；各仓库已提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                                     |
| ----------- | ------ | ---------------------------------------------------------------------------------------- |
| 0–10 min    | P0     | 数字清单（从报告抄，不凭记忆）                                                           |
| 10–45 min   | P0     | ai-engineer 简历 v1（P1） + ai-fullstack v1（P1：可在 ai-engineer 基础上调整顺序与侧重） |
| 45–75 min   | P0     | 15 道面试题                                                                              |
| 75–90 min   | P0     | phase_02 第 8 节逐项勾选                                                                 |
| 90–110 min  | P0     | phase02-review.md                                                                        |
| 110–120 min | P0     | PROJECT_CONFIG + 周复盘 + 提交                                                           |

时间不足时最低保留：ai-engineer 简历 v1 + 面试题 ≥ 25 + 第 8 节勾选 + PROJECT_CONFIG；ai-fullstack 版与完整复盘顺延到 Day58 开头 30 分钟。

## 5. 今日学习（只学完成任务必须的）

- **Bullet 公式**：动词 + 做了什么（技术与设计）+ 可量化结果 + 规模/约束，例如「设计…实现…，使…从 A 提升到 B（N 条评测）」。
- **两版差异**：ai-engineer 版先讲 RAG / Agent / Eval / MCP / Observability；ai-fullstack 版先讲端到端交付（React AI UX：流式、引用、时间线、审批卡片、Trace 瀑布图、Ops 看板）+ 后端 + 部署。
- **面试题答案结构**：概念一句话 → 关键取舍 → 我在 WorkPilot 中怎么做 → 数字/结果 → 局限与下一步。
- **阶段复盘看偏差不看感受**：目标 vs 实际、时间投入、范围扩张、指标差距、下一阶段调整。
- 资料：自己的 `docs/portfolio/p1.md`、`p2.md`、`eval/reports/*.md`、`career/job-market.md`（不需要外部资料）

## 6. 执行步骤

### Step 1 · 数字清单（只从文件抄）

| 指标                                                    | 值           | 来源文件                                |
| ------------------------------------------------------- | ------------ | --------------------------------------- |
| RAG hit@5 / 引用正确率 / 拒答正确率（50 题）            | \_\_         | `eval/reports/20261121-v1.0.md`         |
| RAG P95 / 单次成本                                      | \_\_         | 同上 / Ops                              |
| Agent 任务成功率 / 工具选择准确率 / 平均步数（30 任务） | \_\_         | 同上                                    |
| Agent P95 / 平均成本                                    | \_\_         | 同上                                    |
| 修复前后提升（W14）                                     | ** → **      | `eval/reports/20261117-agent-v0.9.1.md` |
| judge 人工一致率                                        | \_\_/8       | `eval/calibration/`                     |
| 未经审批写操作 / 注入用例                               | 0 / 8/8      | 测试 + `run_security_eval.py`           |
| CI eval-smoke 单次成本 / 耗时                           | ¥** / ** min | Day51 报告                              |
| 自用会话数（真实使用日志）                              | \_\_         | `Conversation` / `AgentRun` 表计数      |

### Step 2 · 简历 v1（AI 改写措辞，数字与事实自己负责）

`resume/ai-engineer-v1.md` 项目段骨架：

```markdown
## WorkPilot —— 可私有部署的研发工作 AI 助手平台（个人项目，开源） 2026.09–至今

技术栈：Python 3.12 / FastAPI / LangGraph / Qdrant / MCP / React + TS / Docker / Gitea Actions

- 【P1 RAG】实现文档导入→结构化分块→bge-m3 向量化→混合检索→带引用回答的 RAG 链路，构建 50 题评测集与 LLM-judge，hit@5 达 **、引用正确率 **、库外拒答率 \_\_。
- 【P1 交付】Docker Compose + Caddy 云端部署，CI 自动测试，备份恢复演练 < \_\_ 分钟。
- 【P2 Agent】基于 LangGraph 构建 plan/act/decide 工作流（checkpoint、重试降级、会话+长期记忆），写操作 interrupt 人工审批，未经审批写操作 0 次。
- 【P2 MCP】基于官方 MCP SDK 实现 MCP Server（stdio/HTTP+token）与 Client，VS Code / Claude Desktop 内直接查询团队知识。
- 【P2 Eval】设计 30 任务 Agent 评测集与轨迹级评测器 + CI 回归门禁，基于失败分类优化使任务成功率 **→**、工具选择准确率 \_\_。
- 【P2 Production】自研 Trace/Span、成本账本与日预算守卫（80% 降级/100% 熔断）、限流与 Guardrail v0，P95 **s、平均成本 ¥**/任务。
```

`resume/ai-fullstack-v1.md`：同一项目，调整为「端到端交付」顺序，增加前端 bullet，例如：

```markdown
- 【AI UX】React + TS 实现流式对话与引用面板、Agent 步骤时间线 + 审批卡片、Trace 瀑布图、Ops 看板（recharts），SSE 首字延迟 \_\_s。
```

两版都保留 5 年全栈/前端工作经历段（只写通用能力，不写公司机密），技能段按 `capability-matrix.md` 更新。

### Step 3 · 新增 15 道面试题（每题：问题 / 要点 3–5 条 / 我的证据）

| #   | 类别    | 题目                                                               |
| --- | ------- | ------------------------------------------------------------------ |
| 1   | Agent   | ReAct、Plan-and-Execute、固定工作流的区别？WorkPilot 怎么选？      |
| 2   | Agent   | LangGraph 的 State / Node / Edge / Checkpointer 分别解决什么问题？ |
| 3   | Agent   | Human-in-the-loop 如何实现？interrupt 与 resume 的状态如何保存？   |
| 4   | Agent   | 会话记忆与长期记忆怎么设计？上下文太长怎么办？                     |
| 5   | Tool    | 工具 schema 和 description 怎么设计才能提高选择准确率？            |
| 6   | Tool    | 工具调用失败、超时、返回超长时怎么处理？                           |
| 7   | Tool    | 如何防止 Agent 过度代理（Excessive Agency）？                      |
| 8   | MCP     | MCP 的能力协商与生命周期（initialize → list → call）是怎样的？     |
| 9   | MCP     | 如何把外部 MCP 工具安全地接入自己的 Agent？                        |
| 10  | Eval    | Agent 评测有哪些指标？轨迹评测与结果评测的区别？                   |
| 11  | Eval    | LLM-as-a-judge 的偏差与校准方法？                                  |
| 12  | Eval    | 评测怎么接入 CI？如何避免 flaky 与成本失控？                       |
| 13  | Obs     | LLM 应用的 Trace 要记录哪些属性？和 OpenTelemetry 的关系？         |
| 14  | Obs     | 如何做成本控制与预算告警？                                         |
| 15  | Obs/Sec | 间接 Prompt Injection 的防护与你的 Guardrail 设计？                |

完成后统计：`grep -c "^### " interview-questions.md` ≥ 25。

### Step 4 · phase_02 README 第 8 节逐项勾选

在本计划仓库 `plan/phase_02/README.md` 第 8 节逐项打勾，并在每项后追加证据：

| 验收项                          | 证据                                           |
| ------------------------------- | ---------------------------------------------- |
| v1.0 tag + 云端更新             | GitHub Release 链接、`/health` 输出            |
| Agent 30 任务报告 5 项数值      | `eval/reports/20261121-v1.0.md`                |
| 未经审批写操作 = 0（测试证明）  | 测试文件路径 + 报告中 unapproved_writes        |
| IDE 中 MCP 调用（录屏）         | 视频链接                                       |
| Trace 页面明细与成本            | 截图 `docs/assets/p2-trace.png`                |
| `make eval` 在 CI、回归会失败   | CI 运行链接 + Day51 退化演示截图               |
| P2 作品集 5 件套                | README / architecture / Demo / 报告 / 文章链接 |
| 简历 v1、JD ≥ 3 次、面试题 ≥ 25 | 文件路径 + 题数                                |

FAIL 项写清：缺什么、补救时间（只能占用 W17 的 P1 时间，不挤占 P0）。

### Step 5 · `~/lab/projects/product-lab/reviews/phase02-review.md`

```markdown
# Phase 2 复盘（W9–W16 · 10-31 → 11-23）

## 1. 目标 vs 实际（版本时间线 v0.6 → v1.0，是否按周达成）

## 2. 指标 vs DA01 §11（P2 Agent / P2 安全，差距与原因）

## 3. 做对了什么（≤3，例如：先评测后优化、MCP 适配层解耦）

## 4. 浪费 / 范围扩张 / 无效学习（如实写，附花费时间）

## 5. 时间投入（实际总小时 / 计划；超时最多的 3 天及原因）

## 6. 合规（是否有公司信息进入外部 LLM 或公开仓库：是/否；检查记录）

## 7. 真实使用（自用会话数、最有用的场景、最没用的功能）

## 8. 商业化信号（Star / Discussions / 文章阅读，只记录不解读过度）

## 9. 求职进展（简历 v1、JD 趋势、面试题、能力矩阵变化）

## 10. 对 phase_03 的输入与调整（主场景包候选、需要补的 P0、计划变更 → 写入 plan/CHANGELOG.md）
```

### Step 6 · PROJECT_CONFIG + 周复盘 + 提交

本计划仓库根目录 `PROJECT_CONFIG.md`「2. 当前状态」更新：

| 配置项     | 新值                                                                                               |
| ---------- | -------------------------------------------------------------------------------------------------- |
| 当前阶段   | 阶段三 · 生产化与求职（第 17–26 周）                                                               |
| 当前周     | 第 17 周                                                                                           |
| DA-01 状态 | WorkPilot v1.0（P2）已发布：Agent + MCP + Eval + Observability；下一步 P3 主场景包 + 安全 + 多空间 |

填写 `plan/phase_02/week_16/README.md` 第 11 节。若复盘导致计划调整，在 `plan/CHANGELOG.md` 记录。

```bash
cd ~/lab/projects
git add career product-lab/reviews
git commit -m "docs(career): resume v1 (ai-engineer, ai-fullstack), interview questions >=25, phase 2 review"
git push
# 本计划仓库（PROJECT_CONFIG、phase_02 README、week_16 README）按你的习惯提交
```

## 7. 概念自检（不看资料，口述，附答案）

1. 用 30 秒介绍 WorkPilot P2。（答：可私有部署的研发 Agent 平台；LangGraph 规划 + 工具调用 + 写操作审批 + MCP 进 IDE；30 任务评测成功率 \_\_、CI 门禁、Trace 与预算守卫，未审批写 0 次）
2. 简历数字被追问「怎么算的」，你怎么答？（答：说清数据集规模与构造、指标口径、模型与 temperature、judge 校准一致率、报告文件可公开查看）
3. ai-engineer 与 ai-fullstack 简历的核心差异？（答：前者突出 LLM 工程深度（RAG/Agent/Eval/MCP/Obs），后者突出端到端交付与 AI UX，同一项目不同切面）
4. Phase 2 最大的偏差是什么？（答：按复盘如实回答，并给出 phase_03 中的调整动作）
5. 为什么阶段验收的 FAIL 项不能挤占下阶段 P0？（答：会导致连锁延误；补救只用 P1 时间，必要时降级为 Backlog 并在 CHANGELOG 记录）

## 8. 对 DA-01 的贡献

Phase 2 正式闭环：DA-01 v1.0 的工程成果被转换为可投递的简历 v1 与可脱稿的面试题库，阶段验收给出客观结论，复盘为 phase_03（主场景包、认证与多空间、安全加固、v2.0）提供输入，`PROJECT_CONFIG.md` 状态推进确保后续计划加载正确上下文。

## 9. 求职映射（D 线）

- 岗位能力：项目量化表达、面试准备、复盘与持续改进
- 对应岗位：AI Engineer / AI Agent Engineer / AI Full-Stack Engineer
- 简历 bullet 草稿：见 Step 2（两版共 ≥ 12 条，数字全部来自报告）
- 面试可能问：
  - 你在项目里最大的失败是什么？（要点：选一个真实 badcase 或范围扩张，讲发现 → 根因 → 修复 → 数字 → 学到的规则）
  - 为什么从前端转 AI 工程？你的优势是什么？（要点：5 年全栈交付经验 + AI UX（流式、审批、可视化）+ 已有可验证的 RAG/Agent/Eval 作品；不是只会调 API）

## 10. 卡住时的处理

| 现象                  | 处理                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------ |
| 某个数字找不到来源    | 不写该数字，改为定性描述或重跑对应评测；绝不估填                                     |
| bullet 写得像功能列表 | 每条加「为什么 / 结果」：删掉形容词，补一个数字或对比                                |
| 面试题写不出要点      | 先写「我在 WorkPilot 中怎么做的」，再补概念；概念题可让 AI 出初稿，自己对照代码改    |
| 阶段验收多项 FAIL     | 按影响排序，只把 P0 缺口列入 W17 P1 时间；其他降级进 Backlog，并写 CHANGELOG         |
| 复盘写成流水账        | 只回答模板 10 个问题，每个 ≤ 5 行                                                    |
| 时间不够              | 先保证 ai-engineer 简历 + 题数 + 第 8 节 + PROJECT_CONFIG；其余 Day58 开头 30 分钟补 |

## 11. 产出记录（执行时填写）

- 两版简历文件路径 / bullet 数：\_\_\_\_
- 面试题总数：\_\_\_\_
- phase_02 第 8 节结果（PASS x / 8）：\_\_\_\_
- FAIL 项与补救计划：\_\_\_\_
- Phase 2 实际总投入小时：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 16 DONE → Phase 2 DONE → 明天进入 Day58（phase_03 · W17 Task 1：P3 问题定义 8 要素）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
