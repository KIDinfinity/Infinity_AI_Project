# Phase 03 · 生产化与求职（第 17–26 周 · Day58–Day77 · 11-24 → 12-13）

## 1. 阶段目标

把 WorkPilot 推进到 **v2.0 = P3 WorkPilot Production**：实现 DA-01 主场景包，具备多空间认证、安全护栏、场景评测与回归体系，可在线演示、可打包售卖；随后把三个里程碑转化为 Portfolio、三版简历、面试能力，并完成半年复盘与 DA-02 规划。

## 2. 资产锚点

| 项                     | 内容                                                                                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 版本推进               | v1.0 → v1.1（主场景 MVP）→ v1.2（Postgres/认证/多空间/自动部署）→ v1.3（场景评测）→ v1.4（安全加固）→ **v2.0（P3 发布 + 模板库 + Pro Kit）**                 |
| 构建模块               | M10 场景包、M11 安全与多租户、M3.5/M3.6 回归与反馈闭环、M4.4/M4.5、M5.4、M12.2/M12.4、M13.3–M13.5、M14 模板库                                                |
| 完成后最终产品多了什么 | WorkPilot 能真正解决一个选定的研发痛点（端到端、可审批、可评测），能给团队安全地用（登录、空间隔离、注入防护、审计），能被别人部署和购买，并沉淀为可复用模板 |

```text
W17 定义 → W18 场景 MVP → W19 工程化 → W20 场景评测 → W21 安全 → W22 回归+模板+Pro Kit
→ W23 Portfolio → W24 简历 → W25 面试 → W26 复盘
```

## 3. 为什么这个阶段存在

「能做 Demo」和「能交付生产系统」是两个层级。P3 证明后者，也是 AI Full-Stack / AI Platform 岗位最看重的证据；同时只有把成果转化为简历和面试表达，能力才能变成 offer 与收入。

## 4. 本阶段必须产生什么（文件级）

| 线   | 产出                                                             | 位置                                                            |
| ---- | ---------------------------------------------------------------- | --------------------------------------------------------------- |
| A    | P3 问题定义（8 要素）+ 成功指标                                  | `docs/product/p3-definition.md`                                 |
| B    | 主场景包 LangGraph 工作流 + 页面                                 | `apps/api/app/scenarios/<sp>/`、`apps/web/src/pages/`           |
| C    | Postgres + Alembic + JWT + RBAC + 空间隔离 + 异步导入 + 自动部署 | `app/db/`、`app/security/`、`.gitea/workflows/deploy.yml`       |
| B    | 场景评测集 + rubric + 人审表 + 反馈闭环                          | `eval/datasets/scenario_*.jsonl`、`eval/reports/`               |
| C    | 威胁模型 + 20 条攻击集 + 防护 + 审计日志                         | `docs/security/threat-model.md`、`eval/datasets/security.jsonl` |
| B    | Badcase 总库 + 回归套件 + Eval v2                                | `eval/badcases/`、`eval/reports/`                               |
| A    | 模板库 + Pro Kit 包 + 在线 Demo                                  | `personal-ai-engineering/`、`dist/pro-kit/`                     |
| D    | Portfolio 网站、三版简历、面试题 ≥ 30、System Design ×2、STAR ×3 | `projects/career/`、Portfolio 站点                              |
| 全部 | 半年报告 + DA-02 提案                                            | `projects/product-lab/half-year-review.md`                      |

## 5. 本阶段不应该做什么

- 不再加新模块（M0–M14 之外的东西一律进 Backlog）；W23 之后不加产品功能。
- 不启动 DA-02 开发（只做提案）。
- 不上 Kubernetes、不做微服务拆分、不做多 Agent。
- 不裸辞、不超预算；求职是「正常公开投递」，不是主动营销。
- 不编造简历经历：所有数字来自 `eval/reports/` 与使用日志。

## 6. 本阶段核心能力

- **B**：场景化 Agent 工作流、Evaluation v2、回归测试、Badcase 驱动优化。
- **C**：Postgres/Alembic、JWT/RBAC、多租户隔离、OWASP LLM Top 10、审计、CI/CD 自动部署、灾备。
- **D**：Portfolio、三版简历、System Design、STAR、模拟面试。
- **A**：Pro Kit 打包定价、在线 Demo、商业化验证复盘。

## 7. 进入条件

phase_02 核心验收 PASS：v1.0 已发布、Agent 评测与 CI 门禁可用、MCP 可演示、简历 v1 完成。

## 8. 完成条件 / 阶段验收（第 26 周 Day76–77）

- [ ] v2.0 tag，公网在线 Demo 可用（演示账号 + 配额）
- [ ] 主场景 20 用例 rubric 通过率 ≥ 0.75（或有明确基线与改进记录）
- [ ] 20 条注入/越权攻击用例拦截率 100%
- [ ] 两个空间数据互不可见（有自动化测试）
- [ ] 干净环境恢复 < 30 分钟（有演练记录）
- [ ] `personal-ai-engineering` 中 ≥ 6 个模板可直接复制使用
- [ ] Portfolio 网站上线，三个项目统一结构展示
- [ ] 三版简历 + ≥ 30 道面试题 + 2 道系统设计 + 3 个 STAR
- [ ] 半年报告覆盖 DA01_TARGET_ASSET §11 全部指标 + DA-02 提案

## 9. 下一阶段依赖什么

本阶段是半年终点。输出：WorkPilot v2.0、模板库、Portfolio、简历、半年报告、DA-02 提案 → 决定下半年是「继续放大 WorkPilot」还是「用模板库快速孵化 DA-02」。

## 完成本阶段后，DA-01 比阶段开始前多了什么？

从「可审批的研发 Agent 平台」变成「能安全交付给团队、解决一个真实研发痛点、可评测可回归、可售卖、可复制成模板」的生产级智能解决方案资产，并已转化为完整的求职材料。
