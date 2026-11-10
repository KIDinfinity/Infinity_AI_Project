# HOW_TO_RUN — project/fund 启动指南

> 本文件回答一个问题：**怎么把这个项目跑起来、它现在能干什么、还缺什么。**
> 阅读前提：先读 [README.md](README.md) 和 [AGENTS.md](AGENTS.md)（项目定位与执行入口）。

---

## 0. 一句话定位

短线基金 AI 分析决策系统：每天/每周跑一次，拉数据、跑分析、给出「持有 / 止盈 / 暴跌预警」建议。**只输出建议，不自动下单交易。**

它是个人 side project（C 线），**不是** DA-01（WorkPilot），只在 `project/fund/` 目录内活动。

---

## 1. 当前真实形态（先纠正预期）

| 你的预期 | 实际情况 |
| -------- | -------- |
| 「应该有一个 UI」 | ❌ **当前没有 UI**，只有命令行（CLI）。Web UI 是 Phase 7 的 Optional 项 F7.3（设计已写好 [design/11_web_ui.md](design/11_web_ui.md)，但**尚未实现**，checklist 里还是 `[ ]`） |
| 「可以保存数据到 local」 | ✅ 是的，全部数据落盘到本地 `data/` 目录的 JSON 文件 |
| 「可以接 agent 去拿数据」 | ⚠️ 半对。内部**有** 4 个分析 agent + 1 个编排器（`src/fund/agents/`），但**数据源和 LLM 目前都是 fake 占位**（`llm.provider="fake"`，`sources/*.py` 返回样例数据）。真实数据源 / 真实 LLM 是 F7.1/F7.2，**尚未实现** |

**结论**：现在能跑通「录入操作 → 每日研判 → 每周复盘」的**完整本地闭环**，但分析结果是占位结构（fake LLM），不是真实行情驱动的结论。

---

## 2. 环境要求

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/)（本机已装：`uv 0.12.22`，路径 `/opt/homebrew/bin/uv`）
- 无外部服务依赖、无数据库、无端口占用（当前 CLI 形态）

---

## 3. 启动步骤（已实测跑通）

```bash
cd /Users/infinity/Documents/a_future/project/fund

# 1) 生成配置文件（必须，load_config 找不到 config.yaml 会直接报错）
cp config.example.yaml config.yaml
#    默认 llm.provider="fake"，api_key 的 ${...} 未设环境变量时替换为空串，不影响离线跑通

# 2) 安装依赖
uv sync

# 3) 跑单元测试（验证环境 OK，106 个用例应全绿）
uv run pytest
```

三步走完即可使用下面的命令。

> 配置文件加载顺序：显式传入 `--path` > 环境变量 `FUND_CONFIG_PATH` > 默认 `project/fund/config.yaml`。所有 API Key 一律走 `config.yaml`，代码里没有硬编码 key。

---

## 4. 三个命令（CLI 即「按钮」）

### 4.1 录入真实买卖操作（数据入口，不调用 AI）

```bash
uv run fund record-operation \
  --fund-code 000001 --type 买入 --date 2026-01-01 \
  --amount 10000 --price 1.0
```

- `--type`：`买入 / 卖出 / 加仓 / 减仓`
- `--amount-unit`：`金额`（默认）/ `份额`
- 纯本地读写，不发任何网络请求。历史持仓的唯一数据来源。

### 4.2 每日研判（Daily Button）

```bash
uv run fund daily                      # 对当前持仓逐只跑研判，落盘 analysis_log
uv run fund daily --fund-code 000001   # 可选：只跑单只，便于调试
```

- 持仓清单由 `actual_operations` 流水重建。
- 输出：止盈信号数 / 暴涨预警数 / 暴跌预警数 / 落盘路径。

### 4.3 每周复盘（Weekly Button）

```bash
uv run fund weekly                     # 复盘上一个 ISO 周
uv run fund weekly --week 2026-W43     # 可选：手动指定复盘周，便于补跑
```

- 落盘 `weekly_review_log`，并回填 `performance_db`。
- 当前没有历史净值数据源，`performance_db` 回填的 `predict_return` 等真实净值字段留空（文档化限制）。

---

## 5. 数据落盘到 local（符合你的预期）

所有数据都写在 `data/` 目录下，按用途分子目录：

