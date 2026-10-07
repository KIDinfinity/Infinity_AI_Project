# Day 18 · 2026-10-22 · Week 04 Task 4：20 题种子集 + 首批 Badcase（v0.2）

## 0. 今天只做一件事

定下评测集 schema，写 20 题种子集，用脚本跑出 v0.2 报告，人工判对错并把失败案例按根因分类写进 Badcase 库，打 tag `v0.2.0`。

不碰：自动指标 hit@k / MRR 与 50 题（W5 Day19）、LLM-judge（Day21）、任何检索优化（Day20）——今天只「记录问题」，不「修问题」。

## 1. 资产锚点

- 构建模块：M3.1 数据集规范、M3.4 Badcase 库（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.2**（RAG MVP：导入文档 → 带引用回答）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`kb_qa.jsonl` 20 题；`eval/reports/20261022-rag-v0.2.md`（来源命中 **/15、库外拒答 **/5、人工正确 \_\_/20）；≥5 条带根因的 Badcase；与 v0.1 私有知识题的前后对比
- 今日 AI 实际应用：RAG 评测的第一步——把「感觉还行」变成「15 题中 x 题命中来源」；Badcase 根因分类指导 W5 优化方向

## 2. 起点（前置确认）

- 已有：`/v1/kb/ask`（返回 `retrieved` 含 `source/section`）、`kb_default` 已入库、v0.1 的 `badcases.md`（简版）。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api && uv run pytest -m "not llm" -q
uv run uvicorn app.main:app --reload --port 8000     # 另开终端
curl -s localhost:8000/v1/kb/docs | python -c "import sys,json;[print(d['source']) for d in json.load(sys.stdin)]" | head -50
```

最后一条命令列出的 `source` 就是写 `expected_sources` 时的合法路径。

## 3. 验收对齐（做完要能勾掉）

- [ ] `eval/datasets/kb_qa.jsonl` 20 行：in_kb 12、out_of_kb 5、confusing 3；脚本启动时 schema 校验全部通过
- [ ] `uv run --project apps/api python scripts/run_kb_smoke.py` 生成 `eval/reports/20261022-rag-v0.2.md`
- [ ] 报告含：来源命中率（in_kb + confusing 共 15 题）、库外拒答率（5 题）、人工正确率（20 题，手填）、平均延迟、总成本
- [ ] `eval/badcases/badcases.md` 升级为完整模板，≥ 5 条（含 v0.1 条目的复测结论）
- [ ] README 有 v0.2 章节（含与 v0.1 对比）
- [ ] `git tag` 有 `v0.2.0` 且已 push；Week 4 README 第 11 节已填写

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                      |
| ------- | ------ | --------------------------------------------------------- |
| 0–35    | P0     | 写 20 题（先问题 + expected_sources，再 expected_answer） |
| 35–60   | P0     | `run_kb_smoke.py`（schema 校验 + 调 API + 报告）          |
| 60–80   | P0     | 跑报告 + 人工判对错                                       |
| 80–100  | P0     | Badcase 模板升级 + ≥5 条                                  |
| 100–112 | P0     | README v0.2 + tag                                         |
| 112–120 | P1     | Week 4 复盘                                               |

时间不足时最低保留：20 题 + 报告 + 5 条 badcase + tag（README 写 3 行即可）。

## 5. 今日学习（只学完成任务必须的）

- 评测集三类题各测什么：in_kb 测召回与生成正确性；out_of_kb 测拒答（防幻觉）；confusing 测区分相近概念（最容易暴露检索排序与生成混淆）。
- `expected_sources` 用「文档路径#章节」：路径用于文档级命中判断，章节用于更细的段落级判断（章节可空）。
- 写题顺序：先挑文档段落 → 用「真实用户的说法」提问（不要照抄原文句子，否则高估召回）→ 再写期望答案。
- Badcase 根因 8 类：未召回 / 召回排序靠后 / 分块切断 / 生成幻觉 / 引用错误 / 拒答失败 / 过度拒答 / 数据缺失——每类对应不同修复手段。
- 资料：https://docs.pydantic.dev/latest/concepts/models/ 、https://docs.python.org/3/library/json.html 、https://git-scm.com/book/en/v2/Git-Basics-Tagging

## 6. 执行步骤

### Step 1 · 数据集 schema + 20 题

`eval/datasets/kb_qa.jsonl`（每行一个 JSON；示例 3 条，路径以 `/v1/kb/docs` 实际输出为准）：

```json
{"id":"q001","question":"FastAPI 里怎么让一个查询参数变成可选的？","type":"in_kb","expected_answer":"给参数设置默认值 None（可配合 Query/Annotated），不传时值为 None","expected_sources":["oss/fastapi/query-params.md#查询参数 > 可选参数"],"tags":["fastapi","参数"]}
{"id":"q013","question":"我们用的 Kubernetes 集群 HPA 的扩容阈值是多少？","type":"out_of_kb","expected_answer":"应拒答：知识库中没有找到相关内容","expected_sources":[],"tags":["拒答"]}
{"id":"q018","question":"前端项目的环境变量怎么区分开发和生产？","type":"confusing","expected_answer":"Vite 使用 .env.[mode] 与 VITE_ 前缀暴露给客户端；不要与后端 pydantic-settings 的 .env 混淆","expected_sources":["oss/vite/env-and-mode.md#"],"tags":["vite","env","易混淆"]}
```

分配建议：12 道 in_kb 覆盖 notes / oss / team 三类语料（team 规范样例至少 3 道，含 v0.1 冒烟里的私有题）；5 道 out_of_kb 包括 2 道「看起来像团队内部但库里没有」的题（最容易诱发编造）；3 道 confusing 选两篇文档都谈到的概念。

### Step 2 · run_kb_smoke.py（样板让 AI 生成，匹配与统计逻辑自己写）

```python
import json, statistics, time
from pathlib import Path
from typing import Literal
import httpx
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
API = "http://localhost:8000/v1/kb/ask"
REFUSAL = "知识库中没有找到"

