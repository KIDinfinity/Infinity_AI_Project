#!/usr/bin/env python3
"""⑤ 生成 day_measure_map.json（day编号 → 小节范围）。

通用工具：根据某 plan 的总小节数，生成「每天练哪几小节」的映射。
用法：
    uv run --with music21 python 05_make_day_map.py \
        --struct <structure.json> --out <day_measure_map.json> [--page-measures 12,12,10,10,8]
"""
import argparse
import json
import math
import os


def page_based_split(total, page_measures):
    ranges = []
    start = 1
    for cnt in page_measures:
        ranges.append([start, start + cnt - 1])
        start += cnt
    if start - 1 < total:  # 页小节数之和 != total 时补到最后
        ranges[-1][1] = total
    return ranges


def even_split(total, total_days):
    per = max(1, math.ceil(total / total_days))
    ranges = []
    start = 1
    while start <= total:
        end = min(start + per - 1, total)
        ranges.append([start, end])
        start = end + 1
    return ranges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--struct", required=True, help="structure.json 路径")
    ap.add_argument("--out", required=True, help="输出 day_measure_map.json 路径")
    ap.add_argument("--page-measures", help="每页小节数，逗号分隔，如 12,12,10,10,8")
    ap.add_argument("--total-days", type=int, default=84, help="计划总天数，默认 84")
    args = ap.parse_args()

    if not os.path.exists(args.struct):
        raise SystemExit(f"未找到 {args.struct}，先运行 03_parse_musicxml.py")
    with open(args.struct) as f:
        data = json.load(f)
    total = len(data["measures"])

    if args.page_measures:
        page_measures = [int(x) for x in args.page_measures.split(",")]
        ranges = page_based_split(total, page_measures)
    else:
        ranges = even_split(total, args.total_days)

    day_map = {i + 1: r for i, r in enumerate(ranges)}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(day_map, f, ensure_ascii=False, indent=2)
    print(f"✅ 总 {total} 小节 → {len(ranges)} 段 → {args.out}")
    print("   提示：默认按小节数均分；建议拿到真实谱后按页/行用 --page-measures 精确切分")


if __name__ == "__main__":
    main()
