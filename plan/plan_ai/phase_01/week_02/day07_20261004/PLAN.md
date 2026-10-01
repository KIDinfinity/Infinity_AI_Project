# Day 07 · 2026-10-04 · Week 02 Task 2：Python 工具链 + FastAPI 骨架

## 0. 今天只做一件事

在 `~/lab/workpilot/apps/api` 用 uv 建 Python 3.12 + FastAPI 项目：`GET /health` 可访问、配置从仓库根 `.env` 读取、pytest 与 ruff 通过，`make dev / test / lint` 接上真实命令。

不碰：LLM 调用（Day08）、数据库、Dockerfile（W7）、日志格式化 / request_id（W7）、前端。

## 1. 资产锚点

- 构建模块：M1 LLM Gateway 前置 —— `apps/api` 骨架（`app/main.py`、`app/core/config.py`、`app/routes/`），见 plan/plan_ai/DA01_TARGET_ASSET.md §5、§6.2
- 版本里程碑：为 v0.1 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`make dev` 启动 API，`/health` 返回 JSON，`/docs` 自动生成接口文档；`make test` 2 个测试通过、`make lint` 0 报错。
- 今日 AI 实际应用：Copilot 生成样板（pyproject 配置、测试样板）；`Settings` 读取 `.env` 的路径计算、依赖注入与 `dependency_overrides` 必须自己理解——明天 LLM Gateway 的 key / base_url / timeout 全靠它注入，测试也靠 override 替换假 provider。

## 2. 起点（前置确认）

- 已有：`~/lab/workpilot`（v0.0.0），根目录有 `.env.example`、Makefile；`make bootstrap` 生成过 `.env`。
- 需确认：

```bash
cd ~/lab/workpilot && git pull && git status --short
uv --version || brew install uv          # Day05 P1 未做则现在装
ls -a | grep -E '^\.env$' || cp .env.example .env
ls apps/api                               # 期望：README.md tests/
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `uv run python --version`（在 apps/api 下）输出 `Python 3.12.x`
- [ ] `make dev` 后 `curl -s localhost:8000/health` 返回 `{"status":"ok","env":"dev","version":"0.0.1"}`
- [ ] 浏览器 `http://localhost:8000/docs` 可见 `GET /health`
- [ ] `make test` 输出 `2 passed`
- [ ] `make lint` 无报错（`All checks passed!` 且格式检查通过）
- [ ] `uv.lock` 已提交，`.venv/` 未出现在 `git status`

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                     |
| ----------- | ------ | -------------------------------------------------------- |
| 0–10 min    | P0     | 前置确认 + `uv python install 3.12`                      |
| 10–25 min   | P0     | uv 初始化 + 加依赖 + pyproject 工具配置                  |
| 25–60 min   | P0     | `config.py` / `health.py` / `main.py` / `test_health.py` |
| 60–80 min   | P0     | Makefile 接线 + 验证 curl / docs / pytest / ruff         |
| 80–90 min   | P0     | 提交 push                                                |
| 90–110 min  | P1     | `/v1/echo` 体验 Pydantic 校验与 422（体验后不提交）      |
| 110–120 min | P1     | 概念自检口述 + 产出记录                                  |
| —           | P2     | 读 FastAPI 教程 Dependencies 一节                        |

时间不足时最低保留：`/health` + `test_health_ok` + `make dev / test` + push；ruff 配置顺延到 Day08 开头。

## 5. 今日学习（只学完成任务必须的）

- **ASGI**：Python 异步 Web 服务器接口；uvicorn 是 ASGI 服务器，FastAPI 是 ASGI 应用，`uvicorn app.main:app` = 「模块路径:变量名」。
- **Pydantic 校验**：请求体 / 响应用 `BaseModel` 声明，类型或约束不符自动 422，并生成 OpenAPI（`/docs`）。
- **依赖注入**：`Annotated[Settings, Depends(get_settings)]` 让路由声明「我需要什么」，测试时用 `app.dependency_overrides` 替换。
- **async def vs def**：`async def` 在事件循环中运行，里面只能用 await 型 IO；普通 `def` 路由被放到线程池执行，不会阻塞。明天调 LLM 用 `async def` + AsyncOpenAI。
- **pydantic-settings**：环境变量 > `.env` 文件 > 默认值；默认禁止多余键，所以要 `extra="ignore"`。
- 资料：https://docs.astral.sh/uv/ 、https://fastapi.tiangolo.com/ 、https://docs.pydantic.dev/latest/concepts/pydantic_settings/ 、https://docs.astral.sh/ruff/ 、https://docs.pytest.org/

