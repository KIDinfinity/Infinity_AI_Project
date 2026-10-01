# Day 21 · 2026-10-18 · Week 05 Task 3：LLM-judge + Badcase 分类 + 定配置（v0.3）

## 0. 今天只做一件事

给评测加上生成质量维度：用 LLM-judge 评正确性 / 忠实度 / 引用正确，并用 10 条人工标注校准 judge；跑出 v0.3 完整报告，按 Badcase 分类修复前 2 类，定下默认配置并打 tag `v0.3.0`。

不碰：新的检索实验（Day20 已结束）、换 judge 模型供应商、评测看板 UI（W20）、Web（W6）。

## 1. 资产锚点

- 构建模块：M3.2 RAG 指标（LLM-judge：正确性/忠实度/引用正确率）、M3.4 Badcase 库（分类统计 + 修复）（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.3**（RAG 优化 + 50 题评测 + Badcase）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make eval-rag-judge` → `eval/reports/20261018-rag-v0.3.{json,md}`（检索 + 生成指标）；judge 与人工一致率；Badcase 分类统计与修复前后对比；`.env.example` 定版默认配置
- 今日 AI 实际应用：LLM-as-a-judge（复用 M1.3 结构化输出）+ 人工校准 → W14 Agent 评测、W20 场景 rubric 评测沿用同一模式

## 2. 起点（前置确认）

- 已有：`run_rag_eval.py`（`--with-answer` 时每行有 `answer/citations`）、ADR 0003 选定配置、`kb_default` 已按其重建、`generate_structured`。
- 需确认：

```bash
cd ~/lab/workpilot
cat docs/adr/0003-chunking-retrieval.md | sed -n '/## 决定/,/## 理由/p'
grep -E "CHUNK|TOP_K|RETRIEVAL|THRESHOLD" apps/api/.env
cd apps/api && uv run pytest -m "not llm" -q
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `eval/datasets/judge_gold.jsonl` 10 条人工标注（覆盖库内对/错、库外拒答、易混淆）
- [ ] `prompts/judge_answer.v1.md` + `eval/runners/judge.py` 可运行；一致率（correctness 完全一致）≥ 80%，或已写未达标原因 + v2 改动
- [ ] `make eval-rag-judge` 生成 `eval/reports/20261018-rag-v0.3.{json,md}`：hit@1/3/5、MRR、拒答正确率、误拒率、正确性均值、忠实度 yes 比例、引用正确率、P50/P95、单次平均成本
- [ ] `SCORE_THRESHOLD` 依据 in_kb / out_of_kb 的 top1 分数分布确定（dense 模式），写进报告
- [ ] `badcases.md` 有分类统计表；前 2 类各有修复动作，并回归（修复前后指标）
- [ ] `.env.example` 默认配置更新；README v0.3；tag `v0.3.0` 已 push
- [ ] `~/lab/projects/career/capability-matrix.md` RAG / Eval 行的证据列已更新；Week 5 README 第 11 节已填写

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                        |
| ------- | ------ | ------------------------------------------- |
| 0–15    | P0     | 人工标注 10 条 gold                         |
| 15–40   | P0     | judge prompt + `judge.py` + 一致率          |
| 40–60   | P0     | 定阈值 + 跑 v0.3 完整评测（带生成 + judge） |
| 60–90   | P0     | Badcase 分类统计 → 修复前 2 类 → 回归       |
| 90–105  | P0     | `.env.example` + README + tag               |
| 105–120 | P1     | 能力矩阵 + Week 5 复盘                      |

时间不足时最低保留：gold 10 条 + judge + 一致率 + v0.3 报告 + tag；修复只做第 1 类，能力矩阵顺延到 W8。

## 5. 今日学习（只学完成任务必须的）

- LLM-as-a-judge：让模型按 rubric 给结构化分数；必须先用人工标注校准（一致率），否则 judge 本身就是未验证的指标。
- 三个维度各回答一个问题：correctness「对不对」（对照 expected_answer）；faithfulness「有没有超出上下文」（对照检索上下文，与对错无关）；citation_correct「[n] 指向的片段是否支撑该句」。
- judge 常见偏差：自我偏好（同模型评自己）、偏好长答案、位置偏差、对「拒答」判分不一致——用低温度、明确 rubric、拒答专门规则、人工抽检缓解。
- 阈值选择：看 in_kb 与 out_of_kb 的 top1 分数分布，选能最大化「拒答正确率 − 误拒率」的值，而不是拍一个 0.5。
- 资料：https://api-docs.deepseek.com/guides/json_mode 、https://docs.pydantic.dev/latest/concepts/json_schema/ 、https://docs.python.org/3/library/statistics.html

