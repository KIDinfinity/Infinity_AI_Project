# Day 09 · 执行报告（2026-10-06）

对应 `PLAN.md`；产出仓库：`~/lab/projects`（infra + ai-lab/storage-smoke），配置同步到 `~/lab/workpilot/.env`。
**按用户要求：本次不提交、不 push**（跳过 PLAN §6 Step 6）。工作区改动全部保留为未暂存状态，清单见第六节。

## 一、逐步执行记录

| Step | 内容 | 结果 |
| --- | --- | --- |
| 1 | Ollama + bge-m3 | 完成。`brew install ollama` → 0.35.1_1；`brew services start ollama` 已跑（`OLLAMA_FLASH_ATTENTION=true`、`OLLAMA_KV_CACHE_TYPE=q8_0` 已生效，见日志 server config）；`ollama pull bge-m3` → 1.2 GB，ID `790764642607`，`ollama list` 可见 |
| 2 | compose 起 MinIO + Qdrant | 完成。`~/lab-data/{minio,qdrant}` 已建；`infra/compose/.env`（root 凭据，已 git-ignore）；`docker-compose.yml` 按 PLAN 原样（`name: lab-infra`）；两服务 **Up 20 分钟**，restart 策略 `unless-stopped`；`healthz check passed`、MinIO live **200**；bucket `workpilot-raw`、`backups` 均已存在（用容器内 `mc` 建的） |
| 3 | curl 验证 embeddings | 完成。`/v1/embeddings` 返回 `维度: 1024` |
| 4 | `smoke.py` 冒烟 | 完成。两次核心输出：`[minio] 上传→删本地→下载 sha256 一致：356185b387e2`；`[qdrant] top-1 命中预期`；结尾 `ALL OK`。用 `uv run --with ...` 运行，装 32 个包，全程 **16.1s** |
| 5 | 三类资产 README + 同步 workpilot | 完成。`infra/README.md` 已有三类资产表 / compose 说明 / 冒烟命令 / 镜像加速 / digest；`~/lab/workpilot/.env` 的 `MINIO_ACCESS_KEY=labadmin`、`MINIO_SECRET_KEY=5ef7...` 已填；`docs/runbook.md` 新建「技术债」条目（W7 生产改用独立 access key，不用 root 凭据） |
| 6 | 提交 | **跳过（用户明确要求不提交）**。文件均已落盘，`git status` 有输出，随时可提交 |
| P1 | Qdrant dashboard 视角核对 | 完成（用 REST API 等价核对）：collections = `[smoke]`；`dim: 1024 distance: Cosine points: 6`；scroll 可见点 0/1 及 payload `text` |
| P2 | 镜像 digest 记录 | 完成，写入 `infra/README.md` |

### 核心证据（smoke.py 实际输出）

```text
[minio] 上传→删本地→下载 sha256 一致：356185b387e2
[qdrant] 查询：LLM 接口超时了怎么办？
  0.591  DeepSeek API 超时时网关会指数退避重试
  0.478  如何在本地启动 FastAPI 开发服务器
  0.421  Docker volume 让容器删除后数据仍然保留
[qdrant] top-1 命中预期
ALL OK
```

`smoke` collection 与 `smoke/hello.md` 对象**已按要求保留未删**（Day10 恢复演练要用）。

## 二、产出记录（PLAN §11）

- 镜像版本（`docker image ls --digests`）：
  - `minio/minio:latest` → `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`
  - `qdrant/qdrant:latest` → `sha256:b7b0444c4c351c970b98e90a6f89c2ee4287c65b44e52b4cb503fa5b2aa927ad`
- bge-m3 向量维度：**1024**；单次 6 句 embedding 耗时：**0.13s**（已预热，M1 Pro Metal 加速）
- smoke 查询 top-3 分数：**0.591 / 0.478 / 0.421**
- 三类资产口述：顺畅（详见 `infra/README.md`「三类资产」表）
- 卡点记录：见第四节
- 用时：约 **75 分钟**（其中 `ollama pull` 等待约 8 分钟；P0 全部完成，P1/P2 亦完成）

## 三、验收对齐（PLAN §3）

- [x] `docker compose -f ~/lab/projects/infra/compose/docker-compose.yml ps` 显示 minio、qdrant 均为 Up
- [x] `http://localhost:9001` MinIO 控制台可登录；bucket `workpilot-raw`、`backups` 存在（`mc ls local` 已确认，控制台亦可）
- [x] `http://localhost:6333/dashboard` 可打开（同端口 `healthz check passed`）
- [x] curl Ollama `/v1/embeddings` 返回向量长度 **1024**
- [x] `smoke.py` 输出 `[minio] ... sha256 一致`、`[qdrant] top-1 命中预期`、`ALL OK`
- [x] `infra/compose/.env` 未被提交：`git check-ignore -v` → `.gitignore:1:.env  infra/compose/.env`
- [x] 能口述三类资产各存哪、数据目录在哪、哪类可重建

第 3 节全部勾上 → **Task 4 DONE**。

