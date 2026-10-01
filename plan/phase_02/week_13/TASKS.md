# Week 13 · TASKS

## Task 1：MCP Server（stdio）+ Inspector（Day46 · 11-12）

### 做什么

新建 `apps/mcp-server`（独立 uv 项目），用官方 `mcp` SDK 的 FastMCP 写 WorkPilot MCP Server，提供 `kb_search`、`kb_ask`、`gitea_repo_read` 三个只读工具；这些工具只通过 httpx 调 WorkPilot HTTP API。后端补一个 `POST /v1/tools/invoke`（只允许 read 工具）。用 MCP Inspector 列出并调用工具。

### 为什么做

DA-01 F4「IDE 集成」的第一步；把 M6 工具层以标准协议对外输出。适配层解耦后，API 升级不影响 MCP Server，MCP Server 也可单独分发（Pro Kit 候选）。

### 资产锚点

M8.1 · 为 v0.9 做准备

### 前置依赖

- WorkPilot API 本地可运行（`make dev` 或 `uv run uvicorn app.main:app --port 8000`），`/v1/kb/ask` 可用，知识库已有语料（含 `PROJECT_STANDARD.md` 分支规范）。
- Node.js ≥ 18（Inspector 与 filesystem server 依赖 `npx`）。

### 具体执行步骤（概要，详见 day46_20261112/PLAN.md）

1. 学 MCP 架构 4 个概念（Host/Client/Server、tools/resources/prompts、传输、JSON-RPC）。
2. 后端补 `/v1/kb/search`（若无）与 `/v1/tools/invoke`（read-only）。
3. `uv init` + `uv add "mcp[cli]" httpx`，写 `server.py`。
4. `uv run mcp dev server.py` 打开 Inspector，逐个调用工具。
5. P2：resource `workpilot://docs/{doc_id}`、prompt `research_brief`。
6. 提交。

### 验收标准

- [ ] Inspector 中 Tools 列表出现 3 个工具，`kb_search` 返回带来源的结果
- [ ] `POST /v1/tools/invoke` 调 `gitea_issue_create` 返回 403（pytest 覆盖）
- [ ] `server.py` 中无 `from app...` 的 import（`grep` 验证）
- [ ] stdout 不被日志污染（日志只写 stderr）

### 完成后的产出（文件路径）

`apps/mcp-server/{pyproject.toml,uv.lock,server.py,README.md}`、`apps/api/app/routes/tools.py`、`apps/api/tests/unit/test_tools_invoke.py`

### 求职映射

MCP Server 实现 / 工具协议设计 / 解耦适配层 → AI Agent Engineer、LLM Application Engineer。

### 如果时间不够 / 没有必要

只做 `kb_search` 一个工具 + Inspector 调通；resource / prompt 延期到 W16 后或进 Backlog。

---

## Task 2：IDE 接入 + HTTP 传输 + MCP Client（Day47 · 11-13）

### 做什么

1. 写 `.vscode/mcp.json`（stdio）让 VS Code Copilot Chat Agent 模式调用 WorkPilot；给出 Claude Desktop 配置示例。
2. 加 streamable-http 传输（127.0.0.1:8100，`/mcp`）+ Bearer token 校验中间件。
3. 后端新增 `app/tools/mcp_client.py`：用 `ClientSession + stdio_client` 连接官方 filesystem server（指向公开 docs 目录），只读白名单工具注册为 `ext.fs.*`（permission=read），Agent 可调用。

### 为什么做

Task 1 只证明协议能跑；本任务证明「真实 Host 能用」（日常效率）+「WorkPilot 能吃外部生态」（M8.2）。鉴权是远程 MCP 的底线安全要求。

### 资产锚点

M8.1 M8.2 · 为 v0.9 做准备

### 前置依赖

Task 1 完成；VS Code 已开启 Copilot Chat，且能使用 Agent 模式；准备一个**只含公开内容**的目录（如 `~/lab/workpilot/data/sample/public-docs`）。

### 具体执行步骤（概要，详见 day47_20261113/PLAN.md）

