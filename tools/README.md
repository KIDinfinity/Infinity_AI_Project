# tools — 通用工具库

> 与任何单个 plan / 曲子无关的可复用工具，按「领域 → 功能」分类。
> 每个 plan（如 `plan/plan_piano`）只存放该 plan 自己的产物（计划、每日谱），不存放工具。

## 目录约定

```text
tools/
├── README.md          ← 本文件
├── music/             ← 音乐与乐器领域
│   ├── README.md
│   ├── omr/           ← 谱面识别：图片 → MusicXML
│   ├── score/         ← 乐谱处理：MusicXML → 结构化 → 按天切分
│   └── work/          ← 中间产物（自动创建，可随时清理）
└── （未来：其他领域，如 image/、audio/、doc/ …）
```

## 分类原则

1. **按领域建目录**（music / image / audio …），领域内再按功能分子目录（omr / score …）。
2. **工具与 plan 解耦**：脚本一律接受 `--plan-root` / `--src-dir` 等参数，不硬编码某个曲子的路径；任何钢琴曲、吉他曲、其他乐器谱都能复用。
3. **中间产物集中在 `work/`**：可随时删除重建；每个 plan 自己的最终产物（每日谱子）才写到该 plan 目录下。
4. **一个工具做一件事**，编号表示链路上的先后顺序，可单独复用。

## 音乐谱面处理链路（钢琴/吉他/任何乐器通用）

```text
谱子图片(多张)
  → tools/music/omr/01_preprocess.py      拼接+增强 → work/preprocessed.png
  → tools/music/omr/02_omr_audiveris.sh   或 02_omr_vision.py → 每页 .mxl
  → tools/music/score/06_merge_musicxml.py 合并多页 → work/full.mxl
  → tools/music/score/03_parse_musicxml.py  MusicXML → work/structure.json
  → tools/music/score/05_make_day_map.py    day编号 → 小节范围 → work/day_measure_map.json
  → tools/music/score/04_gen_day_sheets.py  切分 → 每个 day 的 sheet/{musicxml,mid} 写入目标 plan
```

用法示例（以 plan_piano 为例）：

```bash
cd /Users/infinity/Documents/a_future
uv run --with Pillow --with music21 python tools/music/omr/01_preprocess.py \
    --src-dir draft/bye --out tools/music/work/preprocessed.png
# OMR 出 full.mxl 后：
uv run --with music21 python tools/music/score/03_parse_musicxml.py \
    --src tools/music/work/full.mxl --out tools/music/work/structure.json
uv run --with music21 python tools/music/score/05_make_day_map.py \
    --struct tools/music/work/structure.json --out tools/music/work/day_measure_map.json
uv run --with music21 python tools/music/score/04_gen_day_sheets.py \
    --plan-root plan/plan_piano --src tools/music/work/full.mxl --map tools/music/work/day_measure_map.json
```
