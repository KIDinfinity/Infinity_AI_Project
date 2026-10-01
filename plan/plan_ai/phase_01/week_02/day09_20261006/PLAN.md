# Day 09 · 2026-10-06 · Week 02 Task 4：MinIO + Qdrant + Ollama bge-m3

## 0. 今天只做一件事

用一个 compose 文件跑起 MinIO（对象存储）+ Qdrant（向量库），本地 Ollama 跑 bge-m3 出 1024 维向量，并用一个冒烟脚本证明：文件进出 MinIO 校验和一致、6 句话入 Qdrant 后语义查询命中正确。

不碰：RAG 分块 / 入库流水线（W4）、WorkPilot 代码里的 `rag/` 模块、MinIO 权限策略 / TLS、Qdrant 参数调优、hybrid 检索（W5）。

## 1. 资产锚点

- 构建模块：M0.4 对象存储 + 向量库（同时验证 M2.3 Embedding 的前提：bge-m3 1024 维）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5、§7）
- 版本里程碑：为 v0.2（W4 RAG MVP）做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`docker compose ps` 两个服务 healthy；`smoke.py` 输出 sha256 一致 + 查询「LLM 接口超时了怎么办？」top-1 命中「网关会指数退避重试」；可测量：bge-m3 单句向量维度 = 1024、top-1 相似度分数 = \_\_\_\_。
- 今日 AI 实际应用：学 Embedding + 余弦相似度 + 向量检索 → W4 Day16 直接复用 smoke.py 的「embed → upsert → query_points」三步写进 `apps/api/app/rag/{embedding,store}.py`。

## 2. 起点（前置确认）

- 已有：Docker、Gitea；`~/lab/projects/{ai-lab,infra}`；`workpilot/.env` 中有 `QDRANT_URL`、`MINIO_*`、`EMBEDDING_*` 键（Day04 `.env.example`）。
- 需确认：

```bash
lsof -iTCP -sTCP:LISTEN -P | grep -E ':(9000|9001|6333|6334|11434) ' || echo "端口均空闲"
df -h ~ | tail -1                          # 预留 ≥ 5GB（bge-m3 约 1.2GB + 镜像）
cd ~/lab/projects && git pull
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `docker compose -f ~/lab/projects/infra/compose/docker-compose.yml ps` 显示 minio、qdrant 均为 running
- [ ] `http://localhost:9001` 能登录 MinIO 控制台，存在 bucket `workpilot-raw`、`backups`
- [ ] `http://localhost:6333/dashboard` 可打开
- [ ] curl Ollama `/v1/embeddings` 返回向量长度 1024
- [ ] `smoke.py` 输出 `[minio] ... sha256 一致`、`[qdrant] top-1 命中预期`、`ALL OK`
- [ ] `infra/compose/.env` 未被提交（`git -C ~/lab/projects check-ignore infra/compose/.env` 有输出）
- [ ] 能口述三类资产各存哪、数据目录在哪、哪类可重建

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                          |
| ----------- | ------ | ------------------------------------------------------------- |
| 0–10 min    | P0     | 安装 Ollama 并**先**开始拉 bge-m3（后台下载，边下边做下一步） |
| 10–35 min   | P0     | 数据目录 + `.env` + compose 起服务 + 控制台建 bucket          |
| 35–45 min   | P0     | curl 验证 embeddings                                          |
| 45–85 min   | P0     | 写并跑通 `smoke.py`                                           |
| 85–100 min  | P0     | 三类资产说明写进 README + 同步 `workpilot/.env`               |
| 100–110 min | P0     | 提交                                                          |
| 110–120 min | P1     | Qdrant dashboard 里查看 `smoke` collection 的点和 payload     |
| —           | P2     | 记录镜像 digest 到 README，为 W7 固定版本做准备               |

时间不足时最低保留：Qdrant + bge-m3 + smoke.py 的 `qdrant_semantic()` 部分；MinIO 顺延到 Day10 前 20 分钟。

## 5. 今日学习（只学完成任务必须的）

