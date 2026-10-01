# Day 02 · 2026-09-29 · Week 01 Task 2：Git 代码仓库

## 0. 今天只做一件事

Week 01 Task 2：部署一个自托管 Git 服务（Gitea，跑在昨天的 Docker 上），建测试仓库跑通 `clone / commit / push`，并落下 `projects/{product-lab, ai-lab, infra}` 三目录结构。

不碰：MinIO、Qdrant、CI/CD、项目模板（模板是 Task 4，第 2 周才引存储）。

## 1. 起点（已确认）

- 本机：macOS
- Docker 已可用（Day 01 用 Docker Desktop 装好，`docker run / ps / logs / stop / rm` 已练熟）
- 代理可用：`http://127.0.0.1:7890`（拉镜像时用）
- 待确认：本机 `git` 是否已安装、是否已有全局 user.name / user.email

## 2. 验收对齐（做完要能勾掉）

- [ ] 自托管 Git 服务可访问（浏览器能打开 Web UI，能登录）
- [ ] 能独立在 Web UI 创建新仓库（不看教程）
- [ ] 本地 `clone / commit / push` 跑通一次
- [ ] `projects/{product-lab, ai-lab, infra}` 三目录结构已落到远端仓库
- [ ] 产出：可用的 Git 服务 + 测试仓库 + 三目录结构

## 3. 时间块（约 90 分钟）

| 时间 | 内容 |
|---|---|
| 0–10 min | 本地 Git 基础确认（`git --version` / 配置 user） |
| 10–35 min | 部署 Gitea（Docker）+ 首次 Web 安装 |
| 35–55 min | 建测试仓库 + `clone / commit / push` 跑通 |
| 55–70 min | 建 `projects/{product-lab, ai-lab, infra}` 三目录并推送 |
| 70–80 min | 概念自检（image/container/volume 复用 + Git 三区） |
| 80–90 min | 写产出记录 + 顺手记痛点 |

时间不足时，最低保留：Gitea 起来 + 一个测试仓库 push 成功。

## 4. 执行步骤

### Step 1 · 本地 Git 基础确认

```bash
git --version
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --global init.defaultBranch main
git config --list | grep user   # 确认写入
```

### Step 2 · 部署 Gitea（复用 Day 01 的 Docker）

```bash
docker run -d --name gitea \
  -p 3000:3000 \
  -p 2222:22 \
  -e TZ=Asia/Shanghai \
  -v ~/gitea/data:/data \
  --restart unless-stopped \
  gitea/gitea:latest

docker ps                 # 确认 gitea 在运行
docker logs gitea         # 看启动日志，无报错即可
```

要点：`-v ~/gitea/data:/data` 把 Gitea 全部数据（仓库、账号、配置）放在宿主机，容器删了也不丢 —— 这就是 Day 01 volume 知识的直接复用。

浏览器打开 `http://localhost:3000`，进入首次安装页：

- 数据库：**SQLite**（个人自托管够用，不引入 MySQL/Postgres，保持简单）
- 站点/管理员账号：设置自己的管理员用户名 + 密码
- 其余保持默认，点「安装」

> 若 `3000` 端口被占用，改 `-p 3001:3000`，后面地址同步改。
> 若已有可用的 GitHub/Gitea 托管，可跳过本步，Step 3/4 的 origin 换成现成托管地址即可。

### Step 3 · 建测试仓库 + 跑通 clone / commit / push

1. Web UI 右上角 → 新建仓库，命名 `test-repo`，可见性 Private，勾选「初始化 README」。
2. 复制仓库地址（HTTPS：`http://localhost:3000/<user>/test-repo.git`）。
3. 本地：

```bash
mkdir -p ~/lab && cd ~/lab
git clone http://localhost:3000/<user>/test-repo.git
cd test-repo
echo "hello gitea" > note.txt
git add note.txt
git commit -m "add note"
git push
```

HTTPS 推送会要求用户名/密码。密码处填 Gitea 里生成的 **访问令牌（Token）**：
设置 → 应用 → 生成令牌（勾选 repo 权限），用 Token 当密码。

若要改用 SSH（端口 2222）：

```bash
ssh -T -p 2222 git@localhost    # 首次需在 Gitea 里配置公钥
git remote set-url origin ssh://git@localhost:2222/<user>/test-repo.git
```

