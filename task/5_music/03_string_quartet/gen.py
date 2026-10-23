#!/usr/bin/env python3
"""潮汐 · Tide —— 弦乐四重奏（小提琴 I/II · 中提琴 · 大提琴）。

风格：D 小调，♩=88，多拍号交替。
节奏变化：3/4 → 6/8 → 5/8 → 4/4 → 3/4 再现 → 5/8 收束。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music21 import stream, clef, instrument, tempo, meter, dynamics

from _lib import N, R, CH, new_score, make_part, write_score

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TITLE = "潮汐 · Tide"
COMPOSER = "原创 · AI 生成"
BPM = 88

CHORD_SEQ = (["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "A"] +
             ["Dm", "Dm", "Bb", "Bb", "F", "C", "Dm", "A"] +
             ["Dm", "Gm", "Bb", "A", "Dm", "Gm", "A", "A"] +
             ["Dm", "Bb", "F", "C", "Dm", "Bb", "A", "A"] +
             ["Dm", "Bb", "F", "C", "Dm", "Bb", "Gm", "A"] +
             ["Dm", "Bb", "A", "Dm"])

CH_NOTES = {
    "Dm": ["D4", "F4", "A4"], "Bb": ["D4", "F4", "Bb4"],
    "F": ["C4", "F4", "A4"], "C": ["C4", "E4", "G4"],
    "Gm": ["D4", "G4", "Bb4"], "A": ["C#4", "E4", "A4"],
}
CH_HI = {
    "Dm": ["D5", "F5", "A5"], "Bb": ["D5", "F5", "Bb5"],
    "F": ["C5", "F5", "A5"], "C": ["C5", "E5", "G5"],
    "Gm": ["D5", "G5", "Bb5"], "A": ["C#5", "E5", "A5"],
}
ROOT_BASS = {"Dm": "D2", "Bb": "Bb1", "F": "F2", "C": "C2", "Gm": "G1", "A": "A1"}
FIFTH_BASS = {"Dm": "A2", "Bb": "F2", "F": "C3", "C": "G2", "Gm": "D2", "A": "E2"}

MEL_34 = {
    1: [N("A4", 1.0), N("D5", 1.0), N("F5", 1.0)],
    2: [N("D5", 1.5), N("C5", 1.5)],
    3: [N("A4", 1.0), N("C5", 1.0), N("F5", 1.0)],
    4: [N("E5", 1.5), N("D5", 1.5)],
    5: [N("D5", 1.0), N("A4", 1.0), N("F4", 1.0)],
    6: [N("Bb4", 1.5), N("A4", 1.5)],
    7: [N("G4", 1.0), N("Bb4", 1.0), N("D5", 1.0)],
    8: [N("C#5", 2.0), N("E5", 1.0)],
}
MEL_44 = {
    25: [N("D5", 2.0), N("F5", 1.0), N("A5", 1.0)],
    26: [N("Bb5", 2.0), N("A5", 1.0), N("G5", 1.0)],
    27: [N("F5", 2.0), N("A5", 1.0), N("C6", 1.0)],
    28: [N("E5", 2.0), N("G5", 1.0), N("E5", 1.0)],
    29: [N("D5", 2.0), N("F5", 1.0), N("A5", 1.0)],
    30: [N("Bb5", 2.0), N("G5", 1.0), N("F5", 1.0)],
    31: [N("A5", 2.0), N("C#5", 1.0), N("E5", 1.0)],
    32: [N("A5", 4.0)],
}


def meter_of(m):
    if 1 <= m <= 8 or 33 <= m <= 40:
        return "3/4", 3.0
    if 9 <= m <= 16:
        return "6/8", 3.0
    if 17 <= m <= 24 or 41 <= m <= 44:
        return "5/8", 2.5
    return "4/4", 4.0


def vln1_of(m):
    ch = CHORD_SEQ[m - 1]
    if 1 <= m <= 8:
        return MEL_34[m]
    if 9 <= m <= 16:
        t = CH_HI[ch]
        return [N(t[0], .5), N(t[1], .5), N(t[2], .5), N(t[2], .5), N(t[1], .5), N(t[0], .5)]
    if 17 <= m <= 24:
        t = CH_HI[ch]
        return [N(t[0], .5), N(t[2], .5), N(t[1], .5), N(t[2], .5), N(t[0], .5)]
    if 25 <= m <= 32:
        return MEL_44[m]
    if 33 <= m <= 40:
        return MEL_34[m - 32]
    if m == 41:
        t = CH_HI["Dm"]
        return [N(t[0], .5), N(t[2], .5), N(t[1], .5), N(t[2], .5), N(t[0], .5)]
    if m == 42:
        t = CH_HI["Bb"]
        return [N(t[0], .5), N(t[2], .5), N(t[1], .5), N(t[2], .5), N(t[0], .5)]
    if m == 43:
        return [N("A5", 1.5), N("C#5", 1.0)]
    return [N("D5", 2.5)]


def vln2_of(m):
    ch = CHORD_SEQ[m - 1]
    ts, total = meter_of(m)
    if ts == "5/8":
        return [N(CH_NOTES[ch][1], 1.5), N(CH_NOTES[ch][2], 1.0)]
    return [N(CH_NOTES[ch][1], total)]


def vla_of(m):
    ch = CHORD_SEQ[m - 1]
    ts, total = meter_of(m)
    tones = CH_NOTES[ch]
    n = int(total / 0.5)
    return [N(tones[i % 3], 0.5) for i in range(n)]


def cello_of(m):
    ch = CHORD_SEQ[m - 1]
    ts, total = meter_of(m)
    r, f = ROOT_BASS[ch], FIFTH_BASS[ch]
    if ts == "6/8":
        return [N(r, total)]
    if ts == "5/8":
        return [N(r, 1.5), N(f, 1.0)]
    if ts == "4/4":
        return [N(r, 2.0), N(f, 2.0)]
    return [N(r, 2.0), N(f, 1.0)]


def build():
    sc = new_score(TITLE, COMPOSER, BPM, "3/4", -1)  # D 小调

    v1 = make_part("Violin I", clef.TrebleClef(), instrument.Violin())
    v2 = make_part("Violin II", clef.TrebleClef(), instrument.Violin())
    va = make_part("Viola", clef.AltoClef(), instrument.Viola())
    vc = make_part("Cello", clef.BassClef(), instrument.Violoncello())

    v1_first = None
    for m in range(1, 45):
        ts, total = meter_of(m)
        mv1 = stream.Measure(number=m)
        mv1.insert(0, meter.TimeSignature(ts))
        for n in vln1_of(m):
            mv1.append(n)
        if m == 1:
            mv1.insert(0, tempo.MetronomeMark(number=BPM))
            v1_first = mv1
        v1.append(mv1)

        mv2 = stream.Measure(number=m)
        mv2.insert(0, meter.TimeSignature(ts))
        for n in vln2_of(m):
            mv2.append(n)
        v2.append(mv2)

        mva = stream.Measure(number=m)
        mva.insert(0, meter.TimeSignature(ts))
        for n in vla_of(m):
            mva.append(n)
        va.append(mva)

        mvc = stream.Measure(number=m)
        mvc.insert(0, meter.TimeSignature(ts))
        for n in cello_of(m):
            mvc.append(n)
        vc.append(mvc)

    # 结尾渐慢
    for m, bpm in {42: 80, 43: 72, 44: 64}.items():
        v1[m - 1].insert(0, tempo.MetronomeMark(number=bpm))

    sc.append(v1)
    sc.append(v2)
    sc.append(va)
    sc.append(vc)
    return sc


if __name__ == "__main__":
    write_score(build(), OUT, "song")
