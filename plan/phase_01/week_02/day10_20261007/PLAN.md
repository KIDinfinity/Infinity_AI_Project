# Day 10 · 2026-10-07 · Week 02 Task 5：备份恢复 + 痛点分类 + 周复盘

## 0. 今天只做一件事

写出 `backup.sh` / `restore.sh`，并完成一次真实恢复演练：删掉 Qdrant `smoke` collection、MinIO 一个对象、Gitea `test-repo` → 用备份恢复 → 三项全部回来，记录耗时。然后把痛点池补到 ≥ 10 条并做周复盘。

不碰：云端备份 / 定时任务（W7）、Qdrant snapshot API 与 `gitea dump` 等热备方案、增量备份、加密。

## 1. 资产锚点

- 构建模块：M0.5 备份 / 恢复；M10 痛点分类（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备（W8 验收「干净环境 30 分钟内恢复」，蓝图 §11 运维指标）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：一条命令产出带校验和的备份，一条命令恢复并自动健康检查；可测量：备份停机 \_**\_ 秒、恢复耗时 \_\_** 秒（目标 < 30 分钟）；痛点池 ≥ 10 条带初评分，Day13 可直接排序。
- 今日 AI 实际应用：Copilot 起草 shell 脚本样板 → 自己审 `set -euo pipefail`、`trap`、路径变量、改名留底逻辑（备份脚本写错会毁数据，必须逐行读懂）；痛点池初评分为 Day13 的 AI 场景选型提供量化输入。

## 2. 起点（前置确认）

- 已有：Gitea（`~/gitea/data`）、`lab-infra` compose（MinIO + Qdrant，`~/lab-data/`）；Day09 留下的 `smoke` collection 与 `workpilot-raw/smoke/hello.md`；`test-repo`（Day02）。
- 需确认：

```bash
docker ps --format '{{.Names}}' | sort                        # gitea minio qdrant
curl -s --noproxy '*' localhost:6333/collections/smoke | grep -o '"points_count":[0-9]*'   # 6
du -sh ~/gitea/data ~/lab-data/qdrant ~/lab-data/minio        # 估算备份大小
df -h ~ | tail -1                                             # 剩余空间 > 上面总和 × 3
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `bash -n` 检查两个脚本无语法错误
- [ ] `~/lab-backups/<YYYYmmdd-HHMM>/` 含 `gitea.tar.gz`、`qdrant.tar.gz`、`minio.tar.gz`、`SHA256SUMS`；`shasum -a 256 -c SHA256SUMS` 全部 OK
- [ ] 删除后确认三项都不存在（collection 404、对象不存在、test-repo 页面 404）
- [ ] `restore.sh` 结束输出 3 行 `OK`；恢复后 `smoke` points_count = 6、`hello.md` 可下载、`test-repo` 可 `git fetch`
- [ ] `infra/backup-drill.md` 记录了备份停机时间、恢复耗时、问题
- [ ] 痛点池 ≥ 10 条，问题类型全部填写，含「初评分」列
- [ ] Week 02 README §7 已勾、§11 已填；脚本已 push

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                               |
| ----------- | ------ | -------------------------------------------------- |
| 0–10 min    | P0     | 前置确认                                           |
| 10–40 min   | P0     | 写 `backup.sh` / `restore.sh` + `bash -n`          |
| 40–50 min   | P0     | 首次备份 + 校验                                    |
| 50–80 min   | P0     | 删除三项 → 恢复 → 验证（计时）                     |
| 80–88 min   | P0     | 写 `backup-drill.md`，提交                         |
| 88–103 min  | P0     | 痛点池补到 ≥ 10 条 + 初评分列                      |
| 103–115 min | P0     | Week 02 验收 + 周复盘                              |
| 115–120 min | P1     | 复制一份备份到离线位置（外置盘 / iCloud）          |
| —           | P2     | 用 `crontab` / launchd 每周自动备份（W7 再做也可） |

时间不足时最低保留：`backup.sh` 产出备份 + 只演练 Qdrant 一项恢复 + 痛点池 ≥ 10 条；完整三项演练在 W7 Day29 前补。

## 5. 今日学习（只学完成任务必须的）

- **冷备份**：先停服务再拷数据，保证 SQLite（Gitea）/ Qdrant 段文件 / MinIO 元数据一致；代价是几十秒停机，个人实验室可接受。
- **`set -euo pipefail`**：任一命令失败即退出、未定义变量报错、管道中任一环节失败即失败——备份脚本「静默失败」最危险。
- **`trap ... EXIT`**：无论脚本成功还是中途失败，退出时都执行清理（这里是把容器重新拉起）。
- **校验和**：`SHA256SUMS` 证明备份文件没损坏；恢复前先校验。
- **RTO**：从故障到恢复服务所需时间；没有演练过的备份不算备份。
- 资料：https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes 、https://docs.gitea.com/administration/backup-and-restore 、https://qdrant.tech/documentation/concepts/snapshots/ 、https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin

## 6. 执行步骤

### Step 1 · backup.sh（P0，逐行读懂）

`~/lab/projects/infra/scripts/backup.sh`：

```bash
#!/usr/bin/env bash
# 冷备份：停容器 → 打包 Gitea / Qdrant / MinIO 数据 → 启动容器 → 保留最近 KEEP 份
set -euo pipefail

