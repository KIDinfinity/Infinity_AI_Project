# Day 74 · 2027-03-15 · Week 25 Task 1：面试题库 + 系统设计

## 0. 今天只做一件事

整理面试题库 ≥ 30 题（分六大类，每题要点答案 + WorkPilot 证据链接），完成 2 道系统设计题（企业 AI 知识库 + AI 研发 Agent），含 mermaid 架构图与关键权衡。

不碰：STAR 故事（Day75）、模拟面试（Day75）、新知识学习（只整理已有知识）、WorkPilot 代码。

## 1. 资产锚点

- 构建模块：M13.4 面试准备（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：—（引用 v0.5 / v1.0 / v2.0 证据）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：WorkPilot 的每个技术决策、评测数字、架构权衡都变成可口头表达的面试答案
- 今日 AI 实际应用：用 AI 对每道题的要点答案做「面试官视角审阅」——这个回答能让面试官满意吗？缺什么？

## 2. 起点（前置确认）

- 已有：W16 面试题 ≥ 25、W24 JD 高频汇总、Eval v2 报告、安全报告、`docs/architecture-v2.md`、ADR 0001–0007、`docs/portfolio/p1.md p2.md p3-notes.md`。
- 需确认：

```bash
cd ~/lab/projects && git pull
ls career/interview/ 2>/dev/null || mkdir -p career/interview
wc -l career/interview/questions.md 2>/dev/null || echo "需新建"
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `career/interview/questions.md` ≥ 30 题，分六大类，每题有 3–5 bullet 要点答案
- [ ] ≥ 50%（即 ≥ 15 题）有 WorkPilot 证据链接（`eval/reports/...`、`docs/...`、代码文件路径）
- [ ] `career/interview/system-design-1.md`：企业 AI 知识库，含 mermaid 架构图 + ≥ 3 个关键权衡
- [ ] `career/interview/system-design-2.md`：AI 研发 Agent，含 mermaid 架构图 + ≥ 3 个关键权衡
- [ ] 每道系统设计题有自问自答的「面试官追问」≥ 2 个

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                              |
| ----------- | ------ | ------------------------------------------------- |
| 0–10 min    | P0     | 确定 30 题清单（W16 题库 + JD 高频 → 补缺）       |
| 10–50 min   | P0     | AI 基础 + RAG + Agent 类（约 15 题）要点答案      |
| 50–80 min   | P0     | Engineering + System Design + STAR 类（约 15 题） |
| 80–100 min  | P0     | 系统设计 ×1：企业 AI 知识库（架构图 + 权衡）      |
| 100–115 min | P0     | 系统设计 ×2：AI 研发 Agent（架构图 + 权衡）       |
| 115–120 min | P0     | 提交                                              |
| 顺延        | P2     | 英文版答案、更多追问 → W26                        |

时间不足时最低保留：AI 基础 + RAG + Agent 三类（约 20 题）+ 系统设计 ×1。

## 5. 执行步骤

### 5.1 确定 30 题清单（0–10 min）

从 W16 题库出发，对照 W24 JD 高频汇总，补足缺失类别。六大类分配建议：

| 类别          | 题数 | 来源                                                  |
| ------------- | ---- | ----------------------------------------------------- |
| AI 基础       | 5    | LLM/Embedding/Transformer/Token/Temperature           |
| RAG           | 6    | Chunk/Retrieval/Rerank/Vector DB/Hybrid/Evaluation    |
| Agent         | 6    | Tool Calling/Workflow/Memory/State/Planning/Guardrail |
| Engineering   | 5    | API/Docker/DB/Cache/CI-CD                             |
| System Design | 3    | 知识库/Agent/自选                                     |
| STAR/行为     | 5    | 冲突/失败/学习/领导力/自选                            |

### 5.2 写要点答案（10–80 min）

每题格式：

```markdown
### Q{序号}. {题目}（{类别}）

**要点**：

- {bullet 1}
- {bullet 2}
- {bullet 3}

**证据**：[{文件路径或链接}](...)
```

关键原则：

- 每个 bullet 控制在 1–2 句，面试时能自然展开
- 数字优先：「50 题种子集」>「很多测试用例」
- 证据链接指向具体文件，不是目录

### 5.3 系统设计 ×2（80–115 min）

每道系统设计题格式：

````markdown
# 系统设计：{题目}

## 需求澄清（5 问）

1. ...
2. ...

## 架构图

```mermaid
...
```
````

## 关键组件

- ...
- ...

## 关键权衡

1. {选择 A vs B} → 选 A，因为...
2. ...

## 面试官追问（自问自答）

1. Q: ... → A: ...
2. Q: ... → A: ...

````

### 5.4 提交（115–120 min）

```bash
cd ~/lab/projects
git add career/interview/
git commit -m "day74: 面试题库 ≥30 + 系统设计 ×2"
git push
````

## 6. 概念自查（做完后口头回答）

- [ ] 为什么 RAG 评测用 LLM-judge 而不是人工？（答：人工不可规模化；LLM-judge 经 10 条人审校准一致率 ≥ 0.8 后可作为自动化门禁；人工用于 Badcase 深度分析）
- [ ] Agent 的 Memory 和 RAG 的 Retrieval 有什么区别？（答：Memory 是用户/会话级别的偏好与历史；Retrieval 是知识库级别的语义搜索；前者存 SQLite/Postgres，后者走 Qdrant）
- [ ] 系统设计中为什么用 Qdrant 不用 Pinecone？（答：自托管 → 数据不出环境 + 零额外成本 + Docker Compose 一键部署；Pinecone 是托管服务，适合不想运维的团队）

## 7. DA-01 贡献

- 求职线（D）：面试题库是半年技术能力的「口头化」输出，直接服务于 offer 转化
- 工程线（B）：系统设计题倒逼架构表述清晰化，可能发现 `docs/architecture-v2.md` 的表述问题

## 8. 求职映射

- 本周能力：技术表达、系统设计沟通
- 面试题（本周即产出）：
  1. 你做的 RAG 系统检索准确率怎么算？（答：50 题种子集，MRR@5 / Recall@5，基线报告在 `eval/reports/20261026-rag-baseline.md`）
  2. Agent 的工具调用失败怎么处理？（答：重试策略 + 降级 + 错误透传给用户 + 记录到 Badcase 池）
  3. 你的系统怎么保证多租户数据隔离？（答：Workspace 级别隔离 + JWT claim 校验 + 自动化测试验证）

## 9. 故障排查

| 症状                     | 排查                                      |
| ------------------------ | ----------------------------------------- |
| W16 题库找不到           | `find ~/lab -name "questions.md" -type f` |
| 证据链接指向的文件不存在 | 用实际存在的报告路径；没有报告的数字不写  |
| mermaid 图渲染不出来     | 用 https://mermaid.live 验证语法          |
| 某道题完全没思路         | 标记 `[TODO]`，先跳过，最后用 AI 生成初稿 |

## 10. 输出记录（完成后填写）

```text
题库总数：___
各类数量：AI基础__ / RAG__ / Agent__ / Engineering__ / System Design__ / STAR__
有证据链接的题目数：___
系统设计题：___
未完成 + 原因：___
```

## 11. 完成标准

- [ ] `questions.md` ≥ 30 题
- [ ] `system-design-1.md` 含架构图 + ≥ 3 权衡
- [ ] `system-design-2.md` 含架构图 + ≥ 3 权衡
- [ ] Git 已提交
