# GENERATED_WITH — 本 plan 的生成与落地记录

> 记录「宿命五章 · 5 首原创吉他曲创作计划」从生成到落地用了哪些东西，方便复现或迁移到下一个创作 target。

## 1. 规划方式
- 驱动 prompt：`prompt/target_plan_prompt.md`
- 用户 target：5 首原创吉他曲，宿命感强，每首 3 分钟，周期 1 个月
- 拆解原则：目标分细化（4 里程碑 M1–M4）、循序渐进（方法论 → 打样 → 批量 → 打磨录音）、每天只做一件事、每个 day 写清与最终 target 的关系
- 结构：3 阶段 × 4 周 × 5 天 = 20 天；每首曲子 3 天（动机+和声 → 段落拼装 → 记谱打磨）

## 2. 用到的 prompt / 文档
- `prompt/target_plan_prompt.md` — 通用「给 target 定 plan」的生成规范
- `plan/plan_ai/phase_02/week_09/day34_20261123/PLAN.md` — 密度与风格参照（资产锚点 / 验收对齐 / 执行步骤具体化）
- `plan/plan_guitar_rumbling/` — 吉他类 plan 的谱面 / 工具参照

## 3. 用到的工具 / 脚本
| 工具/脚本 | 作用 | 状态 |
| --- | --- | --- |
| Guitar Pro / TuxGuitar | 手工录入当天创作的小节，导出 `.gp` | 未用（创作期使用） |
| MuseScore 4（`mscore` CLI） | 记谱 + 导出 PDF / 音频 demo | 未用（创作期使用） |
| `tools/music/` 脚本（PyGuitarPro / MusicXML 处理） | 后续如需批量切分/导出分谱可复用 | 未用 |

## 4. 用到的 agent / skill
- 无（规划由主对话完成）

## 5. 外部依赖 / 环境
- 吉他 + 调音器 + 节拍器（手机 App 或实体）
- 录音设备：手机 / 声卡 + 麦克风（M4 阶段录音）
- 记谱软件：Guitar Pro / TuxGuitar / MuseScore（任一）

## 6. 关键产物
- `plan_guitar_compose/TARGET.md` — 目标蓝图（5 首定位 + 里程碑 + 宿命感创作语法）
- `plan_guitar_compose/phase_*/*/dayNN_*/PLAN.md` — 20 天详细计划
- 创作期实际产物（每首的 `.gp`/`.pdf`/录音）在 day 目录内，随执行产出
