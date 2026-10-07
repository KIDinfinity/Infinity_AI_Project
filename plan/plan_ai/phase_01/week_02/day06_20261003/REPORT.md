# Day 06 · 执行报告（2026-10-03）

对应 `PLAN.md`；产出代码仓库：`~/lab/projects/career/`（commit `ad91d05`，已 push 到 `origin/main`）。

## 一、逐步执行记录

| Step | 内容 | 结果 |
| --- | --- | --- |
| 1 | 建 `career/` 骨架 | ✅ `career/{README.md,resume/README.md,job-market.md,capability-matrix.md,jd-skills.jsonl,interview-questions.md}` + 新增 `tally.py` |
| 2 | 收集 10 条 JD | ✅ 10 条，来源猎聘（Boss 需登录、拉勾有滑块、LinkedIn 返回海外岗，均不可用） |
| 3 | AI 抽取技能 → `jd-skills.jsonl` | ✅ 10 行合法 JSON，归一化到 30 项词表，未覆盖技能加 `NEW:` 前缀 |
| 4 | 跑统计 | ✅ `python3 career/tally.py` 输出频次表（10 条 JD / 49 个不同技能） |
| 5 | 填矩阵 + Top-12 + 差距清单 | ✅ `capability-matrix.md` 7 列填满，Top-12 齐全，差距清单 4 项 |
| 6 | 提交 | ✅ `git commit -m "docs(career): add capability matrix v1 from 10 JDs"` + push |
| P1 | 面试题反推 | ✅ `interview-questions.md` 6 题（只写题，不写答案） |

## 二、产出记录（PLAN §11）

- JD 条数 / 公司类型分布：**10 条**；传统行业数字化（制造/基金/租赁/航空/医药）5 条、中厂 2 条、创业 2 条、大厂 1 条 → 覆盖 4 类（要求 ≥3）
- 出现次数 Top-5：**RAG 10/10（必需 9）> Python 9/10（必需 8）> LangChain 6/10 > Tool Calling/Agent 6/10 > Vector DB 6/10**
- AI 抽取抽查错误率：**6 / 32 项 ≈ 19%**（抽查 JD-02、JD-07、JD-09）
  - JD-07 全对
  - JD-02：漏 `Vue`；`SQLAlchemy` 被归为 `SQL/Postgres` 过宽；`SQLAlchemy` 未标 `NEW:`
  - JD-09：漏 3 项加分（科学计算软件集成 / Windows COM / 汽车行业背景）
- Top-12 中由 WorkPilot 证明的项数：**11 / 12**（唯一未覆盖：LlamaIndex；SQL/Postgres 为部分证明，只有 SQLite 会话历史，无 pgvector）
- 差距最大的 3 项：**Tool Calling/Agent（0→3，差距 3）> RAG（0→3，差距 3）> Vector DB（0→2，差距 2）**（第 4 项 LangChain/LangGraph 0→2）
- 卡点记录：Boss 直聘 / 拉勾 / LinkedIn 均不可用（登录、滑块、地域错误）→ 改用猎聘列表页 + 详情页；`NEW:分布式/高并发` 与 `NEW:分布式系统`、`NEW:工作流编排` 与 `NEW:Workflow 编排` 实为同一技能被拆成低频项，即 Day11 Structured Output + 词表约束要解决的问题
- 用时：约 115 分钟（P0 全完成，P1 完成，P2 薪资区间统计未做）

## 三、当日核心发现

1. **RAG 是唯一 10/10 出现的能力**（必需 9），且 WorkPilot M2（W4–W5）直接证明 → 路线正确，W4 不能延期。
2. **Tool Calling/Agent 6/10 且全部为必需**，是第二大缺口，对应 M6/M7（W9–W12）。
3. **LangChain 6/10 全是必需**，蓝图选 LangGraph（同生态）可直接覆盖，不必额外学 LangChain 本体。
4. **LlamaIndex 4/10 出现但不在蓝图** → 记入待观察，不为它排学习（防偏航）；同生态能力可迁移。
5. **AI 抽取错误率 19% 全部集中在「漏项」与「归一过宽」**，没有编造 → Day11 的 Pydantic 校验 + 白名单词表 + 必需/加分分类提示词是最小修复路径。
6. Fine-tuning 0/10、K8s 1/10 → 蓝图 Non-goals 得到市场数据支持，可放心不做。

## 四、验收对齐（PLAN §3）

- [x] `career/` 下 4 个必需文件 + `resume/README.md` 存在
- [x] `grep -c '^## JD-' career/job-market.md` = 10，每条 7 字段齐全（30 处字段标记校验通过）
- [x] `career/jd-skills.jsonl` 10 行合法 JSON，`tally.py` 输出频次表
- [x] 矩阵 7 列填满（不做项写明理由）
- [x] 差距清单 4 项（≥3），计划周与蓝图附录 A 核对一致（M2=W4–5、M6=W9、M7=W10–12）
- [x] 已 push（`origin/main` = `ad91d05`）

## 五、对 DA-01 的贡献

- M13.1「AI 岗位能力矩阵 + JD 追踪」v1 落地，成为后续简历 bullet 与防偏航的唯一数据源。
- 矩阵确立了「每个模块完成 → 更新当前水平 + 证据文件」的闭环。
- 下一次更新：W3 末补齐（如抽到新 JD）+ W9 Day36 常规追踪。

## 六、Day07 前置

- 进入 Day07 Task 2：Python 工具链 + FastAPI 骨架（W2 主线，M1 起步）。
- 今日结论直接支撑 Day11：Structured Output + 词表约束是 JD 抽取错误率 19% 的答案。
