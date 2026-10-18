#!/usr/bin/env python3
"""④ 按 day 切分小节 → 每个 day 生成专属谱（MusicXML + MIDI）。

通用工具：给定目标 plan 根目录 + 完整 MusicXML + day→小节映射，
自动遍历 plan 下的 phase_XX/week_XX/dayNN_YYYYMMDD 目录，为每个 day 写 sheet/。
用法：
    uv run --with music21 python 04_gen_day_sheets.py \
        --plan-root <plan 目录> --src <full.mxl> --map <day_measure_map.json>
"""
import argparse
import json
import os

from music21 import converter, stream, meter


def collect_day_dirs(plan_root):
    dirs = []
    for phase in sorted(os.listdir(plan_root)):
        p = os.path.join(plan_root, phase)
        if not os.path.isdir(p) or not phase.startswith("phase_"):
            continue
        for week in sorted(os.listdir(p)):
            w = os.path.join(p, week)
            if not os.path.isdir(w) or not week.startswith("week_"):
                continue
            for day in sorted(os.listdir(w)):
                d = os.path.join(w, day)
                if os.path.isdir(d) and day.startswith("day"):
                    try:
                        num = int(day.split("_")[0][3:])
                    except ValueError:
                        continue
                    dirs.append((num, d))
    return dict(sorted(dirs))


def slice_score(score, start_measure, end_measure):
    """抽取 [start, end] 小节，重建带拍号的片段谱。"""
    out = stream.Score()
    first_part = score.parts[0]
    ts_list = first_part.getTimeSignatures()
    ts_str = ts_list[0].ratioString if ts_list else "4/4"
    for part in score.parts:
        p = stream.Part()
        p.append(meter.TimeSignature(ts_str))
        for m in part.getElementsByClass("Measure"):
            if start_measure <= m.measureNumber <= end_measure:
                p.append(m)
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-root", required=True, help="目标 plan 根目录，如 plan/plan_piano")
    ap.add_argument("--src", required=True, help="完整 MusicXML 路径（full.mxl）")
    ap.add_argument("--map", required=True, help="day_measure_map.json 路径")
    args = ap.parse_args()

    if not os.path.exists(args.src):
        raise SystemExit(f"未找到 {args.src}")
    if not os.path.exists(args.map):
        raise SystemExit(f"未找到 {args.map}")
    if not os.path.isdir(args.plan_root):
        raise SystemExit(f"未找到 plan 目录 {args.plan_root}")

    with open(args.map) as f:
        day_map = {int(k): v for k, v in json.load(f).items()}

    score = converter.parse(args.src)
    day_dirs = collect_day_dirs(args.plan_root)

    total = 0
    for day_no, (start, end) in sorted(day_map.items()):
        if day_no not in day_dirs:
            print(f"  ⚠️ 未找到 day{day_no:02d} 目录，跳过")
            continue
        day_dir = day_dirs[day_no]
        sheet_dir = os.path.join(day_dir, "sheet")
        os.makedirs(sheet_dir, exist_ok=True)

        frag = slice_score(score, start, end)
        frag.write("musicxml", os.path.join(sheet_dir, "sheet.musicxml"))
        frag.write("midi", os.path.join(sheet_dir, "sheet.mid"))
        total += 1
        print(f"  day{day_no:02d}: 第 {start}-{end} 小节 → {sheet_dir}")

    print(f"✅ 已生成 {total} 个 day 的谱子（MusicXML + MIDI）")
    print("💡 PDF/PNG 渲染：brew install --cask musescore 后执行 "
          "`mscore -o sheet.pdf sheet.musicxml`")


if __name__ == "__main__":
    main()
