# actual_operations/ 目录说明

用户真实买卖操作记录（`ActualOperation`），**手工录入**（`fund record-operation` 命令），按月分文件 JSONL 追加写入。与 [../trade_decision/](../trade_decision/)（系统建议）严格区分，用于日后对比"建议 vs 真实操作"。格式见 [../../design/03_data_model.md](../../design/03_data_model.md) 第 6.1 节。
