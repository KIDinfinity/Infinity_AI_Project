# Day 33 执行步骤清单（可直接逐条执行）

> 来源：[PLAN.md](PLAN.md)。本文件把 PLAN.md 的 6 个 Step 拆成可直接复制执行的命令序列，按顺序从上到下执行。每一步前标注对应 PLAN.md 的小节，方便回查。执行中请把 `<...>` 占位符替换为你的实际值（域名、GitHub 用户名等）。

## 使用说明

- 全程从 `~/lab/workpilot` 出发（你已有的本地仓库）；干净环境演练在 `~/tmp/wp-clean` 另开一份。
- 遇到命令报错先看文末「卡住时处理」速查表，对应 PLAN.md 第 10 节。
- 每做完一个 Step，回到 PLAN.md 第 3 节勾掉对应验收项。

---

## Step 0 · 前置确认（PLAN.md §2）

```bash
cd ~/lab/workpilot && git status && git log --oneline -1 && git ls-remote github | head -3
make down                                  # 释放 8080，避免与干净环境冲突（数据卷保留）
curl -sI https://wp.<域名> | head -1        # 确认云端仍在线（期望看到 401 或 200）
ollama list | grep bge-m3                  # 确认本机有 bge-m3（干净环境的 Embedding 依赖，或改用 SiliconFlow）
```

验证通过标准：`git status` 无异常未提交改动（或能说清楚原因）；`git ls-remote github` 能看到分支；`make down` 无报错；云端 curl 返回状态码。

---

## Step 1 · 干净环境演练 + 计时（PLAN.md Step 1）

```bash
mkdir -p ~/tmp/wp-clean && cd ~/tmp/wp-clean
START=$(date +%s)
git clone https://github.com/<you>/workpilot.git && cd workpilot
cp .env.example .env
```

→ 用编辑器打开 `.env`，只参考 `.env.example` 里的注释手动填写（LLM key、MinIO 账号等）。**不要**从 `~/lab/workpilot/.env` 复制粘贴，否则不算「干净环境」。

```bash
make up PROJECT=wpclean            # 独立的容器 / 卷前缀 wpclean_*
make ps PROJECT=wpclean            # 确认各服务都是 running/healthy
make seed                          # 导入 data/sample 样例数据
curl -sN -X POST localhost:8080/v1/kb/ask/stream -H 'Content-Type: application/json' \
  -d '{"question":"<样例文档中的独有问题>"}' | grep -m1 'event: retrieved'
echo "elapsed: $(( ($(date +%s) - START) / 60 )) min"
```

再打开浏览器访问 `http://localhost:8080`，手动走一遍完整用户流程：

1. 上传一个文档
2. 提问并确认回答带引用
3. 问一个库外问题，确认被拒答
4. 点一次 👎 反馈

记录（填入 PLAN.md 第 11 节「产出记录」）：

- 实际耗时：`echo` 输出的分钟数
- 若想排除本机缓存影响，额外估算全新机器需要的镜像拉取 + `ollama pull bge-m3` 耗时
- 可选：把 `.env` 中 Embedding 配置改成 SiliconFlow，重新验证这条替代路径是否也能跑通
- 每发现一次「README 没写清楚、靠记忆解决」，记一条到 `draft/draft.md`（作为 Step 2 的修复清单）

---

## Step 2 · 修复演练中暴露的问题（PLAN.md Step 2）

回到正式仓库，只改文档 / Makefile / `.env.example`，不加新功能：

```bash
cd ~/lab/workpilot
# 在此处用编辑器按 Step 1 记录的问题清单逐条修复 README / Makefile / .env.example
git add -A
git commit -am "docs: fix quickstart issues found in clean-environment drill"
git push
git push github main
```

若 Step 1 没有发现任何问题，跳过本步，并在产出记录中写「0 问题」。

---

## Step 3 · phase_01 §8 逐项验收（PLAN.md Step 3）

