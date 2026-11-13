# Day 29 · 2026-11-12 · Week 07 Task 4 执行总结（SUMMARY）

> 对应 PLAN：`plan/plan_ai/phase_01/week_07/day29_20261112/PLAN.md`
> 结论：**代码 / 脚本 / 文档已全部产出并本地验证通过；涉及 Docker 与云端服务器的「实际运行」项因环境未就绪（Docker daemon 未运行、`wp-prod` SSH 未配置）未能执行，已标 CONDITIONAL，命令全部备齐（见第三节）。**

---

## 一、每个 Step 做了什么

| Step | 内容 | 状态 | 产出 |
|------|------|------|------|
| 1 | 测试分层：`live` 标记 | ✅ 完成并本地验证 | `apps/api/pyproject.toml`、3 个测试文件、`README.md` |
| 2 | 启动并注册 act_runner | ⚠️ 环境未就绪（Docker 未运行） | 完整命令已备（见 Step 2 / runbook） |
| 3 | `.gitea/workflows/ci.yml` | ✅ 文件已创建、YAML 校验通过 | `.gitea/workflows/ci.yml` |
| 4 | `backup.sh` + 服务器跑一次 + Mac 拉回 | ✅ 脚本已创建；运行项未执行 | `deploy/scripts/backup.sh` |
| 5 | 恢复演练 + `restore.sh` | ✅ 脚本已创建；演练未执行 | `deploy/scripts/restore.sh` |
| 6 | runbook + crontab + 周复盘 + 提交 | ✅ 文档已写、crontab 命令已备；未提交 | `docs/runbook.md`、week_07 `README.md` 第 11 节 |

### Step 1 · 测试分层（已本地验证）

- `apps/api/pyproject.toml`：`markers` 由 `llm` 改为 `live`，`addopts` 改为 `-m 'not live'`。
- `apps/api/tests/test_structured_live.py`：`pytestmark = pytest.mark.llm` → `pytest.mark.live`，docstring 同步。
- `apps/api/tests/test_llm_gateway.py`：`@pytest.mark.llm`（真实 LLM smoke）→ `@pytest.mark.live`。
- `apps/api/tests/test_ask.py`、`README.md`：docstring / 命令中的 `not llm` → `not live`。
- **本地验证结果**：
  - `uv run ruff check .` → `All checks passed!`
  - `uv run pytest -m "not live" -q` → `53 passed, 2 deselected in 3.36s`
  - `uv run pytest --collect-only -q -m live` → `test_live_provider_smoke` + `test_structured_pass_rate_5_cases`（2 个 live 测试，正确被标记、默认跳过）

### Step 2 · 启动并注册 act_runner（未执行，命令备齐）

未执行原因：`docker exec gitea gitea --version` 返回 `Cannot connect to the Docker daemon`（Docker Desktop 未启动）。完整命令见下文第三节「验收 1」及 `docs/runbook.md`「CI」节。

### Step 3 · ci.yml（已创建）

`.gitea/workflows/ci.yml`：`api` job（ruff + pytest 非 live）+ `web` job（tsc + build），均带 `github-server-url: http://host.docker.internal:3000`，api job 带占位 `env`（不放真实密钥）。YAML 已用 `yaml.safe_load` 校验通过。

### Step 4 · backup.sh（已创建）

`deploy/scripts/backup.sh`：Qdrant 快照（创建→下载→删服务端）→ SQLite 在线备份 API → MinIO 只读卷打包 → 汇总 tgz + 保留最近 7 份。`bash -n` 语法校验通过。

### Step 5 · restore.sh（已创建）

`deploy/scripts/restore.sh <backup.tgz>`：校验内容 → 确认提示（删卷）→ 停服删三卷 → 重建空卷 → 还原 MinIO / SQLite / Qdrant 快照 → 起全栈 → 输出 RTO。`bash -n` 语法校验通过。

### Step 6 · runbook + crontab + 周复盘（文档已写）

- `docs/runbook.md`：新增「备份 / 恢复 / CI」三节（内容、位置、保留策略、Mac 拉取、恢复步骤 + RTO 占位、runner 启动命令 + 常见失败）。
- crontab 命令已备（见第三节「验收 7」）。
- 周复盘已填 `plan/plan_ai/phase_01/week_07/README.md` 第 11 节。
- **未提交**（按你的要求「不用帮我提交代码」）。

---

