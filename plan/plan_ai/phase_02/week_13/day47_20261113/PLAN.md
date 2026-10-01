# Day 47 · 2026-11-13 · Week 13 Task 2：IDE 接入 + HTTP 传输 + MCP Client

## 0. 今天只做一件事

让 WorkPilot MCP Server 在 VS Code Copilot Chat（Agent 模式）里被真实调用，并补上 streamable-http + Bearer 鉴权；同时让 WorkPilot Agent 作为 MCP Client 接入官方 filesystem server 的**只读**工具（`ext.fs.*`）。

不碰：OAuth 授权流程、第二个外部 MCP Server、把 MCP HTTP 部署到云端、写工具暴露。

## 1. 资产锚点

- 构建模块：M8.1 WorkPilot MCP Server（HTTP + token）、M8.2 MCP Client（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.9 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：① VS Code 中直接问团队规范；② `127.0.0.1:8100/mcp` 无 token 返回 401；③ Agent 时间线出现 `ext.fs.*` 外部工具调用
- 今日 AI 实际应用：MCP 传输与客户端会话 → 让 WorkPilot 同时成为 MCP 的「提供方」和「消费方」

## 2. 起点（前置确认）

- 已有：Day46 的 `apps/mcp-server/server.py`（stdio，3 个工具）、`/v1/tools/invoke`
- 需确认 + 准备公开语料目录（**只放可公开内容**）：

```bash
cd ~/lab/workpilot/apps/mcp-server && uv run python -c "import mcp, httpx; print('ok')"
code --version                                   # VS Code 版本需支持 MCP（1.102+）
npx -y @modelcontextprotocol/server-filesystem --help 2>&1 | head -3   # 首次会下载
grep -n "def register" ~/lab/workpilot/apps/api/app/tools/registry.py  # 看注册接口
mkdir -p ~/lab/workpilot/data/sample/public-docs
cp ~/lab/workpilot/README.md ~/lab/workpilot/docs/runbook.md ~/lab/workpilot/data/sample/public-docs/
```

## 3. 验收对齐（做完要能勾掉）

- [ ] VS Code Copilot Chat Agent 模式中调用 `kb_ask` 成功，截图保存
- [ ] `--transport http` 启动后：无 token / 错 token → 401；正确 token 的 Python 客户端 `list_tools` 返回 3 个工具
- [ ] Token 少于 32 字符或未设置时 HTTP 模式拒绝启动
- [ ] `MCP_FS_ROOT` 设置时 API 启动日志打印已注册的 `ext.fs.*` 工具；Agent 一次运行中调用了其中之一
- [ ] `test_mcp_client.py` 证明 `write_file` / `edit_file` / `move_file` / `create_directory` 未被注册
- [ ] 已提交并 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                   |
| ----------- | ------ | ------------------------------------------------------ |
| 0–10 min    | P0     | 读 VS Code MCP 文档：mcp.json 结构、Agent 模式工具开关 |
| 10–35 min   | P0     | `.vscode/mcp.json`（stdio）→ Copilot Chat 调用验证     |
| 35–60 min   | P0     | `auth.py` + HTTP 传输 + curl / 客户端验证              |
| 60–105 min  | P0     | `app/tools/mcp_client.py` + lifespan + Agent 调用验证  |
| 105–115 min | P0     | 单测 + 提交                                            |
| 115–120 min | P1     | Claude Desktop 配置示例（只写不强制实测）              |

时间不足时最低保留：VS Code stdio 接入 + MCP Client 只读注册（HTTP 鉴权顺延到 Day48 开头）。

## 5. 今日学习（只学完成任务必须的）

- VS Code 的 MCP 配置在工作区 `.vscode/mcp.json`，顶层键是 `servers`；敏感值用 `inputs` + `${input:id}` 运行时输入，不写进文件。
- streamable HTTP：单端点（默认 `/mcp`），POST 发 JSON-RPC，响应可以是 JSON 或 SSE 流，会话用 `Mcp-Session-Id` 头维持。
- MCP Client 生命周期：`stdio_client` 拉起子进程 → `ClientSession.initialize()` → `list_tools()` / `call_tool()`；用 `AsyncExitStack` 在 FastAPI lifespan 中保持长连接。
- 外部 MCP Server 的工具 = 不可信代码 + 不可信输出：必须白名单、命名空间隔离、输出按 untrusted 包裹。
- 资料：https://code.visualstudio.com/docs/copilot/chat/mcp-servers 、https://modelcontextprotocol.io/ （Transports、Client 快速开始）、https://github.com/modelcontextprotocol/python-sdk