跑通一次即可，端口冲突时 HTTPS 更省事，先不折腾 SSH。

### Step 4 · 建立三目录结构

目标：把未来实验室的骨架一次性落下，之后每个新项目直接放进去。

1. Web UI 新建仓库 `projects`（Private，不初始化 README）。
2. 本地：

```bash
cd ~/lab
git clone http://localhost:3000/<user>/projects.git
cd projects
mkdir -p product-lab ai-lab infra
printf '# product-lab\n\n面向真实产品的项目。\n' > product-lab/README.md
printf '# ai-lab\n\nAI / Agent / 感知-决策 实验。\n' > ai-lab/README.md
printf '# infra\n\n私有云 / Docker / 存储 / 备份。\n' > infra/README.md
printf '# projects\n\n三目录：product-lab / ai-lab / infra\n' > README.md
git add .
git commit -m "init projects skeleton"
git push
```

三个目录的含义（对齐 `PROJECT_CONFIG.md` 的三条线）：

| 目录 | 承载 | 对应工作线 |
|---|---|---|
| `product-lab` | 真实痛点 → 解决方案 / MVP | A |
| `ai-lab` | AI / Agent / 感知-决策 能力实验 | B |
| `infra` | Docker / 存储 / 备份 / 私有云 | C |

## 5. 概念自检（不看教程，口述或默写）

1. Gitea 数据存在哪？容器删了为什么仓库还在？（答：`-v ~/gitea/data:/data`，数据在宿主 volume 里，与容器生命周期无关）
2. `git clone / commit / push` 各做了什么？（答：克隆/落提交/推远端）
3. `git add` 和 `git commit` 的区别？（答：暂存区 vs 版本快照）
4. 为什么 Private 仓库 + Token，而不是明文密码？（答：Token 可撤销、可限权，不泄漏主密码）
5. 三个 lab 目录分别放什么？（答：product-lab=产品 / ai-lab=AI 能力 / infra=基础设施）

## 6. 对 DA-01 的贡献（今天要能答出来）

DA-01 要求「可交付、可迭代」，前提是**统一托管 + 版本历史 + 可备份**。
今天建立的 Git 服务与三目录结构，是 DA-01 代码的唯一归口：后续 Task 3 规范、Task 4 模板、第 2 周存储验证，全部落在这里，避免资产散落本机。

## 7. 卡住时的处理

| 现象 | 处理 |
|---|---|
| 拉 `gitea/gitea` 镜像超时 | 用 Day 01 的代理方式重新拉；或先 `docker pull` 单独拉一次 |
| `3000` 端口被占用 | 改 `-p 3001:3000`，地址同步改 |
| 浏览器打不开 3000 | `docker ps` 看容器是否运行、`docker logs gitea` 看报错 |
| push 报 403 / 认证失败 | 用 Gitea 生成的 Token 当密码，不要用登录密码 |
| push 报 `rejected non-fast-forward` | 先 `git pull --rebase` 再 push |
| 超过 60 分钟还没跑通一次 push | 停止记录卡点，明天优先解决，不硬耗 |

## 8. 产出记录（执行时填写）

- Git 服务地址 / 版本：____
- 是否成功登录 Web UI：____
- 测试仓库 `test-repo` push 是否成功：____
- `projects` 三目录结构是否已推送：____
- 用的认证方式（HTTPS Token / SSH）：____
- 卡点记录：____
- 用时：____ 分钟

## 9. 今日额外（顺手，不占主线）

Task 0 继续：随手再记 2–3 条真实痛点（工作反复遇到的问题 / AI 使用不顺 / 手工重复劳动），一句话一条，本周内补齐到 ≥5 条。

## 10. 完成判定

第 2 节 5 个勾全部勾上 → Task 2 DONE → 明天进入 Task 3（项目规范）。
任一未通过 → Task 2 保持 IN PROGRESS，只补未通过项。

## 11. 追加：Day 01 回顾（可选，2 分钟）

可顺手确认 Day 01 的 Docker 环境仍在：`docker ps` 有输出、`docker version` 的 Server 正常。
Gitea 正是跑在这个环境上的第一个「真实服务」，说明底座可用。
