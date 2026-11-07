# sources/ 目录说明

外部数据源 client，一个数据源一个文件：`fund_info.py`、`stock_financial.py`、`macro_data.py`、`industry_news.py`。统一通过 `../adapter.py` 做容错降级，不直接裸发 HTTP 请求。设计见 [../../../design/01_directory_structure.md](../../../design/01_directory_structure.md) 与 [../../../design/04_api_adapter.md](../../../design/04_api_adapter.md)。
