# Day 29 · 2026-11-12 · Week 07 Task 4 执行总结（SUMMARY）

> 对应 PLAN：`plan/plan_ai/phase_01/week_07/day29_20261112/PLAN.md`
> 结论：**全部 6 个 Step 已执行完成**（测试分层、act_runner 注册、ci.yml、服务器备份、恢复演练、runbook + crontab + 周复盘）。恢复演练实测 **RTO = 22 秒（约 1 分钟）**。CI「跑绿」与「ruff 红→绿」两项因**你要求「不用帮我提交代码」**而未 push，属「待你 commit + push 后自动完成」，命令已备齐（见第三节验收 2 / 3）。
> 环境要点：云端用**公网 IP `8.148.216.61`**（SSH `root@8.148.216.61`）代替域名；云端 Web 走 Caddy 基本认证（密码已轮换，`ChangeMe_2026_Demo` 已失效），故「带引用答案」验证改用**直接进 API 容器**调用本地 `:8000`（见验收 6）。

---

## 一、每个 Step 做了什么

| Step | 内容 | 状态 | 产出 / 实测结果 |
|------|------|------|-----------------|
| 1 | 测试分层：`live` 标记 | ✅ 完成并本地验证 | `apps/api/pyproject.toml`、3 个测试文件、`README.md`；`pytest -m "not live"` → **53 passed, 2 deselected** |
| 2 | 启动并注册 act_runner | ✅ 完成 | `mac-runner` 已注册并在线（label `ubuntu-latest` → `node:20-bookworm`，act_runner v0.6.1） |
| 3 | `.gitea/workflows/ci.yml` | ✅ 已创建、YAML 校验通过 | `.gitea/workflows/ci.yml`（api 与 web 两 job） |
| 4 | `backup.sh` + 服务器跑一次 + Mac 拉回 | ✅ 完成 | 服务器 `/root/backups/wp-20261116-232815.tgz`（656K，含三件）；已拉回 Mac `~/lab/backups/workpilot-cloud/` |
| 5 | 恢复演练 + `restore.sh` | ✅ 完成 | **RTO = 22 秒**；恢复后同问题返回带引用答案（4 条引用，`refused=false`） |
| 6 | runbook + crontab + 周复盘 | ✅ 完成（未 commit/push） | runbook RTO 已回填；root crontab 已装每日备份；week_07 复盘已填 |

### Step 1 · 测试分层（已本地验证）

- `apps/api/pyproject.toml`：`markers` 改为 `live`，`addopts` 改为 `-m 'not live'`。
- `apps/api/tests/test_structured_live.py`、`test_llm_gateway.py`：`pytest.mark.llm` → `pytest.mark.live`；`test_ask.py`、`README.md` 措辞同步。
- 本地验证：`uv run ruff check .` → `All checks passed!`；`uv run pytest -m "not live" -q` → `53 passed, 2 deselected`；`--collect-only -m live` 正确只含 2 个 live 测试。

### Step 2 · 启动并注册 act_runner（已完成）

- 注册 token 来自 Gitea 站点管理 → Actions → Runners → 创建新 Runner（一次性，注册后存于 `~/gitea/runner/.runner`）。
- 实际注册结果：`runner: mac-runner, with version: v0.6.1, with labels: [ubuntu-latest], declare successfully`。
- label 镜像选 **`node:20-bookworm`**（完整版，基于 `buildpack-deps:bookworm`，自带 git / curl / node，满足 `actions/checkout@v4` 与 api/web job 全部依赖；比 PLAN 里的 `gitea/runner-images:ubuntu-latest` 更轻）。

### Step 3 · ci.yml（已创建）

`.gitea/workflows/ci.yml`：`api` job（ruff + pytest 非 live）+ `web` job（tsc + build），均带 `github-server-url: http://host.docker.internal:3000`（job 容器内 `localhost:3000` 不可达），api job 带占位 `env`（不放真实密钥）。YAML 已用 `yaml.safe_load` 校验通过。

### Step 4 · backup.sh（已在服务器跑出首份备份）

