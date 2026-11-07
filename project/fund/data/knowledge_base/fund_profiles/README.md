# fund_profiles/ 目录说明

每只基金一个 JSON 文件（`FundProfile`，含 `ProfileObservation` 历史观察列表）。由 `knowledge.py::upsert_fund_profile` 在每日分析后自动追加观察、整份覆盖写回。格式见 [../../../design/03_data_model.md](../../../design/03_data_model.md) 第 6.3 节。
