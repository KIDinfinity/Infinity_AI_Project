"""`config.py` 单元测试，对应 design/09_feature_checklist.md F0.2。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund.config import AppConfig, ConfigError, load_config


def test_load_config_success(tmp_config: Path) -> None:
    config = load_config(tmp_config)

    assert isinstance(config, AppConfig)
    assert config.strategy.base_profit_rate == 0.10
    assert config.strategy.min_hold_days == 30
    assert config.api.fund_data.endpoint == "https://example.com/api/fund"
    assert config.llm.provider == "fake"
    assert Path(config.path.data_root) == (tmp_config.parent / "data").resolve()


def test_load_config_missing_field_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "strategy:\n  base_profit_rate: 0.10\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError):
        load_config(config_path)


def test_load_config_file_not_found_raises(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.yaml"

    with pytest.raises(ConfigError):
        load_config(missing_path)


def test_load_config_env_substitution(tmp_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FUND_API_KEY", "real-secret-key")

    config = load_config(tmp_config)

    assert config.api.fund_data.api_key == "real-secret-key"


def test_load_config_env_unset_becomes_empty_string(
    tmp_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FUND_API_KEY", raising=False)

    config = load_config(tmp_config)

    assert config.api.fund_data.api_key == ""
