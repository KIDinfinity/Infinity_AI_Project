"""命令行入口，按钮化交互。

详见 ../../design/07_cli_and_ui.md。三个子命令：

- `fund daily [--fund-code]`：调用 `orchestrator.run_daily`。持仓清单由
  `orchestrator.build_holdings_from_operations` 从 `actual_operations` 流水重建
  （见该函数文档说明的加权平均成本法简化）；`--fund-code` 时只跑这一只基金。
- `fund weekly [--week]`：调用 `orchestrator.run_weekly`。`--week` 缺省时用
  `orchestrator.compute_default_week` 取"当前自然周的上一周"；`analysis_records`/
  `trade_decisions` 从 `storage.py` 按周读取拼接；`real_nav_data` 目前没有历史净值
  数据源，固定传空 dict（`performance_db` 回填会相应留空，见 orchestrator.py 模块
  文档的说明）。
- `fund record-operation`：手工录入真实买卖操作（`ActualOperation`），纯本地读写，
  不调用任何 AI/LLM、不发网络请求。
"""

from __future__ import annotations

import argparse
import uuid
from datetime import date

from fund import storage
from fund.agents import orchestrator
from fund.config import load_config
from fund.models import ActualOperation


def _generate_operation_id(fund_code: str, operation_date: date) -> str:
    return f"OP-{fund_code}-{operation_date.isoformat()}-{uuid.uuid4().hex[:8]}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fund")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily", help="跑每日持仓研判（对应 Daily Button）")
    daily.add_argument("--fund-code", dest="fund_code", default=None)

    weekly = subparsers.add_parser("weekly", help="跑每周复盘（对应 Weekly Button）")
    weekly.add_argument("--week", dest="week", default=None)

    record_operation = subparsers.add_parser(
        "record-operation", help="手工录入真实买卖操作（不调用 AI/LLM）"
    )
    record_operation.add_argument("--fund-code", required=True)
    record_operation.add_argument(
        "--type",
        required=True,
        dest="operation_type",
        choices=["买入", "卖出", "加仓", "减仓"],
    )
    record_operation.add_argument("--date", required=True, dest="operation_date")
    record_operation.add_argument("--amount", required=True, type=float)
    record_operation.add_argument(
        "--amount-unit", dest="amount_unit", choices=["金额", "份额"], default="金额"
    )
    record_operation.add_argument("--price", required=True, type=float, dest="price_or_nav")
    record_operation.add_argument("--related-signal-id", dest="related_signal_id", default=None)
    record_operation.add_argument("--note", default="")

    return parser


def _handle_daily(args: argparse.Namespace) -> int:
    config = load_config()
    as_of = date.today()

    holdings = orchestrator.build_holdings_from_operations(config, as_of)
    if args.fund_code:
        holdings = [h for h in holdings if h["fund_code"] == args.fund_code]
        if not holdings:
            print(f"未在当前持仓中找到基金代码 {args.fund_code}，跳过本次研判。")
            return 0

    records = orchestrator.run_daily(config=config, holdings=holdings, as_of=as_of)

    warned_funds = [record.fund_code for record in records if record.data_warning]
    profit_taking = sum(1 for record in records if record.final_decision == "止盈卖出")
    surge_alerts = sum(1 for record in records if record.bull_alert.is_surge)
    crash_alerts = sum(1 for record in records if record.crash_risk.is_crash)

    print(f"本次研判 {len(records)} 只基金（{as_of.isoformat()}）。")
    if warned_funds:
        print(f"数据降级基金：{', '.join(warned_funds)}")
    print(f"止盈信号 {profit_taking} 个，暴涨预警 {surge_alerts} 个，暴跌预警 {crash_alerts} 个。")
    print(f"落盘路径：data/analysis_log/{as_of:%Y-%m-%d}.json")
    return 0


def _handle_weekly(args: argparse.Namespace) -> int:
    config = load_config()
    review_week = args.week or orchestrator.compute_default_week(date.today())

    analysis_records = orchestrator.load_week_analysis_records(review_week)
    trade_decisions = orchestrator.load_week_trade_decisions(review_week)

    review = orchestrator.run_weekly(
        config=config,
        review_week=review_week,
        analysis_records=analysis_records,
        real_nav_data={},
        trade_decisions=trade_decisions,
    )

    print(f"已完成 {review_week} 复盘：共 {review.total_predict} 条预测，准确率 {review.correct_rate:.0%}。")
    if review.new_analysis_factors:
        print(f"新增分析因子：{'；'.join(review.new_analysis_factors)}")
    print(f"落盘路径：data/weekly_review_log/{review_week}-review.json / .md")
    return 0


def _handle_record_operation(args: argparse.Namespace) -> int:
    operation_date = date.fromisoformat(args.operation_date)
    operation = ActualOperation(
        operation_id=_generate_operation_id(args.fund_code, operation_date),
        fund_code=args.fund_code,
        operation_date=operation_date,
        operation_type=args.operation_type,
        amount=args.amount,
        amount_unit=args.amount_unit,
        price_or_nav=args.price_or_nav,
        related_signal_id=args.related_signal_id,
        note=args.note,
    )
    storage.append_actual_operation(operation)
    print(
        f"已记录操作：{operation.operation_id}"
        f"（{operation.fund_code} {operation.operation_type}"
        f" {operation.amount}{operation.amount_unit} @ {operation.price_or_nav}）"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "daily":
        return _handle_daily(args)
    if args.command == "weekly":
        return _handle_weekly(args)
    if args.command == "record-operation":
        return _handle_record_operation(args)

    parser.error(f"未知子命令：{args.command}")
    return 1  # pragma: no cover - argparse.error 会直接退出进程


if __name__ == "__main__":
    raise SystemExit(main())
