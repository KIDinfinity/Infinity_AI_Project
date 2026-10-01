# 半年稳态成长 + AI求职能力 + AI实际应用 + 睡后收入终极落地计划

> 每日投入：1--2小时｜周期：26周｜原则：可持续、可降量、可复用、可长期迭代  
> 核心变化：在原有「资产化 + AI工程能力」框架上，增加一条明确的 **AI求职能力线**，让半年后的成果既能用于产品/收入，也能直接用于简历、作品集和面试。  
> **2026-10-01 新增**：明确「目标数字资产」——DA-01 = **WorkPilot（工作代号）研发工作 AI 助手平台**，P1/P2/P3 是它的三个里程碑。完整蓝图见 `plan/plan_ai/DA01_TARGET_ASSET.md`（本文件 §2.6 为摘要）。

---

# 0. 文档使用说明

本文件继续采用 **「三层级 + 三时间尺度 + 四条能力线」** 管理整个计划。

## 0.1 三层级

- **第一层级：战略目标层** —— 终身方向 / 北极星，回答「最终为什么做」
- **第二层级：阶段目标层** —— 半年目标，回答「未来6个月做到什么」
- **第三层级：执行落地层** —— 周计划 / 日计划，回答「今天具体做什么」

## 0.2 三种时间尺度

- **短期：第1--2个月** —— 能力迁移 + AI应用基建 + 第一个完整项目
- **中期：第3--4个月** —— 生产化 AI 应用 + 作品集 + 开始求职验证 + 首次变现
- **长期：第5--6个月** —— AI工程资产沉淀 + 求职强化 + 产品迭代 + 收入验证

## 0.3 四条能力线

### A线：AI Application / AI Full-Stack

把已有前端、全栈经验迁移到 AI 应用开发。

核心：

- React / TypeScript
- Python / FastAPI
- LLM API
- RAG
- Agent / Tool Calling
- 数据与 API 集成
- AI UX
- Docker / CI/CD
- 云部署

### B线：Agent / RAG / LLM Engineering

从「调用模型」升级到「设计、评测、优化 AI 系统」。

核心：

- Prompt / Context Engineering
- Embedding / Vector DB
- Chunking
- Retrieval / Rerank
- Tool Calling
- Agent Workflow
- Evaluation
- Badcase
- Hallucination / Guardrail
- Latency / Cost / Quality

### C线：Production AI / AI Platform

把 Demo 变成生产系统。

核心：

- Docker
- API
- Logging / Monitoring
- CI/CD
- Security
- 权限
- 数据隔离
- 版本管理
- 可观测性
- LLMOps / AgentOps 基础

### D线：AI实际应用 + 求职作品集

每个学习主题必须尽可能进入真实应用。

每个重要项目同时产出：

1. 可运行项目
2. Git 仓库
3. README
4. 架构图
5. Demo
6. 技术复盘
7. Evaluation / Badcase
8. 简历项目描述
9. 面试讲解材料

> 核心原则：**学习内容不是终点，能否转化成可运行系统和可解释的工程成果才是验收标准。**

---

# 1. 前置条件：个人核心约束

这些规则默认长期有效，是所有阶段任务的边界条件。

## 1.1 个人基础

- 在职前端开发
- 5年全栈实战经验
- 硕士
- Mac Pro设备
- 熟练 Vibe Coding
- 不裸辞
- 已具备较强软件工程基础

## 1.2 时间约束

- 每日副业固定投入：**1--2小时**
- 不熬夜、不内卷
- 当天任务无法完成：**优先减量，不延长工作时间**
- 不为了完成计划而透支主业、睡眠或生活
- 允许阶段性延期，但不允许无限扩张任务范围

## 1.3 社交与获客约束

- 只接受被动沟通
- 不主动推广
- 不社群营销
- 不私聊拓客
- 主要依赖官网、SEO、产品平台等被动流量
- 求职阶段可以进行正常的公开招聘投递，不把求职等同于主动销售

## 1.4 资金约束

- 总试错预算 ≤ 1.5万元
- 优先控制在1万元以内
- 私有云成本 ≤ 3000元
- 30万元存款不动用，仅作为安全垫
- 新增成本必须有明确用途

## 1.5 AI使用原则

AI主要负责：

- 写代码
- 写测试
- Debug
- 生成初稿
- 辅助调研
- 辅助架构讨论
- 文档整理
- 代码Review
- 生成测试数据
- 辅助分析日志和Badcase

自己必须掌控：

- 问题定义
- 系统架构
- 数据流
- 技术选型
- 核心业务逻辑
- AI系统边界
- Evaluation指标
- 成本与安全
- 代码验收
- 部署
- 最终决策

## 1.5.1 数据与合规红线（2026-10-01 新增）

目标资产要「结合工作内容」，因此必须先划红线：

- 公司机密代码 / 文档 / 工单**一律不进入外部 LLM API**。
- 开发与评测语料只用：自己的笔记、公开开源文档、手工改写脱敏的工作场景样例。
- 工作中只「记录痛点」，不在主业时间「开发副业」。
- 若想在公司内真实使用：先获许可，用公司基础设施 + 本地模型，不属于本计划范围。
- 任何对外公开（GitHub / Demo / 文章）前做一次敏感信息检查。

---

# 1.6 通用解决方案闭环

拿到任何真实问题，都使用同一套规范流程：

```text
现实问题
  ↓
感知 / 数据输入
  ↓
AI理解
  ↓
决策 / 规划
  ↓
工具调用 / 执行
  ↓
结果
  ↓
反馈 / Evaluation
  ↓
Badcase
  ↓
优化
  ↓
再次执行
```