打开（或新建）`~/lab/projects/product-lab/reviews/phase01-review.md`，在第 1 节填入下表，把 PASS/FAIL/CONDITIONAL 和证据链接逐项填好：

```bash
mkdir -p ~/lab/projects/product-lab/reviews
touch ~/lab/projects/product-lab/reviews/phase01-review.md
```

| #   | 验收项                                       | 结论 | 证据                                                   |
| --- | -------------------------------------------- | ---- | ------------------------------------------------------ |
| 1   | 干净环境 30 分钟内恢复并运行 v0.5            |      | 今日计时 \_\_\_ 分钟                                   |
| 2   | 公网可访问，上传→带引用问答→反馈 全流程      |      | `https://wp.<域名>` + 今日复测                         |
| 3   | 50 题评测报告，hit@5/引用正确率/拒答率有基线 |      | `eval/reports/<文件>.md`                               |
| 4   | Badcase ≥ 10 条，带分类和处理结论            |      | `eval/badcases/badcases.md`（\_\_\_ 条）               |
| 5   | DA-01 定义文档已写，PROJECT_CONFIG 已回填    |      | `docs/product/da01-definition.md`                      |
| 6   | P1 作品集：README + 架构图 + Demo + 8 问     |      | README / `docs/architecture.md` / `demo.gif` / `p1.md` |
| 7   | 能力矩阵 ≥ 12 项 JD 能力并标出证明模块       |      | `career/capability-matrix.md`                          |
| 8   | 能 3 分钟讲清 P1                             |      | 今日录音时长 \_\_\_                                    |

判定规则：

- 8 项核心全部 PASS → 进入 phase_02（继续 Step 4）
- 附加项（CI、云端恢复 RTO、Playwright E2E、P95/成本实测）CONDITIONAL → 写明「W9 Day34 前 30 分钟补齐」
- 任一核心项 FAIL → **不打 `v0.5.0`**，先回到对应项修复，并在 `plan/CHANGELOG.md` 记录调整

---

## Step 4 · Release notes + Git tag + GitHub Release（PLAN.md Step 4）

```bash
mkdir -p ~/lab/workpilot/docs/releases
```

创建 `~/lab/workpilot/docs/releases/v0.5.0.md`，内容：

```markdown
# WorkPilot v0.5.0 — P1 WorkPilot Knowledge（2026-11-19）

## 亮点

- 文档上传 → 异步入库；流式问答 + 段落引用 + 库外拒答；会话历史与 👍/👎 反馈
- 50 题评测：hit@5 ** · 引用正确率 ** · 库外拒答率 ** · P95 **s · 单次 ¥\_\_（eval/reports/<文件>.md）
- Docker Compose + Caddy HTTPS 部署、request_id 日志、/health /ready、CI、备份恢复（RTO \_\_ 分钟）

## 快速开始

见 README「快速开始」（干净环境实测 \_\_ 分钟）

## 已知问题 / 限制

- 无登录与多用户（basic auth 仅用于 Demo，W19 引入认证）
- 后台导入为进程内任务，重启会中断（W19 评估队列）
- ……（来自 badcases 与演练记录）

## 下一步

v0.6–v1.0（P2）：Tool Calling、Agent（LangGraph）、Memory / HITL、MCP、Agent 评测与可观测
```

```bash
cd ~/lab/workpilot
git add docs/releases/v0.5.0.md
git commit -m "docs: release notes for v0.5.0"
git push
git tag -a v0.5.0 -m "v0.5.0: P1 WorkPilot Knowledge"
git push origin v0.5.0
git push github v0.5.0      # 若 Day32 用了快照分支：改为在 public-main 上打 tag 再推 github
```

然后在 GitHub 网页上：Releases → Draft a new release → 选 tag `v0.5.0` → 粘贴上面的 Release notes → 附上 `demo.gif` 链接 → Publish。
在 Gitea 网页上「版本发布」同样创建一次。

---

## Step 5 · 阶段复盘（PLAN.md Step 5）

在 `~/lab/projects/product-lab/reviews/phase01-review.md` 追加以下结构并填写内容：

