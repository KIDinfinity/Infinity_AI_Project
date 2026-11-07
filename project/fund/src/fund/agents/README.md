# agents/ 目录说明

编排/分析逻辑，一个职责一个文件：`orchestrator.py`（daily/weekly 总调度）、`position_analyst.py`、`bull_scanner.py`、`risk_alert.py`、`weekly_reviewer.py`。分析前调用 `../knowledge.py` 取知识上下文，分析/复盘后调用 `../knowledge.py` 写回新知识。设计见 [../../../design/05_agents_skills_prompts.md](../../../design/05_agents_skills_prompts.md)。