## 6. 执行步骤

### Step 1 · 安装 Python 并初始化项目（P0）

```bash
uv python install 3.12
cd ~/lab/workpilot/apps/api
uv init --app --name workpilot-api --python 3.12 --no-readme --vcs none
rm -f main.py hello.py     # uv 生成的示例入口（版本不同文件名不同），我们的入口是 app/main.py
uv add fastapi "uvicorn[standard]" pydantic-settings
uv add --dev pytest httpx ruff
mkdir -p app/core app/routes
touch app/__init__.py app/core/__init__.py app/routes/__init__.py
```

完成后的目录（每个目录做什么）：

```text
apps/api/
├── pyproject.toml        # 项目元数据 + 依赖 + pytest/ruff 配置；依赖只用 uv add 改
├── uv.lock               # 精确锁定版本，提交到 Git，保证别处 uv sync 结果一致
├── .python-version       # 3.12，uv 据此选解释器
├── .venv/                # 虚拟环境（被根 .gitignore 忽略）
├── app/                  # 应用代码包（蓝图 §6.2）
│   ├── main.py           # create_app()：FastAPI 实例 + 路由挂载（明天加异常处理与 lifespan）
│   ├── core/config.py    # Settings：所有配置的唯一入口
│   └── routes/health.py  # GET /health
└── tests/test_health.py  # pytest + TestClient
```

在 `pyproject.toml` 末尾追加：

```toml
[tool.pytest.ini_options]
pythonpath = ["."]          # 让 tests 能 import app（本项目不作为包安装）
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]   # 基础错误 + 未用变量 + import 排序 + 新语法 + 常见 bug
```

### Step 2 · 配置：app/core/config.py（P0，自己理解）

```python
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# 本文件在 workpilot/apps/api/app/core/config.py
# parents[0]=core [1]=app [2]=api [3]=apps [4]=workpilot（仓库根，.env 所在）
ROOT_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # .env 里有 EMBEDDING_/MINIO_ 等暂未使用的键，忽略而不是报错
    )

    app_env: Literal["dev", "test", "prod"] = "dev"   # 对应 APP_ENV（大小写不敏感）
    log_level: str = "INFO"
    app_version: str = "0.0.1"


@lru_cache
def get_settings() -> Settings:
    """进程内只解析一次 .env；测试中用 dependency_overrides 替换。"""
    return Settings()
```

### Step 3 · 路由与应用（P0）

`app/routes/health.py`：

```python
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: Literal["ok"] = "ok"
    env: str
    version: str


@router.get("/health", response_model=HealthOut)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthOut:
    return HealthOut(env=settings.app_env, version=settings.app_version)
```

`app/main.py`：

```python
from fastapi import FastAPI

from app.core.config import get_settings
from app.routes import health


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="WorkPilot API", version=settings.app_version)
    app.include_router(health.router)
    return app


app = create_app()
```

### Step 4 · 测试：tests/test_health.py（P0）

```python
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["env"] in {"dev", "test", "prod"}


def test_health_uses_injected_settings():
    # 不读 .env，直接注入 —— 明天用同样手法注入假 LLM provider
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, app_env="test")
    try:
        r = client.get("/health")
    finally:
        app.dependency_overrides.clear()
    assert r.json()["env"] == "test"
```

### Step 5 · Makefile 接线（P0）

把仓库根 `Makefile` 中 `dev / test / lint` 三个 TODO target 替换为（配方行 Tab 开头）：

```makefile
API_DIR := apps/api

dev: ## 启动 API（热重载，:8000）
	cd $(API_DIR) && uv run uvicorn app.main:app --reload --port 8000

test: ## 运行 API 测试
	cd $(API_DIR) && uv run pytest -q

lint: ## ruff 检查 + 格式检查
	cd $(API_DIR) && uv run ruff check . && uv run ruff format --check .
```

`API_DIR := apps/api` 放在 `COMPOSE := ...` 下一行。

### Step 6 · 验证（P0）

```bash
cd ~/lab/workpilot
make dev                                   # 终端 A，看到 Uvicorn running on http://127.0.0.1:8000
curl -s localhost:8000/health              # 终端 B，期望 {"status":"ok","env":"dev","version":"0.0.1"}
open http://localhost:8000/docs            # Swagger UI，可点 Try it out
make test                                  # 期望 2 passed
make lint                                  # 若格式检查失败：cd apps/api && uv run ruff format . 后重跑
APP_ENV=prod make dev                      # 体验「环境变量优先于 .env」，/health 返回 env=prod
```

### Step 7 · 体验 Pydantic 422（P1，体验后不提交）

