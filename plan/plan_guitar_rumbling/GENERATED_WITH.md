# GENERATED_WITH — 本 plan 的生成与落地记录

> 记录「The Rumbling 电吉他 4 轨合奏学习计划」从生成到落地用了哪些东西，方便复现或迁移到下一首曲子。

## 1. 规划方式
- 驱动 prompt：`prompt/target_plan_prompt.md`
- 拆解原则：目标分细化（5 里程碑 M1–M5）、循序渐进（基本功 → 分轨 → 合奏 → 提速 → 录音）、每天只做一件事、每个 day 写清与最终目标的关系
- 结构：3 阶段 × 16 周 × 5 天 = 80 天

## 2. 用到的 prompt / 文档
- `prompt/target_plan_prompt.md` — 通用「给 target 定 plan」的生成规范
- `draft/rumbling/rumb_stand_summary.md` — 谱面解析说明（轨道/调弦/速度）
- `draft/rumbling/rumb_stand.gp5` — 总谱源文件（4 轨）
- `draft/rumbling/rumb_stand1~4.pdf` — 分谱（Guitar3 / Rhythm1 / Rhythm2 / Solo）

## 3. 用到的工具 / 脚本
| 工具/脚本 | 作用 | 状态 |
| --- | --- | --- |
| `tools/music/work/rumb_extract.py` | PyGuitarPro 解析 gp5 → `rumb_data.json`（小节/音符/时值/演奏技巧标记/日历） | 已用 |
| `tools/music/work/gen_rumb_plans.py` | 读取 rumb_data.json → 渲染 tab + 逐小节精练清单（音符/和弦/把位/技巧）+ 生成 80 个 PLAN.md | 已用 |
| `tools/music/work/gen_rumb_docs.py` | 生成 README/TARGET/GENERATED_WITH/phase/week 文档 | 已用 |
| `tools/music/work/gen_rumb_sheets.py` | 切分总谱 → 每个 day 的 `sheet/sheet.gp5`（+ `--pdf` 转 `sheet.pdf`） | 已用 |
| `tools/music/work/dump_rumb.py` | 采样打印各轨小节音符（排查用） | 已用 |

## 4. 用到的 agent / skill
- 无（规划与脚本编写由主对话完成）

## 5. 外部依赖 / 环境
- Python + `PyGuitarPro`（`uv run --with PyGuitarPro`）— 解析 + 写出 Guitar Pro 5 文件
- MuseScore 4（`mscore` CLI，`/opt/homebrew/bin/mscore`）— gp5 → PDF 渲染
- 标准库 json / os / datetime / subprocess — 数据结构、日历与外部命令调用

## 6. 关键产物
- `tools/music/work/rumb_data.json` — 全曲结构化数据（4 轨逐小节音符+时值）
- `tools/music/work/rumb_extract.py` — 数据提取脚本（可复现）
- `tools/music/work/gen_rumb_plans.py` — 计划生成脚本（可复现/可改 DAYMAP 后重跑）
- `tools/music/work/gen_rumb_sheets.py` — 分谱切分脚本（可复现/`--pdf` 切换）
- 80 个 `dayNN_DATE/PLAN.md` — 每天详细计划（含真实 tab 谱面）
- 76 个 `dayNN_DATE/sheet.gp5` + `sheet.pdf` — 每天专属分谱（基本功日无谱面）

## 7. 已知瑕疵
- 每个 PLAN 的「本日精练清单」已自动标注推弦/击弦/滑音/闷音/揉弦/延音/泛音等技巧记号，但「第 9 节」的 ASCII tab 本身仅按 16 分音符分辨率对齐、不含技巧记号，练到对应小节仍建议对照 gp5/PDF 原谱核对。
- 时值取整到 16 分格，三连音等细分节奏在 tab 中会被近似对齐，以原谱为准。
