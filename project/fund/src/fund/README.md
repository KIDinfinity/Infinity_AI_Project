# src/fund/ 目录说明

项目主 Python 包。顶层模块一个文件一个职责：`config.py`（配置加载）、`models.py`（pydantic 数据模型）、`storage.py`（读写落盘数据）、`knowledge.py`（知识库检索/匹配/沉淀）、`adapter.py`（接口容错核心）、`llm.py`（LLM 调用封装）、`rules.py`（止盈/暴涨/暴跌纯函数规则）、`cli.py`（命令行入口）。子目录说明见各自的 README。详细设计见 [../../design/01_directory_structure.md](../../design/01_directory_structure.md)。
