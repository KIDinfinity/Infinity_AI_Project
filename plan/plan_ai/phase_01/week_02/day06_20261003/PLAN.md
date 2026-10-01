# Day 06 · 2026-10-03 · Week 02 Task 1：AI 岗位能力矩阵 v1

## 0. 今天只做一件事

收集 10 条真实 AI 应用方向 JD，统计技能频次，建出 `career/capability-matrix.md`：每项高频能力对应「当前水平 → 目标水平 → WorkPilot 哪个模块证明 → 第几周做」，产出 Top-12 能力与差距清单。

不碰：投简历、写简历正文（W10 起）、为 JD 里出现的新技术安排学习、刷面试题。

## 1. 资产锚点

- 构建模块：M13.1 AI 岗位能力矩阵 + JD 追踪（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5（P1 作品集 + 简历条目，W8）做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：一张矩阵证明「WorkPilot 的每个模块对应哪些 JD 高频能力、覆盖了 10 条 JD 中的几条」；可量化：Top-12 能力中由 WorkPilot 证明的项数 = \_\_\_\_ / 12。
- 今日 AI 实际应用：用 LLM 从 JD 原文抽取结构化技能 JSON（这正是 W3 Day11 Structured Output 要在 WorkPilot 里做的事，今天先手工体验其价值和出错方式）→ 人工抽查纠错。

## 2. 起点（前置确认）

- 已有：`~/lab/projects`（product-lab / ai-lab / infra）；蓝图 §1.1「JD 能力 ↔ 模块」表。
- 需确认：

```bash
cd ~/lab/projects && git pull && ls        # 期望无 career/
python3 --version                          # macOS 自带或 Xcode CLT，用于 10 行统计脚本
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `career/` 下存在 `capability-matrix.md`、`job-market.md`、`interview-questions.md`、`resume/README.md`
- [ ] `grep -c '^## JD-' career/job-market.md` = 10，每条 7 个字段齐全（公司类型 / 岗位 / 城市 / 薪资 / 必需技能 / 加分技能 / 链接）
- [ ] `career/jd-skills.jsonl` 10 行，`python3 career/tally.py` 输出频次表
- [ ] 矩阵 Top-12 能力每行 7 列填满（「不做」的能力在证明模块写「不做（理由）」）
- [ ] 差距清单 ≥ 3 项，并已核对计划周与蓝图附录 A 一致
- [ ] 已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                 |
| ----------- | ------ | -------------------------------------------------------------------- |
| 0–10 min    | P0     | 建 `career/` 骨架                                                    |
| 10–50 min   | P0     | 收集 10 条 JD（每条 ≤ 4 分钟，只复制不细读）                         |
| 50–70 min   | P0     | AI 抽取技能 → `jd-skills.jsonl`，抽查 3 条                           |
| 70–95 min   | P0     | 跑统计 → 填矩阵 → 排 Top-12                                          |
| 95–108 min  | P0     | 差距清单 + 提交                                                      |
| 108–120 min | P1     | `interview-questions.md` 填 5 道从 JD 里反推的题（只写题，不写答案） |
| —           | P2     | 按公司类型 / 城市统计薪资区间                                        |

时间不足时最低保留：6 条 JD + 统计 + Top-10 矩阵 + push（W3 末补齐到 10 条）。

## 5. 今日学习（只学完成任务必须的）

- **必需 vs 加分**：「熟悉 / 精通 / 要求」= 必需；「优先 / 加分 / 有…经验更佳」= 加分；统计时两者都计入出现次数，但差距优先看必需。
- **技能归一化**：「向量数据库 / Milvus / Qdrant / pgvector」统一记为 Vector DB，否则频次被稀释。
- **水平 0–3**：0 没接触；1 跟教程做过；2 在项目中独立实现并能解释原理；3 能做生产级取舍并能讲给面试官 / 写成文章。
- **JD 是反馈数据，不是学习清单**：高频但不在 WorkPilot 里的技能（如微调、K8s），只记录并标注理由，按蓝图 §12 规则 3 处理，不加进本周计划。
- 资料：Boss 直聘 https://www.zhipin.com/ 、拉勾 https://www.lagou.com/ 、LinkedIn https://www.linkedin.com/jobs/ ；映射依据：蓝图 §1.1、§5。

## 6. 执行步骤

### Step 1 · 建 career/ 骨架（P0）

```bash
cd ~/lab/projects
mkdir -p career/resume
printf '# career\n\nD 线：能力矩阵、JD 追踪、简历、面试题。JD 是反馈数据，不是学习清单。\n' > career/README.md
printf '# resume\n\n三版简历（Frontend / AI Full-Stack / AI Engineer），W10 起写。\n' > career/resume/README.md
printf '# 面试题库\n\n| # | 分类 | 问题 | 来源 JD | 要点(简) | 状态 |\n|---|---|---|---|---|---|\n' > career/interview-questions.md
touch career/job-market.md career/capability-matrix.md career/jd-skills.jsonl
```

各文件用途：

| 文件                     | 放什么                                     | 更新频率         |
| ------------------------ | ------------------------------------------ | ---------------- |
| `job-market.md`          | JD 原始记录（一条一节）                    | 每 2 周追加 5 条 |
| `jd-skills.jsonl`        | 每条 JD 的结构化技能（AI 抽取 + 人工核对） | 同上             |
| `tally.py`               | 频次统计脚本                               | 不变             |
| `capability-matrix.md`   | 矩阵 + Top-12 + 差距清单                   | 每 2 周          |
| `interview-questions.md` | 面试题（W8 起补答案）                      | 持续             |
| `resume/`                | 简历版本                                   | W10 / W16 / W24  |

### Step 2 · 收集 10 条 JD（P0）

关键词（每个 2 条）：`AI 应用工程师`、`大模型应用开发`、`AI Agent 工程师`、`AI 全栈`、`LLM Engineer`。来源：Boss 直聘 / 拉勾 / LinkedIn / 公司官网招聘页。手工复制，不用爬虫；不用公司账号登录。尽量覆盖 ≥ 3 种公司类型。

`job-market.md` 每条格式：

```markdown
## JD-01

