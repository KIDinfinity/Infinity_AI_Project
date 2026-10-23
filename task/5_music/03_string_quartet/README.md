# 潮汐 · Tide — 弦乐四重奏

D 小调 · ♩=88 · 多拍号。小提琴 I/II · 中提琴 · 大提琴。

节奏：3/4 → 6/8 → 5/8 → 4/4 → 3/4 → 5/8。

## 生成

```bash
cd 03_string_quartet
uv run --with music21 python gen.py
cd out
mscore -o song.pdf song.musicxml
mscore -o song.mp3 song.musicxml
```
