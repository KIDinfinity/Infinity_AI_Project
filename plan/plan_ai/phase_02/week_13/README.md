# Week 13 · MCP Server / Client（Phase 2 · Day46–Day48 · 11-12 → 11-14）

## 1. 本周核心目标

把 WorkPilot 的能力通过 **MCP（Model Context Protocol）** 标准化输出到 IDE，并让 WorkPilot Agent 能反向接入外部 MCP Server：

1. `apps/mcp-server`：基于官方 `mcp` Python SDK（FastMCP）的 WorkPilot MCP Server，作为**薄适配层**调用 WorkPilot HTTP API，支持 stdio 与 streamable-http（Bearer token）。
2. 在 VS Code Copilot Chat（Agent 模式）中调用 `kb_search` / `kb_ask` 成功，并录屏。
3. `app/tools/mcp_client.py`：把官方 filesystem MCP Server 的**只读**工具注册为 `ext.fs.*`，Agent 可调用。
4. 文档 `docs/mcp.md` + tag `v0.9.0`。

## 2. 资产锚点

| 构建模块                                                     | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                              |
| ------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------ |
| M8.1 WorkPilot MCP Server（stdio + streamable HTTP + token） | v0.9       | 在 VS Code 里问「用 workpilot 查我们的分支规范并总结」→ Copilot 调用 `kb_ask` → 带引用回答 |
| M8.2 MCP Client（Agent 调用外部 MCP）                        | v0.9       | WorkPilot Agent 时间线里出现 `ext.fs.read_text_file` 等外部工具调用                        |
| M13.1 / M13.4 求职                                           | —          | JD 追踪第 3 轮（MCP 频次）+ 5 道 MCP 面试题                                                |

## 3. 为什么这一周存在

- **产品侧**：DA-01 §2 的「任意 IDE 用户写代码时查团队知识」场景只能靠 MCP 实现；不做 MCP，WorkPilot 只能在浏览器里用，日常使用频次上不去。
- **工程侧**：MCP 是 Tool Layer（M6）的标准化外延——同一套工具既能给自己的 Agent 用，也能给任意 MCP Host 用；反过来外部 MCP 生态也能成为 WorkPilot 的工具。
- **求职侧**：MCP / Tool Integration 是 2025–2026 Agent 岗位 JD 的高频词，有「Server + Client + 鉴权 + 安全边界」的完整实现是强证据。

## 4. 本周在路线中的位置

```text
W12 产出：LangGraph Agent + Memory + HITL（v0.8），Tool Registry 含 read/write 权限等级
   ↓
W13 本周：MCP Server（对外暴露只读能力）+ MCP Client（接入外部工具）→ v0.9
   ↓
W14 输入：Agent 工具集（含 ext.fs.*）稳定 → 构建 30 任务 Agent 评测集与回归门禁
```

## 5. 每日安排

| Day   | 日期  | Task                                      | 当日 P0 产出                                                       | 模块            | 状态 |
| ----- | ----- | ----------------------------------------- | ------------------------------------------------------------------ | --------------- | ---- |
| Day46 | 11-12 | Task 1：MCP Server（stdio）+ Inspector    | `apps/mcp-server/server.py` 3 个工具在 Inspector 中调用成功        | M8.1            | TODO |
| Day47 | 11-13 | Task 2：IDE 接入 + HTTP 传输 + MCP Client | VS Code 调用成功；HTTP 无 token 返回 401；`ext.fs.*` 被 Agent 调用 | M8.1 M8.2       | TODO |
| Day48 | 11-14 | Task 3：MCP Demo + 文档 + JD 追踪         | 录屏 + `docs/mcp.md` + tag `v0.9.0` + 5 道 MCP 面试题              | M8 / v0.9 / M13 | TODO |

## 6. 本周必须留下的资产

