# Day 10 · 执行报告（2026-10-07）

> 对应 `PLAN.md`（Week 02 · Task 5：备份恢复 + 痛点分类 + 周复盘）。
> 主产出仓库：`~/lab/projects`（`infra/scripts/`、`infra/backup-drill.md`、`product-lab/pain-pool.md`）。
> **按用户要求：不提交、不 push**（跳过 PLAN §6 Step 8 第 3 步）。所有改动保留为未暂存状态，清单见第七节。

## 一、逐步执行记录

| Step | 内容 | 结果 |
| --- | --- | --- |
| 0 | 前置确认 | 完成。`docker ps` → `gitea minio qdrant` 三项 Up；`smoke` collection `points_count` = 6；`~/lab-backups` 不存在（首次）；磁盘剩余 319 Gi。**发现 2 处与 plan 假设不符**，见第四节。 |
| 1 | `backup.sh` | 完成（相对 plan 原文改了 1 处：`GITEA_DATA` 可覆盖，默认 `~/Documents/ai_assets`）。`bash -n` 通过。 |
| 2 | `restore.sh` | 完成，但**改写了 plan 原文的留底逻辑**（整目录 `mv` → 原地清空留底）。原因见第四节「问题 1」。`bash -n` 通过。 |
| 3 | 首次备份 | 完成。`~/lab-backups/20261007-0732/`，428 K，含 `gitea.tar.gz` / `minio.tar.gz` / `qdrant.tar.gz` / `SHA256SUMS`；`shasum -a 256 -c` → **3/3 OK**。备份停机 **1 秒**。 |
| 4 | 删除 → 恢复 → 验证 | 完成。删除 `smoke` collection、MinIO 对象 `workpilot-raw/smoke/hello.md`、Gitea 仓库（`test-repo` 不存在 → 改用 `test_repo1`）→ 三项均确认 404 / 为空 → `restore.sh` 恢复 → **3 项健康检查全 OK，用时 3 秒**。功能级验证：`points_count` = 6、`hello.md` 可 `mc cat`、`git clone test_repo1` 成功。 |
| 5 | 演练记录 | 完成。`~/lab/projects/infra/backup-drill.md`（含 3 个问题的根因与改进）。 |
| 6 | 离线副本（P1） | **未完成**。`/Volumes` 下只有 `Gopeed`、`磁力宅PC` 两个只读 DMG + `Macintosh HD`；`~/Library/Mobile Documents/com~apple~CloudDocs` 不存在（iCloud Drive 未开启）。**本机无可用离线目标**，见第五节。 |
| 7 | 痛点池 v1 | 完成。`product-lab/pain-pool.md`：10 条，问题类型全部填写（AI 9 / 自动化 1），新增**初评分**列（= 频率 × 单次耗时），另附「初评分排序」与「问题类型分布」两张表。合计 **440 分钟/周**。 |
| 8 | 周复盘 + 提交 | 部分完成。Week 02 `README.md` §5 状态、§7 九项验收、§11 周复盘已填写；`PROJECT_CONFIG.md`「当前周」→ **第 3 周**。**提交/推送按用户要求跳过**。 |

## 二、验收对齐（PLAN §3）

- [x] `bash -n` 检查两个脚本无语法错误 → `语法 OK`
- [x] `~/lab-backups/<YYYYmmdd-HHMM>/` 含 3 个 `*.tar.gz` + `SHA256SUMS`；`shasum -a 256 -c SHA256SUMS` 全部 OK → **3/3 OK**
- [x] 删除后确认三项都不存在（collection 404、对象不存在、仓库 404）
- [x] `restore.sh` 结束输出 3 行 `OK`；恢复后 `smoke` `points_count` = 6、`hello.md` 可下载、`test_repo1` 可 clone
- [x] `infra/backup-drill.md` 记录了备份停机时间、恢复耗时、问题（3 条）
- [x] 痛点池 10 条，问题类型全部填写，含「初评分」列
- [x] Week 02 README §7 已勾（9/9）、§11 已填
- [ ] 脚本已 push → **按用户要求未提交**

补充复验（恢复演练之后重新跑一遍，确认存储层未被破坏）：
`cd ~/lab/projects/ai-lab/storage-smoke && uv run smoke.py` → 3.97 s，输出
`[minio] ... sha256 一致：356185b387e2` / `[qdrant] top-1 命中预期` / `ALL OK`。

## 三、产出物清单

### 新增（`~/lab/projects`，未提交）

| 文件 | 说明 |
| --- | --- |
| `infra/scripts/backup.sh` | 冷备份：停容器 → 打包 Gitea/Qdrant/MinIO → 启动 → 保留最近 7 份。`set -euo pipefail` + `trap ... EXIT` + SHA256SUMS |
| `infra/scripts/restore.sh` | 校验 → 停容器 → **原地留底** → 解包 → 启动 → 3 项健康检查，输出耗时 |
| `infra/backup-drill.md` | 演练记录 + 3 个问题根因 + 「下次演练检查清单」 |
| `product-lab/pain-pool.md` | v1：10 条 + 问题类型 + 初评分 + 排序表 + 类型分布表 + Day03 AI 归类对比 |