BACKUP_ROOT="${BACKUP_ROOT:-$HOME/lab-backups}"
KEEP="${KEEP:-7}"
COMPOSE_FILE="$(cd "$(dirname "$0")/../compose" && pwd)/docker-compose.yml"
TARGETS=("gitea:$HOME/gitea/data" "qdrant:$HOME/lab-data/qdrant" "minio:$HOME/lab-data/minio")

DEST="$BACKUP_ROOT/$(date +%Y%m%d-%H%M)"
if [[ -e "$DEST" ]]; then echo "目标已存在：$DEST（同一分钟重复执行？）"; exit 1; fi
mkdir -p "$DEST"

start_all() {
  docker start gitea >/dev/null
  docker compose -f "$COMPOSE_FILE" start >/dev/null
  echo "[backup] 容器已启动，停机 $(( $(date +%s) - stop_ts )) 秒"
}

echo "[backup] 停止容器"
stop_ts=$(date +%s)
trap start_all EXIT              # 先注册：之后无论成功失败，退出时都把容器拉起来
docker stop gitea >/dev/null
docker compose -f "$COMPOSE_FILE" stop >/dev/null

for t in "${TARGETS[@]}"; do
  name="${t%%:*}"; src="${t#*:}"
  echo "[backup] 打包 $name ← $src"
  tar -czf "$DEST/$name.tar.gz" -C "$(dirname "$src")" "$(basename "$src")"