## 6. 执行步骤

### Step 1 · 人工标注 gold（不可交给 AI）

先跑一次带生成的评测拿到答案：`make eval-rag ARGS="--with-answer --name pre-judge"`。从结果中挑 10 题（4 道库内答对、2 道库内答错/不完整、2 道库外、2 道易混淆），逐条看「问题 + 期望答案 + 检索上下文 + 模型答案」，写 `eval/datasets/judge_gold.jsonl`：

```json
{"id":"q007","correctness":2,"faithfulness":"yes","citation_correct":true,"note":"完整且引用对"}
{"id":"q018","correctness":1,"faithfulness":"partial","citation_correct":false,"note":"混入 FastAPI 配置内容"}
{"id":"q041","correctness":2,"faithfulness":"yes","citation_correct":true,"note":"库外题正确拒答"}
```

评分规则（写进 judge prompt，人工也按此标）：correctness 2=要点完整正确，1=部分正确/有遗漏，0=错误或答非所问；库外题正确拒答记 2、编造记 0；库内题错误拒答记 0。

### Step 2 · judge prompt + judge.py（核心逻辑自己写）

`prompts/judge_answer.v1.md`：

```markdown
---
id: judge_answer
version: 1
model: deepseek-chat
changelog:
  - "v1 2026-10-18: correctness 0/1/2、faithfulness yes/partial/no、citation_correct"
---

你是严格的 RAG 评测员。根据下面信息评分，只输出 json。

评分规则：

- correctness：2=覆盖期望答案的要点且无错误；1=部分正确或有遗漏；0=错误、答非所问。期望答案为「应拒答」时：回答拒答记 2，给出具体答案记 0。期望答案非拒答而回答拒答记 0。
- faithfulness：回答中的每个事实是否都能在「检索上下文」中找到依据。全部有依据=yes，部分=partial，大部分没有=no。拒答记 yes。
- citation_correct：回答中的 [n] 是否都指向能支撑对应句子的片段；没有引用但有事实性陈述记 false；拒答记 true。
- 不要因为回答更长而给更高分。reason ≤ 60 字。

问题：{question}
期望答案：{expected_answer}
检索上下文：
{context}
被评回答：
{answer}
```

`eval/runners/judge.py`：

```python
from typing import Literal
from pydantic import BaseModel, Field
from app.llm.prompts import load_prompt
from app.llm.structured import generate_structured

class JudgeResult(BaseModel):
    correctness: Literal[0, 1, 2]
    faithfulness: Literal["yes", "partial", "no"]
    citation_correct: bool
    reason: str = Field(max_length=200)

async def judge_one(question: str, expected: str, context: str, answer: str) -> JudgeResult:
    p = load_prompt("judge_answer.v1")
    msg = p.render(question=question, expected_answer=expected, context=context or "（无检索结果）", answer=answer)
    result, _ = await generate_structured(JudgeResult, [{"role": "user", "content": msg}], temperature=0)
    return result

def agreement(judged: dict[str, JudgeResult], gold: list[dict]) -> dict[str, float]:
    ids = [g["id"] for g in gold if g["id"] in judged]
    n = max(len(ids), 1)
    g = {x["id"]: x for x in gold}
    return {"n": len(ids),
            "correctness": sum(judged[i].correctness == g[i]["correctness"] for i in ids) / n,
            "faithfulness": sum(judged[i].faithfulness == g[i]["faithfulness"] for i in ids) / n,
            "citation": sum(judged[i].citation_correct == g[i]["citation_correct"] for i in ids) / n}
```

> 注意：Day11 的 `generate_structured` 用 `extra.setdefault("temperature", 0.2)`，所以 judge 可以传 `temperature=0` 覆盖；若你当时写成了显式 `temperature=0.2, **extra`，这里会报重复参数，按 Day11 写法改正。

