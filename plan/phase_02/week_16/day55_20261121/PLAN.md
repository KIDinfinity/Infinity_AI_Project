# Day 55 · 2026-11-21 · Week 16 Task 1：P2 README / 架构 / 评测报告（v1.0）

## 0. 今天只做一件事

把 WorkPilot 发布为 **v1.0（P2）**：用 v1.0 候选版重跑一次全量评测拿到最终数字 → README P2 章节 + 架构图 v1 + LangGraph 图 + 评测表 + 截图 → `docs/portfolio/p2.md` → 云端部署 → tag `v1.0.0` + Release notes。

不碰：新功能、UI 重做、Demo 视频与文章（Day56）、简历（Day57）。只修阻断发布的 P0 bug。

## 1. 资产锚点

- 构建模块：M13.2 项目写作（P2 技术复盘）、M12.1 开源核心文档（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v1.0（P2 发布）**
- 今天之后 WorkPilot 多了什么（可演示/可测量）：公开仓库首页可在 3 分钟内看懂 P2（能力、架构、数字、截图）；云端运行 v1.0；GitHub Release `v1.0.0`
- 今日 AI 实际应用：用 LangGraph 自带的图导出生成真实工作流图；用 AI 起草作品集长文，自己核对每个数字与设计取舍

## 2. 起点（前置确认）

- 已有：W14 报告（`eval/reports/20261116-agent-v0.9.md`、`20261117-agent-v0.9.1.md`）、W5/W8 RAG 报告、`docs/mcp.md`、`docs/observability.md`、`docs/runbook.md`、ADR 0001–0007、W15 的 Trace/Ops 截图
- 需确认：

