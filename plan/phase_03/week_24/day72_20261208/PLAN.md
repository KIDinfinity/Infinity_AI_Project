# Day 72 · 2026-12-08 · Week 24 Task 1：三版简历

## 0. 今天只做一件事

建立简历的单一事实来源 `career/resume/facts.md`，基于它写出 Frontend / AI Full-Stack / AI Engineer 三版 1 页简历，经 LLM 招聘方挑刺修订后导出 PDF。

不碰：投递（Day73）、面试题（W25）、Portfolio 改版（只替换简历文件）、任何 WorkPilot 代码。

## 1. 资产锚点

- 构建模块：M13.3 简历 ×3（见 plan/DA01_TARGET_ASSET.md §5）
- 版本里程碑：—（引用 v0.5 / v1.0 / v2.0 的证据）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：WorkPilot 的评测、安全、耗时、使用数据全部变成可追溯的简历 bullet；每个 bullet 都能在面试中出示报告
- 今日 AI 实际应用：LLM 扮演不同岗位招聘方 / 技术面试官审阅简历（输入只含已公开的项目信息）

## 2. 起点（前置确认）

- 已有：`eval/reports/20261204-eval-v2.md`、`20261203-security-v1.4.md`、`docs/portfolio/p3-notes.md`、usage-stats、Portfolio URL、W16 简历 v1、`career/capability-matrix.md`、`career/jd-tracking.md`。
- 需确认：

```bash
cd ~/lab/projects && git pull && ls career/ career/resume/ 2>/dev/null
which pandoc || brew install pandoc
ls "/Applications/Google Chrome.app" >/dev/null && echo chrome-ok     # 用于 HTML → PDF（避免安装 LaTeX）
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `facts.md` ≥ 15 条事实，每条含：数字、来源（仓库内路径或公开链接）、日期
- [ ] `resume-ai-fullstack.md`、`resume-ai-engineer.md`、`resume-frontend.md` 各 1 页（PDF 预览确认）
- [ ] 每版 ≥ 3 个量化 bullet，所有 bullet 可在 facts.md 找到对应编号（bullet 后注释 `<!-- F07 -->`）
- [ ] 个人项目与公司工作经历分开写；公司经历不含内部系统名与业务数据
- [ ] `review-log.md` 记录 ≥ 1 轮 LLM 挑刺（问题 → 是否采纳 → 修改）
- [ ] 三版 PDF 已导出；Portfolio `/about` 简历已替换为 AI Full-Stack 版

## 4. 时间块（≤ 120 分钟）

| 时间        | 优先级 | 内容                                   |
| ----------- | ------ | -------------------------------------- |
| 0–25 min    | P0     | facts.md（逐个报告抄数字 + 路径）      |
| 25–60 min   | P0     | AI Full-Stack 版（主投）               |
| 60–80 min   | P0     | AI Engineer 版（调整顺序与关键词）     |
| 80–90 min   | P1     | Frontend 版（强调前端 + AI UX）        |
| 90–105 min  | P0     | LLM 招聘方挑刺 → 修订 → review-log     |
| 105–115 min | P0     | 导出 PDF + 替换 Portfolio              |
| 115–120 min | P0     | 提交                                   |
| 顺延        | P2     | 英文 AI Engineer 版 → Day73 空隙或 W25 |

时间不足时最低保留：facts.md + AI Full-Stack 版 + PDF。

## 5. 今日学习（只学完成任务必须的）

- **XYZ 公式**：完成了 X（做了什么），以 Y 衡量（数字），通过 Z（怎么做的）。例：「将攻击用例拦截率从 0.55 提升到 1.0（Y），通过场景×角色工具白名单、SSRF 阻断与输出过滤（Z），完成 RAG+Agent 平台安全加固（X）」。
- **三版差异**：同一事实，按岗位调整「顺序 + 关键词 + 详略」，而不是写不同的事实。
- **可信度**：数字精确到报告值（0.78 而不是「约 80%」）；规模如实（20 条评测集、单机部署、个人项目）；小规模但完整的证据比大而空的描述更可信。
- **1 页原则**：招聘方首轮只看 10–30 秒；顶部放链接（Portfolio / GitHub / Demo）。
- 资料：https://pandoc.org/MANUAL.html

## 6. 执行步骤

### Step 1 · facts.md（P0，自己抄，不让 AI 编）

```markdown
# Facts（简历单一事实来源）· 更新于 2026-12-08