对于纯软件问题，可以简化为：

```text
用户问题
→ 数据
→ LLM / RAG / Agent
→ API / 工具
→ 产品界面
→ 用户反馈
→ Evaluation
→ 优化
```

> 不是每个问题都需要 Agent，也不是每个问题都需要 RAG。  
> 先判断问题，再选择技术。

---

# 2. 第一层级：终身战略目标 / 北极星

## 2.1 总体定位

从：

> 前端 / 全栈开发者出售工时

逐步转向：

> **AI Application Engineer + AI Full-Stack + AI Agent/RAG Engineering + 智能解决方案资产**

最终形成：

```text
软件工程能力
      +
AI工程能力
      +
真实业务问题解决能力
      +
AI辅助开发能力
      +
数字资产能力
```

这比单纯追逐某一个 AI 框架更稳定。

---

# 2.2 战略目标A：AI求职能力

半年内建立一套能够对应真实招聘要求的能力矩阵。

当前招聘样本中反复出现的能力包括：

- Python
- TypeScript / JavaScript / React
- LLM API
- RAG
- Embedding
- Vector DB
- Agent / Tool Calling
- Agent orchestration
- Evaluation
- Prompt / Context Engineering
- API / Backend
- Docker / Cloud
- CI/CD
- Observability
- Security / Guardrails
- 生产环境部署
- 业务问题分析
- AI-assisted development

近期招聘样本也明确出现：

- Python + React/TypeScript 的 AI Full-Stack
- LLM + RAG + Agent
- LangGraph / LangChain / LlamaIndex 等 Agent/RAG 框架
- MCP / Tool integration
- Evaluation / LLM-as-a-judge
- Quality / latency / cost
- Production deployment
- AI应用与企业系统集成

参考招聘样本：

- Accenture Federal Services：GenAI Applications Engineer，强调 Agentic Workflow、RAG、Evaluation、生产部署、质量/延迟/成本。
- Ford：Full Stack Software Engineer - AI Applications，强调 Python、JavaScript/TypeScript、React、LLM、RAG、Agent、Evaluation、Cloud、AI-assisted development。
- Accenture：Full Stack AI Developer，强调 Python + Frontend、LLM Application、Agent、MCP、RAG Evaluation、CI/CD、Cloud。
- GM：AI Agent Engineer，强调 Python/TypeScript/Java、LLM Application、RAG、API、生产服务、测试和可观测性。
- Cognizant：AI Engineer / Generative AI Engineer，强调 LLM、RAG、Agent、LangChain/LlamaIndex/LangGraph、Vector Store、Evaluation。

因此，本计划不追求：

> 「把所有 AI 技术都学一遍」

而追求：

> **用已有全栈能力快速进入 AI Application / AI Engineer / Agent Engineer 的招聘能力区间。**

---

# 2.3 战略目标B：AI实际应用能力

半年内至少完成：

> **2026-10-01 优化**：P1 / P2 / P3 不再是三个独立 Demo，而是**同一个目标资产 WorkPilot 的三个版本里程碑**（P1 = v0.5 Knowledge，P2 = v1.0 Agent，P3 = v2.0 Production Solution）。好处：代码与数据持续复用；面试时讲的是「一个系统如何从 RAG 演进到生产级 Agent 平台」，比三个零散项目更有说服力。详见 §2.6。

## 项目P1：AI知识 / 文档助手

能力覆盖：

```text
文件
 ↓
解析
 ↓
Chunk
 ↓
Embedding
 ↓
Vector DB
 ↓
Retrieval
 ↓
Rerank（可选）
 ↓
LLM
 ↓
引用 / Answer
 ↓
Evaluation
```

建议真实应用：

- 技术文档问答
- 公司知识库
- 产品说明书助手
- PDF / Markdown / 网页知识库
- 个人技术知识库

---

## 项目P2：Agent工作流

能力覆盖：

```text
用户任务
 ↓
Agent
 ↓
判断任务
 ↓
选择Tool
 ↓
调用API
 ↓
获取结果
 ↓
继续推理
 ↓
最终回答
 ↓
记录Trace
```

建议真实应用：

- 技术资料研究 Agent
- GitHub / 项目分析 Agent
- 求职岗位分析 Agent
- 个人工作自动化 Agent
- 产品客服 / FAQ Agent

---

## 项目P3：AI Full-Stack应用

至少完成一个：

```text
React / Next.js
       ↓
Python / FastAPI
       ↓
LLM / RAG / Agent
       ↓
Database / Vector DB
       ↓
Docker
       ↓
Cloud
```

要求：

- 有真实 UI
- 有真实 API
- 有错误处理
- 有日志
- 有基本权限
- 有测试
- 有部署
- 有 README
- 有 Demo

---

# 2.4 战略目标C：收入资产化

继续保留原计划：

> 前端卖时间 → 标准化智能解决方案 → 数字资产 → 自动交付

但增加一个原则：

> **优先做能够同时证明 AI 求职能力的产品。**

例如：

```text
一个RAG产品
=
求职作品集
+
AI工程能力证明
+
数字产品
+
SEO内容
+
未来可继续迭代的资产
```

这样避免：

> 为了赚钱做一个项目  
> 为了求职再做一个完全不同的项目

而是：

> **一个真实项目，同时服务能力、作品集、求职、产品、收入。**

---

# 2.5 战略目标D：低消耗、高自由

保持原目标：

