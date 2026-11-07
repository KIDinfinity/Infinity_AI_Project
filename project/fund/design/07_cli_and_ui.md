# 07. CLI 按钮设计 + 后续 UI 扩展

## 第一阶段：CLI 即「按钮」

```bash
cd project/fund
uv run fund daily              # 等价于【Daily Button】
uv run fund weekly             # 等价于【Weekly Button】
uv run fund daily --fund-code 000001   # 可选：只跑单只基金，便于调试
uv run fund weekly --week 2026-W43     # 可选：手动指定复盘周，便于补跑
uv run fund record-operation --fund-code 000001 --type 卖出 --date 2026-11-07 --amount 10000 --price 1.234
```

`record-operation` 是第三个子命令，用于手工录入真实买卖（`ActualOperation`，见 [03_data_model.md](03_data_model.md) 6.1），与前两个自动化命令不同，它不调用任何 AI/LLM，纯本地读写。

`cli.py` 用标准库 `argparse`（不引入额外 CLI 框架依赖，保持简单），三个子命令分别调用 `orchestrator.run_daily` / `orchestrator.run_weekly` / `storage.append_actual_operation`，打印：

- 本次是否有数据降级（汇总 `data_warning` 非空的基金列表）。
- 落盘文件路径。
- 关键结论摘要（止盈信号数 / 暴涨预警数 / 暴跌预警数）。

退出码：全部成功 `0`；有部分数据源降级但流程完成 `0`（降级是预期的容错路径，不是失败）；流程异常中断 `1`。

## 为什么不first做图形界面

- 个人单用户场景，CLI 完全满足"每天点一次 / 每周点一次"的交互需求。
- 符合仓库"保持简单"的总原则，避免过早引入前端框架、服务进程、端口占用等复杂度。
- CLI 天然适合写集成测试（`subprocess` 或直接调用 `main(argv)` 函数断言输出/落盘结果）。

## 后续可选扩展（Feature checklist 中标为 Optional，非必须）

若后续确实需要可视化/移动端快捷触发，按以下顺序渐进扩展，**每一步都复用 `orchestrator.py` 现成函数，不重写业务逻辑**：

1. **本地单页 Web UI**（含登录流程、TODO 小窗口、Weekly 可指定周）：详细设计见 [11_web_ui.md](11_web_ui.md)，不在本文档重复展开。
2. **macOS 快捷指令 / Shell 脚本桌面图标**：直接包一层调用 `uv run fund daily`，双击触发，无需常驻服务。
3. **定时任务**：`cron` 或 `launchd` 按工作日自动跑 `fund daily`，复盘日自动跑 `fund weekly`（需用户确认后再配置，涉及系统级定时任务，属于"影响较大的改动"）。

这些扩展全部放在 Feature checklist 的 Phase 7（Optional），不在首轮实现范围内。