done
(cd "$DEST" && shasum -a 256 ./*.tar.gz > SHA256SUMS)

# 保留最近 KEEP 份（按目录名时间倒序，第 KEEP+1 份起删除）
ls -1d "$BACKUP_ROOT"/[0-9]*-[0-9]* | sort -r | tail -n +"$((KEEP + 1))" | while read -r old; do
  echo "[backup] 清理旧备份 $old"; rm -rf "$old"
done
echo "[backup] 完成：$DEST（$(du -sh "$DEST" | cut -f1)）"
```

### Step 2 · restore.sh（P0）

`~/lab/projects/infra/scripts/restore.sh`：

```bash
#!/usr/bin/env bash
# 恢复：校验 → 停容器 → 当前数据改名留底 → 解包 → 启动 → 健康检查
set -euo pipefail

SRC="${1:?用法：restore.sh ~/lab-backups/YYYYmmdd-HHMM}"
COMPOSE_FILE="$(cd "$(dirname "$0")/../compose" && pwd)/docker-compose.yml"
TARGETS=("gitea:$HOME/gitea/data" "qdrant:$HOME/lab-data/qdrant" "minio:$HOME/lab-data/minio")

[[ -d "$SRC" ]] || { echo "备份目录不存在：$SRC"; exit 1; }
echo "[restore] 校验 SHA256"
(cd "$SRC" && shasum -a 256 -c SHA256SUMS)
read -r -p "将用 $SRC 覆盖当前数据（旧数据改名保留），输入 yes 继续：" ans
[[ "$ans" == "yes" ]] || { echo "已取消"; exit 1; }

start_ts=$(date +%s); stamp=$(date +%Y%m%d-%H%M%S)
docker stop gitea >/dev/null
docker compose -f "$COMPOSE_FILE" stop >/dev/null
for t in "${TARGETS[@]}"; do
  name="${t%%:*}"; dst="${t#*:}"
  if [[ -e "$dst" ]]; then mv "$dst" "$dst.before-restore-$stamp"; fi
  mkdir -p "$(dirname "$dst")"
  tar -xzf "$SRC/$name.tar.gz" -C "$(dirname "$dst")"
  echo "[restore] $name → $dst（旧数据：$dst.before-restore-$stamp）"
done
docker start gitea >/dev/null
docker compose -f "$COMPOSE_FILE" up -d >/dev/null

wait_ok() {   # wait_ok <名称> <URL>：最多等 60 秒
  for _ in $(seq 1 30); do
    if curl -fsS --noproxy '*' "$2" >/dev/null 2>&1; then echo "[restore] $1 OK"; return 0; fi
    sleep 2
  done
  echo "[restore] $1 健康检查失败：$2"; return 1
}
wait_ok gitea  http://localhost:3000/api/healthz
wait_ok qdrant http://localhost:6333/healthz
wait_ok minio  http://localhost:9000/minio/health/live
echo "[restore] 完成，用时 $(( $(date +%s) - start_ts )) 秒"
```

```bash
cd ~/lab/projects/infra/scripts
chmod +x backup.sh restore.sh
bash -n backup.sh && bash -n restore.sh && echo "语法 OK"
```

### Step 3 · 首次备份（P0）

```bash
~/lab/projects/infra/scripts/backup.sh
ls ~/lab-backups/                                     # 记下目录名，如 20261007-2105
cd ~/lab-backups/<目录名> && shasum -a 256 -c SHA256SUMS   # 3 行 OK
```

**重要**：MinIO 数据需要相同的 root 凭据才能正常启动，而 `infra/compose/.env`、`workpilot/.env` 都不在备份里——现在把 MinIO 用户名 / 密码、DeepSeek key 存进密码管理器（或钥匙串）。

### Step 4 · 删除三项 → 恢复 → 验证（P0，计时）

备份后**不要**再往 Gitea 推新提交（恢复会回到备份时刻）。

```bash
# 1) 删除
curl -s --noproxy '*' -X DELETE localhost:6333/collections/smoke
set -a; source ~/lab/projects/infra/compose/.env; set +a
docker exec minio mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null
docker exec minio mc rm local/workpilot-raw/smoke/hello.md
# Gitea：打开 test-repo → 设置 → 危险操作区 → 删除此仓库

# 2) 确认已删除
curl -s --noproxy '*' -o /dev/null -w '%{http_code}\n' localhost:6333/collections/smoke    # 404
docker exec minio mc ls local/workpilot-raw/smoke/                                          # 空
curl -s --noproxy '*' -o /dev/null -w '%{http_code}\n' localhost:3000/<user>/test-repo      # 404

# 3) 恢复（开始计时）
~/lab/projects/infra/scripts/restore.sh ~/lab-backups/<目录名>

# 4) 验证
curl -s --noproxy '*' localhost:6333/collections/smoke | grep -o '"points_count":[0-9]*'  # 6
docker exec minio mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null
docker exec minio mc cat local/workpilot-raw/smoke/hello.md                                # 原文内容
git -C ~/lab/test-repo fetch && echo "test-repo OK"
```

全部验证通过后，确认无误再手动删除 `~/gitea/data.before-restore-*`、`~/lab-data/*.before-restore-*`（建议保留到明天）。

### Step 5 · 演练记录（P0）

`~/lab/projects/infra/backup-drill.md`：

```markdown
# 备份恢复演练记录

| 日期       | 备份目录          | 备份大小 | 备份停机(s) | 恢复耗时(s) | 删除项                                  | 恢复结果 | 问题与改进 |
| ---------- | ----------------- | -------- | ----------- | ----------- | --------------------------------------- | -------- | ---------- |
| 2026-10-07 | 20261007-\_\_\_\_ | \_\_\_\_ | \_\_\_\_    | \_\_\_\_    | smoke collection / hello.md / test-repo | 3/3      | \_\_\_\_   |
```

### Step 6 · 离线副本（P1）

```bash
cp -R ~/lab-backups/<目录名> /Volumes/<外置盘>/lab-backups/
# 或 iCloud：cp -R ~/lab-backups/<目录名> ~/Library/Mobile\ Documents/com~apple~CloudDocs/lab-backups/
```

本机磁盘坏了，`~/lab-backups` 会一起丢——至少保留一份不在本机的副本。备份里只有个人项目与公开资料（无公司数据），可放个人云盘。

### Step 7 · 痛点池 v1（P0）

1. 按 Day03 的 8 类提示，补到 ≥ 10 条（仍然只记亲历）。
2. 把所有「问题类型」为空或「待定」的条目定下来。
3. 在表格最右侧加一列 `初评分`：先填 `频率 × 单次耗时`（= 每周损失分钟）；Day13 用完整评分模型（价值 / 可复现 / 合规 / 与 WorkPilot 模块重合度）覆盖。

### Step 8 · 周复盘 + 提交（P0）

1. 打开 `plan/phase_01/week_02/README.md`，逐项勾 §7，填 §11。
2. `PROJECT_CONFIG.md`「当前周」改为第 3 周。
3. 提交：

```bash
cd ~/lab/projects
git add infra/scripts/ infra/backup-drill.md product-lab/pain-pool.md
git commit -m "feat(infra): add backup and restore scripts with drill record"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么不在容器运行时直接 tar 数据目录？（答：SQLite / Qdrant 正在写入时拷贝可能得到不一致的文件，恢复后损坏）
2. `trap start_all EXIT` 解决什么问题？（答：tar 中途失败时脚本因 `set -e` 退出，若无 trap 容器会一直停着）
3. restore 为什么先改名而不是直接删除当前数据？（答：备份本身可能有问题，留底可回滚；确认无误后再删）
4. 为什么 `.env` 里的密码也要单独保存？（答：备份不含 `.env`；MinIO 数据需要原 root 凭据，丢了凭据等于丢了数据访问能力）
5. 恢复后 test-repo 回来了，但备份之后推送的提交会怎样？（答：丢失；所以要定期备份，且演练前不能有新提交）
6. 只有本机备份够吗？（答：不够，磁盘损坏 / 丢失时一起没；至少一份离线或异地副本，即 3-2-1 原则的简化版）

## 8. 对 DA-01 的贡献

WorkPilot 依赖的三类有状态资产（代码、原文、向量）从今天起可在分钟级恢复，且有演练记录作证据；W7 云端部署直接复用同一脚本思路做 `deploy/scripts/backup.sh`，W8 的「干净环境 30 分钟恢复」有了基线。痛点池 v1 让 Day13 的场景选型可以按数据排序。

## 9. 求职映射（D 线）

- 岗位能力：数据备份恢复、Shell 脚本健壮性、RTO 意识、运维文档
- 对应岗位：AI Platform Engineer、AI 全栈工程师（「具备生产环境运维意识」）
- 简历 bullet 草稿：为自托管 AI 研发底座（Gitea / MinIO / Qdrant）编写带校验和与自动健康检查的备份恢复脚本，完成删除-恢复演练，RTO \_\_ 分钟，保留 7 份滚动备份 + 离线副本。
- 面试可能问：
  - 「向量库要不要备份？」→ 要点：可由原文重建，但重建耗时 + 花 embedding 费用；小规模直接备份，大规模用 snapshot；原文与元数据必须备份。
  - 「怎么证明你的备份可用？」→ 要点：校验和 + 定期恢复演练 + 恢复后功能级验证 + 记录 RTO。

## 10. 卡住时的处理

| 现象                                                                        | 处理                                                                                            |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `docker compose ... stop` 报 `required variable MINIO_ROOT_USER is missing` | `compose/.env` 不在 compose 文件同目录；确认 `infra/compose/.env` 存在                          |
| `tar: ... Permission denied`                                                | 某些文件属主异常：`ls -l` 查看，必要时 `sudo tar ...`；不要 `chmod -R 777`                      |
| `shasum -c` 报 FAILED                                                       | 备份文件损坏，删除该目录重新备份；检查磁盘空间                                                  |
| 恢复后 MinIO 无法启动 / 登录失败                                            | `compose/.env` 凭据与备份时不一致；改回原凭据后 `docker compose up -d`                          |
| Gitea 健康检查超时                                                          | `docker logs gitea` 查看；数据目录层级错误（应恢复为 `~/gitea/data`，不是 `~/gitea/data/data`） |
| 恢复后想回到恢复前状态                                                      | 停容器 → 删除新解包目录 → 把 `*.before-restore-<stamp>` 改回原名 → 启动                         |

## 11. 产出记录（执行时填写）

- 备份大小 / 停机秒数：\_\_\_\_
- 恢复耗时：\_**\_ 秒　3 项验证：\_\_** / 3
- 离线副本位置：\_\_\_\_
- 痛点池条数 / 每周损失 Top 3：\_\_\_\_
- 本周 DeepSeek 花费：¥\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 5 DONE，Week 02 结束 → 明天进入 Week 03 Day11（Structured Output + Prompt 版本化）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（备份 + 至少一项恢复 + 痛点池 ≥ 10 条为 Day13 前的硬性前置）。