- 采集日期：2026-10-03
- 公司类型：大厂 / 中厂 / 创业 / 外企 / 传统行业数字化
- 岗位 · 城市 · 薪资：AI 应用工程师 · 上海 · 25–40K×15
- 必需技能：（原文关键句，精简）
- 加分技能：
- 链接：
- 与 WorkPilot 的关联：（一句话，如「要求 RAG + 评测」）
```

### Step 3 · AI 抽取技能（P0；JD 是公开信息，可发给外部 LLM）

对每条 JD 用以下提示词（Copilot Chat 或 DeepSeek 网页均可）：

```text
你是技术招聘分析助手。抽取下面 JD 的技能，只输出一行 JSON，不要解释：
{"id":"JD-01","required":[...],"bonus":[...]}
规则：
1. 只抽原文明确写出的技能，不推断。
2. 「熟悉/精通/要求/必须」归 required；「优先/加分/更佳」归 bonus。
3. 技能名归一化到词表；无法归入的原样保留并加前缀 NEW:
   词表：Python, FastAPI, TypeScript, React, LLM API, Prompt Engineering, Structured Output,
   Streaming, RAG, Embedding, Vector DB, Rerank, Tool Calling/Agent, LangChain, LangGraph, MCP,
   Memory, Evaluation, Observability, Guardrails/Security, Fine-tuning, Docker, K8s, Cloud, CI/CD,
   SQL/Postgres, Java/Go, Multimodal, AI-assisted Dev
JD 原文：
<<<
（粘贴）
>>>
```

把每行 JSON 追加到 `career/jd-skills.jsonl`。**人工核对**：随机抽 3 条，对照原文逐项检查「有没有编造 / 漏掉 / 必需加分放错」，错误率写进产出记录（这就是 Day11 要用 Pydantic 校验 + 评测解决的问题）。

### Step 4 · 统计频次（P0）

`career/tally.py`：

```python
"""统计 jd-skills.jsonl 中每个技能出现在多少条 JD 里（必需与加分合并计数）。"""
import collections
import json
import pathlib

path = pathlib.Path(__file__).with_name("jd-skills.jsonl")
rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
total = collections.Counter()
required = collections.Counter()
for r in rows:
    total.update(set(r["required"]) | set(r["bonus"]))
    required.update(set(r["required"]))
print(f"JD 数：{len(rows)}")
for skill, n in total.most_common(25):
    print(f"{n:>2}/{len(rows)}  (必需 {required[skill]:>2})  {skill}")
```

```bash
python3 career/tally.py
```

### Step 5 · 填矩阵 + Top-12 + 差距清单（P0）

`capability-matrix.md` 结构（下表的模块 / 证据 / 计划周已按蓝图预填，**次数和水平按实际统计与自评填写，不要照抄占位**）：

```markdown
# AI 岗位能力矩阵 v1（2026-10-03 · 样本 10 条 JD）

| 能力                                          | JD 出现次数(/10) | 当前水平(0–3) | 目标水平 | WorkPilot 证明模块(Mx)    | 证据文件                  | 计划周    |
| --------------------------------------------- | ---------------- | ------------- | -------- | ------------------------- | ------------------------- | --------- |
| Python / FastAPI                              | \_               | \_            | 3        | M1 M2.6                   | apps/api/                 | W2        |
| LLM API / Structured Output / Streaming       | \_               | \_            | 3        | M1                        | apps/api/app/llm/         | W2–3      |
| Prompt Engineering（版本化）                  | \_               | \_            | 2        | M1.6                      | prompts/                  | W3        |
| RAG（Chunking / Retrieval / Grounded Answer） | \_               | \_            | 3        | M2                        | apps/api/app/rag/         | W4–5      |
| Embedding / Vector DB                         | \_               | \_            | 2        | M2.3                      | app/rag/store.py          | W4        |
| Rerank / Hybrid Search                        | \_               | \_            | 2        | M2.4                      | app/rag/retrieve.py       | W5        |
| Evaluation / LLM-as-a-judge                   | \_               | \_            | 3        | M3                        | eval/                     | W5 / W14  |
| React / TypeScript / AI UX                    | \_               | \_            | 3        | M4                        | apps/web/                 | W6        |
| Docker / Cloud / CI/CD                        | \_               | \_            | 2        | M5                        | deploy/ .gitea/workflows/ | W7        |
| Tool Calling / Agent                          | \_               | \_            | 3        | M6 M7                     | app/tools/ app/agent/     | W9–10     |
| LangGraph / Memory / HITL                     | \_               | \_            | 2        | M7.2–M7.4                 | app/agent/                | W11–12    |
| MCP                                           | \_               | \_            | 2        | M8                        | apps/mcp-server/          | W13       |
| Observability / Cost                          | \_               | \_            | 2        | M9                        | app/obs/                  | W15       |
| Guardrails / Security                         | \_               | \_            | 2        | M11                       | app/security/             | W15 / W21 |
| Fine-tuning                                   | \_               | \_            | —        | 不做（蓝图 Non-goals）    | —                         | —         |
| K8s                                           | \_               | \_            | —        | 不做（单机 compose 足够） | —                         | —         |

