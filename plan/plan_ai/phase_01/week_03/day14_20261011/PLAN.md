# Day 14 · 2026-10-11 · Week 03 Task 4：LLM 应用 v0 + 10 题冒烟（v0.1）

## 0. 今天只做一件事

交付 WorkPilot v0.1：一个**无检索**的「技术文档助手 v0」（`POST /v1/ask` + 流式版），用 10 题冒烟量化它的表现，并把观察到的幻觉写成首批 Badcase，打 tag `v0.1.0`。

不碰：向量检索 / 语料（W4）、自动化评分（W5）、前端（W6）。

## 1. 资产锚点

- 构建模块：v0.1 发布（集成 M1.3–M1.6）、M3.1 数据集规范（冒烟集雏形）、M3.4 Badcase 库（首批）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5、§9）
- 版本里程碑：**v0.1**（tag `v0.1.0`）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`/v1/ask` 返回结构化回答并标注来源；10 题冒烟报告（平均延迟、总成本、低置信比例）；≥3 条幻觉 Badcase
- 今日 AI 实际应用：结构化输出 + 流式 + 成本记录组合成第一个 LLM 应用；用「团队内部知识」题暴露幻觉 → 作为 W4 RAG 的对照组基线

## 2. 起点（前置确认）

- 已有：Day11 `generate_structured` + `StructuredAnswer`、Day12 `gateway.stream()` + SSE、Day13 `da01-definition.md`（主场景）。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
uv run pytest -m "not llm" -q
grep -n "主场景\|SP-" ../../docs/product/da01-definition.md | head
uv run uvicorn app.main:app --reload --port 8000     # 另开终端
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `POST /v1/ask` 返回 `{answer: StructuredAnswer, source_note: "来源：模型通用知识（未接入知识库）", prompt, usage, cost, latency_ms}`
- [ ] `POST /v1/ask/stream` 用 `curl -N` 可见 token 流，`done` 事件含 `source_note`
- [ ] `eval/datasets/smoke_v0.jsonl` 10 行，可被 `json.loads` 逐行解析
- [ ] `eval/reports/20261011-smoke-v0.1.md` 存在：10 行结果 + 平均延迟 + 总成本 + low 置信占比
- [ ] `eval/badcases/badcases.md` ≥ 3 条幻觉案例
- [ ] README 有 v0.1 章节；`git tag` 有 `v0.1.0` 并已 push
- [ ] Week 3 README 第 11 节已填写

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                           |
| ------- | ------ | ------------------------------ |
| 0–25    | P0     | `qa_answer.v0.md` + `/v1/ask`  |
| 25–40   | P1     | `/v1/ask/stream`               |
| 40–55   | P0     | 写 10 题冒烟集                 |
| 55–75   | P0     | `run_smoke.py` + 跑报告        |
| 75–95   | P0     | 人工阅读答案，写 ≥3 条 badcase |
| 95–110  | P0     | README v0.1 + tag              |
| 110–120 | P1     | Week 3 复盘                    |

时间不足时最低保留：`/v1/ask` + 10 题 + 报告 + 3 条 badcase + tag（流式版与 README 美化顺延）。

## 5. 今日学习（只学完成任务必须的）

- 「冒烟测试」只回答「能不能跑、明显问题是什么」，不是正式评测；正式指标在 W5。
- 幻觉最容易出现在**模型不可能知道的私有知识**（你们团队的规范、你自己的项目约定）上，这正是 RAG 要解决的。
- 置信度自报（`confidence`）不可靠：要对照真实答案看「高置信但错误」的比例。
- 版本 tag 用附注标签（`git tag -a`），记录版本说明，便于 Gitea Release。
- 资料：https://api-docs.deepseek.com/ 、https://git-scm.com/book/en/v2/Git-Basics-Tagging 、https://docs.python.org/3/library/json.html

## 6. 执行步骤

### Step 1 · Prompt v0 + /v1/ask

`prompts/qa_answer.v0.md`：

