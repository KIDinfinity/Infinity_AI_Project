# Day 46 · 2026-12-21 · Week 13 Task 1：MCP Server（stdio）+ Inspector

## 0. 今天只做一件事

在 `~/lab/workpilot/apps/mcp-server` 用官方 MCP Python SDK（FastMCP）写出 WorkPilot MCP Server（stdio），提供 `kb_search` / `kb_ask` / `gitea_repo_read` 三个只读工具，并在 MCP Inspector 中调用成功。

不碰：VS Code / Claude Desktop 接入、streamable-http、鉴权、MCP Client（都是 Day47）；OAuth、sampling、elicitation。

## 1. 资产锚点

- 构建模块：M8.1 WorkPilot MCP Server（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.9 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：任何 MCP Host 都能以标准协议列出并调用 WorkPilot 的 3 个只读工具；后端多了一个「只允许 read 工具」的调用入口 `POST /v1/tools/invoke`
- 今日 AI 实际应用：学 MCP 的 Host/Client/Server 与 tools 原语 → 把 M6 Tool Layer 的能力以 MCP tools 形式暴露

## 2. 起点（前置确认）

- 已有：WorkPilot v0.8（`apps/api` 含 `/v1/kb/*`、Tool Registry、内置工具）；知识库已导入 `PROJECT_STANDARD.md`（含分支/提交规范）
- 需确认：

