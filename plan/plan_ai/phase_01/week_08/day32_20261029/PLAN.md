# Day 32 · 2026-10-29 · Week 08 Task 3：GitHub 公开 + 简历条目 + 面试 10 题

## 0. 今天只做一件事

通过敏感信息检查后把 WorkPilot 公开到 GitHub（MIT），并把 P1 转化为求职材料：简历 bullets、10 道 RAG 面试题（答案链接到 WorkPilot 证据）、能力矩阵证据列。

不碰：GitHub Actions 迁移、Portfolio 网站（W23）、投递简历（W24）、宣传推广（违反「仅被动沟通」约束）。

## 1. 资产锚点

- 构建模块：M12.1 开源核心（GitHub 公共仓库）、M13.3 简历（AI Full-Stack 草稿）、M13.4 面试题库（第一批 10 题）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：公开链接 `https://github.com/<you>/workpilot`；gitleaks 扫描 0 发现的记录；简历中可引用的 P1 条目
- 今日 AI 实际应用：把 RAG / 评测 / LLM 工程能力映射为 JD 语言；用 Copilot 起草面试答案，但每个答案必须指向自己系统里的证据

## 2. 起点（前置确认）

- 已有：README / 架构 / ADR / Demo / p1.md；`~/lab/projects/career/capability-matrix.md`（W2）。
- 需确认：

```bash
brew install gitleaks && gitleaks version
cd ~/lab/workpilot && git status && git log --oneline | wc -l
ssh -T git@github.com            # 显示 "Hi <you>!"；不通可改用 HTTPS + 代理
mkdir -p ~/lab/.private && touch ~/lab/.private/sensitive-words.txt   # 不在任何仓库内
```

在 `~/lab/.private/sensitive-words.txt` 每行写一个敏感词：公司中英文名、产品代号、同事姓名、内网域名、工号（例如本机用户名 `226838` 若是工号也要写进去）。

## 3. 验收对齐（做完要能勾掉）

- [ ] `gitleaks git --redact -v .`（含全部历史）结果 `no leaks found`，或误报已写入 `.gitleaksignore` 并逐条说明
- [ ] 敏感词 grep（全部历史）0 命中；`/Users/<用户名>` 路径 0 命中
- [ ] `.env`、`data/corpus/`、`*.db` 从未出现在任何提交中
- [ ] 提交作者邮箱不是公司邮箱（或已决定处理方式并记录）
- [ ] GitHub 公共仓库可访问：README、Demo GIF、mermaid 正常显示；`main` 与全部 tag 已推送；LICENSE 为 MIT
- [ ] `career/resume/ai-fullstack-draft.md` 含 ≥ 3 条带数字的 P1 bullets
- [ ] `career/interview-questions.md` 含 10 道 RAG 题，每题有要点 + WorkPilot 证据链接
- [ ] 能力矩阵 ≥ 12 项填写「由 WorkPilot 哪个模块证明」；projects 仓库已提交

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                |
| ------- | ------ | --------------------------------------------------- |
| 0–30    | P0     | gitleaks + 敏感词 + 历史文件 + 作者邮箱 四项检查    |
| 30–45   | P0     | LICENSE + GitHub 建仓 + 推送 main / tags + 页面检查 |
| 45–65   | P0     | 简历 P1 bullets                                     |
| 65–105  | P0     | 面试 10 题                                          |
| 105–115 | P0     | 能力矩阵证据列 + 提交                               |
| 115–120 | P2     | Gitea 推送镜像到 GitHub（之后自动同步）             |

时间不足时最低保留：四项检查 + GitHub 公开；面试题可先 5 道（W9 补齐）。

**检查发现问题时，立即停止公开流程**，按 Step 2 决策处理，今天剩余时间改做简历和题库。

## 5. 今日学习（只学完成任务必须的）

- gitleaks 用规则 + 熵检测扫描密钥；`gitleaks git` 扫描提交历史，`gitleaks dir` 扫描当前文件（旧版命令为 `gitleaks detect`）。
- 一旦密钥进入过 Git 历史，**删除文件不等于删除密钥**；正确处理是先轮换密钥，再决定是否改写历史。
- 改写历史（`git filter-repo`）会改变所有提交哈希，是破坏性操作；只对未公开的仓库、在全新镜像克隆上做。
- 资料：https://github.com/gitleaks/gitleaks 、https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning 、https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository 、https://choosealicense.com/licenses/mit/ 、https://docs.gitea.com/usage/repo-mirror

## 6. 执行步骤

### Step 1 · 发布前四项检查（全部在 ~/lab/workpilot 执行）

```bash
# ① 密钥扫描：全部提交历史 + 当前工作区（--redact 防止密钥打印到终端）
gitleaks git --redact -v .        || true     # 旧版本：gitleaks detect --source . --redact -v
gitleaks dir --redact -v . 2>&1 | grep -v '/.env' | tail -20   # 本地 .env 被扫到属预期（它不在 Git 中）

# ② 敏感词 + 本机路径（全部历史）
git grep -n -i -F -f ~/lab/.private/sensitive-words.txt $(git rev-list --all) | head
git grep -nE '/Users/[A-Za-z0-9_]+' $(git rev-list --all) | head

# ③ 不该入库的文件是否出现过
git rev-list --all --objects | grep -E '(^| )\.env$|data/corpus/|\.db$' | head
git log --all --oneline -- .env 'data/corpus' '*.db' | head

# ④ 提交作者
git log --all --format='%an <%ae>' | sort -u
```

