"""`cli.py` 单元测试，对应 design/09_feature_checklist.md F2.5.5 / F6.1。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fund import cli, storage


def test_record_operation_persists_actual_operation_without_network_calls(
    tmp_data_root: Path, monkeypatch
) -> None:
    # 任何网络/LLM 调用都应该报错失败，确保 record-operation 纯本地读写。
    def _fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("record-operation 不应该发起网络/LLM 调用")

    monkeypatch.setattr("httpx.get", _fail_if_called, raising=False)
    monkeypatch.setattr("httpx.post", _fail_if_called, raising=False)

    exit_code = cli.main(
        [
            "record-operation",
            "--fund-code",
            "000001",
            "--type",
            "卖出",
            "--date",
            "2026-11-07",
            "--amount",
            "10000",
            "--price",
            "1.234",
        ]
    )

    assert exit_code == 0
    operations = storage.load_actual_operations()
    assert len(operations) == 1
    operation = operations[0]
    assert operation.fund_code == "000001"
    assert operation.operation_type == "卖出"
    assert operation.operation_date.isoformat() == "2026-11-07"
    assert operation.amount == 10000.0
    assert operation.amount_unit == "金额"
    assert operation.price_or_nav == 1.234
    assert operation.operation_id.startswith("OP-000001-2026-11-07-")


def test_record_operation_supports_amount_unit_and_note(tmp_data_root: Path) -> None:
    exit_code = cli.main(
        [
            "record-operation",
            "--fund-code",
            "000002",
            "--type",
            "加仓",
            "--date",
            "2026-11-08",
            "--amount",
            "500",
            "--amount-unit",
            "份额",
            "--price",
            "2.1",
            "--related-signal-id",
            "SIG-001",
            "--note",
            "补仓",
        ]
    )

    assert exit_code == 0
    operations = storage.load_actual_operations()
    assert len(operations) == 1
    operation = operations[0]
    assert operation.amount_unit == "份额"
    assert operation.related_signal_id == "SIG-001"
    assert operation.note == "补仓"


# ---------------------------------------------------------------------------
# F6.1 fund daily / fund weekly
# ---------------------------------------------------------------------------


def test_cli_daily_persists_analysis_from_recorded_operations(tmp_data_root: Path) -> None:
    exit_code = cli.main(
        [
            "record-operation",
            "--fund-code",
            "000001",
            "--type",
            "买入",
            "--date",
            "2020-01-01",
            "--amount",
            "10000",
            "--price",
            "1.0",
        ]
    )
    assert exit_code == 0

    exit_code = cli.main(["daily"])
    assert exit_code == 0

    records = storage.load_daily_analysis(date.today())
    assert len(records) == 1
    assert records[0].fund_code == "000001"


def test_cli_daily_fund_code_filter_skips_funds_not_currently_held(tmp_data_root: Path) -> None:
    exit_code = cli.main(["daily", "--fund-code", "000099"])

    assert exit_code == 0
    assert storage.load_daily_analysis(date.today()) == []


def test_cli_weekly_reads_this_week_analysis_log_and_saves_review(tmp_data_root: Path) -> None:
    cli.main(
        [
            "record-operation",
            "--fund-code",
            "000001",
            "--type",
            "买入",
            "--date",
            "2020-01-01",
            "--amount",
            "10000",
            "--price",
            "1.0",
        ]
    )
    cli.main(["daily"])

    iso_year, iso_week, _ = date.today().isocalendar()
    review_week = f"{iso_year}-W{iso_week:02d}"

    exit_code = cli.main(["weekly", "--week", review_week])

    assert exit_code == 0
    data_root = tmp_data_root
    assert (data_root / "weekly_review_log" / f"{review_week}-review.json").is_file()
    assert (data_root / "weekly_review_log" / f"{review_week}-review.md").is_file()