```bash
cd ~/lab/workpilot
git status && git log --oneline -3 && git tag | tail -3          # 工作区干净，最新 tag v0.9.0
ls eval/reports/ docs/ docs/portfolio/ docs/assets/ 2>/dev/null
make eval-smoke                                                  # 发布前必须绿
ssh <云服务器> 'cd ~/workpilot && git log --oneline -1 && docker compose -f deploy/docker-compose.prod.yml ps'
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `eval/reports/20261121-v1.0.md`：RAG 50 题 + Agent 30 任务在 v1.0 候选版上的最终数字（与 DA01 §11 目标对照）
- [ ] `docs/architecture.md` 含架构图 v1（mermaid）+ LangGraph 图（由 `draw_mermaid()` 导出）
- [ ] README 新增 P2 章节：Agent / MCP / Eval / Observability 各 3–5 行 + 评测表 + ≥ 4 张截图
- [ ] `docs/portfolio/p2.md` 覆盖 10 个小节，每个数字标注来源文件
- [ ] 云端 `/health` 返回 `1.0.0`；冒烟（问答、Agent + 审批、Trace、Ops）通过；云端 8100 端口未对外开放
- [ ] tag `v1.0.0` 已推送到 Gitea 与 GitHub；GitHub Release notes 已发布

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                       |
| ----------- | ------ | ------------------------------------------ |
| 0–5 min     | P0     | 后台启动 `make eval-full`（边跑边写文档）  |
| 5–20 min    | P0     | 导出 LangGraph 图 + 更新架构图 v1          |
| 20–50 min   | P0     | README P2 章节 + 截图整理                  |
| 50–80 min   | P0     | `docs/portfolio/p2.md`（AI 起草 → 自己改） |
| 80–90 min   | P0     | 汇总 v1.0 评测报告并回填数字               |
| 90–110 min  | P0     | 云端部署 + 冒烟                            |
| 110–120 min | P0     | CHANGELOG + tag + Release                  |

时间不足时最低保留：README P2 章节 + 评测表 + tag `v1.0.0`；`p2.md` 先写大纲 + 数字，云端部署顺延到 Day56 开头。

## 5. 今日学习（只学完成任务必须的）

- **作品集叙事顺序**：问题 → 为什么需要 Agent（而不是 RAG 就够）→ 架构 → 关键设计取舍 → 评测方法与数字 → 失败与优化 → 成本/延迟 → 部署与安全。面试官要看的是「判断力」，不是功能列表。
- **数字可追溯**：每个数字都链接到 `eval/reports/*.md`，并写明数据集规模与模型。
- **LangGraph 图导出**：`graph.get_graph().draw_mermaid()` 输出真实节点与边，比手画更可信。
- **语义化版本**：v1.0.0 表示 P2 能力稳定、对外可用；Release notes 写「新增 / 变更 / 已知限制 / 升级说明」。
- 资料：https://langchain-ai.github.io/langgraph/ （Graph API → visualization）、https://modelcontextprotocol.io/

## 6. 执行步骤

### Step 1 · 后台跑全量评测（P0，先做）

```bash
cd ~/lab/workpilot
sed -i '' 's/^version = .*/version = "1.0.0"/' apps/api/pyproject.toml     # /health 读取的版本来源按实际
(make eval-full > /tmp/eval-v1.0.log 2>&1; echo "exit=$?" >> /tmp/eval-v1.0.log) &
uv run --project apps/api python eval/runners/run_security_eval.py           # 8/8
```

结束后用 Day50 的报告脚本生成 `eval/reports/20261121-v1.0.md`（RAG + Agent + 安全 三段，含与 v0.9 对比列）。若 full 回归失败：只修 P0（或回滚导致退化的提交），不在今天做优化。

### Step 2 · LangGraph 图 + 架构图 v1

```bash
cd apps/api && uv run python -c "
from langgraph.checkpoint.memory import InMemorySaver
from app.agent.graph import build_graph
print(build_graph(checkpointer=InMemorySaver()).get_graph().draw_mermaid())" > ../../docs/assets/agent-graph.mmd
```

`docs/architecture.md` 增加「v1 架构」：以 DA01 §4 架构图为底，**只画已实现的模块**（Web / IDE(MCP) / API：Guardrail、Routes、RAG、Agent(LangGraph)、Tools(含 ext.\* MCP Client)、Gateway(预算/降级)、Obs(Trace/LLMCall)；存储：SQLite、Qdrant、MinIO；外部：LLM、Gitea、Web Search），并嵌入 `agent-graph.mmd` 内容。认证/多空间/Postgres 标注「P3 规划」。

### Step 3 · README P2 章节（结构固定，文字自己写）

```markdown
## P2 · WorkPilot Agent（v1.0）

> 从「会回答」到「会做事」：规划 → 调用工具 → 写操作人工审批 → 可评测、可观测、可嵌入 IDE。

### 能力

- **Agent（LangGraph）**：plan / act / tools / decide / synthesize；checkpoint 可恢复；会话 + 长期记忆；写工具前 interrupt 审批
- **Tools**：kb_search / web_search / gitea_repo_read / gitea_issue_read / gitea_issue_create(需审批) / calculator + 外部 MCP（ext.fs.\* 只读）
- **MCP**：WorkPilot MCP Server（stdio / streamable HTTP + token），VS Code / Cursor / Claude Desktop 可用 → [docs/mcp.md](docs/mcp.md)
- **Eval**：RAG 50 题 + Agent 30 任务 + 安全 8 条；LLM-judge 人工校准；CI 回归门禁
- **Observability & Production**：Trace/Span 瀑布图、成本账本、日预算降级/熔断、限流、Guardrail v0

### 评测结果（v1.0，详见 [eval/reports/20261121-v1.0.md](eval/reports/20261121-v1.0.md)）

| 维度             | 指标                                   | v0.9 | v1.0    | 目标               |
| ---------------- | -------------------------------------- | ---- | ------- | ------------------ |
| RAG（50 题）     | hit@5 / 引用正确率 / 拒答正确率        | \_\_ | \_\_    | 0.85 / 0.80 / 0.80 |
| Agent（30 任务） | 任务成功率 / 工具选择准确率 / 平均步数 | \_\_ | \_\_    | 0.70 / 0.85 / ≤6   |
| Agent            | P95 延迟 / 平均成本                    | \_\_ | \_\_    | —                  |
| 安全             | 未经审批写操作 / 注入用例识别          | \_\_ | 0 / 8/8 | 0                  |

