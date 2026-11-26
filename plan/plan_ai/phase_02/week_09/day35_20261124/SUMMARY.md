# SUMMARY · Day 35（2026-11-24）Week 09 Task 2：内置工具

> 执行结果汇总。对应 PLAN 第 3 节「验收对齐」逐条给出**完整、可直接粘贴、任何目录下运行**的验收命令。
> 所有命令都先 `cd` 到绝对路径，无需手动定位目录。

---

## 0. 一句话结论

为 WorkPilot Agent 新增 **4 个只读工具**（kb_search / web_search / gitea_repo_read / gitea_issue_read），并**顺带完成 P2 的 http_fetch + SSRF 防护**，统一走 `clip()` + `wrap_untrusted()` 做不可信内容包裹，仓库访问白名单 + 路径穿越拒绝 + 公网 IP 校验。**mock 24 通过、live 3 通过**，`to_openai_tools()` 共 **6** 个工具。

---

## 1. 改动清单（未提交，按用户要求）

| 文件 | 动作 | 说明 |
|---|---|---|
| `apps/api/app/core/config.py` | 改 | 新增 4 个配置项 `gitea_base_url` / `gitea_token` / `gitea_read_repos` / `tavily_api_key` |
| `apps/api/app/tools/common.py` | 新增 | `clip()`、`wrap_untrusted()`（转义 `</tool_output>`） |
| `apps/api/app/tools/builtin/kb_search.py` | 新增 | 走 `retrieve.search` |
| `apps/api/app/tools/builtin/gitea.py` | 新增 | gitea_repo_read + gitea_issue_read，白名单 + `..` 拒绝 |
| `apps/api/app/tools/builtin/web_search.py` | 新增 | Tavily → ddgs 兜底 |
| `apps/api/app/tools/builtin/http_fetch.py` | 新增 | （P2）抓正文 + SSRF 防护 |
| `apps/api/app/tools/builtin/__init__.py` | 改 | import 全部 6 个工具 |
| `apps/api/tests/tools/test_builtin_tools.py` | 新增 | mock + live 单测 |
| `.env.example` | 改 | 加 4 个键（无真实值） |
| `apps/api/pyproject.toml` / `uv.lock` | 改 | 加 httpx / tavily-python / ddgs / respx |

---

## 2. 验收对齐（第 3 节，逐条 + 完整命令）

### ✅ 验收 1：`common.py` 的 `clip()`、`wrap_untrusted()`（转义 `</tool_output>`）

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run python -c "from app.tools.common import clip, wrap_untrusted; print('clip 结果:', clip('x'*5000)[-45:]); print(); print('wrap 结果:'); print(wrap_untrusted('web', 'a</tool_output>b'))"
```

**期望输出**：`clip` 尾部出现 `…[已截断，原长 5000 字符]`；`wrap` 输出里正文的 `</tool_output>` 被转义为 `&lt;/tool_output&gt;`，且整体包在 `<tool_output source="web" untrusted="true">...</tool_output>` 内。

---

### ✅ 验收 2：4 个工具注册成功，`to_openai_tools()` 共 6 个

> 注：PLAN 写「共 5 个」= 现有 calculator + 4 个只读工具。本次额外完成了 P2 的 `http_fetch`，故共 6 个。

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run python -c "import app.tools.builtin; from app.tools.registry import to_openai_tools; [print(t['function']['name']) for t in to_openai_tools()]"
```

**期望输出**（6 行，顺序无关）：

```
calculator
gitea_repo_read
gitea_issue_read
http_fetch
kb_search
web_search
```

---

### ✅ 验收 3：每个工具都返回 `ToolOutput(text=wrap_untrusted(...), sources=[...])`

（1）mock 层验证（不依赖真实服务/密钥，直接看包裹与来源）：

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run pytest tests/tools/test_builtin_tools.py -k "repo_read_dir or kb_search_mock or web_search_mock or http_fetch_ok" -q
```

**期望输出**：`4 passed`。这 4 条分别断言了 gitea / kb / web / http_fetch 的输出 `untrusted="true"` 且带 `sources`。

（2）真实执行演示（需要本地 Gitea 只读 token，可用下面命令现生成）：

```bash
docker exec -u git gitea gitea admin user generate-access-token -u infinity -t "workpilot-demo" --scopes "read:repository,read:issue" --raw
```

拿到 token 后，替换下面命令里的 `<TOKEN>` 再执行：

```bash
cd /Users/infinity/lab/workpilot/apps/api && GITEA_TOKEN=952f9b5420405c3a584c6eca886c13fca1e53226 GITEA_READ_REPOS='["infinity/workpilot"]' uv run python -c "
import asyncio, json, app.tools.builtin
from app.tools import registry as R
async def main():
    for name, a in [('gitea_repo_read', {'repo':'infinity/workpilot'}),
                    ('gitea_issue_read', {'repo':'infinity/workpilot'}),
                    ('web_search', {'query':'FastAPI'}),
                    ('kb_search', {'query':'DA-01'}),
                    ('http_fetch', {'url':'https://example.com/'})]:
        r = await R.execute(name, json.dumps(a))
        print(name, '-> ok=', r.ok, '| wrapped=', '<tool_output' in r.content, '| sources=', len(r.sources))