class QA(BaseModel):
    id: str
    question: str
    type: Literal["in_kb", "out_of_kb", "confusing"]
    expected_answer: str
    expected_sources: list[str]
    tags: list[str] = []

def match(expected: str, hit: dict) -> bool:
    path, _, sec = expected.partition("#")
    return hit["source"] == path and (not sec or sec in hit["section"])

def main() -> None:
    lines = (ROOT / "eval/datasets/kb_qa.jsonl").read_text(encoding="utf-8").splitlines()
    data = [QA.model_validate_json(line) for line in lines if line.strip()]   # schema 校验，不合法直接报错
    rows = []
    with httpx.Client(timeout=120) as c:
        for q in data:
            d = c.post(API, json={"question": q.question}).raise_for_status().json()
            hit = any(match(e, h) for e in q.expected_sources for h in d["retrieved"]) if q.expected_sources else None
            rows.append({"q": q, "hit": hit, "refused": d["refused"], "n_cite": len(d["citations"]),
                         "top1": d["retrieved"][0]["source"] if d["retrieved"] else "-",
                         "latency": d["latency_ms"], "cost": d["cost"] or 0.0,
                         "answer": d["answer"][:50].replace("\n", " ").replace("|", "/")})
    src = [r for r in rows if r["q"].type != "out_of_kb"]
    ook = [r for r in rows if r["q"].type == "out_of_kb"]
    out = [f"# RAG v0.2 种子集报告 · {time.strftime('%Y-%m-%d')}", "",
           f"- 来源命中：{sum(r['hit'] for r in src)}/{len(src)}",
           f"- 库外拒答：{sum(r['refused'] for r in ook)}/{len(ook)}",
           f"- 平均延迟：{statistics.mean(r['latency'] for r in rows):.0f} ms；总成本：{sum(r['cost'] for r in rows):.6f}",
           "- 人工正确：__/20（逐行勾选后手填）", "",
           "| id | type | 来源命中 | 拒答 | 引用数 | top1 来源 | 答案摘要 | 人工 |", "|---|---|---|---|---|---|---|---|"]
    out += [f"| {r['q'].id} | {r['q'].type} | {'-' if r['hit'] is None else ('✅' if r['hit'] else '❌')} | "
            f"{'是' if r['refused'] else '否'} | {r['n_cite']} | {r['top1']} | {r['answer']} | ☐对 ☐错 |" for r in rows]
    path = ROOT / f"eval/reports/{time.strftime('%Y%m%d')}-rag-v0.2.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:6]), f"\n→ {path}")

