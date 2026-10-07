# Day 56 · 2027-01-12 · Week 16 Task 2：Demo + 技术文章 + 产品页 / 开源边界

## 0. 今天只做一件事

让 v1.0 被「看见」：录 2–3 分钟 Demo 视频、发布 1 篇 2000–3000 字技术文章、定稿开源边界 `docs/product/open-core.md`、在 README 顶部（或 GitHub Pages）放一个简单产品页；发布前 gitleaks + 敏感词再扫一次。

不碰：Pro Kit 打包与收费（W22）、社群推广与私聊、视频精剪/配乐、新功能。

## 1. 资产锚点

- 构建模块：M12.1 开源核心 + 文档、M12.3 产品页 + SEO 技术文章（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：v1.0（P2 发布的对外部分）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：1 个可分享的 Demo 视频链接、1 篇公开技术文章、1 个产品页（含 Pro Kit 即将推出 + Discussions 兴趣帖）；之后可被动观察 Star / 阅读 / 兴趣留言数
- 今日 AI 实际应用：用 AI 起草文章与产品文案，自己负责技术判断、数字核对与合规审查

## 2. 起点（前置确认）

- 已有：Day55 README P2 章节、`docs/portfolio/p2.md`、v1.0 评测报告、截图；W13 MCP 录屏；W10 起草过的 `docs/product/` 文档（若有 open-core 草稿）
- 需确认：

```bash
cd ~/lab/workpilot
git tag | grep v1.0.0 && curl -s https://<你的域名>/health
ls docs/product/ docs/assets/
which gitleaks && gitleaks version
ls ~/.private/sensitive-words.txt 2>/dev/null || echo "需要创建本地敏感词表（不入库）"
```

- 本地敏感词表 `~/.private/sensitive-words.txt`：公司名/简称、内部系统名、同事姓名、内网域名，一行一个（**不提交到任何仓库**）。

## 3. 验收对齐（做完要能勾掉）

- [ ] Demo 视频 2–3 分钟，含三个场景：研究任务 + 审批、VS Code 中 MCP 调用、Trace 页（+ Ops 一瞥）；已上传，README 有链接
- [ ] 技术文章 2000–3000 字，含架构图与评测数字，已发布到个人博客 / 掘金，文末链接 GitHub
- [ ] `docs/product/open-core.md` 定稿：功能边界表（免费 vs Pro Kit）、许可、定价区间、边界原则
- [ ] README 顶部产品区块（定位、3 个卖点、截图、快速开始、Pro Kit 即将推出 → Star / Discussions）；GitHub Discussions 已开启并有「Pro Kit 兴趣」帖
- [ ] `gitleaks` 历史 + 工作区扫描 0 告警；敏感词 grep 无命中（仓库、文章、视频画面）
- [ ] 已提交并 push 到 Gitea 与 GitHub

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                                                      |
| ----------- | ------ | ------------------------------------------------------------------------- |
| 0–30 min    | P0     | Demo 脚本（5 分钟）+ 录制 2 遍 + 上传                                     |
| 30–75 min   | P0/P1  | 文章：大纲（自己）→ AI 起草 → 改写关键段与数字 → 发布（P1：可先发精简版） |
| 75–95 min   | P0     | `open-core.md` 定稿                                                       |
| 95–108 min  | P0     | README 顶部产品区块 + Discussions                                         |
| 108–120 min | P0     | gitleaks + 敏感词检查 + 提交                                              |

时间不足时最低保留：视频 + `open-core.md` + gitleaks；文章先发 1500 字精简版（W17 补全），GitHub Pages 不做。

## 5. 今日学习（只学完成任务必须的）

- **Demo 原则**：先展示结果再讲原理；每个场景一句话说明「解决了什么」；全程用公开语料。
- **Open Core 边界原则**：免费版必须「单人完整可用」（否则没人试用）；付费部分卖「团队生产化节省的时间」（部署包、认证、场景包、评测模板、手册），而不是锁住核心能力。
- **被动收集兴趣**：Star、Discussions 留言、文章阅读数就是信号；不私聊、不拉群。
- **发布前合规**：gitleaks 查密钥，敏感词表查公司信息，两者都要覆盖 Git 历史与工作区。
- 资料：https://github.com/gitleaks/gitleaks （用法）、https://genai.owasp.org/ （文章中安全部分的引用）

## 6. 执行步骤

### Step 1 · Demo 视频（macOS `Cmd+Shift+5`，可无配音、加字幕）

