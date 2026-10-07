# Day 69 · 2027-02-23 · Week 22 Task 2：抽取模板库 + Pro Kit 打包（v2.0）

## 0. 今天只做一件事

从 WorkPilot 真实代码中抽取 `personal-ai-engineering` 模板库（10 个目录，每个有「如何复制使用」README，核心模板最小可运行），打包 Pro Kit 并定价，发布 `v2.0.0`（P3 完成）。

不碰：新功能、Portfolio 网站（Day70）、正式上架收款（W23 安全检查后再决定）、把 WorkPilot 整仓复制成模板。

## 1. 资产锚点

- 构建模块：M14 可复用工程模板、M12.2 Pro Kit（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v2.0（P3 发布：生产级解决方案 + 回归体系 + Pro Kit）**
- 今天之后 WorkPilot 多了什么（可演示/可测量）：v2.0.0 Release；`personal-ai-engineering` 公开仓库（复制 fastapi-template 5 分钟跑起来，计时可证）；`dist/workpilot-pro-kit-v2.0.0.zip`
- 今日 AI 实际应用：把半年做过的 RAG / Agent / Eval / Observability 抽象成可复用骨架——DA-02 将直接从这里起步

## 2. 起点（前置确认）

- 已有：WorkPilot v1.4 + Day68 评测体系；W1 `ai-project-template`；W16 `docs/open-core.md`；Day59 开源边界决定。
- 需确认：

```bash
cd ~/lab/workpilot && git status && make eval-smoke          # 主干干净且门禁绿
grep -n -i "pro\|MIT" docs/open-core.md | head              # 开源边界
ls ~/lab/                                                    # 确认没有同名目录
which gitleaks || docker pull ghcr.io/gitleaks/gitleaks:latest
```

在 Gitea Web UI 新建仓库 `personal-ai-engineering`（Public 或 Private 均可，GitHub 上公开），**先在 Web UI 建再 clone**。

## 3. 验收对齐（做完要能勾掉）

- [ ] 10 个目录：rag-template、agent-template、evaluation-template、fastapi-template、docker-template、ai-observability、prompts、badcases、datasets、interview，每个有 README（用途 / 复制命令 / 依赖 / 最小运行 / 来源 WorkPilot 文件）
- [ ] fastapi-template：`cp -r` 到 `/tmp` → `uv sync` → `pytest` → `/health` 200，计时 ≤ 5 分钟（P0）
- [ ] docker-template：`docker compose up -d` 起 api + postgres，`/ready` 200（P0）
- [ ] rag / agent / evaluation / observability 四个模板含最小可运行代码（P1，Day76 前必须完成，凑满 ≥ 6）
- [ ] gitleaks 扫描无发现，推送 Gitea + GitHub
- [ ] WorkPilot `v2.0.0` tag + `docs/releases/v2.0.0.md` Release notes，自动部署成功
- [ ] （P1）`scripts/build_pro_kit.sh` 生成 `dist/workpilot-pro-kit-v2.0.0.zip`；定价写入 `pricing.md`；上架草稿写入 `listing-draft.md`

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                   |
| ----------- | ------ | ---------------------------------------------------------------------- |
| 0–10 min    | P0     | 建仓库 + 10 目录 + README 模板                                         |
| 10–35 min   | P0     | fastapi-template 抽取 + 5 分钟验证（计时）                             |
| 35–50 min   | P0     | docker-template 抽取 + 验证                                            |
| 50–60 min   | P0     | prompts / badcases / datasets / interview 四个文档型目录               |
| 60–70 min   | P0     | gitleaks + 推送；WorkPilot tag v2.0.0 + Release notes                  |
| 70–95 min   | P1     | rag / agent / evaluation / observability 最小代码（AI 抽取，人工裁剪） |
| 95–115 min  | P1     | Pro Kit 素材 + 打包脚本 + 定价 + 上架草稿                              |
| 115–120 min | P0     | 提交                                                                   |
| 顺延        | P2     | 模板 CI、cookiecutter/copier 参数化、英文 README → Backlog             |

时间不足时最低保留：仓库骨架 + fastapi / docker 两个可运行模板 + tag v2.0.0。

## 5. 今日学习（只学完成任务必须的）

