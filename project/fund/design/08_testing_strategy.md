# 08. 测试策略

## 原则

- 每个 feature checklist 条目落地时，**同一提交内必须带对应单测**，测试不过不进入下一条（呼应用户"单元测试稳步进行"的要求）。
- 纯逻辑模块（`rules.py`、`models.py`、`adapter.py` 状态机）要求高覆盖率、无需 mock 网络。
- 涉及外部依赖（HTTP、LLM）的模块，一律通过依赖注入的方式在测试中替换为 fake 实现，**单测不发真实网络请求、不消耗真实 API 额度**。

## 分层测试矩阵

| 模块              | 测试类型                   | 关键用例                                                                                                                                                                                                                                                                                           |
| ----------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config.py`       | 单元                       | 合法配置加载成功；缺字段报错；`${ENV}` 占位符正确替换；环境变量未设置时字段为空不崩溃                                                                                                                                                                                                              |
| `models.py`       | 单元                       | 合法数据构造成功；`confidence` 超出 `[0,100]` 报错；JSON 序列化/反序列化往返一致                                                                                                                                                                                                                   |
| `storage.py`      | 单元                       | 写入后能读回且内容一致；JSONL 追加不覆盖已有行；按日期/周号生成的文件名符合约定                                                                                                                                                                                                                    |
| `adapter.py`      | 单元（覆盖状态机每条分支） | 200 直接成功；401 不重试直接失败；429 退避后成功；5xx 重试耗尽后切备用；备用也失败后降级返回；格式异常触发精简 payload；精简后仍失败走降级；每条分支都验证 `append_api_error_log` 被正确调用                                                                                                       |
| `rules.py`        | 单元                       | 止盈规则：收益<10% 不触发；=10% 触发；持有<30天但手续费覆盖时触发豁免，并核对返回的说明文案；暴涨置信度边界（69/70/71）三种结果；`crash_priority_over_profit` 恒为真                                                                                                                               |
| `sources/*.py`    | 单元                       | 用 fake `request_fn` 验证参数组装正确、能正确透传 `adapter` 返回的降级标记                                                                                                                                                                                                                         |
| `knowledge.py`    | 单元                       | `upsert_fund_profile` 追加观察不覆盖旧记录；`query_lessons` 按 `tags`/`applicable_scope` 过滤正确且排除 `status="deprecated"`；`match_market_patterns` 命中/不命中两类用例                                                                                                                         |
| `agents/*.py`     | 单元 + 小型集成            | 用 `llm.py` 的 `"fake"` provider + fake 数据源，验证组装出的 `AnalysisRecord`/`BullAlert`/`CrashRisk`/`WeeklyReview` 字段符合预期；验证 `data_warning` 非空时置信度被正确封顶；验证 prompt 含 `knowledge_context`、`weekly_reviewer` 产出的 `new_analysis_factors` 被正确转成 `LessonLearned` 写入 |
| `orchestrator.py` | 集成                       | 端到端跑 `run_daily`/`run_weekly`（全部依赖 fake），断言落盘文件存在且内容可被 `storage` 读回；断言"暴跌优先于止盈"的合并逻辑生效                                                                                                                                                                  |
| `cli.py`          | 集成                       | 调用 `main(["daily"])` / `main(["weekly"])` / `main(["record-operation", ...])`，断言退出码、标准输出关键字段、落盘文件                                                                                                                                                                            |

## Fixture 约定（`tests/conftest.py`）

- `tmp_config(tmp_path)`：生成一份写入临时目录的 `config.yaml`（`data_root` 指向 `tmp_path`），避免测试污染真实 `data/` 目录。
- `fake_llm_provider`：返回固定 JSON 字符串，覆盖各 agent 期望的输出结构。
- `fake_request_fn_factory(status_sequence: list[int | Exception])`：按调用顺序依次返回指定状态码/异常，用于精确构造 `adapter` 的各种分支。

## 工具与命令

```bash
cd project/fund
uv run pytest                     # 跑全部单测
uv run pytest tests/test_adapter.py -v   # 跑单个模块，便于按 feature checklist 逐条验证
uv run pytest --cov=src/fund             # 可选：覆盖率（后续按需加 pytest-cov 依赖）
```

## 验收口径（贯穿整个 feature checklist）

一个功能点被视为"完成"，当且仅当：

1. 对应函数/模块按设计文档的签名实现；
2. 新增的单测全部通过，且覆盖设计文档里列出的关键分支/边界用例；
3. `uv run pytest` 全量跑通（不允许新功能导致既有测试变红）；
4. 不引入未在 `config.yaml` 中声明的硬编码密钥或魔法数字（阈值类数字必须来自 `config`）。