- **Embedding**：把文本映射为定长向量（bge-m3 = 1024 维），语义相近 → 向量方向相近；中英文混合效果好。
- **余弦相似度**：比较向量夹角，与长度无关；Qdrant collection 创建时固定 `size` 与 `distance`，之后不能改，维度不匹配会直接报错。
- **Qdrant 基本概念**：collection（≈表）→ point（id + vector + payload）；payload 存原文 / 元数据，W19 用它做 workspace 隔离过滤。
- **S3 / MinIO**：bucket + object key（`smoke/hello.md` 中的 `/` 只是名字的一部分）；API 端口 9000，控制台 9001。
- **Ollama OpenAI 兼容端点**：`http://localhost:11434/v1/embeddings`，同一段 OpenAI SDK 代码，生产换 SiliconFlow 只改 base_url / key / model 名。
- 资料：https://qdrant.tech/documentation/ 、https://min.io/docs/ 、https://ollama.com/ 、https://docs.docker.com/compose/ 、https://docs.astral.sh/uv/guides/scripts/

## 6. 执行步骤

### Step 1 · Ollama + bge-m3（P0，先开始下载）

```bash
brew install ollama
brew services start ollama                  # 开机自启；或前台运行：ollama serve
ollama pull bge-m3                          # 约 1.2GB，慢的话见第 10 节代理处理
ollama list                                 # 期望看到 bge-m3
```

### Step 2 · compose 起 MinIO + Qdrant（P0）

目录与职责：

```text
~/lab/projects/infra/
├── README.md
└── compose/
    ├── docker-compose.yml   # 个人实验室共享的有状态服务（提交）
    └── .env                 # MinIO root 凭据（不提交）
~/lab-data/                  # 有状态服务的数据目录（不在任何 Git 仓库里，Day10 备份它）
├── minio/
└── qdrant/
```

```bash
mkdir -p ~/lab-data/{minio,qdrant} ~/lab/projects/infra/compose
cd ~/lab/projects
printf '.env\n.DS_Store\n__pycache__/\n.venv/\n' >> .gitignore
printf 'MINIO_ROOT_USER=labadmin\nMINIO_ROOT_PASSWORD=%s\n' "$(openssl rand -hex 16)" > infra/compose/.env
git check-ignore -v infra/compose/.env      # 期望命中 .gitignore:1:.env
```

`infra/compose/docker-compose.yml`：

```yaml
name: lab-infra # 固定项目名，Day10 备份脚本按它启停
services:
  minio:
    image: minio/minio:latest
    container_name: minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:?set in compose/.env}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:?set in compose/.env}
    ports:
      - "9000:9000" # S3 API（代码连这个）
      - "9001:9001" # Web 控制台（浏览器用）
    volumes:
      - ${HOME}/lab-data/minio:/data
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333" # REST + dashboard
      - "6334:6334" # gRPC
    volumes:
      - ${HOME}/lab-data/qdrant:/qdrant/storage
    restart: unless-stopped
```

```bash
cd ~/lab/projects/infra/compose
docker compose up -d                        # compose 自动读取同目录 .env
docker compose ps                           # 两个服务 running
curl -s --noproxy '*' localhost:6333/healthz          # healthz check passed
curl -s --noproxy '*' -o /dev/null -w '%{http_code}\n' localhost:9000/minio/health/live   # 200
```

建 bucket：浏览器打开 `http://localhost:9001`，用 `.env` 里的用户名 / 密码登录 → 创建 `workpilot-raw`、`backups`。若控制台没有创建按钮，用容器内自带的 `mc`：

```bash
set -a; source ~/lab/projects/infra/compose/.env; set +a
docker exec minio mc alias set local http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
docker exec minio mc mb -p local/workpilot-raw local/backups
```

（`smoke.py` 也会在 bucket 不存在时自动创建，作为第三道保险。）

### Step 3 · 验证 embeddings 端点（P0）

```bash
curl -s --noproxy '*' http://localhost:11434/v1/embeddings -H 'Content-Type: application/json' \
  -d '{"model":"bge-m3","input":["你好，WorkPilot"]}' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d["data"][0]["embedding"]))'
# 期望：1024
```

### Step 4 · 冒烟脚本（P0，核心逻辑自己读懂）

`~/lab/projects/ai-lab/storage-smoke/smoke.py`：

