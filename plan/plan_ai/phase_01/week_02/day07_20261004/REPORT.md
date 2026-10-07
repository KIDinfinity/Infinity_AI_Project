# Day 07 · 执行报告（2026-10-04）

对应 `PLAN.md`；产出代码仓库：`~/lab/workpilot`（commit `066a878`，已 push 到 `origin/main`）。
分支：`main`。变更：11 files changed, 831 insertions(+), 6 deletions(-)。

## 一、逐步执行记录

| Step | 内容 | 结果 |
| --- | --- | --- |
| 1 | uv 初始化 + 依赖 | ✅ `uv python install 3.12` → 3.12.15；`uv init --app` 后**删除 uv 0.12 默认的 `src/` 布局**、移除 `[project.scripts]` 与 `[build-system]`（本项目不作为包安装，与计划 §6.1 的 `pythonpath=["."]` 一致）；依赖 fastapi / uvicorn[standard] / pydantic-settings + dev pytest / httpx / ruff |
| 2 | `app/core/config.py` | ✅ 按计划原样实现（`parents[4]` 定位仓库根 `.env`、`extra="ignore"`、`@lru_cache`） |
| 3 | `app/routes/health.py` + `app/main.py` | ✅ `Annotated[Settings, Depends(get_settings)]`（规避 ruff B008）+ `create_app()` 工厂 |
| 4 | `tests/test_health.py` | ✅ 2 个用例：正常响应 + `dependency_overrides` 注入 `APP_ENV=test` |
| 5 | Makefile 接线 | ✅ 新增 `API_DIR := apps/api`，`dev / test / lint` 三个 TODO 替换为真实命令 |
| 6 | 验证 | ✅ 见下表（含 `APP_ENV=prod` 覆盖验证） |
| 7 | Pydantic 422 体验 | ✅ 临时加 `/v1/echo` 验证后**已回滚**（`health.py` 仅剩 /health） |
| 8 | 提交 | ✅ `feat(api): bootstrap FastAPI app with settings, health check and tests` + push |

### Step 6 验证结果

| 验证项 | 命令 | 实际输出 |
| --- | --- | --- |
| health | `curl -s --noproxy '*' localhost:8000/health` | `{"status":"ok","env":"dev","version":"0.0.1"}` |
| docs | `curl -o /dev/null -w '%{http_code}' localhost:8000/docs` | `200` |
| OpenAPI | `GET /openapi.json` | `paths = ['/health']` |
| 测试 | `make test` | `2 passed, 1 warning in 0.93s` |
| 静态检查 | `make lint` | `All checks passed!` + `8 files already formatted` |
| 环境变量优先 | `APP_ENV=prod make dev` → `/health` | `{"status":"ok","env":"prod","version":"0.0.1"}` |
| 422 | `POST /v1/echo {"text":"hi","times":9}` | `422`，`loc=["body","times"]` `type=less_than_equal` `msg=Input should be less than or equal to 3` |
| 422（多字段） | `{"text":"","times":0}` | 同时返回 `string_too_short`（text）与 `greater_than_equal`（times） |

## 二、产出记录（PLAN §11）