## 二、环境现状（诚实说明）

| 前置依赖 | 现状 |
|----------|------|
| Docker daemon | ❌ 未运行（`Cannot connect to the Docker daemon`） |
| Gitea（`http://localhost:3000`） | ❌ 依赖 Docker，未运行 |
| `wp-prod` SSH 别名 | ❌ 未配置（`Could not resolve hostname wp-prod`） |
| uv / ruff / pytest | ✅ 可用（ruff 0.16.10） |

**结论**：Step 2 / 4 / 5 的「实际运行」以及全部 7 条验收的「现场执行」，需要先启动 Docker Desktop、配置 `~/.ssh/config` 的 `wp-prod`、完成 Gitea runner 注册。所有命令已在第三节逐条备齐，可直接按序执行。

---

## 三、验收对齐（逐条完整命令）

> 说明：以下每条都是**可直接复制到终端、任何目录下都能跑**的完整命令；唯一需要你替换的是**密钥类占位**（token / 密码 / 域名），其余均无省略号、无「...」。
> 执行前一次性准备：

```bash
# ① 启动 Docker Desktop（图形化打开即可），确认 daemon 就绪
docker info >/dev/null 2>&1 && echo "docker OK" || echo "请先启动 Docker Desktop"

# ② 获取 Gitea API token（一次性）：浏览器打开
#    http://localhost:3000/user/settings/applications → 生成令牌（勾选 read:repository、read:organization）→ 复制
#    然后在终端 export（供下面 curl 复用）
export GITEA_TOKEN="<粘贴你的 Gitea token>"

# ③ wp-prod 别名：在 ~/.ssh/config 增加（HostName 换成你的服务器 IP），之后 ssh wp-prod 才可用
#    Host wp-prod
#      HostName <服务器IP>
#      User deploy
#      IdentityFile ~/.ssh/workpilot_ed25519
```

---

### 验收 1 · Gitea Runners 中 runner 状态 Idle / Online

**完整命令：**

```bash
# 1a. 先按 Step 2 启动并注册 runner（token 从 http://localhost:3000 → 站点管理 → Actions → Runners → 创建新 Runner 复制）
mkdir -p ~/gitea/runner
docker run -d --name gitea-runner --restart unless-stopped \
  -e GITEA_INSTANCE_URL=http://host.docker.internal:3000 \
  -e GITEA_RUNNER_REGISTRATION_TOKEN=<粘贴 Registration Token> \
  -e GITEA_RUNNER_NAME=mac-runner \
  -e GITEA_RUNNER_LABELS=ubuntu-latest:docker://gitea/runner-images:ubuntu-latest \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/gitea/runner:/data \
  gitea/act_runner:latest

# 1b. 看注册日志，出现 "declared successfully" 即注册成功
docker logs gitea-runner 2>&1 | grep -i "declared successfully"

# 1c. 终端确认 runner 容器在跑
docker ps --filter "name=gitea-runner" --format "{{.Names}}  {{.Status}}"

# 1d. 用 API 确认 runner 状态（返回 JSON，含 "status":"idle"）
curl -s -H "Authorization: token $GITEA_TOKEN" \
  "http://localhost:3000/api/v1/admin/runners" | python3 -m json.tool
```

**预期效果**：`1b` 打印出 `runner: mac-runner ... declared successfully`；`1c` 输出 `gitea-runner  Up ...`；`1d` 的 JSON 里 `status` 为 `idle`（或浏览器 Runners 页显示 mac-runner 为 Idle / Online）。

---

### 验收 2 · push 后 Actions 页 `ci` 工作流 api / web 两个 job 均绿色

**完整命令：**

```bash
# 2a. 推送当前改动触发 CI
cd ~/lab/workpilot && git push

# 2b. 用徽章确认工作流状态（仓库公开则无需 token；绿色 "passing" 即通过）
curl -s "http://localhost:3000/infinity/workpilot/actions/workflows/ci.yml/badge.svg" \
  | grep -oE "passing|failing|pending|unknown"

# 2c. 用 API 看最近一次 run 及其 job 结论（"conclusion":"success"）
curl -s -H "Authorization: token $GITEA_TOKEN" \
  "http://localhost:3000/api/v1/repos/infinity/workpilot/actions/runs?limit=1" \
  | python3 -m json.tool
```

