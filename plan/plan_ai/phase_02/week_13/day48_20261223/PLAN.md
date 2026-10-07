# Day 48 · 2026-12-23 · Week 13 Task 3：MCP Demo + 文档 + JD 追踪（v0.9）

## 0. 今天只做一件事

把本周的 MCP 能力变成「别人看得见、照着能配」的资产：1 段录屏 + `docs/mcp.md` + ADR，tag `v0.9.0`；顺带完成 JD 追踪第 3 轮与 5 道 MCP 面试题，做周复盘。

不碰：新增 MCP 工具、OAuth、云端部署 MCP HTTP、视频剪辑与配音美化。

## 1. 资产锚点

- 构建模块：M8.1 M8.2（文档化与发布）、M13.1 JD 追踪、M13.4 面试题库（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.9**（MCP Server / Client）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：可复现的 MCP 配置文档（3 种 Host）、1–2 分钟演示录屏、GitHub 上的 `v0.9.0` tag；面试题库 +5、JD 中 MCP 出现频次有数据
- 今日 AI 实际应用：用 MCP 在 IDE 中查团队规范（真实工作流演示）→ 作为 P2 作品集素材

## 2. 起点（前置确认）

- 已有：Day46 Server（stdio）、Day47 VS Code 接入 + HTTP 鉴权 + `ext.fs.*`
- 需确认：

```bash
cd ~/lab/workpilot
git status && git log --oneline -5
git tag | tail -3                              # 上一个应是 v0.8.0
ls ~/lab/projects/career/                      # job-market.md / interview-questions.md
grep -c "^### " ~/lab/projects/career/interview-questions.md   # 当前题数（按你的标题格式）
which gitleaks || brew install gitleaks
```

- 若 Day47 HTTP 鉴权未完成：先用 30 分钟补完（P0），再录屏。

## 3. 验收对齐（做完要能勾掉）

- [ ] 录屏（1–2 分钟）展示：VS Code Agent 模式提问 → `kb_ask`/`kb_search` 调用确认 → 带引用回答
- [ ] `docs/mcp.md` 含：工具清单表、VS Code / Cursor / Claude Desktop 配置、HTTP 模式、安全说明 ≥ 5 条、排障
- [ ] `docs/adr/0007-mcp-adapter.md` 存在，README 有 MCP 章节链接
- [ ] `job-market.md` 第 3 轮 ≥ 10 条 JD，含 MCP 出现频次与前两轮对比
- [ ] `interview-questions.md` 新增 5 道 MCP 题（含答题要点）
- [ ] gitleaks 无告警；tag `v0.9.0` 已推送到 Gitea 与 GitHub
- [ ] 本周 README 第 11 节周复盘已填写

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                   |
| ----------- | ------ | -------------------------------------- |
| 0–20 min    | P0     | 录屏（按脚本录 2 遍，选 1 遍）         |
| 20–55 min   | P0     | `docs/mcp.md` + ADR 0007 + README 链接 |
| 55–80 min   | P1     | JD 追踪第 3 轮                         |
| 80–95 min   | P0     | 5 道 MCP 面试题                        |
| 95–110 min  | P0     | CHANGELOG + gitleaks + tag + push      |
| 110–120 min | P0     | 周复盘                                 |

时间不足时最低保留：`docs/mcp.md` 最小版（工具清单 + VS Code 配置 + 安全说明）+ tag `v0.9.0`；录屏可用 3 张截图替代，JD 追踪压缩为 5 条。

## 5. 今日学习（只学完成任务必须的）

- Cursor 的 MCP 配置在项目 `.cursor/mcp.json`（或全局 `~/.cursor/mcp.json`），顶层键 `mcpServers`，格式与 Claude Desktop 一致。
- 文档的读者是「第一次接触 WorkPilot 的开发者」：先给能复制的配置，再讲原理。
- MCP 安全话术要能落到具体机制：鉴权、只读默认、白名单、不可信输出、审计。
- 资料：https://modelcontextprotocol.io/ （Security Best Practices 一节）、https://code.visualstudio.com/docs/copilot/chat/mcp-servers

## 6. 执行步骤

### Step 1 · 录屏（macOS `Cmd+Shift+5`）

脚本（先在纸上过一遍）：

1. 终端已启动 WorkPilot API（画面一角可见）。
2. VS Code 打开 `workpilot` 仓库 → Copilot Chat → Agent 模式 → 展示工具列表中的 workpilot 工具。
3. 输入：「用 workpilot 查我们的分支规范并总结」。
4. 展示工具调用确认 → 展开参数与返回 → 最终回答中的引用来源（`PROJECT_STANDARD.md`）。
5. （可选 10 秒）Web AgentPage 时间线中的 `ext.fs.read_text_file` 调用。

保存到 `~/lab/workpilot-media/mcp-demo-v0.9.mov`（不进仓库；Day56 上传后在 README 引用链接）。