### 截图

（Agent 时间线 + 审批卡片｜VS Code 中调用 MCP｜Trace 瀑布图｜Ops 看板）
```

截图放 `docs/assets/p2-*.png`，确认画面无 token、无真实邮箱/公司内容。

### Step 4 · `docs/portfolio/p2.md`（AI 起草，自己逐段改「为什么」与数字）

| 小节              | 必须回答                                                                            |
| ----------------- | ----------------------------------------------------------------------------------- |
| 1. 问题           | 哪些研发工作流 RAG 解决不了（调研、拆任务建 Issue、跨源核对）                       |
| 2. 为什么用 Agent | 何时用工作流、何时用 Agent；为什么从手写循环迁到 LangGraph（引用 W11 对比报告）     |
| 3. 架构           | 架构图 v1 + LangGraph 图 + 一次请求的数据流                                         |
| 4. 工具设计       | Registry、权限等级、description 写法、超时/截断/错误归一化、MCP 适配层              |
| 5. HITL           | interrupt → 审批 → resume；为什么写操作不暴露给 MCP；「未审批写 = 0」如何被测试证明 |
| 6. 评测方法与数字 | 30 任务设计、指标口径、judge 校准一致率、CI 门禁                                    |
| 7. Badcases       | Top 3 失败类别、真实例子（脱敏）、根因                                              |
| 8. 优化           | 修复前后对比（W14 Day51），哪些优化无效                                             |
| 9. 成本 / 延迟    | 单任务平均成本、P95、最耗时 span、预算守卫                                          |
| 10. 部署与安全    | compose + Caddy、MCP HTTP 不公开、Guardrail v0、已知限制与 P3 计划                  |

### Step 5 · 云端部署 v1.0

```bash
git add README.md docs eval/reports apps/api/pyproject.toml && git commit -m "docs(p2): README P2 section, architecture v1, portfolio p2, v1.0 eval report"
git push origin main && git push github main
ssh <云服务器>
cd ~/workpilot && ./deploy/scripts/backup.sh                       # 部署前先备份
git fetch --tags && git pull
docker compose -f deploy/docker-compose.prod.yml up -d --build
curl -s https://<你的域名>/health                                   # 预期含 "version":"1.0.0"
ss -tlnp | grep 8100 || echo "OK: MCP HTTP 未在云端监听"
```

冒烟（浏览器，Caddy basic_auth）：① 问答带引用；② Agent 研究任务 → 触发审批 → 批准（写入沙盒仓库）；③ `/traces/<id>` 有瀑布图；④ `/ops` 卡片有数据。新表（Trace/Span/LLMCall）若启动时未自动创建，执行 W7 的建表命令。

### Step 6 · CHANGELOG + tag + Release

`CHANGELOG.md` 与 `docs/release/v1.0.0.md`（Release notes 模板）：

```markdown
# WorkPilot v1.0.0（P2 · Agent）— 2026-11-21

## 新增

- LangGraph Agent（记忆、checkpoint、写操作审批）、Tool Registry + 6 内置工具
- MCP Server（stdio / HTTP + token）与 MCP Client（ext.fs 只读）
- Agent 评测（30 任务）+ LLM-judge + CI 回归门禁
- Trace/Span、成本账本、日预算守卫、限流、Guardrail v0、Ops 看板

## 指标（见 eval/reports/20261121-v1.0.md）

## 已知限制

- 单用户、无登录（Caddy basic_auth 保护）；SQLite；规则型护栏 → P3 处理

## 升级

