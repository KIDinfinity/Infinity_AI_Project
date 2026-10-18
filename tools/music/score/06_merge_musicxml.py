#!/usr/bin/env python3
"""⑥ 合并多页 MusicXML → 一个完整 MusicXML（重排小节号）。

通用工具：把 OMR 识别的「一页一个 .mxl」合并成整曲，左右手声部分别合并。
用法：
    uv run --with music21 python 06_merge_musicxml.py \
        --src-dir <含多个.mxl的目录> --out <full.mxl>
"""
import argparse
import copy
import glob
import os

from music21 import converter, stream, meter, key


def flatten_voices(m):
    """把 measure 内多 voice 打平成单层，避免 voice id 跨页不连续导致 makeTies 报错。"""
    for v in list(m.voices):
        for el in list(v.elements):
            v.remove(el)
            m.append(el)
        m.remove(v)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-dir", required=True, help="含多个 .mxl/.xml 的目录")
    ap.add_argument("--out", required=True, help="输出完整谱路径")
    ap.add_argument("--pattern", default="*.mxl", help="文件名匹配，默认 *.mxl")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.src_dir, args.pattern)))
    if not files:
        raise SystemExit(f"未找到文件：{args.src_dir}/{args.pattern}")

    scores = [converter.parse(f) for f in files]
    n_parts = len(scores[0].parts)
    print(f"合并 {len(files)} 页 → {n_parts} 个声部")

    # 用第一页的拍号/调号作为模板
    first = scores[0]
    ts_objs = list(first.recurse().getElementsByClass(meter.TimeSignature))
    ts_str = ts_objs[0].ratioString if ts_objs else "4/4"
    key_objs = list(first.recurse().getElementsByClass(key.KeySignature))
    key_obj = key_objs[0] if key_objs else key.KeySignature(0)

    out_score = stream.Score()
    measure_counter = 1
    for pi in range(n_parts):
        out_part = stream.Part()
        out_part.append(meter.TimeSignature(ts_str))
        out_part.append(key_obj)
        for s in scores:
            part = s.parts[pi]
            for m in part.getElementsByClass("Measure"):
                m = copy.deepcopy(m)
                m.number = measure_counter
                # 清除跨页连音线 + 打平多 voice（OMR 的 voice 编号跨页常不连续，写出时会导致 makeTies 报错）
                for n in m.recurse().notes:
                    n.tie = None
                flatten_voices(m)
                out_part.append(m)
                measure_counter += 1
        measure_counter = 1  # 每个声部小节号独立重排
        out_score.append(out_part)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    out_score.write("musicxml", args.out)
    total = len(out_score.parts[0].getElementsByClass("Measure"))
    print(f"✅ 已合并 → {args.out}（{total} 个小节）")


if __name__ == "__main__":
    main()
