# 01. 目录结构设计

## 总体结构

```text
project/fund/
├── README.md                  # 项目说明、快速开始
├── pyproject.toml             # uv 项目定义 + 依赖声明
├── config.example.yaml        # 配置模板（可提交）
├── config.yaml                # 实际配置，含真实 key（gitignore，不提交）
├── design/                    # 设计文档（本目录）
├── src/
│   └── fund/
│       ├── __init__.py
│       ├── config.py          # 加载 + 校验 config.yaml
│       ├── models.py          # 全部 pydantic 数据模型
│       ├── storage.py         # 记录读写（JSON / JSONL）
│       ├── knowledge.py       # 知识库检索/匹配/沉淀（lessons_learned、fund_profiles、market_patterns、actual_operations 的业务层）
│       ├── adapter.py         # api_adapter 容错核心逻辑
│       ├── llm.py             # LLM 调用薄封装（provider 可替换）
│       ├── rules.py           # base_rule 纯函数（止盈/暴涨/暴跌阈值判断）
│       ├── cli.py             # 命令行入口（daily / weekly "按钮"）
│       ├── sources/           # 数据源 client，一个数据源一个文件
│       │   ├── __init__.py
│       │   ├── fund_info.py       # fetch_fund_info
│       │   ├── stock_financial.py # fetch_stock_financial
│       │   ├── macro_data.py      # fetch_macro_data
│       │   └── industry_news.py   # fetch_industry_news
│       ├── agents/            # 编排/分析逻辑，一个职责一个文件
│       │   ├── __init__.py
│       │   ├── orchestrator.py    # 总调度：daily / weekly 入口函数
│       │   ├── position_analyst.py
│       │   ├── bull_scanner.py
│       │   ├── risk_alert.py
│       │   └── weekly_reviewer.py
│       └── prompts/           # Prompt 模板（纯文本/markdown，带 {变量} 占位）
│           ├── daily_analysis.md
│           ├── weekly_improve.md
│           ├── bull_scanner.md
│           └── risk_alert.md
├── data/
│   ├── raw_data/               # 原始数据 + api_error_log.json（只读不改）
│   ├── analysis_log/           # 每日分析 JSON，一天一个文件 YYYY-MM-DD.json
│   ├── trade_decision/         # 买卖信号记录，JSONL 流水账
│   ├── weekly_review_log/      # 每周复盘报告，YYYY-WW-review.md + .json
│   ├── performance_db/         # 预测效果数据集，JSONL 流水账
│   ├── actual_operations/      # 用户真实买卖操作记录（手工录入），按月分文件 JSONL
│   └── knowledge_base/         # 知识沉淀层：历史经验 + 长期市场规律（见 design/10_knowledge_base.md）
│       ├── fund_profiles/      # 每只基金的经验画像，一基金一个 JSON 文件
│       ├── lessons_learned/    # 从复盘提炼的结构化教训，JSONL 追加写入
│       └── market_patterns/    # 近几十年市场规律参考库，人工维护为主
└── tests/
    ├── conftest.py              # 公共 fixture（临时 config / 临时 data 目录）
    ├── test_config.py
    ├── test_models.py
    ├── test_storage.py
    ├── test_adapter.py
    ├── test_rules.py
    ├── test_sources.py
    ├── test_knowledge.py
    ├── test_agents.py
    └── test_cli.py
```

## 扩展点（新增能力时，只新增文件，不改既有模块）

| 想要新增                             | 怎么做                                                                                                                         | 不应该做                                                         |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| 一个新数据源（如基金评级）           | 在 `sources/` 新增 `fund_rating.py`，暴露 `fetch_fund_rating(adapter, params) -> dict`                                         | 不要在 `orchestrator.py` 里直接写抓取逻辑                        |
| 一条新规则（如"连续下跌 N 天提醒"）  | 在 `rules.py` 新增一个纯函数 + 对应单测                                                                                        | 不要把规则逻辑写进 agent 文件里                                  |
| 一个新分析角色（如"行业轮动分析师"） | 在 `agents/` 新增 `sector_rotation.py`，复用 `llm.py` + `prompts/`                                                             | 不要复制整个 orchestrator                                        |
| 一个新 Prompt                        | 在 `prompts/` 新增 `.md` 文件，agent 里用 `load_prompt("xxx")` 加载                                                            | 不要把 prompt 文本内联写在 `.py` 里                              |
| 一种新的存储记录类型                 | 在 `models.py` 新增 pydantic 模型 + 在 `storage.py` 新增对应读写函数                                                           | 不要绕过 `storage.py` 直接 `open()` 写文件                       |
| 新的 UI（Web 按钮）                  | 新增 `src/fund/web.py` 或独立 `ui/` 目录，调用 `agents.orchestrator` 里现成的函数                                              | 不要把业务逻辑写进 UI 层                                         |
| 一条新的长期市场规律                 | 人工审阅后直接编辑 `data/knowledge_base/market_patterns/patterns.json` 新增一条 `MarketPatternEntry`                           | 不要让 daily/weekly 自动流程写入这个文件，避免幻觉污染长期参考层 |
| 一条可复用的教训                     | `weekly_reviewer` 产出 `new_analysis_factors` 后自动调用 `knowledge.append_lesson(...)` 落成 `LessonLearned`；也可人工直接追加 | 不要只写在 `weekly_review_log` 的自然语言里就结束                |

## 为什么不按原 draft 的 `agents/main_orchestrator/`、`skills/api_adapter/` 这种"每个能力一个文件夹"设计

- 当前规模下每个 Agent / Skill 逻辑体量很小（几十到两百行），用文件夹会产生大量空嵌套、增加查找成本。
- 扁平化后，`agents/`、`sources/`、`prompts/` 三个目录内直接按文件名区分职责，IDE 内一屏可见全部能力清单。
- 真的某个模块长大到需要拆分（如 `orchestrator.py` 超过 300 行），再拆成 `orchestrator/` 目录，这是后置决策，不提前做。

## 原 draft 中 `mcp/`、`skills/api_adapter/` 等概念的落位

| draft 中的概念                    | 本设计中的落位                                                                                                              |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `skills/api_adapter/`             | `src/fund/adapter.py`                                                                                                       |
| `skills/fund_holding_analysis` 等 | 融合进 `agents/position_analyst.py` + `rules.py`                                                                            |
| `mcp/*.json`（工具声明）          | 暂不单独做 MCP 协议层；`sources/*.py` 的函数签名即工具声明，后续若要接 MCP server，再在 `sources/` 外包一层，不影响现有结构 |
| `prompts/`（拆分版单 prompt）     | `src/fund/prompts/*.md`，与原 draft 目录同名、位置略调整到 `src/fund` 下以便 `agents/` 直接 import 路径加载                 |