| 路径                                                                                  | 说明                                                       |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `~/lab/workpilot/apps/mcp-server/pyproject.toml`、`server.py`、`auth.py`、`README.md` | MCP Server（stdio + streamable-http）                      |
| `~/lab/workpilot/apps/api/app/routes/tools.py`                                        | `POST /v1/tools/invoke`（仅 read 工具，供 MCP 适配层调用） |
| `~/lab/workpilot/apps/api/app/tools/mcp_client.py`                                    | 外部 MCP → WorkPilot 工具（`ext.fs.*`，只读白名单）        |
| `~/lab/workpilot/apps/api/tests/unit/test_mcp_client.py`                              | 白名单 / 命名空间测试                                      |
| `~/lab/workpilot/.vscode/mcp.json.example`                                            | VS Code 配置示例（不含真实 token）                         |
| `~/lab/workpilot/docs/mcp.md`                                                         | 配置 / 工具清单 / 安全说明                                 |
| `~/lab/workpilot/docs/adr/0007-mcp-adapter.md`                                        | 「MCP Server 走 HTTP API 而非 import 内部代码」决策        |
| `~/lab/projects/career/job-market.md`（第 3 轮）、`interview-questions.md`（+5）      | D 线                                                       |
| 录屏文件（本地，不进仓库，可上传后在 README 引用链接）                                | Demo                                                       |

## 7. 本周验收标准

- [ ] PASS / FAIL：`npx @modelcontextprotocol/inspector` 中列出 ≥ 3 个工具并成功调用 `kb_search`
- [ ] PASS / FAIL：VS Code Copilot Chat Agent 模式通过 `.vscode/mcp.json` 调用 WorkPilot 工具成功（截图/录屏）
- [ ] PASS / FAIL：streamable-http 模式下，无 / 错误 token 请求返回 401；正确 token 可 list tools
- [ ] PASS / FAIL：MCP Server 不暴露任何 write 工具（`/v1/tools/invoke` 对 write 工具返回 403，有测试）
- [ ] PASS / FAIL：WorkPilot Agent 一次运行中调用了 `ext.fs.*` 工具，且外部写工具（write_file 等）未被注册（有测试）
- [ ] PASS / FAIL：`docs/mcp.md` 存在，tag `v0.9.0` 已推送到 Gitea 与 GitHub
- [ ] PASS / FAIL：JD 追踪第 3 轮已记录；面试题新增 5 道 MCP 题

## 8. 求职映射

- **本周能力**：MCP Server/Client 实现、Tool Integration、传输层选择、鉴权与最小权限、IDE 集成。
- **简历 bullet 草稿**：
  - 基于官方 MCP Python SDK 实现 WorkPilot MCP Server（stdio + streamable HTTP + Bearer 鉴权），将知识库检索/问答/仓库读取以 ** 个只读工具接入 VS Code / Claude Desktop，IDE 内查询团队规范耗时从 ** 分钟降至 \_\_ 秒。
  - 实现 MCP Client 适配层，将外部 MCP Server 工具按只读白名单动态注册进 LangGraph Agent（命名空间隔离），新增外部工具接入成本 < \_\_ 行配置。
- **面试题**：
  1. MCP 解决了什么问题？和 Function Calling 是什么关系？
  2. stdio 与 streamable HTTP 传输怎么选？远程 MCP Server 的安全风险有哪些？
  3. 你的 MCP Server 为什么不直接 import 后端代码，而是调 HTTP API？

## 9. 本周禁止事项

- 不做 MCP 的 OAuth 完整授权流程（只做静态 Bearer token，OAuth 记 Backlog）。
- 不把 write 工具（`gitea_issue_create`）暴露给 MCP。
- 不接入第二个外部 MCP Server（只接 filesystem 一个，证明机制即可）。
- 不把 MCP HTTP 端口暴露到公网；不在公开仓库提交任何 token。
- 不研究 MCP sampling / elicitation / roots 等高级特性（了解名词即可）。

## 10. 时间不够时（最小保留）

- Day46：stdio Server + `kb_search` 一个工具 + Inspector 调通。
- Day47：VS Code stdio 接入成功；HTTP 鉴权与 MCP Client 可延到 Day48 前半。
- Day48：`docs/mcp.md` 最小版 + tag `v0.9.0`；录屏可用截图替代，JD 追踪可压缩为 5 条 JD。

## 11. 周复盘（Day48 填写）

- 完成：\_\_\_\_
- 未完成 / 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_
- 是否出现无效学习或范围扩张（如钻研 OAuth、sampling）：\_\_\_\_
- 下周调整（W14 Agent 评测要用的工具集是否稳定）：\_\_\_\_