逐项把结果写进 draft.md（「0 命中」也要记录）。

### Step 2 · 发现问题时的决策（不要自动执行，先停下确认）

| 发现                                    | 处理                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 真实 API key 出现在历史中               | **先在供应商后台作废并重新生成该 key**（无论后续是否改写历史，旧 key 都视为已泄露）                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 敏感文件 / 词出现在历史中，仓库尚未公开 | 方案 A（推荐、非破坏性）：Gitea 私有仓库保留完整历史；对外只推送一个**无历史的快照分支**：`git checkout --orphan public-main && git add -A && git commit -m "chore: initial public release (v0.5 snapshot)"`，检查后 `git push github public-main:main`（**不要推送旧 tag**，它们指向含敏感内容的历史；Day33 在快照上重新打 `v0.5.0`）。方案 B（破坏性）：在 `git clone --mirror` 出的新副本上执行 `git filter-repo --path .env --path data/corpus --invert-paths`，会改写全部提交哈希、使旧 tag 失效——**执行前必须备份并确认**，只在完全理解影响后进行 |
| 工作区文件含敏感词（未在历史）          | 修改文件 → 提交 → 重新检查                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 作者邮箱是公司邮箱                      | 今后 `git config user.email` 改为个人邮箱；历史可接受方案 A 的快照分支处理                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| gitleaks 误报（如测试里的假 key）       | 加入 `.gitleaksignore`（填报告中的 Fingerprint）并在提交说明里写原因                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

### Step 3 · LICENSE + GitHub 公开

```bash
cat > LICENSE <<'EOF'
MIT License

Copyright (c) 2026 <你的名字或笔名>

Permission is hereby granted, free of charge, ...（从 https://choosealicense.com/licenses/mit/ 复制全文）
EOF
git add LICENSE && git commit -m "chore: add MIT license" && git push
```

GitHub 网页：New repository → 名称 `workpilot` → **Public** → 不勾选 README / .gitignore / License（保持空仓库）→ 创建。

```bash
git remote add github git@github.com:<you>/workpilot.git
git push github main && git push github --tags
# 若 SSH 不通：git remote set-url github https://github.com/<you>/workpilot.git
#            git -c http.proxy=http://127.0.0.1:7890 push github main --tags
```

GitHub 页面检查：README 渲染、GIF 播放、mermaid 渲染、Tags 页面、About 填一句话描述 + topics（`rag` `fastapi` `react` `qdrant` `llm`）；Settings → Code security 确认 Secret scanning / Push protection 已开启。

P2：Gitea 仓库设置 → 镜像设置 → 推送镜像，填 GitHub 仓库 HTTPS 地址 + fine-grained token（仅该仓库 Contents 读写），勾选「推送时同步」。

### Step 4 · 简历 P1 bullets（~/lab/projects/career/resume/ai-fullstack-draft.md）

格式：动词开头 + 做了什么 + 用什么 + 量化结果；每条 1–2 行。数字从 p1.md 抄，不估。

```markdown
## 项目：WorkPilot Knowledge — 研发知识 RAG 助手（个人项目，开源） github.com/<you>/workpilot

- 设计并实现无框架 RAG 链路（FastAPI + Qdrant + bge-m3 + DeepSeek），支持段落级引用与阈值拒答；50 题评测 hit@5 **、引用正确率 **、库外拒答率 \_\_。
- 构建评测体系（hit@k / MRR / LLM-as-judge）与 badcase 分类，经 chunk / hybrid / query rewrite 实验将 hit@5 从 ** 提升至 **；接入线上 👎 反馈自动导出回归候选。
- 基于 React 18 + TypeScript 实现流式问答 Console（fetch 解析 SSE、引用溯源面板、会话历史、知识库管理），首字延迟 \_\_s。
- 以 Docker 多阶段 + Compose + Caddy 部署至云服务器（HTTPS、request_id 日志、健康检查），Gitea Actions CI，备份恢复 RTO ** 分钟；单次问答成本 ¥**。
```

### Step 5 · 面试 10 题（~/lab/projects/career/interview-questions.md）

每题格式：`### Qn 问题` → 3–5 条要点 → `证据：` WorkPilot 链接（GitHub 文件 URL）。

