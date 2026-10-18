# GENERATED_WITH — 本 plan 的生成与落地记录

> 记录「诀别书」3 个月钢琴学习计划从生成到落地全过程用了哪些东西，方便复现或迁移到下一首曲子。

## 1. 规划方式
- 驱动 prompt：`prompt/target_plan_prompt.md`（由用户 draft.md 需求演化而来）
- 拆解原则：目标分细化（4 里程碑 M1–M4）、循序渐进（右手 → 左手 → 双手，慢速 → 原速 → 表现力）、每天只做一件事、每个 day 写清与最终目标的关系
- 结构：3 阶段（Phase01 右手 / Phase02 双手 / Phase03 打磨）× 12 周 × 84 天

## 2. 用到的 prompt / 文档
- `prompt/target_plan_prompt.md` — 通用「给 target 定 plan」的生成规范
- `draft/bye/draft.md` — 用户原始需求（3 个月学会、每天 1 小时、每 week 4 天固定计划）
- `draft/bye/诀别书1~5.jpg` — 5 页谱子图片（原始素材）
- `history/AI半年稳态成长_求职能力_实际应用_资产化_新版计划.md` — 参考的分细化计划风格

## 3. 用到的工具 / 脚本（tools/music/ 通用乐谱工具库）
| 工具/脚本 | 作用 | 状态 |
|-----------|------|------|
| `tools/music/omr/01_preprocess.py` | 5 张图拼接 + 灰度二值化增强 | 已用 |
| `tools/music/omr/02_omr_audiveris.sh` | Audiveris 批量 OMR | 已用（命令行直接调用 Audiveris） |
| `tools/music/score/06_merge_musicxml.py` | 多页 .mxl 合并为整曲（106 小节） | 已用 |
| `tools/music/score/03_parse_musicxml.py` | MusicXML → structure.json（小节/音符/和弦展开） | 已用 |
| `tools/music/score/04_gen_day_sheets.py` | 按 day 切分 → 每日 sheet/{musicxml,mid} | 已用 |
| `tools/music/score/05_make_day_map.py` | day→小节 映射（本例改用 gen_day_map.py） | 未用 |
| `tools/music/score/07_render_sheets.py` | 批量渲染 PDF + PNG | 已用 |
| `tools/music/work/gen_day_map.py` | 生成 84 天「day→小节范围」映射（曲子特定，一次性） | 已用 |
| `tools/music/work/gen_plans.py` | 生成 84 个详细 PLAN.md（曲子特定，一次性） | 已用 |

## 4. 用到的 agent / skill
- 无（本 plan 的规划与脚本编写均由主对话完成，未调用 Explore/其他 subagent）

## 5. 外部依赖 / 环境
- Java 17（`brew install --cask temurin@17`）— Audiveris 运行前提
- Audiveris 5.11.0（arm64 dmg，`/Applications/Audiveris.app`）— 谱面 OMR 识别
- MuseScore 4（`brew install --cask musescore`，`mscore` CLI）— MusicXML 渲染 PDF/PNG
- music21（`uv run --with music21`）— MusicXML 解析/切分/合并
- Pillow（`uv run --with Pillow`）— 图片预处理

## 6. 关键产物
- `tools/music/work/full.mxl` — 全曲完整 MusicXML（106 小节，左右手双声部）
- `tools/music/work/structure.json` — 全曲结构化数据（每小节右手/左手音符、时值）
- `tools/music/work/day_measure_map.json` — 84 天「day → 小节范围」映射
- 84 个 `dayNN_*/sheet/` — 每天专属谱（musicxml + mid + pdf + png）
- 84 个 `dayNN_*/PLAN.md` — 每天详细计划（资产锚点/步骤/验收/谱子引用）

## 7. 已知瑕疵
- Audiveris OMR 对跨小节连音/延音识别不全，部分小节音符稀疏（如某些偶数小节右手为空），练到对应天时需在 MuseScore 对照原图手动补。