临时在 `health.py` 末尾加：

```python
from pydantic import Field


class EchoIn(BaseModel):
    text: str = Field(min_length=1, max_length=200)
    times: int = Field(1, ge=1, le=3)


@router.post("/v1/echo")
async def echo(body: EchoIn) -> dict[str, str]:
    return {"echo": " ".join([body.text] * body.times)}
```

```bash
curl -s -X POST localhost:8000/v1/echo -H 'Content-Type: application/json' -d '{"text":"hi","times":9}'
# 期望 422，detail 指出 times 应 <= 3；明天 /v1/chat 的入参校验就是这个机制
git restore apps/api/app/routes/health.py
```

### Step 8 · 提交

```bash
cd ~/lab/workpilot
git status --short            # 应有 apps/api/{pyproject.toml,uv.lock,.python-version,app/,tests/} 与 Makefile；无 .venv、.env
git add apps/api Makefile
git commit -m "feat(api): bootstrap FastAPI app with settings, health check and tests"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. `uvicorn app.main:app` 中两个 `app` 各指什么？（答：前者是 `app` 包 / 模块路径，后者是 `main.py` 里的 FastAPI 实例变量）
2. 环境变量 `APP_ENV=prod` 与 `.env` 中 `APP_ENV=dev` 同时存在，取哪个？（答：环境变量优先，`prod`）
3. 为什么 `get_settings` 要 `@lru_cache`？（答：避免每个请求重新读文件解析；同时保证全局同一份配置）
4. 请求体 `times=9` 为什么不会进到函数里？（答：Pydantic 在调用前校验失败，FastAPI 直接返回 422）
5. `async def` 路由里调用同步阻塞的 `requests.get` 会怎样？（答：阻塞整个事件循环，所有请求变慢；应改用异步客户端或普通 `def`）
6. `uv.lock` 为什么要提交？（答：锁定传递依赖的精确版本，CI / 新机器 / Docker 构建可复现）

## 8. 对 DA-01 的贡献

WorkPilot 有了可运行的后端进程与「配置 → 依赖注入 → 路由 → 测试」的标准链路。明天的 LLM Gateway、W4 的 `/v1/kb/*`、W9 的工具接口都按同一模式加文件；`dependency_overrides` 让所有外部依赖（LLM、Qdrant）在单测中可替换，`make test` 不触网。

## 9. 求职映射（D 线）

- 岗位能力：Python 3.12 / FastAPI / Pydantic v2 / pytest / uv / ruff
- 对应岗位：AI 应用工程师、AI 全栈工程师、LLM Engineer（JD 最高频的 Python + FastAPI）
- 简历 bullet 草稿：基于 FastAPI + Pydantic v2 + pydantic-settings 搭建 AI 服务后端骨架，依赖注入实现配置与外部服务可替换，单测不依赖网络，`make test` \_\_ 秒内完成。
- 面试可能问：
  - 「FastAPI 的依赖注入有什么用？」→ 要点：解耦配置 / 客户端 / 鉴权；可组合可缓存；测试中 `dependency_overrides` 替换外部依赖。
  - 「为什么选 uv 而不是 pip / poetry？」→ 要点：速度快、统一管理 Python 版本 + 虚拟环境 + 锁文件，一个工具替代 pyenv + pip + poetry。

## 10. 卡住时的处理

| 现象                                                                     | 处理                                                                               |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `uv python install` 下载超时                                             | 从 GitHub 下载解释器：`export HTTPS_PROXY=http://127.0.0.1:7890` 后重试            |
| `curl localhost:8000` 返回代理错误页或 502                               | 终端设置了代理：`export NO_PROXY=localhost,127.0.0.1`，或 `curl --noproxy '*' ...` |
| `ModuleNotFoundError: No module named 'app'`（pytest）                   | pyproject 缺 `pythonpath = ["."]`，或不在 `apps/api` 下运行                        |
| `ValidationError ... Extra inputs are not permitted`                     | `SettingsConfigDict` 缺 `extra="ignore"`                                           |
| `uv init` 报 `already initialized`                                       | 已有 `pyproject.toml`；检查内容后直接从 `uv add` 继续                              |
| ruff 报 `B008 Do not perform function call Depends in argument defaults` | 改用 `Annotated[Settings, Depends(get_settings)]` 写法                             |

## 11. 产出记录（执行时填写）

- Python / uv / FastAPI 版本：\_\_\_\_
- `/health` 返回：\_\_\_\_
- pytest 结果：\_**\_　ruff 结果：\_\_**
- 422 体验时 detail 的关键信息：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day08 Task 3（LLM Gateway v0）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
