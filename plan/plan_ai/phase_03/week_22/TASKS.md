# Week 22 · TASKS

## Task 1：Badcase 总库 + 回归套件 + Eval v2（Day68 · 02-22）

### 做什么

合并 RAG / Agent / 场景 / 安全 badcases 到 `eval/badcases/`（分类法 + 状态）；每个已修复 badcase 转为带 `regression` 标签的用例；`make eval-all` 跑四类评测并生成 Eval v2 报告，展示 v0.5 → v1.0 → v2.0 指标趋势；CI 门禁覆盖 rag + agent + scenario + security 冒烟集。

### 为什么做

统一的 badcase 视图能发现系统性问题；回归 + 门禁保证 v2.0 之后的改动不退化；趋势报告是 Portfolio「Optimization / Result」节的硬证据。

### 资产锚点

- 模块：M3.4、M3.5
- 版本：v2.0（评测部分）

### 前置依赖

- W5 `badcases.md`、W14 agent 评测 + compare_eval.py、W20 场景 runner + EvalRun、W21 security runner
- 各版本基线报告（v0.5、v1.0）

### 具体执行步骤（概要，详见 day68_20261204/PLAN.md）

1. 写分类法与状态机。
2. 迁移旧 badcases 到 `badcases.jsonl`（脚本 + 人工补字段）。
3. 已修复项 → regression 用例（补 tags）。
4. `run_all.py` + `make eval-all` + 报告生成（含三版本对比）。
5. CI：eval-smoke 四类子集 + 阈值；故意改坏验证。

### 验收标准

- [ ] 总库每条有 source / category / status
- [ ] fixed 项 100% 有 regression_case_id
- [ ] Eval v2 报告含三版本对比
- [ ] CI 门禁对坏改动报红

### 完成后的产出

- `eval/badcases/{README.md, badcases.jsonl, summary.md}`
- `eval/runners/run_all.py`、`eval/reports/20270222-eval-v2.md`
- `.gitea/workflows/ci.yml`、`Makefile`

### 求职映射

评测体系完整度是 AI Engineer 与普通「调 API 开发者」的分水岭。

### 如果时间不够 / 没有必要

- 报告趋势只用表格（不画图）。
- CI 中 scenario 冒烟只跑 3 条（judge 成本）。

---

## Task 2：抽取模板库 + Pro Kit 打包（v2.0）（Day69 · 02-23）

### 做什么

Gitea Web UI 新建 `personal-ai-engineering`（并镜像到 GitHub 公开）：`rag-template`、`agent-template`、`evaluation-template`、`fastapi-template`、`docker-template`、`ai-observability`、`prompts`、`badcases`（只含分类法）、`datasets`（schema + 公开样例）、`interview`（链接），每个带「如何复制使用」README 与最小可运行代码（从 WorkPilot 抽取）；验证 fastapi-template 5 分钟跑起来。Pro Kit：`scripts/build_pro_kit.sh` 组装 `dist/pro-kit/` 并生成版本化 zip；定价决策；面包多 / Gumroad 上架草稿；tag `v2.0.0` + Release notes。

### 为什么做

模板库是半年最可复用的工程资产（DA-02 将直接使用）；Pro Kit 是商业化验证的载体；v2.0 标志 P3 完成。

### 资产锚点

- 模块：M14、M12.2
- 版本：**v2.0**

### 前置依赖

- Day68 评测体系
- W16 `docs/open-core.md`、Day59 开源边界决定
- v1.4 安全加固完成

### 具体执行步骤（概要，详见 day69_20261205/PLAN.md）

1. Gitea 建仓库 → clone → 10 目录骨架 + 统一 README 模板。
2. 抽取 fastapi-template + docker-template → 5 分钟验证。
3. 抽取其余模板（rag / agent / evaluation / observability）。
4. gitleaks 扫描 → 推 Gitea + GitHub。
5. Pro Kit 素材（私有）+ 打包脚本 + zip。
6. 定价 + 上架草稿；tag v2.0.0 + Release notes。

### 验收标准

- [ ] 10 个目录 README 齐全；≥ 6 个模板可运行（P0 ≥ 2）
- [ ] fastapi-template 5 分钟验证通过
- [ ] gitleaks 无发现
- [ ] v2.0.0 发布；Pro Kit zip 可生成；定价已定

### 完成后的产出

- `~/lab/personal-ai-engineering/`
- `scripts/build_pro_kit.sh`、`dist/workpilot-pro-kit-v2.0.0.zip`
- `~/lab/projects/product-lab/pro-kit/{manual.md, LICENSE-PRO.md, pricing.md, listing-draft.md}`
- `docs/releases/v2.0.0.md`

### 求职映射

「工程模板化 + 产品化」体现的是资深工程师的复用与交付意识。

### 如果时间不够 / 没有必要

- 只保 fastapi + docker 两个模板 + 其余 README，剩余模板在 Day76 前补齐。
- Pro Kit 只做打包脚本与 zip，上架草稿顺延到 Day71 之后（W23 安全检查后）。

---