| 编号 | 项目/经历               | 事实                              | 数值                  | 来源                                       | 日期       |
| ---- | ----------------------- | --------------------------------- | --------------------- | ------------------------------------------ | ---------- |
| F01  | WorkPilot P1            | RAG 检索 hit@5                    | 0.\_\_                | workpilot/eval/reports/20261204-eval-v2.md | 2026-12-04 |
| F02  | WorkPilot P1            | 引用正确率 / 拒答准确率           | 0.** / 0.**           | 同上                                       |            |
| F03  | WorkPilot P2            | Agent 任务成功率 / 工具选择准确率 | 0.** / 0.**           | 同上                                       |            |
| F04  | WorkPilot P3            | 场景 rubric 通过率（20 条）       | 0.\_\_                | eval/reports/20261130-scenario-spb.md → v2 |            |
| F05  | WorkPilot P3            | judge 与人审一致率（n=10）        | 0.\_\_                | eval/human_review/20261130.csv             |            |
| F06  | WorkPilot P3            | 端到端耗时 手工 → WP              | ** → ** min           | docs/portfolio/p3-notes.md                 |            |
| F07  | WorkPilot 安全          | 攻击用例拦截率 基线 → v1.4        | 0.\_\_ → 1.0（20 条） | eval/reports/20261203-security-v1.4.md     |            |
| F08  | WorkPilot 运维          | 干净环境恢复耗时                  | \_\_ min              | docs/runbook.md                            |            |
| F09  | WorkPilot               | badcase 总数 / 已转回归           | ** / **               | eval/badcases/summary.md                   |            |
| F10  | WorkPilot               | 真实使用次数（半年）              | \_\_                  | eval/reports/\*usage-stats.md              |            |
| F11  | WorkPilot               | 单次场景成本 / P95 延迟           | ¥** / ** s            | Ops 看板截图                               |            |
| F12  | personal-ai-engineering | 可运行模板数 / 新项目启动耗时     | ** / ** min           | 仓库 README 验证记录                       |            |
| F13  | 公司经历                | 前端工作年限 / 主要技术栈         | 5 年 / ...            | 自述（不含内部信息）                       |            |
| F14  | 开源                    | GitHub stars / Pro Kit 下载或试用 | ** / **               | GitHub / 平台后台                          |            |
| F15  | Portfolio               | URL / Demo URL                    | ...                   | —                                          |            |
```

> 公司经历只写可公开的通用描述（如「负责中后台 React 应用，性能优化使首屏 LCP 降低 \_\_%」），数字必须是你能在面试中解释、且不涉密的。

### Step 2 · 三版结构与侧重（P0）

| 版本                  | 标题定位                                | 项目顺序                                            | 关键词侧重                                                                  | 公司经历详略 |
| --------------------- | --------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------- | ------------ |
| AI Full-Stack（主投） | AI Full-Stack Engineer                  | P3 → P2 → P1 合并为「WorkPilot」一个项目 3 个里程碑 | React/TS、FastAPI、RAG、Agent、HITL UX、Postgres、Docker、CI/CD             | 中           |
| AI Engineer           | AI / LLM Application Engineer           | 评测与 Agent 优先                                   | RAG、Embedding、Rerank、LangGraph、Tool Calling、MCP、Evaluation、Guardrail | 少           |
| Frontend              | Senior Frontend Engineer（AI 产品方向） | 公司经历优先，WorkPilot 突出前端与 AI UX            | React、TypeScript、性能、工程化、流式 UI、可编辑审批                        | 多           |

通用骨架（Markdown，可让 AI 生成样式 CSS）：

```markdown
# 姓名 · AI Full-Stack Engineer

城市 · 邮箱 · Portfolio: <url> · GitHub: <url> · Demo: <url>

## 概述（2 行）

5 年全栈/前端；半年独立构建并上线 RAG + Agent 研发助手平台 WorkPilot（开源），覆盖评测、安全与部署全链路。

## 项目 · WorkPilot（个人开源项目，2026.09–2026.12）

- 场景：…（XYZ，<!-- F04 F06 -->）
- RAG：…（<!-- F01 F02 -->）
- Agent / MCP：…（<!-- F03 -->）
- 安全与多租户：…（<!-- F07 -->）
- 评测体系：…（<!-- F05 F09 -->）
- 交付：…（<!-- F08 F11 -->）

## 工作经历

## 技能（按岗位关键词排序，只写能被追问的）

