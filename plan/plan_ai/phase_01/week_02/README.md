# Week 02 · 能力矩阵 + FastAPI + LLM Gateway + 存储与备份（Phase 1 · Day06–Day10 · 10-03 → 10-07）

## 1. 本周核心目标

1. **D 线**：用 10 个真实 JD 建立 AI 岗位能力矩阵 v1，每项能力映射到 WorkPilot 的证明模块（M13.1）。
2. **B 线**：在 `workpilot/apps/api` 起 FastAPI 骨架，并写出 LLM Gateway v0：`POST /v1/chat` 经 DeepSeek 返回，带超时、指数退避重试、token / 延迟记录（M1.1 M1.2）。
3. **C 线**：MinIO + Qdrant 以 compose 运行，Ollama 本地 bge-m3 出 1024 维向量，冒烟脚本跑通（M0.4）；写备份 / 恢复脚本并完成一次恢复演练（M0.5）。
4. **A 线**：痛点池补到 ≥ 10 条、加初评分列，为 W3 Day13 选型准备（M10）。

## 2. 资产锚点

| 项                            | 内容                                                                                                                                                                                                                                                                              |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 构建模块                      | M13.1 能力矩阵、M1 前置（FastAPI 骨架）、M1.1 Provider 抽象、M1.2 可靠性（timeout / retry）、M0.4 对象存储 + 向量库、M0.5 备份恢复、M10 痛点分类                                                                                                                                  |
| 版本里程碑                    | 为 **v0.1** 做准备（W3 Day14 打 `v0.1.0`）；本周不打 tag                                                                                                                                                                                                                          |
| 本周结束 WorkPilot 能演示什么 | `make dev` 启动 API → `/docs` 页面 → `curl /v1/chat` 得到 DeepSeek 回答并在日志看到 tokens / latency_ms；把超时调到 0.001 秒得到结构化 504；`make test` 全绿；`smoke.py` 演示「文件进 MinIO、向量进 Qdrant、语义查询命中」；`restore.sh` 把删掉的仓库 / collection / 对象恢复回来 |

## 3. 为什么这一周存在

W3 的结构化输出、流式、成本记录，W4 的 RAG，全部建立在「一个可靠的 LLM 调用层 + 一个能存原文和向量的存储层」之上。能力矩阵则让 B 线的每一步都有 JD 证据，避免「学了但简历写不出来」。备份恢复提前到 W2，是因为从本周起 Gitea / MinIO / Qdrant 开始承载真实资产。

## 4. 本周在路线中的位置

```text
上周产出（W1）：Docker + Gitea + ai-project-template + workpilot v0.0.0 + pain-pool v0（≥8 条）
   ↓
本周（W2）：能力矩阵 v1 → FastAPI /health → LLM Gateway /v1/chat → MinIO+Qdrant+bge-m3 → 备份恢复 + 痛点 ≥10
   ↓
下周输入（W3）：
  - app/llm/gateway.py（Day11 加 Structured Output，Day12 加 SSE 流式与成本记录）
  - Qdrant + bge-m3 已验证（W4 Day16 Chunking + 入库直接复用）
  - pain-pool v1（≥10 条，含问题类型与初评分占位）→ Day13 场景选型
  - capability-matrix v1 → 每 2 周更新（W9 Day36 首次 JD 追踪）
```

## 5. 每日安排

| Day | 日期  | Task                                   | 当日 P0 产出                                                                  | 模块       | 状态   |
| --- | ----- | -------------------------------------- | ----------------------------------------------------------------------------- | ---------- | ------ |
| 06  | 10-03 | Task 1：AI 岗位能力矩阵 v1             | `projects/career/{capability-matrix.md,job-market.md}`，10 条 JD，Top-12 能力 | M13.1      | 已完成 |
| 07  | 10-04 | Task 2：Python 工具链 + FastAPI 骨架   | `apps/api` `/health` + pytest + ruff + `make dev/test/lint`                   | M1 前置    | 已完成 |
| 08  | 10-05 | Task 3：LLM Gateway v0                 | `app/llm/gateway.py` + `POST /v1/chat` + 重试 / 超时测试                      | M1.1 M1.2  | 已完成 |
| 09  | 10-06 | Task 4：MinIO + Qdrant + Ollama bge-m3 | `infra/compose/docker-compose.yml` + `ai-lab/storage-smoke/smoke.py` 通过     | M0.4       | 已完成 |
| 10  | 10-07 | Task 5：备份恢复 + 痛点分类 + 周复盘   | `infra/scripts/{backup,restore}.sh` + 恢复演练记录 + 痛点 ≥10                 | M0.5 / M10 | 已完成 |

## 6. 本周必须留下的资产（文件路径级）