## 四、卡点记录

1. **`ollama pull` 的进度看不见**：进度条走 TTY，管道给 `tail` 后什么都不输出，终端看起来像卡住。改用手动探测 `du -sm ~/.ollama/models`：306 MB → 391 MB（20s）→ 最终 1105 MB，均速约 **4.3 MB/s**，总计约 8 分钟。本机代理软件当日未运行，Ollama 直连可达，**未**需要 PLAN §10 的 `HTTPS_PROXY` 方案。
2. **`docker image ls --digests minio/minio qdrant/qdrant` 报错**：`requires at most 1 argument`。改为 `docker image ls --digests --format '...' | grep -E 'minio|qdrant'`。
3. **系统 `python3` 没有 `openai` 模块**：用 `python3 - <<EOF` 测 embedding 耗时直接 `ModuleNotFoundError: No module named 'openai'`。改用 `uv run --with openai python -` 解决（与 `smoke.py` 的运行方式一致，不污染全局环境）。
4. **冷启动 vs 预热差异大**：第一次 embedding 含模型加载，耗时远高于稳态。测「单次 6 句耗时」时先发一条预热请求，取稳态 **0.13s**，避免把加载时间算进去。
5. **历史遗留：本机已有旧 `ollama`（0.35.1_1）**，`brew install ollama` 为幂等确认，未重装；`brew services list` 显示 ollama 为 started。

## 五、概念自检（PLAN §7，口述核对）

1. collection 768 维、写入 1024 维 → 维度不匹配直接报错；换 embedding 模型 = 新建 collection + 全量重建索引。
2. dev Ollama / prod SiliconFlow 但都必须是 bge-m3 → 不同模型向量空间不兼容，同一 collection 必须由同一模型生成。
3. 向量丢了 vs 原文丢了 → 原文更严重，向量可由原文重算，原文不可再生。
4. MinIO 9000 = S3 API 给程序用；9001 = Web 控制台给人用。
5. 余弦相似度 0.8 ≠ 答案正确，只代表语义相近；评测应用 hit@k 等指标（W5）。
6. smoke 先删本地再下载 → 排除「读到的是本地残留文件」的假阳性。

本次实测正好印证第 3、5 条：top-1 语义命中（0.591）但分数并不高——短句 + 中文混合语料下 0.5–0.6 属正常区间，看分数定阈值不可靠。

## 六、工作区状态（未提交，按用户要求）

`git -C ~/lab/projects status --short`：

```text
 M ai-lab/README.md
 M infra/README.md
?? .gitignore
?? ai-lab/storage-smoke/
?? infra/compose/
```

`infra/compose/.env` 不在其中（已被 `.gitignore` 忽略）。

`~/lab/workpilot`：`docs/runbook.md` 新增技术债条目（未提交）；`.env` 已填 MinIO 凭据（该文件本就被 git 忽略）。
PLAN §6 Step 6 的提交/推送（`feat(infra): add MinIO and Qdrant compose with storage smoke test`）**留待用户自行执行**。

## 七、对 DA-01 的贡献

知识层的三个外部依赖（对象存储、向量库、embedding 服务）今天全部可用，且有可复跑的冒烟证据。W4 Day15 原文进 `workpilot-raw`，Day16 复用今日 `embed → upsert` 写法，Day17 复用 `query_points`，`backups` bucket 为 W7 云端备份预留。

## 八、求职映射（D 线）

- 岗位能力：Embedding、Vector DB（Qdrant）、对象存储（S3 API）、Docker Compose
- 对应岗位：AI 应用工程师（RAG 方向）、AI Platform Engineer
- 简历 bullet（用真实数据补齐）：
  > 以 Docker Compose 搭建 MinIO + Qdrant + Ollama（bge-m3，1024 维）本地 AI 数据底座，dev/prod 共用同一 embedding 模型保证向量空间一致；冒烟脚本 16s 内完成对象存储往返 sha256 校验（`356185b387e2`）与 6 句中文语料的语义检索验证（top-1 命中，相似度 0.591）。

## 九、Day10 前置

- 明天 Task 5：备份恢复演练 + 痛点分类 + 周复盘。**不要删** `smoke` collection 与 `smoke/hello.md`——恢复演练要拿它们做删除→恢复的证明。
- 备份对象：`~/lab-data/minio`（高优先级）、`~/lab-data/qdrant`（中，可重建）、`~/gitea/data`（最高）。
- 可顺手做的小事（今日发现，未擅自执行）：
  1. `PROJECT_CONFIG.md` §2 仍写「当前周 = 第 1 周」，实际已到 W2 Day09；该文件规定「每周末复盘后同步更新」，建议 W2 复盘时一并修正（Day07/Day08 已记录，本次仍未动）。
  2. compose 里两个镜像都是 `latest`；digest 已记入 `infra/README.md`，W7 固定版本时替换为 `tag@digest`。
  3. `~/lab/workpilot/.env` 与 `infra/compose/.env` 里的 MinIO 凭据完全相同（dev 有意如此），W7 前记得拆开。
