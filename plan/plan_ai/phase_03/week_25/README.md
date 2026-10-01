# Week 25 · 面试准备（Phase 3 · Day74–Day75 · 12-10 → 12-11）

## 1. 本周核心目标

基于 W24 投递反馈与 JD 高频要求，完成面试题库 ≥ 30 道（含 AI 基础 / RAG / Agent / Engineering / System Design / STAR）、2 道系统设计题、3 个 STAR 故事；用 LLM 模拟面试官进行至少 1 轮模拟面试并记录改进点。

## 2. 资产锚点

| 构建模块           | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                        |
| ------------------ | ---------- | ------------------------------------------------------------------------------------ |
| M13.4 面试准备     | —          | 面试题库 ≥ 30 题（每题有要点答案 + WorkPilot 证据链接）；系统设计 ×2 有架构图 + 权衡 |
| M13.3 简历（复用） | —          | 面试中每个 bullet 都能在 30 秒内讲出「背景 → 行动 → 结果 + 数字」                    |

## 3. 为什么这一周存在

- 总计划 §6.6：面试是求职线的最后一环——「能做出东西」和「能讲清楚东西」是两种能力。
- W24 投递后可能收到面试邀约，需要在被问到之前准备好。
- 只有 2 天：Day74 题库 + 系统设计，Day75 STAR + 模拟面试。

## 4. 本周在路线中的位置

```text
上周产出（W24）：三版简历 + 3–5 个岗位投递 + JD 高频汇总
        ↓
本周（W25）：面试题库 ≥ 30 → 系统设计 ×2 → STAR ×3 → 模拟面试 ≥ 1 轮
        ↓
下周输入（W26）：面试反馈（如有）→ 半年复盘；题库与 STAR 作为复盘材料
```

## 5. 每日安排

| Day   | 日期  | Task                        | 当日 P0 产出                           | 模块  | 状态 |
| ----- | ----- | --------------------------- | -------------------------------------- | ----- | ---- |
| Day74 | 12-10 | Task 1：面试题库 + 系统设计 | 题库 ≥ 30 题 + 系统设计 ×2（含架构图） | M13.4 | TODO |
| Day75 | 12-11 | Task 2：STAR + 模拟面试     | STAR ×3 + 模拟面试 ≥ 1 轮 + 改进记录   | M13.4 | TODO |

## 6. 本周必须留下的资产

- `~/lab/projects/career/interview/questions.md`（≥ 30 题，分类 + 要点答案 + 证据链接）
- `~/lab/projects/career/interview/system-design-1.md`（企业 AI 知识库）
- `~/lab/projects/career/interview/system-design-2.md`（AI 客服 Agent 或自选）
- `~/lab/projects/career/interview/star-stories.md`（≥ 3 个 STAR）
- `~/lab/projects/career/interview/mock-interview-log.md`（模拟面试记录 + 改进点）

## 7. 本周验收标准

- [ ] PASS / FAIL：题库 ≥ 30 题，覆盖 AI 基础 / RAG / Agent / Engineering / System Design / STAR 六大类
- [ ] PASS / FAIL：每题有要点答案（3–5 bullet），≥ 50% 的题目有 WorkPilot 证据链接（指向 `eval/reports/`、`docs/`、代码文件）
- [ ] PASS / FAIL：系统设计 ×2 有架构图（mermaid 或手绘照片）+ 关键权衡（如「为什么用 Qdrant 不用 Pinecone」「为什么用 LangGraph 不用 AutoGen」）
- [ ] PASS / FAIL：STAR ×3 覆盖 P1/P2/P3 各一个场景，每个有「情境 → 任务 → 行动 → 结果 + 数字」
- [ ] PASS / FAIL：模拟面试 ≥ 1 轮，有 LLM 面试官反馈 + 改进记录

## 8. 求职映射

- 本周能力：技术面试表达、系统设计沟通、STAR 故事化
- 面试题（本周即产出）：
  1. 你做的 RAG 系统怎么评测？（答：50 题种子集 + LLM-judge + 人审校准一致率 + 回归门禁，详见 `eval/reports/`）
  2. Agent 的写操作安全怎么保证？（答：HITL 审批节点 + 工具策略 + 审计日志 + 20 条攻击用例拦截率 100%）
  3. 为什么从零搭建而不是用 Dify/Coze？（答：Dify 是产品不是能力——我要证明的是能独立设计/实现/评测/交付一个 AI 系统）

## 9. 本周禁止事项

- 不追新论文、不学新技术栈（本周只整理已有知识）。
- 不编造面试答案——所有数字必须来自 WorkPilot 实际报告。
- 不在模拟面试中使用公司内部信息。
- 如果收到真实面试邀约：正常参加，记录到 `applications.md`，不因面试打乱本周节奏。

## 10. 时间不够时（最小保留）

- Day74：题库 ≥ 20 题（AI 基础 + RAG + Agent 三类优先）+ 系统设计 ×1（企业 AI 知识库）
- Day75：STAR ×2（P2/P3）+ 模拟面试 1 轮

## 11. 周复盘（Day75 末尾填写）

- 完成：\_\_\_
- 未完成 + 原因：\_\_\_
- 题库各类数量：AI基础** / RAG** / Agent** / Engineering** / System Design** / STAR**
- 模拟面试发现的主要问题：\_\_\_
