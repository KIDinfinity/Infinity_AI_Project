# 02. 配置规范 `config.yaml`

## 原则

- 所有 API Key、接口地址、策略阈值、重试参数**统一且只**在 `config.yaml` 中配置；代码里**禁止出现任何字面量 key**。
- `config.yaml` 本地保存真实值，**加入 `.gitignore`，不提交仓库**；仓库中只提交 `config.example.yaml`（字段齐全、值为占位符）。
- 启动任何命令前，`config.py` 必须先加载并用 pydantic 模型校验；校验失败则直接报错退出，不允许"部分字段缺失但继续跑"。

## 完整字段模板（`config.example.yaml`）

```yaml
# ========== 业务策略参数（对应 base_rule Target1/2/3）==========
strategy:
  base_profit_rate: 0.10 # 基础止盈目标 10%
  min_hold_days: 30 # 默认最低持有天数
  confidence_threshold: 70 # 暴涨预警最低置信分数线（<70 只标观察，不推荐买入）
  surge_upper_target: 0.30 # 暴涨预期上限 30%

# ========== 数据源接口 & 密钥配置 ==========
api:
  fund_data:
    endpoint: "https://xxx/api/fund"
    api_key: "${FUND_API_KEY}" # 支持环境变量占位符，见下方"密钥管理"
    timeout: 15
    retry_max: 3
    backup_endpoints: ["https://backup-xxx/api/fund"]
  stock_financial:
    endpoint: "https://xxx/api/financial"
    api_key: "${FINANCIAL_API_KEY}"
    timeout: 15
    retry_max: 3
    backup_endpoints: []
  macro_data:
    endpoint: "https://xxx/api/macro"
    api_key: "${MACRO_API_KEY}"
    timeout: 15
    retry_max: 3
    backup_endpoints: []
  financial_news:
    endpoint: "https://xxx/api/news"
    api_key: "${NEWS_API_KEY}"
    timeout: 20
    retry_max: 4
    backup_endpoints: []

# ========== API 自适应容错适配器参数 ==========
api_adapter:
  backoff_factor: 2 # 指数退避系数
  rate_limit_sleep: 5 # 429 限流基础休眠秒数
  auto_reduce_payload: true # 失败时自动精简请求参数
  enable_switch_backup: true # 允许自动切换备用接口

# ========== LLM 调用配置 ==========
llm:
  provider: "openai" # provider 标识，llm.py 按此分发
  model: "gpt-4.1"
  api_key: "${LLM_API_KEY}"
  timeout: 60

# ========== 系统固定路径常量 ==========
path:
  data_root: "./data" # 相对 project/fund/ 的路径，便于项目整体迁移

# ========== Web UI 配置（Optional，F7.3 实现时才需要）==========
web:
  host: "127.0.0.1" # 默认只绑定本机，禁止随意改成 0.0.0.0（见 11_web_ui.md 第 2 节安全要点）
  port: 8765
  password_salt: "${WEB_PASSWORD_SALT}" # 随机字符串，本地生成
  password_hash: "${WEB_PASSWORD_HASH}" # pbkdf2_hmac(密码, salt, 200000) 的结果，禁止存明文密码
  secret_key: "${WEB_SECRET_KEY}" # session 签名密钥，随机字符串
  session_expire_minutes: 720 # 会话过期时间，默认 12 小时
  todo_lookback_weeks: 8 # TODO 小窗口最多回看多少周的缺失复盘
```

## 密钥管理（禁止硬编码的落地方式）

- `config.yaml` 中 `api_key` 字段支持 `${ENV_VAR_NAME}` 占位符写法。
- `config.py` 加载时：先读 YAML 原文，用正则替换 `${XXX}` 为 `os.environ["XXX"]`；**环境变量未设置时视为未配置**（允许为空字符串，但调用该接口时 `adapter` 直接返回"配置缺失"降级，不报 500 级异常崩溃整个流程）。
- 也允许 `api_key` 直接写字面量值（本地单用户场景，`config.yaml` 本身已被 gitignore，风险可接受）；两种写法都支持，`${}` 只是可选的进阶用法。
- **唯一禁止的是**：把 key 写在 `.py` / `.md` / 代码仓库里任何会被提交的文件中。
- `web.password_hash` / `web.password_salt` / `web.secret_key` 同样遵守上述规则，且**额外禁止**出现明文密码本身（只存哈希结果）；生成方式见 [11_web_ui.md](11_web_ui.md) 第 2 节。

## 校验规则（`config.py` 职责）

1. 用 pydantic 模型 `AppConfig` 定义上述结构（字段名、类型、默认值）。
2. 必填项缺失 / 类型错误 → 抛 `ConfigError`，附清晰字段路径（如 `api.fund_data.endpoint 不能为空`）。
3. 提供 `load_config(path: str | None = None) -> AppConfig`：
   - 默认按 `project/fund/config.yaml` 路径加载；支持通过参数或环境变量 `FUND_CONFIG_PATH` 覆盖（便于测试传入临时文件）。
4. `data_root` 解析为绝对路径（相对 `project/fund/` 目录），供 `storage.py` 统一使用。

## 与 `.gitignore` 的配合

在仓库根 `.gitignore` 新增：

```gitignore
# project/fund 本地密钥配置
project/fund/config.yaml
project/fund/.env
```