## 6. 执行步骤

### Step 1 · VS Code stdio 接入

在 `~/lab/workpilot/.vscode/mcp.json`：

```json
{
  "servers": {
    "workpilot": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "${workspaceFolder}/apps/mcp-server",
        "run",
        "server.py"
      ],
      "env": { "WORKPILOT_API_URL": "http://127.0.0.1:8000" }
    }
  }
}
```

Step 2 完成后再加 HTTP 条目：`servers` 中加 `"workpilot-http": {"type": "http", "url": "http://127.0.0.1:8100/mcp", "headers": {"Authorization": "Bearer ${input:workpilot-mcp-token}"}}`，顶层加 `"inputs": [{"type": "promptString", "id": "workpilot-mcp-token", "password": true}]`（token 运行时输入，不落盘）。

操作：命令面板 `MCP: List Servers` → `workpilot` → Start；打开 Copilot Chat → 切到 **Agent** 模式 → 工具图标中勾选 workpilot 的工具 → 提问「用 workpilot 查我们的分支命名规范并总结成 3 条」→ 确认工具调用 → 看到带引用的回答。截图。

> 若 `${workspaceFolder}` 未被替换，改成绝对路径 `/Users/<你>/lab/workpilot/apps/mcp-server`。复制一份为 `.vscode/mcp.json.example` 提交（本文件无密钥，也可直接提交）。

### Step 2 · streamable-http + Bearer 鉴权（核心逻辑自己写）

`apps/mcp-server/auth.py`（纯 ASGI 中间件，不破坏 SSE 流）：

```python
import hmac

from starlette.responses import JSONResponse

class BearerAuthMiddleware:
    def __init__(self, app, token: str):
        if not token or len(token) < 32:
            raise ValueError("MCP_HTTP_TOKEN 未设置或少于 32 字符，拒绝启动")
        self.app = app
        self.expected = f"Bearer {token}".encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            got = dict(scope["headers"]).get(b"authorization", b"")
            if not hmac.compare_digest(got, self.expected):      # 常量时间比较
                resp = JSONResponse({"error": "unauthorized"}, status_code=401,
                                    headers={"WWW-Authenticate": "Bearer"})
                await resp(scope, receive, send)
                return
        await self.app(scope, receive, send)                     # lifespan 直接透传
```

改 `server.py` 末尾：

```python
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    args = ap.parse_args()
    if args.transport == "stdio":
        mcp.run()
    else:
        import uvicorn
        from auth import BearerAuthMiddleware
        app = BearerAuthMiddleware(mcp.streamable_http_app(), os.getenv("MCP_HTTP_TOKEN", ""))
        uvicorn.run(app, host=os.getenv("MCP_HTTP_HOST", "127.0.0.1"),   # 默认只监听本机
                    port=int(os.getenv("MCP_HTTP_PORT", "8100")))
```

验证：

```bash
export MCP_HTTP_TOKEN=$(openssl rand -hex 32)   # 存到本机 .env，不提交
uv run server.py --transport http &
curl -s -o /dev/null -w '%{http_code}\n' -X POST 127.0.0.1:8100/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{}'   # 预期 401
```

正向验证 `apps/mcp-server/scripts/check_http.py`（约 12 行，可 AI 生成）：`streamablehttp_client("http://127.0.0.1:8100/mcp", headers={"Authorization": f"Bearer {token}"})` → `ClientSession(r, w)` → `initialize()` → 打印 `list_tools()` 名字，预期 `['kb_search', 'kb_ask', 'gitea_repo_read']`。

> 安全底线：不要把 `MCP_HTTP_HOST` 改成 `0.0.0.0` 再映射到公网；云端如需远程使用，放在 Caddy 后 + HTTPS + token，且 Day55 再决定。