- 居家办公
- 低社交压力
- 主业稳定
- 技术能力持续增长
- 数字资产收入
- 保留健身 / 音乐等生活空间
- 不裸辞
- 不熬夜

---

# 2.6 目标数字资产：DA-01 = WorkPilot（2026-10-01 新增）

> 完整版：`plan/plan_ai/DA01_TARGET_ASSET.md`。所有 phase / week / day 计划必须引用其中的「模块编号 Mx.y + 版本号」作为资产锚点。

## 2.6.1 一句话定义

**WorkPilot：一个可私有部署的「研发工作 AI 助手平台」**——接入团队/个人研发知识（文档、规范、代码仓库、Issue、运行手册），用带引用的 RAG 回答问题，用可审批的 Agent 调用工具完成高频研发工作流（调研、需求拆解、评审、排障、周报），通过 MCP 嵌入 IDE，自带评测、可观测、安全护栏和一键部署。

## 2.6.2 为什么是它

1. **求职对齐**：§2.2 中每一项 JD 高频能力（RAG / Agent / MCP / Evaluation / Observability / React+FastAPI / Docker+Cloud）都对应 WorkPilot 的一个真实模块。
2. **工作对齐**：「企业知识 + 研发效能 Agent」是当前 AI 落地最成熟的方向之一；场景就是自己每天的研发工作，痛点真实、可自测。
3. **资产对齐**：开源核心（作品集 + 被动流量）+ 付费 Pro Kit（标准化、不接外包）。
4. **与「问题决定技术」不冲突**：能力骨架固定；具体解决哪个痛点（场景包 M10）在第 3 周从真实问题池中选出。

## 2.6.3 由哪些部分组成

| 模块                | 作用                                                            | 里程碑          |
| ------------------- | --------------------------------------------------------------- | --------------- |
| M0 研发底座         | Docker / Gitea / 模板 / MinIO / Qdrant / 备份                   | W1–2            |
| M1 LLM Gateway      | 多模型切换、结构化输出、流式、重试、成本                        | v0.1            |
| M2 Knowledge Engine | 导入 → 分块 → 向量化 → 检索 → 带引用回答                        | v0.2–0.3（P1）  |
| M3 Eval Kit         | 数据集、RAG/Agent 指标、Badcase、回归门禁                       | 贯穿            |
| M4 Web Console      | React 聊天 / 知识库 / Agent 时间线 / 看板                       | v0.4 起         |
| M5 Deploy Kit       | Docker Compose、云部署、CI/CD、备份恢复                         | v0.5（P1 发布） |
| M6 Tool Layer       | 工具注册、权限等级、kb/web/gitea 工具                           | v0.6            |
| M7 Agent Runtime    | 手写循环 → LangGraph → Memory → HITL                            | v0.7–0.8        |
| M8 MCP              | MCP Server 嵌入 IDE + MCP Client                                | v0.9            |
| M9 Observability    | Trace、成本账本、预算守卫、限流                                 | v1.0（P2 发布） |
| M10 场景包          | 知识问答 / 需求拆解 / 评审 / 排障 / 周报 / 调研（选 1 主 1 辅） | v1.1            |
| M11 安全与多租户    | 认证、空间隔离、注入防护、审计                                  | v1.2–1.4        |
| M12 交付与商业化    | 开源核心、Pro Kit、产品页、在线 Demo                            | v1.0 / v2.0     |
| M13 求职包          | 能力矩阵、作品集写作、简历 ×3、面试题、Portfolio                | 贯穿            |
| M14 模板库          | `personal-ai-engineering`                                       | v2.0（P3 发布） |

## 2.6.4 最终用户可见功能（v2.0）

知识空间（多空间隔离、文档/仓库接入）→ 带引用问答（拒答、反馈）→ Agent 任务中心（步骤可视化、写操作审批）→ IDE 集成（MCP）→ 评测中心（数据集、回归、Badcase）→ 运维看板（延迟/错误/成本/预算）→ 安全（登录、角色、注入防护、审计）→ 一键部署与恢复。

## 2.6.5 每层计划如何使用它

- **Phase**：说明本阶段把 WorkPilot 从哪个版本推进到哪个版本。
- **Week**：说明本周构建哪些模块、达到哪个可演示状态。
- **Day**：第 1 节「资产锚点」写清模块编号 + 「今天之后 WorkPilot 多了什么能被演示/测量的东西」。答不出来就是跑偏。

---

# 3. 第二层级：半年阶段目标

## 半年最终目标

26周结束时，不是简单得到：

> 「我学过 RAG / Agent / Docker」

而是得到：

```text
一个完整AI应用
+
一个Agent项目
+
一个生产化AI项目
+
一套Evaluation / Badcase体系
+
一套个人AI工程模板
+
GitHub / Portfolio
+
简历AI项目经历
+
面试讲解材料
+
至少一次真实用户/订单/使用验证
```

---

# 3.1 六个月能力路线

```text
第1月
全栈 → AI工程迁移
        ↓
第2月
RAG + AI应用
        ↓
第3月
Agent + Tool Calling
        ↓
第4月
Production AI + Evaluation
        ↓
第5月
完整AI项目 + Portfolio + 求职验证
        ↓
第6月
项目强化 + 面试 + 资产化
```

---

# 4. 短期目标：第1--2个月 / 第1--8周

## 阶段名称：AI工程迁移 + 第一个真实应用

### 阶段定位

不再花大量时间学习抽象 AI 理论。

重点是：

> **把已有5年全栈经验迁移到 AI Application Engineering。**

