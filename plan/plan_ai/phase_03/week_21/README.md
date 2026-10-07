# Week 21 · 安全加固（OWASP LLM Top 10）（Phase 3 · Day66–Day67 · 02-15 → 02-16）

## 1. 本周核心目标

对照 OWASP Top 10 for LLM Applications 2025 做 WorkPilot 威胁建模，把攻击集从 8 条扩到 20 条并跑出基线（预期有失败）；然后逐项实现防护（工具白名单、写操作上限、Markdown 外链图片阻断、SSRF 阻断、检索空间断言、PII 脱敏、输入限制、审计日志），重跑攻击集达到 100% 拦截，完成生产恢复演练，发布 **v1.4.0**。

## 2. 资产锚点

| 构建模块                                                                  | 版本里程碑 | 本周结束 WorkPilot 能演示什么                                                                                                                                  |
| ------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M11.3 Guardrails、M11.4 审计 / 密钥 / 限流、M5.5 备份恢复、M3（安全评测） | **v1.4**   | `make eval-security` 显示 20/20 拦截；威胁模型表能从任一 OWASP 条目追到「缓解代码 + 测试 id」；AuditLog 页可查登录 / 审批 / 写工具记录；恢复演练记录 < 30 分钟 |

## 3. 为什么这一周存在

- v1.2 起 WorkPilot 读外部内容（文档、网页、Gitea issue、MCP）并能写外部系统——间接注入 + 过度代理是 LLM 应用最现实的风险。
- 蓝图 §11 P3 安全指标：20 条攻击用例拦截率 100%；运维指标：干净环境恢复 < 30 分钟。
- 「能说清 OWASP LLM Top 10 并给出自己系统的缓解与测试」是 AI Platform / AI Engineer 面试的高分项。

## 4. 本周在路线中的位置

```text
上周产出（W20）：v1.3、场景评测 runner 框架、EvalRun、badcase 流程
        ↓
本周（W21）：threat-model.md（资产 / 信任边界 / OWASP → 风险 → 缓解 → 测试映射）
             security.jsonl 20 条 + run_security_eval.py 基线 → 防护实现 → 20/20 → AuditLog → 恢复演练 → v1.4.0
        ↓
下周输入（W22）：安全 badcase 并入总库；security 冒烟集进入 CI 门禁；Pro Kit 打包安全模块
```

## 5. 每日安排

| Day   | 日期  | Task                                       | 当日 P0 产出                                                        | 模块  | 状态 |
| ----- | ----- | ------------------------------------------ | ------------------------------------------------------------------- | ----- | ---- |
| Day66 | 02-15 | Task 1：威胁建模 + 攻击集                  | `docs/security/threat-model.md` + `security.jsonl` 20 条 + 基线报告 | M11.3 | TODO |
| Day67 | 02-16 | Task 2：防护实现 + 审计 + 恢复演练（v1.4） | 防护代码 + 攻击集 20/20 + AuditLog + tag `v1.4.0`（恢复演练 P1）    | M11   | TODO |

## 6. 本周必须留下的资产

- `docs/security/threat-model.md`
- `eval/datasets/security.jsonl`（20 条）、`eval/runners/run_security_eval.py`
- `eval/reports/20270215-security-baseline.md`、`eval/reports/20270216-security-v1.4.md`
- `apps/api/app/security/{policy.py, ssrf.py, output_filter.py, redact.py, audit.py}`
- `apps/api/app/db/models.py`（AuditLog）
- `docs/security/risk-acceptance.md`（剩余风险接受记录）
- `docs/runbook.md`（恢复演练记录：pg_dump + Qdrant snapshot + MinIO）
- tag `v1.4.0`

## 7. 本周验收标准

- [ ] PASS / FAIL：威胁模型覆盖 LLM01 / 02 / 05 / 06 / 07 / 08 / 10，每条都映射到测试 id
- [ ] PASS / FAIL：攻击集 20 条，基线报告如实记录失败项
- [ ] PASS / FAIL：防护后 20/20 拦截（或按风险接受记录说明的例外——例外不计入 100%，必须为 0 条才算 PASS）
- [ ] PASS / FAIL：AuditLog 记录登录（成功/失败）、审批、写工具、成员管理
- [ ] PASS / FAIL：恢复演练在干净目录 / 新服务器完成，计时 < 30 分钟，写入 runbook
- [ ] PASS / FAIL：`v1.4.0` 已部署，原有 rag / agent / scenario 冒烟不退化

## 8. 求职映射

- 本周能力：LLM 应用威胁建模、Prompt Injection（直接/间接）防护、SSRF、过度代理控制、审计、灾备。
- 简历 bullet 草稿：
  - 「对照 OWASP LLM Top 10（2025）完成威胁建模，构建 20 条攻击用例（间接注入、Markdown 外传、SSRF、跨空间检索等），防护后拦截率 0.\_\_ → 1.0」
  - 「完成生产恢复演练（Postgres + Qdrant snapshot + MinIO），干净环境恢复 \_\_ 分钟」
- 面试题：
  1. 间接 Prompt Injection 怎么防？（答要点：不能靠 prompt 根治；外部内容标记为数据、写工具需审批、工具白名单、输出过滤、最小权限、可审计）
  2. 为什么说系统提示不应依赖保密？（答要点：LLM07——系统提示总能被诱导泄露；不放密钥与权限逻辑，权限在代码层执行）
  3. Agent 的 http_fetch 有哪些风险？（答要点：SSRF 访问内网/云元数据；对策：协议限制、DNS 解析后私网 IP 阻断、禁用重定向或逐跳校验、域名白名单、超时与大小限制）

## 9. 本周禁止事项

- 不引入付费安全网关 / WAF / 商业 guardrail 服务。
- 不训练分类器模型；注入检测保持规则 + 结构化防护。
- 不为了「100%」删除或弱化攻击用例。
- 不在攻击集中使用真实可利用的外部恶意域名（用 `evil.example` 等保留域名）。

## 10. 时间不够时（最小保留）

- Day66：threat-model 映射表 + 20 条攻击集 + 基线跑通（资产/边界描述可简写）。
- Day67：工具白名单 + 写上限 + SSRF + Markdown 图片 + 空间断言 + 输入限制 → 重跑；AuditLog 与恢复演练最晚 Day76 前完成（阶段验收项）。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_**\_（预期：攻击集 0.** → 1.0 对比报告）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