```python
"""存储冒烟：MinIO 往返 sha256 一致 + bge-m3 向量入 Qdrant 并语义查询。"""
import hashlib
import os
import pathlib
import tempfile

import boto3
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

MINIO = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
QDRANT = os.getenv("QDRANT_URL", "http://localhost:6333")
EMB_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434/v1")
BUCKET, COLLECTION, DIM = "workpilot-raw", "smoke", 1024


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def minio_roundtrip() -> None:
    s3 = boto3.client("s3", endpoint_url=MINIO, region_name="us-east-1",
                      aws_access_key_id=os.environ["MINIO_ROOT_USER"],
                      aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"])
    existing = {b["Name"] for b in s3.list_buckets()["Buckets"]}
    for b in (BUCKET, "backups"):
        if b not in existing:
            s3.create_bucket(Bucket=b)
    src = pathlib.Path(tempfile.mkdtemp()) / "hello.md"
    src.write_text("# smoke\nWorkPilot 的原始文档存放在 MinIO。\n", encoding="utf-8")
    before = sha256(src)
    s3.upload_file(str(src), BUCKET, "smoke/hello.md")
    src.unlink()                                     # 删本地，证明下面拿到的来自 MinIO
    s3.download_file(BUCKET, "smoke/hello.md", str(src))
    assert sha256(src) == before, "sha256 不一致"
    print(f"[minio] 上传→删本地→下载 sha256 一致：{before[:12]}")


def qdrant_semantic() -> None:
    texts = [
        "如何在本地启动 FastAPI 开发服务器",
        "Docker volume 让容器删除后数据仍然保留",
        "Gitea 仓库需要先在 Web 界面创建再 clone",
        "DeepSeek API 超时时网关会指数退避重试",
        "React 组件文件名使用 PascalCase",
        "MinIO 是兼容 S3 协议的对象存储",
    ]
    emb = OpenAI(base_url=EMB_URL, api_key="ollama")
    vecs = [d.embedding for d in emb.embeddings.create(model="bge-m3", input=texts).data]
    assert len(vecs[0]) == DIM, f"维度 {len(vecs[0])} != {DIM}"
    qc = QdrantClient(url=QDRANT)
    if qc.collection_exists(COLLECTION):
        qc.delete_collection(COLLECTION)
    qc.create_collection(COLLECTION, vectors_config=VectorParams(size=DIM, distance=Distance.COSINE))
    points = [PointStruct(id=i, vector=v, payload={"text": t})
              for i, (t, v) in enumerate(zip(texts, vecs, strict=True))]
    qc.upsert(COLLECTION, points=points)
    query = "LLM 接口超时了怎么办？"
    qv = emb.embeddings.create(model="bge-m3", input=[query]).data[0].embedding
    hits = qc.query_points(COLLECTION, query=qv, limit=3).points
    print(f"[qdrant] 查询：{query}")
    for h in hits:
        print(f"  {h.score:.3f}  {h.payload['text']}")
    assert hits[0].payload["text"] == texts[3], "top-1 未命中预期句子"
    print("[qdrant] top-1 命中预期")


if __name__ == "__main__":
    minio_roundtrip()
    qdrant_semantic()
    print("ALL OK")
```

运行（`--with` 让 uv 临时装依赖，不污染任何项目）：

```bash
cd ~/lab/projects/ai-lab/storage-smoke
export NO_PROXY=localhost,127.0.0.1
set -a; source ~/lab/projects/infra/compose/.env; set +a
uv run --with qdrant-client --with openai --with boto3 smoke.py
```

期望输出形如：`[minio] ... 一致`、3 行「分数 + 句子」且第一行是 DeepSeek 那句、`ALL OK`。**跑完不要删** `smoke` collection 和 `smoke/hello.md` 对象——Day10 恢复演练要删它们再恢复。

### Step 5 · 三类资产说明 + 同步 workpilot 配置（P0）

在 `infra/README.md` 追加：

| 资产                         | 存哪   | 宿主机数据目录      | 可否重建                     | 备份优先级 |
| ---------------------------- | ------ | ------------------- | ---------------------------- | ---------- |
| 代码 / 文档 / 规范           | Gitea  | `~/gitea/data`      | 否                           | 最高       |
| 原始文件（文档原文、备份包） | MinIO  | `~/lab-data/minio`  | 否（原文丢了就没了）         | 高         |
| 向量 + payload               | Qdrant | `~/lab-data/qdrant` | 是（可由原文重新 embedding） | 中         |

把 `infra/compose/.env` 的用户名 / 密码填入 `~/lab/workpilot/.env` 的 `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`（仅 dev；在 `workpilot/docs/runbook.md` 记一条技术债：W7 生产环境改用独立 access key）。

### Step 6 · 提交