if __name__ == "__main__":
    main()
```

```bash
cd ~/lab/workpilot && uv run --project apps/api python scripts/run_kb_smoke.py
```

> 「来源命中」这里检查的是 `retrieved`（top_k 内是否出现期望来源），W5 会细化为 hit@1/3/5 与 MRR。

### Step 3 · 人工判定

打开报告逐行对照 `expected_answer` 勾「对 / 错」，填「人工正确 \_\_/20」。对每个 ❌ 或「错」，用 `/v1/kb/search` 看 top10 检索结果，判断根因：

| 观察                                 | 根因         |
| ------------------------------------ | ------------ |
| 期望来源不在 top10                   | 未召回       |
| 在 top10 但不在 top5                 | 召回排序靠后 |
| 命中了来源但关键句被切到相邻块       | 分块切断     |
| 来源正确但答案说了资料里没有的内容   | 生成幻觉     |
| 答案对但 `[n]` 指向无关片段 / 无引用 | 引用错误     |
| 库外题给出了答案                     | 拒答失败     |
| 库内题被拒答                         | 过度拒答     |
| 语料里本来就没有这部分               | 数据缺失     |

### Step 4 · Badcase 库升级

`eval/badcases/badcases.md` 改为完整模板（v0.1 条目迁移进来并补「v0.2 复测」结论）：

```markdown
# Badcase 库

根因分类：未召回 / 召回排序靠后 / 分块切断 / 生成幻觉 / 引用错误 / 拒答失败 / 过度拒答 / 数据缺失
状态：open / fixing / fixed（附修复版本）/ wontfix

| ID     | 版本      | 问题                                   | 现象                                  | 期望                     | 检索结果（top3 来源/分数）           | 根因分类     | 修复思路              | 状态        |
| ------ | --------- | -------------------------------------- | ------------------------------------- | ------------------------ | ------------------------------------ | ------------ | --------------------- | ----------- |
| BC-001 | v0.1→v0.2 | WorkPilot 的提交信息规范是什么？       | v0.1 编造；v0.2 正确引用 [1]          | 以 PROJECT_STANDARD 为准 | notes/PROJECT_STANDARD.md 0.71       | 数据缺失     | 接入知识库            | fixed(v0.2) |
| BC-004 | v0.2      | 前端项目的环境变量怎么区分开发和生产？ | 混入 pydantic-settings 内容并引用 [3] | 只讲 Vite .env.[mode]    | vite/env 0.63；fastapi/settings 0.61 | 召回排序靠后 | W5：hybrid / 标题加权 | open        |
```

≥ 5 条（v0.1 迁移的可计入，但至少 3 条是 v0.2 新发现）。

### Step 5 · README v0.2 + tag

README 追加：

```markdown
## v0.2（2026-10-22）· RAG MVP