---

# 4.1 第一阶段核心能力

### 软件工程

- Python
- FastAPI
- REST API
- PostgreSQL / 基础数据库
- Docker
- Git
- Testing
- Logging

### AI工程

- LLM API
- Structured Output
- Embedding
- Vector DB
- RAG
- Prompt / Context Engineering
- Tool Calling
- 基础 Agent

### AI生产化

- 环境变量
- API Key安全
- Error handling
- Retry
- Timeout
- Logging
- Token / Cost tracking

---

# 4.2 第1--2周：岗位能力地图

建立：

```text
AI岗位能力矩阵.md
```

至少分：

| 能力          | 当前水平       | 招聘重要性   | 项目证明方式          |
| ------------- | -------------- | ------------ | --------------------- |
| React/TS      | 已有基础       | 高           | AI UI                 |
| Python        | 待强化         | 高           | FastAPI               |
| LLM API       | 新增           | 高           | AI Feature            |
| RAG           | 新增           | 高           | P1                    |
| Agent         | 新增           | 高           | P2                    |
| Evaluation    | 新增           | 高           | Eval                  |
| Vector DB     | 新增           | 中高         | P1                    |
| Tool Calling  | 新增           | 高           | P2                    |
| Docker        | 已有/强化      | 高           | 部署                  |
| Cloud         | 强化           | 高           | 上线                  |
| CI/CD         | 强化           | 中高         | GitHub Actions        |
| Observability | 新增           | 中高         | Trace/Log             |
| MCP           | 了解并做小实验 | 中高         | Tool integration Demo |
| Fine-tuning   | 暂不作为主线   | 低于上述能力 | 后置                  |

> 注意：这不是给个人能力打分，而是为了确定半年内项目应该证明什么。

---

# 4.3 第3周：LLM应用基础

完成：

- LLM API
- Streaming
- Structured Output
- Prompt模板
- Token / Cost记录
- Error handling
- Retry
- 简单聊天页面

### 实际应用

做一个：

> **AI技术文档助手 v0**

输入：

```text
用户问题
```

输出：

```text
结构化回答
+
引用来源
+
置信提示
```

---

# 4.4 第4周：RAG MVP

完成：

```text
Document
→ Parse
→ Chunk
→ Embedding
→ Vector DB
→ Retrieve
→ LLM
→ Answer
```

技术可以使用：

- Qdrant
- PostgreSQL + pgvector
- Chroma

不需要同时学多个。

### 实际应用

把自己的技术文档放进去：

```text
React
TypeScript
Docker
FastAPI
AI
项目文档
```

最终得到：

> 个人技术知识库 Agent v1

---

# 4.5 第5周：RAG优化

重点不是继续堆功能，而是研究：

- Chunk大小
- Overlap
- Metadata
- Top-K
- Query Rewrite
- Retrieval
- Rerank
- Citation

建立：

```text
evaluation_dataset.json
badcases.md
```

至少准备：

> 20--50个问题

记录：

```text
Question
Expected Answer
Retrieved Documents
Actual Answer
是否正确
是否引用正确
Badcase原因
```

---

# 4.6 第6周：AI Full-Stack

实现：

```text
React
 ↓
FastAPI
 ↓
RAG Service
 ↓
Qdrant
 ↓
LLM
```

加入：

- Streaming
- Loading
- Error
- History
- Citation
- Feedback

---

# 4.7 第7周：Docker + Deployment

完成：

- Dockerfile
- docker-compose
- .env
- health check
- logging
- backup

部署到轻量云。

---

# 4.8 第8周：第一个作品集

形成：

```text
P1-AI-Knowledge-Assistant
├── README
├── Architecture
├── Demo
├── Evaluation
├── Badcases
├── Docker
├── Deployment
└── Technical-Writeup
```

同时写：

> 一页项目复盘

回答：

1. 为什么需要RAG？
2. 为什么使用这个Vector DB？
3. Chunk如何设计？
4. Retrieval如何评估？
5. 哪些Badcase？
6. 如何降低幻觉？
7. 如何控制成本？
8. 如何部署？

---

# 5. 中期目标：第3--4个月 / 第9--16周

## 阶段名称：Agent + Production AI + 求职验证

这一阶段开始从：

> 「会做AI Demo」

升级到：

> **「能做生产级AI应用」**

---

# 5.1 第9--10周：Tool Calling

理解：

```text
LLM
 ↓
Tool Schema
 ↓
Tool Selection
 ↓
Tool Execution
 ↓
Tool Result
 ↓
LLM
```

做3个工具：

- Calculator
- Web/Search
- 项目数据库 / 本地API

---

# 5.2 第11周：Agent Workflow

不要直接做复杂 Multi-Agent。

先做：

```text
Planner
 ↓
Tool
 ↓
Observation
 ↓
Decision
 ↓
Answer
```

实际应用：

> **AI Research Agent**

例如：

```text
输入：
「帮我分析一个技术主题」

Agent：
1. 搜索资料
2. 提取信息
3. 整理
4. 判断冲突
5. 输出报告
6. 给出引用
```

---

# 5.3 第12周：Agent框架

选择一个主框架：

> 优先 LangGraph / LangChain 体系之一。

同时理解：

- State
- Node
- Edge
- Tool
- Memory
- Human-in-the-loop
- Retry
- Fallback

原则：

> 框架是实现方式，不是学习目标。

---

# 5.4 第13周：MCP / Tool Integration

做一个最小 MCP / Tool integration 实验。

目标不是「精通 MCP」。

