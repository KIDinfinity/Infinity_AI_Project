"""LLM 调用薄封装 + Prompt 模板加载/渲染。

详见 ../../design/05_agents_skills_prompts.md。`call_llm` 按 `config.llm.provider`
分发：`"fake"` 用于离线单测，返回固定占位 JSON 字符串，不发真实请求；`"openai"`
真实接入留到 feature checklist Phase 7（Optional），当前阶段抛 `NotImplementedError`
占位。`agents/*.py` 真正做单测时，不依赖这里的 `"fake"` 占位内容，而是各自在函数
签名里注入 `call_llm_fn: Callable[[AppConfig, str], str] = call_llm` 参数，测试里传入
返回特定 JSON 的 fake 函数（与 `adapter.py` 的 `request_fn` 注入方式同一套约定）。

`load_prompt(name, **variables) -> str` 加载 `prompts/{name}.md`，替换 `{{var}}`
占位符；渲染后仍残留未替换的占位符会直接报错，避免漏传变量导致模板"看起来成功但内容有坑"。
"""

from __future__ import annotations

import re
from pathlib import Path

from fund.config import AppConfig

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
_PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")

_FAKE_RESPONSE = "{}"


def call_llm(config: AppConfig, prompt: str) -> str:
    provider = config.llm.provider
    if provider == "fake":
        return _FAKE_RESPONSE
    if provider == "openai":
        raise NotImplementedError("真实 openai provider 接入见 feature checklist Phase 7（Optional），当前阶段未实现")
    raise ValueError(f"不支持的 llm.provider: {provider!r}")


def load_prompt(name: str, **variables: object) -> str:
    template_path = _PROMPTS_DIR / f"{name}.md"
    template = template_path.read_text(encoding="utf-8")

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            return match.group(0)
        return str(variables[key])

    rendered = _PLACEHOLDER_PATTERN.sub(_replace, template)

    missing = sorted(set(_PLACEHOLDER_PATTERN.findall(rendered)))
    if missing:
        raise ValueError(f"prompt 模板 {name!r} 缺少变量: {missing}")

    return rendered