- **抽取而非复制**：模板 = 「去掉业务的最小骨架 + 扩展点说明」；判断标准：别人 5 分钟能跑、30 分钟能改成自己的东西。
- **模板 README 四要素**：解决什么问题 / 一条复制命令 / 最小运行步骤 / 在哪里改（扩展点）。
- **Pro Kit 价值主张**：开源代码可以自己搭，Pro Kit 卖「省掉的 N 小时」：生产 compose + Caddy + 认证/多空间配置、部署手册、场景包 prompt/rubric/评测集、备份恢复脚本、6 个月更新。
- **定价锚点**：以「省下的时间 × 时薪」与同类模板价格为参照，在 ¥199–499 区间选一个，可设早鸟价。
- 资料：https://docs.gitea.com/ 、https://docs.astral.sh/uv/ 、https://github.com/gitleaks/gitleaks 、https://choosealicense.com/

## 6. 执行步骤

### Step 1 · 仓库骨架（P0）

```bash
cd ~/lab && git clone http://localhost:3000/<user>/personal-ai-engineering.git && cd personal-ai-engineering
mkdir -p rag-template agent-template evaluation-template fastapi-template docker-template \
         ai-observability prompts badcases datasets interview
```

每个目录 README 模板（可让 AI 按此批量生成初稿，再逐个改）：

```markdown
# fastapi-template

> 来源：WorkPilot apps/api（v2.0.0）的最小骨架。

## 解决什么

新 AI 后端项目 5 分钟起步：配置、JSON 日志 + request_id、/health /ready、pytest、Dockerfile。

## 复制使用

cp -r fastapi-template ~/lab/<new-project>/api && cd $\_ && uv sync && uv run pytest && uv run uvicorn app.main:app --reload

## 扩展点

- app/core/config.py：新增配置项
- app/routes/：新增路由

## 不包含

认证、数据库、LLM（分别见 docker-template / rag-template）
```

根 README：一句话定位 + 目录表（模板 / 用途 / 成熟度：runnable / doc-only）+ License（MIT）。

### Step 2 · fastapi-template（P0，计时）

从 WorkPilot 抽取，只保留：

```text
fastapi-template/
├── pyproject.toml          # fastapi, uvicorn, pydantic-settings, pytest, httpx
├── app/
│   ├── main.py             # app 实例 + request_id 中间件 + 路由挂载
│   ├── core/config.py      # Settings(BaseSettings)
│   ├── core/logging.py     # JSON 日志
│   └── routes/health.py    # /health /ready
├── tests/test_health.py
├── Dockerfile              # 多阶段，uv
└── .env.example
```

```python
# app/main.py
import uuid, logging
from fastapi import FastAPI, Request
from app.core.logging import setup_logging
from app.routes import health

setup_logging()
app = FastAPI(title="service")
app.include_router(health.router)

@app.middleware("http")
async def request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex
    response = await call_next(request)
    response.headers["x-request-id"] = rid
    logging.getLogger("access").info("request", extra={"request_id": rid, "path": request.url.path,
                                                      "status": response.status_code})
    return response
```

5 分钟验证（**计时，写进 README「验证记录」**）：

```bash
rm -rf /tmp/tpl-check && time ( cp -r fastapi-template /tmp/tpl-check && cd /tmp/tpl-check \
  && uv sync -q && uv run pytest -q && (uv run uvicorn app.main:app --port 8099 & sleep 3) \
  && curl -fsS localhost:8099/health )
pkill -f "uvicorn app.main:app --port 8099"
```

### Step 3 · docker-template（P0）

`docker-template/`：`docker-compose.yml`（api 构建自 `../fastapi-template` 或占位镜像 + postgres:16 + healthcheck）、`Caddyfile.example`、`backup.sh` / `restore.sh`（从 WorkPilot 简化，去掉 Qdrant/MinIO 或标为可选）、README（端口、卷、备份恢复命令）。验证 `docker compose up -d && curl -fsS localhost:8000/ready`。

### Step 4 · 文档型目录 + 其余模板（P0 / P1）

