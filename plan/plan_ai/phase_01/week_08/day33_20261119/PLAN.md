# Day 33 · 2026-11-19 · Week 08 Task 4：8 周总验收 + 干净环境恢复（v0.5）

## 0. 今天只做一件事

在一个全新目录里从 GitHub clone WorkPilot，按 README 计时跑通（目标 < 30 分钟），然后逐项完成 phase_01 §8 验收，发布 `v0.5.0`（P1 WorkPilot Knowledge），写阶段复盘，并把项目状态切到「阶段二 · 第 9 周」。

不碰：任何新功能、Tool Calling（W9 才开始）、重构、README 再润色（只修演练中发现的错误）。

## 1. 资产锚点

- 构建模块：v0.5 总验收（覆盖 M1 M2 M3 M4 M5 M12.1 M13）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5、§9）
- 版本里程碑：**v0.5 = P1 发布**
- 今天之后 WorkPilot 多了什么（可演示/可测量）：干净环境恢复实测 \_\_\_\_ 分钟；tag `v0.5.0` + Release notes；§8 验收表（PASS / FAIL / CONDITIONAL + 证据）；3 分钟讲解录音
- 今日 AI 实际应用：以「陌生用户」身份验证整个 AI 应用（LLM key 配置 → embedding → 向量库 → 带引用问答）是否可复现——可复现性是 AI 系统交付的第一要求

## 2. 起点（前置确认）

- 已有：GitHub 公共仓库（Day32）；云端 Demo（Day28）；评测报告、badcases、p1.md、简历条目。
- 需确认：

```bash
cd ~/lab/workpilot && git status && git log --oneline -1 && git ls-remote github | head -3
make down                                  # 释放 8080，避免与干净环境冲突（数据卷保留）
curl -sI https://wp.<域名> | head -1        # 云端仍在线（401）
ollama list | grep bge-m3                  # 干净环境的 Embedding 依赖（或改用 SiliconFlow，见 Step 1）
```

## 3. 验收对齐（做完要能勾掉）

- [ ] 干净环境：从 GitHub clone → 填 `.env` → `make up` → `make seed` → 带引用问答通过，计时 < 30 分钟（写下实际分钟数）
- [ ] 演练中发现的 README / Makefile 问题已修复并推送（无问题则记录「0 问题」）
- [ ] phase_01 README §8 的 8 项全部给出 PASS / FAIL / CONDITIONAL 和证据链接；核心项全 PASS
- [ ] `docs/releases/v0.5.0.md` 已写；tag `v0.5.0` 已推送到 Gitea 与 GitHub；GitHub Release 已发布
- [ ] `~/lab/projects/product-lab/reviews/phase01-review.md` 已写并提交
- [ ] `PROJECT_CONFIG.md` 当前状态已更新为阶段二 · 第 9 周
- [ ] 3 分钟 P1 讲解录音一次（本地保存，不入库），时长 2:30–3:30

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                    |
| ------- | ------ | --------------------------------------- |
| 0–35    | P0     | 干净环境演练（计时）+ 记录卡点          |
| 35–45   | P0     | 修复 README / Makefile 中暴露的问题     |
| 45–70   | P0     | §8 逐项验收表                           |
| 70–85   | P0     | Release notes + tag `v0.5.0` + 推送     |
| 85–105  | P0     | 阶段复盘 + PROJECT_CONFIG + Week 8 复盘 |
| 105–115 | P0     | 3 分钟讲解录音                          |
| 115–120 | P1     | 清理干净环境的容器与卷                  |

时间不足时最低保留：干净环境演练 + 验收表 + tag。复盘和录音最晚在 W9 Day34 开始前补完。

## 5. 今日学习（只学完成任务必须的）

- 「干净环境」验证的是文档与自动化，而不是你的记忆：只能看 README 和 `.env.example`，不许参考本机已有配置。
- Compose 项目名决定容器 / 卷 / 网络前缀；用 `-p wpclean` 起一套完全独立的栈，不会碰到原来的数据卷。
- 发布说明（Release notes）面向使用者：新增了什么、指标多少、已知问题、如何升级。
- 资料：https://docs.docker.com/compose/how-tos/project-name/ 、https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository 、https://docs.gitea.com/usage/repo-mirror 、https://keepachangelog.com/

## 6. 执行步骤

### Step 1 · 干净环境演练（只看 README，开始计时）

```bash
mkdir -p ~/tmp/wp-clean && cd ~/tmp/wp-clean
START=$(date +%s)
git clone https://github.com/<you>/workpilot.git && cd workpilot
cp .env.example .env
# 仅按 .env.example 的注释填写（LLM key、MinIO 账号等）；不要复制 ~/lab/workpilot/.env
make up PROJECT=wpclean            # 独立的容器 / 卷前缀 wpclean_*
make ps PROJECT=wpclean
make seed                          # 导入 data/sample
curl -sN -X POST localhost:8080/v1/kb/ask/stream -H 'Content-Type: application/json' \
  -d '{"question":"<样例文档中的独有问题>"}' | grep -m1 'event: retrieved'
echo "elapsed: $(( ($(date +%s) - START) / 60 )) min"
```