## 教育
```

### Step 3 · 写 bullet（P0）

示例（数字以 facts.md 为准）：

- 「设计并实现『需求 → 任务拆解 → Issue』LangGraph 工作流（自检回边 + 可编辑人工审批 + 幂等写入），20 条场景评测 rubric 通过率 0.**，端到端耗时较手工降低 **%」
- 「构建四类评测（RAG / Agent / 场景 / 安全）与 badcase 回归体系，LLM judge 经人审校准（一致率 0.\_\_），CI 门禁阻止质量回退」
- 「对照 OWASP LLM Top 10 完成威胁建模与 20 条攻击用例，通过工具白名单、SSRF 阻断、输出过滤与租户隔离将拦截率从 0.\_\_ 提升至 1.0」
- 「Postgres + JWT/RBAC 多租户、SKIP LOCKED 异步导入、Gitea Actions tag 部署与自动回滚；恢复演练 \_\_ 分钟」

### Step 4 · LLM 招聘方挑刺（P0）

输入只含简历文本（已公开信息），分别以三种角色各跑一次：

```text
你是一家中型科技公司的 {AI Full-Stack / AI Engineer / 资深前端} 岗位招聘经理，正在 30 秒内筛简历。
请输出：
1) 30 秒印象（一句话）；2) 最可信的 3 个点；3) 最可疑或空泛的 3 处（引用原文）；
4) 你在面试中会追问的 5 个问题；5) 若只能改 3 处，改什么。
不要润色全文，不要编造任何经历或数字。
```

`review-log.md` 记录：问题 → 采纳/不采纳（理由）→ 修改后文本。「会追问的问题」直接加入 W25 题库。

### Step 5 · 导出 PDF（P0）

```bash
cd ~/lab/projects/career/resume
for v in ai-fullstack ai-engineer frontend; do
  pandoc resume-$v.md -s --metadata title="Resume" -c resume.css -o resume-$v.html
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
     --no-pdf-header-footer --print-to-pdf=resume-$v.pdf resume-$v.html
done
open resume-ai-fullstack.pdf      # 确认 1 页、中文字体正常
cp resume-ai-fullstack.pdf ~/lab/portfolio/public/resume.pdf
```

`resume.css` 设置 `@page { size: A4; margin: 14mm }`、正文 10.5pt、系统中文字体（`-apple-system, "PingFang SC"`）。旧版 Chrome 无 `--no-pdf-header-footer` 时用 `--print-to-pdf-no-header`。

### Step 6 · 提交

```bash
cd ~/lab/projects && git add career/resume && git commit -m "career: facts sheet and three resume versions" && git push
cd ~/lab/portfolio && git add public/resume.pdf && git commit -m "chore: update resume" && git push && git push github main
```

> `projects` 是私有 Gitea 仓库；简历 PDF 中的手机号等联系方式只放在私有仓库和投递渠道，Portfolio 公开版可只留邮箱。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么先写 facts.md 再写简历？（答：单一事实来源，避免三版数字不一致；面试时可快速找到证据）
2. 三版简历的本质区别是什么？（答：同一事实的排序、关键词和详略不同，不是不同的事实）
3. 个人项目如何写才不被认为「玩具」？（答：真实问题 + 真实使用 + 评测数字 + 安全与部署 + 公开代码与 Demo）
4. 为什么数字要写报告原值？（答：可核验；面试官追问时能出示来源，模糊数字反而降低可信度）
5. LLM 挑刺为什么要求「不要润色全文」？（答：目标是找问题和追问点；全文润色容易引入空话和与事实不符的表述）

## 8. 对 DA-01 的贡献

DA-01 的价值从「系统本身」延伸到「职业证据」：WorkPilot 的每个指标都成为可验证的简历条目，完成 DA-01 的「求职作品集 P1/P2/P3」身份（蓝图 §0）。

## 9. 求职映射（D 线）

- 岗位能力：成果量化表达、岗位定位、技术写作。
- 对应岗位：AI Full-Stack Engineer（主）、AI / LLM Application Engineer、Senior Frontend Engineer（AI 产品）。
- 简历 bullet 草稿：见 Step 3。
- 面试可能问：
  1. 简历上哪一条最能代表你？——要点：选 P3 场景或安全加固，按 XYZ 讲 + 出示报告。
  2. 这些数字样本量很小，有说服力吗？——要点：承认规模，强调方法（人审校准、回归、门禁）可扩展，并说明下一步如何扩大样本。

## 10. 卡住时的处理

| 现象                     | 处理                                                                |
| ------------------------ | ------------------------------------------------------------------- |
| 超过 1 页                | 删技能清单中无法被追问的词；公司经历合并为 3 条；项目 bullet ≤ 6 条 |
| 某个指标未达 §11 目标    | 如实写实际值，或写提升幅度（基线 → 现值）；不美化                   |
| 不确定公司经历能写什么   | 只写通用技术与个人贡献，不写系统名、客户、营收；拿不准就不写        |
| PDF 中文乱码             | CSS 指定系统中文字体；用 Chrome 打印而不是 LaTeX                    |
| LLM 建议加入未做过的技术 | 不采纳；记录到 review-log「不采纳：未实践」                         |
| 时间不够                 | 只做 AI Full-Stack 版，另两版 Day73 上午补                          |

## 11. 产出记录（执行时填写）

- facts 条数：\_\_
- 三版页数：fullstack ** / engineer ** / frontend \_\_
- LLM 挑刺采纳：** / ** 条
- 新增到 W25 题库的追问：\_\_ 条
- 用时：\_\_ 分钟
- 卡点：\_\_\_\_

## 12. 完成判定

第 3 节全部勾上 → Task 1 DONE → 明天进入 Day73 · W24 Task 2「小批量投递 + 追踪」。任一未通过 → 保持 IN PROGRESS，明天先补 P0（facts.md + AI Full-Stack 版 PDF）。
