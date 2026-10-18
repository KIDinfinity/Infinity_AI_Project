#!/usr/bin/env python3
"""③ 解析 MusicXML → 结构化 JSON。

通用工具：任何乐器的 MusicXML 都适用。
用法：
    uv run --with music21 python 03_parse_musicxml.py \
        --src <full.mxl> --out <structure.json>
"""
import argparse
import json
import os

from music21 import converter


def parse_parts(score):
    parts = list(score.parts)
    if len(parts) >= 2:
        right, left = parts[0], parts[1]
    else:
        right, left = parts[0], None
    return right, left


def notes_of(part):
    result = {}
    for m in part.getElementsByClass("Measure"):
        idx = m.measureNumber
        notes = []
        for n in m.notes:
            # 和弦：展开成多个音；单音：一个音
            if n.isChord:
                for p in n.pitches:
                    notes.append({
                        "pitch": p.nameWithOctave,
                        "midi": p.midi,
                        "duration": float(n.quarterLength),
                    })
            else:
                notes.append({
                    "pitch": n.nameWithOctave,
                    "midi": n.pitch.midi if n.pitch else None,
                    "duration": float(n.quarterLength),
                })
        result[idx] = notes
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="MusicXML 文件路径（full.mxl）")
    ap.add_argument("--out", required=True, help="输出 JSON 路径")
    args = ap.parse_args()

    if not os.path.exists(args.src):
        raise SystemExit(f"未找到 {args.src}，请先完成 OMR 识别生成 MusicXML")

    score = converter.parse(args.src)
    right, left = parse_parts(score)
    right_map = notes_of(right)
    left_map = notes_of(left) if left else {}

    measures = []
    for i in sorted(set(right_map) | set(left_map)):
        measures.append({
            "index": i,
            "right_hand": right_map.get(i, []),
            "left_hand": left_map.get(i, []),
        })

    data = {"title": score.metadata.title or "未命名", "measures": measures}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已解析 {len(measures)} 个小节 → {args.out}")


if __name__ == "__main__":
    main()
