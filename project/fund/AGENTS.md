# AGENTS.md — project/fund 执行入口

> 本文件是 `project/fund/` 这**一个独立项目**的唯一执行入口。新开一个对话时，只需要告诉大模型"按 `project/fund/AGENTS.md` 跑这个 project"，即可无损恢复上下文、接着往下推进，不需要每次重新粘贴设计文档。

## 0. 这是什么

短线基金 AI 分析决策系统：每天/每周跑一次，拉数据、跑分析、给出持有/止盈/预警建议，**只输出建议，不自动下单**。

## 1. 它在整个仓库里的位置（重要，不要越界）

- 本仓库根目录是「半年数字资产项目」，当前 DA-01 = `WorkPilot`（见仓库根 `GLOBAL_CONTEXT.md` / `PROJECT_CONFIG.md`）。
- `project/fund` **不是 DA-01**，是 `project/` 目录下**独立的一个** side project（`project/` 之下未来可能有其他项目，彼此独立）。
- 执行本项目任务时：
  - **只**读写 `project/fund/` 目录内的文件；
  - **不要**修改仓库根 `GLOBAL_CONTEXT.md`、`PROJECT_CONFIG.md`、`plan/` 等 DA-01 相关文件；
  - **不要**顺带碰 `project/` 下其他同级项目目录。

## 2. 执行任何任务前必须读（按顺序，第 1 条每次都不能跳过）

1. [GLOBAL_CONTEXT.md](GLOBAL_CONTEXT.md) — **全局上下文，不论任务大小，每次操作前都必须读取**；后续新增的全局规则都会追加在这个文件里
2. [design/00_overview.md](design/00_overview.md) — 项目定位、设计原则、技术选型
3. [design/09_feature_checklist.md](design/09_feature_checklist.md) — **进度唯一来源**，找到第一条未勾选 `[ ]` 的功能点
4. 该功能点关联的具体设计文档章节（`design/01` ~ `design/10`，按功能点描述里引用的文档去读）

## 3. 每次推进的工作流程

1. 打开 [design/09_feature_checklist.md](design/09_feature_checklist.md)，定位第一条 `[ ]` 未完成项（不允许跳着做，标 Optional 的除外）。
2. 读该条涉及的设计章节，确认函数签名 / 数据模型 / 验收标准。
3. 实现代码 + 配套单元测试（同一批次完成，不拆开）。
4. `cd project/fund && uv run pytest` 全绿。
5. 把该条 checklist 勾选为 `[x]`。
6. 过一遍下面第 4 节的硬约束自查清单，再进入下一条。

## 4. 硬约束自查清单（每次改动前后都要过一遍）

- [ ] 没有在任何代码/文档里硬编码 API Key（一律走 `config.yaml`，见 [design/02_config.md](design/02_config.md)）。
- [ ] 没有编造任何财报/新闻/行情/基金数据；接口失败一律走 `api_adapter` 降级并标注 `data_warning`（见 [design/04_api_adapter.md](design/04_api_adapter.md)）。
- [ ] 没有引入任何自动下单 / 对接券商的代码路径。
- [ ] 暴跌风险预警优先级高于止盈规则这条合并逻辑没有被破坏（见 [design/06_daily_weekly_flow.md](design/06_daily_weekly_flow.md)）。
- [ ] 新增能力是"新增一个文件"，没有改动已有模块的内部结构（扁平化、可扩展原则，见 [design/01_directory_structure.md](design/01_directory_structure.md)）。
- [ ] 没有让 daily/weekly 自动流程写入 `data/knowledge_base/market_patterns/`（这一层只允许人工审阅后入库，见 [design/10_knowledge_base.md](design/10_knowledge_base.md)）。
- [ ] 若涉及 Web UI（F7.3）：没有把 `web.host` 擅自改成 `0.0.0.0`，没有在任何地方存明文密码（只存 `password_hash`），见 [design/11_web_ui.md](design/11_web_ui.md)。
- [ ] 新增的功能点有对应单元测试，且 `uv run pytest` 全绿。

## 5. 目录速查（一句话版，详细见 [design/01_directory_structure.md](design/01_directory_structure.md)）

| 目录/文件           | 作用                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| `GLOBAL_CONTEXT.md` | **每次操作都必须先读**，持续追加的全局规则                                                             |
| `design/`           | 全部设计文档，先读这里                                                                                 |
| `src/fund/`         | 源码：config / models / storage / adapter / llm / rules / knowledge / sources / agents / prompts / cli |
| `data/`             | 落盘数据：原始数据、每日/每周分析记录、真实操作记录、知识库                                            |
| `tests/`            | 单元测试，与 Feature checklist 的 Phase 一一对应                                                       |
| `config.yaml`       | 本地真实配置（不进 git），从 `config.example.yaml` 复制而来                                            |

> 每个目录下都有一份简短 `README.md` 说明该目录的用途，细节不在这里重复。

## 6. 进度唯一来源

[design/09_feature_checklist.md](design/09_feature_checklist.md)。不要另建进度文档、不要在其他地方重复记录"做到哪了"。
