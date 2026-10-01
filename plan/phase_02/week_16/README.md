# Week 16 · P2 发布：作品集 + 开源 + 简历 v1（Phase 2 · Day55–Day57 · 11-21 → 11-23）

## 1. 本周核心目标

把 W9–W15 的工程成果打包成 **v1.0 = P2 WorkPilot Agent** 并对外发布：

1. README P2 章节 + 架构图 v1 + LangGraph 图 + 评测表 + 截图；`docs/portfolio/p2.md`；云端部署 v1.0；tag `v1.0.0` + Release notes。
2. 2–3 分钟 Demo 视频 + 2000–3000 字技术文章（发布到个人博客 / 掘金）；`docs/product/open-core.md` 定稿；README 顶部 / GitHub Pages 简单产品页；发布前 gitleaks。
3. 简历 v1（ai-fullstack、ai-engineer 两版）；面试题累计 ≥ 25；Phase 2 验收与复盘；`PROJECT_CONFIG.md` 推进到阶段三 · 第 17 周。

## 2. 资产锚点

| 构建模块                                 | 版本里程碑          | 本周结束 WorkPilot 能演示什么                                                                    |
| ---------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------ |
| M13.2 项目写作（P2）                     | **v1.0（P2 发布）** | GitHub README 一屏看懂：Agent + MCP + Eval + Observability，带数字与截图；`docs/portfolio/p2.md` |
| M12.1 开源核心 / M12.3 产品页 + 技术文章 | v1.0                | 公开仓库 + Release v1.0.0 + Demo 视频 + 1 篇技术文章 + 产品页（Pro Kit 即将推出）                |
| M13.3 简历 v1 / M13.4 面试题库           | —                   | 两版简历含 P1+P2 量化 bullets；面试题 ≥ 25                                                       |

## 3. 为什么这一周存在

- Phase 2 的价值只有在「别人能看到、能运行、能理解」时才成立：作品集、开源、简历是 D 线在本阶段的唯一产出窗口。
- 商业化验证需要入口：开源核心 + 产品页 + 文章是被动流量的起点（不私聊拓客）。
- 下一阶段（P3）要基于 v1.0 做场景包和安全加固，需要一个干净、打了 tag、部署在云端的稳定基线。

## 4. 本周在路线中的位置

```text
W15 产出：Trace / 成本账本 / 预算 / 限流 / Guardrail v0 / Ops 看板 + W14 评测报告与门禁 + W13 MCP
   ↓
W16 本周：P2 README/作品集 → v1.0 部署与 Release → Demo + 文章 + 产品页/开源边界 → 简历 v1 + 面试题 + 阶段验收
   ↓
W17 输入（phase_03）：v1.0 稳定基线 + 评测/可观测/护栏底座 + 简历 v1 → P3 问题定义（主场景包）与架构 v2
```

## 5. 每日安排

| Day   | 日期  | Task                                        | 当日 P0 产出                                                                                                   | 模块         | 状态 |
| ----- | ----- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------ | ---- |
| Day55 | 11-21 | Task 1：P2 README / 架构 / 评测报告（v1.0） | README P2 章节 + `docs/architecture.md` v1 + `docs/portfolio/p2.md` + 云端 v1.0 + tag `v1.0.0` + Release notes | M13.2 / v1.0 | TODO |
| Day56 | 11-22 | Task 2：Demo + 技术文章 + 产品页 / 开源边界 | Demo 视频 + 文章发布 + `docs/product/open-core.md` + 产品页 + gitleaks 通过                                    | M12.1 M12.3  | TODO |
| Day57 | 11-23 | Task 3：简历 v1 + 面试题 + Phase 2 复盘     | 两版简历 v1 + 面试题 ≥ 25 + `phase02-review.md` + PROJECT_CONFIG 更新                                          | M13.3 M13.4  | TODO |

## 6. 本周必须留下的资产