### Step 3 · MCP Client：外部工具注册为 `ext.fs.*`（核心逻辑必须自己理解）

`apps/api/app/tools/mcp_client.py`：

```python
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from app.tools.registry import registry

FS_READ_ONLY = {"read_text_file", "read_file", "read_multiple_files", "list_directory",
                "directory_tree", "search_files", "get_file_info", "list_allowed_directories"}

def select_tools(tools: list[Tool], allow: set[str]) -> list[Tool]:
    return [t for t in tools if t.name in allow]          # 白名单：未知/写工具一律不注册

class MCPToolset:
    def __init__(self, namespace: str, params: StdioServerParameters, allow: set[str]):
        self.namespace, self.params, self.allow = namespace, params, allow
        self._stack = AsyncExitStack()
        self.session: ClientSession | None = None

    async def start(self) -> list[str]:
        r, w = await self._stack.enter_async_context(stdio_client(self.params))
        self.session = await self._stack.enter_async_context(ClientSession(r, w))
        await self.session.initialize()
        names = []
        for t in select_tools((await self.session.list_tools()).tools, self.allow):
            name = f"{self.namespace}.{t.name}"
            registry.register_external(                     # 新增方法：接受原始 JSON Schema
                name=name, fn_name=name.replace(".", "__"),  # 函数名不能含 "."
                description=f"[外部MCP:{self.namespace}] {t.description or ''}",
                input_schema=t.inputSchema, permission="read", untrusted=True,
                handler=self._handler(t.name))
            names.append(name)
        return names

    def _handler(self, remote: str):
        async def call(**kwargs) -> str:
            res = await self.session.call_tool(remote, kwargs)
            text = "\n".join(c.text for c in res.content if c.type == "text")
            if res.isError:
                raise RuntimeError(text[:500])
            return text
        return call

    async def aclose(self):
        await self._stack.aclose()
```

`registry.register_external(...)` 按现有 `ToolSpec` 结构补约 15 行：保存原始 schema、`fn_name`（给 LLM 的函数名，OpenAI 兼容接口只允许 `[a-zA-Z0-9_-]`）、`untrusted=True`（输出走 `<tool_output untrusted="true">`）。

`main.py` lifespan（约 15 行）：仅当 `settings.mcp_fs_root` 非空时创建 `MCPToolset("ext.fs", StdioServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", root]), FS_READ_ONLY)`；`await fs.start()` 包在 try 中，失败只 `log.exception` 并降级为无外部工具；`yield` 后 `await fs.aclose()`。云端容器默认不配置即不启用。

`.env.example` 新增 `MCP_FS_ROOT=`（注释：只指向公开目录）、`MCP_HTTP_TOKEN=`。

### Step 4 · Agent 调用验证

```bash
MCP_FS_ROOT=$HOME/lab/workpilot/data/sample/public-docs make dev
curl -N -X POST 127.0.0.1:8000/v1/agent/run -H 'Content-Type: application/json' \
  -d '{"task":"读取本地公开文档目录中的 runbook.md，总结备份恢复的步骤"}'
```

预期 SSE 事件中出现 `tool_call` 且 name 为 `ext.fs.read_text_file`（或 `ext__fs__...` 映射回的名字）；Web AgentPage 时间线同样可见。若 Agent 选了 `kb_search`，在 task 中写明「本地文件」再试，并把这条记入 W14 工具选择用例。

### Step 5 · 单测 + 提交

`apps/api/tests/unit/test_mcp_client.py`：用 `mcp.types.Tool(name=n, description="", inputSchema={"type": "object"})` 构造 `read_text_file / write_file / edit_file / move_file / create_directory / list_directory / unknown_tool`，断言 `select_tools(tools, FS_READ_ONLY)` 只保留 `{"read_text_file", "list_directory"}`。

```bash
cd ~/lab/workpilot/apps/api && uv add mcp && uv run pytest tests/unit/test_mcp_client.py -q
cd ~/lab/workpilot
git add .vscode/mcp.json.example apps/mcp-server apps/api .env.example
git commit -m "feat(mcp): vscode config, streamable-http bearer auth, MCP client for ext.fs read-only tools"
git push
```