| 资产                            | 路径                                                                                                    |
| ------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 能力矩阵 / JD 记录 / 面试题骨架 | `~/lab/projects/career/{capability-matrix.md,job-market.md,interview-questions.md,resume/README.md}`    |
| FastAPI 应用                    | `~/lab/workpilot/apps/api/{pyproject.toml,uv.lock,app/main.py,app/core/config.py,app/routes/health.py}` |
| LLM Gateway                     | `~/lab/workpilot/apps/api/app/llm/{gateway.py,schemas.py}`、`app/routes/chat.py`、`app/core/errors.py`  |
| 测试                            | `~/lab/workpilot/apps/api/tests/{test_health.py,test_llm_gateway.py}`                                   |
| 存储编排                        | `~/lab/projects/infra/compose/docker-compose.yml`（`.env` 不提交）                                      |
| 存储冒烟                        | `~/lab/projects/ai-lab/storage-smoke/smoke.py`                                                          |
| 备份恢复                        | `~/lab/projects/infra/scripts/{backup.sh,restore.sh}`、`infra/backup-drill.md`                          |
| 痛点池 v1                       | `~/lab/projects/product-lab/pain-pool.md`（≥ 10 条）                                                    |

## 7. 本周验收标准

- [x] **PASS**：`career/capability-matrix.md` 含 10 条 JD 统计后的 Top-12 能力，每项有 WorkPilot 证明模块（Top-12 行已编号；源数据 `jd-skills.jsonl` + `tally.py`）
- [x] **PASS**：`cd ~/lab/workpilot && make test && make lint` 全部通过（`6 passed, 1 deselected`；`All checks passed!` / `15 files already formatted`）
- [x] **PASS**：`curl -s localhost:8000/health` 返回 `{"status":"ok","env":"dev","version":"0.0.1"}`；`/docs` → 200
- [x] **PASS（附条件）**：`curl /v1/chat` 返回回答，响应含 `prompt_tokens` / `completion_tokens` / `latency_ms`（实测 `model=deepseek-flash`，875 ms）。
  - ⚠️ 当前 `.env` 里 `LLM_PROVIDER=doubao`，而豆包账号返回 `403 AccountOverdueError`（欠费），故 `:8000/v1/chat` 现在返回结构化 502 `llm_upstream_error`。
  - 修复只需一行：`LLM_PROVIDER=deepseek`（本项验收即用 `LLM_PROVIDER=deepseek` 覆盖启动 `:8001` 完成验证，未改动 `.env`）。
- [x] **PASS**：`LLM_TIMEOUT_S=0.001` 时返回 HTTP 504 + `{"error":{"code":"llm_timeout","message":"上游模型响应超时"}}`；响应与 `/tmp/api8002.log` 中 `grep -c 'sk-'` = 0（不含 API key）
- [x] **PASS（附说明）**：`git -C ~/lab/workpilot log -p --all | grep -c 'sk-'` = 1，但唯一命中是测试里的**故意假密钥** `FAKE_KEY = "sk-test-should-never-leak"`（用于断言错误响应不泄露 key）；`~/lab/projects` = 0。**无真实密钥入库**。
- [x] **PASS**：`smoke.py` 输出 MinIO sha256 一致、Qdrant top-1 命中预期句子（复验：`smoke` collection `points_count` = 6；`mc cat workpilot-raw/smoke/hello.md` 返回原文）
- [x] **PASS**：恢复演练完成，被删的 `test_repo1`（`test-repo` 不存在，改用 Day02 的 public 练习仓库）/ `smoke` collection / MinIO 对象全部恢复，耗时已记录（备份停机 1 s，恢复 **3 s**，远低于 30 分钟目标）→ 详见 `infra/backup-drill.md`
- [x] **PASS**：痛点池 10 条，问题类型全部填写，含「初评分」列（初评分合计 ≈ 440 分钟/周）

## 8. 求职映射

- **本周能力**：JD 拆解；Python / FastAPI / Pydantic；LLM API 调用、超时重试、错误归一化；向量库 / 对象存储；备份恢复。
- **简历 bullet 草稿**：
  - 基于 FastAPI + OpenAI 兼容 SDK 实现多供应商 LLM Gateway，统一超时、指数退避重试与错误码，记录每次调用的 token 与延迟，上游超时时返回结构化 504，单测覆盖 \_\_ 个故障场景。
  - 以 Docker Compose 搭建 MinIO + Qdrant + Ollama(bge-m3) 本地 AI 数据底座，编写备份 / 恢复脚本，恢复演练耗时 \_\_ 分钟。
- **面试题**：
  1. LLM 调用哪些错误该重试、哪些不该？（要点：超时 / 连接 / 429 / 5xx 重试；400 / 401 / 内容过滤不重试；指数退避 + 上限；关掉 SDK 自带重试避免叠加）
  2. 为什么原文放对象存储、向量放向量库，而不是都放数据库？（要点：大文件 / 二进制 / 可追溯原文 vs 高维 ANN 检索 + payload 过滤；各自擅长）
  3. 你的备份方案如何验证是有效的？（要点：定期恢复演练、校验和、恢复后功能验证、记录 RTO）

