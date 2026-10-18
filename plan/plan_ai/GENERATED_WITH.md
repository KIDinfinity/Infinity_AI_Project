# GENERATED_WITH — 本 plan 的生成与落地记录

> 记录 WorkPilot（DA-01）半年计划是怎么被做出来的，方便复现或迁移。

## 1. 规划方式
- 驱动：两份源计划结构化而来（见 §2），由 AI 拆分到「阶段 → 周 → 天」三级目录
- 拆解原则：目标分细化（26 周 → 3 阶段 → 周 → Day，模块编号 M0–M14 = 资产锚点）、里程碑版本化（v0.0 → v0.5 P1 → v1.0 P2 → v2.0 P3）、每个 day 写清「资产锚点 + 与最终产品的关系 + 验收」
- 结构：3 阶段 × 26 周 × 77 天（W1–2 每周 5 天，W3 起改周一–周四/更少）

## 2. 用到的 prompt / 文档
- `history/0_半年稳态成长+睡后收入+AI能力沉淀终极落地计划（每日1-2小时·可永久复用）.md` — 源总计划
- `history/AI半年稳态成长_求职能力_实际应用_资产化_新版计划.md` — 源计划（新版，主参考）
- `history/半年稳态成长+睡后收入+AI能力沉淀_第1-8周详细目标与验收版.md` — 第 1–8 周详细版源计划
- `prompt/项目结构变更.md`、`prompt/需求拆解.md` — 多 project 结构改造需求
- `GLOBAL_CONTEXT.md`、`PROJECT_CONFIG.md` — 项目级最高判断标准与配置

## 3. 用到的工具 / 脚本
| 工具/脚本 | 作用 | 状态 |
|-----------|------|------|
| `plan/CHANGELOG.md` 记录过的目录重命名批量替换 | 日历重排时 67 个 day 目录 + 498 处日期引用批量改 | 已用（一次性） |

## 4. 用到的 agent / skill
- 规划与文档生成主要由主对话完成；执行期（Day 计划落地到代码）会按需调用 Explore subagent 做仓库探索、Pylance 系列工具做 Python 诊断。

## 5. 外部依赖 / 环境
- 无专门乐谱/图像类工具链（本 plan 是软件研发计划，产物在 `~/lab/workpilot` 仓库）
- 执行期依赖：Docker、Gitea、uv、DeepSeek API、Ollama（embedding）、Qdrant、MinIO 等（见 DA01_TARGET_ASSET.md 架构）

## 6. 关键产物
- `DA01_TARGET_ASSET.md` — 最终产品蓝图（模块编号 = 资产锚点）
- `README.md` — 26 周总路线
- `phase_01/02/03/` — 三阶段，每周 README + TASKS + 逐日 PLAN.md
- 对应代码仓库 `~/lab/workpilot`（Gitea + GitHub）