而是理解：

```text
AI
 ↓
标准化Tool
 ↓
外部系统
```

实际连接：

- 文件
- Git
- 数据库
- API

形成：

> MCP / Tool Integration Demo

---

# 5.5 第14周：Evaluation

这一周非常重要。

建立：

```text
Input Dataset
 ↓
Agent
 ↓
Output
 ↓
Evaluator
 ↓
Score
 ↓
Badcase
 ↓
Regression Test
```

评估：

- Accuracy
- Groundedness
- Citation
- Tool selection
- Tool success
- Latency
- Token cost

不追求复杂指标体系。

先做到：

> **每次修改后，知道系统有没有变好。**

---

# 5.6 第15周：Production AI

增加：

- Logging
- Trace
- Request ID
- Error tracking
- Token tracking
- Cost tracking
- Timeout
- Retry
- Rate limit
- Guardrail

形成：

> AI应用不是「调用API」，而是一个需要运营和维护的软件系统。

---

# 5.7 第16周：作品集项目P2

形成：

```text
P2-AI-Research-Agent
├── Agent
├── Tools
├── RAG
├── Evaluation
├── Badcases
├── Observability
├── Docker
├── Demo
└── Architecture
```

---

# 5.8 第9--16周：开始求职验证

从第10周开始，不必等半年结束。

每周固定：

- 看10个相关AI岗位
- 提取JD高频技能
- 更新能力矩阵
- 每2周做一次简历调整
- 有合适岗位就进行小规模投递
- 记录面试问题
- 把面试问题反向加入学习计划

建立：

```text
job-market.md
interview-questions.md
resume-ai-version.md
```

核心原则：

> **招聘市场是反馈数据，不是新的学习清单。**

如果JD出现一个暂时没学的技术：

```text
是否多个岗位反复出现？
        ↓
是 → 判断是否值得加入
否 → 暂不扩展
```

---

# 6. 长期目标：第5--6个月 / 第17--26周

## 阶段名称：完整AI项目 + Portfolio + 求职强化 + 资产沉淀

---

# 6.1 第17--20周：完整AI应用

选择一个真实问题。

使用：

```text
现实问题
↓
数据
↓
AI
↓
决策
↓
Tool
↓
执行
↓
反馈
↓
Evaluation
```

完成一个真正的：

> **AI Solution**

而不是 Demo。

候选：

### 方向A：企业知识助手

```text
企业文档
→ RAG
→ Agent
→ 权限
→ 引用
→ Feedback
```

### 方向B：AI研发助手

```text
GitHub
→ Code
→ Issue
→ Documentation
→ Agent
→ Report
```

### 方向C：AI运营助手

```text
业务数据
→ 分析
→ Agent
→ Action
→ Feedback
```

### 方向D：AI个人工作流

```text
输入任务
→ Agent
→ 工具
→ 执行
→ 结果
→ Review
```

---

# 6.2 第21周：Production Hardening

重点：

- Security
- Authentication
- Authorization
- Prompt Injection
- Data Leakage
- Rate Limit
- Logging
- Monitoring
- Cost Control
- Backup
- Recovery

---

# 6.3 第22周：AI系统Evaluation

最终项目必须有：

```text
Evaluation Dataset
+
Automated Evaluation
+
Human Review
+
Badcase
+
Regression
```

目标：

> 证明你不仅会「让AI跑起来」，还会判断「AI到底有没有变好」。

---

# 6.4 第23周：Portfolio

建立个人：

```text
AI Portfolio
```

至少展示：

### Project 1

AI RAG Application

### Project 2

AI Agent

### Project 3

Production AI Solution

每个项目统一结构：

```text
Problem
↓
Why AI
↓
Architecture
↓
Implementation
↓
Evaluation
↓
Badcases
↓
Optimization
↓
Deployment
↓
Result
```

---

# 6.5 第24周：简历

建立：

```text
Frontend Resume
AI Full-Stack Resume
AI Engineer Resume
```

不是编造经历，而是从真实项目中提炼：

- Problem
- Scale
- Architecture
- Technology
- Engineering difficulty
- AI difficulty
- Evaluation
- Result

---

# 6.6 第25周：面试

准备：

## AI基础

- LLM基本原理
- Embedding
- Transformer基本概念
- Context
- Token
- Temperature

## RAG

- Chunk
- Retrieval
- Rerank
- Embedding
- Vector DB
- Hybrid Search
- Evaluation

## Agent

- Tool Calling
- Workflow
- Memory
- State
- Planning
- Retry
- Guardrail

## Engineering

- API
- Docker
- Database
- Cache
- Queue
- Logging
- Monitoring
- CI/CD

## System Design

回答：

> 「设计一个企业AI知识库」

或者：

> 「设计一个AI客服Agent」

必须能够画出：

```text
User
 ↓
Frontend
 ↓
API
 ↓
AI Orchestrator
 ├── RAG
 ├── Tools
 ├── Memory
 └── Guardrails
 ↓
LLM
 ↓
Response
 ↓
Evaluation / Observability
```

---

# 6.7 第26周：半年复盘

最终回答：

### 求职

- 能否独立解释3个AI项目？
- 能否完成AI系统设计？
- 能否解释RAG？
- 能否解释Agent？
- 能否解释Evaluation？
- 能否解释Production问题？

### 产品

- 是否有真实用户？
- 是否有真实订单？
- 是否有可持续流量？

### AI工程

- 是否可以独立完成：
  - RAG
  - Agent
  - Tool Calling
  - Evaluation
  - Deployment
  - Monitoring

