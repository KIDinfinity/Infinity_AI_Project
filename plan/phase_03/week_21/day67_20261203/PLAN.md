# Day 67 · 2026-12-03 · Week 21 Task 2：防护实现 + 审计 + 恢复演练（v1.4）

## 0. 今天只做一件事

按 Day66 基线失败清单实现防护，重跑攻击集到 20/20，加 AuditLog，完成生产恢复演练并发布 `v1.4.0`。

不碰：新功能、注入检测模型训练、付费安全服务、WAF、前端大改（只改图片渲染）。

## 1. 资产锚点

- 构建模块：M11.3 Guardrails、M11.4 审计 / 密钥 / 限流、M5.5 备份 / 恢复（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v1.4**（安全加固）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：攻击集拦截率 基线 → 1.0 的对比报告；AuditLog 可查关键操作；恢复演练用时（目标 < 30 分钟）
- 今日 AI 实际应用：把「LLM 不可信」落到工程层——工具权限、写上限、输出过滤、检索断言，不依赖模型自觉

## 2. 起点（前置确认）

- 已有：Day66 基线报告与失败清单；W15 guardrails v0；W19 RBAC；W7 `backup.sh` / `restore.sh`。
- 需确认：

```bash
cd ~/lab/workpilot
grep -A30 "失败清单" eval/reports/20261202-security-baseline.md | head -30
grep -rn "def execute\|def call" apps/api/app/tools/registry.py    # 工具执行入口（防护插入点）
ls deploy/scripts/                                                  # backup.sh restore.sh
ssh deploy@<server> 'df -h / | tail -1'                             # 恢复演练磁盘空间
```

## 3. 验收对齐（做完要能勾掉）

- [ ] 工具执行器入口统一走 `policy.authorize()`：按场景白名单 + 角色 + 单运行写上限（默认 5）
- [ ] http_fetch：仅 http/https；DNS 解析后私网 / 回环 / 链路本地 / 保留地址一律拒绝；禁自动重定向；可选域名白名单
- [ ] 输出：服务端剥离非白名单图片；前端 `img` 组件只渲染白名单主机；不渲染原始 HTML
- [ ] 检索结果空间断言失败 → 拒绝并写 AuditLog（不再是裸 assert）
- [ ] PII 脱敏（手机号 / 身份证 / 邮箱）作用于最终输出；请求体 > 64KB → 413；上传 > 10MB → 413
- [ ] 系统提示审查：无密钥 / 无权限逻辑；canary 已注入
- [ ] AuditLog 记录：login_success / login_failed / approval / tool_write / member_change
- [ ] 重跑攻击集 20/20；`eval/reports/20261203-security-v1.4.md` 有前后对比
- [ ] （P1）恢复演练计时并写入 runbook；`docs/security/risk-acceptance.md` 完成
- [ ] `v1.4.0` 已部署；rag / agent / scenario 冒烟不退化

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                               |
| ----------- | ------ | ------------------------------------------------------------------ |
| 0–20 min    | P0     | policy.py：白名单 + 写上限，接入执行器                             |
| 20–35 min   | P0     | ssrf.py 接入 http_fetch                                            |
| 35–50 min   | P0     | output_filter（图片/HTML）+ redact（PII）+ 前端 img 白名单         |
| 50–60 min   | P0     | 输入大小中间件 + 检索断言 + canary                                 |
| 60–75 min   | P0     | AuditLog 模型 + 5 个写入点                                         |
| 75–85 min   | P0     | 重跑攻击集 + 其他冒烟 → 报告                                       |
| 85–110 min  | P1     | 恢复演练（计时）+ runbook + 风险接受记录                           |
| 110–120 min | P0     | tag v1.4.0                                                         |
| 顺延        | P2     | AuditLog 页面、依赖漏洞扫描、DNS rebinding 连接级固定 IP → Backlog |

时间不足时最低保留：policy + SSRF + 输出过滤 + 输入限制 + 重跑 20/20 + tag；恢复演练最晚 Day76 前完成。

## 5. 今日学习（只学完成任务必须的）