| 时间      | 画面                                                                                                                                                                          | 字幕要点                               |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 0:00–0:15 | README 首屏                                                                                                                                                                   | WorkPilot：可私有部署的研发 Agent 平台 |
| 0:15–1:15 | Web AgentPage：输入「调研 Qdrant 混合检索并给出是否默认开启的建议，再在沙盒仓库创建跟进 Issue」→ 时间线（plan → kb_search → web_search → 报告）→ 审批卡片 → 批准 → Issue 链接 | 写操作必须人工审批                     |
| 1:15–1:50 | VS Code Copilot Agent 模式：「用 workpilot 查我们的分支规范并总结」→ 工具调用 → 带引用回答                                                                                    | MCP：在 IDE 里直接用团队知识           |
| 1:50–2:25 | 刚才那次 Agent 运行的 Trace 瀑布图 → 点 llm span 看 tokens/成本 → Ops 看板                                                                                                    | 每次请求可追踪，成本有预算             |
| 2:25–2:45 | 评测表 + GitHub 链接                                                                                                                                                          | 30 任务成功率 \_\_，CI 回归门禁        |

上传到 B 站或 YouTube（标题与简介只写项目说明 + GitHub 链接，不做推广），README 与文章引用链接。

### Step 2 · 技术文章（大纲自己写，正文 AI 起草后改）

标题候选：《从 RAG 到可审批的研发 Agent：WorkPilot 的评测驱动实践》

| 节                      | 字数 | 内容（必须有自己的判断与数字）                                         |
| ----------------------- | ---- | ---------------------------------------------------------------------- |
| 1. 背景：知识助手不够用 | 250  | 哪些研发工作流需要「会做事」                                           |
| 2. 架构总览             | 350  | 架构图 v1 + LangGraph 图；为什么从手写循环迁到 LangGraph               |
| 3. 工具层与 MCP         | 450  | 权限等级、description 设计、MCP 适配层、只读默认                       |
| 4. Human-in-the-loop    | 350  | interrupt/resume、为什么写操作不暴露给 MCP                             |
| 5. 评测驱动             | 600  | 30 任务设计、指标口径、judge 校准、失败分类、一次修复前后对比、CI 门禁 |
| 6. 生产化               | 450  | Trace、成本账本与预算、限流、Guardrail v0（间接注入）                  |
| 7. 踩坑与取舍           | 300  | 3 个真实坑（如 stdio stdout 污染、函数名不能含点、SSE 下 trace flush） |
| 8. 总结与下一步         | 150  | v2.0 计划；GitHub 链接                                                 |

发布：个人博客 + 掘金（只发布）。发布前用敏感词表 `grep -nif ~/.private/sensitive-words.txt article.md` 检查。文章源文件保存到 `~/lab/projects/career/articles/2026-11-workpilot-p2.md`。

### Step 3 · `docs/product/open-core.md` 定稿

```markdown
# WorkPilot 开源边界（Open Core）· 定稿 2027-01-12

## 原则

1. 开源核心（MIT）对个人开发者「单人完整可用」：RAG、Agent、HITL、MCP、评测、Trace 全部免费。
2. Pro Kit 卖的是「团队生产化节省的时间」，不锁核心能力。
3. 不做定制外包；Pro Kit 为标准化一次性买断。

## 功能边界

| 能力                             | 开源核心（MIT）                   | Pro Kit                                                            |
| -------------------------------- | --------------------------------- | ------------------------------------------------------------------ |
| LLM Gateway / RAG / Agent / HITL | ✔                                 | ✔                                                                  |
| MCP Server / Client              | ✔                                 | ✔                                                                  |
| 评测 runner + 示例数据集         | ✔                                 | ✔ + 场景评测模板与 rubric 库                                       |
| Trace / 成本 / 预算 / Ops 看板   | ✔                                 | ✔                                                                  |
| 部署                             | docker compose（dev + 基础 prod） | 生产部署包：Postgres、登录/RBAC、多空间、Caddy HTTPS、备份恢复脚本 |
| 场景包                           | SP-A 知识问答                     | 主场景包（P3 选定）+ 后续场景包                                    |
| 文档                             | README / runbook                  | 部署手册、运维手册、安全加固清单                                   |
| 更新                             | 社区                              | 6 个月更新                                                         |

## 定价（W22 发布时最终确认）

- 早鸟 ¥199 / 标准 ¥399（区间 ¥199–499），渠道：面包多 / Gumroad / 爱发电（三选一，W22 定）

## 当前状态

- Pro Kit：即将推出（W22）。兴趣收集：GitHub Star + Discussions「Pro Kit 兴趣」帖，不私聊。
```

### Step 4 · README 顶部产品区块（P2：GitHub Pages）

```markdown
# WorkPilot

**可私有部署的研发工作 AI 助手：带引用的知识问答 + 可审批的 Agent + IDE 内 MCP 调用 + 自带评测与可观测。**

- 🔎 带引用回答团队文档与仓库问题，知识不足会拒答
- 🤖 Agent 调研、拆任务、建 Issue —— 写操作必须人工审批
- 🧩 VS Code / Cursor / Claude Desktop 通过 MCP 直接调用
  （截图 + Demo 视频链接 + 快速开始 3 行命令）

> **Pro Kit（团队生产部署包）即将推出** —— 感兴趣请 Star 本仓库，或在 Discussions「Pro Kit 兴趣」帖留言你的使用场景。
```

