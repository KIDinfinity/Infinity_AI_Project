# 06. Daily / Weekly 主流程

## Daily（对应【Daily Button】）

```mermaid
sequenceDiagram
    participant U as 用户
    participant CLI as cli.py
    participant ORCH as orchestrator.run_daily
    participant KB as knowledge.py
    participant SRC as sources/*
    participant RULES as rules.py
    participant PA as position_analyst
    participant BS as bull_scanner
    participant RA as risk_alert
    participant ST as storage.py

    U->>CLI: fund daily
    CLI->>ORCH: run_daily(config)
    ORCH->>SRC: 拉取持仓/净值/财报/宏观/新闻（全部经 adapter）
    SRC-->>ORCH: 数据 + data_warning（如有降级）
    ORCH->>KB: get_knowledge_context(fund_code) 检索 fund_profile/lessons/patterns
    KB-->>ORCH: knowledge_context（供拼入 prompt）
    ORCH->>PA: 逐只基金：止盈校验 + 论证组装（带 knowledge_context）
    PA->>RULES: check_base_profit(...)
    RULES-->>PA: 持有/卖出 + 说明
    PA->>KB: upsert_fund_profile(fund_code, observation) 追加今日观察
    ORCH->>BS: 暴涨扫描（持仓 + 备选池，带 knowledge_context）
    BS->>RULES: classify_bull_alert(...)
    ORCH->>RA: 暴跌风险复核（读历史 analysis_log，带 knowledge_context）
    ORCH->>ORCH: 合并为 AnalysisRecord 列表
    ORCH->>ST: save_daily_analysis(records)
    ORCH->>ST: 若触发止盈/预警 -> append_trade_decision(...)
    ORCH-->>CLI: 当天报告摘要（自然语言 + 落盘路径）
    CLI-->>U: 打印结果
```

关键约束：

- 任一数据源降级（`adapter` 返回 `degraded=True`），对应 `AnalysisRecord.data_warning` 必须非空，且该基金当天结论不得输出"置信度 100% 的强推荐"（由 `rules.py` 统一兜底：`data_warning` 非空时，`bull_alert.confidence` 上限封顶，具体数值作为 feature 点实现时定，默认不超过 `confidence_threshold - 1`，即自动降为"观察"）。
- `risk_alert` 优先级高于止盈规则：`orchestrator` 合并结论时，若 `crash_risk.is_crash=True`，`final_decision` 固定取"减仓/清仓"分支，不被 `base_profit_signal="持有"` 覆盖。

## Weekly（对应【Weekly Button】）

```mermaid
sequenceDiagram
    participant U as 用户
    participant CLI as cli.py
    participant ORCH as orchestrator.run_weekly
    participant ST as storage.py
    participant WR as weekly_reviewer
    participant KB as knowledge.py

    U->>CLI: fund weekly
    CLI->>ORCH: run_weekly(config, week=None)
    ORCH->>ST: 读取本周全部 analysis_log + trade_decision
    ORCH->>WR: 生成复盘（命中率统计 + 误差分类 + 新增因子）
    WR-->>ORCH: WeeklyReview
    ORCH->>ST: save_weekly_review(review) -> (.json, .md)
    ORCH->>KB: append_lesson_from_review(review) 把 new_analysis_factors 转成结构化 LessonLearned
    ORCH->>ST: append_performance_record(...) 为本周每条预测回填 real_return/error
    ORCH-->>CLI: 复盘摘要 + 下周前置条件
    CLI-->>U: 打印结果
```

复盘产出的 `prompt_optimize_content` / `next_week_context` 作为**纯文本**存入 `WeeklyReview`，下次 `run_daily` 执行时由 `orchestrator` 读取最近一次 `weekly_review_log` 并拼入 `daily_analysis` 的 prompt 变量（如 `base_rule_text` 追加段落），形成闭环。**不自动改 `rules.py` 代码**——代码阈值调整仍需人工看复盘报告后手动改 `config.yaml`，避免 AI 自动改规则导致不可控。

`week` 参数说明：`week=None` 时 `orchestrator.run_weekly` 内部调用 `compute_default_week(date.today())` 取"当前自然周的上一周"（`YYYY-Www` 格式）；`cli.py` 的 `--week` 与 Web UI 的 `POST /api/weekly` 共用这同一个默认值计算函数，不各写一套。详细设计见 [11_web_ui.md](11_web_ui.md) 第 5 节。