## 9. 本周禁止事项

- 不做 Structured Output / 流式 / 成本计价（W3）；不做 RAG 分块、入库（W4）。
- 不引入 LangChain / LlamaIndex；LLM 调用只走自己的 Gateway。
- 不在 `.env` 以外的任何地方写真实 API key（包括测试代码、日志、聊天记录、截图）。
- 不把任何公司数据发给 DeepSeek 或写进 Qdrant / MinIO。
- 不为 MinIO / Qdrant 做集群、TLS、权限细化；不写 Dockerfile（W7）。
- 能力矩阵不变成学习清单：JD 里出现但 WorkPilot 用不到的技术，只记录不安排。

## 10. 时间不够时（最小保留）

1. Day07 + Day08 的 P0（FastAPI + `/v1/chat` + 超时 / 重试单测）—— 本周最高优先，W3 直接依赖。
2. Day09 P0：Qdrant + bge-m3 冒烟（MinIO 部分可顺延到 Day10 前半）。
3. Day10 P0：`backup.sh` 能产出备份 + 至少恢复一项（Qdrant collection）。
4. Day06：可压缩为 6 条 JD + Top-10 能力，W3 末补到 10 条。
5. 痛点池补到 ≥ 10 条**必须**在 Day13 前完成。

## 11. 周复盘（周末填写）

- 完成：
  - D 线：`career/{capability-matrix.md, job-market.md, jd-skills.jsonl, tally.py, interview-questions.md, resume/}`，10 条 JD → Top-12 能力，11/12 有 WorkPilot 证明模块。
  - B 线：`apps/api` FastAPI 骨架（`/health`、`/docs`、pytest、ruff、`make dev/test/lint`）+ LLM Gateway v0（`/v1/chat`、超时、指数退避重试、错误归一化、token / latency 记录）。
  - C 线：`infra/compose/docker-compose.yml`（MinIO + Qdrant）、`ai-lab/storage-smoke/smoke.py`（bge-m3 1024 维）、`infra/scripts/{backup.sh,restore.sh}` + 一次完整恢复演练。
  - A 线：`product-lab/pain-pool.md` v1，10 条 + 问题类型 + 初评分列。
- 未完成：本机外的离线备份副本（Step 6 / P1）。　原因：`/Volumes` 下只有两个只读 DMG，无外置可写盘；iCloud Drive 未开启 → 无可用离线目标。
- WorkPilot 本周多了什么可演示的东西：`make dev` → `/docs` → `curl /v1/chat` 拿到带 token / latency 的回答；`LLM_TIMEOUT_S=0.001` 得到结构化 504；`make test` / `make lint` 全绿；一条命令产出带 SHA256 的备份、一条命令恢复并 3 项健康检查；`restore.sh` 把删掉的仓库 / collection / 对象全部恢复。
- DeepSeek 本周花费：未逐日记账（本周实际由 `LLM_PROVIDER=doubao` 承载，豆包账号已欠费）。查询 `GET /user/balance`：余额 **¥52.00**（`total_balance` = `topped_up_balance`，即基本未消耗）。
- 恢复演练耗时：**3 秒**（备份停机 1 秒；数据量 ~9 MB，RTO 目标 < 30 分钟）
- 是否出现无效学习或范围扩张：**出现了 2 处，已收敛**。
  1. 豆包（火山方舟）供应商接入属于 W2 之外的扩展，且因账号欠费反而使 `/v1/chat` 在默认配置下不可用（建议改回 `LLM_PROVIDER=deepseek`）。
  2. `restore.sh` 第一版照 plan 原文「整目录 mv 留底」，在 Docker Desktop(macOS) 上踩到 bind mount inode 问题，多花了约 20 分钟返工——这是必要的排障，不算浪费，但说明「照抄脚本」前应先理解容器挂载语义。
- 能力矩阵差距最大的 3 项：
  1. **Tool Calling / Agent**（出现 6/10，全必需，0 → 3，W9–W10）
  2. **RAG**（出现 10/10，必需 9，0 → 3，W4–W5）
  3. **Vector DB**（出现 6/10，必需 5，0 → 2，W4）
  - 紧随其后：LangChain / LangGraph（6/10，全必需，0 → 2，W11）。
- 下周调整：
  1. 把 `.env` 的 `LLM_PROVIDER` 改回 `deepseek`（或给豆包账号充值）——否则 W3 的 Structured Output、SSE 流式都会卡在上游 403。
  2. 给 Day10 Step 6 的离线副本找落点（U 盘 / 外置盘），或明确接受「仅本机备份」的风险并写进 `backup-drill.md`。
  3. MinIO root 凭据与 DeepSeek key 存入 macOS 钥匙串（W2 未做）。
  4. 24h 内清理 6 个 `.before-restore-*` 留底目录，回收磁盘。
  5. W3 起 A 线为核心，冻结基础设施扩张（`PROJECT_CONFIG.md` §4 已明确）。