```markdown
---
id: qa_answer
version: 0
model: deepseek-chat
changelog:
  - "v0 2026-10-11: 无检索版本，仅依赖模型通用知识（v0.1 基线）"
---

你是 WorkPilot 技术文档助手，服务对象是一名全栈/前端工程师。
规则：

1. 只回答研发相关问题（前端、后端、工程化、团队研发流程）。
2. 你没有接入任何团队内部文档。凡是涉及「我们团队 / 我们项目 / 公司内部」的约定，必须说明你无法确认，confidence 设为 low，needs_more_context 设为 true。
3. 不确定时直说不确定，不要编造 API、配置项或版本号。
4. 回答用中文，先结论后理由。
```

`apps/api/app/routes/ask.py`：

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.llm.gateway import gateway
from app.llm.prompts import load_prompt
from app.llm.schemas import StructuredAnswer
from app.llm.structured import StructuredError, generate_structured
from app.routes.chat import sse

router = APIRouter(prefix="/v1", tags=["ask"])
SOURCE_NOTE = "来源：模型通用知识（未接入知识库）"
PROMPT = "qa_answer.v0"

class AskReq(BaseModel):
    question: str = Field(min_length=2, max_length=2000)

def _messages(q: str) -> list[dict]:
    return [{"role": "system", "content": load_prompt(PROMPT).render()},
            {"role": "user", "content": q}]

@router.post("/ask")
async def ask(req: AskReq):
    try:
        data, res = await generate_structured(StructuredAnswer, _messages(req.question))
    except StructuredError:
        raise HTTPException(502, "structured output failed")
    return {"answer": data, "source_note": SOURCE_NOTE, "prompt": load_prompt(PROMPT).ref,
            "usage": res.usage, "cost": res.cost, "latency_ms": res.latency_ms, "request_id": res.request_id}

@router.post("/ask/stream")
async def ask_stream(req: AskReq):
    async def gen():
        try:
            async for ev in gateway.stream(_messages(req.question)):
                if ev["type"] == "token":
                    yield sse("token", {"text": ev["text"]})
                else:
                    r = ev["result"]
                    yield sse("done", {"source_note": SOURCE_NOTE, "usage": r.usage.model_dump(),
                                       "cost": r.cost, "latency_ms": r.latency_ms, "ttft_ms": r.ttft_ms})
        except Exception:
            yield sse("error", {"message": "LLM 调用失败，请稍后重试"})
    return StreamingResponse(gen(), media_type="text/event-stream")
```

注意：`generate_structured` 会在前面再插一条「结构化输出」system 消息，两条 system 消息共存没问题；流式版输出自然语言，不要求 JSON。

```bash
curl -s localhost:8000/v1/ask -H 'Content-Type: application/json' \
  -d '{"question":"Vite 的 import.meta.env 和 process.env 有什么区别？"}' | python -m json.tool
curl -N -X POST localhost:8000/v1/ask/stream -H 'Content-Type: application/json' \
  -d '{"question":"我们团队的 commit message 规范要求 scope 怎么写？"}'
```

### Step 2 · 10 题冒烟集

`eval/datasets/smoke_v0.jsonl`（题目围绕 Day13 主场景调整；必须包含 ≥3 道「只有你的文档里才有答案」的题，答案写在 `expected` 里供人工对照）：

```json
{"id":"s01","question":"React 中 useEffect 依赖数组为空时什么时候执行？","type":"public","expected":"组件挂载后执行一次，卸载时执行清理函数","tags":["react"]}
{"id":"s02","question":"FastAPI 中如何声明一个可选的查询参数？","type":"public","expected":"参数默认值设为 None，可配合 Annotated/Query","tags":["fastapi"]}
{"id":"s03","question":"Vite 中只有什么前缀的环境变量会暴露给客户端代码？","type":"public","expected":"VITE_ 前缀","tags":["vite"]}
{"id":"s04","question":"WorkPilot 仓库的提交信息规范是什么？","type":"private","expected":"以 PROJECT_STANDARD.md 为准（Conventional Commits …）","tags":["standard"]}
{"id":"s05","question":"WorkPilot 的 .env.example 里价格相关的配置键有哪些？","type":"private","expected":"PRICE_CURRENCY / PRICE_INPUT_HIT_PER_M / PRICE_INPUT_MISS_PER_M / PRICE_OUTPUT_PER_M","tags":["config"]}
```

其余 5 题：2 道公开题（主场景相关）、2 道私有题（如「我们的前端代码评审规范里对组件命名有什么要求？」——引用你 Day13 计划重写的规范样例）、1 道库外/无关题（如「今天上海天气怎样？」，期望拒答或说明超出范围）。

### Step 3 · 冒烟脚本

`scripts/run_smoke.py`（样板可让 AI 生成；统计逻辑自己核对）：

```python
import json, statistics, time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]
API = "http://localhost:8000/v1/ask"

