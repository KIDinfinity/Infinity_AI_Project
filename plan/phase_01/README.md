# Phase 01 · 探索与 P1（第 1–8 周 · Day01–Day33 · 09-28 → 10-30）

## 1. 阶段目标

从零建立研发底座，用真实痛点确定 DA-01 的主场景，并把 WorkPilot 从「空仓库」推进到 **v0.5 = P1 WorkPilot Knowledge**：一个已部署到云端、带评测与 Badcase、可通过 Web 使用的研发知识 RAG 助手。

## 2. 资产锚点（本阶段在目标资产中的位置）

| 项                     | 内容                                                                                                                                                                  |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 版本推进               | 无 → v0.0（骨架）→ v0.1（LLM Gateway）→ v0.2（RAG MVP）→ v0.3（评测优化）→ v0.4（Web）→ **v0.5（P1 发布）**                                                           |
| 构建模块               | M0 研发底座、M1 LLM Gateway、M2 Knowledge Engine、M3.1/M3.2/M3.4/M3.6 Eval、M4.1/M4.2 Web、M5 Deploy Kit、M9.1 request_id、M10 场景选型、M12.1 开源、M13.1/M13.2 求职 |
| 完成后最终产品多了什么 | WorkPilot 的「知识层」完整可用：能导入研发文档，带引用回答，知识不足会拒答，有 50 题评测基线，有公网地址                                                              |

```text
W1 底座+规范 → W2 FastAPI+LLM+存储 → W3 结构化/流式+选场景 → W4 RAG → W5 评测 → W6 Web → W7 部署 → W8 作品集
```

## 3. 为什么这个阶段存在

后面所有能力（Agent、MCP、安全、多租户）都建在「LLM 调用层 + 知识层 + 部署底座」之上。P1 是求职最基础、JD 出现频率最高的作品（RAG + Full-Stack），也是 DA-01 的地基。

## 4. 本阶段必须产生什么（文件级）

| 线  | 产出                                         | 位置                                                                             |
| --- | -------------------------------------------- | -------------------------------------------------------------------------------- |
| C   | Docker / Gitea / MinIO / Qdrant / 备份脚本   | `~/lab/projects/infra/`                                                          |
| C   | 项目规范 + 模板仓库                          | `ai-project-template`、`PROJECT_STANDARD.md`                                     |
| A   | 痛点池（≥10 条，已分类、已评分）+ DA-01 定义 | `projects/product-lab/pain-pool.md`、`workpilot/docs/product/da01-definition.md` |
| B   | LLM Gateway（结构化/流式/重试/成本）         | `workpilot/apps/api/app/llm/`                                                    |
| B   | RAG 链路 + KB API                            | `workpilot/apps/api/app/rag/`                                                    |
| B   | 50 题评测集 + runner + 报告 + Badcase        | `workpilot/eval/`                                                                |
| B   | Web Console（聊天/引用/历史/反馈/上传）      | `workpilot/apps/web/`                                                            |
| C   | Dockerfile + compose + 云部署 + CI           | `workpilot/deploy/`、`.gitea/workflows/`                                         |
| D   | 能力矩阵、P1 作品集、简历条目、面试 10 题    | `projects/career/`、`workpilot/docs/portfolio/p1.md`                             |

## 5. 本阶段不应该做什么

- 不做 Agent / Tool Calling / MCP（那是 phase_02）。
- 不上 Postgres、认证、多租户（phase_03）。
- 不同时试多个向量库 / 多个框架；不引入 LangChain 做 RAG（手写链路更利于理解与面试）。
- 不预设「必须具身 / 必须硬件」；不为「完整」堆功能。
- 公司机密数据不进入外部 LLM（见 DA01_TARGET_ASSET §8）。

## 6. 本阶段核心能力

- **B**：Python/FastAPI、LLM API、Structured Output、Streaming、Embedding、Qdrant、Chunking、Retrieval、Hybrid Search、RAG Evaluation、LLM-as-a-judge。
- **A**：痛点发现、问题类型判断、场景评分选型。
- **C**：Docker Compose、云部署、Caddy HTTPS、CI、备份恢复。
- **D**：JD 拆解、能力矩阵、项目技术写作、简历 bullet。

## 7. 进入条件

无（从零开始）。Day01 Docker ✅、Day02 Gitea ✅。

## 8. 完成条件 / 阶段验收（第 8 周 Day33）

- [ ] 干净环境（新目录 / 新机器）按 README 30 分钟内恢复并运行 WorkPilot v0.5
- [ ] 公网地址可访问，上传文档 → 带引用问答 → 反馈 全流程可演示
- [ ] 50 题评测报告存在，hit@5、引用正确率、拒答率有基线数值
- [ ] Badcase ≥ 10 条，带分类和处理结论
- [ ] DA-01 定义文档已写，`PROJECT_CONFIG.md` 已回填
- [ ] P1 作品集：README + 架构图 + Demo + 技术复盘 8 问
- [ ] 能力矩阵覆盖 ≥ 12 项 JD 高频能力，并标出「由 WorkPilot 哪个模块证明」
- [ ] 能 3 分钟讲清 P1（问题 → 架构 → 评测 → 结果）

核心项全 PASS 进入 phase_02；非核心项（CI、云端恢复演练）可 CONDITIONAL，在 W9 第一天补齐。

## 9. 下一阶段依赖什么

phase_02 直接复用：`app/llm`（Agent 的模型层）、`app/rag`（变成 `kb_search` 工具）、`eval/`（扩展为 Agent 评测）、`apps/web`（加 Agent 时间线）、`deploy/`（继续部署 v1.0）。

## 完成本阶段后，DA-01 比阶段开始前多了什么？

从「什么都没有」变成：一个已部署、已评测、可演示的 WorkPilot v0.5（P1），一个已用真实痛点选定的主场景，一套固定的研发底座和项目模板，以及第一份可写进简历的 AI 项目。
