# project/fund 测试目录

按 [../design/08_testing_strategy.md](../design/08_testing_strategy.md) 的分层矩阵实现测试文件，与 [../design/09_feature_checklist.md](../design/09_feature_checklist.md) 的 Phase 一一对应。

实现顺序：`conftest.py` → `test_config.py` → `test_models.py` → `test_storage.py` → `test_adapter.py` → `test_rules.py` → `test_sources.py` → `test_knowledge.py` → `test_agents.py` → `test_cli.py`。