再用浏览器 http://localhost:8080 完整走一遍：上传 → 问答带引用 → 库外拒答 → 👎。

注意与记录：

- 本机已缓存基础镜像、Ollama 已有 bge-m3，所以耗时会比「全新机器」短；在记录中注明，并估算全新机器额外耗时（镜像拉取 + `ollama pull bge-m3`）。
- 若想去掉 Ollama 依赖：在 `.env` 中把 Embedding 指向 SiliconFlow（同模型），验证 README 中这条替代路径也可用。
- 每遇到一次「README 没写清楚、我凭记忆解决了」，都算一个问题，记入 draft.md。

### Step 2 · 修复演练暴露的问题

只改文档 / Makefile / `.env.example`（不加功能），在 `~/lab/workpilot` 修改后提交：

```bash
cd ~/lab/workpilot
git commit -am "docs: fix quickstart issues found in clean-environment drill" && git push && git push github main
```

### Step 3 · phase_01 §8 逐项验收（写入 phase01-review.md 第 1 节）

| #   | 验收项                                           | 结论        | 证据                                                   |
| --- | ------------------------------------------------ | ----------- | ------------------------------------------------------ |
| 1   | 干净环境 30 分钟内恢复并运行 v0.5                | PASS / FAIL | 今日计时 \_\_\_\_ 分钟                                 |
| 2   | 公网可访问，上传 → 带引用问答 → 反馈 全流程      |             | `https://wp.<域名>`（Day28）+ 今日复测                 |
| 3   | 50 题评测报告，hit@5 / 引用正确率 / 拒答率有基线 |             | `eval/reports/<文件>.md`                               |
| 4   | Badcase ≥ 10 条，带分类和处理结论                |             | `eval/badcases/badcases.md`（\_\_\_\_ 条）             |
| 5   | DA-01 定义文档已写，PROJECT_CONFIG 已回填        |             | `docs/product/da01-definition.md`                      |
| 6   | P1 作品集：README + 架构图 + Demo + 8 问         |             | README / `docs/architecture.md` / `demo.gif` / `p1.md` |
| 7   | 能力矩阵 ≥ 12 项 JD 能力并标出证明模块           |             | `career/capability-matrix.md`                          |
| 8   | 能 3 分钟讲清 P1                                 |             | 今日录音时长 \_\_\_\_                                  |

附加（非核心，可 CONDITIONAL）：CI 绿（Day29）、云端恢复演练 RTO（Day29）、Playwright E2E（Day25）、P95 / 单次成本实测（README 中是否还有「待测」）。

判定规则：8 项核心全部 PASS → 进入 phase_02；附加项 CONDITIONAL 的，写明「W9 Day34 前 30 分钟补齐」；任一核心项 FAIL → 不打 `v0.5.0`，W9 第一天先补该项（记录到 `plan/CHANGELOG.md`）。

### Step 4 · Release notes + tag

`docs/releases/v0.5.0.md`：

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
git add docs/releases/v0.5.0.md && git commit -m "docs: release notes for v0.5.0" && git push
git tag -a v0.5.0 -m "v0.5.0: P1 WorkPilot Knowledge"
git push origin v0.5.0 && git push github v0.5.0      # Day32 若用了快照分支：在 public-main 上打 tag 并推 github
```

GitHub → Releases → Draft a new release → 选 `v0.5.0` → 粘贴 Release notes → 附上 `demo.gif` 链接 → Publish。Gitea 同样在「版本发布」中创建。

### Step 5 · 阶段复盘（~/lab/projects/product-lab/reviews/phase01-review.md）

```markdown
# Phase 01 复盘（W1–W8 · 09-28 → 11-19）

## 1. 验收结果 （Step 3 表格）

## 2. 指标 vs 目标 （DA01 §11：hit@5 / 引用正确率 / 拒答率 / P95 / 成本 / 恢复时间）

## 3. 投入 实际总时长 \_**\_ h（计划 33 天 × 1–2h）；超时的天：\_\_**

## 4. 花费 LLM ¥** · Embedding ¥** · 云 ¥** · 域名 ¥**（预算 ≤ ¥1100 / 半年）

## 5. 做对了什么 （3 条）

## 6. 做错 / 返工 （3 条，带根因）

## 7. 无效学习 / 范围扩张（有则列出与浪费时长）

## 8. 真实使用 自己用 WorkPilot 的次数（脱敏语料）：\_\_\_\_