### Step 2 · `docs/mcp.md`（结构自己定，内容可让 AI 起草后逐条核对）

```markdown
# WorkPilot MCP 集成

## 1. 能做什么

在 VS Code / Cursor / Claude Desktop 中直接查询团队知识库与仓库；WorkPilot Agent 也能调用外部 MCP 工具。

## 2. 工具清单（MCP Server 暴露）

| 工具            | 权限 | 输入               | 输出               | 调用的 API            |
| --------------- | ---- | ------------------ | ------------------ | --------------------- |
| kb_search       | read | query, top_k(1–10) | 带来源与分数的片段 | POST /v1/kb/search    |
| kb_ask          | read | question           | 带引用编号的答案   | POST /v1/kb/ask       |
| gitea_repo_read | read | owner, repo, path  | 文件文本           | POST /v1/tools/invoke |

（P2：resource `workpilot://docs/{doc_id}`、prompt `research_brief`）

## 3. 快速配置

### 3.1 VS Code（`.vscode/mcp.json`，顶层 `servers`）

### 3.2 Cursor（`.cursor/mcp.json`，顶层 `mcpServers`）

### 3.3 Claude Desktop（`~/Library/Application Support/Claude/claude_desktop_config.json`，顶层 `mcpServers`）

### 3.4 HTTP 模式（`uv run server.py --transport http`，127.0.0.1:8100/mcp，Bearer token）

## 4. 安全说明

1. 默认 stdio，仅本机；HTTP 模式默认只监听 127.0.0.1，必须设置 ≥32 字符 token，否则拒绝启动。
2. 只读默认：MCP 不暴露任何 write 工具；后端 `/v1/tools/invoke` 白名单 + permission=read 双重校验。
3. 写操作（如创建 Issue）只能在 WorkPilot Agent 内经人工审批执行，不经 MCP。
4. 外部 MCP 工具（`ext.*`）按白名单注册，输出一律标记为不可信数据。
5. token 不进仓库：VS Code 用 `${input:...}` 运行时输入；`.env` 已 gitignore。
6. 不要将 MCP HTTP 端口直接暴露到公网；如需远程，经 Caddy HTTPS + token。

## 5. MCP Client（外部工具）

`MCP_FS_ROOT=<公开目录>` 启用官方 filesystem server，只注册只读工具为 `ext.fs.*`。

## 6. 排障

（复制 Day46/47 PLAN 第 10 节中真实遇到的条目）
```

`docs/adr/0007-mcp-adapter.md`：

```markdown
# ADR 0007：MCP Server 作为 HTTP 适配层

- 状态：Accepted（2026-12-23）
- 背景：需要把 WorkPilot 能力接入 IDE；可选「MCP Server import 后端代码」或「调用 HTTP API」。
- 决策：独立 uv 项目 apps/mcp-server，只通过 HTTP 调 WorkPilot API；只暴露 read 工具。
- 理由：复用后端权限/审计/超时；依赖隔离；可单独分发；安全边界清晰。
- 代价：多一跳网络（本机 < \_\_ ms）；需要维护 API 契约。
- 备选：直接 import（拒绝：耦合、易绕过权限）；OAuth（推迟：单用户场景静态 token 足够）。
```

README 增加「MCP（IDE 集成）」小节：2 句话 + 链接 `docs/mcp.md`。

### Step 3 · JD 追踪第 3 轮（P1）

在 `~/lab/projects/career/job-market.md` 追加：

```markdown
## 第 3 轮 · 2026-12-23（关注 MCP）

| #   | 岗位（公司可匿名） | 城市 | 薪资 | RAG | Agent/LangGraph | MCP | Eval | Observability | 备注           |
| --- | ------------------ | ---- | ---- | --- | --------------- | --- | ---- | ------------- | -------------- |
| 1   | AI 应用工程师      | 上海 | \_\_ | ✔   | ✔               | ✔   | —    | —             | MCP 写在加分项 |

### 统计

