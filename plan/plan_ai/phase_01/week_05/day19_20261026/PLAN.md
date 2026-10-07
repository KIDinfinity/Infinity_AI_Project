# Day 19 · 2026-10-26 · Week 05 Task 1：评测集 50 题 + 检索指标 runner

## 0. 今天只做一件事

把评测集扩到 50 题，并写一个可重复运行的 runner：一条命令算出 hit@1/3/5、MRR、库外拒答正确率、延迟、成本，报告自带配置快照——产出 v0.3 的**基线报告**。

不碰：调参（Day20）、LLM-judge（Day21）、评测框架（RAGAS 等）、前端看板。

## 1. 资产锚点

- 构建模块：M3.1 数据集规范（50 题）、M3.2 RAG 指标（检索指标 + 拒答）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.3 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make eval-rag` → `eval/reports/20261026-rag-baseline.{json,md}`，含 hit@1/3/5、MRR、拒答正确率、P50/P95、总成本、配置快照（git sha）
- 今日 AI 实际应用：用 LLM 生成候选评测题（M1.3 结构化输出）+ 人工审核 → 学会「AI 辅助造数据但不盲信」；runner 是 W14 Agent 评测、W22 回归门禁的骨架

## 2. 起点（前置确认）

- 已有：`kb_qa.jsonl` 20 题、`retrieve.search(collection=...)`、`answer.ask(**search_kw)`、`generate_structured`、`data/index_manifest/kb_default.json`（若 Day16 P1 未做，今天在 Step 3 中用 settings 兜底）。
- 需确认：

```bash
cd ~/lab/workpilot
wc -l eval/datasets/kb_qa.jsonl                                   # 20
python3 -c "import json,collections;print(collections.Counter(json.loads(l)['type'] for l in open('eval/datasets/kb_qa.jsonl')))"
ls data/index_manifest/ 2>/dev/null
cd apps/api && uv run pytest -m "not llm" -q
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `kb_qa.jsonl` 50 行：in_kb 30 / out_of_kb 12 / confusing 8；schema 校验通过；`question` 无重复
- [ ] LLM 生成并入选的题 `tags` 含 `llm_seed`，且每道都经过人工改写/核对（第 11 节记录改写数）
- [ ] `make eval-rag` 成功，生成 `eval/reports/20261026-rag-baseline.json` 与 `.md`
- [ ] 报告头含：dataset 行数、collection、chunk_size、overlap、top_k、embed_model、answer_prompt、git sha
- [ ] 报告含：hit@1/3/5、MRR（38 道有来源的题）、库外拒答正确率（12 题）、库内误拒率、检索与回答 P50/P95、总成本
- [ ] 每题记录 `top1_score`；报告给出 in_kb 与 out_of_kb 的 top1 分数均值
- [ ] 已 push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                        |
| ------- | ------ | ----------------------------------------------------------- |
| 0–15    | P1     | `seed_question.v1.md` + `seed_eval.py`，生成 40 道候选      |
| 15–50   | P0     | 人工审核候选 → 选入 18 道 in_kb；手写 7 道库外 + 5 道易混淆 |
| 50–85   | P0     | `run_rag_eval.py`（匹配、指标、快照、报告）                 |
| 85–100  | P0     | Makefile + 跑基线                                           |
| 100–115 | P0     | 读报告，记录 3 个最差题                                     |
| 115–120 | P0     | 提交                                                        |

时间不足时最低保留：手写补齐 50 题（跳过 seed 脚本）+ runner 检索指标 + 库外题拒答 + 基线报告。

## 5. 今日学习（只学完成任务必须的）

- hit@k：期望来源出现在前 k 个结果中的题目比例（「找没找到」）；MRR：第一个正确结果排名倒数的均值（「排得靠不靠前」），未命中记 0。
- 检索指标用固定 top10 计算，与线上 `top_k`（送进 prompt 的数量）解耦：hit@5 衡量检索，top_k 影响生成、成本与拒答。
- P95 延迟：把延迟排序后取第 95 百分位，比平均值更能反映「最慢的那批用户体验」。
- LLM 生成评测题的偏差：措辞贴近原文 → 召回虚高；只考单块事实 → 缺跨文档题；期望答案可能错 → 必须人工审核改写。
- 资料：https://qdrant.tech/documentation/concepts/search/ 、https://docs.python.org/3/library/statistics.html 、https://pyyaml.org/wiki/PyYAMLDocumentation 、https://www.gnu.org/software/make/manual/make.html