## Top-12（按出现次数排序）

1. ...

## 差距清单（目标 − 当前 ≥ 2，且出现次数 ≥ 5）

| 能力 | 差距 | 由哪周补 | 补完的客观证据 |

## 待观察（高频但不在 WorkPilot 范围）

- 技能：**　次数：**　处理：只记录，W9 Day36 JD 追踪时复核
```

排序规则：先按「出现次数」降序，再按「必需次数」降序；取前 12 写入 Top-12。

### Step 6 · 提交（P0）

```bash
cd ~/lab/projects
git add career/
git commit -m "docs(career): add capability matrix v1 from 10 JDs"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么要做技能归一化？（答：同义词会把一个高频能力拆成多个低频项，导致优先级判断错误）
2. 一项能力 9/10 出现但 WorkPilot 不覆盖，怎么办？（答：记入待观察；若确实阻碍求职再按蓝图 §12 写 CHANGELOG 评估，不直接加学习任务）
3. AI 抽取 JD 技能最常见的错误是什么？（答：推断出原文没写的技能、必需 / 加分放错、同义词未归一）
4. 水平「2」和「3」的区别？（答：2 = 能独立实现并解释；3 = 能讲清生产级取舍并有公开证据，如评测报告 / 文章）
5. 矩阵里为什么要有「证据文件」列？（答：面试和简历只认证据；没有文件路径的能力等于没有）

## 8. 对 DA-01 的贡献

矩阵把 WorkPilot 的模块和市场需求逐项对齐：后续每个模块完成时，在矩阵里更新「当前水平」和证据文件，P1 / P2 / P3 的简历 bullet 直接从这里生成。它也是防跑偏工具——不在矩阵 Top-12 又不在蓝图里的技术，不进计划。

## 9. 求职映射（D 线）

- 岗位能力：岗位分析、自我评估、学习路径规划
- 对应岗位：AI 应用工程师 / 大模型应用开发 / AI Agent 工程师 / AI 全栈
- 简历 bullet 草稿：（今天不产出简历 bullet；矩阵是后续所有 bullet 的来源）
- 面试可能问：
  - 「你觉得 AI 应用工程师最核心的能力是什么？」→ 要点：用 10 条 JD 统计结果回答（如 RAG **/10、Evaluation **/10），再说 WorkPilot 如何逐项证明。
  - 「前端转 AI 工程的优势与短板？」→ 要点：优势 AI UX / 全栈交付；短板 Python 后端与评测，按矩阵差距清单给出补齐计划与已完成证据。

## 10. 卡住时的处理

| 现象                              | 处理                                                                                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 招聘网站要求登录才能看 JD         | 用个人账号或换 LinkedIn / 公司官网；不用公司账号                                                                                             |
| 搜到的 JD 大多是算法 / 训练岗     | 加「应用」「工程」「全栈」关键词，排除「算法」「训练」「推理优化」                                                                           |
| AI 输出不是合法 JSON              | 提示词里强调「只输出一行 JSON」；仍失败就手工修；`python3 -c 'import json,sys;[json.loads(l) for l in open("career/jd-skills.jsonl")]'` 校验 |
| `tally.py` 报 `KeyError: 'bonus'` | 某行缺字段，补 `"bonus":[]`                                                                                                                  |
| 自评水平拿不准                    | 按 §5 的 0–3 定义：没写过代码就 ≤ 1                                                                                                          |
| 想顺手开始学某个高频新技术        | 写进「待观察」，关掉页面（防偏航 GLOBAL_CONTEXT §12）                                                                                        |

## 11. 产出记录（执行时填写）

- JD 条数 / 公司类型分布：\_\_\_\_
- 出现次数 Top-5：\_\_\_\_
- AI 抽取抽查错误率：\_**\_ / \_\_**
- Top-12 中由 WorkPilot 证明的项数：\_\_\_\_ / 12
- 差距最大的 3 项：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day07 Task 2（Python 工具链 + FastAPI 骨架）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（JD 不足 10 条可在 W3 末补齐，但统计与矩阵必须今天完成）。