### Step 6 · P1：Claude Desktop 配置示例（写进 Day48 文档）

文件 `~/Library/Application Support/Claude/claude_desktop_config.json`，顶层键 `mcpServers`，内容与 Step 1 的 `workpilot` 条目相同，但去掉 `type`、`command` 写 `which uv` 的绝对路径、`--directory` 写绝对路径（Claude Desktop 不继承 shell PATH，也不认 `${workspaceFolder}`）。改完需完全退出并重启 Claude Desktop。

## 7. 概念自检（不看资料，口述，附答案）

1. VS Code 与 Claude Desktop 的 MCP 配置顶层键分别是什么？（答：VS Code `.vscode/mcp.json` 用 `servers`；Claude Desktop 用 `mcpServers`）
2. 为什么 token 比较用 `hmac.compare_digest`？（答：常量时间比较，避免计时侧信道逐字节猜 token）
3. stdio 模式为什么不需要 token，而 HTTP 必须？（答：stdio 是 Host 拉起的本机子进程，信任边界=本机用户；HTTP 是网络服务，任何能访问端口的人都能调用）
4. 外部 MCP 工具为什么要白名单而不是黑名单？（答：外部 Server 升级可能新增写工具，黑名单会默认放行未知工具；白名单默认拒绝）
5. 为什么外部工具的函数名用 `ext__fs__xxx`？（答：OpenAI 兼容 Function Calling 的 name 只允许字母数字下划线连字符，`.` 会被拒绝；内部仍用 `ext.fs.*` 作命名空间展示）

## 8. 对 DA-01 的贡献

WorkPilot 真正进入日常 IDE 工作流（F4），并具备「接入任意 MCP 生态工具」的扩展点（M8.2）；鉴权 + 本机监听 + 只读白名单把新增攻击面控制在可接受范围，为 W15 Guardrail 与 W21 安全加固打底。

## 9. 求职映射（D 线）

- 岗位能力：IDE 集成、协议传输选型、API 鉴权、外部工具接入与沙箱化
- 对应岗位：AI Agent Engineer / AI Platform Engineer / AI Full-Stack Engineer
- 简历 bullet 草稿：为 MCP Server 增加 streamable HTTP 传输与 Bearer 鉴权（常量时间校验、本机监听默认），并实现 MCP Client 将外部 MCP 工具按白名单动态注册为 Agent 工具，接入新外部 Server 仅需 \_\_ 行配置。
- 面试可能问：
  - 远程 MCP Server 有哪些安全风险？（要点：无鉴权暴露、工具投毒/描述注入、过度权限、输出间接注入、token 透传；对策：鉴权、只读默认、白名单、输出标记不可信、审计）
  - 长连接 MCP Client 放在哪里管理？（要点：FastAPI lifespan + AsyncExitStack，同一 task 进入和退出，失败降级不影响主服务）

## 10. 卡住时的处理

| 现象                                                 | 处理                                                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| VS Code 中看不到 workpilot 工具                      | 确认 Chat 处于 Agent 模式；`MCP: List Servers` 看状态，`Show Output` 查看 Server 日志            |
| HTTP 正确 token 仍 401                               | 确认请求头为 `Authorization: Bearer <token>`，`export` 的 token 与启动进程环境一致               |
| `streamablehttp_client` 406 / 400                    | 必须同时 Accept `application/json, text/event-stream`；用 SDK 客户端而不是手写 curl 验证正向路径 |
| lifespan 关闭时报 `cancel scope in a different task` | `start()` 与 `aclose()` 必须在同一个 lifespan 协程里调用，不要在请求里 start                     |
| Agent 不选 `ext.fs.*`                                | 改进外部工具 description 前缀（「读取本机公开文档目录的文件」），记录为 W14 工具选择用例         |

## 11. 产出记录（执行时填写）

- VS Code 调用截图路径：\_\_\_\_
- HTTP 401 / 正向验证输出：\_\_\_\_
- 注册的 `ext.fs.*` 工具列表：\_\_\_\_
- Agent run_id 与调用的外部工具：\_\_\_\_
- Claude Desktop 是否实测：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day48（W13 Task 3：MCP Demo + 文档 + JD 追踪，v0.9）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