## 6. 执行步骤

### Step 1 · （P1）LLM 生成候选题

`prompts/seed_question.v1.md`（front matter 同前，id: seed_question）正文：

```markdown
下面是知识库中的一段资料。请站在「一个忙碌的工程师在工作中遇到问题」的角度，提出 1 个可以仅凭这段资料回答的问题。
要求：不要照抄资料中的句子和标题用词，用口语化的说法；不要问「这段资料讲了什么」；如果资料信息量太少，answerable 设为 false。
输出 json：question、expected_answer（≤ 80 字）、answerable。

文档：{title}
章节：{section}
资料：
{text}
```

`scripts/seed_eval.py`（样板让 AI 生成）：用 `store.client.scroll(collection, limit=500, with_payload=True)` 取点 → `random.Random(42).sample(points, 40)` → 逐个 `generate_structured(SeedQuestion, ...)`（`SeedQuestion{question, expected_answer, answerable: bool}`）→ `answerable` 为真的写入 `eval/datasets/kb_qa.candidates.jsonl`，字段：`type="in_kb"`、`expected_sources=[f"{source}#{section}"]`、`tags=["llm_seed"]`。

```bash
cd ~/lab/workpilot/apps/api && PYTHONPATH=. uv run python ../../scripts/seed_eval.py --n 40
```

### Step 2 · 人工审核 + 补题（P0，不可交给 AI）

审核规则（每道候选逐条过）：

1. 措辞与原文重合度高 → 改写成你自己会问的说法；
2. 答案太琐碎（如「第 3 步是什么」）→ 删；
3. 核对 `expected_answer` 与原文一致，`expected_sources` 的 section 是否正确；
4. 至少 5 道改成「跨两节/两篇」的问题，`expected_sources` 写两个；
5. 选入 18 道（20 题种子中的 12 道 in_kb + 18 = 30）。

再手写 7 道 out_of_kb（凑满 12）与 5 道 confusing（凑满 8）。追加到 `kb_qa.jsonl`，id 续编 `q021…q050`。

```bash
cd ~/lab/workpilot
python3 -c "import json,collections;rows=[json.loads(l) for l in open('eval/datasets/kb_qa.jsonl')];print(len(rows),collections.Counter(r['type'] for r in rows));assert len({r['question'] for r in rows})==len(rows)"
```

### Step 3 · run_rag_eval.py（核心逻辑必须自己写）

`eval/runners/run_rag_eval.py`（从 `apps/api` 目录以 `PYTHONPATH=.` 运行，可直接 import `app.*`）：