| 目录                      | 内容（只放可公开的）                                                                        | 来源                           |
| ------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------ |
| prompts                   | 版本化 prompt 规范 + 4 个通用 prompt（qa_answer、planner、breakdown、judge_scenario）       | `prompts/`                     |
| badcases                  | 分类法 + 状态机 + JSONL schema（**不含任何具体 badcase 原文**）                             | `eval/badcases/README.md`      |
| datasets                  | 各数据集 schema + 每类 2–3 条公开样例                                                       | `eval/datasets/README.md`      |
| interview                 | 指向 `career/` 公开版或 Portfolio 的链接 + 题目分组目录                                     | W25 补全                       |
| rag-template（P1）        | loaders(md) + chunking + embedding 接口 + Qdrant store（带 workspace 过滤）+ answer（引用） | `app/rag/`                     |
| agent-template（P1）      | LangGraph 最小图：节点 + 条件边 + interrupt 审批 + 工具注册表                               | `app/agent/`、`app/scenarios/` |
| evaluation-template（P1） | jsonl 加载 + 硬规则 + judge + 报告 + gate 对比                                              | `eval/runners/`                |
| ai-observability（P1）    | trace/span 上下文管理器 + LLMCall 成本记录 + 预算守卫                                       | `app/obs/`                     |

抽取方法：让 Copilot「只保留 X 功能所需代码，删除 WorkPilot 业务与配置，生成 README 与 1 个单测」，**自己检查**：无 WorkPilot 专有路径、无密钥、单测能跑。

### Step 5 · 安全扫描 + 推送（P0）

```bash
cd ~/lab/personal-ai-engineering
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:latest dir /repo -v   # 旧版本用 detect --source /repo --no-git
git add . && git commit -m "feat: extract reusable AI engineering templates from WorkPilot v2.0" && git push
# GitHub 新建空仓库后：
git remote add github git@github.com:<user>/personal-ai-engineering.git && git push github main
```

### Step 6 · WorkPilot v2.0.0（P0）

`docs/releases/v2.0.0.md`：

```markdown
# WorkPilot v2.0.0 · P3 Production

## 新增（v1.0 → v2.0）

- SP-B 需求→任务拆解→Issue（LangGraph + 可编辑审批）
- Postgres + Alembic、JWT 登录、owner/member/viewer、空间隔离（测试覆盖）
- 异步导入 worker（SKIP LOCKED）、tag 自动部署 + 回滚
- 场景评测 + 隐式反馈闭环 + EvalRun 趋势
- OWASP LLM Top 10 加固：攻击集 20/20、AuditLog、恢复演练 \_\_ 分钟
- Eval v2：四类评测 + badcase 总库 + CI 门禁

## 指标（见 eval/reports/20270222-eval-v2.md）

## 升级说明：先备份 → 拉取 v2.0.0 → alembic upgrade head
```

```bash
cd ~/lab/workpilot
git add docs/releases/v2.0.0.md && git commit -m "docs(release): v2.0.0 release notes" && git push
git tag -a v2.0.0 -m "v2.0.0: P3 production release" && git push origin v2.0.0
```

在 Gitea 与 GitHub 的 Releases 页面各发布一次（粘贴 notes）。

### Step 7 · Pro Kit（P1）

私有素材放 `~/lab/projects/product-lab/pro-kit/`（不进 WorkPilot 公开仓库）：`manual.md`（部署手册：服务器要求 → 域名 → .env → compose up → 创建 owner → 备份 cron → 升级 → 排障）、`LICENSE-PRO.md`（单团队使用、不可转售、6 个月更新）、`pricing.md`、`listing-draft.md`。

```bash
#!/usr/bin/env bash
# scripts/build_pro_kit.sh <version>
set -euo pipefail
V="${1:?version}"; SRC="${PRO_SRC:-$HOME/lab/projects/product-lab/pro-kit}"; OUT="dist/pro-kit"
rm -rf "$OUT" && mkdir -p "$OUT"/{deploy,scenario-pack,eval-templates,docs}
cp deploy/docker-compose.prod.yml deploy/Caddyfile deploy/scripts/{backup.sh,restore.sh,deploy.sh} "$OUT/deploy/"
cp .env.example "$OUT/deploy/.env.example"
cp -r apps/api/app/scenarios/sp_b_req_breakdown/prompts "$OUT/scenario-pack/prompts"
cp prompts/judge_scenario.v1.md eval/datasets/README.md "$OUT/eval-templates/"
cp "$SRC/manual.md" "$SRC/LICENSE-PRO.md" "$OUT/docs/"
grep -rIl -E "(sk-|ghp_|BEGIN .*PRIVATE KEY)" "$OUT" && { echo "secret-like string found"; exit 1; } || true
(cd dist && zip -qr "workpilot-pro-kit-${V}.zip" pro-kit)
ls -lh "dist/workpilot-pro-kit-${V}.zip"
```