```markdown
# Phase 01 复盘（W1–W8 · 09-28 → 11-19）

## 1. 验收结果（Step 3 表格）

## 2. 指标 vs 目标（DA01 §11：hit@5 / 引用正确率 / 拒答率 / P95 / 成本 / 恢复时间）

## 3. 投入 实际总时长 **_ h（计划 33 天 × 1–2h）；超时的天：_**

## 4. 花费 LLM ¥** · Embedding ¥** · 云 ¥** · 域名 ¥**（预算 ≤ ¥1100 / 半年）

## 5. 做对了什么（3 条）

## 6. 做错 / 返工（3 条，带根因）

## 7. 无效学习 / 范围扩张（有则列出与浪费时长）

## 8. 真实使用 自己用 WorkPilot 的次数（脱敏语料）：\_\_\_

## 9. 对 phase_02 的调整（CONDITIONAL 补齐计划、需要改的节奏或范围）
```

同时打开 `plan/plan_ai/phase_01/week_08/README.md`，填写第 11 节「周复盘」。

```bash
cd ~/lab/projects
git add product-lab/reviews
git commit -m "docs: phase 01 review"
git push
```

---

## Step 6 · 状态切换 + 讲解录音 + 收尾（PLAN.md Step 6）

**1. 更新项目状态**

打开 `/Users/226838/Documents/privacy/Infinity_AI_Project/PROJECT_CONFIG.md`，把「当前状态」改为：

- 当前阶段 → 阶段二 · Agent 与 P2（第 9–16 周）
- 当前周 → 第 9 周
- DA-01 状态 → 「v0.5.0 P1 已发布（GitHub 链接），下一步 M6 Tool Layer」

若 Step 3 因 FAIL 调整了计划，同步把调整写入 `plan/CHANGELOG.md`。

**2. 讲解录音**

按 Day31 讲稿脱稿讲一遍（时长 2:30–3:30），用 macOS QuickTime Player「文件 → 新建音频录制」或手机录音 App，录完回听一次，把卡壳点记到 `draft/draft.md`（作为 W25 面试准备素材）。录音只本地保存，不入库。

**3. 清理干净环境**

```bash
cd ~/tmp/wp-clean/workpilot
make down PROJECT=wpclean
docker volume ls --filter name=wpclean_ -q            # 先确认要删的卷都带 wpclean_ 前缀
docker volume rm $(docker volume ls --filter name=wpclean_ -q)
cd ~/lab/workpilot && make up                          # 恢复日常开发环境
```

---

## 完成判定（PLAN.md §12）

PLAN.md 第 3 节全部勾上 →
Task 4 DONE → Week 8 DONE → **Phase 1 DONE（v0.5 P1 发布）** →
下一次进入 Day34（Phase 2 · Week 09 Task 1：Tool Calling 原理 + Registry，M6.1）。

任一核心项未通过 → 保持 IN PROGRESS，Day34 先补该项，再开始 Tool Calling。

---

## 卡住时的处理（摘自 PLAN.md §10）

| 现象                                                      | 处理                                                                               |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | 原环境未停：`cd ~/lab/workpilot && make down`；或临时改端口并记录                  |
| 干净环境 api 启动即退出（缺变量）                         | `.env.example` 漏了键或注释不清，这是要修的文档问题，修完重新计时                  |
| `make seed` 找不到 `data/sample`                          | `.gitignore` 把样例文件忽略了：修 `.gitignore` 并补提交样例                        |
| 演练超过 30 分钟                                          | 不作弊，记录真实时间与主要耗时环节，判 FAIL/CONDITIONAL，W9 第一天针对性改进后复测 |
| GitHub tag 推送被拒（已存在）                             | 确认该 tag 指向的提交；不要强推覆盖已公开 tag，改发 `v0.5.1`                       |
| 复盘写不出来                                              | 先按 9 个标题各写一句话，再补数字；数字从 `draft/draft.md` 和当日产出记录中抄      |