```python
import argparse, asyncio, json, math, statistics, subprocess, time
from pathlib import Path
import yaml
from app.core.config import REPO_ROOT, settings
from app.rag.answer import ask
from app.rag.retrieve import search

def match(expected: str, hit) -> bool:
    path, _, sec = expected.partition("#")
    return hit.source == path and (not sec or sec in hit.section)

def first_rank(expected: list[str], hits) -> int | None:
    return next((i for i, h in enumerate(hits, 1) if any(match(e, h) for e in expected)), None)

def pct(xs: list[float], p: float) -> float:
    s = sorted(xs)
    return s[max(0, math.ceil(p * len(s)) - 1)] if s else 0.0

def snapshot(cfg: dict) -> dict:
    mf = REPO_ROOT / "data/index_manifest" / f"{cfg['collection']}.json"
    manifest = json.loads(mf.read_text()) if mf.exists() else {}
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT).stdout.strip()
    return {"collection": cfg["collection"], "chunk_size": manifest.get("chunk_size", settings.chunk_size),
            "overlap": manifest.get("overlap", settings.chunk_overlap), "top_k": cfg["top_k"],
            "retrieval": cfg.get("retrieval", "dense"), "embed_model": settings.embed_model,
            "answer_prompt": settings.answer_prompt, "git_sha": sha, "dataset": cfg["dataset"]}

async def run(cfg: dict) -> dict:
    lines = Path(cfg["dataset"]).read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    out = []
    for q in rows:
        t0 = time.perf_counter()
        hits = await search(q["question"], top_k=10, collection=cfg["collection"], score_threshold=0.0)
        r = {"id": q["id"], "type": q["type"], "retrieve_ms": int((time.perf_counter() - t0) * 1000),
             "top1_score": round(hits[0].score, 4) if hits else 0.0,
             "rank": first_rank(q["expected_sources"], hits) if q["expected_sources"] else None,
             "top3": [f"{h.source}#{h.section}" for h in hits[:3]]}
        if cfg["with_answer"] or q["type"] == "out_of_kb":
            a = await ask(q["question"], top_k=cfg["top_k"], collection=cfg["collection"])
            r |= {"refused": a.refused, "answer": a.answer, "answer_ms": a.latency_ms, "cost": a.cost or 0.0,
                  "citations": [c.n for c in a.citations]}
        out.append(r)
    ranked = [r for r in out if r["type"] != "out_of_kb"]
    ook = [r for r in out if r["type"] == "out_of_kb"]
    inkb_ans = [r for r in ranked if "refused" in r]
    m = {f"hit@{k}": round(sum(1 for r in ranked if r["rank"] and r["rank"] <= k) / len(ranked), 3) for k in (1, 3, 5)}
    m |= {"mrr": round(sum(1 / r["rank"] for r in ranked if r["rank"]) / len(ranked), 3),
          "refusal_acc_out_of_kb": round(sum(r["refused"] for r in ook) / len(ook), 3),
          "false_refusal_in_kb": round(sum(r["refused"] for r in inkb_ans) / len(inkb_ans), 3) if inkb_ans else None,
          "retrieve_p50_ms": pct([r["retrieve_ms"] for r in out], .5), "retrieve_p95_ms": pct([r["retrieve_ms"] for r in out], .95),
          "answer_p95_ms": pct([r["answer_ms"] for r in out if "answer_ms" in r], .95),
          "cost_total": round(sum(r.get("cost", 0) for r in out), 6),
          "top1_mean_in_kb": round(statistics.mean(r["top1_score"] for r in ranked), 4),
          "top1_mean_out_of_kb": round(statistics.mean(r["top1_score"] for r in ook), 4)}
    return {"name": cfg["name"], "date": time.strftime("%Y-%m-%d %H:%M"), "config": snapshot(cfg), "metrics": m, "rows": out}
```

`main()`（样板让 AI 生成）：argparse `--config`（YAML，可选）、`--name`（默认 `rag-baseline`）、`--collection`（默认 `kb_default`）、`--top-k`（默认 settings）、`--with-answer`；`dataset` 默认 `REPO_ROOT/eval/datasets/kb_qa.jsonl`。写 `eval/reports/{YYYYMMDD}-{name}.json` 与 `.md`：MD 头部是配置快照表 + 指标表，再列「最差 10 题」（未命中或 rank > 5，含 `top3`），供 Day21 归因。

> 设计点：检索指标固定 top10、`score_threshold=0.0`（不受阈值影响）；库外题始终生成回答以测拒答；`--with-answer` 时库内题也生成（Day21 judge 需要），成本约 50 次调用。

### Step 4 · Makefile + 基线

`~/lab/workpilot/Makefile` 追加（缩进必须是 Tab）：

```makefile
eval-rag:
	cd apps/api && PYTHONPATH=. uv run python ../../eval/runners/run_rag_eval.py --name rag-baseline $(ARGS)
```

```bash
cd ~/lab/workpilot
make eval-rag ARGS="--with-answer"
cat eval/reports/$(date +%Y%m%d)-rag-baseline.md | head -40
```

预期指标区块形如：

```text
| hit@1 | hit@3 | hit@5 | MRR | 拒答正确率 | 库内误拒率 | 检索P95 | 回答P95 | 总成本 |
| 0.55  | 0.74  | 0.82  | 0.66 | 0.67     | 0.07      | 180ms  | 6400ms | 0.0300 |
```

（数值仅示意格式，以实际为准。）