## 9. 对 phase_02 的调整（CONDITIONAL 补齐计划、需要改的节奏或范围）
```

同时填写 `plan/phase_01/week_08/README.md` 第 11 节周复盘。

### Step 6 · 状态切换 + 讲解录音 + 收尾

1. 更新 `Infinity_AI_Project/PROJECT_CONFIG.md`「当前状态」：当前阶段 → 阶段二 · Agent 与 P2（第 9–16 周）；当前周 → 第 9 周；DA-01 状态 → 「v0.5.0 P1 已发布（GitHub 链接），下一步 M6 Tool Layer」。若因 FAIL 调整了计划，同步写入 `plan/CHANGELOG.md`。
2. 按 Day31 讲稿脱稿讲一遍，用 QuickTime「新建音频录制」或手机录音，回听一次，把卡壳点记下（W25 面试准备素材）。
3. 清理干净环境（确认是 `wpclean` 前缀后再删）：

```bash
cd ~/tmp/wp-clean/workpilot && make down PROJECT=wpclean
docker volume ls --filter name=wpclean_ -q            # 先看清要删哪些
docker volume rm $(docker volume ls --filter name=wpclean_ -q)
cd ~/lab/workpilot && make up                          # 恢复日常环境
cd ~/lab/projects && git add product-lab/reviews && git commit -m "docs: phase 01 review" && git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么干净环境演练要用 `-p wpclean` 而不是直接 `make up`？（答：compose 项目名相同会复用原来的数据卷，等于没有「干净」；独立项目名得到全新的卷和网络）
2. 干净环境耗时主要花在哪里？如何缩短？（答：镜像拉取 / 构建、依赖安装、embedding 模型下载、语料导入；可预构建镜像推 Registry、用 API embedding、提供 seed 脚本）
3. 核心项 FAIL 时为什么不打 v0.5.0？（答：版本号代表可演示状态的承诺；打了不达标的 tag 会让作品集与实际不符）
4. 复盘为什么要写「无效学习 / 范围扩张」？（答：GLOBAL_CONTEXT 防偏航要求；phase_02 的 Agent 生态更容易诱发跑偏，需要提前识别自己的模式）

## 8. 对 DA-01 的贡献

DA-01 第一个里程碑完成：WorkPilot 从空仓库到 **v0.5 P1**——已部署、已评测、可演示、可复现、已开源。phase_02 将直接复用 `app/llm`（Agent 的模型层）、`app/rag`（变为 `kb_search` 工具）、`eval/`（扩展为 Agent 评测）、`apps/web`（加 Agent 时间线）、`deploy/`（继续部署 v1.0）。

## 9. 求职映射（D 线）

- 岗位能力：端到端交付、可复现性、阶段复盘与自我管理
- 对应岗位：AI Engineer / GenAI Application Engineer / AI Full-Stack
- 简历 bullet 草稿：独立完成 RAG 知识助手从 0 到公开发布（8 周、约 ** 小时），开源仓库支持 clone 后 ** 分钟内一键启动（干净环境实测），核心指标 hit@5 ** / 引用正确率 ** / 拒答率 \_\_。
- 面试可能问：
  - 「如果让别人接手你的项目，需要多久能跑起来？」要点：README 3 条命令 + `.env.example` 注释 + 干净环境实测 \_\_ 分钟 + runbook。
  - 「这个项目你最想改进的是什么？」要点：从 Release notes「已知问题」挑一条：问题 → 影响 → 计划（例如认证与多空间在 W19、队列化导入）。

## 10. 卡住时的处理

| 现象                                                      | 处理                                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | 原环境未停：`cd ~/lab/workpilot && make down`；或临时改端口并在记录中注明            |
| 干净环境 api 启动即退出（缺变量）                         | 说明 `.env.example` 漏了键或注释不清：这是要修的文档问题，修完重新计时               |
| clone 后 `make seed` 找不到 `data/sample`                 | `.gitignore` 规则把样例忽略了（Day26 Step 6）：修 `.gitignore` 并补提交样例          |
| 演练超过 30 分钟                                          | 不作弊；记录真实时间与主要耗时环节，判 FAIL / CONDITIONAL，W9 第一天针对性改进后复测 |
| GitHub tag 推送被拒（已存在）                             | 之前推过同名 tag：确认指向的提交；不要强推覆盖已公开的 tag，改发 `v0.5.1`            |
| 复盘写不出来                                              | 先按 9 个标题各写一句话，再补数字；数字从 draft.md 和 Day 产出记录中抄               |

## 11. 产出记录（执行时填写）

- 干净环境计时：\_**\_ 分钟（其中镜像构建 \_\_** 分钟）
- 演练发现的问题数 / 已修复数：\_**\_ / \_\_**
- §8 结果：PASS ** / CONDITIONAL ** / FAIL \_\_
- v0.5.0 commit：\_\_\_\_
- 录音时长：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE → Week 8 DONE → **Phase 1 DONE（v0.5 P1 发布）** → 下一次进入 Day34（Phase 2 · Week 09 Task 1：Tool Calling 原理 + Registry，M6.1）。任一核心项未通过 → 保持 IN PROGRESS，Day34 先补该项，再开始 Tool Calling。
