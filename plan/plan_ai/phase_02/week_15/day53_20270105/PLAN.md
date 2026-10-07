# Day 53 · 2027-01-05 · Week 15 Task 2：成本账本 + 预算守卫 + 限流

## 0. 今天只做一件事

给 WorkPilot 装上「钱包和闸门」：LLM 调用写入 `LLMCall` 表（迁移历史 jsonl），每次调用前检查当日预算（>80% 降级、>100% 拒绝 `BUDGET_EXCEEDED`），用 slowapi 按 IP 限流，并把超时 / 重试 / 限流 / 预算参数集中到配置与 runbook。

不碰：看板 UI（Day54）、Redis、按用户/空间计费（W19 后）、告警推送（邮件/IM）。

## 1. 资产锚点

- 构建模块：M9.2 Token / 成本账本 + 日预算守卫、M9.3 限流 / 超时 / 重试集中管理、M1.5 成本计量（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v1.0 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`DAILY_BUDGET_CNY=0.01` 演示「先降级、再拒绝」；1 分钟内第 21 次 ask 返回 429；任何一天的 LLM 花费可一条 SQL 查出并按 trace 归因
- 今日 AI 实际应用：LLM 成本治理与弹性设计 → 让 WorkPilot 可以安全地长期运行与公开演示

## 2. 起点（前置确认）

- 已有：Gateway（chat/stream/structured、pricing、重试、fallback）写 `data/logs/llm_calls.jsonl`；Day52 `trace_id_var`；W7 compose prod（Caddy → api）
- 需确认：