### 资产

- 是否形成：
  - AI Template
  - RAG Template
  - Agent Template
  - Evaluation Template
  - Docker Template
  - Prompt Library
  - Badcase Library

---

# 7. 第三层级：执行落地系统

## 7.1 永久执行规则

每天：

> **1--2小时封顶**

任务：

- P0：今天必须完成
- P1：有余力完成
- P2：可延期

如果时间不足：

```text
P2删除
↓
P1延期
↓
P0减量
```

禁止：

> 为了完成计划增加到3--5小时。

---

# 7.2 三条原有工作线升级为四条

## A线：AI产品 / 变现

目标：

> 做一个真实AI解决方案。

## B线：AI Engineering

目标：

> RAG + Agent + Evaluation + Production AI。

## C线：Infrastructure

目标：

> Docker + Cloud + CI/CD + Observability。

## D线：Job Market / Portfolio

目标：

> 把真实项目转化成简历、GitHub、Demo和面试能力。

---

# 7.3 四条线优先级

第1--8周：

> **B > A > C > D**

第9--16周：

> **B > D > A > C**

第17--26周：

> **D ≈ B > A > C**

原因：

> 到中后期，继续搭基础设施的边际收益下降，应该把已有能力转化成「可证明的成果」。

---

# 8. 26周执行路线

| 周  | 阶段 | 主线  | 核心目标                                       | 主要产出                     | WorkPilot 资产锚点 / 版本      |
| --- | ---- | ----- | ---------------------------------------------- | ---------------------------- | ------------------------------ |
| 1   | 短期 | C/A/D | 研发底座 + 痛点池 + 项目规范                   | 模板、workpilot 仓库、痛点池 | M0.1–M0.3 / v0.0               |
| 2   | 短期 | B/D/C | AI岗位能力地图 + Python/FastAPI/LLM API + 存储 | JD能力矩阵、AI API           | M13.1 M1.1 M1.2 M0.4 M0.5      |
| 3   | 短期 | B/A   | Structured Output/Streaming + DA-01 场景选型   | LLM应用v0                    | M1.3–M1.6 M10 / v0.1           |
| 4   | 短期 | B     | RAG Pipeline                                   | RAG MVP                      | M2.1–M2.6 / v0.2               |
| 5   | 短期 | B     | Chunk/Retrieval/Eval                           | Evaluation Dataset           | M2.2 M2.4 M3.1–M3.4 / v0.3     |
| 6   | 短期 | A/B   | AI Full-Stack                                  | React+FastAPI                | M4.1 M4.2 M3.6 / v0.4          |
| 7   | 短期 | C     | Docker/部署                                    | Cloud MVP                    | M5.1–M5.5 M9.1                 |
| 8   | 短期 | D     | 项目包装                                       | P1 Portfolio                 | M13.2 M12.1 / **v0.5 = P1**    |
| 9   | 中期 | B     | Tool Calling                                   | Tool Demo                    | M6 / v0.6                      |
| 10  | 中期 | B     | Agent Workflow                                 | Research Agent v0            | M7.1 M7.5 M4.3 / v0.7          |
| 11  | 中期 | B     | Agent框架                                      | Agent v1                     | M7.2                           |
| 12  | 中期 | B     | Memory/State/HITL                              | Agent v2                     | M7.3 M7.4 / v0.8               |
| 13  | 中期 | B     | MCP/Tool Integration                           | MCP Demo                     | M8 / v0.9                      |
| 14  | 中期 | B     | Evaluation                                     | Eval Harness                 | M3.3 M3.5                      |
| 15  | 中期 | C/B   | Production AI                                  | Logging/Cost/Trace           | M9 M11.3 M4.4                  |
| 16  | 中期 | D     | 求职作品集                                     | P2 Portfolio                 | M13 M12 / **v1.0 = P2**        |
| 17  | 长期 | A/B   | 真实问题定义                                   | P3 Definition                | M10 M11 设计                   |
| 18  | 长期 | A/B   | 核心AI链路                                     | P3 MVP                       | M10 / v1.1                     |
| 19  | 长期 | B/C   | 工程化                                         | Production v1                | M11.1 M11.2 M5.4 / v1.2        |
| 20  | 长期 | B     | Evaluation                                     | P3 Eval                      | M3 M4.4 / v1.3                 |
| 21  | 长期 | C     | Security/Guardrail                             | Production Hardening         | M11 / v1.4                     |
| 22  | 长期 | B     | Badcase/Regression + 模板抽取                  | Eval v2 + 模板库             | M3.5 M14 M12.2 / **v2.0 = P3** |
| 23  | 长期 | D     | Portfolio                                      | 个人AI Portfolio             | M13.5 M12.4                    |
| 24  | 长期 | D     | 简历                                           | AI Resume                    | M13.3                          |
| 25  | 长期 | D/B   | 面试                                           | System Design/Interview      | M13.4                          |
| 26  | 长期 | 全部  | 半年复盘                                       | 半年报告                     | 全部                           |

> **节奏说明（2026-10-01）**：执行目录 `plan/` 中「周」是 2–5 天的冲刺（Day01–Day77 连续日期，每天 1–2 小时）。逐日安排见 `plan/plan_ai/DA01_TARGET_ASSET.md` 附录 A。

---

# 9. 每日任务生成规则

每天任务必须采用：

## ① 今日目标

为什么今天做？

## ② 今日岗位能力

这个任务对应什么招聘能力？

例如：

> RAG Retrieval → AI Engineer / GenAI Application Engineer