### 修改

| 文件 | 变更 |
| --- | --- |
| `plan/plan_ai/phase_01/week_02/README.md` | §5 五日状态 → 已完成；§7 九项补齐 PASS/FAIL 与实测证据；§11 周复盘全部填写 |
| `PROJECT_CONFIG.md` | §2「当前周」第 1 周 → **第 3 周** |

### 未改动的既有资产（本周已存在，Day10 只做验证）

`~/lab/workpilot/apps/api`（FastAPI + LLM Gateway）、`~/lab/projects/infra/compose/`、`~/lab/projects/ai-lab/storage-smoke/`、`~/lab/projects/career/`。

## 四、与 PLAN 的偏差与原因

### 问题 1 · `restore.sh` 的留底逻辑必须改写（**重要**）

plan 原文用 `mv "$dst" "$dst.before-restore-$stamp"` 把整个数据目录挪走、再由 `tar` 新建同名目录。
在 **Docker Desktop(macOS)** 上这会失败：容器的 bind mount 认的是目录 **inode**，整目录被替换后容器仍指向旧 inode，于是

- Gitea：`/data/git/repositories/.../test_repo1.git` 看不见 → 仓库 404
- MinIO：`mc cat hello.md` → `Object does not exist`
- Qdrant：正常（它自己扫描目录）

必须 `docker restart` 才恢复。改法：**原地清空留底**，保留 `$dst` 目录本身：

```bash
mkdir -p "${dst}.before-restore-${stamp}"
find "$dst" -mindepth 1 -maxdepth 1 -exec mv {} "${dst}.before-restore-${stamp}"/ \;
```

改后重跑：3 项一次恢复成功，无需额外 restart。已写入 `backup-drill.md`。

> 教训：脚本可以照抄，但「为什么这么写」不能跳过——这是 PLAN §6 Step 1「逐行读懂」要防的正是这类事。

### 问题 2 · Gitea 数据目录与 plan 写的不一致

- plan §2 / §6 写 `~/gitea/data`；**实际运行容器挂载的是 `~/Documents/ai_assets`**（`GITEA_CUSTOM=/data/gitea`）。
- `~/gitea/data` 是 9-29 的残留，只含 `test-repo` / `projects` —— 如果照 plan 备份，**备份的是错目录**，而且恢复演练会因为「删掉的仓库不在被备份的目录里」而给出假阳性通过。
- 改法：两个脚本加 `GITEA_DATA="${GITEA_DATA:-$HOME/Documents/ai_assets}"`，可用环境变量覆盖。
- 同时这也解释了为什么 `test-repo` 不存在（它躺在旧目录里）→ 演练对象改用 `test_repo1`。

### 问题 3 · `/bin/bash` 3.2（macOS 自带）多字节字符紧跟 `$VAR` 解析异常

`echo "...$DEST（..."` 报 `DEST<byte>: unbound variable`（全角括号首字节被并入变量名）。
改法：所有「变量后紧跟全角字符」处改用 `${VAR}` 显式界定。

### 问题 4 · `LLM_PROVIDER=doubao` 使 `:8000/v1/chat` 当前返回 502（**待处理**）

Week 02 §7 第 4、5 条验收要求 `/v1/chat` 返回 DeepSeek 回答、超时返回结构化 504。实测发现：

- `.env` 里 `LLM_PROVIDER=doubao`，而豆包（火山方舟）账号返回 **`403 AccountOverdueError`（欠费）**；
- 于是 `:8000/v1/chat` → `502 {"error":{"code":"llm_upstream_error"}}`；
- DeepSeek key 正常：直连 `https://api.deepseek.com/chat/completions` → `200`，余额 `GET /user/balance` → **¥52.00**。

为**不改动用户的 `.env`**，验收用环境变量覆盖另起临时实例完成：

| 端口 | 覆盖参数 | 结果 |
| --- | --- | --- |
| 8001 | `LLM_PROVIDER=deepseek` | `/health` → `{"status":"ok","env":"dev","version":"0.0.1"}`；`/v1/chat` → `200`，`model=deepseek-flash`、`prompt_tokens=10`、`completion_tokens=24`、`latency_ms=875` |
| 8002 | `LLM_PROVIDER=deepseek LLM_TIMEOUT_S=0.001 LLM_MAX_ATTEMPTS=1` | `504 {"error":{"code":"llm_timeout","message":"上游模型响应超时"}}`；日志 `grep -c 'sk-'` = **0**（不泄露 key） |