`run_rag_eval.py` 增加 `--judge`：生成回答时保留 `build_context(hits)` 作为 `context`，对每题调 `judge_one`，汇总：`correctness_mean`（0–2 → 再除以 2 归一）、`faithfulness_yes_rate`、`citation_correct_rate`（只统计非拒答题）；若存在 `judge_gold.jsonl` 则输出一致率。Makefile：

```makefile
eval-rag-judge:
	cd apps/api && PYTHONPATH=. uv run python ../../eval/runners/run_rag_eval.py --with-answer --judge --name rag-v0.3 $(ARGS)
```

一致率 < 80%：看分歧题的 `reason`，多半是拒答规则或「部分正确」边界不清 → 改 prompt 为 `judge_answer.v2`（changelog 写原因），最多迭代 1 次，结果如实记录。

### Step 3 · 定阈值 + 跑 v0.3

从 `pre-judge` 报告的 `rows` 中取 in_kb/out_of_kb 的 `top1_score`，用 AI 写个 10 行小脚本扫描阈值 0.30–0.80（步长 0.02），对每个阈值计算「库外 top1 < 阈值的比例」与「库内 top1 < 阈值的比例」，选前者高、后者 ≤ 5% 的点。写入 `apps/api/.env` 的 `SCORE_THRESHOLD`（hybrid 模式不使用该阈值，见 ADR 0003）。

```bash
cd ~/lab/workpilot && make eval-rag-judge
```

### Step 4 · Badcase 分类统计 + 修复前 2 类

从 v0.3 报告中把 correctness ≤ 1、faithfulness ≠ yes、citation 错、拒答错的题归入 8 类根因（Day18 判定表），追加到 `badcases.md`，并在文件顶部加统计：

```markdown
## 分类统计（v0.3 · 2026-10-18）

| 根因         | 数量 | 占比 | 修复动作                                      | 修复后 |
| ------------ | ---- | ---- | --------------------------------------------- | ------ |
| 召回排序靠后 | 5    | 31%  | 向量文本拼标题已做；top_k 5→6                 | 2      |
| 生成幻觉     | 4    | 25%  | qa_answer.v2：无依据的句子不写；temperature 0 | 1      |
```

修复动作对照（选与你前 2 类匹配的）：未召回 → 补文档 / hybrid / 调分块；排序靠后 → top_k、标题加权；分块切断 → 增大 overlap、代码块不切；生成幻觉 → prompt v2 + 温度 0；引用错误 → prompt 给引用示例；拒答失败 → 阈值；过度拒答 → 阈值下调、prompt 允许部分回答；数据缺失 → 补语料。

改了 prompt 就新建 `qa_answer.v2.md` 并把 `ANSWER_PROMPT=qa_answer.v2`；修复后重跑 `make eval-rag-judge ARGS="--name rag-v0.3-fix"`，在报告中写修复前后对比，被修复的 badcase 标 `fixed(v0.3)`。

### Step 5 · 定配置 + README + tag

`.env.example` 更新默认值（无密钥）：

```bash
# RAG 默认配置（ADR 0003 + v0.3 评测，2026-10-18）
CHUNK_SIZE=600
CHUNK_OVERLAP=100
TOP_K=5
RETRIEVAL_MODE=dense
SCORE_THRESHOLD=0.45
ANSWER_PROMPT=qa_answer.v2
```

（数值以你的实验结果为准，上面仅示意格式。）

README 追加 v0.3：评测结果表（基线 vs v0.3）、链接 ADR 0003 与报告、与蓝图 §11 目标对比。若基线明显偏离目标（如 hit@5 远低于 0.85），在 `plan/CHANGELOG.md` 记录目标调整及原因（蓝图 §11 允许 W5 后调整）。

```bash
cd ~/lab/workpilot
git add eval prompts apps/api .env.example README.md Makefile
git commit -m "feat(eval): llm-judge with human calibration, badcase stats and fixes; release v0.3"
git tag -a v0.3.0 -m "v0.3.0: RAG eval (50 q, retrieval + judge) and tuned defaults"
git push && git push origin v0.3.0
```

### Step 6 · 能力矩阵 + 复盘（P1）

`~/lab/projects/career/capability-matrix.md` 中 RAG、Evaluation、LLM-as-a-judge 相关行的「证据」列填：`workpilot v0.3.0：eval/reports/20261018-rag-v0.3.md（hit@5 __ / 正确性 __ / judge 一致率 __%）`、`docs/adr/0003-chunking-retrieval.md`。提交 projects 仓库；填写 Week 5 README 第 11 节。

