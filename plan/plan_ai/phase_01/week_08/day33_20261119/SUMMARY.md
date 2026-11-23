# Day 33 · 2026-11-19 · Week 08 Task 4 实施步骤总结（SUMMARY）

> 本文件是 [PLAN.md](./PLAN.md) 的可执行版本：给出每一步的**完整命令**（任意目录下均可直接运行，不依赖当前工作目录）以及**每个参数的解释**。执行时按顺序走，每步勾掉即完成对应验收项。
>
> 关键路径：干净环境演练（计时）→ 修文档 → §8 验收 → 发 v0.5.0 → 阶段复盘 → 切阶段二 → 录音 → 清理。

---

## 0. 目标（一句话）

从 GitHub 在全新目录 clone WorkPilot，按 README 计时跑通（< 30 分钟），完成 phase_01 §8 验收，发布 `v0.5.0`，写阶段复盘，把项目切到「阶段二 · 第 9 周」。

---

## 1. 占位符约定（执行前先替换）

命令中用 `<尖括号>` 表示需要你替换成真实值：

| 占位符 | 含义 | 例子 |
| ------ | ---- | ---- |
| `<github-user>` | 你的 GitHub 用户名 | `octocat` |
| `<样例独有问题>` | 只存在于 `data/sample` 样例文档中的问题 | `公司前端规范里 Button 组件必须带什么属性？` |
| `<file>.md` | 50 题评测报告文件名（Day30 产物） | `50q-v1.md` |

> 云端 Demo 改用**固定 IP**，不再使用域名：`http://8.148.216.61`（服务器 SSH 用户为 `root`）。
>
> 下文所有命令里的 `~` 指当前用户的 home 目录（macOS 下即 `/Users/<你>`），任意目录下执行时 shell 都会正确展开。

---

## 2. 前置确认（确认起点状态正确）

在干净演练之前，先确认日常环境状态，避免端口 / 远程冲突。以下每条命令均用 `git -C` 或绝对路径，**任意目录下都能执行**：

```bash
# 1) 确认日常仓库干净、处于最新提交
git -C ~/lab/workpilot status
#    -C <路径>   : 在指定路径下执行 git，等价于「先 cd 再执行」，因此不依赖当前目录

git -C ~/lab/workpilot log --oneline -1
#    log          : 查看提交历史
#    --oneline    : 每个提交压缩成一行（只显示短 hash + 标题）
#    -1           : 只显示最近 1 条提交

# 2) 确认 GitHub 远程（名为 github）可达
git -C ~/lab/workpilot ls-remote github | head -3
#    ls-remote    : 列出远程仓库的引用（分支 / tag），不发包只探测，用于验证网络与权限
#    github       : Day32 配置的远程名，指向你的 GitHub 公共仓库
#    head -3      : 只看前 3 行，避免刷屏

# 3) 停掉日常环境的容器，释放 8080 端口（数据卷保留，不删）
make -C ~/lab/workpilot down
#    -C <路径>    : make 在指定目录下执行（等价于 cd 后 make）
#    down         : Makefile 里封装的 docker compose down 目标，停止并移除容器/网络，但保留卷

# 4) 确认云端 Demo 仍在线（预期返回 401，因为开启了 basic auth）
curl -sI http://8.148.216.61 | head -1
#    -s   : silent，静默模式，不显示进度条
#    -I   : 只发 HEAD 请求，拿响应头（不下载正文），用于探活
#    head -1 : 只显示第一行（HTTP 状态行，如 HTTP/1.1 401）

# 5) 确认干净环境所需的 Embedding 模型已就绪（或改用 SiliconFlow，见 Step 1）
ollama list | grep bge-m3
#    list      : 列出本机已下载的 Ollama 模型
#    grep bge-m3 : 过滤出 bge-m3 模型行，确认存在（空结果=未下载，需 ollama pull bge-m3）
```

---

## 3. Step 1 · 干净环境演练（只看 README，开始计时）

> 原则：只允许看 clone 下来的 README 和 `.env.example`，**不许参考本机已有的 `~/lab/workpilot/.env` 或你的记忆**。每遇到一次「README 没写清楚、我凭记忆解决」，记一条到 draft.md。