```bash
cd ~/lab/workpilot
node -v && uv --version      # Node ≥ 18（Inspector 需要 npx）
make dev                     # 或 cd apps/api && uv run uvicorn app.main:app --port 8000
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8000/v1/kb/search \
  -H 'Content-Type: application/json' -d '{"query":"分支","top_k":3}'   # 404 说明需要今天补
grep -n "permission" apps/api/app/tools/registry.py | head   # 确认 read/write 字段名
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `apps/mcp-server` 为独立 uv 项目，`uv run server.py` 可启动（stdio 下无任何 stdout 日志输出）
- [ ] Inspector Tools 页列出 `kb_search`、`kb_ask`、`gitea_repo_read` 3 个工具，各调用成功一次
- [ ] `POST /v1/tools/invoke` 调 `gitea_issue_create` 返回 403，pytest 通过
- [ ] `grep -rn "from app" apps/mcp-server/*.py` 无输出（证明未 import 后端内部代码）
- [ ] 代码已 push 到 Gitea

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                 |
| ----------- | ------ | -------------------------------------------------------------------- |
| 0–15 min    | P0     | 读 MCP 架构文档，口述 Host/Client/Server 与三原语                    |
| 15–40 min   | P0     | 后端：`/v1/kb/search`（若无）+ `/v1/tools/invoke`（read-only）+ 测试 |
| 40–80 min   | P0     | `apps/mcp-server`：uv init + `server.py` 三个工具                    |
| 80–100 min  | P0     | Inspector 调用 3 个工具，记录输入输出                                |
| 100–112 min | P2     | resource `workpilot://docs/{doc_id}` + prompt `research_brief`       |
| 112–120 min | P0     | README + 提交                                                        |

时间不足时最低保留：`kb_search` 一个工具 + Inspector 调通 + 提交。

## 5. 今日学习（只学完成任务必须的）

- **Host / Client / Server**：Host 是用户用的 AI 应用（VS Code、Claude Desktop），Host 内每连接一个 Server 就有一个 Client，Server 暴露能力。
- **三原语**：tools（模型决定调用的函数）、resources（应用/用户选择读取的只读数据，URI 寻址）、prompts（用户选择的提示模板）。
- **传输**：stdio（Host 拉起子进程，stdin/stdout 走消息，本机单用户）vs streamable HTTP（独立服务，可多客户端/远程，需要鉴权）。
- **JSON-RPC 2.0**：所有消息是 request/response/notification；握手 `initialize` → `tools/list` → `tools/call`。
- **stdio 铁律**：stdout 只能写协议消息，任何 `print` / 日志都必须去 stderr，否则 Host 解析失败。
- 资料：https://modelcontextprotocol.io/ （Architecture、Server 快速开始）、https://github.com/modelcontextprotocol/python-sdk （README 的 FastMCP 部分）

## 6. 执行步骤

### Step 1 · 后端补「MCP 可调用」的只读入口（自己写，核心是权限判断）

`apps/api/app/routes/kb.py` 若没有 search，加 `POST /v1/kb/search`：入参 `query`（1–500 字）、`top_k`（1–10，默认 5），复用现有 `retrieve()`，返回 `{"hits": [{source, chunk_id, score, text}]}`（约 12 行，可 AI 生成，按实际函数签名调整）。

新建 `apps/api/app/routes/tools.py`：

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.tools.registry import registry

router = APIRouter(prefix="/v1/tools", tags=["tools"])

# 双重限制：显式白名单 + permission 必须是 read
MCP_EXPOSED = {"gitea_repo_read", "gitea_issue_read"}

class InvokeReq(BaseModel):
    name: str
    args: dict = Field(default_factory=dict)

@router.post("/invoke")
async def invoke_tool(req: InvokeReq):
    tool = registry.get(req.name)
    if tool is None:
        raise HTTPException(404, detail={"code": "TOOL_NOT_FOUND"})
    if tool.permission != "read" or req.name not in MCP_EXPOSED:
        raise HTTPException(403, detail={"code": "TOOL_FORBIDDEN"})
    result = await registry.execute(req.name, req.args)   # 复用超时/截断/审计
    return {"name": req.name, "ok": result.ok, "output": result.output, "error": result.error}
```

在 `main.py` `app.include_router(tools.router)`。测试 `apps/api/tests/unit/test_tools_invoke.py`：

```python
def test_write_tool_forbidden(client):
    r = client.post("/v1/tools/invoke", json={"name": "gitea_issue_create", "args": {}})
    assert r.status_code == 403
```

```bash
cd apps/api && uv run pytest tests/unit/test_tools_invoke.py -q
```

### Step 2 · 初始化 MCP Server 项目

```bash
cd ~/lab/workpilot/apps
uv init mcp-server --app --python 3.12
cd mcp-server
uv add "mcp[cli]" httpx
rm -f main.py hello.py       # 目录最终：pyproject.toml / uv.lock / server.py / auth.py(Day47) / README.md
```

### Step 3 · 写 `server.py`（样板可让 AI 生成；`_post` 错误处理和工具描述自己审）

```python
"""WorkPilot MCP Server：薄适配层，只通过 HTTP 调 WorkPilot API，不 import 后端代码。"""
import logging
import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(stream=sys.stderr, level=logging.INFO)   # stdio 下绝不能写 stdout

API_URL = os.getenv("WORKPILOT_API_URL", "http://127.0.0.1:8000")
API_TOKEN = os.getenv("WORKPILOT_API_TOKEN", "")            # 本地 dev 可空
TIMEOUT = float(os.getenv("WORKPILOT_TIMEOUT", "60"))

mcp = FastMCP("workpilot")

async def _post(path: str, payload: dict) -> dict:
    headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}
    async with httpx.AsyncClient(base_url=API_URL, timeout=TIMEOUT, headers=headers) as c:
        r = await c.post(path, json=payload)
        if r.status_code >= 400:
            raise RuntimeError(f"WorkPilot API {path} -> {r.status_code}: {r.text[:200]}")
        return r.json()

@mcp.tool()
async def kb_search(query: str, top_k: int = 5) -> str:
    """在 WorkPilot 团队知识库中检索原文片段（只读）。适合查规范、文档、历史决策的原文。"""
    data = await _post("/v1/kb/search", {"query": query, "top_k": max(1, min(top_k, 10))})
    hits = data.get("hits", [])
    if not hits:
        return "知识库中没有找到相关内容。"
    return "\n\n".join(
        f"[{i}] {h['source']} (score={h['score']:.2f})\n{h['text'][:800]}"
        for i, h in enumerate(hits, 1)
    )

@mcp.tool()
async def kb_ask(question: str) -> str:
    """向 WorkPilot 知识库提问，返回带引用编号的答案；知识不足时会明确拒答。"""
    data = await _post("/v1/kb/ask", {"question": question})
    cites = "\n".join(f"[{c['index']}] {c['source']}" for c in data.get("citations", []))
    return f"{data['answer']}\n\n引用：\n{cites or '（无）'}"

@mcp.tool()
async def gitea_repo_read(owner: str, repo: str, path: str = "README.md") -> str:
    """读取 Gitea 仓库中的单个文件内容（只读）。"""
    data = await _post("/v1/tools/invoke",
                       {"name": "gitea_repo_read", "args": {"owner": owner, "repo": repo, "path": path}})
    if not data.get("ok"):
        raise RuntimeError(data.get("error") or "gitea_repo_read failed")
    return str(data["output"])

if __name__ == "__main__":
    mcp.run()   # 默认 stdio
```

要点（必须自己理解）：

- 工具的 docstring = 给模型看的 description，决定 Host 是否会选它，写清「何时用」。
- 类型注解自动生成 inputSchema；工具内抛异常会被 FastMCP 转成 `isError=true` 的结果返回给 Host，而不是让进程崩溃。
- `/v1/kb/ask` 的响应字段（`answer`、`citations[].index/source`）按你的实际 schema 调整。

### Step 4 · Inspector 调试

```bash
cd ~/lab/workpilot/apps/mcp-server
export WORKPILOT_API_URL=http://127.0.0.1:8000
uv run mcp dev server.py
# 或：npx @modelcontextprotocol/inspector uv --directory "$PWD" run server.py
```

浏览器打开终端打印的地址（新版 Inspector 带 session token 的 URL）→ Connect → Tools → List Tools：

| 工具            | 输入                                                     | 预期                                   |
| --------------- | -------------------------------------------------------- | -------------------------------------- |
| kb_search       | `{"query":"分支命名","top_k":3}`                         | 3 条片段，来源含 `PROJECT_STANDARD.md` |
| kb_ask          | `{"question":"提交信息格式是什么？"}`                    | 带 `[1]` 引用的答案                    |
| gitea_repo_read | `{"owner":"<你>","repo":"workpilot","path":"README.md"}` | README 文本                            |

再故意停掉 API 调一次 `kb_search`，确认 Inspector 显示错误结果而不是 Server 断开。

### Step 5 · P2：resource + prompt

- `@mcp.resource("workpilot://docs/{doc_id}")` 装饰 `async def get_doc(doc_id: str) -> str`：httpx GET `/v1/kb/docs/{doc_id}` 返回原文（后端无此接口则跳过）。
- `@mcp.prompt()` 装饰 `def research_brief(topic: str) -> str`：返回「先用 kb_search 检索 {topic} → 背景/现状/3 个方案及取舍/建议，结论标注来源」的模板字符串。
- Inspector 的 Resources / Prompts 页各验证一次。

### Step 6 · README + 提交

`apps/mcp-server/README.md` 写：用途、环境变量（`WORKPILOT_API_URL` / `WORKPILOT_API_TOKEN` / `WORKPILOT_TIMEOUT`）、`uv run mcp dev server.py`。

```bash
cd ~/lab/workpilot
grep -rn "from app" apps/mcp-server/*.py || echo "OK: decoupled"
git add apps/mcp-server apps/api/app/routes apps/api/app/main.py apps/api/tests
git commit -m "feat(mcp): add WorkPilot MCP server (stdio) with read-only kb/gitea tools"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. Host、Client、Server 分别是什么？一个 VS Code 连 3 个 Server 有几个 Client？（答：Host=AI 应用，Client=Host 内与某个 Server 1:1 的连接，Server=能力提供方；3 个 Client）
2. tools / resources / prompts 的控制方分别是谁？（答：tools 由模型决定调用；resources 由应用/用户选择；prompts 由用户显式选择）
3. 为什么 stdio Server 里 `print()` 会把连接搞坏？（答：stdout 是 JSON-RPC 通道，混入非协议文本会导致 Host 解析失败；日志应写 stderr）
4. 为什么 MCP Server 调 HTTP API 而不是 import 后端？（答：解耦部署与依赖、复用后端已有的权限/审计/超时、Server 可单独分发；代价是多一跳网络）
5. `/v1/tools/invoke` 为什么要「白名单 + permission=read」双重判断？（答：防止新增工具时默认被暴露；纵深防御，任一配置失误不至于暴露写操作）

## 8. 对 DA-01 的贡献

WorkPilot 第一次拥有「标准协议出口」：工具层不再只服务自己的 Agent，而能被任何 MCP Host 使用，是 F4 IDE 集成与 v0.9 的地基；只读暴露 + 后端统一入口保证了 §8 合规与 P2 安全指标「未经审批写操作 = 0」。

## 9. 求职映射（D 线）

- 岗位能力：MCP Server 开发、工具协议设计、服务解耦、最小权限
- 对应岗位：AI Agent Engineer / LLM Application Engineer / AI Platform Engineer
- 简历 bullet 草稿：基于官方 MCP Python SDK（FastMCP）实现 WorkPilot MCP Server，以适配层方式暴露 \_\_ 个只读工具（知识检索/问答/仓库读取），后端统一入口对写工具 100% 拒绝。
- 面试可能问：
  - MCP 和 OpenAI Function Calling 什么关系？（要点：Function Calling 是模型→应用的调用格式；MCP 是应用↔工具提供方的标准协议，解决 N×M 集成问题；Host 拿到 MCP tools 后仍通过 Function Calling 交给模型）
  - 工具 description 怎么写？（要点：写「何时用/何时不用」、参数约束、返回格式；直接影响选择准确率，W14 会量化）

## 10. 卡住时的处理

| 现象                                            | 处理                                                                                                    |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Inspector 显示连接后立即断开 / JSON parse error | 检查 `server.py` 是否有 `print` 或日志写到 stdout；`logging.basicConfig(stream=sys.stderr)`             |
| `uv run mcp dev` 报找不到 `mcp` 命令            | 确认装的是 `mcp[cli]`；或改用 `npx @modelcontextprotocol/inspector uv --directory "$PWD" run server.py` |
| Inspector 页面打不开 / 提示 auth                | 用终端打印的完整 URL（含 token）打开；端口冲突时关掉旧 Inspector 进程                                   |
| 工具调用报 `Connection refused`                 | WorkPilot API 未启动或 `WORKPILOT_API_URL` 写成 `localhost` 解析到 IPv6，改 `127.0.0.1`                 |
| 超过 60 分钟 Inspector 仍不通                   | 停下记录卡点，只保留 Step 1 后端入口 + 测试提交，明天 Step 0 先修                                       |

## 11. 产出记录（执行时填写）

- `/v1/kb/search` 是新建还是已有：\_\_\_\_
- Inspector 中 3 个工具调用结果（截图路径）：\_\_\_\_
- API 停止时 Inspector 显示：\_\_\_\_
- P2 resource / prompt 是否完成：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day47（W13 Task 2：IDE 接入 + HTTP 传输 + MCP Client）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