| 关键词 | 第1轮(W9) | 第2轮(W11) | 第3轮(W13) |
| ------ | --------- | ---------- | ---------- |
| MCP    | **/**     | **/**      | **/**      |

### 结论（≤3 条）：MCP 是加分项还是必备？是否影响 P2 叙事重点？
```

### Step 4 · 5 道 MCP 面试题（P0）

追加到 `interview-questions.md`（每题：问题 / 要点 3–5 条 / 我的项目证据）：

1. MCP 是什么？解决什么问题？与 Function Calling 的关系？
2. tools / resources / prompts 区别？你的 Server 为什么主要用 tools？
3. stdio 与 streamable HTTP 怎么选？你如何给 HTTP 加鉴权？
4. MCP 的主要安全风险与你的防护措施（工具投毒、间接注入、过度权限、token 泄露）？
5. 你如何让自己的 Agent 使用外部 MCP 工具？生命周期、命名、权限怎么处理？

### Step 5 · 发布 v0.9.0

```bash
cd ~/lab/workpilot
gitleaks git -v . || gitleaks detect -v      # 新旧版本命令二选一；有告警先处理
# CHANGELOG.md 新增 v0.9.0：MCP Server(stdio+http+token)、MCP Client(ext.fs 只读)、docs/mcp.md、ADR 0007
git add docs/mcp.md docs/adr/0007-mcp-adapter.md README.md CHANGELOG.md
git commit -m "docs(mcp): add MCP integration guide, ADR 0007, changelog v0.9.0"
git tag -a v0.9.0 -m "v0.9.0: MCP server/client"
git push origin main --tags
git push github main --tags                   # GitHub 远端名按实际
cd ~/lab/projects && git add career && git commit -m "docs(career): JD round 3 and 5 MCP interview questions" && git push
```

### Step 6 · 周复盘

填写 `plan/phase_02/week_13/README.md` 第 11 节，并在第 7 节逐条标 PASS/FAIL。重点回答：W14 的 Agent 评测要覆盖哪些工具（含 `ext.fs.*`）。

## 7. 概念自检（不看资料，口述，附答案）

1. 用一句话向非技术同事解释 MCP。（答：AI 工具的「USB-C 接口」——工具按一个标准接一次，任何支持 MCP 的 AI 应用都能用）
2. 为什么 MCP 不暴露 `gitea_issue_create`？（答：IDE Host 的工具确认不等于 WorkPilot 的审批流与审计；写操作只在有 HITL 与审计的 Agent 内执行）
3. Cursor 与 VS Code 的配置差异？（答：Cursor 用 `.cursor/mcp.json` + `mcpServers`；VS Code 用 `.vscode/mcp.json` + `servers`，且支持 `inputs` 变量）
4. v0.9 相比 v0.8 多了什么可演示的东西？（答：IDE 内调用 WorkPilot、HTTP 鉴权服务、Agent 调用外部 MCP 工具）
5. ADR 的作用是什么？（答：记录决策背景、选项、取舍与代价，让未来的自己/面试官理解「为什么这样设计」）

## 8. 对 DA-01 的贡献

v0.9 完成：DA-01 的 F4（IDE 集成）具备可复现的配置文档和演示素材；安全说明把「只读默认 + 审批写」写成对外承诺，后续 P2 作品集（Day55）和产品页（Day56）直接复用；JD 数据为 P2 叙事重点提供依据。

## 9. 求职映射（D 线）

- 岗位能力：技术文档、演示表达、架构决策记录、市场洞察
- 对应岗位：AI Agent Engineer / AI Full-Stack Engineer / Developer Experience 方向
- 简历 bullet 草稿：编写 MCP 集成文档与 ADR，支持 VS Code / Cursor / Claude Desktop 三种 Host 一键接入；在 ** 条 AI 岗位 JD 中 MCP 出现率 **%，据此调整作品集重点。
- 面试可能问：
  - 你怎么证明 MCP 集成真的提升了效率？（要点：录屏对比切出 IDE 搜索 vs IDE 内调用的耗时；记录本周真实使用次数）
  - 为什么不用 OAuth？（要点：单用户自托管、stdio 为主；静态 token + 本机监听足够；多用户场景（W19 认证后）再评估 OAuth，已记 Backlog）

## 10. 卡住时的处理

| 现象                                 | 处理                                                                                       |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| 录屏时 Copilot 没调用 workpilot 工具 | 提问中显式写「用 workpilot」，或在 Chat 输入 `#kb_ask` 引用工具                            |
| 录屏中出现公司内容/真实姓名          | 立即重录；只用 WorkPilot 自身公开文档作为知识库                                            |
| gitleaks 报告历史提交中有疑似密钥    | 先确认是否真实密钥；真实则立即作废并轮换，再评估是否需要清理历史（清理前先备份并单独确认） |
| `git push github` 失败               | `git remote -v` 确认远端名；token 过期则在 GitHub 重新生成                                 |
| JD 平台信息不足                      | 只记岗位关键词与技能要求，薪资可空；条数不足 10 条也可，注明样本量                         |
| 超过 120 分钟                        | 停止，tag 与文档优先；JD 与面试题顺延到 Day49 开头 15 分钟                                 |

## 11. 产出记录（执行时填写）

- 录屏路径 / 时长：\_\_\_\_
- `docs/mcp.md` 行数：\_\_\_\_
- JD 第 3 轮条数 / MCP 出现率：\_\_\_\_
- 面试题总数：\_\_\_\_
- tag 推送结果（Gitea / GitHub）：\_\_\_\_
- gitleaks 结果：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → Week 13 DONE → 明天进入 Day49（W14 Task 1：Agent 评测集 30 任务 + 轨迹记录）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