```bash
# 1) 创建干净目录并进入（-p：父目录不存在时自动创建）
mkdir -p ~/tmp/wp-clean && cd ~/tmp/wp-clean
#    -p   : parents，递归创建不存在的父级目录

# 2) 开始计时：记录当前 Unix 时间戳（秒）
START=$(date +%s)
#    date +%s : 输出从 1970-01-01 起的秒数；存入变量 START 用于最后算耗时

# 3) 从 GitHub clone（模拟陌生用户，不含任何本地缓存配置）
git clone https://github.com/<github-user>/workpilot.git && cd workpilot
#    clone <url> : 克隆远程仓库到当前目录下名为 workpilot 的子目录
#    &&          : 上一步成功才执行下一步（clone 成功后进入目录）

# 4) 用模板生成 .env，并只按 .env.example 里的注释填写真实值
cp .env.example .env
#    cp 源 目标 : 复制 .env.example 为 .env；随后用编辑器手动填写 LLM key、MinIO 账号等

# 5) 以独立项目名启动整套栈（关键：不与日常环境共用卷/网络）
make up PROJECT=wpclean
#    up         : Makefile 封装的 docker compose up -d --build，后台构建并启动
#    PROJECT=wpclean : 传给 Makefile 的变量，指定 compose 项目名；容器/卷/网络前缀变为 wpclean_*
#                      若省略则项目名默认取自目录名 workpilot，会复用日常环境的旧数据卷（不再"干净"）

# 6) 查看容器状态，确认全部 healthy / running
make ps PROJECT=wpclean
#    ps         : 列出当前项目的容器状态
#    PROJECT=wpclean : 必须与 up 一致，才能看到刚才这套干净栈

# 7) 导入样例语料（data/sample）
make seed
#    seed       : Makefile 里封装的数据导入目标，把 data/sample 下样例文档切块/入库并生成 embedding

# 8) 验证「带引用问答」：发流式请求，命中引用事件即成功
curl -sN -X POST localhost:8080/v1/kb/ask/stream \
  -H 'Content-Type: application/json' \
  -d '{"question":"<样例独有问题>"}' | grep -m1 'event: retrieved'
#    -s          : silent，静默
#    -N          : no-buffer，禁用输出缓冲，实时打印流式响应（SSE 必须）
#    -X POST     : 指定请求方法为 POST
#    -H '...'    : 设置请求头，声明请求体为 JSON
#    -d '{...}'  : 请求体（JSON），question 填入样例文档独有的问题
#    grep -m1 'event: retrieved' : 从流式输出中匹配到第一个「检索到引用」事件后立即停止，证明 RAG 生效

# 9) 输出本次演练总耗时（分钟）
echo "elapsed: $(( ($(date +%s) - START) / 60 )) min"
#    $(date +%s) : 再次取当前时间戳
#    $(( ... ))  : shell 算术运算，两时间戳相减得秒数，再 /60 转分钟
```

**再用浏览器走一遍全流程**（打开 http://localhost:8080 ）：上传文档 → 提问并看到段落引用 → 问库外问题被拒答 → 点 👎 反馈。

**记录两点（写入 draft.md）**：

- 本机已缓存镜像 / bge-m3，实际耗时会比「全新机器」短；注明并估算全新机器额外耗时（镜像拉取 + `ollama pull bge-m3`）。
- 若想验证「无 Ollama」替代路径：在 `.env` 里把 Embedding 指向 SiliconFlow（同模型），确认 README 这条路径也可用。

---

## 4. Step 2 · 修复演练暴露的问题

只改文档 / Makefile / `.env.example`，**不加功能**。改完后提交并双推：

```bash
# 一次性暂存已跟踪文件的改动并提交（-a 暂存所有已跟踪文件，-m 附提交信息）
git -C ~/lab/workpilot commit -am "docs: fix quickstart issues found in clean-environment drill"
#    -C <路径> : 在 ~/lab/workpilot 下执行
#    -a        : add all，把已跟踪文件的修改全部暂存（新文件仍需单独 git add）
#    -m "..."  : 提交信息

# 推送到 Gitea（origin）
git -C ~/lab/workpilot push
#    push        : 推送本地提交到默认远程 origin（Gitea）

# 推送到 GitHub（远程名 github，分支 main）
git -C ~/lab/workpilot push github main
#    push github main : 推送到名为 github 的远程的 main 分支
```