确认 `dist/` 在 `.gitignore` 中。认证 / 多空间模块按 Day59 开源边界决定：公开方案下 Pro Kit 提供「生产配置 + 手册」，私有方案下从 `workpilot-pro` 复制模块。

`pricing.md`：定价（如 ¥299，早鸟 ¥199）、理由（省时 \_\_ 小时）、退款政策；`listing-draft.md`：标题、3 条卖点、包含内容清单、截图占位、FAQ（数据是否离开服务器 / 支持哪些模型）。平台：面包多或 Gumroad，只写草稿，W23 安全检查后再决定是否上线。

## 7. 概念自检（不看资料，口述，附答案）

1. 模板和「复制整个项目」的区别？（答：模板只保留通用骨架与扩展点，去掉业务与配置；目标是 5 分钟跑、30 分钟改）
2. 为什么 badcases 模板只放分类法？（答：具体 badcase 含业务语境与潜在敏感输入，不适合公开；分类法与流程才是可复用资产）
3. 开源核心与 Pro Kit 不冲突的原因？（答：开源建立信任与流量；Pro 卖时间、生产就绪与更新，目标用户愿为省时付费）
4. 为什么打包脚本里要做密钥特征检查？（答：防止 .env 或测试密钥被误打包，作为发布前最后一道闸门）
5. 为什么 v2.0 后不再加功能？（答：W23–W26 是作品集、求职、复盘阶段；功能冻结保证 Demo 与文档一致）

## 8. 对 DA-01 的贡献

WorkPilot 达到 v2.0：P3 完成，具备生产级能力、评测回归体系和可售卖形态（Pro Kit）。同时半年工程经验沉淀为 `personal-ai-engineering`，这是 DA-02 及以后所有项目的起点，资产从「一个产品」扩展为「一套可复制的生产方法」。

## 9. 求职映射（D 线）

- 岗位能力：工程模板化、复用设计、发布管理、产品打包与定价。
- 对应岗位：AI Full-Stack Engineer、AI Platform Engineer、Tech Lead（AI 方向）。
- 简历 bullet 草稿：「从生产项目抽取 \_\_ 个可复用 AI 工程模板（FastAPI / Docker / RAG / Agent / Eval / Observability），复制即用，新项目启动 ≤ 5 分钟；发布 WorkPilot v2.0 与付费部署包」
- 面试可能问：
  1. 你如何在团队里推广工程规范？——要点：模板化默认值 + README 扩展点 + CI 守护 + 示例项目，而不是只写文档。
  2. 讲讲你的发版流程。——要点：门禁绿 → Release notes → tag → 自动部署 → 冒烟 → 回滚预案。

## 10. 卡住时的处理

| 现象                                  | 处理                                                                              |
| ------------------------------------- | --------------------------------------------------------------------------------- |
| 抽取后 import 依赖 WorkPilot 内部模块 | `grep -rn "from app\.\(rag\|agent\|security\)" fastapi-template` 找出并删除或内联 |
| 5 分钟验证超时（uv 下载慢）           | 记录实际时间；配置 uv 镜像（`UV_INDEX_URL`）后重测；README 写明前置条件           |
| gitleaks 报误报                       | 确认是示例占位符后加 `.gitleaksignore`（写明原因），不要整体关闭规则              |
| GitHub 推送需认证                     | 用 SSH key 或 fine-grained token；不要把 token 写进 remote URL                    |
| 自动部署 v2.0.0 失败                  | 按 runbook 回滚已自动发生；修复后发 `v2.0.1`，不要移动已发布 tag                  |
| 定价纠结                              | 先定 ¥299（早鸟 ¥199），记录理由，W26 复盘根据数据再调                            |

## 11. 产出记录（执行时填写）

- 模板可运行数：** / 10（runnable：\_\_**）
- fastapi-template 验证耗时：** 分 ** 秒
- gitleaks：通过 / 发现 \_\_（已处理）
- v2.0.0 Release 链接：Gitea \_**\_ / GitHub \_\_**
- Pro Kit zip 大小：**；定价：¥**
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节 P0 项全部勾上 → Task 2 DONE → 明天进入 Day70 · W23 Task 1「Portfolio 网站」。任一 P0 未通过 → 保持 IN PROGRESS，明天先补 P0；P1 模板在 Day76 验收前补齐到 ≥ 6 个可运行。