```bash
cd ~/lab/workpilot
wc -l data/logs/llm_calls.jsonl && head -1 data/logs/llm_calls.jsonl | jq .     # 字段名
grep -rn "timeout\|max_retries\|retry" apps/api/app/core/config.py apps/api/app/llm/*.py | head -20   # 散落的参数
grep -n "uvicorn" deploy/docker-compose.prod.yml apps/api/Dockerfile                 # 启动参数（代理头）
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `LLMCall` 表建立；迁移脚本执行后行数 = jsonl 有效行数；新调用实时入表（含 trace_id）
- [ ] `budget_decision()` 单测覆盖 ok / degrade / reject；接口级测试：预算耗尽时 `/v1/kb/ask` 返回 429 + `{"code":"BUDGET_EXCEEDED"}`
- [ ] 降级时日志出现 `budget_degrade` 且实际使用 `BUDGET_DEGRADE_MODEL`
- [ ] slowapi：ask 20/min、agent run 5/min（可配置）；测试证明超限返回 429 `RATE_LIMITED`
- [ ] `docs/runbook.md` 有「超时 / 重试 / 限流 / 预算」参数表与预算告警处理步骤
- [ ] Day49 runner 的 usage 统计改为读 `LLMCall`；`make eval-smoke` 通过；已提交

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                          |
| ----------- | ------ | --------------------------------------------- |
| 0–10 min    | P0     | 设计：表字段、日边界（Asia/Shanghai）、错误码 |
| 10–35 min   | P0     | `LLMCall` 表 + Gateway 写入 + 迁移脚本        |
| 35–60 min   | P0     | `cost.py` 预算守卫 + Gateway 接入 + 测试      |
| 60–85 min   | P0     | slowapi 接入 + 代理 IP + 测试                 |
| 85–105 min  | P0     | 配置集中 + runbook 参数表                     |
| 105–120 min | P0     | runner 改读表 + eval-smoke + 提交             |

时间不足时最低保留：`LLMCall` 写入 + 100% 拒绝 + ask 限流；降级、迁移脚本顺延到 Day54 开头。

## 5. 今日学习（只学完成任务必须的）

- **成本账本**：每次 LLM 调用一行（模型、tokens、单价计算的成本、trace_id、用途），是预算、归因、看板的唯一事实来源。
- **预算守卫的位置**：放在 Gateway 调用前（所有入口都经过），而不是各路由里分别判断。
- **降级 vs 拒绝**：软阈值切便宜模型保可用，硬阈值拒绝保钱包；两者都必须留日志。
- **slowapi**：基于 `limits` 库，装饰器 `@limiter.limit("20/minute")`，路由函数必须有 `request: Request` 参数；反向代理后要让 uvicorn 信任 `X-Forwarded-For`，否则所有人共享 Caddy 的 IP。
- **超时 / 重试集中**：一个配置对象 + 一张 runbook 表，避免「改一处漏三处」。
- 资料：https://slowapi.readthedocs.io/

## 6. 执行步骤

### Step 1 · `LLMCall` 表 + Gateway 写入

```python
class LLMCall(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    trace_id: str | None = Field(default=None, index=True)
    workspace: str = Field(default="default", index=True)
    provider: str
    model: str = Field(index=True)
    purpose: str = "chat"                      # chat / kb_ask / agent / judge / eval
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_cny: float = 0.0
    latency_ms: int = 0
    ok: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
```

Gateway 记录处：`trace_id = trace_id_var.get() or request_id_var.get()`（评测脚本没有 trace，用 request_id），写入用 `await asyncio.to_thread(...)`；jsonl 写入改为 `LLM_JSONL_LOG=false` 时关闭（默认关闭）。

迁移脚本 `scripts/migrate_llm_calls.py`（AI 生成，自己审字段映射）：表非空则退出（除非 `--force`，保证幂等）；逐行读 jsonl，坏行计数跳过；映射 `ts->created_at(UTC)`、`cost->cost_cny`、`request_id->trace_id` 等；每 500 行提交；打印 migrated / skipped。

```bash
uv run --project apps/api python scripts/migrate_llm_calls.py --dry-run
uv run --project apps/api python scripts/migrate_llm_calls.py
sqlite3 data/workpilot.db "select count(*), round(sum(cost_cny),4) from llmcall;"   # 表名按实际
```

### Step 2 · 预算守卫 `app/obs/cost.py`（核心逻辑自己写）

```python
from datetime import datetime, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from sqlmodel import Session, func, select

from app.core.config import settings
from app.core.errors import AppError
from app.db.models import LLMCall
from app.db.session import engine

TZ = ZoneInfo("Asia/Shanghai")

class BudgetExceeded(AppError):
    status_code, code = 429, "BUDGET_EXCEEDED"

def budget_decision(spent: float, budget: float, degrade_ratio: float) -> Literal["ok", "degrade", "reject"]:
    if budget <= 0:
        return "ok"                                    # 0 或负数 = 不限（仅本地开发）
    ratio = spent / budget
    if ratio >= 1.0:
        return "reject"
    return "degrade" if ratio >= degrade_ratio else "ok"

def today_spent() -> float:
    start = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    with Session(engine) as db:
        return float(db.exec(select(func.coalesce(func.sum(LLMCall.cost_cny), 0.0))
                             .where(LLMCall.created_at >= start)).one())
```

Gateway 每次调用前：

```python
spent = await asyncio.to_thread(today_spent)
match budget_decision(spent, settings.daily_budget_cny, settings.budget_degrade_ratio):
    case "reject":
        log.warning("budget_reject", extra={"spent": spent, "budget": settings.daily_budget_cny})
        raise BudgetExceeded(f"今日 LLM 预算已用尽（¥{spent:.2f}/¥{settings.daily_budget_cny}）")
    case "degrade":
        log.warning("budget_degrade", extra={"spent": spent, "from": model, "to": settings.budget_degrade_model})
        model = settings.budget_degrade_model
```

SSE 接口中遇到 `BudgetExceeded`：发送 `event: error` + `{"code":"BUDGET_EXCEEDED"}` 后结束流；前端显示「今日额度已用完」。

### Step 3 · slowapi 限流

`cd apps/api && uv add slowapi`。`app/obs/ratelimit.py`（约 12 行）：`limiter = Limiter(key_func=get_remote_address, enabled=settings.ratelimit_enabled)`；`rate_limit_handler(request, exc: RateLimitExceeded)` 返回 `JSONResponse({"code": "RATE_LIMITED", "detail": str(exc.detail)}, status_code=429)`。

`main.py`：`app.state.limiter = limiter`；`app.add_exception_handler(RateLimitExceeded, rate_limit_handler)`。路由：

```python
@router.post("/ask")
@limiter.limit(lambda: settings.ratelimit_kb_ask)        # "20/minute"
async def ask(request: Request, body: AskReq): ...

@router.post("/run")
@limiter.limit(lambda: settings.ratelimit_agent_run)     # "5/minute"
async def run(request: Request, body: AgentRunReq): ...
```

反向代理：`deploy/docker-compose.prod.yml` 中 api 启动命令加 `--proxy-headers --forwarded-allow-ips="*"`（api 不直接暴露公网，只有 Caddy 能访问，因此可信任转发头）。

### Step 4 · 配置集中 + runbook

`core/config.py` 统一字段（示例默认值）：

| 参数                | 环境变量                                        | 默认                 | 作用               | 何时调整         |
| ------------------- | ----------------------------------------------- | -------------------- | ------------------ | ---------------- |
| LLM 超时            | `LLM_TIMEOUT_S`                                 | 60                   | 单次 LLM 请求超时  | 长输出报告超时   |
| LLM 重试            | `LLM_MAX_RETRIES` / `LLM_BACKOFF_BASE_S`        | 2 / 1                | 指数退避（1s、2s） | 供应商不稳定     |
| 工具超时            | `TOOL_TIMEOUT_S`                                | 20                   | 单个工具执行上限   | web_search 慢    |
| 工具输出截断        | `TOOL_OUTPUT_MAX_CHARS`                         | 8000                 | 防上下文爆炸       | 长文件读取       |
| Agent 步数 / 总时长 | `AGENT_MAX_STEPS` / `AGENT_RUN_TIMEOUT_S`       | 8 / 180              | 防死循环           | 评测步数超限     |
| 限流                | `RATELIMIT_KB_ASK` / `RATELIMIT_AGENT_RUN`      | 20/minute / 5/minute | 按 IP              | 公开 Demo 前收紧 |
| 日预算              | `DAILY_BUDGET_CNY`                              | 3                    | 硬上限             | 按月预算 ÷ 30    |
| 降级阈值 / 模型     | `BUDGET_DEGRADE_RATIO` / `BUDGET_DEGRADE_MODEL` | 0.8 / 备用便宜模型   | 软阈值             | —                |

把此表写入 `docs/runbook.md`，并加「预算告警处理」：① 查 `LLMCall` 当日按 purpose / trace 汇总；② 定位异常 trace；③ 临时调高预算需记录原因；④ 次日 0 点（Asia/Shanghai）自动恢复。`.env.example` 同步新增键。

### Step 5 · 测试

`tests/unit/test_budget.py`：

```python
@pytest.mark.parametrize("spent,expected", [(0.0, "ok"), (0.79, "ok"), (0.8, "degrade"), (1.0, "reject"), (5, "reject")])
def test_budget_decision(spent, expected):
    assert budget_decision(spent, 1.0, 0.8) == expected

def test_ask_rejected_when_budget_exhausted(client, monkeypatch):
    monkeypatch.setattr("app.llm.gateway.today_spent", lambda: 999.0)
    r = client.post("/v1/kb/ask", json={"question": "x"})
    assert r.status_code == 429 and r.json()["code"] == "BUDGET_EXCEEDED"
```

`tests/unit/test_ratelimit.py`：

```python
def test_ask_rate_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "ratelimit_kb_ask", "2/minute")
    monkeypatch.setattr("app.routes.kb.answer_question", fake_answer)   # 不打真实 LLM
    limiter.reset()
    codes = [client.post("/v1/kb/ask", json={"question": "x"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
```

（其他测试在 conftest 中 `RATELIMIT_ENABLED=false`，避免互相影响。）

### Step 6 · 收尾

- Day49 `usage_from_llm_log()` 改为查 `LLMCall where trace_id = rid`。
- 手动演示：`DAILY_BUDGET_CNY=0.01 make dev` → 连续提问，记录 degrade / reject 日志。

```bash
uv run --project apps/api pytest apps/api/tests -q && make eval-smoke
git add apps/api scripts/migrate_llm_calls.py docs/runbook.md .env.example deploy eval/runners
git commit -m "feat(obs): LLM cost ledger, daily budget guard and rate limiting"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 预算检查为什么放在 Gateway 而不是路由？（答：Gateway 是所有 LLM 调用的唯一出口（问答、Agent、judge），放这里不会漏，路由层分散判断易遗漏）
2. 日预算的「今天」按什么时区？为什么？（答：按 Asia/Shanghai 本地日；数据库存 UTC，查询时把本地 0 点换算成 UTC，避免早 8 点才「重置」）
3. 反向代理后限流为什么会失效？（答：后端看到的远端地址都是 Caddy，所有用户共享一个桶；需 `--proxy-headers` 并只信任代理）
4. 降级会影响评测结果吗？怎么处理？（答：会；评测时预算应足够或单独配置，报告中记录实际模型，Trace 的 model 属性可核对）
5. 限流用内存存储有什么局限？（答：多进程/多实例不共享计数、重启清零；当前单实例单 worker 可接受，扩容时换 Redis 存储）

## 8. 对 DA-01 的贡献

WorkPilot 具备成本可控的生产属性（M9.2/M9.3）：任何一天的花费可查、可归因、有硬上限，滥用请求会被限流——这是 W23 公开在线 Demo 与 Pro Kit「生产部署包」的必要条件，也让半年 LLM 预算（≈ ¥300）有技术保障。

## 9. 求职映射（D 线）

- 岗位能力：LLM 成本治理、限流与弹性、配置管理、运维手册
- 对应岗位：AI Platform Engineer / Backend AI Engineer / LLMOps
- 简历 bullet 草稿：设计 LLM 成本账本与日预算守卫（80% 自动降级至低价模型、100% 熔断），结合按接口限流与集中化超时/重试配置，将日均 LLM 成本稳定在 ¥\_\_ 以内。
- 面试可能问：
  - 怎么防止 Agent 把预算烧光？（要点：步数/总时长上限、工具输出截断、日预算硬上限、降级模型、限流、Trace 定位异常运行）
  - 限流算法有哪些？slowapi 用的是哪种？（要点：固定窗口、滑动窗口、令牌桶；slowapi 基于 limits 库，默认固定窗口，可配置移动窗口）

## 10. 卡住时的处理

| 现象                                                                               | 处理                                                                                  |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| slowapi 报 `parameter 'request' must be an instance of starlette.requests.Request` | 路由函数缺少 `request: Request` 参数，或参数名不是 `request`                          |
| 装饰器不生效                                                                       | `@router.post` 必须在 `@limiter.limit` 之上；确认 `app.state.limiter` 已设置          |
| 测试之间限流互相干扰                                                               | 每个测试前 `limiter.reset()`；默认在 conftest 关闭限流，只在限流测试中开启            |
| 迁移后成本总和与 jsonl 不一致                                                      | 检查坏行与单位（元 vs 分）；先 `--dry-run` 打印前 3 行映射结果                        |
| 预算降级模型不可用                                                                 | 降级模型调用失败时走 Gateway 已有 provider fallback；仍失败则返回明确错误，不无限重试 |

## 11. 产出记录（执行时填写）

- 迁移行数 / 历史总成本：\_\_\_\_
- 预算演示日志（degrade / reject 时间点）：\_\_\_\_
- 限流测试结果：\_\_\_\_
- runbook 参数表是否完整：\_\_\_\_
- eval-smoke 结果：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day54（W15 Task 3：Guardrail v0 + Ops 看板）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