- Python / uv / FastAPI 版本：**Python 3.12.15 / uv 0.12.22 / FastAPI 0.142.2**（另：pydantic 2.13.5、pydantic-settings 2.15.0、ruff 0.16.10、pytest 9.1.1）
- `/health` 返回：`{"status":"ok","env":"dev","version":"0.0.1"}`
- pytest 结果：**2 passed**（+1 warning）　ruff 结果：**All checks passed!**（无报错、格式检查通过）
- 422 体验时 detail 的关键信息：`less_than_equal`，`loc=["body","times"]`，`ctx={"le":3}`，`input=9` —— 校验在进入函数前完成，业务代码零防御性判断
- 卡点记录：
  1. `uv init --app`（uv 0.12.22）默认生成 `src/workpilot_api/` 布局 + `[project.scripts]` + `[build-system]`，与计划要求的根级 `app/` 布局冲突 → 删除 `src/`、移除 scripts 与 build-system，使项目成为非安装型工程，`pythonpath=["."]` 生效
  2. 本机 shell 有代理，curl 直连 localhost 需 `--noproxy '*'`（计划 §10 已预判）
  3. `git restore health.py` 无法回滚未提交文件（Step7 的行不通） → 改用编辑工具手工删除 `/v1/echo`
  4. 非阻塞提示：`testclient` 发出 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead`（不影响结果，httpx2 成熟后再切）
- 用时：约 105 分钟（P0 全完成；P1 的 422 体验 + 自检完成；P2「读 FastAPI Dependencies 一节」未单独做，依赖注入已通过实现理解）

## 三、验收对齐（PLAN §3）

- [x] `uv run python --version` → `Python 3.12.15`
- [x] `curl -s localhost:8000/health` → `{"status":"ok","env":"dev","version":"0.0.1"}`
- [x] `http://localhost:8000/docs` → HTTP 200，OpenAPI 可见 `GET /health`
- [x] `make test` → `2 passed`
- [x] `make lint` → `All checks passed!` 且 `8 files already formatted`
- [x] `uv.lock` 已提交；`git status` 无 `.venv/`、无 `.env`（`.gitignore` 覆盖 `.venv/` 与 `.env`）

## 四、对 DA-01 的贡献

- WorkPilot 从「只有目录」变为**可运行的 API 进程**（`make dev` 起 :8000，`/docs` 自动接口文档），v0.1 里程碑的前提达成。
- 打通标准链路：**配置（Settings）→ 依赖注入（Depends）→ 路由（APIRouter）→ 测试（dependency_overrides）**。Day08 的 LLM Gateway 只需按同一模式新增 `app/core/llm.py` + `app/routes/chat.py`，测试用同一个 override 手法注入假 provider，`make test` 保持不触网。
- `app_env` 已接入 `Literal["dev","test","prod"]`，W7 的日志分级与 W7 的 Docker 环境切换无需改代码。

## 五、求职映射（D 线）

- 岗位能力：Python 3.12 / FastAPI / Pydantic v2 / pydantic-settings / pytest / uv / ruff —— 对应 Day06 矩阵中 Python 9/10（必需 8）、FastAPI 4/10（必需 3）
- 简历 bullet 草稿：基于 FastAPI + Pydantic v2 + pydantic-settings 搭建 AI 服务后端骨架，依赖注入实现配置与外部服务可替换，单测不依赖网络，`make test` **0.93 秒**完成（2 passed），ruff 零报错。
- 面试可能问到且今天已能回答：
  - 「FastAPI 的依赖注入有什么用？」→ 解耦配置 / 客户端 / 鉴权；可组合可缓存（`lru_cache`）；测试用 `dependency_overrides` 替换外部依赖，这就是单测不触网的原因。
  - 「为什么选 uv？」→ 一个工具替代 pyenv + pip + poetry：管 Python 版本、虚拟环境、锁文件，速度快。
  - 「`async def` 里调同步 `requests` 会怎样？」→ 阻塞事件循环（今天刻意用普通 `def` 写 `/health`，Day08 调 LLM 才切 `async def`）。

## 六、Day08 前置

- 明天 Task 3：LLM Gateway v0 —— `app/core/llm.py` + `POST /v1/chat`，测试继续用 `dependency_overrides` 注入假 provider。
- 今日结论：`Settings` 是唯一配置入口，`OPENAI_API_KEY` / base_url / timeout 都加到 `Settings` 里即可；`.env` 已存在且 `extra="ignore"`，加新键无需改配置代码。

## 七、计划外待办（未擅自执行）

- `PROJECT_CONFIG.md` §2 仍写「当前周 = 第 1 周」，而实际已进入第 2 周（Day06–Day07 均为 W2）。按该文件规则「每周末做完复盘后同步更新」，建议 W2 复盘时一并修正，本次未改动以免越界。