```bash
cd ~/lab/projects
printf '# storage-smoke\n\nMinIO + Qdrant + bge-m3 冒烟。运行方式见 smoke.py 与 Day09 PLAN。\n' > ai-lab/storage-smoke/README.md
git status --short                          # 不应出现 infra/compose/.env
git add .gitignore infra/ ai-lab/storage-smoke/
git commit -m "feat(infra): add MinIO and Qdrant compose with storage smoke test"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. collection 已按 768 维创建，用 1024 维向量写入会怎样？（答：报维度不匹配错误；必须新建 collection，所以换 embedding 模型 = 全量重建索引）
2. 为什么开发用 Ollama、生产用 SiliconFlow，但都必须是 bge-m3？（答：不同模型的向量空间不兼容，同一 collection 必须由同一模型生成）
3. 向量丢了和原文丢了，哪个更严重？（答：原文；向量可从原文重新生成，原文不可再生）
4. MinIO 9000 与 9001 的区别？（答：9000 是 S3 API 给程序用，9001 是 Web 控制台给人用）
5. 余弦相似度 0.8 一定代表「答案正确」吗？（答：不一定，只代表语义相近；W5 用 hit@k 等评测而不是看分数）
6. 为什么 smoke.py 要先删本地文件再下载？（答：排除「读到的是本地残留文件」的假阳性）

## 8. 对 DA-01 的贡献

WorkPilot 的知识层（M2）所需的三个外部依赖今天全部可用并有可复跑的冒烟证据：W4 Day15 原文进 `workpilot-raw`，Day16 用同一段 embed → upsert 代码入库，Day17 用 `query_points` 检索。`backups` bucket 为 W7 云端备份预留。

## 9. 求职映射（D 线）

- 岗位能力：Embedding、Vector DB（Qdrant）、对象存储（S3 API）、Docker Compose
- 对应岗位：AI 应用工程师（RAG 方向）、AI Platform Engineer
- 简历 bullet 草稿：以 Docker Compose 搭建 MinIO + Qdrant + Ollama(bge-m3, 1024 维) 本地 AI 数据底座，dev / prod 使用同一 embedding 模型保证向量空间一致，冒烟脚本 \_\_ 秒完成存取与语义检索验证。
- 面试可能问：
  - 「为什么选 Qdrant 而不是 pgvector / Milvus？」→ 要点：单容器部署轻、原生 payload 过滤与 hybrid、JD 常见；数据量 < 百万时 pgvector 也可，Milvus 运维重；决策写 ADR（W8）。
  - 「换 embedding 模型要做什么？」→ 要点：新 collection、全量重算、评测对比 hit@k 后切换别名，旧 collection 保留回滚。

## 10. 卡住时的处理

| 现象                                                  | 处理                                                                                                                           |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `ollama pull` 很慢或失败                              | 让 Ollama 服务走代理：`brew services stop ollama` 后前台运行 `HTTPS_PROXY=http://127.0.0.1:7890 ollama serve`，另开终端再 pull |
| curl / Python 连 localhost 返回 502 或卡住            | 代理拦截了本地请求：`export NO_PROXY=localhost,127.0.0.1`，curl 加 `--noproxy '*'`                                             |
| `required variable MINIO_ROOT_USER is missing`        | 不在 `infra/compose/` 目录执行，或 `.env` 不存在 / 键名拼错                                                                    |
| MinIO 容器反复重启，日志提示密码长度                  | `MINIO_ROOT_PASSWORD` 至少 8 位；改 `.env` 后 `docker compose up -d`                                                           |
| 拉 `minio/minio` 镜像失败或控制台功能缺失             | 先确认 Docker 代理；控制台缺按钮就用 Step 2 的 `docker exec minio mc ...` 或 smoke.py 自动建桶                                 |
| `UserWarning: Qdrant client version ... incompatible` | 客户端与服务端小版本差异的提示，冒烟可忽略；W4 在项目里固定版本                                                                |

## 11. 产出记录（执行时填写）

- 镜像版本（`docker image ls minio/minio qdrant/qdrant`）：\_\_\_\_
- bge-m3 向量维度：\_**\_　单次 6 句 embedding 耗时：\_\_**
- smoke 查询 top-3 分数：\_\_\_\_
- 三类资产口述是否顺畅：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE → 明天进入 Day10 Task 5（备份恢复 + 痛点分类 + 周复盘）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
