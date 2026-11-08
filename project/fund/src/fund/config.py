"""配置加载与校验。

详细规范见 ../../design/02_config.md。

- 所有 API Key / 接口地址 / 策略阈值统一从 config.yaml 读取，代码中不允许出现字面量 key。
- 支持 `${ENV_VAR}` 占位符，加载时替换为对应环境变量；未设置时视为空字符串，不崩溃。
- `path.data_root` 会在加载时解析为绝对路径（相对配置文件所在目录），供 storage.py 统一使用。
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

# project/fund/ 目录（本文件位于 project/fund/src/fund/config.py）
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATTERN = re.compile(r"\$\{(\w+)\}")


class ConfigError(Exception):
    """配置文件缺失、解析失败或校验失败时抛出。"""


class StrategyConfig(BaseModel):
    base_profit_rate: float
    min_hold_days: int
    confidence_threshold: int
    surge_upper_target: float


class ApiEndpointConfig(BaseModel):
    endpoint: str
    api_key: str = ""
    timeout: int
    retry_max: int
    backup_endpoints: list[str] = Field(default_factory=list)


class ApiConfig(BaseModel):
    fund_data: ApiEndpointConfig
    stock_financial: ApiEndpointConfig
    macro_data: ApiEndpointConfig
    financial_news: ApiEndpointConfig


class ApiAdapterConfig(BaseModel):
    backoff_factor: float
    rate_limit_sleep: float
    auto_reduce_payload: bool
    enable_switch_backup: bool


class LlmConfig(BaseModel):
    provider: str
    model: str
    api_key: str = ""
    timeout: int


class PathConfig(BaseModel):
    data_root: str


class AppConfig(BaseModel):
    strategy: StrategyConfig
    api: ApiConfig
    api_adapter: ApiAdapterConfig
    llm: LlmConfig
    path: PathConfig


def _default_config_path() -> Path:
    env_path = os.environ.get("FUND_CONFIG_PATH")
    if env_path:
        return Path(env_path)
    return _PROJECT_ROOT / "config.yaml"


def _substitute_env(text: str) -> str:
    """将 `${ENV_VAR}` 替换为对应环境变量，未设置时替换为空字符串。"""
    return _ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), ""), text)


def load_config(path: str | Path | None = None) -> AppConfig:
    """加载并校验配置文件，返回 `AppConfig`。

    加载顺序：显式传入的 `path` > 环境变量 `FUND_CONFIG_PATH` > 默认
    `project/fund/config.yaml`。

    校验失败（必填字段缺失/类型错误）统一抛出 `ConfigError`，附带清晰的字段路径。
    """
    config_path = Path(path) if path is not None else _default_config_path()
    if not config_path.is_file():
        raise ConfigError(f"配置文件不存在：{config_path}")

    raw_text = config_path.read_text(encoding="utf-8")
    substituted = _substitute_env(raw_text)

    try:
        raw_data = yaml.safe_load(substituted) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"配置文件 YAML 解析失败：{exc}") from exc

    path_section = raw_data.get("path") or {}
    data_root = path_section.get("data_root")
    if data_root:
        resolved_root = (config_path.parent / data_root).resolve()
        path_section = {**path_section, "data_root": str(resolved_root)}
        raw_data["path"] = path_section

    try:
        return AppConfig(**raw_data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(loc) for loc in err['loc'])} : {err['msg']}"
            for err in exc.errors()
        )
        raise ConfigError(f"配置校验失败：{details}") from exc