> 若演练中无任何问题，则跳过修改，直接记录「0 问题」并进入 Step 3。

---

## 5. Step 3 · phase_01 §8 逐项验收（写入 phase01-review.md 第 1 节）

这是**文字填写**步骤（无命令），把下表逐项填入 `~/lab/projects/product-lab/reviews/phase01-review.md` 第 1 节，结论写 PASS / FAIL / CONDITIONAL，并附证据链接：

| # | 验收项 | 结论 | 证据 |
| - | ------ | ---- | ---- |
| 1 | 干净环境 30 分钟内恢复并运行 v0.5 | | 今日计时 \_\_ 分钟 |
| 2 | 公网可访问，上传→带引用问答→反馈 全流程 | | `http://8.148.216.61`（Day28）+ 今日复测 |
| 3 | 50 题评测报告，hit@5 / 引用正确率 / 拒答率有基线 | | `eval/reports/<file>.md` |
| 4 | Badcase ≥ 10 条，带分类和处理结论 | | `eval/badcases/badcases.md`（\_\_ 条） |
| 5 | DA-01 定义文档已写，PROJECT_CONFIG 已回填 | | `docs/product/da01-definition.md` |
| 6 | P1 作品集：README + 架构图 + Demo + 8 问 | | README / `docs/architecture.md` / `demo.gif` / `p1.md` |
| 7 | 能力矩阵 ≥ 12 项 JD 能力并标出证明模块 | | `career/capability-matrix.md` |
| 8 | 能 3 分钟讲清 P1 | | 今日录音时长 \_\_ |

**判定规则**：8 项核心全 PASS → 进入 phase_02；附加项 CONDITIONAL 的写明「W9 Day34 前 30 分钟补齐」；任一核心项 FAIL → 不打 `v0.5.0`，W9 第一天先补该项（记入 `plan/CHANGELOG.md`）。

---

## 6. Step 4 · Release notes + tag `v0.5.0`

### 6.1 写 Release notes

创建 `docs/releases/v0.5.0.md`，内容模板见 [PLAN.md](./PLAN.md) Step 4（亮点 / 快速开始 / 已知问题 / 下一步四段），把 `**`、`¥__`、`__ 分钟` 等占位换成真实指标。

```bash
# 暂存新文件并提交、推送
git -C ~/lab/workpilot add docs/releases/v0.5.0.md
#    add <文件> : 暂存该文件（新文件必须显式 add）

git -C ~/lab/workpilot commit -m "docs: release notes for v0.5.0" && git -C ~/lab/workpilot push
#    &&   : 提交成功后推送；-m 附提交信息；push 推送到 origin（Gitea）
```

### 6.2 打 tag 并双推

```bash
# 打带说明的附注 tag（推荐用 -a，比轻量 tag 多存 tagger/时间/说明）
git -C ~/lab/workpilot tag -a v0.5.0 -m "v0.5.0: P1 WorkPilot Knowledge"
#    tag         : 创建 tag
#    -a v0.5.0   : 创建附注（annotated）tag，名为 v0.5.0
#    -m "..."    : tag 的说明信息

# 推 tag 到 Gitea
git -C ~/lab/workpilot push origin v0.5.0
#    push origin v0.5.0 : 只推送 v0.5.0 这个 tag 到 origin

# 推 tag 到 GitHub
git -C ~/lab/workpilot push github v0.5.0
#    push github v0.5.0 : 推送 v0.5.0 tag 到 GitHub 远程
```

> 若 Day32 用了快照分支（public-main），则在 `public-main` 上打 tag 再推 github。

### 6.3 在 GitHub / Gitea 上发布 Release（网页手动操作）

- GitHub：仓库页 → **Releases** → **Draft a new release** → 选择 tag `v0.5.0` → 粘贴 Release notes → 附 `demo.gif` 链接 → **Publish release**。
- Gitea：同样在「版本发布」里创建 Release。

---

## 7. Step 5 · 阶段复盘

