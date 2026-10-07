# Week 22 · Eval v2 + 模板库 + Pro Kit（v2.0）（Phase 3 · Day68–Day69 · 02-22 → 02-23）

## 1. 本周核心目标

把 RAG / Agent / 场景 / 安全四类 badcase 合并成统一总库（分类法 + 状态），把已修复 badcase 全部转为 regression 用例，`make eval-all` 生成 Eval v2 报告（v0.5 → v1.0 → v2.0 指标趋势），CI 门禁覆盖四类冒烟集；然后从 WorkPilot 抽取 `personal-ai-engineering` 模板库，打包 Pro Kit，发布 **v2.0.0（P3 完成）**。

## 2. 资产锚点

| 构建模块                                                     | 版本里程碑          | 本周结束 WorkPilot 能演示什么                                                                                                                                                           |
| ------------------------------------------------------------ | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M3.4 Badcase 库、M3.5 回归 + 门禁、M14 模板库、M12.2 Pro Kit | **v2.0（P3 发布）** | 一条 `make eval-all` 得到四类评测 + 趋势报告；PR 改坏 prompt 时 CI 门禁变红；`personal-ai-engineering` 中复制 fastapi-template 5 分钟跑起来；`dist/workpilot-pro-kit-v2.0.0.zip` 可下载 |

## 3. 为什么这一周存在

- 总计划 §6.3：最终项目必须有 Evaluation Dataset + Automated Evaluation + Human Review + Badcase + Regression——证明「AI 到底有没有变好」。
- 总计划 §12.4 / 蓝图 M14：半年要沉淀可复用工程模板，**从真实代码抽取**，不是从零写。
- 蓝图 §10：Pro Kit 是商业化验证的载体；v2.0 是 P3 作品集的版本锚点。

## 4. 本周在路线中的位置

```text
上周产出（W21）：v1.4、security 20/20、AuditLog、恢复演练、四类 runner 与 EvalRun
        ↓
本周（W22）：eval/badcases/（分类法 + badcases.jsonl）+ regression 标签 + make eval-all + Eval v2 报告 + CI 门禁
             personal-ai-engineering（10 目录，≥ 6 个可运行模板）+ dist/pro-kit + 定价 + 上架草稿 → v2.0.0
        ↓
下周输入（W23）：Portfolio 三个项目页的 Evaluation / Badcases / Result 节直接引用 Eval v2；在线 Demo 用 v2.0
```

## 5. 每日安排

| Day   | 日期  | Task                                      | 当日 P0 产出                                                                                              | 模块      | 状态 |
| ----- | ----- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------- | --------- | ---- |
| Day68 | 02-22 | Task 1：Badcase 总库 + 回归套件 + Eval v2 | `eval/badcases/` 总库 + regression 用例 + `make eval-all` + Eval v2 报告 + CI 门禁                        | M3.4 M3.5 | TODO |
| Day69 | 02-23 | Task 2：抽取模板库 + Pro Kit 打包（v2.0） | `personal-ai-engineering` 骨架 + fastapi/docker 模板可跑 + tag `v2.0.0` + Release notes（Pro Kit zip P1） | M14 M12.2 | TODO |

## 6. 本周必须留下的资产

- `eval/badcases/README.md`（分类法 + 状态机）、`eval/badcases/badcases.jsonl`、`eval/badcases/summary.md`（生成）
- 各数据集中 `tags: ["regression"]` 用例
- `eval/runners/run_all.py`、`eval/reports/20270222-eval-v2.md`
- `.gitea/workflows/ci.yml`（eval-smoke 覆盖 rag + agent + scenario + security）
- `~/lab/personal-ai-engineering/`（Gitea + GitHub 公开）
- `scripts/build_pro_kit.sh`、`dist/workpilot-pro-kit-v2.0.0.zip`（dist 不入库）
- `~/lab/projects/product-lab/pro-kit/`（手册、LICENSE、定价、上架文案——私有）
- tag `v2.0.0` + Release notes

## 7. 本周验收标准

- [ ] PASS / FAIL：badcase 总库覆盖 4 个来源，每条有 category + status；所有 status=fixed 的都有 regression 用例 id
- [ ] PASS / FAIL：`make eval-all` 一条命令产出 Eval v2 报告，含 v0.5 / v1.0 / v2.0 三列对比
- [ ] PASS / FAIL：CI 门禁跑四类冒烟集；人为改坏一个 prompt 时 CI 失败
- [ ] PASS / FAIL：`personal-ai-engineering` 10 个目录都有 README；≥ 6 个模板含最小可运行代码（P0 至少 2 个，余下最晚 Day76 前补齐）
- [ ] PASS / FAIL：复制 fastapi-template 到新目录 5 分钟内 `/health` 返回 200（计时记录）
- [ ] PASS / FAIL：`v2.0.0` tag + Release notes 已发布并自动部署
- [ ] PASS / FAIL：Pro Kit zip 可生成，定价已决定（¥199–499 区间内），上架草稿已写（不要求上线）

## 8. 求职映射

- 本周能力：评测体系、回归门禁、badcase 管理、工程模板化、产品打包与定价。
- 简历 bullet 草稿：
  - 「建立 RAG / Agent / 场景 / 安全四类评测 + badcase 总库（** 条，** 条已转回归），CI 门禁阻止质量回退；核心指标 v0.5 → v2.0：hit@5 ** → **，任务成功率 ** → **」
  - 「从生产项目抽取 6+ 个可复用工程模板（FastAPI / RAG / Agent / Eval / Docker / Observability），新项目启动时间降至 5 分钟」
- 面试题：
  1. 你如何防止 prompt 改动导致质量回退？（答要点：回归集 + 基线对比 + CI 门禁阈值 + 冒烟集控成本 + 全量定期跑）
  2. Badcase 怎么管理？（答要点：分类法（检索/生成/工具/安全…）、根因、状态机、修复后转回归、按类别统计找系统性问题）
  3. 开源和付费如何划界？（答要点：开源核心建立信任与流量；付费卖「省时间」与生产就绪：部署包、手册、场景资产、更新）

## 9. 本周禁止事项

- 不加新产品功能（v2.0 之后只修 bug）。
- 不把 WorkPilot 整仓复制成模板；模板只含最小可运行代码。
- 不在模板库 / Pro Kit 中放任何真实数据、密钥、公司信息、私有 badcase 原文。
- 不正式上架收款（只写草稿）——发布前必须过 W23 安全检查。

## 10. 时间不够时（最小保留）

- Day68：badcase 总库 + regression 标签 + `make eval-all` + 报告；CI 门禁可只加 security 冒烟（最便宜）。
- Day69：模板库骨架（10 个 README）+ fastapi-template + docker-template 可运行 + tag v2.0.0；其余模板与 Pro Kit 在 Day70–Day76 碎片时间补齐（Day76 验收前必须 ≥ 6 个）。

## 11. 周复盘

- 完成：\_\_\_\_
- 未完成 + 原因：\_\_\_\_
- WorkPilot 本周多了什么可演示的东西：\_\_\_\_（预期：Eval v2 趋势 + 模板库 + Pro Kit）
- 是否出现无效学习或范围扩张：\_\_\_\_
- 下周调整：\_\_\_\_
