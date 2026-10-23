#!/usr/bin/env python3
"""裂变脉冲 · Split Pulse —— 摇滚乐队（电吉他 / 电贝斯 / 鼓组）。

风格：E 小调，♩=150，4/4 摇滚。
节奏变化：3+3+2 切分 riff、副歌强力和弦、半速 breakdown、结尾 16 分双倍速冲刺。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music21 import stream, clef, instrument, tempo

from _lib import N, R, CH, UNP, new_score, make_part, add_voices, write_score

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TITLE = "裂变脉冲 · Split Pulse"
COMPOSER = "原创 · AI 生成"
BPM = 150

E5 = ["E3", "B3", "E4"]
G5 = ["G3", "D4", "G4"]
A5 = ["A3", "E4", "A4"]
C5 = ["C3", "G3", "C4"]
D5 = ["D3", "A3", "D4"]


def rep(p, n, d):
    return [N(p, d) for _ in range(n)]


def build_guitar():
    g = []
    for _ in range(4):  # A m1-8
        g.append(rep("E3", 4, 0.5) + rep("G3", 2, 0.5) + rep("E3", 2, 0.5))
        g.append(rep("A3", 2, 0.5) + rep("G3", 2, 0.5) + rep("E3", 2, 0.5) + rep("B3", 2, 0.5))
    for _ in range(4):  # B m9-16
        g.append(rep("E3", 2, 0.5) + [N("G3", 0.5)] + [N("A3", 0.5)] + rep("E3", 2, 0.5) + [N("D3", 0.5)] + [N("E3", 0.5)])
        g.append(rep("B3", 2, 0.5) + rep("A3", 2, 0.5) + rep("G3", 2, 0.5) + rep("E3", 2, 0.5))
    ch = [E5, G5, A5, C5, E5, G5, D5, A5]  # 副歌 m17-24
    for c in ch:
        g.append([CH(c, 2.0), CH(c, 2.0)])
    for _ in range(4):  # A' m25-32
        g.append(rep("E3", 4, 0.5) + rep("G3", 2, 0.5) + rep("E3", 2, 0.5))
        g.append(rep("A3", 2, 0.5) + rep("G3", 2, 0.5) + rep("E3", 2, 0.5) + rep("B3", 2, 0.5))
    bd = [E5, A5, E5, C5, E5, A5, D5, D5]  # breakdown m33-40
    for c in bd:
        g.append([CH(c, 2.0), R(2.0)])
    for _ in range(7):  # 结尾 16 分双倍速 m41-47
        g.append(rep("E3", 16, 0.25))
    g.append([CH(E5, 4.0)])  # m48
    return g


def build_bass():
    roots = (["E"] * 8 +
             ["E", "G", "A", "E", "B", "A", "G", "E"] +
             ["E", "G", "A", "C", "E", "G", "D", "A"] +
             ["E"] * 8 +
             ["E", "A", "E", "C", "E", "A", "D", "D"] +
             ["E"] * 8)
    lines = []
    for i, r in enumerate(roots):
        m = i + 1
        n = f"{r}2"
        if 17 <= m <= 24:
            lines.append([N(n, 2.0), N(n, 2.0)])
        elif 33 <= m <= 40:
            lines.append([N(n, 4.0)])
        elif 41 <= m <= 47:
            lines.append([N(n, 0.25) for _ in range(16)])
        else:
            lines.append([N(n, 0.5) for _ in range(8)])
    lines[47] = [N("E2", 4.0)]
    return lines


def drums_of(m):
    if m == 48:
        return [[UNP(49, 1.0), R(3.0)], [UNP(36, 1.0), UNP(38, 1.0), R(2.0)]]
    if 33 <= m <= 40:  # half-time breakdown
        v2 = [UNP(s, 0.5) if s else R(0.5) for s in [36, None, None, None, 38, None, None, None]]
        return [[UNP(42, 0.5) for _ in range(8)], v2]
    if 41 <= m <= 47:  # double-time
        v2 = [UNP(36, 0.5)] + [UNP(38, 0.25) for _ in range(12)] + [UNP(36, 0.5)]
        return [[UNP(42, 0.5) for _ in range(8)], v2]
    v1 = [UNP(42, 0.5) for _ in range(8)]
    v2 = [UNP(s, 0.5) if s else R(0.5) for s in [36, None, 38, None, 36, None, 38, None]]
    if m % 8 == 0:  # 乐句末 fill
        v2 = ([UNP(36, 0.5), R(0.5), UNP(38, 0.5), R(0.5)] +
              [UNP(38, 0.25) for _ in range(7)] + [UNP(38, 0.5)])
    return [v1, v2]


def build():
    sc = new_score(TITLE, COMPOSER, BPM, "4/4", -1)  # E 小调 = 1 个升号

    gt = make_part("Electric Guitar", clef.TrebleClef(), instrument.ElectricGuitar())
    bs = make_part("Electric Bass", clef.BassClef(), instrument.ElectricBass())
    dr = make_part("Drums", clef.PercussionClef(), instrument.UnpitchedPercussion())

    guitar = build_guitar()
    bass = build_bass()

    for m in range(1, 49):
        mg = stream.Measure(number=m)
        for n in guitar[m - 1]:
            mg.append(n)
        if m == 1:
            mg.insert(0, tempo.MetronomeMark(number=BPM))
        gt.append(mg)

        mb = stream.Measure(number=m)
        for n in bass[m - 1]:
            mb.append(n)
        bs.append(mb)

        md = stream.Measure(number=m)
        add_voices(md, drums_of(m))
        dr.append(md)

    for m, bpm in {45: 160, 46: 170, 47: 180, 48: 192}.items():
        gt[m - 1].insert(0, tempo.MetronomeMark(number=bpm))

    sc.append(gt)
    sc.append(bs)
    sc.append(dr)
    return sc


if __name__ == "__main__":
    write_score(build(), OUT, "song")