创建 `~/lab/projects/product-lab/reviews/phase01-review.md`，按 [PLAN.md](./PLAN.md) Step 5 的 9 个标题填写（验收结果 / 指标 vs 目标 / 投入 / 花费 / 做对了什么 / 做错返工 / 无效学习 / 真实使用次数 / 对 phase_02 调整）。

同时填写 `plan/phase_01/week_08/README.md` 第 11 节周复盘。

```bash
# 提交复盘产物并推送
git -C ~/lab/projects add product-lab/reviews
#    add product-lab/reviews : 暂存整个 reviews 目录（含新写的 phase01-review.md）

git -C ~/lab/projects commit -m "docs: phase 01 review" && git -C ~/lab/projects push
#    commit -m : 提交；push : 推送
```

---

## 8. Step 6 · 状态切换 + 录音 + 收尾

### 8.1 更新 PROJECT_CONFIG（手动编辑）

编辑 `/Users/infinity/Documents/a_future/PROJECT_CONFIG.md` 的「当前状态」表：

- 当前阶段 → `阶段二 · Agent 与 P2（第 9–16 周）`
- 当前周 → `第 9 周`
- DA-01 状态 → `v0.5.0 P1 已发布（GitHub 链接），下一步 M6 Tool Layer`

> 若 Step 3 出现 FAIL 调整了计划，同步写入 `plan/CHANGELOG.md`。

### 8.2 3 分钟讲解录音

按 Day31 讲稿脱稿讲一遍，用 QuickTime「新建音频录制」或手机录音，回听一次，把卡壳点记下（W25 面试素材）。时长控制在 2:30–3:30，本地保存、不入库。

### 8.3 清理干净环境（确认 wpclean 前缀后再删）

```bash
# 1) 停掉并移除干净环境的容器（不删卷）
make -C ~/tmp/wp-clean/workpilot down PROJECT=wpclean
#    down PROJECT=wpclean : 停止并移除 wpclean_ 前缀的容器/网络

# 2) 先看清有哪些 wpclean 卷（只看名字，不删）
docker volume ls --filter name=wpclean_ -q
#    ls          : 列出卷
#    --filter name=wpclean_ : 只匹配名字含 wpclean_ 的卷
#    -q          : quiet，只输出卷名（ID 不显示），便于后续删除

# 3) 删除 wpclean 卷（更安全的替代：docker volume prune，见下注）
docker volume rm $(docker volume ls --filter name=wpclean_ -q)
#    rm <名字...> : 删除指定卷；$(...) 命令替换，把上一条列出的卷名作为删除参数

# 4) 恢复日常环境
make -C ~/lab/workpilot up
#    up          : 重新启动日常环境（wp 项目名，数据卷仍在）
```

> 更安全做法：用 `docker volume prune --filter name=wpclean_`（prune 自动跳过正在使用的卷，且空结果不会报错）。若上面 `rm $(...)` 因无匹配卷而报错，属正常，可忽略。

---

## 9. 完成判定

第 3 节（验收对齐）全部勾上 → Task 4 DONE → Week 8 DONE → **Phase 1 DONE（v0.5 P1 发布）** → 下次进入 Day34（Phase 2 · Week 09 Task 1：Tool Calling 原理 + Registry，M6.1）。

任一核心项未通过 → 保持 IN PROGRESS，Day34 先补该项，再开始 Tool Calling。

---

## 附：常见卡点速查（对应 PLAN §10）

| 现象 | 处理 |
| ---- | ---- |
| `port is already allocated` | 日常环境未停：`make -C ~/lab/workpilot down`；或临时改端口并记录 |
| 干净环境 api 启动即退出（缺变量） | `.env.example` 漏键或注释不清 → 这是要修的文档问题，修完重新计时 |
| `make seed` 找不到 `data/sample` | `.gitignore` 忽略了样例 → 修 `.gitignore` 并补提交样例 |
| 演练超 30 分钟 | 不作弊，记真实时间与主要耗时环节，判 FAIL / CONDITIONAL，W9 改进后复测 |
| GitHub tag 推送被拒（已存在） | 不强推覆盖已公开 tag，改发 `v0.5.1` |