- 能力：md/pdf/html 导入 → 标题感知分块 → bge-m3 → Qdrant；/v1/kb/ask（引用 + 拒答）、/v1/kb/ask/stream、/v1/kb/search、/v1/kb/docs
- 语料：** 篇 / ** 分块（来源与许可见 docs/product/corpus-sources.md）
- 种子集 20 题：来源命中 **/15，库外拒答 **/5，人工正确 \_\_/20（eval/reports/20261022-rag-v0.2.md）
- 对比 v0.1：私有知识题 幻觉 **/** → 正确引用 **/**
- 已知问题：见 eval/badcases/badcases.md（open \_\_ 条）
```

```bash
cd ~/lab/workpilot
git add eval scripts/run_kb_smoke.py README.md
git commit -m "feat(eval): kb_qa seed set (20), smoke runner, badcase taxonomy; release v0.2"
git tag -a v0.2.0 -m "v0.2.0: RAG MVP with citations and refusal"
git push && git push origin v0.2.0
```

### Step 6 · Week 4 复盘（P1）

填写 `plan/phase_01/week_04/README.md` 第 11 节。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么评测集里必须有库外题？（答：只测库内题无法发现「拒答失败」，而编造是 RAG 最严重的问题。）
2. 为什么提问不能照抄原文？（答：照抄会让向量相似度虚高，高估召回；真实用户的措辞与文档不同。）
3. 「未召回」和「召回排序靠后」的修复手段有何不同？（答：前者改分块/语料/检索方式（hybrid）；后者调 top_k、rerank、标题加权。）
4. 来源命中但答案错，说明问题在哪一层？（答：生成层或分块层——看关键句是否在命中块内，区分生成幻觉与分块切断。）
5. 为什么 v0.1 的 badcase 要复测？（答：形成「修复 → 回归」闭环，证明改进有效，也是 M3.5 回归用例的雏形。）

## 8. 对 DA-01 的贡献

WorkPilot 达到 v0.2：RAG MVP 可演示，且有第一份数据化的质量报告与根因分类的 Badcase 库。W5 的评测 runner、实验、judge 都在今天的 schema 与 Badcase 分类上扩展。

## 9. 求职映射（D 线）

- 岗位能力：RAG Evaluation 数据集设计、Badcase 分析与根因分类、版本发布。
- 对应岗位：AI Engineer、RAG Engineer、LLM Evaluation Engineer。
- 简历 bullet 草稿：「设计 RAG 评测数据规范（库内/库外/易混淆三类 + 期望来源到章节级），建立 8 类根因的 Badcase 库；v0.2 种子集来源命中 **/15、库外拒答 **/5，私有知识题幻觉相比无检索基线下降 \_\_%。」
- 面试可能问：
  1. 「你的 RAG 评测集怎么构建的？」——要点：三类题比例、真实措辞、期望来源到章节、先种子 20 再扩 50、LLM 生成候选需人工审核。
  2. 「发现 badcase 后怎么处理？」——要点：复现 → 看检索 top10 → 归入 8 类根因 → 按类修复 → 转为回归用例。

## 10. 卡住时的处理

| 现象                                     | 处理                                                                                                                           |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `pydantic_core.ValidationError` 指向某行 | 该行 JSON 字段缺失或 `type` 拼错；用 `python -c "import json;[json.loads(l) for l in open('eval/datasets/kb_qa.jsonl')]"` 定位 |
| 来源命中全是 ❌ 但答案明显正确           | `expected_sources` 路径与 payload `source` 不一致（如多了 `data/corpus/` 前缀）；用 `/v1/kb/docs` 的输出复制路径               |
| 章节匹配总失败                           | section 是「A > B > C」完整路径，`expected` 只写最后一级也能 `in` 匹配；或先留空只做文档级                                     |
| `httpx.HTTPStatusError: 502`             | 后端 LLM 调用失败，看 uvicorn 日志；单题失败不要中断全部，可加 try/except 记为 ERR                                             |
| 写不出 5 道库外题                        | 用「看似团队内部」的问题：内部系统名、具体值班表、上周会议结论等语料中没有的内容                                               |
| 20 题全对、找不到 badcase                | 题目太简单或照抄原文；补 3 道口语化、跨文档的题                                                                                |

## 11. 产出记录（执行时填写）

- 来源命中 / 库外拒答 / 人工正确：**/15、**/5、\_\_/20
- 平均延迟 / 总成本：\_**\_ ms / ¥\_\_**
- Badcase 新增编号与根因分布：\_\_\_\_
- v0.1 → v0.2 私有知识题对比：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE → Week 04 完成（v0.2），明天进入 Day19（W5 Task 1：评测集 50 题 + 检索指标 runner）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（tag 与 badcase 优先）。
