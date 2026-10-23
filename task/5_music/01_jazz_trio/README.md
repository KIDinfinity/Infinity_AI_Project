# 午夜漫步 · Midnight Stroll — 爵士三重奏

B♭ 大调 · ♩=132 · 4/4 摇摆。钢琴 / 低音提琴 / 鼓组。

节奏：摇摆八分、切分、停拍尾声、鼓组 fill。

## 生成

```bash
cd 01_jazz_trio
uv run --with music21 python gen.py
cd out
mscore -o song.pdf song.musicxml
mscore -o song.mp3 song.musicxml
```
