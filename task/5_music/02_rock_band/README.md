# 裂变脉冲 · Split Pulse — 摇滚乐队

E 小调 · ♩=150 · 4/4。电吉他 / 电贝斯 / 鼓组。

节奏：3+3+2 切分 riff、半速 breakdown、16 分双倍速结尾 + 渐快。

## 生成

```bash
cd 02_rock_band
uv run --with music21 python gen.py
cd out
mscore -o song.pdf song.musicxml
mscore -o song.mp3 song.musicxml
```