- 脚本 `/home/deploy/workpilot/deploy/scripts/backup.sh`：Qdrant 快照（创建→下载→删服务端）→ SQLite 在线备份 API → MinIO 只读卷打包 → 汇总 tgz + 保留最近 7 份。
- 首份备份：`/root/backups/wp-20261116-232815.tgz`（656K），内容三件：`qdrant-kb_default.snapshot`、`workpilot.db`、`minio.tgz`。
- 已 `rsync` 拉回 Mac `~/lab/backups/workpilot-cloud/`。

### Step 5 · restore.sh 恢复演练（已完成，RTO 22 秒）

- 脚本 `/home/deploy/workpilot/deploy/scripts/restore.sh <backup.tgz>`（交互式 `输入 yes` 确认后删卷）。
- 完整周期：校验 tar → `down` + 删三卷 → 重建空卷 + 起 qdrant → 还原 MinIO / SQLite / Qdrant 快照（`{"result":true,"status":"ok"}`）→ 起全栈 → **RTO = 22 秒（约 1 分钟）**。
- 恢复后验证：知识库 5 篇文档、同问题返回带引用答案（4 条引用）、`refused=false`。

### Step 6 · runbook + crontab + 周复盘（已完成，未 commit）

- `docs/runbook.md`：RTO 占位已回填为 `RTO 1 分钟（实测 22 秒，2026-11-16）`；CI 节 runner label 已统一为 `node:20-bookworm`。
- root crontab 已装：`30 3 * * * /home/deploy/workpilot/deploy/scripts/backup.sh >> /root/backups/backup.log 2>&1`（03:30 UTC = 北京时间 11:30）。
- week_07 `README.md` 第 11 节周复盘已填（记录恢复演练 RTO 22s、runner 在线、crontab 已装，并注明 CI「跑绿」待你 push）。
- **未 commit / push**（按你的要求）。

---

## 二、环境与访问方式（本次实际使用）

| 项 | 值 |
|----|----|
| 云端服务器 | `8.148.216.61`，SSH `root@8.148.216.61` |
| 云端代码目录 | `/home/deploy/workpilot/`（属主 `deploy`，uid/gid 10001） |
| 云端容器 | `workpilot-{web,api,qdrant,minio}-1`，网络 `workpilot_default`，卷 `workpilot_{api,minio,qdrant}-data` |
| 本地 Gitea | `http://localhost:3000`（admin `infinity`，仓库 `infinity/workpilot`） |
| 本地 runner | 容器 `gitea-runner`，runner 名 `mac-runner` |
| 云端 API 访问 | 基本认证密码已轮换 → 改用 `docker exec workpilot-api-1 python3` 直连容器内 `http://localhost:8000` |

> 说明：云端 Web 由 Caddy（web 容器内）做基本认证；`.env` 里注释的 `ChangeMe_2026_Demo` 与实际 bcrypt 哈希不匹配（已轮换）。因此「带引用答案」类验证不经过 Caddy，直接进 api 容器调用，避免 401。

---

## 三、验收对齐（逐条完整命令，任何目录可直接复制执行）

> 约定：云端命令已展开为完整 `ssh root@8.148.216.61 '...'`。密钥占位用 `<...>`，其余无省略号、无「...」。

### 验收 1 · Gitea Runners 中 runner 状态 Idle / Online

```bash
# 1a. 确认 runner 容器在跑
docker ps --filter "name=gitea-runner" --format "{{.Names}}  {{.Status}}"

# 1b. 看注册日志（出现 "declared successfully" 即注册成功）
docker logs gitea-runner 2>&1 | grep -i "declared successfully"

# 1c. 浏览器确认（Runners 页显示 mac-runner 为 Idle/Online）
open "http://localhost:3000/admin/actions/runners"
```

**预期效果**：`1a` 输出 `gitea-runner  Up ...`；`1b` 打印 `runner: mac-runner ... declared successfully`；`1c` 打开 Gitea 站点管理 → Actions → Runners 页面，`mac-runner` 状态为 `Idle`/`Online`。

### 验收 2 · push 后 Actions 页 `ci` 工作流 api / web 两个 job 均绿色

```bash
# 2a. 推送当前改动触发 CI（在本地工作区执行）
cd ~/lab/workpilot && git add -A && git commit -m "ops: add gitea ci workflow and cloud backup/restore scripts with runbook" && git push

# 2b. 用徽章确认工作流状态（绿色 "passing" 即通过）
curl -s "http://localhost:3000/infinity/workpilot/actions/workflows/ci.yml/badge.svg" \
  | grep -oE "passing|failing|pending|unknown"

# 2c. 浏览器看两个 job 的日志与结论
open "http://localhost:3000/infinity/workpilot/actions"
```

