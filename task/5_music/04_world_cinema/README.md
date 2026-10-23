# 沙漠脉冲 · Desert Pulse — 世界 / 电影配乐

A 小调（多利亚）· ♩=120 · 奇数拍号。马林巴 · 颤音琴 · 大提琴 · 打击乐。

节奏：7/8（3+2+2）→ 5/8（2+3）→ 7/8 → 4/4 → 7/8 → 5/8。

## 生成

```bash
cd 04_world_cinema
uv run --with music21 python gen.py
cd out
mscore -o song.pdf song.musicxml
mscore -o song.mp3 song.musicxml
```