1. `.vscode/mcp.json` stdio 接入 → Copilot Agent 模式提问验证。
2. `auth.py` 纯 ASGI Bearer 中间件 + `--transport http` 启动参数 → curl 验证 401/200。
3. `mcp_client.py`：`MCPToolset.start()` → `list_tools()` → 白名单过滤 → 注册 `ext.fs.*`；FastAPI lifespan 管理生命周期。
4. Agent 跑一个需要读本地公开文档的任务，时间线中看到 `ext.fs.*`。
5. 单测 + 提交。

### 验收标准

- [ ] VS Code Copilot Chat 中出现 WorkPilot 工具调用确认并返回结果
- [ ] `curl` 无 token → 401；带正确 token 的 MCP 客户端可 list tools
- [ ] Agent 运行记录（AgentStep）中有 `ext.fs.*` 调用
- [ ] 单测证明 `write_file` / `edit_file` / `move_file` 未被注册

### 完成后的产出（文件路径）

`.vscode/mcp.json.example`、`apps/mcp-server/auth.py`、`apps/api/app/tools/mcp_client.py`、`apps/api/tests/unit/test_mcp_client.py`、`.env.example`（新增 `MCP_HTTP_TOKEN`、`MCP_FS_ROOT`）

### 求职映射

IDE 集成、MCP 传输与鉴权、外部工具生态接入、最小权限 → AI Agent Engineer / AI Platform Engineer。

### 如果时间不够 / 没有必要

P0 = VS Code stdio 接入 + MCP Client；HTTP 鉴权可推迟到 Day48 前 30 分钟；Claude Desktop 只写配置示例不实测。

---

## Task 3：MCP Demo + 文档 + JD 追踪（v0.9）（Day48 · 11-14）

### 做什么

录 1–2 分钟屏：VS Code 中「用 workpilot 查我们的分支规范并总结」→ 工具调用 → 回答。写 `docs/mcp.md`（VS Code / Cursor / Claude Desktop 配置、工具清单、安全说明）+ ADR 0007。JD 追踪第 3 轮（关注 MCP 频次）；面试题 +5 道 MCP。tag `v0.9.0`；周复盘。

### 为什么做

没有文档和演示，MCP 能力对用户与面试官都不可见；JD 追踪验证「MCP 是否值得作为 P2 卖点」。

### 资产锚点

M8 / **v0.9** / M13.1 M13.4

### 前置依赖

Task 1、Task 2 的 P0 完成。

### 具体执行步骤（概要，详见 day48_20261114/PLAN.md）

1. 录屏脚本 + 录制。
2. `docs/mcp.md` + ADR 0007 + README 链接。
3. JD 追踪第 3 轮（≥ 10 条 JD）。
4. 面试题 +5。
5. CHANGELOG + tag `v0.9.0` + 推送 Gitea / GitHub。
6. 周复盘。

### 验收标准

- [ ] 录屏文件存在且展示完整「提问 → 工具调用 → 带引用回答」
- [ ] `docs/mcp.md` 含 3 种 Host 配置、工具清单表、安全说明 5 条
- [ ] `job-market.md` 有第 3 轮记录与 MCP 出现频次统计
- [ ] `interview-questions.md` 新增 5 道 MCP 题（含答题要点）
- [ ] `git tag` 中有 `v0.9.0`，GitHub 可见；gitleaks 无告警

### 完成后的产出（文件路径）

`docs/mcp.md`、`docs/adr/0007-mcp-adapter.md`、`CHANGELOG.md`、`~/lab/projects/career/job-market.md`、`~/lab/projects/career/interview-questions.md`、`plan/phase_02/week_13/README.md` 第 11 节

### 求职映射

技术文档能力、Demo 表达、市场洞察 → 所有 AI 应用岗位。

### 如果时间不够 / 没有必要

录屏可用 3 张截图替代；JD 追踪最少 5 条；Cursor 配置只写一句「与 VS Code 同格式，文件 `.cursor/mcp.json`、顶层键 `mcpServers`」。

---