## 7. 概念自检（不看资料，口述，附答案）

1. faithfulness 与 correctness 的区别？（答：前者看回答是否被上下文支撑，后者看是否与期望答案一致；可能「忠实但错」（上下文本身错/不全）或「对但不忠实」（用了模型自身知识）。）
2. 为什么 judge 必须用人工标注校准？（答：judge 本身可能有偏差，一致率证明它可以替代人工做大规模评测。）
3. 同一模型既回答又评判有什么风险？怎么缓解？（答：自我偏好；低温度、明确 rubric、人工抽检，后续可换不同模型做 judge。）
4. 阈值怎么定比较合理？（答：用库内/库外 top1 分数分布，在误拒率可接受的前提下最大化库外拒答。）
5. 修复 badcase 后为什么要重跑全量评测？（答：防止修一处坏多处，以全量指标确认净收益。）

## 8. 对 DA-01 的贡献

WorkPilot 达到 v0.3：检索与生成两个层面都有可复现指标，judge 经过人工校准，默认配置有数据与 ADR 支撑，Badcase 有分类统计和修复闭环。P1 验收中「50 题评测报告 + 基线数值 + Badcase ≥10 条」基本达成，W6 Web Console 直接使用定版配置。

## 9. 求职映射（D 线）

- 岗位能力：LLM-as-a-judge、评测校准、Badcase 驱动优化、指标体系设计。
- 对应岗位：LLM Evaluation Engineer、AI Engineer、RAG Engineer。
- 简历 bullet 草稿：「引入 LLM-as-a-judge（正确性 / 忠实度 / 引用正确三维 rubric，结构化输出），以 10 条人工标注校准，一致率 **%；基于 Badcase 根因统计修复前两类问题，正确性 ** → **、忠实度 ** → **，库外拒答正确率 **。」
- 面试可能问：
  1. 「你怎么保证 LLM-judge 靠谱？」——要点：rubric 明确、结构化输出、温度 0、人工 gold 一致率、分歧分析、prompt 版本化。
  2. 「RAG 上线后效果下降怎么排查？」——要点：先看检索指标（hit@k/MRR）还是生成指标（忠实度/正确性）下降 → 对应到 badcase 根因 → 回归评测。

## 10. 卡住时的处理

| 现象                                                                       | 处理                                                                                           |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `TypeError: chat() got multiple values for keyword argument 'temperature'` | `generate_structured` 写死了 temperature，改为 `extra.setdefault("temperature", 0.2)` 后再透传 |
| `ValidationError: correctness Input should be 0, 1 or 2`                   | 模型输出了 `"2"` 字符串或 1.5；prompt 写明「整数 0/1/2」，校验失败重试会兜底                   |
| 一致率很低且分歧集中在拒答题                                               | 拒答规则写进 prompt 第一条并给例子；gold 中拒答题的标注也要按同一规则                          |
| 跑一次 judge 评测成本偏高                                                  | 每题 2 次调用（回答 + judge），50 题约 100 次；调试时用 `--limit 10`（自己加参数）             |
| 阈值扫描找不到 ≤5% 误拒的点                                                | 库内外分数分布重叠严重：阈值放宽，拒答主要依赖 prompt；在报告与 ADR 中说明                     |
| `git push origin v0.3.0` 被拒                                              | 同名 tag 已存在：不要强推，改 `v0.3.1` 并说明                                                  |

## 11. 产出记录（执行时填写）

- judge 一致率：correctness **% / faithfulness **% / citation **%（prompt 版本：\_\_**）
- SCORE_THRESHOLD：\_**\_（库外拒答 ** / 库内误拒 \_\_）
- v0.3：hit@5 ** / MRR ** / 拒答 ** / 正确性 ** / 忠实度 yes ** / 引用正确 ** / P95 **s / 单次 ¥**
- 前 2 类根因与修复前后：\_\_\_\_
- 与蓝图 §11 目标差距、是否调整：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 05 完成（v0.3），明天进入 Day22（W6 Task 1：Web 脚手架 + 聊天页）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（报告与 tag 优先，能力矩阵可顺延到 W8）。