| 路径                                                                   | 说明                                                                  |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `~/lab/workpilot/README.md`                                            | P2 章节、评测表、截图、Demo 链接、产品页顶部区块                      |
| `~/lab/workpilot/docs/architecture.md`                                 | 架构图 v1（mermaid）+ LangGraph 图                                    |
| `~/lab/workpilot/docs/portfolio/p2.md`                                 | P2 作品集长文（问题→架构→工具→HITL→评测→badcase→优化→成本/延迟→部署） |
| `~/lab/workpilot/docs/assets/`                                         | 截图（Agent 时间线、审批卡片、IDE MCP、Trace、Ops）                   |
| `~/lab/workpilot/CHANGELOG.md`、GitHub Release `v1.0.0`                | 发布说明                                                              |
| `~/lab/workpilot/docs/product/open-core.md`                            | 免费 vs Pro Kit 边界定稿                                              |
| `~/lab/workpilot/docs/site/index.html`（可选）                         | GitHub Pages 简单落地页                                               |
| 博客 / 掘金文章链接                                                    | 技术文章（同时写入 README）                                           |
| `~/lab/projects/career/resume/ai-fullstack-v1.md`、`ai-engineer-v1.md` | 简历 v1                                                               |
| `~/lab/projects/career/interview-questions.md`                         | ≥ 25 道                                                               |
| `~/lab/projects/product-lab/reviews/phase02-review.md`                 | Phase 2 复盘                                                          |
| `PROJECT_CONFIG.md`                                                    | 当前状态 → 阶段三 · 第 17 周                                          |

## 7. 本周验收标准

- [ ] PASS / FAIL：README 含 P2 章节（Agent、MCP、Eval、Observability）、架构图 v1、LangGraph 图、RAG + Agent 评测表、≥ 4 张截图
- [ ] PASS / FAIL：`docs/portfolio/p2.md` 覆盖 10 个小节且全部数字可追溯到报告文件
- [ ] PASS / FAIL：云端运行 v1.0（`/health` 返回版本 1.0.0）；MCP HTTP 未公开或有 token 保护
- [ ] PASS / FAIL：tag `v1.0.0` 在 Gitea 与 GitHub；GitHub Release notes 已发布
- [ ] PASS / FAIL：Demo 视频 2–3 分钟（研究任务 + 审批、IDE MCP、Trace 页）已上传并在 README 链接
- [ ] PASS / FAIL：技术文章 2000–3000 字已发布并链接 GitHub
- [ ] PASS / FAIL：`open-core.md` 定稿 + 产品页上线；gitleaks 扫描无告警
- [ ] PASS / FAIL：简历 v1 两版完成；面试题 ≥ 25；phase_02 README 第 8 节逐项勾选；`phase02-review.md` 完成；PROJECT_CONFIG 已更新

## 8. 求职映射

- **本周能力**：技术写作、作品集叙事、开源发布、产品化表达、简历量化。
- **简历 bullet 草稿（P2 总述）**：
  - 独立设计并交付可私有部署的研发 Agent 平台 WorkPilot v1.0（FastAPI + LangGraph + React），支持工具调用、写操作人工审批、长期记忆、MCP IDE 集成；30 任务评测成功率 **、工具选择准确率 **、P95 **s、单任务平均成本 ¥**。
  - 建立评测驱动开发流程（RAG 50 题 + Agent 30 任务 + CI 回归门禁）与自研 Trace/成本/护栏体系，未经审批写操作 0 次。
- **面试题**：
  1. 用 3 分钟介绍你的 WorkPilot 项目（STAR + 数字）。
  2. 你项目里最难的技术问题是什么？怎么解决的？
  3. 如果给 WorkPilot 支持 100 个团队，你会怎么改架构？

## 9. 本周禁止事项

- 不加新功能（发现 bug 只修阻断发布的 P0 bug）。
- 不在文章 / Demo / 仓库中出现任何公司内容、同事姓名、内部系统截图。
- 不主动私聊拓客、不在社群推广；文章只发布不引流。
- 不开始 Pro Kit 打包与收费（W22），本周只定边界与「即将推出」。
- 不为产品页引入新框架（纯 README 或单个静态 HTML）。

## 10. 时间不够时（最小保留）

- Day55：README P2 章节 + 评测表 + tag `v1.0.0`（云端部署可顺延 1 天，`p2.md` 可先写大纲 + 数字）。
- Day56：Demo 视频（可无配音、字幕说明）+ `open-core.md` + gitleaks；文章可先发布 1500 字精简版，W17 补全。
- Day57：简历 v1（ai-engineer 版优先）+ 面试题 ≥ 25 + 阶段验收勾选 + PROJECT_CONFIG 更新；复盘可精简为 1 页。

## 11. 周复盘（Day57 填写）

- 完成：\_\_\_\_
- 未完成 / 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西（Release、视频、文章、产品页）：\_\_\_\_
- 外部反馈（Star / 阅读 / Discussions，只观察不拉票）：\_\_\_\_
- 是否出现无效学习或范围扩张（如重做 UI、加功能）：\_\_\_\_
- 下周调整（进入 phase_03 前需要补的 P0）：\_\_\_\_