def main() -> None:
    text = (ROOT / "eval/datasets/smoke_v0.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    out = []
    with httpx.Client(timeout=90) as c:
        for r in rows:
            resp = c.post(API, json={"question": r["question"]})
            if resp.status_code != 200:
                out.append({**r, "status": resp.status_code}); continue
            d = resp.json()
            out.append({**r, "status": 200, "summary": d["answer"]["answer"][:60].replace("\n", " "),
                        "confidence": d["answer"]["confidence"], "latency_ms": d["latency_ms"],
                        "cost": d["cost"] or 0.0})
    ok = [o for o in out if o["status"] == 200]
    lines = [f"# Smoke v0.1 · {time.strftime('%Y-%m-%d')}", "",
             "| id | type | 答案摘要 | 置信度 | 延迟ms | 成本 | 人工判定 |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {o['id']} | {o['type']} | {o.get('summary','ERR')} | {o.get('confidence','-')} | "
              f"{o.get('latency_ms','-')} | {o.get('cost','-')} | ☐对 ☐错 ☐幻觉 |" for o in out]
    lines += ["", f"- 成功 {len(ok)}/{len(out)}；平均延迟 {statistics.mean(o['latency_ms'] for o in ok):.0f} ms；"
              f"总成本 {sum(o['cost'] for o in ok):.6f}；low 置信占比 "
              f"{sum(o['confidence']=='low' for o in ok)/max(len(ok),1):.0%}"]
    report = ROOT / f"eval/reports/{time.strftime('%Y%m%d')}-smoke-v0.1.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
```

```bash
cd ~/lab/workpilot && uv run --project apps/api python scripts/run_smoke.py
```

然后打开报告，逐行对照 `expected` 勾「对 / 错 / 幻觉」。

### Step 4 · 首批 Badcase

`eval/badcases/badcases.md`（W4 Day18 会扩展成完整模板，今天先用简版，字段向后兼容）：

```markdown
# Badcase 库

| ID     | 版本 | 问题                                 | 现象                                                                 | 期望                        | 根因分类            | 修复思路                 | 状态 |
| ------ | ---- | ------------------------------------ | -------------------------------------------------------------------- | --------------------------- | ------------------- | ------------------------ | ---- |
| BC-001 | v0.1 | WorkPilot 仓库的提交信息规范是什么？ | 编造了 "type(scope): ..." 外加不存在的 JIRA 编号要求，confidence=mid | 以 PROJECT_STANDARD.md 为准 | 数据缺失 / 生成幻觉 | W4 接入知识库 + 拒答规则 | open |
```

至少 3 条；重点记录「**高/中置信但错误**」的案例——这是 RAG 前后对比的核心证据。

### Step 5 · README v0.1 + tag

README 追加：

```markdown
## v0.1（2026-10-11）· LLM 应用 v0

- 能力：结构化输出（/v1/structured/\*）、流式（/v1/chat/stream）、成本记录（data/logs/llm_calls.jsonl）、CLI（scripts/chat.py）、文档助手 v0（/v1/ask，无检索）
- 冒烟：10 题，平均延迟 ** ms，总成本 ¥**，私有知识题幻觉 **/** → 见 eval/badcases/badcases.md
- 已知限制：未接入知识库，团队内部问题无法可靠回答（W4 RAG 解决）
```

```bash
cd ~/lab/workpilot
git add prompts apps/api eval scripts README.md
git commit -m "feat(ask): document assistant v0 with smoke eval and first badcases"
git tag -a v0.1.0 -m "v0.1.0: LLM gateway (structured/stream/cost) + assistant v0"
git push && git push origin v0.1.0
```

在 Gitea Web UI → 仓库 → Releases 确认能看到 `v0.1.0`。

### Step 6 · Week 3 复盘（P1）

填写 `plan/phase_01/week_03/README.md` 第 11 节；`PROJECT_CONFIG.md` 当前周如需推进到第 4 周，周一开工时再改。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 v0.1 要故意做「无检索」版本？（答：建立对照基线，量化幻觉，证明 RAG 的必要性与收益。）
2. 冒烟测试和正式评测的区别？（答：冒烟看能否跑通与明显问题，样本少、人工判；正式评测有数据集规范、指标、可重复。）
3. 为什么模型自报的 confidence 不可信？（答：模型并不知道自己是否正确，常出现高置信幻觉；需与真实答案对照校准。）
4. 「数据缺失」和「生成幻觉」两个根因有什么区别？（答：前者是模型根本没有该知识，后者是有/无知识都编造；v0 中私有题多属前者导致后者。）
5. 附注 tag 与轻量 tag 的区别？（答：附注 tag 有作者、日期、说明，适合发版。）

## 8. 对 DA-01 的贡献

WorkPilot 有了第一个可演示版本 v0.1 和第一份量化数据（延迟、成本、幻觉比例），同时得到了 W4 RAG 的明确验收目标：把 Badcase 中「私有知识题」从幻觉变为带引用的正确回答或明确拒答。

## 9. 求职映射（D 线）

- 岗位能力：LLM 应用端到端交付、基线评测意识、Badcase 驱动迭代。
- 对应岗位：AI Engineer、GenAI Application Engineer。
- 简历 bullet 草稿：「交付 LLM 文档助手 v0（结构化 + 流式），以 10 题冒烟建立无检索基线：私有知识题幻觉率 **%、平均延迟 **ms、单次成本 ¥\_\_，据此立项 RAG 并定义改进目标。」
- 面试可能问：
  1. 「你怎么证明 RAG 有用？」——要点：先建无检索基线 → 同一题集对比 → 幻觉率、引用正确率、拒答率的前后变化。
  2. 「Badcase 怎么管理？」——要点：编号、版本、现象/期望、根因分类、修复思路、状态；修复后转成回归用例。

## 10. 卡住时的处理

| 现象                                          | 处理                                                                                                  |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/v1/ask` 返回 502 `structured output failed` | 看 uvicorn 日志里的 ValidationError；多为 `confidence` 取值不在枚举内，prompt 中明确写出 low/mid/high |
| `KeyError: prompt qa_answer.v0 缺少变量`      | v0 prompt 不应含 `{xxx}`；若误写了花括号示例，改为不带标识符的形式                                    |
| 冒烟脚本 `httpx.ReadTimeout`                  | `timeout=90` 仍超时说明回答过长，prompt 限制字数；或检查网络/代理                                     |
| 报告里 `cost` 全为 0                          | Day12 价格未配置，`.env` 填价格后重跑（报告注明）                                                     |
| `git push origin v0.1.0` 报 `rejected`        | 远端已存在同名 tag：不要强推，改用 `v0.1.1` 并在 CHANGELOG 说明                                       |
| 模型对私有题都老实说「不知道」，找不到幻觉    | 也是有效结论：记录为「过度保守 / 无法作答」类 badcase，同样证明需要知识库                             |

## 11. 产出记录（执行时填写）

- 10 题：对 ** / 错 ** / 幻觉 **；高置信错误 ** 条
- 平均延迟 / 总成本：\_**\_ ms / ¥\_\_**
- Badcase 编号：\_\_\_\_
- tag 是否已 push：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE → Week 03 完成，明天进入 Day15（W4 Task 1：语料准备 + Ingest）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（tag 与 badcase 优先）。