**预期效果**：`2b` 输出 `passing`；`2c` 打开 Actions 页，`ci` 工作流的 `api`（ruff + pytest 非 live）与 `web`（tsc + build）两个 job 均为绿色 ✓。

### 验收 3 · 故意引入一个 ruff 错误 push → CI 红 → 修复后绿（证明门禁有效）

```bash
# 3a. 制造错误：追加未使用 import（触发 ruff F401/E402）
cd ~/lab/workpilot
echo "import os" >> apps/api/app/main.py
git add apps/api/app/main.py && git commit -m "ci: introduce intentional ruff error" && git push

# 3b. 等约 1 分钟查徽章，应为 failing（红）
curl -s "http://localhost:3000/infinity/workpilot/actions/workflows/ci.yml/badge.svg" \
  | grep -oE "passing|failing|pending|unknown"

# 3c. 修复：删掉刚追加的那行，重新 push
sed -i '' '/^import os$/d' apps/api/app/main.py
git add apps/api/app/main.py && git commit -m "ci: fix intentional ruff error" && git push

# 3d. 再等约 1 分钟查徽章，应回到 passing（绿）
curl -s "http://localhost:3000/infinity/workpilot/actions/workflows/ci.yml/badge.svg" \
  | grep -oE "passing|failing|pending|unknown"
```

**预期效果**：`3b` 输出 `failing`（红，`api` job Lint 步报 `F401 os imported but unused` 或 `E402`），`3d` 输出 `passing`（绿），证明门禁有效。

### 验收 4 · 服务器 `~/backups/wp-*.tgz` 存在，内含 `qdrant-*.snapshot`、`workpilot.db`、`minio.tgz`

```bash
# 4a. 列出最新一份备份文件
ssh root@8.148.216.61 'ls -1t ~/backups/wp-*.tgz | head -1'

# 4b. 校验最新一份内容（必须看到三件）
ssh root@8.148.216.61 'tar tzf $(ls -1t ~/backups/wp-*.tgz | head -1)'
```

**预期效果**：`4a` 输出 `/root/backups/wp-20261116-232815.tgz`（时间戳可能更新）；`4b` 输出三行，分别包含 `qdrant-kb_default.snapshot`、`workpilot.db`、`minio.tgz`。

### 验收 5 · Mac `~/lab/backups/workpilot-cloud/` 有同一份副本

```bash
# 5a. 从服务器拉回 Mac（异地副本；每周至少手动拉一次）
mkdir -p ~/lab/backups/workpilot-cloud && rsync -az root@8.148.216.61:backups/ ~/lab/backups/workpilot-cloud/

# 5b. Mac 端列出最新一份并校验内容（与服务器同一时间戳、同样三件）
ls -1t ~/lab/backups/workpilot-cloud/wp-*.tgz | head -1
tar tzf $(ls -1t ~/lab/backups/workpilot-cloud/wp-*.tgz | head -1)
```

**预期效果**：`5b` 第一行输出与 `4a` 同名（同一时间戳）的 `.tgz`；`tar tzf` 同样输出 `qdrant-kb_default.snapshot`、`workpilot.db`、`minio.tgz` 三行。

### 验收 6 · 恢复演练：清空卷后问答失败 → 恢复后同一问题返回带引用答案；RTO 写入 runbook

**6a. 执行恢复演练（脚本内含「输入 yes」确认，仅对 Demo 环境执行）：**

```bash
ssh root@8.148.216.61 'echo yes | /home/deploy/workpilot/deploy/scripts/restore.sh $(ls -1t ~/backups/wp-*.tgz | head -1)'
```

**预期效果**：脚本末尾输出 `RTO: XXs（约 1 分钟）`。本次实测 **RTO = 22 秒**。

**6b. 恢复后验证带引用答案（直接进 api 容器，绕过已轮换的基本认证）：**

