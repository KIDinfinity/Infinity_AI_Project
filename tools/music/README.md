# tools/music — 音乐与乐器工具

钢琴、吉他、任何五线谱/简谱乐器的通用谱面处理工具，分两个功能组：

| 子目录 | 功能 | 输入 → 输出 |
|--------|------|-------------|
| `omr/`   | 谱面识别（OMR） | 谱子图片 → MusicXML |
| `score/` | 乐谱解析与切分 | MusicXML → 结构化 JSON → 每日小谱（MusicXML + MIDI） |

## 工具清单

| 脚本 | 作用 |
|------|------|
| `omr/01_preprocess.py` | 多张图片拼接 + 增强 → 预处理长图 |
| `omr/02_omr_audiveris.sh` | Audiveris OMR（离线开源，最准） |
| `omr/02_omr_vision.py` | 本地视觉 LLM 兜底（Ollama） |
| `score/06_merge_musicxml.py` | 多页 .mxl 合并为整曲（重排小节号、打平多 voice） |
| `score/03_parse_musicxml.py` | MusicXML → 结构化 JSON（小节/音符/时值/和弦展开） |
| `score/05_make_day_map.py` | 生成 day→小节 映射（均分或按页） |
| `score/04_gen_day_sheets.py` | 按 day 切分 → 每日 MusicXML + MIDI |

> `work/` 是中间产物目录，可随时删除重建，不要放需要长期保留的东西。

## 已跑通的实例（诀别书）

- 环境：`brew install --cask temurin@17` + Audiveris 5.11.0（arm64 dmg，已装 `/Applications/Audiveris.app`）。
- OMR 结果：5 页 → 106 小节（页边界 31/24/24/20/7），导出 `work/full.mxl`。
- 产物：84 个 day 目录下各有 `sheet/sheet.musicxml` + `sheet/sheet.mid`。
