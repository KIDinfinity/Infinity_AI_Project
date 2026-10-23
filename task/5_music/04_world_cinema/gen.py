#!/usr/bin/env python3
"""沙漠脉冲 · Desert Pulse —— 世界/电影配乐（马林巴 · 颤音琴 · 大提琴 · 打击乐）。

风格：A 小调（多利亚色彩），♩=120，混合奇数拍号。
节奏变化：7/8（3+2+2）→ 5/8（2+3）→ 7/8 → 4/4 长线条 → 7/8 → 5/8 收束。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music21 import stream, clef, instrument, tempo, meter

from _lib import N, R, CH, UNP, new_score, make_part, write_score

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TITLE = "沙漠脉冲 · Desert Pulse"
COMPOSER = "原创 · AI 生成"
BPM = 120

CHORD_SEQ = (["Am", "Am", "D", "D", "Am", "Am", "G", "F"] +
             ["Am", "Am", "F", "G", "Am", "Am", "F", "G"] +
             ["Am", "Am", "D", "D", "Am", "Am", "G", "F"] +
             ["Am", "G", "F", "D", "Am", "G", "F", "E"] +
             ["Am", "Am", "D", "D", "Am", "Am", "G", "F"] +
             ["Am", "D", "F", "Am"])

MAR = {  # 马林巴低八度和弦音
    "Am": ["A3", "C4", "E4"], "D": ["D3", "F#3", "A3"],
    "G": ["G3", "B3", "D4"], "F": ["F3", "A3", "C4"],
    "E": ["E3", "G#3", "B3"],
}
VIB = {  # 颤音琴旋律音
    "Am": ["A4", "C5", "E5"], "D": ["D4", "F#4", "A4"],
    "G": ["G4", "B4", "D5"], "F": ["F4", "A4", "C5"],
    "E": ["E4", "G#4", "B4"],
}
ROOT = {"Am": "A2", "D": "D2", "G": "G2", "F": "F2", "E": "E2"}


def meter_of(m):
    if 1 <= m <= 8 or 17 <= m <= 24 or 33 <= m <= 40:
        return "7/8", 3.5
    if 9 <= m <= 16 or 41 <= m <= 44:
        return "5/8", 2.5
    return "4/4", 4.0


def marimba_of(m):
    t = MAR[CHORD_SEQ[m - 1]]
    ts, total = meter_of(m)
    if ts == "7/8":
        idx = [0, 0, 1, 2, 0, 1, 0]
        return [N(t[i], 0.5) for i in idx]
    if ts == "5/8":
        idx = [0, 1, 0, 2, 0]
        return [N(t[i], 0.5) for i in idx]
    # 4/4
    idx = [0, 0, 1, 2, 0, 0, 1, 2]
    return [N(t[i], 0.5) for i in idx]


def vibe_of(m):
    t = VIB[CHORD_SEQ[m - 1]]
    ts, total = meter_of(m)
    if ts == "4/4":
        return [N(t[2], 1.5), N(t[1], 0.5), N(t[0], 2.0)]
    if ts == "5/8":
        return [N(t[2], 2.5)]
    return [N(t[2], 1.5), N(t[1], 1.0), N(t[0], 1.0)]


def cello_of(m):
    ch = CHORD_SEQ[m - 1]
    ts, total = meter_of(m)
    return [N(ROOT[ch], total)]


def perc_of(m):
    ts, total = meter_of(m)
    if ts == "7/8":
        return [UNP(36, .5), UNP(38, .5), UNP(40, .5), UNP(36, .5),
                UNP(38, .5), UNP(40, .5), UNP(50, .5)]
    if ts == "5/8":
        return [UNP(36, .5), UNP(38, .5), UNP(40, .5), UNP(36, .5), UNP(38, .5)]
    return [UNP(36, .5), UNP(38, .5), UNP(40, .5), UNP(38, .5),
            UNP(36, .5), UNP(38, .5), UNP(40, .5), UNP(50, .5)]


def build():
    sc = new_score(TITLE, COMPOSER, BPM, "7/8", 0)  # A 小调

    ma = make_part("Marimba", clef.TrebleClef(), instrument.Marimba())
    vb = make_part("Vibraphone", clef.TrebleClef(), instrument.Vibraphone())
    vc = make_part("Cello", clef.BassClef(), instrument.Violoncello())
    pc = make_part("Percussion", clef.PercussionClef(), instrument.UnpitchedPercussion())

    ma_first = None
    for m in range(1, 45):
        ts, total = meter_of(m)
        mm = stream.Measure(number=m)
        mm.insert(0, meter.TimeSignature(ts))
        for n in marimba_of(m):
            mm.append(n)
        if m == 1:
            mm.insert(0, tempo.MetronomeMark(number=BPM))
            ma_first = mm
        ma.append(mm)

        mv = stream.Measure(number=m)
        mv.insert(0, meter.TimeSignature(ts))
        for n in vibe_of(m):
            mv.append(n)
        vb.append(mv)

        mc = stream.Measure(number=m)
        mc.insert(0, meter.TimeSignature(ts))
        for n in cello_of(m):
            mc.append(n)
        vc.append(mc)

        mp = stream.Measure(number=m)
        mp.insert(0, meter.TimeSignature(ts))
        for n in perc_of(m):
            mp.append(n)
        pc.append(mp)

    # 结尾渐慢
    for m, bpm in {42: 108, 43: 96, 44: 84}.items():
        ma[m - 1].insert(0, tempo.MetronomeMark(number=bpm))

    sc.append(ma)
    sc.append(vb)
    sc.append(vc)
    sc.append(pc)
    return sc


if __name__ == "__main__":
    write_score(build(), OUT, "song")