（emoji 可按个人喜好删除。）GitHub 仓库 → Settings → Features → 勾选 Discussions → 新建分类帖「Pro Kit 兴趣」：说明计划内容与预计时间，邀请留言场景（不收集手机号/微信）。

P2：`docs/site/index.html` 单页（同样内容），Settings → Pages → Deploy from branch `main` `/docs`，访问 `https://<用户名>.github.io/workpilot/site/`。

### Step 5 · 发布前合规检查 + 提交

```bash
cd ~/lab/workpilot
gitleaks git -v . || gitleaks detect -v                # 历史提交（旧版本命令二选一）
gitleaks dir -v . || gitleaks detect --no-git -v       # 工作区
grep -rnif ~/.private/sensitive-words.txt --exclude-dir={.git,node_modules,.venv,data} . && echo "!! 命中敏感词" || echo "OK"
git add README.md docs/product/open-core.md        # 做了 GitHub Pages 再加 docs/site
git commit -m "docs(product): finalize open-core boundary, product section, demo and article links"
git push origin main && git push github main
```

视频画面也要检查：终端里是否露出 token、浏览器书签栏/标签页是否有公司系统。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 MCP 和 Trace 放在免费版？（答：它们是吸引个人开发者试用与 Star 的核心卖点，锁住会失去流量入口；付费卖团队生产化）
2. 开源核心用 MIT 有什么风险？怎么接受？（答：他人可商用/二次分发；目标是作品集与流量，Pro Kit 的价值在部署包、场景包、手册与更新，不依赖代码保密）
3. 产品页为什么不放联系方式拉私聊？（答：遵守「被动、标准化、不私聊拓客」约束；Star/Discussions 已足够验证兴趣）
4. gitleaks 为什么要扫历史？（答：密钥一旦进过提交历史，即使后来删除，公开仓库仍可从历史中取出）
5. 一篇技术文章同时承担哪三个作用？（答：作品集证据、SEO 被动流量、对外表达与面试谈资）

## 8. 对 DA-01 的贡献

DA-01 的 A 线第一次有了对外入口：开源边界明确了「什么免费、什么付费」（W22 Pro Kit 直接按此打包），产品页 + Discussions 开始被动收集真实兴趣信号，视频与文章让 v1.0 的价值可以在 3 分钟内被理解；合规检查确保 §8 红线在公开发布时被遵守。

## 9. 求职映射（D 线）

- 岗位能力：技术写作、产品化表达、开源发布、合规意识
- 对应岗位：AI Full-Stack Engineer / AI Agent Engineer（加分项：技术影响力）
- 简历 bullet 草稿：发布 WorkPilot 开源核心（MIT）与技术文章《**》（阅读 **、Star \_\_），制定 Open Core / Pro Kit 产品边界与定价方案。
- 面试可能问：
  - 你的开源项目有用户吗？（要点：如实给 Star/阅读/Discussions 数据；强调自用频次与评测数据；说明被动增长策略）
  - 如果要商业化，你怎么划分免费与付费？（要点：单人完整可用 vs 团队生产化；卖时间不卖锁；标准化不定制）

## 10. 卡住时的处理

| 现象                                    | 处理                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------- |
| 录屏中 Agent 运行太慢                   | 先跑一遍预热（缓存/模型加载），录制时剪掉等待段或加「加速」字幕                    |
| 审批演示写到了真实仓库                  | 立即确认 `write_repo_allowlist` 只含沙盒仓库；删除该 Issue 并重录                  |
| 文章写不满 2000 字                      | 用 `p2.md` 的 10 小节扩写，每节补一个真实例子或数字；不要堆砌概念                  |
| gitleaks 命中测试用假 key（如 sk-abc…） | 确认是假数据后加入 `.gitleaksignore`（按 fingerprint），并在测试中改成明显的假格式 |
| 敏感词命中                              | 逐条修改或删除；若在已推送的历史中，先私有化仓库再评估清理（单独确认后执行）       |
| 掘金审核未通过 / 延迟                   | 先发个人博客，掘金次日再试；README 先链接博客                                      |

## 11. 产出记录（执行时填写）

- 视频链接 / 时长：\_\_\_\_
- 文章标题 / 字数 / 链接：\_\_\_\_
- 定价区间与渠道候选：\_\_\_\_
- Discussions 帖链接：\_\_\_\_
- gitleaks / 敏感词检查结果：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day57（W16 Task 3：简历 v1 + 面试题 + Phase 2 复盘）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
