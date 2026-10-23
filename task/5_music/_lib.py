#!/usr/bin/env python3
"""5_music 共享生成工具：乐谱/MIDI 写出与音符构造辅助。"""
import os

from music21 import (
    stream, note, chord, meter, key, tempo, clef,
    instrument, metadata, pitch,
)


def N(p, d=1.0):
    return note.Note(p, quarterLength=d)


def R(d=1.0):
    return note.Rest(quarterLength=d)


def CH(ps, d=1.0):
    return chord.Chord(list(ps), quarterLength=d)


def UNP(midi, d=1.0):
    n = note.Unpitched()
    n.ps = midi
    n.quarterLength = d
    return n


def new_score(title, composer, bpm, timesig="4/4", keysig=0):
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = title
    md.composer = composer
    sc.insert(0, md)
    sc.insert(0, meter.TimeSignature(timesig))
    sc.insert(0, key.KeySignature(keysig))
    return sc


def make_part(name, clef_obj, instr=None):
    p = stream.Part()
    p.partName = name
    if instr is not None:
        p.append(instr)
    p.append(clef_obj)
    return p


def add_voices(m, voices):
    """把一个 Measure 里的多个声部依次加入（每声部一个 Voice）。"""
    for v in voices:
        vo = stream.Voice()
        for n in v:
            vo.append(n)
        m.append(vo)


def write_score(sc, out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    mx = os.path.join(out_dir, name + ".musicxml")
    mid = os.path.join(out_dir, name + ".mid")
    sc.write("musicxml", mx)
    sc.write("midi", mid)
    print(f"generated: {mx}")
    print(f"generated: {mid}")
    print(f"render: mscore -o {os.path.join(out_dir, name + '.pdf')} {mx}")
    print(f"render: mscore -o {os.path.join(out_dir, name + '.mp3')} {mx}")
