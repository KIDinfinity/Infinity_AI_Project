# Day 01 · 2026-09-28 · Week 01 Task 1：Docker 环境

## 0. 今天只做一件事

Week 01 Task 1：装上 Docker，跑通最小容器，练熟 5 条命令，能口头解释 image / container / volume。

不碰：Git 服务、MinIO、Qdrant、CI/CD（那是 Task 2 和第 2 周）。

## 1. 起点（已确认）

- 本机：macOS，arm64（Apple Silicon）
- `docker` 未安装
- 本机代理可用：`http://127.0.0.1:7890`（直连 GitHub / Docker Hub 会超时，拉镜像需要代理）

## 2. 验收对齐（做完要能勾掉）

- [ ] `docker run / ps / logs / stop / rm` 5 条命令独立完成
- [ ] 口头解释：image 与 container 的区别
- [ ] 口头解释：volume 的作用（为什么容器删了数据还在）
- [ ] 产出：一个可用的 Docker 环境 + 一个最小运行示例

## 3. 时间块（约 90 分钟）

| 时间 | 内容 |
|---|---|
| 0–15 min | 安装运行时（OrbStack 或 Docker Desktop）并启动 |
| 15–25 min | `hello-world` 跑通 + `docker version / info` |
| 25–45 min | `nginx` 跑通 + 5 条命令逐个练 |
| 45–60 min | volume 练习（挂载本地目录，改内容生效） |
| 60–75 min | 概念自检（对着空文档口述，不看教程） |
| 75–90 min | 写产出记录（下方第 8 节）+ 顺手记 3 条痛点 |

时间不足时，最低保留：安装 + hello-world + 5 条命令。

## 4. 执行步骤

### Step 1 · 安装运行时（二选一）

- 首选 OrbStack（轻、启动快、个人免费、资源占用低，够跑 Gitea/MinIO/Qdrant）：
  `brew install --cask orbstack`
- 备选 Docker Desktop：
  `brew install --cask docker`

安装后启动 App，等状态栏图标变为运行中。

验证：

```bash
docker version
docker info
```

`docker version` 应能同时看到 Client 与 Server 两段（只有 Client = 守护进程没起来）。

### Step 2 · 配置代理（拉镜像必需）

编辑 `~/.orbstack/config/docker.json`（Docker Desktop 则是 `~/.docker/daemon.json`）：

```json
{
  "proxies": {
    "http-proxy": "http://host.docker.internal:7890",
    "https-proxy": "http://host.docker.internal:7890",
    "no-proxy": "localhost,127.0.0.1"
  }
}
```

注意：容器内访问宿主机代理要用 `host.docker.internal`，不是 `127.0.0.1`。
同时确认代理 App 已开启「允许局域网 / Allow LAN」，否则虚拟机连不上。

重启运行时后验证：

```bash
docker pull hello-world
```

卡在 `Waiting` 或 `timeout` = 代理没生效，先解决这一步，不要往下走。

### Step 3 · hello-world

```bash
docker run hello-world
```

看到 `Hello from Docker!` 即通过。

### Step 4 · nginx + 5 条命令

```bash
docker run -d -p 8080:80 --name web nginx
docker ps
docker logs web
curl -I http://localhost:8080
docker stop web
docker ps -a
docker rm web
```

对应关系理解：

| 命令 | 作用 |
|---|---|
| `docker run` | 由 image 创建并启动一个 container |
| `docker ps` | 看正在运行的容器（`-a` 看全部，含已停止） |
| `docker logs` | 看容器内进程输出 |
| `docker stop` | 停止容器（不删除） |
| `docker rm` | 删除容器（不删除 image） |

再补两条辅助：

```bash
docker images        # 本机有哪些 image
docker image rm nginx  # 删 image（需先删依赖它的容器）
```

### Step 5 · volume 练习

```bash
mkdir -p ~/docker-lab/site
echo "hello volume" > ~/docker-lab/site/index.html
docker run -d -p 8080:80 --name web -v ~/docker-lab/site:/usr/share/nginx/html:ro nginx
curl http://localhost:8080
echo "changed" > ~/docker-lab/site/index.html
curl http://localhost:8080
docker rm -f web
ls ~/docker-lab/site        # 容器删了，文件还在
```

要点：volume 把数据放在容器生命周期之外，所以容器可删可重建，数据不丢。
这正是后面 Gitea / MinIO 能「可备份、可迁移」的基础。

## 5. 概念自检（不看教程，口述或默写）

1. image 和 container 的关系？（答：image 是只读模板，container 是它的一次运行实例；一个 image 可起多个 container）
2. `stop` 和 `rm` 的区别？容器停了数据一定还在吗？（答：停不等于删；数据在容器可写层或 volume 里，`rm` 后才丢，volume 里的不丢）
3. volume 解决什么问题？（答：数据持久化 + 容器间/重建后复用，不随容器删除消失）
4. `-p 8080:80` 两边分别是什么？（答：左=宿主机端口，右=容器内端口）
5. `-d` 是什么意思？（答：后台运行）

## 6. 对 DA-01 的贡献（今天要能答出来）

DA-01 需要一个「换台机器也能一键起来」的运行环境。今天建立的 Docker 环境是它的载体：
后续 Gitea（Task 2）、MinIO / Qdrant（第 2 周）、第 8 周的「干净环境恢复并运行」验收，全部依赖今天这一步。

## 7. 卡住时的处理

| 现象 | 处理 |
|---|---|
| `docker: command not found` | 运行时没装或没启动；确认 App 已运行，终端重开 |
| `Cannot connect to the Docker daemon` | 守护进程未启动，启动 App 后重试 |
| 端口被占用 | 换 `-p 8081:80` |
| 拉镜像超时 | 回到 Step 2 检查代理 / Allow LAN |
| 超过 60 分钟还没跑通 hello-world | 停止并记录卡点，明天优先解决，不硬耗 |

## 8. 产出记录（执行时填写）

- 使用的运行时：____
- `docker version` 是否 Server 正常：____
- hello-world 结果：____
- nginx 练习 5 条命令是否全部独立完成：____
- volume 练习是否成功（改文件 → curl 生效 → 删容器文件仍在）：____
- 卡点记录：____
- 用时：____ 分钟

## 9. 今日额外（顺手，不占主线）

Task 0 的最低启动：随手记 3 条真实痛点（工作反复遇到的问题 / AI 使用不顺的地方 / 手工重复劳动），一句话一条。
不要求今天凑齐 5 条，先留草稿，本周内补齐。

## 10. 完成判定

第 2 节 4 个勾全部勾上 → Task 1 DONE → 明天进入 Task 2（Git 服务）。
任一未通过 → Task 1 保持 IN PROGRESS，只补未通过项。
