# 00. 项目总览

## 定位

**短线基金 AI 分析决策系统**：每天/每周点一次按钮，系统自动拉取数据、跑分析、给出「持有 / 止盈 / 预警」结论，**只输出建议，不自动下单**。

来源需求：[draft/fund/prompt.md](../../../draft/fund/prompt.md)、[draft/fund/frame.md](../../../draft/fund/frame.md)。

> **新开对话 / 新窗口怎么接着做**：直接把 [../AGENTS.md](../AGENTS.md) 这个路径告诉大模型（"按 project/fund/AGENTS.md 跑这个 project"）即可恢复全部上下文，不需要每次重新粘贴设计文档。

## 与仓库主线的关系（必须显式声明）

- 本仓库当前 DA-01 = `WorkPilot`（团队规范 / 组件库 Grounded Q&A），见 `PROJECT_CONFIG.md`。
- `project/fund` **不是 DA-01**，是个人工程 / C 线下的独立 side project（已与用户确认），**不占用 A 线（DA-01）的开发时间预算**。
- 本设计及后续实现，严格限制在 `project/fund/` 目录内，不修改 `plan/`、`PROJECT_CONFIG.md` 等 DA-01 相关文件。

## 设计原则

1. **扁平优先**：能用一个文件解决的，不建子目录；只有当同类文件 ≥ 3 个且会持续增长时才建目录（如 `sources/`、`agents/`、`prompts/`）。
2. **按功能点增量实现**：设计一次性做完，实现严格按 [09_feature_checklist.md](09_feature_checklist.md) 逐条推进，每条都有对应单元测试，测试通过才进入下一条。
3. **可扩展优先于一次做全**：新增一个数据源 / 一个 Agent / 一条规则，只应是"新增一个文件"，不应改动已有模块的内部结构。
4. **安全边界固定**：
   - 禁止硬编码任何 API Key，统一在 `config.yaml`（本地，不进 git）中配置。
   - 禁止编造数据；接口失败一律走 `api_adapter` 降级 + 打标 `data_warning`，不编造财报/新闻/行情。
   - 系统只输出分析结论，**不接入任何券商 / 基金软件下单通道**。
5. **先 CLI 后 UI**：「Daily Button / Weekly Button」第一阶段用 CLI 命令实现（`fund daily` / `fund weekly`），跑通全链路后再按需加最小化本地 Web UI，不本末倒置先做 UI。
6. **数据驱动优先（系统最核心的资产）**：分析结论应尽量引用 `knowledge_base` 中沉淀的真实历史操作/经验教训/长期市场规律，而不是单纯依赖 LLM 当场生成；其中 `market_patterns`（近几十年市场运行规律）只能人工审阅后入库，系统日常流程不自动写入，避免幻觉污染长期参考层。详见 [10_knowledge_base.md](10_knowledge_base.md)。

## 技术选型

| 项            | 选择                              | 理由                                                            |
| ------------- | --------------------------------- | --------------------------------------------------------------- |
| 语言          | Python 3.11+                      | 与仓库现有 `task/5_music` 一致，生态适合数据处理 + 轻量 AI 调用 |
| 包管理 / 运行 | `uv`                              | 仓库既有约定（见 `task/5_music/README.md`），免全局安装依赖     |
| 数据模型      | `pydantic` v2                     | 字段校验 + JSON 序列化一步到位，错误信息清晰，便于单测断言      |
| 存储格式      | JSON（单条记录）/ JSONL（流水账） | 无需引入数据库，符合"保持简单"的仓库总原则                      |
| 测试          | `pytest`                          | 标准、仓库其余 Python 任务也适用                                |
| LLM 调用      | 统一经 `llm.py` 薄封装            | Provider 可替换，不在业务代码里直连某个 SDK                     |

## 文档索引

| 文档                                                       | 内容                                                                                  |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| [01_directory_structure.md](01_directory_structure.md)     | 完整目录结构 + 每类文件的扩展方式                                                     |
| [02_config.md](02_config.md)                               | `config.yaml` 字段规范与校验规则                                                      |
| [03_data_model.md](03_data_model.md)                       | 全部数据模型定义与落盘格式                                                            |
| [04_api_adapter.md](04_api_adapter.md)                     | 接口自适应容错状态机设计                                                              |
| [05_agents_skills_prompts.md](05_agents_skills_prompts.md) | Agents / Prompts / 数据源 的调用关系与扩展规范                                        |
| [06_daily_weekly_flow.md](06_daily_weekly_flow.md)         | Daily / Weekly 两条主流程时序                                                         |
| [07_cli_and_ui.md](07_cli_and_ui.md)                       | CLI 按钮设计 + 后续 UI 扩展路径                                                       |
| [08_testing_strategy.md](08_testing_strategy.md)           | 测试分层策略与每个模块的测试要点                                                      |
| [09_feature_checklist.md](09_feature_checklist.md)         | **实现执行清单**：功能点拆解 + 验收标准（后续按此逐条实现）                           |
| [10_knowledge_base.md](10_knowledge_base.md)               | **数据积累与知识库设计**：历史操作、经验教训、长期市场规律——系统的核心资产层          |
| [11_web_ui.md](11_web_ui.md)                               | **Web UI 详细设计（Optional）**：登录流程、主页面布局、TODO 小窗口、Weekly 指定周参数 |

## 非目标（明确不做）

- 不自动对接券商 / 基金交易软件下单（用户已明确标注"目前先不做"，后续独立量化平台）。
- 不做分布式 / 多用户系统，默认单用户本地运行。
- 不引入数据库（SQLite 都不用），JSON/JSONL 文件足够当前数据量。
- 第一阶段不做图形界面，CLI 即可满足"按一次按钮"的交互诉求。