- 新增环境变量：DAILY*BUDGET_CNY、RATELIMIT*_、MCP\__（见 .env.example）
```

```bash
git add CHANGELOG.md docs/release apps/api/pyproject.toml && git commit -m "chore(release): v1.0.0"
git tag -a v1.0.0 -m "v1.0.0: P2 WorkPilot Agent"
git push origin main --tags && git push github main --tags
```

GitHub 仓库 → Releases → Draft new release → 选 `v1.0.0` → 粘贴 `docs/release/v1.0.0.md`（或 `gh release create v1.0.0 --notes-file docs/release/v1.0.0.md`）。

## 7. 概念自检（不看资料，口述，附答案）

1. P2 比 P1 的核心增量是什么？（答：从被动问答到主动执行：工具、规划、审批、记忆、MCP；外加评测门禁与生产可观测）
2. 为什么 README 的数字必须链接报告？（答：可追溯才可信；面试官或用户能复现，避免「数字是编的」的质疑）
3. 为什么架构图只画已实现的模块？（答：作品集要诚实，规划中的部分单独标注，防止面试被追问时无法落地）
4. 部署前为什么先备份？（答：新版本引入新表与配置，出问题可在 30 分钟内用 W7 恢复流程回滚）
5. v1.0 的已知限制有哪些？（答：单用户无登录、SQLite、规则护栏、内存限流——都对应 phase_03 的计划）

## 8. 对 DA-01 的贡献

DA-01 达成第二个里程碑 **v1.0 / P2**：WorkPilot 以「可审批、可评测、可观测、可嵌入 IDE 的研发 Agent 平台」形态公开发布并在云端运行，所有数字可追溯，成为 phase_03 场景包与安全加固的稳定基线，也是 Pro Kit 与作品集的共同底座。

## 9. 求职映射（D 线）

- 岗位能力：项目叙事、架构表达、评测数据呈现、发布管理
- 对应岗位：AI Agent Engineer / AI Engineer / AI Full-Stack Engineer
- 简历 bullet 草稿：主导 WorkPilot v1.0 发布：LangGraph Agent + MCP + 评测门禁 + 可观测，30 任务成功率 **、工具选择准确率 **、P95 **s、平均成本 ¥**/任务，未经审批写操作 0 次。
- 面试可能问：
  - 什么场景你不会用 Agent？（要点：流程固定、可枚举步骤时用工作流/规则更稳更便宜；Agent 用于开放式、多源、需动态决策的任务；WorkPilot 中 kb_qa 直接走 RAG 链路）
  - 你的评测数字可信吗？（要点：数据集规模与构造、judge 校准一致率、temperature=0、样本量局限、CI 回归、真实使用日志补充）

## 10. 卡住时的处理

| 现象                              | 处理                                                                                |
| --------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------- |
| `eval-full` 回归失败              | 查看哪项超阈值 → 定位 W15 的哪个提交引起 → 修 P0 或回滚该改动；不更新基线来「过关」 |
| `draw_mermaid()` 报错或图过于复杂 | 用 `get_graph(xray=False)`；仍不行就手写 mermaid，但节点/边与代码保持一致           |
| 云端构建失败 / 内存不足           | 本地构建镜像推到私有 registry 或 `docker save                                       | ssh ... docker load`；先停 web 容器再构建 api |
| 云端新表不存在                    | 确认启动时 `create_all` 是否覆盖新模型；手动执行一次建表脚本                        |
| 截图中出现密钥/个人信息           | 重新截图或打码后再提交；已提交则改写提交前先确认是否已推送                          |
| 时间不够                          | 先打 tag（以本地验证为准），云端部署与 Release notes 顺延 Day56 开头                |

## 11. 产出记录（执行时填写）

- v1.0 评测主要数字（RAG / Agent / 安全）：\_\_\_\_
- 与 v0.9 对比的最大变化：\_\_\_\_
- 云端 `/health` 输出与冒烟结果：\_\_\_\_
- Release 链接：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day56（W16 Task 2：Demo + 技术文章 + 产品页 / 开源边界）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