- **最小权限（LLM06）**：工具可用性由「场景 × 角色」白名单决定，而不是由模型想调什么决定；写操作数量有硬上限。
- **SSRF 防护要点**：协议白名单 → 解析主机得到全部 IP → 任一为私网/回环/链路本地/保留即拒绝 → 禁止自动重定向（或每跳重检）→ 超时与响应大小上限。残留风险：解析与连接之间的 DNS 重绑定。
- **输出处理（LLM05）**：把 LLM 输出当作不可信用户输入——转义、剥离危险元素、外链白名单。
- **审计日志**：只追加；记录谁、何时、在哪个空间、做了什么、目标是什么；不记录密码与完整敏感内容。
- 资料：https://genai.owasp.org/ 、https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html 、https://www.postgresql.org/docs/ （pg_dump）、https://qdrant.tech/documentation/ （Snapshots）

## 6. 执行步骤

### Step 1 · 工具策略（P0，核心逻辑自己写）

```python
# app/security/policy.py
from dataclasses import dataclass, field
from app.core.config import settings

class ToolDenied(Exception): ...

SCENARIO_TOOLS = {
    "sp_b":     {"kb_search", "gitea_issue_read", "gitea_issue_create"},
    "research": {"kb_search", "web_search", "http_fetch"},
    "kb_qa":    {"kb_search"},
}
ROLE_CAN_WRITE = {"owner": True, "member": True, "viewer": False}

@dataclass
class RunBudget:
    writes: int = 0
    steps: int = 0

def authorize(tool, *, scenario: str, role: str, budget: RunBudget):
    if tool.name not in SCENARIO_TOOLS.get(scenario, set()):
        raise ToolDenied(f"tool {tool.name} not allowed in {scenario}")
    budget.steps += 1
    if budget.steps > settings.max_steps_per_run:               # LLM10
        raise ToolDenied("step budget exceeded")
    if tool.permission in ("write", "dangerous"):
        if not ROLE_CAN_WRITE.get(role, False):
            raise ToolDenied("role cannot write")
        if budget.writes >= settings.max_writes_per_run:         # 默认 5
            raise ToolDenied("write budget exceeded")
        budget.writes += 1
```

在 registry 执行器开头调用 `authorize(...)`；捕获 `ToolDenied` → AgentStep `status="denied"` + AuditLog，返回给模型一条「工具被策略拒绝」的 observation（不抛 500）。Day60 `create_issues` 中写死的 `[:5]` 改为依赖该策略。

### Step 2 · SSRF 防护（P0）

```python
# app/security/ssrf.py
import ipaddress, socket
from urllib.parse import urlparse
from app.security.policy import ToolDenied

def assert_public_url(url: str, allow_domains: set[str] | None = None) -> None:
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ToolDenied("scheme not allowed")
    host = u.hostname.lower()
    if allow_domains and not any(host == d or host.endswith("." + d) for d in allow_domains):
        raise ToolDenied("domain not in allowlist")
    port = u.port or (443 if u.scheme == "https" else 80)
    for *_, sockaddr in socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP):
        ip = ipaddress.ip_address(sockaddr[0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
                or ip.is_multicast or ip.is_unspecified):
            raise ToolDenied(f"blocked address {ip}")
```

http_fetch：调用前 `assert_public_url`；`httpx.get(url, follow_redirects=False, timeout=10)`；响应体最多读 1MB；3xx 时对 Location 再次校验后最多跟 2 跳。

### Step 3 · 输出过滤 + PII（P0）

```python
# app/security/output_filter.py
import re
IMG = re.compile(r'!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?[^)]*\)')
ALLOWED_IMG_HOSTS = {"workpilot.example.com"}          # 自有域名，按部署配置
def strip_external_images(md: str) -> str:
    def repl(m):
        host = re.sub(r"^https?://([^/:?#]+).*$", r"\1", m.group(2))
        return m.group(0) if host in ALLOWED_IMG_HOSTS else f"[图片已移除: {m.group(1) or 'external'}]"
    return IMG.sub(repl, md)

def strip_html(md: str) -> str:
    return re.sub(r"<\s*/?\s*(script|img|iframe|object|embed|svg)[^>]*>", "", md, flags=re.I)

# app/security/redact.py
PII = [(re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[手机号]"),
       (re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"), "[身份证号]"),
       (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[邮箱]")]
def redact(text: str) -> str:
    for pat, rep in PII:
        text = pat.sub(rep, text)
    return text
```

