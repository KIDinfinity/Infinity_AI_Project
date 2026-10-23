#!/usr/bin/env python3
"""生成「诀别 · 宿命」—— 宿命感强的原创钢琴曲（约 3 分钟）。

风格锚点：D 小调、♩=60、i–VI–III–VII 宿命循环 + 哀歌低音 D–C–B♭–A、
叹息动机（下行二度）贯穿全曲。

用法：
    uv run --with music21 python gen.py
    # 再渲染 PDF / MP3：
    mscore -o out/song.pdf out/song.musicxml
    mscore -o out/song.mp3 out/song.musicxml

依赖：music21；渲染需 MuseScore（mscore）。
"""
import os

from music21 import (
    stream, note, chord, meter, key, tempo, clef,
    instrument, metadata, dynamics, expressions, pitch,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

TITLE = "诀别 · 宿命"
COMPOSER = "原创 · AI 生成"
BPM = 60


def N(p, d=1.0):
    return note.Note(p, quarterLength=d)


def R(d=1.0):
    return note.Rest(quarterLength=d)


def CH(ps, d=1.0):
    return chord.Chord(list(ps), quarterLength=d)


def down8(p):
    return pitch.Pitch(p).transpose(-12).nameWithOctave


# ---------------------------------------------------------------------------
# 和声表：每小节 → (低音, 三音, 五音, 八度音)
# ---------------------------------------------------------------------------
def chord_of(m):
    dm = ("D2", "F3", "A3", "D4")
    bb = ("Bb1", "D3", "F3", "Bb3")
    f_ = ("F2", "A2", "C3", "F3")
    c_ = ("C2", "E3", "G3", "C4")
    gm = ("G1", "Bb2", "D3", "G3")
    a_ = ("A1", "C#3", "E3", "A3")
    return {
        5: dm, 6: bb, 7: f_, 8: c_, 9: dm, 10: bb, 11: f_, 12: c_,
        13: dm, 14: bb, 15: f_, 16: c_, 17: dm, 18: bb, 19: gm, 20: a_,
        21: dm, 22: c_, 23: bb, 24: a_, 25: dm, 26: c_, 27: bb, 28: a_,
        29: dm, 30: c_, 31: bb, 32: a_,
        33: dm, 34: bb, 35: f_, 36: c_, 37: dm, 38: bb, 39: f_, 40: a_,
    }[m]


def arp8(bass, third, fifth, octv):
    """分解和弦八分：根-三-五-八-五-三-根-三（摇摆型）。"""
    return [N(bass, 0.5), N(third, 0.5), N(fifth, 0.5), N(octv, 0.5),
            N(fifth, 0.5), N(third, 0.5), N(bass, 0.5), N(third, 0.5)]


def oct_bass8(bass, octv):
    """高潮段八度低音：根-八 交替。"""
    out = []
    for _ in range(4):
        out.append(N(bass, 0.5))
        out.append(N(octv, 0.5))
    return out


# ---------------------------------------------------------------------------
# 旋律表（右手）
# ---------------------------------------------------------------------------
def melody_of(m):
    tbl = {
        # --- 引子（m1-4，分解琶音确立 Dm）---
        1: [(N("D4", 1.0)), (N("F4", 1.0)), (N("A4", 1.0)), (N("D5", 1.0))],
        2: [(N("D5", 1.0)), (N("A4", 1.0)), (N("F4", 1.0)), (N("D4", 1.0))],
        3: [(N("D4", 1.0)), (N("F4", 1.0)), (N("A4", 1.0)), (N("C5", 1.0))],
        4: [(N("A4", 3.0)), (N("G4", 1.0))],
        # --- 主题 A（乐句 1，m5-12）---
        5: [(N("A4", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        6: [(N("F4", 2.0)), (N("F4", 1.0)), (N("E4", 1.0))],
        7: [(N("C5", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        8: [(N("G4", 2.0)), (N("E4", 1.0)), (N("F4", 1.0))],
        9: [(N("A4", 2.0)), (N("D5", 1.0)), (N("C5", 1.0))],
        10: [(N("Bb4", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        11: [(N("A4", 2.0)), (N("F4", 1.0)), (N("E4", 1.0))],
        12: [(N("E4", 2.0)), (N("D4", 1.0)), (N("C#4", 1.0))],
        # --- 主题 A（乐句 2，m13-20）---
        13: [(N("A4", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        14: [(N("F4", 2.0)), (N("F4", 1.0)), (N("E4", 1.0))],
        15: [(N("C5", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        16: [(N("G4", 2.0)), (N("E4", 1.0)), (N("F4", 1.0))],
        17: [(N("A4", 2.0)), (N("D5", 1.0)), (N("C5", 1.0))],
        18: [(N("Bb4", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        19: [(N("Bb4", 2.0)), (N("A4", 1.0)), (N("G4", 1.0))],
        20: [(N("C#5", 2.0)), (N("A4", 2.0))],
        # --- 发展 B（m21-32，上行，哀歌低音）---
        21: [(N("D5", 2.0)), (N("E5", 1.0)), (N("F5", 1.0))],
        22: [(N("E5", 2.0)), (N("F5", 1.0)), (N("G5", 1.0))],
        23: [(N("F5", 2.0)), (N("E5", 1.0)), (N("D5", 1.0))],
        24: [(N("C#5", 2.0)), (N("D5", 1.0)), (N("E5", 1.0))],
        25: [(N("F5", 2.0)), (N("E5", 1.0)), (N("D5", 1.0))],
        26: [(N("E5", 2.0)), (N("D5", 1.0)), (N("C5", 1.0))],
        27: [(N("D5", 2.0)), (N("C5", 1.0)), (N("Bb4", 1.0))],
        28: [(N("C#5", 3.0)), (R(1.0))],
        29: [(N("A5", 2.0)), (N("G5", 1.0)), (N("F5", 1.0))],
        30: [(N("G5", 2.0)), (N("F5", 1.0)), (N("E5", 1.0))],
        31: [(N("F5", 2.0)), (N("E5", 1.0)), (N("D5", 1.0))],
        32: [(N("E5", 2.0)), (N("C#5", 2.0))],
        # --- 高潮 C（m33-40，八度加厚）---
        33: [(N("A5", 4.0))],
        34: [(N("F5", 2.0)), (N("G5", 1.0)), (N("A5", 1.0))],
        35: [(N("A5", 2.0)), (N("G5", 1.0)), (N("F5", 1.0))],
        36: [(N("E5", 2.0)), (N("D5", 1.0)), (N("C5", 1.0))],
        37: [(N("D5", 2.0)), (N("E5", 1.0)), (N("F5", 1.0))],
        38: [(N("G5", 2.0)), (N("F5", 1.0)), (N("E5", 1.0))],
        39: [(N("F5", 2.0)), (N("E5", 1.0)), (N("D5", 1.0))],
        40: [(N("C#5", 2.0)), (N("E5", 2.0))],
        # --- 破碎再现 A'（m41-44）---
        41: [(N("A4", 2.0)), (R(2.0))],
        42: [(N("F4", 1.0)), (N("E4", 1.0)), (R(2.0))],
        43: [(N("C5", 1.0)), (N("A4", 1.0)), (R(2.0))],
        44: [(N("G4", 1.0)), (N("E4", 1.0)), (R(2.0))],
        # --- 尾声（m45-48，消逝）---
        45: [(N("D4", 2.0)), (N("F4", 2.0))],
        46: [(N("C4", 2.0)), (N("E4", 2.0))],
        47: [(N("Bb3", 2.0)), (N("D4", 2.0))],
        48: [(N("D4", 4.0))],
    }
    return tbl[m]


# ---------------------------------------------------------------------------
# 力度表（标在右手小节起点）
# ---------------------------------------------------------------------------
DYNAMICS = {
    1: "pp", 5: "p", 13: "mp", 21: "mf", 25: "f", 29: "f",
    33: "ff", 37: "ff", 41: "p", 45: "pp",
}


def build():
    score = stream.Score()
    md = metadata.Metadata()
    md.title = TITLE
    md.composer = COMPOSER
    score.insert(0, md)

    rh = stream.Part()
    rh.partName = "Piano"
    rh.append(instrument.Piano())
    rh.append(clef.TrebleClef())
    lh = stream.Part()
    lh.partName = "Piano"
    lh.append(instrument.Piano())
    lh.append(clef.BassClef())

    rh_measures = []
    lh_measures = []
    for m in range(1, 49):
        mrh = stream.Measure(number=m)
        mlh = stream.Measure(number=m)

        # 右手
        mel = melody_of(m)
        if 33 <= m <= 40:  # 高潮段八度加厚
            mel = [CH([n.pitch.nameWithOctave, down8(n.pitch.nameWithOctave)], n.quarterLength)
                   if isinstance(n, note.Note) else n for n in mel]
        for n in mel:
            mrh.append(n)

        # 左手
        if m <= 4:  # 引子：长低音
            mlh.append(N("D2", 4.0))
        elif 5 <= m <= 32:  # A + B：分解和弦
            bass, third, fifth, octv = chord_of(m)
            for n in arp8(bass, third, fifth, octv):
                mlh.append(n)
        elif 33 <= m <= 40:  # 高潮：八度低音
            bass, third, fifth, octv = chord_of(m)
            for n in oct_bass8(bass, octv):
                mlh.append(n)
        elif 41 <= m <= 44:  # 破碎再现：长低音
            bass = {"Dm": "D2", "Bb": "Bb1", "F": "F2", "C": "C2"}
            ch = {41: "Dm", 42: "Bb", 43: "F", 44: "C"}[m]
            mlh.append(N(bass[ch], 4.0))
        else:  # 尾声：哀歌低音 D-C-Bb-D
            coda_bass = {45: "D2", 46: "C2", 47: "Bb1", 48: "D2"}
            mlh.append(N(coda_bass[m], 4.0))

        rh.append(mrh)
        lh.append(mlh)
        rh_measures.append(mrh)
        lh_measures.append(mlh)

        # 力度
        if m in DYNAMICS:
            mrh.append(dynamics.Dynamic(DYNAMICS[m]))
            mlh.append(dynamics.Dynamic(DYNAMICS[m]))

    score.append(rh)
    score.append(lh)

    score.insert(0, meter.TimeSignature("4/4"))
    score.insert(0, key.KeySignature(-1))  # F 大调 = D 小调

    # 速度：主速度标在首小节；尾声渐慢标在对应小节
    rh_measures[0].insert(0, tempo.MetronomeMark(number=BPM))
    rit = {44: 58, 45: 54, 46: 50, 47: 46, 48: 42}
    for m, bpm in rit.items():
        rh_measures[m - 1].insert(0, tempo.MetronomeMark(number=bpm))

    # 末音延音记号
    last_rh = rh[-1].notes[-1]
    last_lh = lh[-1].notes[-1]
    last_rh.expressions.append(expressions.Fermata())
    last_lh.expressions.append(expressions.Fermata())

    return score


def main():
    os.makedirs(OUT, exist_ok=True)
    score = build()
    score.write("musicxml", os.path.join(OUT, "song.musicxml"))
    score.write("midi", os.path.join(OUT, "song.mid"))
    print(f"✅ 已生成谱面：{os.path.join(OUT, 'song.musicxml')}")
    print(f"✅ 已生成 MIDI：{os.path.join(OUT, 'song.mid')}")
    print("下一步渲染 PDF / MP3：")
    print("  mscore -o out/song.pdf out/song.musicxml")
    print("  mscore -o out/song.mp3 out/song.musicxml")


if __name__ == "__main__":
    main()