## ③ 今日学习

只学习完成任务所必须的知识。

原则：

> 先做任务，再补知识。

## ④ 今日资料

优先：

1. 官方文档
2. 官方教程
3. 高质量技术文章
4. 视频
5. 其他资料

## ⑤ 今日AI实际应用

必须说明：

> 今天这个技术最终在哪里使用？

例如：

```text
学习Tool Calling
↓
给Research Agent增加搜索工具
```

## ⑥ 今日实战

至少产生一个：

- API
- 页面
- Agent
- RAG
- Tool
- Evaluation
- Docker服务
- 测试
- 文档

## ⑦ 今日验收

必须回答：

> 「做到什么程度，今天才算完成？」

## ⑧ 今日资产

记录：

- Code
- Prompt
- Badcase
- Dataset
- Architecture
- Documentation

## ⑨ 今日求职映射

记录：

> 这个能力以后可以如何写进简历？

## ⑩ 今日资产锚点（2026-10-01 新增，必填）

必须写清：

- 本任务构建的是 WorkPilot 哪个模块（`plan/plan_ai/DA01_TARGET_ASSET.md` §5 的 Mx.y）；
- 推进的是哪个版本里程碑（§9）；
- 「今天之后，WorkPilot 多了什么能被演示或被测量的东西？」

答不出来的任务，按 GLOBAL_CONTEXT §10 降级或删除。

---

# 10. AI协作规则

## 10.1 AI负责

- 写代码
- Debug
- 测试
- 文档
- 重构
- 搜索资料
- 生成测试数据
- 分析日志
- 分析Badcase
- 生成初步方案
- 代码Review

## 10.2 人负责

必须自己理解：

- 为什么做
- 为什么用AI
- 为什么不用AI
- 架构
- 数据流
- AI边界
- Evaluation
- 安全
- 成本
- 最终代码

---

# 10.3 推荐模型协作方式

### 主规划模型

负责：

- 半年路线
- 周计划
- 日计划
- 架构Review
- 项目范围控制
- 复盘
- 求职能力映射

### 工程模型

负责：

- Python
- FastAPI
- API
- Database
- Docker
- RAG
- Agent
- Test
- Debug

### UI模型

负责：

- React
- TypeScript
- UI
- CSS
- 交互

---

# 10.4 AI协作的新原则

从：

> AI帮我写代码

升级到：

> **AI帮我完成工程任务，我负责定义问题、架构、验收和反馈。**

推荐工作流：

```text
我定义问题
↓
AI分析方案
↓
我选择架构
↓
AI实现
↓
AI生成测试
↓
我Review
↓
运行Evaluation
↓
分析Badcase
↓
AI提出优化
↓
我决定是否修改
```

这与当前部分 AI 软件工程岗位强调的「AI-assisted development + engineer负责架构、判断和验证」方向一致。Ford 的 AI Applications 岗位就明确强调 AI agent orchestration、代码审查与架构判断，而不是单纯写代码。citeturn0search6

---

# 11. 每周复盘机制

每周回答：

1. 本周完成多少？
2. 哪些没完成？
3. 为什么？
4. 是否任务设计过量？
5. 是否出现无效学习？
6. 是否产生代码资产？
7. 是否产生AI应用？
8. 是否增加求职能力？
9. 是否产生可展示项目？
10. 是否产生Badcase？
11. 是否建立Evaluation？
12. 是否应该减少任务？
13. 是否偏离北极星？

---

# 11.1 增加「岗位反馈复盘」

每2周检查：

```text
最近看到的AI岗位
↓
高频要求
↓
我已有能力
↓
我缺少能力
↓
是否值得补
↓
是否能通过项目证明
```

不要：

> 看到一个JD就新增一个技术。

只有当一个能力：

1. 多个岗位重复出现
2. 与现有项目相关
3. 可以在1--2周内形成成果

才考虑加入。

---

# 12. 半年最终验收

## A. AI求职能力

至少可以独立讲清：

- LLM Application
- RAG
- Embedding
- Vector DB
- Retrieval
- Rerank
- Agent
- Tool Calling
- MCP基础
- Evaluation
- Badcase
- Guardrail
- Cost
- Latency
- Docker
- Cloud
- API
- Observability

---

# 12.1 AI项目

至少：

### P1

RAG AI Application

### P2

Agent + Tool Calling

### P3

Production AI Solution

---

# 12.2 每个项目必须具备

```text
Problem
Architecture
Implementation
Evaluation
Badcase
Optimization
Deployment
Demo
README
```

---

# 12.3 求职资产

必须形成：

- AI Resume
- AI Full-Stack Resume
- GitHub
- Portfolio
- Project Demo
- Project Architecture
- Interview Notes
- System Design Notes
- 30个以上AI面试问题
- 3个项目的STAR/技术讲解版本

---

# 12.4 AI工程资产

最终形成：

```text
personal-ai-engineering/
├── rag-template/
├── agent-template/
├── evaluation-template/
├── fastapi-template/
├── docker-template/
├── ai-observability/
├── prompts/
├── badcases/
├── datasets/
├── interview/
└── projects/
```

> 来源：第 22 周从 WorkPilot 真实代码中抽取（M14），不单独从零写模板。

---

# 12.5 收入

继续验证：

- 产品是否有人使用？
- 是否产生订单？
- 是否有自然流量？
- 是否可以标准化交付？
- 是否可以继续作为数字资产？

收入不是半年唯一验收指标。

---

# 13. 三层逻辑总览