两个临时实例已关闭（`lsof` 确认 8001/8002 无监听），用户的 `:8000` 未受影响。

**建议**：把 `.env` 的 `LLM_PROVIDER` 改回 `deepseek`（或给豆包充值）——否则 W3 的 Structured Output 与 SSE 流式会全部卡在 403。

### 问题 5 · 密钥入库检查的假阳性

Week 02 §7 要求 `git -C ~/lab/workpilot log -p | grep -c 'sk-'` 为 0，实测为 **1**，但唯一命中是 `apps/api/tests/test_llm_gateway.py:15` 的**故意假密钥**：

```python
FAKE_KEY = "sk-test-should-never-leak"   # 用于断言错误响应不泄露 key
```

`~/lab/projects` 为 **0**。判定：**无真实密钥入库，本项 PASS**。

## 五、未完成项

| 项 | 状态 | 原因 |
| --- | --- | --- |
| PLAN §6 Step 6 · 离线副本（P1） | ❌ | 本机 `/Volumes` 只有 `Gopeed`、`磁力宅PC`（只读 DMG）与 `Macintosh HD`；iCloud Drive 未开启（`~/Library/Mobile Documents/com~apple~CloudDocs` 不存在）。**无可用离线目标**。 |
| PLAN §6 Step 8 · 提交 / push | ⏭️ 跳过 | 用户明确要求「不用帮我提交代码」。 |
| MinIO root 凭据 / DeepSeek key 存密码管理器 | ❌ | plan §6 Step 3 的「重要」提示，本次未做（建议 Day11 前补）。 |
| PLAN §4 · P2 crontab/launchd 定时备份 | ⏭️ | plan 已注明「W7 再做也可」。 |
| 清理 `.before-restore-*` 留底 | ⏳ | plan 建议保留到明天再删；当前 6 个目录：`~/Documents/ai_assets.before-restore-20261007-0733{02,00}`、`~/lab-data/{minio,qdrant}.before-restore-20261007-0733{02,00}` |

## 六、概念自检（PLAN §7 逐条作答）

1. **为什么不在容器运行时直接 tar 数据目录？** SQLite（Gitea）/ Qdrant 段文件在写入过程中被拷贝，可能拿到撕裂的文件，恢复后损坏。
2. **`trap start_all EXIT` 解决什么问题？** `set -e` 下 tar 中途失败会直接退出，若无 trap 容器就一直停着，服务静默下线。
3. **restore 为什么先改名而不是直接删除当前数据？** 备份本身可能已损坏；留底可回滚。本次演练正是靠留底兜住了问题 1 的两轮返工。
4. **为什么 `.env` 里的密码也要单独保存？** 备份不含 `.env`；MinIO 数据需要原 root 凭据才能访问，凭据丢了等于数据丢了。
5. **恢复后 test-repo 回来了，但备份之后推送的提交会怎样？** 全部丢失——恢复到备份时刻。所以演练前不能有新提交；也和 Day10 的 `test_repo1` 演练一致（备份时刻 = HEAD `cfd62e3`）。
6. **只有本机备份够吗？** 不够（磁盘坏 / 丢了一起没）。至少一份异地或离线副本 = 3-2-1 的简化版。**本次未达成**，见第五节。

## 七、工作区状态（未提交，按用户要求）

`git -C ~/lab/projects status --short`：

```text
?? infra/backup-drill.md
?? infra/scripts/
?? product-lab/pain-pool.md
```

`git -C ~/lab/workpilot status --short`：` M docs/runbook.md`（Day09 遗留，本次未动）。

`git -C ~/Documents/a_future status --short`：` M PROJECT_CONFIG.md`、` M plan/plan_ai/phase_01/week_02/README.md`、`?? plan/plan_ai/phase_01/week_02/day10_20261007/REPORT.md`（本文件），以及若干 Day01–Day05 的历史改动。

**全部未提交、未 push。** Day10 对应的提交命令（供需要时手动执行）：

```bash
cd ~/lab/projects
git add infra/scripts/ infra/backup-drill.md product-lab/pain-pool.md
git commit -m "feat(infra): add backup and restore scripts with drill record"
git push
```

## 八、遗留与下一步（W3 前建议处理）

1. **`.env` 的 `LLM_PROVIDER` 改回 `deepseek`**（或给豆包充值）——W3 的前置阻塞项。
2. MinIO root 凭据 + DeepSeek key 存入 macOS 钥匙串（`backup-drill.md` 已登记为技术债）。
3. 给离线副本找落点（U 盘 / 外置盘 / 开启 iCloud Drive），或明确接受「仅本机备份」并写进 `backup-drill.md` 的风险栏。
4. 24h 内清理 6 个 `.before-restore-*` 留底目录（约 9 MB，回收空间）。
5. 把「Docker Desktop bind mount 认 inode」这条教训固化进 `backup-drill.md` 的「下次演练检查清单」（已完成）。