在 Gateway 最终输出（流式在完成后对整段再处理 + 前端兜底）依次调用 `strip_html → strip_external_images → redact`。前端 react-markdown：`components={{ img: SafeImg }}`，`SafeImg` 只渲染白名单主机；确认未启用 `rehype-raw`。

> 流式输出的过滤：逐块输出时外链图片可能先被渲染——前端 `SafeImg` 是必须的第二道防线。

### Step 4 · 输入限制 + 检索断言 + canary（P0）

```python
# app/main.py 中间件
@app.middleware("http")
async def limit_body(request, call_next):
    cl = int(request.headers.get("content-length") or 0)
    limit = 10 * 1024 * 1024 if request.url.path.startswith("/v1/kb/ingest") else 64 * 1024
    if cl > limit:
        return JSONResponse({"detail": "payload too large"}, status_code=413)
    return await call_next(request)
```

- 检索：Day62 的 `assert all(...)` 改为：发现不匹配 → 丢弃该结果 + `audit("retrieval_violation", ...)` + 记录 error 日志。
- 系统提示：通读 `prompts/*.md`，确认无密钥、无「你只能对 owner 做 X」之类权限描述（权限在代码层）；系统提示末尾注入 `{SYSTEM_CANARY}`（从 `.env` 读取）。

### Step 5 · AuditLog（P0）

```python
class AuditLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    workspace_id: uuid.UUID | None = Field(default=None, index=True)
    user_id: uuid.UUID | None = None
    action: str            # login_success|login_failed|approval|tool_write|tool_denied|member_change|retrieval_violation
    target: str | None = None
    detail: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    ip: str | None = None

def audit(session, action, *, ctx=None, target=None, **detail): ...
```

写入点：login 成功/失败（失败只记 email 哈希或前 3 位）、resume 审批（批准/拒绝 + 任务数）、写工具成功、ToolDenied、成员增删改。迁移：`alembic revision --autogenerate -m "audit log"`。

### Step 6 · 重跑 + 报告 + 风险接受（P0 / P1）

```bash
make eval-security && make eval-smoke     # 安全 20/20；rag/agent/scenario 冒烟不退化
```

`eval/reports/20261203-security-v1.4.md`：基线 vs v1.4 按 id 对比表 + 每个修复对应的代码文件。

`docs/security/risk-acceptance.md`（剩余写入风险）：

```markdown
| 风险                                 | 为什么接受               | 补偿控制                               | 复审时间 |
| ------------------------------------ | ------------------------ | -------------------------------------- | -------- |
| 用户审批时未细看就批准注入产生的任务 | 人审是最终决定           | 写上限 5、幂等、AuditLog、Issue 可关闭 | 2027-03  |
| DNS 重绑定（解析后与连接时 IP 不同） | 实现连接级 IP 固定成本高 | 域名白名单优先、超时、仅公网工具       | 2027-03  |
| LLM 在流式输出中短暂显示外链文本     | 前端不渲染外链图片       | SafeImg 白名单 + 服务端完成后过滤      | 2027-03  |
```

### Step 7 · 恢复演练（P1，计时）

```bash
# 服务器上（或一台新机器 / 本机干净目录）
time ( \
  docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U workpilot -Fc workpilot > pg.dump && \
  curl -s -X POST "http://localhost:6333/collections/workpilot_chunks/snapshots" && \
  docker run --rm --network host -e MINIO_USER -e MINIO_PASS -v $PWD/minio-bak:/bak --entrypoint sh minio/mc -c 'mc alias set s http://localhost:9000 $MINIO_USER $MINIO_PASS && mc mirror s/workpilot /bak' \
)
# 恢复：新目录 → compose up postgres qdrant minio → pg_restore -d workpilot pg.dump
#      → Qdrant 上传 snapshot 恢复 collection → mc mirror 回写 → up api worker web → /ready + 登录 + 问 1 题
```