| #   | 题目                                                 | 证据指向                                  |
| --- | ---------------------------------------------------- | ----------------------------------------- |
| 1   | 讲一下 RAG 的完整流程和你项目的架构                  | `docs/architecture.md` sequenceDiagram    |
| 2   | chunk size / overlap 怎么定？按结构切还是定长？      | W5 实验报告、`app/rag/chunking.py`        |
| 3   | 为什么要 hybrid search？稀疏和稠密各擅长什么？       | W5 实验对比表                             |
| 4   | 如何评估检索质量？hit@k 和 MRR 的区别？              | `eval/run_rag_eval.py`、报告              |
| 5   | LLM-as-judge 有什么偏差？怎么校准？                  | `eval/judge.py`、人工抽检记录             |
| 6   | 如何降低幻觉？拒答阈值怎么定？                       | `prompts/qa_answer.v*.md`、拒答率数据     |
| 7   | 引用是怎么实现的？怎么保证引用对得上？               | `app/rag/answer.py`、`AnswerMarkdown.tsx` |
| 8   | 为什么选 bge-m3？开发和生产 embedding 如何保持一致？ | ADR、Day28                                |
| 9   | 流式输出前后端怎么实现？代理层要注意什么？           | `useStreamingAnswer.ts`、`Caddyfile`      |
| 10  | 如何控制成本和延迟？                                 | `app/llm/pricing.py`、P95 / 成本数据      |

答案先让 Copilot 根据 p1.md 生成草稿，你用自己的话改写到能脱稿说出。

### Step 6 · 能力矩阵 + 提交

`career/capability-matrix.md` 的「证据」列：对照 DA01 §1.1 表，把已完成项填为具体链接（如「RAG → github.com/<you>/workpilot/tree/main/apps/api/app/rag」），未完成项标注计划周（W9+）。

```bash
cd ~/lab/projects
git add career/
git commit -m "docs(career): P1 resume bullets, 10 RAG interview questions, matrix evidence"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 密钥进过 Git 历史后，删除文件再提交够不够？（答：不够，历史中仍可取出；必须轮换密钥，必要时改写历史或只发布无历史快照）
2. 为什么推荐「无历史快照分支」而不是直接 filter-repo？（答：非破坏性，私有仓库完整历史不受影响；filter-repo 改写所有哈希、tag 失效，出错难恢复）
3. 为什么敏感词表放在仓库之外？（答：把公司名写进仓库里的检查脚本本身就是泄露）
4. MIT 许可对你意味着什么？（答：任何人可使用 / 修改 / 商用，只需保留版权声明；与 Pro Kit 付费不冲突——付费卖的是部署包、场景包和更新服务）
5. 简历 bullet 为什么必须带数字？（答：数字可验证、可比较，体现结果导向；没有数字的 bullet 无法与其他候选人区分）

## 8. 对 DA-01 的贡献

DA-01 第一次对外可见：M12.1 开源核心建立，后续 P2 / P3 在同一仓库持续演进，Star / 下载即 §10 商业化验证的被动流量入口；D 线第一次有了「可链接的证据」，简历和面试不再空讲。

## 9. 求职映射（D 线）

- 岗位能力：开源发布、安全合规意识、项目包装与表达
- 对应岗位：AI Engineer / AI Full-Stack / GenAI Application Engineer
- 简历 bullet 草稿：见 Step 4（P1 共 4 条）。
- 面试可能问：
  - 「你的项目怎么保证不泄露敏感数据？」要点：合规红线（公司数据不进外部 LLM、不进公开仓库）、语料只用公开 / 脱敏样例、发布前 gitleaks + 敏感词 + 历史检查、密钥 SecretStr 与 600 权限。
  - 「这是个人项目，你怎么证明它是可用的？」要点：公开仓库 + Demo + 评测报告 + 干净环境 30 分钟恢复（Day33）+ 自己真实使用记录。

## 10. 卡住时的处理

| 现象                                                             | 处理                                                                                |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------- |
| `gitleaks: unknown command "git"`                                | 版本较旧：改用 `gitleaks detect --source . --redact -v`；或 `brew upgrade gitleaks` |
| gitleaks 报大量 `generic-api-key` 指向 eval 报告 / lock 文件     | 先逐条确认是否真实密钥；确认误报后加入 `.gitleaksignore`                            |
| `git grep ... $(git rev-list --all)` 报 `Argument list too long` | 提交太多：改为 `git rev-list --all                                                  | xargs -n 50 git grep -n -i -F -f <词表>` |
| `ssh -T git@github.com` 超时                                     | 改 HTTPS + 代理推送；或在 `~/.ssh/config` 用 `Hostname ssh.github.com` + `Port 443` |
| GitHub 拒绝推送 `GH013: Repository rule violations ... secret`   | Push protection 检测到密钥：**不要绕过**，回到 Step 2 处理并轮换该密钥              |
| GitHub 上 GIF 不显示                                             | 路径大小写不一致或文件 > 10MB：检查 `docs/assets/demo.gif` 实际文件名               |

## 11. 产出记录（执行时填写）

- 四项检查结果（gitleaks / 敏感词 / 历史文件 / 作者邮箱）：\_\_\_\_
- 是否采用快照分支或改写历史：\_**\_（原因：\_\_**）
- GitHub 链接：\_\_\_\_
- 简历 bullets 条数 / 面试题完成数：\_**\_ / \_\_**
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 3 DONE → 明天进入 Day33（8 周总验收 + 干净环境恢复 + v0.5.0）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（检查未通过时禁止公开，Day33 的干净环境演练改为从 Gitea clone）。