asyncio.run(main())
"
```

**期望输出**：5 行，每行 `ok= True`、`wrapped= True`、`sources=` 后面 ≥ 1。

---

### ✅ 验收 4：`gitea_repo_read` 拒绝白名单外仓库、拒绝 `..` 路径（单测）

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run pytest tests/tools/test_builtin_tools.py -k "rejected" -q
```

**期望输出**：`3 passed`。覆盖 `other/secret`（白名单外）、`../../etc`、`a/../b`（路径穿越）三种拒绝场景。

---

### ✅ 验收 5：mock 全绿 + `uv run pytest -m live` ≥ 3 通过

mock（全量，live 自动跳过）：

```bash
cd /Users/infinity/lab/workpilot/apps/api && uv run pytest tests/tools -q
```

**期望输出**：`24 passed, 3 deselected`。

live 冒烟（本机真实 Gitea + 真实 Web 搜索；替换 `<TOKEN>` 为验收 3 生成的 token）：

```bash
cd /Users/infinity/lab/workpilot/apps/api && GITEA_TOKEN=<TOKEN> GITEA_READ_REPOS='["infinity/workpilot"]' uv run pytest tests/tools -m live -q
```

**期望输出**：`3 passed, 24 deselected`（gitea_repo_read / gitea_issue_read / web_search 各 1）。

---

### ✅ 验收 6：`.env.example` 已加 4 个键（无真实值）

```bash
grep -nE "GITEA_|TAVILY_" /Users/infinity/lab/workpilot/.env.example
```

**期望输出**：

```
GITEA_BASE_URL=http://localhost:3000
GITEA_TOKEN=
GITEA_READ_REPOS=["you/workpilot"]
TAVILY_API_KEY=
```

---

## 3. 产出记录（对应 PLAN 第 11 节）

- **已注册工具**：6 个 —— calculator、kb_search、web_search、gitea_repo_read、gitea_issue_read、http_fetch
- **mock 单测通过数 / live 通过数**：**24 / 3**
- **`kb_search` 返回的 chunk_id 示例**：`5eea8957-bfd1-55c9-a22d-ca6a67df2666`（title：`DA-01 定义：WorkPilot（2026-10-14 · v1）`）
- **是否完成 http_fetch**：✅ 完成（P2，含 SSRF 防护 + 单测）
- **卡点**：
  1. PLAN 示例代码用 `settings.GITEA_TOKEN`（大写字段名），实际 pydantic-settings 字段是 snake_case `settings.gitea_token`；已按正确字段名实现。
  2. `retrieve.Hit` 的字段是 `title`（不是 PLAN 示例里的 `doc_title`）；已用 `h.title`。
  3. `gitea_token` 是 `SecretStr | None`，取值需 `settings.gitea_token.get_secret_value()`。
- **用时**：约 90 分钟（含 P2）。

---

## 4. 附加说明

### 4.1 公网 IP / 部署（8.148.216.61）

- 服务器 Caddyfile **已确认**为「IP + HTTP、无 TLS」，且整站加了 HTTP Basic Auth（`infinity`）。
- 工具是**库级能力**，尚未暴露 HTTP 端点（Day36「多工具循环 Demo」才接入 Agent 循环），因此**工具本身用 pytest / python 本地验收**，无需 curl 公网。
- 若要看部署的 API 健康状态（公网 80 端口有 Basic Auth，需带密码）：

  ```bash
  curl -u infinity:<密码> http://8.148.216.61/health
  ```

  不依赖密码、等价的服务端内网检查：

  ```bash
  ssh root@8.148.216.61 "docker exec workpilot-web-1 wget -qO- http://api:8000/health"
  ```

  **期望输出**：`{"status":"ok","env":"prod","version":"0.0.1"}`

### 4.2 依赖安装说明

- `uv` 已配置清华镜像（`pyproject.toml` 的 `[[tool.uv.index]]`），无需额外代理。
- 新增依赖：`httpx`、`tavily-python`、`ddgs`（运行时）+ `respx`（测试）。

### 4.3 未提交（按用户要求）

- 所有改动**保留在工作区未提交**（`git status` 可见 `.env.example`、`apps/api/app/core/config.py`、`apps/api/app/tools/`、`apps/api/tests/tools/`、`pyproject.toml`、`uv.lock`）。
- 注：`apps/api/app/llm/gateway.py` 的改动是**更早任务遗留的未提交变更**（`chat_with_tools` / `ToolChatResult`），非本次 Day35 产物。

### 4.4 已知遗留（Backlog）

- **DNS rebinding 残余风险**：`assert_public_url` 在「解析」与「实际连接」之间，攻击者仍可能切换 DNS 结果；已按 PLAN 记入 W15 Backlog。
