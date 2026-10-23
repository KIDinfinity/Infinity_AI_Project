#!/usr/bin/env python3
"""午夜漫步 · Midnight Stroll —— 爵士三重奏（钢琴 / 低音提琴 / 鼓组）。

风格：B♭ 大调，♩=132，摇摆 4/4，AABA 主题 + 停拍尾声。
节奏变化：摇摆八分、切分 anticipations、三连音装饰、停拍（stop-time）与鼓组 fill。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music21 import stream, clef, instrument, dynamics

from _lib import N, R, CH, UNP, new_score, make_part, add_voices, write_score

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TITLE = "午夜漫步 · Midnight Stroll"
COMPOSER = "原创 · AI 生成"
BPM = 132

# 每小节和弦（40 小节）
HEAD = ["Bb", "G7", "Cm", "F7"]
BRIDGE = ["Eb", "Eb", "Bb", "Bb", "C7", "C7", "F7", "F7"]
OUTRO = ["Bb", "Bb", "G7", "G7", "Cm", "F7", "Bb", "F7"] * 2
CHORDS = HEAD * 2 + BRIDGE + HEAD * 2 + OUTRO

# 低音走线用（每和弦四拍：根 / 五 / 三 / 邻接）
BASS = {
    "Bb": ["Bb2", "F2", "D3", "A2"],
    "G7": ["G2", "D2", "B2", "F2"],
    "Cm": ["C2", "G2", "Eb3", "Bb2"],
    "F7": ["F2", "C2", "A2", "Eb2"],
    "Eb": ["Eb2", "Bb2", "G3", "D3"],
    "C7": ["C2", "G2", "E3", "Bb2"],
}
# 钢琴左手 comp 声部
VOICING = {
    "Bb": ["D4", "F4", "A4"],
    "G7": ["F4", "B4", "D5"],
    "Cm": ["Eb4", "G4", "Bb4"],
    "F7": ["Eb4", "A4", "C5"],
    "Eb": ["G4", "Bb4", "D5"],
    "C7": ["E4", "Bb4", "C5"],
}

# 主题旋律（右手）
MELODY = {
    1: [N("D5", 1.5), N("C5", 0.5), N("Bb4", 1.0), N("D5", 1.0)],
    2: [N("F5", 2.0), N("D5", 1.0), N("B4", 1.0)],
    3: [N("C5", 1.5), N("Bb4", 0.5), N("Eb5", 1.0), N("D5", 1.0)],
    4: [N("C5", 2.0), N("A4", 1.0), N("C5", 1.0)],
    5: [N("Bb4", 1.5), N("C5", 0.5), N("D5", 1.0), N("F5", 1.0)],
    6: [N("D5", 2.0), N("F5", 1.0), N("D5", 1.0)],
    7: [N("Eb5", 1.5), N("D5", 0.5), N("C5", 1.0), N("Bb4", 1.0)],
    8: [N("A4", 2.0), N("G4", 1.0), N("A4", 1.0)],
    9: [N("G4", 1.5), N("Bb4", 0.5), N("Eb5", 1.0), N("D5", 1.0)],
    10: [N("Eb5", 2.0), N("G5", 1.0), N("F5", 1.0)],
    11: [N("D5", 2.0), N("F5", 1.0), N("D5", 1.0)],
    12: [N("Bb4", 2.0), N("C5", 1.0), N("D5", 1.0)],
    13: [N("E5", 1.5), N("D5", 0.5), N("C5", 1.0), N("E5", 1.0)],
    14: [N("G5", 2.0), N("E5", 1.0), N("C5", 1.0)],
    15: [N("A4", 1.5), N("Bb4", 0.5), N("C5", 1.0), N("A4", 1.0)],
    16: [N("F4", 2.0), N("G4", 1.0), N("A4", 1.0)],
    17: [N("D5", 1.5), N("C5", 0.5), N("Bb4", 1.0), N("D5", 1.0)],
    18: [N("F5", 2.0), N("D5", 1.0), N("B4", 1.0)],
    19: [N("C5", 1.5), N("Bb4", 0.5), N("Eb5", 1.0), N("D5", 1.0)],
    20: [N("C5", 2.0), N("A4", 1.0), N("C5", 1.0)],
    21: [N("Bb4", 1.5), N("C5", 0.5), N("D5", 1.0), N("F5", 1.0)],
    22: [N("D5", 2.0), N("F5", 1.0), N("D5", 1.0)],
    23: [N("Eb5", 1.5), N("D5", 0.5), N("C5", 1.0), N("Bb4", 1.0)],
    24: [N("A4", 1.0), N("Bb4", 1.0), N("C5", 1.0), N("D5", 1.0)],
}
# 尾声停拍 riff（右手）
OUTRO_MEL = {
    25: [N("Bb4", 1.0), R(1.0), N("Bb4", 1.0), R(1.0)],
    26: [R(4.0)],
    27: [N("D5", 1.0), N("F5", 1.0), R(2.0)],
    28: [R(4.0)],
    29: [N("Eb5", 1.0), N("D5", 1.0), R(2.0)],
    30: [N("C5", 1.0), N("A4", 1.0), R(2.0)],
    31: [N("Bb4", 1.0), R(1.0), N("D5", 1.0), R(1.0)],
    32: [R(4.0)],
    33: [N("Bb4", 1.0), R(1.0), N("Bb4", 1.0), R(1.0)],
    34: [R(4.0)],
    35: [N("D5", 1.0), N("F5", 1.0), R(2.0)],
    36: [R(4.0)],
    37: [N("Eb5", 1.0), N("D5", 1.0), R(2.0)],
    38: [N("C5", 1.0), N("A4", 1.0), R(2.0)],
    39: [N("D5", 2.0), R(2.0)],
    40: [N("Bb4", 4.0)],
}

STOP_BARS = set(range(25, 41))  # 尾声为停拍段


def melody_of(m):
    return OUTRO_MEL.get(m, MELODY.get(m, [R(4.0)]))


def comp_of(m):
    v = VOICING[CHORDS[m - 1]]
    if m in STOP_BARS:
        return [CH(v, 1.0), R(3.0)]
    return [R(1.0), CH(v, 1.0), R(1.0), CH(v, 1.0)]


def bass_of(m):
    b = BASS[CHORDS[m - 1]]
    return [N(b[0], 1.0), N(b[1], 1.0), N(b[2], 1.0), N(b[3], 1.0)]


def drums_of(m):
    ride = [UNP(51, 0.5) for _ in range(8)]
    slots = [36, 42, 38, 42, 36, 42, 38, 42]
    time_v = [UNP(s, 0.5) for s in slots]
    if m in STOP_BARS:
        ride = [UNP(49, 1.0), R(1.0), UNP(51, 0.5), UNP(51, 0.5),
                UNP(51, 0.5), UNP(51, 0.5)]
        time_v = [UNP(36, 1.0), UNP(38, 1.0), UNP(38, 0.5), UNP(38, 0.5),
                  UNP(38, 0.5), UNP(38, 0.5)]
    elif m % 8 == 0:  # 乐句末 fill
        time_v = [UNP(s, 0.5) for s in [36, 42, 38, 42, 36, 38, 38, 38]]
    return [ride, time_v]


def build():
    sc = new_score(TITLE, COMPOSER, BPM, "4/4", -2)  # B♭ 大调 = 2 个降号

    pno = make_part("Piano", clef.TrebleClef(), instrument.Piano())
    pno_b = make_part("Piano", clef.BassClef(), instrument.Piano())
    bs = make_part("Double Bass", clef.BassClef(), instrument.Contrabass())
    dr = make_part("Drums", clef.PercussionClef(), instrument.UnpitchedPercussion())

    rh_meas = []
    for m in range(1, 41):
        mrh = stream.Measure(number=m)
        for n in melody_of(m):
            mrh.append(n)
        if m in STOP_BARS and m > 25:
            mrh.append(dynamics.Dynamic("mp"))
        pno.append(mrh)
        rh_meas.append(mrh)

        mlh = stream.Measure(number=m)
        for n in comp_of(m):
            mlh.append(n)
        pno_b.append(mlh)

        mb = stream.Measure(number=m)
        for n in bass_of(m):
            mb.append(n)
        bs.append(mb)

        md = stream.Measure(number=m)
        add_voices(md, drums_of(m))
        dr.append(md)

    # 首拍速度
    rh_meas[0].insert(0, __import__("music21").tempo.MetronomeMark(number=BPM))
    # 尾声渐慢
    from music21 import tempo
    rit = {38: 124, 39: 112, 40: 100}
    for m, bpm in rit.items():
        rh_meas[m - 1].insert(0, tempo.MetronomeMark(number=bpm))

    sc.append(pno)
    sc.append(pno_b)
    sc.append(bs)
    sc.append(dr)
    return sc


if __name__ == "__main__":
    write_score(build(), OUT, "song")