**预期效果**：`2b` 输出 `passing`；`2c` 的 JSON 里最近 run 的 `conclusion` 为 `success`；浏览器 `http://localhost:3000/infinity/workpilot/actions` 里 `ci` 的 `api`、`web` 两个 job 均为绿色 ✓。

---

### 验收 3 · 故意引入一个 ruff 错误 push → CI 红 → 修复后绿（证明门禁有效）

**完整命令（先制造错误）：**

```bash
cd ~/lab/workpilot
# 在 main.py 末尾追加一个未使用的 import，触发 ruff F401/E402
echo "import os" >> apps/api/app/main.py
git add apps/api/app/main.py
git commit -m "ci: introduce intentional ruff error"
git push

# 等约 1 分钟后查徽章，应为 failing（红）
curl -s "http://localhost:3000/infinity/workpilot/actions/workflows/ci.yml/badge.svg" \
  | grep -oE "passing|failing|pending|unknown"
```

**预期效果**：输出 `failing`；Actions 页 `api` job 的 Lint 步骤红，报 `F401 os imported but unused` 或 `E402`。

**完整命令（修复错误）：**

```bash
cd ~/lab/workpilot
# 删掉刚追加的那行 import os
sed -i '' '/^import os$/d' apps/api/app/main.py
git add apps/api/app/main.py
git commit -m "ci: fix intentional ruff error"
git push

# 等约 1 分钟后查徽章，应回到 passing（绿）
curl -s "http://localhost:3000/infinity/workpilot/actions/workflows/ci.yml/badge.svg" \
  | grep -oE "passing|failing|pending|unknown"
```

**预期效果**：先 `failing`（红）后 `passing`（绿），证明门禁确实能拦住坏代码。

---

### 验收 4 · 服务器 `~/backups/wp-*.tgz` 存在，内含 `qdrant-*.snapshot`、`workpilot.db`、`minio.tgz`

**完整命令：**

```bash
# 4a. 同步脚本到服务器并首次手动跑一次备份
ssh wp-prod 'chmod +x ~/workpilot/deploy/scripts/backup.sh && ~/workpilot/deploy/scripts/backup.sh'

# 4b. 列出最新一份备份文件（应看到 wp-YYYYmmdd-HHMMSS.tgz）
ssh wp-prod 'ls -1t ~/backups/wp-*.tgz | head -1'

# 4c. 校验最新一份的内容，必须看到三件
ssh wp-prod 'tar tzf $(ls -1t ~/backups/wp-*.tgz | head -1)'
```

**预期效果**：`4a` 最后一行输出 `backup ok: /home/deploy/backups/wp-YYYYmmdd-HHMMSS.tgz (XXM)`；`4c` 输出三行，分别包含 `qdrant-kb_default.snapshot`、`workpilot.db`、`minio.tgz`。

---

### 验收 5 · Mac `~/lab/backups/workpilot-cloud/` 有同一份副本

**完整命令：**

```bash
# 5a. 从服务器拉回 Mac（异地副本）
mkdir -p ~/lab/backups/workpilot-cloud && rsync -az wp-prod:backups/ ~/lab/backups/workpilot-cloud/

# 5b. Mac 端列出最新一份
ls -1t ~/lab/backups/workpilot-cloud/wp-*.tgz | head -1

# 5c. Mac 端校验内容与服务器一致（同样三件）
tar tzf $(ls -1t ~/lab/backups/workpilot-cloud/wp-*.tgz | head -1)
```

**预期效果**：`5b` 输出与 `4b` 同名（同一时间戳）的 `.tgz`；`5c` 同样输出 `qdrant-kb_default.snapshot`、`workpilot.db`、`minio.tgz` 三行。

---

### 验收 6 · 恢复演练：清空卷后问答失败 → 恢复后同一问题返回带引用答案；RTO 写入 runbook

**完整命令（执行恢复演练，脚本内含确认提示，输入 yes）：**

```bash
# 6a. 执行恢复（会删云端数据卷，只对 Demo 环境执行；提示处输入 yes）
ssh wp-prod '~/workpilot/deploy/scripts/restore.sh $(ls -1t ~/backups/wp-*.tgz | head -1)'
```

**预期效果**：脚本末尾输出 `RTO: XX 秒（约 X 分钟）`。

**完整命令（恢复后验证服务与问答带引用）：**