```bash
# 6b-1. 健康检查（返回 {"status":"ok",...}）
ssh root@8.148.216.61 'docker exec workpilot-api-1 python3 -c "import urllib.request,json; print(json.load(urllib.request.urlopen(\"http://localhost:8000/health\")))"'

# 6b-2. 同一样例问题问 RAG（answer 有正文、citations 非空）
ssh root@8.148.216.61 'docker exec workpilot-api-1 python3 -c "import urllib.request,json; d=json.dumps({\"question\":\"什么是 Vite？\"}).encode(); r=urllib.request.Request(\"http://localhost:8000/v1/kb/ask\", data=d, headers={\"Content-Type\":\"application/json\"}); o=json.load(urllib.request.urlopen(r)); print(\"ANSWER:\", o.get(\"answer\",\"\")[:300]); print(\"CITES:\", len(o.get(\"citations\",[])))"'

# 6b-3. 知识库文档列表与备份前一致（应为 5 篇）
ssh root@8.148.216.61 'docker exec workpilot-api-1 python3 -c "import urllib.request,json; o=json.load(urllib.request.urlopen(\"http://localhost:8000/v1/kb/docs\")); docs=o if isinstance(o,list) else o.get(\"docs\",o); print(len(docs) if isinstance(docs,list) else o)"'
```

**预期效果**：`6b-1` 返回 `{"status":"ok",...}`；`6b-2` 打印 `ANSWER:`（正文带 `[1][3]` 引用）与 `CITES: 4`；`6b-3` 输出 `5`。

**6c. RTO 已写入 runbook：**

```bash
grep -n "RTO" ~/lab/workpilot/docs/runbook.md
```

**预期效果**：输出包含 `RTO 1 分钟（实测 22 秒，2026-11-16...）`。

### 验收 7 · 服务器 `crontab -l` 含每日备份；Week 7 复盘已填；已 commit + push

```bash
# 7a. 校验 cron 已写入（应看到 30 3 * * * 那一行）
ssh root@8.148.216.61 'crontab -l'

# 7b. 校验 Week 7 复盘已填（应看到恢复演练 / runner / crontab 相关记录）
grep -n "恢复\|runner\|crontab\|RTO" /Users/infinity/Documents/a_future/plan/plan_ai/phase_01/week_07/README.md | head -20

# 7c. 提交并推送（等你验收通过后执行；按你的要求，本环节未代提交）
cd ~/lab/workpilot && git add -A && git commit -m "ops: add cloud backup/restore scripts and runbook with restore drill result" && git push
```

**预期效果**：`7a` 输出包含 `30 3 * * * /home/deploy/workpilot/deploy/scripts/backup.sh >> /root/backups/backup.log 2>&1`；`7b` 有匹配行；`7c` 推送成功后验收 2 / 3 可随之完成。

---

## 四、改动文件清单（均未提交，待你 commit + push）

**`~/lab/workpilot`：**

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
| `docs/runbook.md` | 新增「备份 / 恢复 / CI」三节 + RTO 回填 + CI label 统一为 `node:20-bookworm` |
| `.gitea/workflows/.gitkeep`、`deploy/scripts/.gitkeep` | 删除（已有真实文件） |

**`/Users/infinity/Documents/a_future`：**

| 文件 | 变更 |
|------|------|
| `plan/plan_ai/phase_01/week_07/README.md` | 第 11 节周复盘已填（恢复演练 RTO 22s、runner 在线、crontab 已装、CI 待 push） |

---

## 五、遗留与说明

1. **CI 跑绿 + ruff 红→绿**（验收 2 / 3）：唯一未完成项，因你要求「不用帮我提交代码」。`ci.yml`、`backup.sh`、`restore.sh`、runbook 等改动已在本地工作区就绪，`git push` 后 Gitea Actions 自动跑 `ci`，两个 job 应绿；门禁验证按验收 3 的命令做一次即可。
2. **云端基本认证**：密码已轮换（`.env` 注释的 `ChangeMe_2026_Demo` 已失效）。本次用「直接进 api 容器」绕过；若后续需从公网调云端 API，需先更新基本认证口令。
3. **runner label 镜像**：已选 `node:20-bookworm`（完整版，自带 git/curl/node），本仓库 runbook 已统一为前者（PLAN 原文 `gitea/runner-images:ubuntu-latest` 仅作参考）。
4. **RPO / RTO**：每日备份 → RPO ≤ 24 小时；RTO = 22 秒（本次演练实测，约 1 分钟）。