```text
第一层级：终身北极星
│
├── AI工程能力
├── AI实际问题解决能力
├── AI求职能力
├── 收入资产化
└── 低消耗自由生活
        ↓
第二层级：半年阶段目标
│
├── 第1–2月
│   └── AI应用 + RAG + Full-Stack
│
├── 第3–4月
│   └── Agent + Evaluation + Production
│
└── 第5–6月
    └── 完整项目 + Portfolio + 求职 + 资产
        ↓
第三层级：每日执行
│
├── 今日目标
├── 岗位能力
├── 学习
├── 实际应用
├── 实战
├── 验收
├── 资产
└── 求职映射
```

---

# 14. 永久兜底规则

1. 时间不够：减量，不加班。
2. 不裸辞。
3. 不动30万元安全垫。
4. 不超预算。
5. 不接定制外包。
6. 不做主动社群营销。
7. 不做一次性Demo，尽量沉淀为长期资产。
8. 每个项目尽量文档化、容器化、可迁移、可备份。
9. 学习必须服务于当前项目。
10. AI可以写代码，但核心架构和业务逻辑必须自己理解。
11. 新需求必须经过优先级判断。
12. 连续完不成任务时，优先重新设计计划。
13. 半年重点是建立「能力 + 项目 + 作品集 + 资产 + 验证」。
14. 每个阶段必须留下可复用成果。
15. **不要为了追逐AI热点而频繁换技术栈。**
16. **不要把学习Agent框架本身当成目标。**
17. **不要把「会调用LLM API」等同于AI工程能力。**
18. **优先证明完整系统，而不是堆砌技术名词。**
19. **每学一个重要AI能力，尽量至少进入一个真实应用。**
20. **招聘JD只作为反馈数据，不作为无限扩张学习范围的理由。**

---

# 15. 给AI模型的分析上下文

当把本文件交给 ChatGPT / DeepSeek 等模型分析时：

> 你不是单纯的代码生成器，而是本项目的「AI工程学习 + 项目执行 + 求职能力分析辅助AI」。

你的任务是在：

- 不影响主业
- 不熬夜
- 每日1--2小时
- 预算受限
- 不裸辞
- 不做定制外包

的约束下，帮助用户完成：

```text
AI能力
+
AI实际应用
+
AI工程项目
+
求职作品集
+
数字资产
```

每次提出建议必须：

1. 判断第一、第二还是第三层级；
2. 判断短期、中期还是长期；
3. 判断A/B/C/D哪条线；
4. 说明为什么现在做；
5. 控制在1--2小时；
6. 给出验收标准；
7. 给出实际应用场景；
8. 给出最终资产；
9. 如果可以，说明对应哪类AI岗位能力；
10. 不无理由增加新技术；
11. 优先复用已有项目；
12. 如果任务对半年目标帮助小，应建议延后或删除。

当用户说：

> 「今天做什么？」

输出：

```text
今日目标
→ 对应岗位能力
→ 学习内容
→ 学习资料
→ 实际应用
→ 实战任务
→ 验收标准
→ 预计耗时
→ 产出物
→ 简历/Portfolio如何体现
→ 下一步
```

当用户提交代码或项目结果：

```text
先检查：
1. 当前阶段目标
2. AI应用是否真实
3. 工程质量
4. Evaluation
5. Badcase
6. 部署
7. 是否形成作品集
8. 是否能转化为求职证据
9. 最后决定下一步
```

---

# 16. 本计划最核心的一条新原则

过去的路径容易变成：

```text
学习Docker
↓
学习RAG
↓
学习Agent
↓
学习MCP
↓
学习很多AI技术
```

新的路径改成：

```text
真实问题
↓
判断是否需要AI
↓
选择最小AI方案
↓
做出可用版本
↓
接入真实数据
↓
部署
↓
Evaluation
↓
Badcase
↓
优化
↓
形成项目
↓
形成Portfolio
↓
形成求职证据
↓
形成可复用资产
↓
形成产品 / 收入
```

最终半年真正要沉淀的不是：

> 「我学了多少AI技术」

而是：

> **「我可以拿到一个真实问题，把它变成一个AI系统，并且能够解释、实现、评估、部署、优化它。」**

这就是整个计划从「学习计划」升级成「AI工程能力 + 实际应用 + 求职 + 资产」系统后的核心闭环。

---

# 附：本版本使用的招聘市场观察来源

以下招聘信息用于确定本计划中的岗位能力映射，具体职位要求会随公司、地区、级别和时间变化，不应理解为所有AI岗位的统一要求。

- Accenture Federal Services — Generative AI Applications Engineer：Agentic workflows、RAG、LLM evaluation、tool use、production deployment、quality/latency/cost。
- Ford — Full Stack Software Engineer - AI Applications：Python、JavaScript/TypeScript、React、LLM、RAG、agents、evaluation、cloud、AI-assisted development。
- Accenture — Full Stack AI Developer：Python + frontend、LLM applications、agents、MCP、RAG evaluation、CI/CD、cloud。
- GM — AI Agent Engineer：Python/TypeScript/Java、LLM applications、RAG、REST API、production services、observability/testing。
- Cognizant — AI Engineer / Generative AI Engineer：LLM、RAG、Agentic AI、LangChain/LlamaIndex/LangGraph、vector stores、evaluation。
- NTT DATA — Agentic AI Engineer：agent workflows、RAG、tool calling、full-stack AI applications、cloud deployment、enterprise integration。

> 招聘市场观察的使用方式：**看共同能力，不追逐单个公司的全部技术栈。**