| 子目录 | 内容 |
| ------ | ---- |
| `actual_operations/` | 手工录入的真实买卖流水 |
| `analysis_log/` | 每日研判记录 |
| `weekly_review_log/` | 每周复盘记录（`.json` + `.md`） |
| `trade_decision/` | 需要落盘的交易决策 |
| `performance_db/` | 预测 vs 实际收益的回填库 |
| `raw_data/` | 数据源原始数据 |
| `knowledge_base/` | 知识库（基金画像 / 经验教训 / 市场规律，**只允许人工审阅后入库**） |

---

## 6. Agent / 数据源现状（「接 agent 拿数据」的真相）

### 6.1 内部 Agent（已实现，可跑）

`src/fund/agents/`：

| 模块 | 职责 |
| ---- | ---- |
| `position_analyst.py` | 持仓分析（Target1 止盈 + Target4 论证），产出后回写基金画像 |
| `bull_scanner.py` | 暴涨预警扫描（Target2） |
| `risk_alert.py` | 暴跌风险预警（Target3） |
| `weekly_reviewer.py` | 每周复盘、误差分类、产出新分析因子 → 落成经验教训 |
| `orchestrator.py` | 编排器：串联上述 agent，合并结果落盘 |

### 6.2 数据源（当前是 fake）

`src/fund/sources/`：`fund_info / stock_financial / macro_data / industry_news` 四个源，**当前返回样例/占位数据**，真实接口地址已在 `config.example.yaml` 的 `api.*.endpoint` 里留了占位符。

### 6.3 LLM（当前是 fake）

`src/fund/llm.py`：`llm.provider="fake"` 时返回空 JSON 占位、**不发真实请求**；`"openai"` 分支当前是 `NotImplementedError` 占位。

### 6.4 要接真实数据/LLM 还需做什么（Phase 7 · Optional，未实现）

按 [design/09_feature_checklist.md](design/09_feature_checklist.md) 的进度，以下都是 `[ ]` 未完成：

- **F7.1** 真实 LLM provider 接入 `llm.py`（如 OpenAI 兼容接口）
- **F7.2** 真实数据源接口接入（替换 `sources/*.py` 样例数据为真实 endpoint）
- **F7.3** 本地最小 Web UI（`web.py` + 登录 + 主页面 + TODO 窗口）
- **F7.4** 定时任务（`launchd`/`cron`）自动触发 daily/weekly

---

## 7. 关于 UI：现状与计划

- **现在**：只有 CLI，没有图形界面（设计原则「先 CLI 后 UI」）。
- **计划中的 Web UI（F7.3）**：详见 [design/11_web_ui.md](design/11_web_ui.md)，要点：
  - 单用户本地工具，默认只绑定 `127.0.0.1`，不对外暴露；
  - 技术栈 Flask + 纯 HTML/原生 JS，**不引入 npm/构建**；
  - 功能：登录（pbkdf2 密码哈希 + session cookie + 失败锁定）、Daily/Weekly 操作区、右下角 TODO 小窗口。
- 若你想让 UI 提前落地，需要先把 F7.3 从 Optional 提上来，且**按 checklist 顺序推进**（先确认不做会阻碍主线再决定）。

---

## 8. 常见问题

- **`ConfigError: 配置文件不存在`** → 忘了 `cp config.example.yaml config.yaml`。
- **`fund` 命令找不到** → 没执行 `uv sync`（`fund` 入口脚本由 `[project.scripts]` 注册）。
- **分析内容看起来是空的** → 正常。`llm.provider="fake"` 时 daily/weekly 只产出占位结构，真实结论需先完成 F7.1/F7.2。
- **想换数据目录** → 改 `config.yaml` 的 `path.data_root`（相对 `project/fund/`）。

---

## 9. 硬约束（改动前必读，摘自 AGENTS.md）

- 不硬编码 API Key；不编造任何财报/新闻/行情/基金数据（失败走 `api_adapter` 降级并标 `data_warning`）。
- 不引入任何自动下单/对接券商的代码。
- 不擅自把 `web.host` 改成 `0.0.0.0`；不存明文密码（只存 `password_hash`）。
- 新增能力 = 新增文件，不改已有模块内部结构。
- daily/weekly 自动流程**不得**写 `data/knowledge_base/market_patterns/`（只允许人工审阅入库）。