### Step 5 · 读报告

记录到第 11 节：最差 3 题的 id 与 `top3`；in_kb 与 out_of_kb 的 top1 分数均值差距（差距越大，阈值越好定）；与蓝图 §11 目标（hit@5 ≥ 0.85、拒答 ≥ 0.80）的差距。

### Step 6 · 提交

```bash
git add eval prompts/seed_question.v1.md scripts/seed_eval.py Makefile
git status --short | grep candidates   # 候选文件可提交（无敏感内容），便于追溯审核过程
git commit -m "feat(eval): 50-question kb_qa set and retrieval metrics runner with config snapshot"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. hit@5 = 0.8、MRR = 0.4 说明什么？（答：多数能找到，但正确结果常排在 2–5 位，排序有改进空间（rerank/hybrid）。）
2. 为什么检索指标固定用 top10 而不是线上 top_k？（答：解耦检索质量与生成配置，换 top_k 不影响检索指标的可比性。）
3. 为什么库外题必须走生成？（答：拒答发生在检索阈值或生成层，只看检索无法判断是否拒答。）
4. LLM 生成的评测题有什么风险？（答：措辞贴近原文导致召回虚高、题型单一、期望答案可能错；需人工改写审核并标注来源。）
5. 报告为什么要记录 git sha 与配置快照？（答：保证可复现与可对比，否则无法判断指标变化来自哪次改动。）

## 8. 对 DA-01 的贡献

WorkPilot 有了第一份可复现的 50 题基线评测：之后每次改分块、检索、prompt 都能用同一命令得到可对比的数字，P1「评测报告存在且有基线数值」的验收项从今天开始有了数据来源。

## 9. 求职映射（D 线）

- 岗位能力：RAG 检索评测（hit@k / MRR）、评测数据构建（LLM 辅助 + 人工审核）、可复现实验。
- 对应岗位：AI Engineer、RAG Engineer、LLM Evaluation Engineer。
- 简历 bullet 草稿：「构建 50 题 RAG 评测集（库内 30 / 库外 12 / 易混淆 8，LLM 生成候选 + 人工审核改写）与自动评测 runner，输出 hit@k、MRR、拒答正确率、P95 延迟与成本并记录配置快照；基线 hit@5 = **、MRR = **。」
- 面试可能问：
  1. 「你怎么评估检索质量？」——要点：hit@k + MRR，期望来源到章节，固定 top10，三类题，报告配置快照。
  2. 「评测集是怎么造的？会不会有偏差？」——要点：LLM 生成候选的偏差 + 人工改写、跨文档题、手写库外题、种子集与扩展集。

## 10. 卡住时的处理

| 现象                                         | 处理                                                                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `ModuleNotFoundError: No module named 'app'` | 必须在 `apps/api` 目录下并设置 `PYTHONPATH=.`，或使用 `make eval-rag`                      |
| `Makefile:2: *** missing separator. Stop.`   | 命令行缩进用了空格，改成 Tab                                                               |
| `ZeroDivisionError`（拒答/误拒率）           | 某类题数为 0（如没有 `--with-answer` 时 inkb_ans 为空），已用条件返回 None；检查数据集比例 |
| hit 全为 0                                   | `expected_sources` 与 payload `source` 格式不一致；打印一题的 `top3` 对比                  |
| 跑一次要 10 分钟以上                         | `--with-answer` 会调 50 次 LLM；调试时先不加，只跑检索 + 库外题                            |
| `generate_structured` 在 seed 中频繁失败     | 资料片段过短或是代码块；`answerable=false` 的直接跳过，不重试                              |

## 11. 产出记录（执行时填写）

- 50 题比例：in_kb ** / out_of_kb ** / confusing **；llm_seed 选入 ** 道，改写 \_\_ 道
- 基线：hit@1 ** / hit@3 ** / hit@5 ** / MRR ** / 拒答 ** / 误拒 **
- top1 均值 in_kb ** vs out_of_kb **
- 检索 P95 ** ms / 回答 P95 ** ms / 总成本 ¥\_\_
- 最差 3 题：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day20（检索实验：chunk / overlap / top_k / hybrid）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（runner 与基线报告优先，实验依赖它）。