```bash
# 6b. 确认 api 就绪（返回 {"status":"ok",...}）
curl -s -u "<BASIC_AUTH_USER>:<BASIC_AUTH_PASSWORD>" "https://wp.<域名>/health"

# 6c. 用同一个样例问题问 RAG（返回 JSON 里 answer 有内容、citations 非空）
curl -s -u "<BASIC_AUTH_USER>:<BASIC_AUTH_PASSWORD>" \
  -H 'Content-Type: application/json' \
  -d '{"question":"<同一样例问题>"}' \
  "https://wp.<域名>/v1/kb/ask"

# 6d. 确认知识库文档列表与备份前一致（返回 JSON 数组）
curl -s -u "<BASIC_AUTH_USER>:<BASIC_AUTH_PASSWORD>" "https://wp.<域名>/v1/kb/docs"
```

**预期效果**：`6b` 返回 `"status":"ok"`；`6c` 返回的 `answer` 有正文且 `citations` 数组非空（引用点开有片段）；`6d` 文档列表与备份前一致。

**回填 RTO：** 把 `6a` 输出的分钟数写进 `docs/runbook.md`「恢复」节的 `RTO ___ 分钟`（当前为占位，待实测后回填）。

---

### 验收 7 · 服务器 `crontab -l` 含每日备份；Week 7 复盘已填；已 commit + push

**完整命令（设置每日备份 cron）：**

```bash
# 7a. 安装每日备份 cron（每天 03:30 UTC = 北京时间 11:30）
ssh wp-prod '(crontab -l 2>/dev/null; echo "30 3 * * * \$HOME/workpilot/deploy/scripts/backup.sh >> \$HOME/backups/backup.log 2>&1") | crontab -'

# 7b. 校验 cron 已写入（应看到 30 3 * * * 那一行）
ssh wp-prod 'crontab -l'
```

**预期效果**：`7b` 输出包含 `30 3 * * * .../backup.sh ...` 一行。

**Week 7 复盘**：已填（`plan/plan_ai/phase_01/week_07/README.md` 第 11 节）。

**提交**（等你验收通过后执行，我不代提交）：

```bash
cd ~/lab/workpilot
git add .gitea/workflows/ci.yml deploy/scripts/backup.sh deploy/scripts/restore.sh \
        apps/api/pyproject.toml apps/api/tests/test_structured_live.py \
        apps/api/tests/test_llm_gateway.py apps/api/tests/test_ask.py README.md docs/runbook.md
git commit -m "ops: add gitea ci workflow and cloud backup/restore scripts with runbook" && git push
```

---

## 四、改动文件清单

**`~/lab/workpilot`（未提交）：**

| 文件 | 变更 |
|------|------|
| `apps/api/pyproject.toml` | markers `llm`→`live`、addopts `-m 'not live'` |
| `apps/api/tests/test_structured_live.py` | `pytest.mark.llm`→`live` |
| `apps/api/tests/test_llm_gateway.py` | `@pytest.mark.llm`→`live` |
| `apps/api/tests/test_ask.py` | docstring 措辞 |
| `README.md` | 单测命令 `not llm`→`not live` |
| `.gitea/workflows/ci.yml` | 新增（api lint/test + web typecheck/build） |
| `deploy/scripts/backup.sh` | 新增 |
| `deploy/scripts/restore.sh` | 新增 |
| `docs/runbook.md` | 新增「备份 / 恢复 / CI」三节 |
| `.gitea/workflows/.gitkeep`、`deploy/scripts/.gitkeep` | 删除（已有真实文件） |

**`/Users/infinity/Documents/a_future`（未提交）：**

| 文件 | 变更 |
|------|------|
| `plan/plan_ai/phase_01/week_07/README.md` | 第 11 节周复盘已填 |

---

## 五、待办（环境就绪后按序补齐，标 CONDITIONAL / W9 第一天）

1. 启动 Docker Desktop，启动 Gitea，注册 act_runner（验收 1）。
2. `git push` 触发 CI，把 `ci` 跑到两个 job 全绿（验收 2）。
3. 做一次「故意 ruff 错误 → 红 → 修复 → 绿」（验收 3）。
4. 配置 `wp-prod` SSH，`make deploy` 同步脚本，跑一次 `backup.sh` 并 rsync 回 Mac（验收 4 / 5）。
5. 跑 `restore.sh` 恢复演练，记录 RTO 回填 runbook（验收 6）。
6. 装 crontab，`commit + push`（验收 7）。