> collection 名、MinIO bucket 以实际为准；Qdrant 端口若只在容器网络内，用 `docker compose exec` 或临时端口映射。SqliteSaver 的 checkpoint 文件（volume）一并复制。

runbook 记录：开始时间、每步耗时、总耗时（目标 < 30 分钟）、遇到的问题与修正。

### Step 8 · 发布

```bash
git add apps/api apps/web/src docs/security eval/reports/20261203-security-v1.4.md docs/runbook.md
git commit -m "feat(security): tool policy, ssrf guard, output filtering, pii redaction and audit log"
git push && git tag -a v1.4.0 -m "v1.4.0: OWASP LLM hardening, 20/20 attack suite, audit log" && git push origin v1.4.0
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么工具白名单按「场景」而不是全局？（答：最小权限——SP-B 不需要 http_fetch，开放即增加被注入利用的面）
2. 写上限为什么在策略层而不是 prompt 里？（答：prompt 可被注入绕过；代码层硬上限是确定性控制）
3. 为什么 SSRF 要禁自动重定向？（答：公网 URL 可 302 到内网地址，绕过首次校验）
4. 服务端已过滤图片，为什么前端还要 SafeImg？（答：流式片段可能在服务端最终过滤前到达；纵深防御）
5. 审计日志为什么不能记录密码或完整文档内容？（答：审计日志本身会成为敏感数据泄露点，只记必要元数据）
6. 恢复演练为什么要计时而不只是「能恢复」？（答：RTO 是可承诺的运维指标；不计时无法发现慢步骤，也无法支撑 < 30 分钟的承诺）

## 8. 对 DA-01 的贡献

WorkPilot 达到蓝图 §11 的安全指标（20/20、未经审批写操作 0）和运维指标（恢复 < 30 分钟），v1.4 是可以对外开放 Demo（W23）和售卖 Pro Kit（W22）的安全前提。

## 9. 求职映射（D 线）

- 岗位能力：LLM 应用纵深防御、SSRF 防护、最小权限、审计、灾备演练。
- 对应岗位：AI Platform Engineer、AI Engineer、后端（安全意识强）。
- 简历 bullet 草稿：「实现场景 × 角色工具白名单、单运行写上限、SSRF 私网阻断、Markdown 外链过滤与 PII 脱敏，攻击用例拦截率 ** → 100%；恢复演练 ** 分钟」
- 面试可能问：
  1. 如何限制 Agent 的破坏半径？——要点：工具最小集、权限分级、审批、配额/上限、沙盒目标、审计与可撤销。
  2. RTO/RPO 是什么，你的系统是多少？——要点：RTO=恢复耗时（演练 \_\_ 分钟），RPO=可丢数据窗口（取决于备份频率，如每日备份 = 24h）。

## 10. 卡住时的处理

| 现象                                     | 处理                                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| 加策略后正常场景也被拒                   | 检查 SCENARIO_TOOLS 名称与 registry 中工具名一致；先跑 `make eval-smoke` 定位               |
| `getaddrinfo` 在测试中慢或失败           | 测试里 monkeypatch `socket.getaddrinfo` 返回固定 IP                                         |
| 正则误伤（如代码块中的长数字被当身份证） | 只对自然语言输出启用；代码块（```）内跳过，记录为已知局限                                   |
| 流式输出过滤后前后不一致                 | 服务端在 done 事件中发送过滤后的最终文本，前端用它替换                                      |
| pg_restore 报角色不存在                  | `pg_restore --no-owner --role=workpilot`；恢复前先建同名用户（compose 环境变量已建）        |
| 演练超过 30 分钟                         | 记录瓶颈步骤（常见：镜像拉取、向量快照上传），写入 runbook 优化项；指标以实测为准，不改数字 |

## 11. 产出记录（执行时填写）

- 攻击集：基线 **/20 → v1.4 **/20
- 其他冒烟：rag ** / agent ** / scenario \_\_（是否退化）
- AuditLog 事件类型数：\_\_
- 恢复演练：备份 ** min / 恢复 ** min / 总计 \_\_ min
- 风险接受条数：\_\_
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day68 · W22 Task 1「Badcase 总库 + 回归套件 + Eval v2」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（20/20 + tag）；恢复演练未完成则列入 Day76 前必做。
