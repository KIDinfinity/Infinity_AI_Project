# Week 01 · 研发底座 + 痛点池 + 项目规范/模板（Phase 1 · Day01–Day05 · 09-28 → 10-02）

## 1. 本周核心目标

把「代码放哪、项目长什么样、要解决什么问题」三件事一次定下来：

1. **底座**：Docker（M0.1）+ Gitea（M0.2）可用，所有代码只进 Gitea。
2. **痛点**：从过去两周真实研发工作中记下 ≥ 8 条痛点（M10 候选输入），为 W3 Day13 场景选型准备事实。
3. **规范 + 模板**：写下 `PROJECT_STANDARD.md`，做成 Gitea 模板仓库 `ai-project-template`，并由它生成 DA-01 仓库 `workpilot`，打 tag `v0.0.0`。

## 2. 资产锚点

| 项                            | 内容                                                                                                                                                                        |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 构建模块                      | M0.1 Docker 运行时 ✅、M0.2 Gitea ✅、M0.3 项目规范 + 模板、M10 场景包候选（痛点池）                                                                                        |
| 版本里程碑                    | **v0.0**：仓库骨架 + 规范 + 模板（蓝图 §9）                                                                                                                                 |
| 本周结束 WorkPilot 能演示什么 | 在 Gitea 上打开 `workpilot` 仓库：目录结构与蓝图 §6.2 一致、`make help` 列出统一入口、`make up/down` 能起停一个示例容器、README 写清一句话定位与版本路线、tag `v0.0.0` 存在 |

## 3. 为什么这一周存在

后面 25 周所有代码、评测、部署都落在同一个仓库里。如果第一周不定规范，第 4 周会出现「评测脚本放哪」「.env 有没有被提交」「这个 prompt 是哪个版本」之类的返工。痛点池则保证 DA-01 的场景包（M10）由真实问题决定，而不是由「想学什么技术」决定（GLOBAL_CONTEXT §1、§9）。

## 4. 本周在路线中的位置

```text
上周产出：无（从零开始）
   ↓
本周（W1）：Docker ✅ → Gitea ✅ → 痛点池 v0 → PROJECT_STANDARD → 模板仓库 → workpilot v0.0.0
   ↓
下周输入（W2）：
  - workpilot 仓库（Day07 在 apps/api 起 FastAPI，Day08 写 LLM Gateway）
  - .env.example 的键名（Day07/08 的 Settings 直接按它读取）
  - Makefile 统一入口（Day07 把 dev/test/lint 接上真实命令）
  - pain-pool.md（Day10 补到 ≥10 条并加初评分列）
```

## 5. 每日安排

| Day | 日期  | Task                              | 当日 P0 产出                                                                                            | 模块        | 状态              |
| --- | ----- | --------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------- | ----------------- |
| 01  | 09-28 | Task 1：Docker 环境               | Docker Desktop 可用；nginx + volume 练习完成                                                            | M0.1        | ✅ 已完成         |
| 02  | 09-29 | Task 2：Gitea + 三目录            | Gitea `:3000`；`projects/{product-lab,ai-lab,infra}` 已推送                                             | M0.2        | ✅ 已完成         |
| 03  | 09-30 | Task 0：研发工作痛点池 v0         | `projects/product-lab/pain-pool.md` ≥ 8 条                                                              | M10         | ⏳ 日期已过，待补 |
| 04  | 10-01 | Task 3：项目规范                  | `ai-project-template` 仓库 + `PROJECT_STANDARD.md` + 骨架目录 + `.gitignore/.editorconfig/.env.example` | M0.3        | ▶ 今日执行        |
| 05  | 10-02 | Task 4：工程模板 + workpilot 仓库 | 模板仓库化；`workpilot` 由模板生成；tag `v0.0.0`                                                        | M0.3 / v0.0 | 待开始            |

## 6. 本周必须留下的资产（文件路径级）

| 资产              | 路径                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Docker 运行时     | Docker Desktop（`docker version` Server 正常）                                                                            |
| Gitea 服务 + 数据 | `http://localhost:3000`，数据 `~/gitea/data`                                                                              |
| 实验室仓库        | `~/lab/projects/{product-lab,ai-lab,infra}/README.md`                                                                     |
| 痛点池 v0         | `~/lab/projects/product-lab/pain-pool.md`                                                                                 |
| 项目规范          | `~/lab/ai-project-template/PROJECT_STANDARD.md`                                                                           |
| 根配置三件套      | `~/lab/ai-project-template/{.gitignore,.editorconfig,.env.example}`                                                       |
| 模板工程文件      | `~/lab/ai-project-template/{README.md,Makefile,scripts/bootstrap.sh,deploy/docker-compose.yml,docs/adr/0000-template.md}` |
| DA-01 仓库        | `~/lab/workpilot`（Gitea `workpilot`，tag `v0.0.0`）                                                                      |
| 目标资产摘要      | `~/lab/workpilot/docs/product/target-asset.md`                                                                            |

