# 短线基金 AI 分析平台 · fund

个人工程 / C 线独立 side project，**不是** DA-01（WorkPilot），不占用 DA-01 开发时间预算。

> 只输出分析建议，不自动下单交易。

## 唯一执行入口

跟大模型说一声"按 [AGENTS.md](AGENTS.md) 跑这个 project"即可，无需每次重新粘贴设计文档。[AGENTS.md](AGENTS.md) 会要求每次操作前先读 [GLOBAL_CONTEXT.md](GLOBAL_CONTEXT.md)（全局规则，持续追加，例如未来要加的"每次操作记一条日志"之类的要求就加在那里）。

## 先看设计

实现前请先完整阅读 [design/](design/)，尤其是：

1. [design/00_overview.md](design/00_overview.md) — 项目定位、设计原则、技术选型
2. [design/10_knowledge_base.md](design/10_knowledge_base.md) — 数据积累与知识库设计（历史操作/经验教训/长期市场规律，系统最核心的资产层）
3. [design/09_feature_checklist.md](design/09_feature_checklist.md) — **按此清单逐条实现 + 写单测**，不要跳跃

其余文档（目录结构、配置、数据模型、容错适配器、Agent/Prompt 规范、Daily/Weekly 流程、CLI/UI、测试策略）见 [design/](design/) 目录索引。

## 快速开始（骨架搭好、Phase 0 开始实现后可用）

```bash
cd project/fund
cp config.example.yaml config.yaml   # 按需填入真实 api_key / endpoint
uv sync                              # 安装依赖
uv run pytest                        # 跑单元测试
uv run fund daily                    # 【Daily Button】等价命令（Phase 6 实现后可用）
uv run fund weekly                   # 【Weekly Button】等价命令（Phase 6 实现后可用）
```

## 目录速览

```text
project/fund/
├── AGENTS.md          # 执行入口（先读这里）
├── GLOBAL_CONTEXT.md  # 全局上下文（每次操作都必须读，持续追加规则）
├── design/      # 设计文档
├── src/fund/    # 源码
├── data/        # 结构化落盘数据 + 知识库
├── tests/       # 单元测试
├── config.example.yaml  # 配置模板（可提交）
└── config.yaml           # 真实配置（本地，不提交）
```

> 每个目录下都有一份简短 `README.md` 说明用途。

## 当前进度

跟踪见 [design/09_feature_checklist.md](design/09_feature_checklist.md)，当前处于 **Phase 0（骨架）尚未开始**。
