# Week 21 · TASKS

## Task 1：威胁建模 + 攻击集（Day66 · 02-15）

### 做什么

写 `docs/security/threat-model.md`：资产清单、信任边界（用户输入 / 上传文档 / 网页 / Gitea 内容 / MCP 客户端 / LLM）、OWASP LLM Top 10 → WorkPilot 风险 → 缓解（现状 / 计划）→ 测试 id 映射表；`eval/datasets/security.jsonl` 扩到 20 条（直接注入、文档/网页/issue 间接注入、跨空间检索、系统提示泄露、一次创建 100 个 issue、Markdown 图片外传、http_fetch SSRF、PII 泄露、超长输入等）；`eval/runners/run_security_eval.py` 跑基线。

### 为什么做

先测量再防护：基线失败项就是 Day67 的工作清单；映射表是面试与 Portfolio 的安全证据。

### 资产锚点

- 模块：M11.3、M3（安全评测集）
- 版本：为 v1.4 做准备

### 前置依赖

- W15 `guardrails.py` v0 与 8 条 security 用例
- W19 认证 / 空间隔离；W20 runner 框架

### 具体执行步骤（概要，详见 day66_20261202/PLAN.md）

1. 资产 + 信任边界图。
2. OWASP 映射表（7 条重点）。
3. 攻击集 20 条（含 canary 设计、恶意文档种子）。
4. runner：按 check 类型断言（API 状态码 / 输出不含 / 无写工具调用 / 工具被拒）。
5. 跑基线 → 报告。

### 验收标准

- [ ] 映射表 ≥ 7 行，每行有测试 id
- [ ] 20 条用例可执行
- [ ] 基线报告列出失败项与对应缓解计划

### 完成后的产出

- `docs/security/threat-model.md`、`eval/datasets/security.jsonl`、`eval/runners/run_security_eval.py`
- `eval/datasets/security_fixtures/`（恶意文档 / 网页种子）
- `eval/reports/20270215-security-baseline.md`

### 求职映射

「威胁建模 + 攻击集」是 AI 安全相关问题的完整答案框架。

### 如果时间不够 / 没有必要

- 资产与边界用一张 mermaid 图 + 5 行文字。
- LLM03/04/09 只在表中写「不适用 / 已由供应商负责」一句话。

---

## Task 2：防护实现 + 审计 + 恢复演练（v1.4）（Day67 · 02-16）

### 做什么

按基线失败项实现：按角色 / 场景的工具白名单；每次运行写操作上限；Markdown 渲染禁外部图片；SSRF 阻断私网 + 域名白名单；检索层空间断言；系统提示去敏感化 + canary；输出 PII 脱敏；输入大小限制；AuditLog（登录、审批、写工具、管理操作）；重跑攻击集至 100%；剩余风险接受记录；生产恢复演练（pg_dump + Qdrant snapshot + MinIO）计时并更新 runbook；tag `v1.4.0`。

### 为什么做

把威胁模型中的「计划」变成「代码 + 测试」，满足 §11 安全与运维指标。

### 资产锚点

- 模块：M11.3、M11.4、M5.5
- 版本：**v1.4**

### 前置依赖

- Day66 基线报告与失败清单
- W7 备份脚本、W19 Postgres

### 具体执行步骤（概要，详见 day67_20261203/PLAN.md）

1. policy.py（白名单 + 写上限）接入工具执行器。
2. ssrf.py 接入 http_fetch。
3. output_filter.py（外链图片）+ 前端 img 白名单；redact.py（PII）。
4. 检索断言 + 输入大小中间件 + canary。
5. AuditLog 模型 + 写入点。
6. 重跑攻击集 → 报告；风险接受记录。
7. 恢复演练 → runbook；tag v1.4.0。

### 验收标准

- [ ] 攻击集 20/20
- [ ] AuditLog 4 类事件可查
- [ ] 恢复演练 < 30 分钟有记录
- [ ] `v1.4.0` 已部署，其他评测冒烟不退化

### 完成后的产出

- `apps/api/app/security/{policy.py, ssrf.py, output_filter.py, redact.py, audit.py}`
- `eval/reports/20270216-security-v1.4.md`、`docs/security/risk-acceptance.md`、`docs/runbook.md`
- tag `v1.4.0`

### 求职映射

「从攻击集基线到 100% 拦截」的前后对比是安全话题最有说服力的量化证据。

### 如果时间不够 / 没有必要

- 恢复演练顺延到 Day68 开头或 Day76 前（阶段验收必需，不可删除）。
- AuditLog 页面不做，只做表 + SQL 查询示例。

---