## 7. 本周验收标准

- [x] PASS：`docker version` 同时显示 Client 与 Server（29.8.0 / 29.8.0）
- [x] PASS：Gitea 可见 `projects`、`ai-project-template`、`workpilot` 三个仓库
- [x] FAIL：`pain-pool.md` 不存在（Day03 待补，≥ 8 条未完成）
- [x] PASS：不看文档能说出模板中每个顶层目录的用途（apps / prompts / eval / data / deploy / scripts / docs / .gitea）
- [x] PASS：`git check-ignore .env` 有输出，`git check-ignore .env.example` 无输出
- [x] 部分 PASS：`make help` 列出 10 个命令；`make up && make down` 未过（Docker 拉取 whoami 镜像需配代理 `http://127.0.0.1:7890`）
- [x] PASS：`git ls-remote --tags origin` 能看到 `v0.0.0`
- [x] PASS：`PROJECT_CONFIG.md` 的 DA-01 路径已回填 `~/lab/workpilot`

## 8. 求职映射

- **本周能力**：Docker 基础、自托管 Git、工程规范（目录 / 命名 / Conventional Commits / semver / 环境变量管理）、模板化复用。
- **简历 bullet 草稿**：
  - 搭建个人自托管研发底座（Docker + Gitea），制定 AI 项目工程规范与模板仓库，新项目初始化时间从 ~\_\_ 分钟降至 < 5 分钟。
  - 建立「痛点池 → 评分 → 场景选型」流程，从 \_\_ 条真实研发痛点中选定 AI 助手主场景。
- **面试题**：
  1. 你如何管理 LLM 项目的密钥和环境配置？（要点：`.env` 不入库、`.env.example` 列全键、pydantic-settings 统一读取、密钥可轮换、生产用平台 Secret）
  2. 为什么 AI 项目要单独有 `prompts/` 和 `eval/` 目录？（要点：prompt 是代码要版本化、评测数据集和报告要随代码演进做回归）
  3. 你们团队的提交规范是什么？带来什么好处？（要点：Conventional Commits → 可读历史、自动 changelog、按 type 过滤）

## 9. 本周禁止事项

- 不写任何业务代码（FastAPI 是 Day07 的事），不装 Python 依赖。
- 不配 CI（`.gitea/workflows/` 只留空目录，W7 才写）。
- 不部署 MinIO / Qdrant（Day09）。
- 不为痛点设计解决方案、不调研竞品、不选型（Day13）。
- 不在痛点池或任何仓库里写公司名、同事名、业务数据、内部链接。
- 不为规范文档「写得漂亮」超时：规范够用即可，后续以 ADR 形式迭代。

## 10. 时间不够时（最小保留）

1. Day04 P0：模板仓库 + 骨架目录 + `.gitignore` / `.env.example` + `PROJECT_STANDARD.md` §1–§4 + push。
2. Day05 P0：Makefile（help/up/down）+ 模板化 + 生成 `workpilot` + tag `v0.0.0`。
3. Day03 痛点池：压缩为 40 分钟版本（≥ 8 条，只填 ID / 场景 / 痛点 / 频率 / 耗时 / 类型 6 列），放在 Day04 P0 完成后的余量，或替换 Day05 的 P1（安装 uv / pnpm / node 可顺延到 Day07 开头）。
4. 仍不够：痛点池顺延到 Day06 前完成，但必须在 Day10 之前达到 ≥ 8 条。

## 11. 周复盘（周末填写）

- 完成：Docker 底座、Gitea、`PROJECT_STANDARD.md` + 骨架三件套、模板仓库（README/ADR/Makefile/compose/bootstrap）、workpilot 由模板生成、tag `v0.0.0`。
- 未完成：**痛点池 pain-pool.md（Day03）**　原因：日期已过仍未产出，需 Day06 前补齐 ≥ 8 条。
- WorkPilot 本周多了什么可演示的东西：Gitea 上有 `workpilot` 仓库 + tag `v0.0.0`；`make help` 列出 10 个统一入口；README 写清一句话定位与版本路线；`docs/product/target-asset.md` 摘要。
- 是否出现无效学习或范围扩张（如去研究 Gitea 高级功能、写太长的规范）：无；但发现 `infinity/projects` 仓库此前已丢失（Gitea 404），本次通过 API 重建并回推。
- 痛点池现在有几条？最痛的 3 条是：0 条（未建），待补。
- 实际总用时：\_\_\_\_ 分钟（目标 ≤ 5 × 120）
- 下周调整：Day06 开头先补痛点池；Docker Desktop 配代理 127.0.0.1:7890 后重跑 `make up/down` 验收；Day07 起在 `apps/api/` 接 FastAPI。
